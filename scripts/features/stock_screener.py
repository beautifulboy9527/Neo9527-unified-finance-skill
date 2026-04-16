#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票筛选器 - 多策略技术形态筛选
整合自 stock-screener-cn

功能:
- A股/港股技术形态筛选
- 多策略支持 (均线多头/突破/RSI/放量/背离)
- 批量筛选
- 自定义条件组合
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import pandas as pd
import numpy as np

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class StockScreener:
    """
    股票筛选器
    
    支持策略:
    - ma_bull: 均线多头排列
    - ma_bear: 均线空头排列
    - breakout_up: 向上突破
    - breakout_down: 向下突破
    - rsi_oversold: RSI超卖
    - rsi_overbought: RSI超买
    - volume_break: 放量突破
    - macd_golden: MACD金叉
    - macd_death: MACD死叉
    - divergence_bull: 底背离
    - divergence_bear: 顶背离
    """
    
    # 内置策略
    STRATEGIES = {
        'ma_bull': {
            'name': '均线多头排列',
            'description': 'MA5 > MA10 > MA20',
            'market': ['a', 'hk', 'us']
        },
        'ma_bear': {
            'name': '均线空头排列',
            'description': 'MA5 < MA10 < MA20',
            'market': ['a', 'hk', 'us']
        },
        'breakout_up': {
            'name': '向上突破',
            'description': '突破20日高点',
            'market': ['a', 'hk', 'us']
        },
        'breakout_down': {
            'name': '向下突破',
            'description': '跌破20日低点',
            'market': ['a', 'hk', 'us']
        },
        'rsi_oversold': {
            'name': 'RSI超卖',
            'description': 'RSI < 30',
            'market': ['a', 'hk', 'us']
        },
        'rsi_overbought': {
            'name': 'RSI超买',
            'description': 'RSI > 70',
            'market': ['a', 'hk', 'us']
        },
        'volume_break': {
            'name': '放量突破',
            'description': '放量 + 突破',
            'market': ['a', 'hk', 'us']
        },
        'macd_golden': {
            'name': 'MACD金叉',
            'description': 'MACD上穿信号线',
            'market': ['a', 'hk', 'us']
        },
        'macd_death': {
            'name': 'MACD死叉',
            'description': 'MACD下穿信号线',
            'market': ['a', 'hk', 'us']
        },
        'near_ma20': {
            'name': '回踩MA20',
            'description': '价格接近MA20',
            'market': ['a', 'hk', 'us']
        },
        'strong_uptrend': {
            'name': '强势上涨',
            'description': '涨幅>5% + 量比>1.5',
            'market': ['a', 'hk', 'us']
        }
    }
    
    def __init__(self):
        self.cache = {}
    
    def screen(
        self,
        strategy: str,
        market: str = 'a',
        symbols: List[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        执行筛选策略
        
        Args:
            strategy: 策略名称
            market: 市场类型 (a/hk/us)
            symbols: 股票列表 (可选，默认全市场)
            limit: 返回数量
            
        Returns:
            [
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'price': 1500.0,
                    'change_pct': 2.5,
                    'match_score': 0.85,
                    'indicators': {...}
                }
            ]
        """
        if strategy not in self.STRATEGIES:
            return []
        
        # 获取股票列表
        if symbols is None:
            symbols = self._get_market_symbols(market, limit=500)
        
        # 执行筛选
        results = []
        strategy_func = getattr(self, f'_screen_{strategy}', None)
        
        if strategy_func:
            for symbol in symbols[:limit * 3]:  # 多获取一些用于筛选
                try:
                    ohlcv = self._get_ohlcv(symbol, market)
                    if ohlcv is not None and not ohlcv.empty:
                        match = strategy_func(ohlcv)
                        if match['matched']:
                            quote = self._get_quote(symbol, market)
                            results.append({
                                'symbol': symbol,
                                'name': quote.get('name', ''),
                                'price': quote.get('price', 0),
                                'change_pct': quote.get('change_pct', 0),
                                'match_score': match['score'],
                                'indicators': match['indicators'],
                                'market': market
                            })
                except:
                    continue
        
        # 按匹配度排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results[:limit]
    
    def screen_multi(
        self,
        strategies: List[str],
        market: str = 'a',
        mode: str = 'and',
        limit: int = 50
    ) -> List[Dict]:
        """
        多策略组合筛选
        
        Args:
            strategies: 策略列表
            market: 市场类型
            mode: 组合模式 (and/or)
            limit: 返回数量
            
        Returns:
            [
                {
                    'symbol': '600519',
                    'matched_strategies': ['ma_bull', 'macd_golden'],
                    'combined_score': 0.9,
                    ...
                }
            ]
        """
        symbols = self._get_market_symbols(market, limit=500)
        results = []
        
        for symbol in symbols[:limit * 3]:
            try:
                ohlcv = self._get_ohlcv(symbol, market)
                if ohlcv is None or ohlcv.empty:
                    continue
                
                # 检查每个策略
                matched_strategies = []
                scores = []
                
                for strategy in strategies:
                    strategy_func = getattr(self, f'_screen_{strategy}', None)
                    if strategy_func:
                        match = strategy_func(ohlcv)
                        if match['matched']:
                            matched_strategies.append(strategy)
                            scores.append(match['score'])
                
                # 根据模式判断是否匹配
                should_include = False
                if mode == 'and' and len(matched_strategies) == len(strategies):
                    should_include = True
                elif mode == 'or' and len(matched_strategies) > 0:
                    should_include = True
                
                if should_include:
                    quote = self._get_quote(symbol, market)
                    combined_score = np.mean(scores) if scores else 0
                    
                    results.append({
                        'symbol': symbol,
                        'name': quote.get('name', ''),
                        'price': quote.get('price', 0),
                        'change_pct': quote.get('change_pct', 0),
                        'matched_strategies': matched_strategies,
                        'combined_score': round(combined_score, 2),
                        'market': market
                    })
            
            except:
                continue
        
        # 排序
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return results[:limit]
    
    def _get_market_symbols(self, market: str, limit: int = 500) -> List[str]:
        """获取市场股票列表"""
        try:
            if market == 'a':
                import akshare as ak
                df = ak.stock_zh_a_spot_em()
                return df['代码'].head(limit).tolist()
            elif market == 'hk':
                import akshare as ak
                df = ak.stock_hk_spot_em()
                return df['代码'].head(limit).tolist()
            elif market == 'us':
                # 美股使用热门股票
                return [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
                    'TSLA', 'META', 'BRK.B', 'JPM', 'V',
                    'JNJ', 'UNH', 'HD', 'PG', 'MA',
                    'DIS', 'PYPL', 'ADBE', 'NFLX', 'INTC'
                ] * 25  # 扩展列表
        except:
            return []
        
        return []
    
    def _get_ohlcv(self, symbol: str, market: str):
        """获取K线数据"""
        try:
            if market == 'a':
                import akshare as ak
                df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')
                return df
            elif market == 'hk':
                import akshare as ak
                df = ak.stock_hk_daily(symbol=symbol, adjust='qfq')
                return df
            elif market == 'us':
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period='3mo')
        except:
            return None
    
    def _get_quote(self, symbol: str, market: str) -> Dict:
        """获取行情数据"""
        try:
            if market == 'a':
                import akshare as ak
                df = ak.stock_zh_a_spot_em()
                row = df[df['代码'] == symbol].iloc[0]
                return {
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change_pct': float(row['涨跌幅'])
                }
            elif market == 'us':
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                return {
                    'name': info.get('shortName', ''),
                    'price': info.get('currentPrice', 0),
                    'change_pct': (info.get('currentPrice', 0) - info.get('previousClose', 0)) / info.get('previousClose', 1) * 100
                }
        except:
            pass
        
        return {'name': '', 'price': 0, 'change_pct': 0}
    
    # === 筛选策略实现 ===
    
    def _screen_ma_bull(self, ohlcv: pd.DataFrame) -> Dict:
        """均线多头排列"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        
        matched = ma5 > ma10 > ma20
        score = 0.9 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'ma5': round(ma5, 2),
                'ma10': round(ma10, 2),
                'ma20': round(ma20, 2)
            }
        }
    
    def _screen_ma_bear(self, ohlcv: pd.DataFrame) -> Dict:
        """均线空头排列"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        
        matched = ma5 < ma10 < ma20
        score = 0.9 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'ma5': round(ma5, 2),
                'ma10': round(ma10, 2),
                'ma20': round(ma20, 2)
            }
        }
    
    def _screen_breakout_up(self, ohlcv: pd.DataFrame) -> Dict:
        """向上突破"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        high = ohlcv['最高'] if '最高' in ohlcv else ohlcv['High']
        
        current = close.iloc[-1]
        high_20 = high.iloc[-21:-1].max()
        
        matched = current > high_20
        score = 0.85 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'current': round(current, 2),
                'high_20': round(high_20, 2),
                'breakout_pct': round((current - high_20) / high_20 * 100, 2) if matched else 0
            }
        }
    
    def _screen_breakout_down(self, ohlcv: pd.DataFrame) -> Dict:
        """向下突破"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        low = ohlcv['最低'] if '最低' in ohlcv else ohlcv['Low']
        
        current = close.iloc[-1]
        low_20 = low.iloc[-21:-1].min()
        
        matched = current < low_20
        score = 0.85 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'current': round(current, 2),
                'low_20': round(low_20, 2),
                'breakout_pct': round((current - low_20) / low_20 * 100, 2) if matched else 0
            }
        }
    
    def _screen_rsi_oversold(self, ohlcv: pd.DataFrame) -> Dict:
        """RSI超卖"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        # 计算RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_value = rsi.iloc[-1]
        matched = rsi_value < 30
        score = (30 - rsi_value) / 30 if matched else 0.0
        
        return {
            'matched': matched,
            'score': round(score, 2),
            'indicators': {
                'rsi': round(rsi_value, 2)
            }
        }
    
    def _screen_rsi_overbought(self, ohlcv: pd.DataFrame) -> Dict:
        """RSI超买"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_value = rsi.iloc[-1]
        matched = rsi_value > 70
        score = (rsi_value - 70) / 30 if matched else 0.0
        
        return {
            'matched': matched,
            'score': round(score, 2),
            'indicators': {
                'rsi': round(rsi_value, 2)
            }
        }
    
    def _screen_volume_break(self, ohlcv: pd.DataFrame) -> Dict:
        """放量突破"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        volume = ohlcv['成交量'] if '成交量' in ohlcv else ohlcv['Volume']
        high = ohlcv['最高'] if '最高' in ohlcv else ohlcv['High']
        
        # 量比
        avg_volume = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        # 突破
        current_price = close.iloc[-1]
        high_20 = high.iloc[-21:-1].max()
        
        matched = volume_ratio > 1.5 and current_price > high_20
        score = min((volume_ratio - 1) / 2, 1.0) if matched else 0.0
        
        return {
            'matched': matched,
            'score': round(score, 2),
            'indicators': {
                'volume_ratio': round(volume_ratio, 2),
                'current_price': round(current_price, 2),
                'high_20': round(high_20, 2)
            }
        }
    
    def _screen_macd_golden(self, ohlcv: pd.DataFrame) -> Dict:
        """MACD金叉"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        # 计算MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        
        # 金叉判断
        matched = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]
        score = 0.9 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'macd': round(macd.iloc[-1], 4),
                'signal': round(signal.iloc[-1], 4)
            }
        }
    
    def _screen_macd_death(self, ohlcv: pd.DataFrame) -> Dict:
        """MACD死叉"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        
        matched = macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]
        score = 0.9 if matched else 0.0
        
        return {
            'matched': matched,
            'score': score,
            'indicators': {
                'macd': round(macd.iloc[-1], 4),
                'signal': round(signal.iloc[-1], 4)
            }
        }
    
    def _screen_near_ma20(self, ohlcv: pd.DataFrame) -> Dict:
        """回踩MA20"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        
        current = close.iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        
        # 距离MA20的百分比
        distance_pct = abs(current - ma20) / ma20 * 100
        
        matched = distance_pct < 2  # 2%以内
        score = (2 - distance_pct) / 2 if matched else 0.0
        
        return {
            'matched': matched,
            'score': round(score, 2),
            'indicators': {
                'current': round(current, 2),
                'ma20': round(ma20, 2),
                'distance_pct': round(distance_pct, 2)
            }
        }
    
    def _screen_strong_uptrend(self, ohlcv: pd.DataFrame) -> Dict:
        """强势上涨"""
        close = ohlcv['收盘'] if '收盘' in ohlcv else ohlcv['Close']
        volume = ohlcv['成交量'] if '成交量' in ohlcv else ohlcv['Volume']
        
        # 涨幅
        change_pct = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
        
        # 量比
        avg_volume = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        matched = change_pct > 5 and volume_ratio > 1.5
        score = min(change_pct / 10, 1.0) if matched else 0.0
        
        return {
            'matched': matched,
            'score': round(score, 2),
            'indicators': {
                'change_pct': round(change_pct, 2),
                'volume_ratio': round(volume_ratio, 2)
            }
        }


def screen_stocks(
    strategy: str,
    market: str = 'a',
    limit: int = 50
) -> List[Dict]:
    """股票筛选入口"""
    screener = StockScreener()
    return screener.screen(strategy, market, limit=limit)


def screen_multi_strategies(
    strategies: List[str],
    market: str = 'a',
    mode: str = 'and',
    limit: int = 50
) -> List[Dict]:
    """多策略筛选入口"""
    screener = StockScreener()
    return screener.screen_multi(strategies, market, mode, limit)


def list_strategies() -> Dict:
    """列出所有策略"""
    return StockScreener.STRATEGIES


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='股票筛选器')
    parser.add_argument('--strategy', help='策略名称')
    parser.add_argument('--strategies', nargs='+', help='多策略组合')
    parser.add_argument('--market', default='a', help='市场类型 (a/hk/us)')
    parser.add_argument('--mode', default='and', help='组合模式 (and/or)')
    parser.add_argument('--limit', type=int, default=20, help='返回数量')
    parser.add_argument('--list', action='store_true', help='列出所有策略')
    
    args = parser.parse_args()
    
    if args.list:
        result = list_strategies()
    elif args.strategies:
        result = screen_multi_strategies(args.strategies, args.market, args.mode, args.limit)
    elif args.strategy:
        result = screen_stocks(args.strategy, args.market, args.limit)
    else:
        result = list_strategies()
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
