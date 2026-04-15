#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值监控模块 - 饕餮整合自 stock-valuation-monitor
PE/PB 历史百分位、ETF 溢价监控、BAND 分析
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class ValuationMonitor:
    """
    估值监控器 - 饕餮整合自 stock-valuation-monitor
    
    能力:
    - PE/PB 历史百分位计算
    - ETF 溢价/折价监控
    - BAND 分析 (股债利差)
    - 个股估值跟踪
    """
    
    # 估值阈值参考
    THRESHOLDS = {
        'pe': {'low': 15, 'high': 30},
        'pb': {'low': 2, 'high': 5},
        'dividend_yield': {'low': 2, 'high': 4}
    }
    
    def __init__(self):
        self.data_dir = OUTPUT_DIR / 'data'
        self.reports_dir = OUTPUT_DIR / 'reports'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_percentile(
        self,
        symbol: str,
        metric: str = 'pe',
        period_years: int = 5
    ) -> Dict:
        """
        计算估值指标的历史百分位
        
        Args:
            symbol: 股票代码
            metric: 指标类型 (pe/pb/ps/dividend_yield)
            period_years: 回溯年数
            
        Returns:
            百分位分析结果
        """
        result = {
            'symbol': symbol,
            'metric': metric,
            'current_value': None,
            'percentile': None,
            'historical_range': {},
            'valuation_level': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            # 获取历史数据
            ticker = yf.Ticker(symbol)
            
            # 获取估值指标历史
            if metric in ['pe', 'pb', 'ps']:
                # 从 financials 获取
                info = ticker.info
                current_value = info.get(f'trailing{metric.upper()}', info.get(f'priceTo{metric.upper()[0]}ook' if metric == 'pb' else metric))
                
                # 获取历史价格估算 (简化版)
                hist = ticker.history(period=f'{period_years}y')
                
                if hist.empty:
                    result['error'] = '无历史数据'
                    return result
                
                # 使用价格分布作为估值参考 (简化方法)
                current_price = hist['Close'].iloc[-1]
                prices = hist['Close']
                
                # 计算百分位
                percentile = (prices < current_price).sum() / len(prices) * 100
                
                result['current_value'] = current_value
                result['percentile'] = round(percentile, 2)
                result['historical_range'] = {
                    'min': round(float(prices.min()), 2),
                    'max': round(float(prices.max()), 2),
                    'mean': round(float(prices.mean()), 2),
                    'median': round(float(prices.median()), 2),
                    'std': round(float(prices.std()), 2)
                }
                
                # 判断估值水平
                if percentile < 20:
                    result['valuation_level'] = '低估'
                elif percentile < 40:
                    result['valuation_level'] = '偏低'
                elif percentile < 60:
                    result['valuation_level'] = '合理'
                elif percentile < 80:
                    result['valuation_level'] = '偏高'
                else:
                    result['valuation_level'] = '高估'
                
                result['data_source'] = 'yfinance'
                
            elif metric == 'dividend_yield':
                info = ticker.info
                current_value = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None
                
                result['current_value'] = round(current_value, 2) if current_value else None
                result['valuation_level'] = self._classify_dividend_yield(current_value) if current_value else None
                result['data_source'] = 'yfinance'
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _classify_dividend_yield(self, yield_value: float) -> str:
        """分类股息率"""
        if yield_value < 1:
            return '极低'
        elif yield_value < 2:
            return '偏低'
        elif yield_value < 4:
            return '合理'
        elif yield_value < 6:
            return '偏高'
        else:
            return '高收益'
    
    def analyze_etf_premium(self, etf_symbol: str) -> Dict:
        """
        分析 ETF 溢价/折价
        
        Args:
            etf_symbol: ETF 代码
            
        Returns:
            溢价分析结果
        """
        result = {
            'etf_symbol': etf_symbol,
            'nav': None,
            'price': None,
            'premium_rate': None,
            'status': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(etf_symbol)
            info = ticker.info
            
            # 获取净值和价格
            nav = info.get('navPrice')  # 净值
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if nav and price:
                premium_rate = (price - nav) / nav * 100
                
                result['nav'] = round(nav, 4)
                result['price'] = round(price, 4)
                result['premium_rate'] = round(premium_rate, 4)
                
                if premium_rate > 2:
                    result['status'] = '大幅溢价'
                elif premium_rate > 0.5:
                    result['status'] = '小幅溢价'
                elif premium_rate > -0.5:
                    result['status'] = '正常'
                elif premium_rate > -2:
                    result['status'] = '小幅折价'
                else:
                    result['status'] = '大幅折价'
                
                result['data_source'] = 'yfinance'
            else:
                result['error'] = '无法获取净值或价格数据'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def calculate_band(
        self,
        symbol: str,
        risk_free_rate: float = 0.03
    ) -> Dict:
        """
        BAND 分析 - 股债利差
        
        Args:
            symbol: 股票代码
            risk_free_rate: 无风险利率 (默认3%)
            
        Returns:
            BAND 分析结果
        """
        result = {
            'symbol': symbol,
            'earnings_yield': None,
            'risk_free_rate': risk_free_rate,
            'equity_risk_premium': None,
            'band_signal': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取市盈率
            pe = info.get('trailingPE')
            
            if pe and pe > 0:
                earnings_yield = 1 / pe * 100  # 收益率 = 1/PE
                equity_risk_premium = earnings_yield - risk_free_rate * 100
                
                result['earnings_yield'] = round(earnings_yield, 4)
                result['equity_risk_premium'] = round(equity_risk_premium, 4)
                
                # BAND 信号判断
                if equity_risk_premium > 3:
                    result['band_signal'] = '极度低估'
                elif equity_risk_premium > 1:
                    result['band_signal'] = '低估'
                elif equity_risk_premium > -1:
                    result['band_signal'] = '合理'
                elif equity_risk_premium > -3:
                    result['band_signal'] = '高估'
                else:
                    result['band_signal'] = '极度高估'
                
                result['data_source'] = 'yfinance'
            else:
                result['error'] = '无法获取市盈率数据'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_valuation_summary(self, symbol: str) -> Dict:
        """
        获取估值摘要
        
        Args:
            symbol: 股票代码
            
        Returns:
            估值摘要
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pe_analysis': {},
            'pb_analysis': {},
            'dividend_analysis': {},
            'band_analysis': {},
            'overall_assessment': None,
            'error': None
        }
        
        try:
            # PE 分析
            pe_result = self.calculate_percentile(symbol, 'pe', 5)
            result['pe_analysis'] = {
                'current_pe': pe_result.get('current_value'),
                'percentile': pe_result.get('percentile'),
                'level': pe_result.get('valuation_level')
            }
            
            # PB 分析
            pb_result = self.calculate_percentile(symbol, 'pb', 5)
            result['pb_analysis'] = {
                'current_pb': pb_result.get('current_value'),
                'percentile': pb_result.get('percentile'),
                'level': pb_result.get('valuation_level')
            }
            
            # 股息率分析
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 获取股息率 (yfinance 可能返回小数或百分比)
                div_yield = info.get('dividendYield')
                trailing_yield = info.get('trailingAnnualDividendYield')
                
                # 优先使用 trailing 值
                if trailing_yield and trailing_yield < 1:
                    div_yield_pct = trailing_yield * 100
                elif div_yield:
                    # yfinance 有时返回错误的比例
                    if div_yield > 1:
                        # 可能已经是百分比
                        div_yield_pct = div_yield
                    else:
                        div_yield_pct = div_yield * 100
                else:
                    div_yield_pct = 0
                
                if div_yield_pct > 0:
                    # 分类
                    if div_yield_pct < 1:
                        level = '偏低'
                    elif div_yield_pct < 3:
                        level = '合理'
                    elif div_yield_pct < 5:
                        level = '较高'
                    else:
                        level = '高收益'
                    
                    result['dividend_analysis'] = {
                        'current_yield': round(float(div_yield_pct), 2),
                        'level': level
                    }
                else:
                    result['dividend_analysis'] = {
                        'current_yield': 0,
                        'level': '无分红'
                    }
            except Exception as e:
                result['dividend_analysis'] = {
                    'current_yield': 0,
                    'level': '数据缺失',
                    'error': str(e)
                }
            
            # BAND 分析
            band_result = self.calculate_band(symbol)
            result['band_analysis'] = {
                'earnings_yield': band_result.get('earnings_yield'),
                'risk_premium': band_result.get('equity_risk_premium'),
                'signal': band_result.get('band_signal')
            }
            
            # 综合评估
            signals = []
            if result['pe_analysis'].get('level'):
                signals.append(result['pe_analysis']['level'])
            if result['pb_analysis'].get('level'):
                signals.append(result['pb_analysis']['level'])
            if result['band_analysis'].get('signal'):
                signals.append(result['band_analysis']['signal'])
            
            # 简单投票
            low_count = sum(1 for s in signals if '低' in str(s))
            high_count = sum(1 for s in signals if '高' in str(s))
            
            if low_count > high_count:
                result['overall_assessment'] = '低估 - 可能存在投资机会'
            elif high_count > low_count:
                result['overall_assessment'] = '高估 - 建议谨慎'
            else:
                result['overall_assessment'] = '合理 - 持续观察'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def calculate_percentile(symbol: str, metric: str = 'pe', period_years: int = 5) -> Dict:
    """计算估值百分位"""
    monitor = ValuationMonitor()
    return monitor.calculate_percentile(symbol, metric, period_years)


def analyze_etf_premium(etf_symbol: str) -> Dict:
    """分析 ETF 溢价"""
    monitor = ValuationMonitor()
    return monitor.analyze_etf_premium(etf_symbol)


def calculate_band(symbol: str, risk_free_rate: float = 0.03) -> Dict:
    """BAND 分析"""
    monitor = ValuationMonitor()
    return monitor.calculate_band(symbol, risk_free_rate)


def get_valuation_summary(symbol: str) -> Dict:
    """获取估值摘要"""
    monitor = ValuationMonitor()
    return monitor.get_valuation_summary(symbol)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='估值监控 - 饕餮整合自 stock-valuation-monitor')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # percentile
    pct_parser = subparsers.add_parser('percentile', help='估值百分位')
    pct_parser.add_argument('symbol', help='股票代码')
    pct_parser.add_argument('--metric', default='pe', help='指标 (pe/pb/ps/dividend_yield)')
    pct_parser.add_argument('--years', type=int, default=5, help='回溯年数')
    
    # etf
    etf_parser = subparsers.add_parser('etf', help='ETF溢价分析')
    etf_parser.add_argument('symbol', help='ETF代码')
    
    # band
    band_parser = subparsers.add_parser('band', help='BAND分析')
    band_parser.add_argument('symbol', help='股票代码')
    band_parser.add_argument('--risk-free', type=float, default=0.03, help='无风险利率')
    
    # summary
    sum_parser = subparsers.add_parser('summary', help='估值摘要')
    sum_parser.add_argument('symbol', help='股票代码')
    
    args = parser.parse_args()
    
    monitor = ValuationMonitor()
    
    if args.command == 'percentile':
        result = monitor.calculate_percentile(args.symbol, args.metric, args.years)
    elif args.command == 'etf':
        result = monitor.analyze_etf_premium(args.symbol)
    elif args.command == 'band':
        result = monitor.calculate_band(args.symbol, args.risk_free)
    elif args.command == 'summary':
        result = monitor.get_valuation_summary(args.symbol)
    else:
        parser.print_help()
        sys.exit(0)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
