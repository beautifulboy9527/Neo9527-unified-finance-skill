#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三层分析框架 - 整合自 sm-analyze
宏观(20分) → 行业(20分) → 个股(60分) → 综合评分(100分)
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MacroAnalyzer:
    """宏观分析器 (20分)"""
    
    def analyze(self, market: str = 'cn') -> Dict:
        result = {
            'market': market,
            'cycle': 'range',
            'cycle_score': 8,
            'flow_score': 4,
            'total_score': 12,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            if market == 'cn':
                result = self._analyze_cn_market()
            elif market == 'us':
                result = self._analyze_us_market()
            elif market == 'hk':
                result = self._analyze_hk_market()
        except Exception as e:
            result['error'] = str(e)
        
        result['total_score'] = result.get('cycle_score', 8) + result.get('flow_score', 4)
        return result
    
    def _analyze_cn_market(self) -> Dict:
        result = {'market': 'cn', 'cycle': 'range', 'cycle_score': 8, 'flow_score': 4}
        
        try:
            import akshare as ak
            
            df = ak.stock_zh_index_daily(symbol="sh000300")
            if not df.empty:
                close = df['close'].iloc[-1]
                ma20 = df['close'].rolling(20).mean().iloc[-1]
                change_60d = (close - df['close'].iloc[-60]) / df['close'].iloc[-60] * 100
                
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                    result['cycle_desc'] = '牛市'
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                    result['cycle_desc'] = '熊市'
                else:
                    result['cycle'] = 'range'
                    result['cycle_score'] = 8
                    result['cycle_desc'] = '震荡'
                
                result['hs300'] = round(close, 2)
                result['hs300_ma20'] = round(ma20, 2)
        except:
            pass
        
        try:
            import akshare as ak
            north_flow = ak.stock_em_hsgt_north_net_flow_in(indicator="北向资金")
            if not north_flow.empty:
                flow_5d = north_flow['北向资金'].tail(5).sum()
                result['north_flow_5d'] = round(flow_5d, 2)
                
                if flow_5d > 50:
                    result['flow_score'] = 8
                    result['flow_signal'] = '外资积极'
                elif flow_5d < -50:
                    result['flow_score'] = 2
                    result['flow_signal'] = '外资撤退'
                else:
                    result['flow_score'] = 4
                    result['flow_signal'] = '外资观望'
        except:
            pass
        
        return result
    
    def _analyze_us_market(self) -> Dict:
        result = {'market': 'us', 'cycle': 'range', 'cycle_score': 8, 'flow_score': 4}
        
        try:
            import yfinance as yf
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="3mo")
            
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change_60d = (close - hist['Close'].iloc[-60]) / hist['Close'].iloc[-60] * 100
                
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                
                result['sp500'] = round(close, 2)
        except:
            pass
        
        return result
    
    def _analyze_hk_market(self) -> Dict:
        result = {'market': 'hk', 'cycle': 'range', 'cycle_score': 8, 'flow_score': 4}
        
        try:
            import yfinance as yf
            hsi = yf.Ticker("^HSI")
            hist = hsi.history(period="3mo")
            
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change_60d = (close - hist['Close'].iloc[-60]) / hist['Close'].iloc[-60] * 100
                
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                
                result['hsi'] = round(close, 2)
        except:
            pass
        
        return result


