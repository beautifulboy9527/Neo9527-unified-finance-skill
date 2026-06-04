#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流动性分析模块 - 完整集成自 stock-liquidity skill
买卖价差、成交量分析、市场冲击估算、换手率、Amihud 非流动性指标
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quote import detect_market


class LiquidityAnalyzer:
    """
    流动性分析器 - 集成自 stock-liquidity skill
    
    分析维度:
    - 买卖价差 (bid-ask spread)
    - 成交量分析
    - 市场冲击估算 (market impact)
    - 换手率
    - Amihud 非流动性指标
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.market = detect_market(symbol)
    
    def _normalize_for_yfinance(self, symbol: str) -> str:
        """
        标准化股票代码为 yfinance 格式
        A股需要添加 .SS 或 .SZ 后缀
        """
        import re
        
        # 如果已经有后缀，直接返回
        if '.' in symbol:
            return symbol
        
        # A股: 6位数字
        if re.match(r'^[0-9]{6}$', symbol):
            if symbol.startswith('6'):
                return f"{symbol}.SS"  # 上海
            elif symbol.startswith(('0', '3')):
                return f"{symbol}.SZ"  # 深圳
            else:
                return f"{symbol}.SS"  # 默认上海
        
        # 港股: 5位数字
        if re.match(r'^[0-9]{5}$', symbol):
            return f"{symbol}.HK"
        
        # 美股: 纯字母，无需转换
        return symbol
    
    def analyze(self, period: str = '3mo') -> Dict:
        """
        完整流动性分析 - Liquidity Dashboard
        
        Args:
            period: 回溯周期 (默认 3mo)
            
        Returns:
            流动性分析结果
        """
        result = {
            'symbol': self.symbol,
            'market': self.market,
            'spread': {},
            'volume': {},
            'turnover': {},
            'impact': {},
            'amihud': None,
            'grade': None,
            'data_source': 'none',
            'update_time': None,
            'error': None
        }
        
        try:
            import yfinance as yf
            import numpy as np
            
            # 标准化股票代码
            yf_symbol = self._normalize_for_yfinance(self.symbol)
            
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            hist = ticker.history(period=period)
            
            if hist.empty:
                result['error'] = '无历史数据'
                return result
            
            # ===== 1. 买卖价差分析 =====
            bid = info.get('bid')
            ask = info.get('ask')
            bid_size = info.get('bidSize')
            ask_size = info.get('askSize')
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
            
            spread = None
            spread_pct = None
            spread_bps = None
            
            if bid and ask and bid > 0 and ask > 0:
                spread = round(ask - bid, 4)
                midpoint = (ask + bid) / 2
                spread_pct = round((spread / midpoint) * 100, 4)
                spread_bps = round(spread_pct * 100, 2)
            
            result['spread'] = {
                'bid': bid,
                'ask': ask,
                'bid_size': bid_size,
                'ask_size': ask_size,
                'spread': spread,
                'spread_pct': spread_pct,
                'spread_bps': spread_bps,
                'current_price': round(current_price, 2)
            }
            
            # ===== 2. 成交量分析 =====
            vol = hist['Volume']
            close = hist['Close']
            dollar_volume = vol * close
            
            # 相对成交量 (今天 vs 平均)
            rvol = vol.iloc[-1] / vol.mean() if vol.mean() > 0 else None
            
            # 成交量趋势
            x = np.arange(len(vol))
            slope, _ = np.polyfit(x, vol.values, 1) if len(vol) > 1 else (0, 0)
            trend_pct = (slope * len(vol)) / vol.mean() * 100 if vol.mean() > 0 else 0
            
            result['volume'] = {
                'avg_daily_volume': int(vol.mean()),
                'median_volume': int(vol.median()),
                'avg_dollar_volume': round(dollar_volume.mean(), 0),
                'current_volume': int(vol.iloc[-1]),
                'relative_volume': round(rvol, 2) if rvol else None,
                'volume_trend_pct': round(trend_pct, 1),
                'max_volume': int(vol.max()),
                'min_volume': int(vol.min()),
                'volume_std': int(vol.std()),
                'volume_cv': round(vol.std() / vol.mean(), 3) if vol.mean() > 0 else None
            }
            
            # ===== 3. 换手率分析 =====
            shares_outstanding = info.get('sharesOutstanding')
            float_shares = info.get('floatShares')
            
            if shares_outstanding:
                avg_vol = vol.mean()
                daily_turnover = avg_vol / shares_outstanding
                
                result['turnover'] = {
                    'daily_turnover': round(daily_turnover, 6),
                    'annualized_turnover': round(daily_turnover * 252, 2),
                    'days_to_trade_float': round(float_shares / avg_vol, 1) if float_shares else None,
                    'float_turnover_daily': round(avg_vol / float_shares, 6) if float_shares else None,
                    'float_turnover_annualized': round((avg_vol / float_shares) * 252, 2) if float_shares else None,
                    'shares_outstanding': shares_outstanding,
                    'float_shares': float_shares
                }
            
            # ===== 4. 市场冲击估算 =====
            returns = hist['Close'].pct_change().dropna()
            daily_volatility = returns.std()
            
            # Square-root impact model
            # Impact (%) = σ × √(Q / V)
            # 计算 1% ADV 的冲击
            avg_vol = vol.mean()
            participation_rate = 0.01
            impact_pct = daily_volatility * np.sqrt(participation_rate) * 100
            impact_bps = impact_pct * 100
            
            # 生成不同规模的冲击曲线
            sizes = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10]
            impact_curve = []
            for s in sizes:
                q = avg_vol * s
                imp = daily_volatility * np.sqrt(s) * 100
                impact_curve.append({
                    'pct_adv': round(s * 100, 1),
                    'shares': int(q),
                    'dollars': round(q * current_price, 0),
                    'impact_bps': round(imp * 100, 1)
                })
            
            result['impact'] = {
                'daily_volatility_pct': round(daily_volatility * 100, 2),
                'impact_1pct_adv_bps': round(impact_bps, 2),
                'impact_curve': impact_curve
            }
            
            # ===== 5. Amihud 非流动性指标 =====
            # Average of |daily return| / daily dollar volume
            dollar_vol = (hist['Close'] * hist['Volume']).iloc[1:]  # align with returns
            amihud_values = returns.abs() / dollar_vol
            amihud = amihud_values[amihud_values.replace([np.inf, -np.inf], np.nan).notna()].mean()
            
            result['amihud'] = {
                'value': round(amihud * 1e9, 4) if not np.isnan(amihud) else None,
                'interpretation': 'Amihud × 10^9, 越高表示流动性越差'
            }
            
            # ===== 6. 流动性评级 =====
            dollar_vol_avg = dollar_volume.mean()
            spread_pct_val = spread_pct if spread_pct else 999
            
            if dollar_vol_avg > 500e6 and spread_pct_val < 0.03:
                grade = 'Very High'
                grade_desc = '极高流动性 - 大盘蓝筹股'
            elif dollar_vol_avg > 50e6 and spread_pct_val < 0.10:
                grade = 'High'
                grade_desc = '高流动性 - 中大盘股'
            elif dollar_vol_avg > 5e6 and spread_pct_val < 0.50:
                grade = 'Moderate'
                grade_desc = '中等流动性 - 中小盘股'
            elif dollar_vol_avg > 500e3 and spread_pct_val < 2.0:
                grade = 'Low'
                grade_desc = '低流动性 - 小盘股'
            else:
                grade = 'Very Low'
                grade_desc = '极低流动性 - 微盘股或冷门股'
            
            result['grade'] = grade
            result['grade_description'] = grade_desc
            result['data_source'] = 'yfinance'
            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}. 请运行: pip install yfinance numpy'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_spread(self) -> Dict:
        """买卖价差分析"""
        result = {
            'symbol': self.symbol,
            'spread': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            bid = info.get('bid', 0)
            ask = info.get('ask', 0)
            bid_size = info.get('bidSize')
            ask_size = info.get('askSize')
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            if bid > 0 and ask > 0:
                midpoint = (bid + ask) / 2
                result['spread'] = {
                    'bid': bid,
                    'ask': ask,
                    'bid_size': bid_size,
                    'ask_size': ask_size,
                    'absolute_spread': round(ask - bid, 4),
                    'relative_spread_pct': round((ask - bid) / midpoint * 100, 4),
                    'relative_spread_bps': round((ask - bid) / midpoint * 10000, 2)
                }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_volume(self, period: str = '3mo') -> Dict:
        """成交量分析"""
        result = {
            'symbol': self.symbol,
            'volume': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import numpy as np
            
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                result['error'] = '无历史数据'
                return result
            
            vol = hist['Volume']
            close = hist['Close']
            dollar_vol = vol * close
            
            # 相对成交量
            rvol = vol.iloc[-1] / vol.mean() if vol.mean() > 0 else None
            
            # 成交量趋势
            x = np.arange(len(vol))
            slope, _ = np.polyfit(x, vol.values, 1) if len(vol) > 1 else (0, 0)
            trend_pct = (slope * len(vol)) / vol.mean() * 100 if vol.mean() > 0 else 0
            
            # 按星期几分组
            hist_copy = hist.copy()
            hist_copy['DayOfWeek'] = hist_copy.index.dayofweek
            day_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'}
            vol_by_day = hist_copy.groupby('DayOfWeek')['Volume'].mean()
            vol_by_day.index = vol_by_day.index.map(day_names)
            
            result['volume'] = {
                'avg_volume': int(vol.mean()),
                'median_volume': int(vol.median()),
                'avg_dollar_volume': round(dollar_vol.mean(), 0),
                'current_volume': int(vol.iloc[-1]),
                'relative_volume': round(rvol, 2) if rvol else None,
                'volume_trend_pct': round(trend_pct, 1),
                'volume_by_day': vol_by_day.to_dict(),
                'max_volume': int(vol.max()),
                'min_volume': int(vol.min())
            }
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def estimate_market_impact(self, order_shares: int = None, order_dollars: float = None, period: str = '3mo') -> Dict:
        """
        市场冲击估算 - Square-root model
        
        Args:
            order_shares: 订单股数
            order_dollars: 订单金额 (与 order_shares 二选一)
            period: 回溯周期
        """
        result = {
            'symbol': self.symbol,
            'impact': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import numpy as np
            
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                result['error'] = '无历史数据'
                return result
            
            current_price = info.get('currentPrice') or hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            returns = hist['Close'].pct_change().dropna()
            daily_volatility = returns.std()
            
            # 确定订单大小
            if order_dollars and not order_shares:
                order_shares = order_dollars / current_price
            elif not order_shares:
                # 默认: 1% ADV
                order_shares = avg_volume * 0.01
            
            participation_rate = order_shares / avg_volume if avg_volume > 0 else 0
            pct_adv = participation_rate * 100
            
            # Square-root impact model
            impact_pct = daily_volatility * np.sqrt(participation_rate) * 100
            impact_bps = impact_pct * 100
            impact_dollars = impact_pct / 100 * current_price * order_shares
            
            # 冲击曲线
            sizes = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]
            curve = []
            for s in sizes:
                q = avg_volume * s
                imp = daily_volatility * np.sqrt(s) * 100
                curve.append({
                    'pct_adv': round(s * 100, 1),
                    'shares': int(q),
                    'dollars': round(q * current_price, 0),
                    'impact_bps': round(imp * 100, 1),
                    'impact_dollars_per_share': round(imp / 100 * current_price, 4)
                })
            
            result['impact'] = {
                'current_price': round(current_price, 2),
                'avg_daily_volume': int(avg_volume),
                'daily_volatility_pct': round(daily_volatility * 100, 2),
                'order_shares': int(order_shares),
                'order_dollars': round(order_shares * current_price, 0),
                'pct_of_adv': round(pct_adv, 2),
                'estimated_impact_bps': round(impact_bps, 1),
                'estimated_impact_pct': round(impact_pct, 4),
                'estimated_impact_total_dollars': round(impact_dollars, 2),
                'impact_curve': curve
            }
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def analyze_liquidity(symbol: str, period: str = '3mo') -> Dict:
    """流动性分析入口"""
    analyzer = LiquidityAnalyzer(symbol)
    return analyzer.analyze(period)


def analyze_spread(symbol: str) -> Dict:
    """买卖价差分析"""
    analyzer = LiquidityAnalyzer(symbol)
    return analyzer.analyze_spread()


def analyze_volume(symbol: str, period: str = '3mo') -> Dict:
    """成交量分析"""
    analyzer = LiquidityAnalyzer(symbol)
    return analyzer.analyze_volume(period)


def estimate_market_impact(symbol: str, order_shares: int = None, order_dollars: float = None) -> Dict:
    """市场冲击估算"""
    analyzer = LiquidityAnalyzer(symbol)
    return analyzer.estimate_market_impact(order_shares, order_dollars)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='流动性分析 - 集成自 stock-liquidity skill')
    parser.add_argument('--symbol', required=True, help='股票代码')
    parser.add_argument('--period', default='3mo', help='分析周期')
    parser.add_argument('--type', choices=['full', 'spread', 'volume', 'impact'], default='full')
    parser.add_argument('--order-shares', type=int, help='订单股数 (用于市场冲击估算)')
    parser.add_argument('--order-dollars', type=float, help='订单金额 (用于市场冲击估算)')
    
    args = parser.parse_args()
    
    analyzer = LiquidityAnalyzer(args.symbol)
    
    if args.type == 'full':
        result = analyzer.analyze(args.period)
    elif args.type == 'spread':
        result = analyzer.analyze_spread()
    elif args.type == 'volume':
        result = analyzer.analyze_volume(args.period)
    elif args.type == 'impact':
        result = analyzer.estimate_market_impact(args.order_shares, args.order_dollars)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