class SectorAnalyzer:
    """行业分析器 (20分)"""
    
    def analyze(self, symbol: str) -> Dict:
        result = {
            'symbol': symbol,
            'relative_strength': 'following',
            'strength_score': 10,
            'flow_score': 3,
            'total_score': 13,
            'sectors': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            sectors = self._get_sectors(symbol)
            result['sectors'] = sectors
        except Exception as e:
            result['error'] = str(e)
        
        result['total_score'] = result['strength_score'] + result['flow_score']
        return result
    
    def _get_sectors(self, symbol: str) -> List[Dict]:
        sectors = []
        
        try:
            if symbol.isdigit():
                import akshare as ak
                df = ak.stock_individual_info_em(symbol=symbol)
                if not df.empty:
                    for _, row in df.iterrows():
                        if '行业' in str(row['item']) or '概念' in str(row['item']):
                            sectors.append({'name': row['item'], 'value': row['value']})
            else:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info.get('sector'):
                    sectors.append({'name': 'sector', 'value': info['sector']})
                if info.get('industry'):
                    sectors.append({'name': 'industry', 'value': info['industry']})
        except:
            pass
        
        return sectors


class StockAnalyzer:
    """个股技术分析器 (60分)"""
    
    def analyze(self, symbol: str) -> Dict:
        result = {
            'symbol': symbol,
            'trend': {},
            'trend_score': 10,
            'momentum': {},
            'momentum_score': 8,
            'volume': {},
            'volume_score': 6,
            'position': {},
            'position_score': 8,
            'total_score': 32,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is not None and not ohlcv.empty:
                result['trend'] = self._analyze_trend(ohlcv)
                result['trend_score'] = result['trend']['score']
                
                result['momentum'] = self._analyze_momentum(ohlcv)
                result['momentum_score'] = result['momentum']['score']
                
                result['volume'] = self._analyze_volume(ohlcv)
                result['volume_score'] = result['volume']['score']
                
                result['position'] = self._analyze_position(ohlcv)
                result['position_score'] = result['position']['score']
        except Exception as e:
            result['error'] = str(e)
        
        result['total_score'] = (
            result['trend_score'] + 
            result['momentum_score'] + 
            result['volume_score'] + 
            result['position_score']
        )
        
        return result
    
    def _get_ohlcv(self, symbol: str):
        try:
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="6mo")
            else:
                import akshare as ak
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
                return df
        except:
            return None
    
    def _analyze_trend(self, ohlcv) -> Dict:
        result = {'status': 'mixed', 'score': 10}
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            result['ma5'] = float(close.rolling(5).mean().iloc[-1])
            result['ma10'] = float(close.rolling(10).mean().iloc[-1])
            result['ma20'] = float(close.rolling(20).mean().iloc[-1])
            
            if result['ma5'] > result['ma10'] > result['ma20']:
                result['status'] = 'bullish'
                result['score'] = 25
                result['desc'] = '多头排列'
            elif result['ma5'] < result['ma10'] < result['ma20']:
                result['status'] = 'bearish'
                result['score'] = 5
                result['desc'] = '空头排列'
            else:
                result['status'] = 'mixed'
                result['score'] = 10
                result['desc'] = '均线纠缠'
        except:
            pass
        
        return result
    
    def _analyze_momentum(self, ohlcv) -> Dict:
        result = {'macd': {}, 'rsi': {}, 'score': 8}
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            result['rsi']['value'] = round(float(rsi.iloc[-1]), 2)
            
            if result['rsi']['value'] > 70:
                result['rsi']['status'] = 'overbought'
            elif result['rsi']['value'] < 30:
                result['rsi']['status'] = 'oversold'
            else:
                result['rsi']['status'] = 'neutral'
            
            # MACD
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            
            result['macd']['value'] = round(float(macd.iloc[-1]), 4)
            result['macd']['signal'] = round(float(signal.iloc[-1]), 4)
            
            if macd.iloc[-1] > signal.iloc[-1]:
                result['macd']['status'] = 'bullish'
            else:
                result['macd']['status'] = 'bearish'
            
            # 评分
            score = 8
            if result['rsi']['status'] == 'neutral':
                score += 3
            if result['macd']['status'] == 'bullish':
                score += 4
            result['score'] = min(score, 15)
            
        except:
            pass
        
        return result
    
    def _analyze_volume(self, ohlcv) -> Dict:
        result = {'ratio': 1.0, 'status': 'normal', 'score': 6}
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            volume = ohlcv['Volume'] if 'Volume' in ohlcv else ohlcv['成交量']
            
            avg_volume = volume.rolling(20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            result['ratio'] = round(float(current_volume / avg_volume), 2)
            
            price_change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            
            if price_change > 0 and result['ratio'] > 1.5:
                result['status'] = 'volume_up'
                result['score'] = 10
                result['desc'] = '放量上涨'
            elif price_change < 0 and result['ratio'] > 1.5:
                result['status'] = 'volume_drop'
                result['score'] = 2
                result['desc'] = '放量下跌'
            else:
                result['score'] = 6
                result['desc'] = '量价平稳'
        except:
            pass
        
        return result
    
    def _analyze_position(self, ohlcv) -> Dict:
        result = {'score': 8}
        
        try:
            high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
            low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            
            result['atr'] = round(float(atr), 4)
            result['atr_pct'] = round(float(atr / close.iloc[-1] * 100), 2)
            
            if result['atr_pct'] < 2:
                result['score'] = 10
            elif result['atr_pct'] > 4:
                result['score'] = 5
        except:
            pass
        
        return result


class AnalysisFramework:
    """完整的三层分析框架"""
    
    def __init__(self):
        self.macro = MacroAnalyzer()
        self.sector = SectorAnalyzer()
        self.stock = StockAnalyzer()
    
    def analyze(self, symbol: str, market: str = 'auto') -> Dict:
        # 自动检测市场
        if market == 'auto':
            if symbol.isdigit():
                market = 'cn'
            elif symbol.isdigit() and len(symbol) == 5:
                market = 'hk'
            else:
                market = 'us'
        
        # 三层分析
        macro_result = self.macro.analyze(market)
        sector_result = self.sector.analyze(symbol)
        stock_result = self.stock.analyze(symbol)
        
        # 总分
        total_score = (
            macro_result['total_score'] +
            sector_result['total_score'] +
            stock_result['total_score']
        )
        
        # 评级
        if total_score >= 80:
            rating = 'strong'
            suggestion = '强势 - 可积极参与'
        elif total_score >= 65:
            rating = 'bullish'
            suggestion = '偏强 - 可适度参与'
        elif total_score >= 50:
            rating = 'neutral'
            suggestion = '中性 - 观望为主'
        elif total_score >= 35:
            rating = 'bearish'
            suggestion = '偏弱 - 谨慎'
        else:
            rating = 'weak'
            suggestion = '弱势 - 回避'
        
        return {
            'symbol': symbol,
            'market': market,
            'macro': macro_result,
            'sector': sector_result,
            'stock': stock_result,
            'total_score': total_score,
            'rating': rating,
            'suggestion': suggestion,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def analyze_full(symbol: str, market: str = 'auto') -> Dict:
    """完整分析入口"""
    framework = AnalysisFramework()
    return framework.analyze(symbol, market)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='三层分析框架')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--market', default='auto', help='市场类型')
    
    args = parser.parse_args()
    
    result = analyze_full(args.symbol, args.market)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
