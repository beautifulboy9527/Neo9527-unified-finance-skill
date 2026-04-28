#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
入场信号分析器 - 整合自 entry-signals
内置信号库仅作规则参考；当前版本不代表已针对请求标的完成实时历史回测。
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 内置信号库。success_rate/samples 是规则库元数据，不等同于当前标的实时回测结果。
SIGNAL_STATS_VERIFIED = False

HIGH_CONFIDENCE_SIGNALS = {
    'multi_timeframe_bullish': {
        'name': '多时间框架多头对齐',
        'pattern': '15m/1h/4h 全部多头',
        'success_rate': 0.88,
        'samples': 164,
        'confidence': 0.85,
        'action': 'buy',
        'risk_level': 'low',
        'description': 'Multi-timeframe bullish alignment (15m, 1h, 4h) WITH explicit risk validation'
    },
    'sma_macd_bullish': {
        'name': 'SMA金叉 + MACD多头',
        'pattern': 'SMA金叉 + MACD金叉 + 布林中性',
        'success_rate': 0.82,
        'samples': 184,
        'confidence': 0.80,
        'action': 'buy',
        'risk_level': 'low',
        'description': 'SMA crossover + bullish MACD + neutral Bollinger'
    },
    'scale_winning': {
        'name': '加仓获胜仓位',
        'pattern': '已有盈利仓位 + 趋势延续',
        'success_rate': 0.80,
        'samples': 157,
        'confidence': 0.75,
        'action': 'add_position',
        'risk_level': 'medium',
        'description': 'Scaling into existing winning position'
    },
    'multi_timeframe_bearish': {
        'name': '多时间框架空头对齐',
        'pattern': '15m/1h/4h 全部空头',
        'success_rate': 0.65,
        'samples': 103,
        'confidence': 0.95,
        'action': 'sell',
        'risk_level': 'medium',
        'description': 'Multi-timeframe bearish alignment for short'
    },
    'rsi_divergence': {
        'name': 'RSI背离',
        'pattern': '价格创新高但RSI未创新高',
        'success_rate': 0.45,
        'samples': 79,
        'confidence': 0.60,
        'action': 'watch',
        'risk_level': 'high',
        'description': 'Relative strength divergence'
    }
}

MEDIUM_CONFIDENCE_SIGNALS = {
    'high_funding_rate': {
        'name': '高资金费率做多',
        'pattern': '资金费率异常高',
        'success_rate': 0.35,
        'samples': 248,
        'confidence': 0.75,
        'action': 'avoid',
        'risk_level': 'very_high',
        'description': 'High funding rate alone as bullish signal (low success)'
    },
    'rsi_overbought_macd_bearish': {
        'name': 'RSI超买 + MACD空头',
        'pattern': 'RSI > 70 + MACD死叉',
        'success_rate': 0.30,
        'samples': 35,
        'confidence': 0.95,
        'action': 'sell',
        'risk_level': 'high',
        'description': 'RSI overbought + MACD bearish as short signal'
    }
}


class MultiTimeframeAnalyzer:
    """多时间框架分析器"""
    
    TIMEFRAMES = ['15m', '1h', '4h', '1d']
    
    def analyze(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        多时间框架分析
        
        Args:
            symbol: 股票代码
            timeframes: 时间框架列表
            
        Returns:
            {
                'alignment': 'bullish/bearish/mixed',
                'timeframes': {...},
                'confidence': 0.85,
                'success_rate': 0.88
            }
        """
        if timeframes is None:
            timeframes = ['1h', '4h', '1d']  # 股票默认用较长周期
        
        result = {
            'symbol': symbol,
            'timeframes': {},
            'alignment': 'mixed',
            'confidence': 0.5,
            'success_rate': 0.5,
            'signal': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            trends = {}
            
            for tf in timeframes:
                ohlcv = self._get_ohlcv(symbol, tf)
                if ohlcv is not None and not ohlcv.empty:
                    trend = self._analyze_trend(ohlcv)
                    trends[tf] = trend
                    result['timeframes'][tf] = trend
            
            # 判断对齐
            if trends:
                trend_values = [t['trend'] for t in trends.values()]
                
                if all(t == 'bullish' for t in trend_values):
                    result['alignment'] = 'bullish'
                    result['confidence'] = 0.85
                    result['success_rate'] = 0.88
                    result['signal'] = 'multi_timeframe_bullish'
                elif all(t == 'bearish' for t in trend_values):
                    result['alignment'] = 'bearish'
                    result['confidence'] = 0.95
                    result['success_rate'] = 0.65
                    result['signal'] = 'multi_timeframe_bearish'
                else:
                    result['alignment'] = 'mixed'
                    result['confidence'] = 0.5
                    result['success_rate'] = 0.5
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_ohlcv(self, symbol: str, timeframe: str):
        """获取指定时间框架的K线数据"""
        try:
            # 简化实现：获取日线数据
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="3mo")
            else:
                import akshare as ak
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
                return df
        except:
            return None
    
    def _analyze_trend(self, ohlcv) -> Dict:
        """分析趋势"""
        result = {'trend': 'neutral', 'score': 5}
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            ma5 = close.rolling(5).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            current = close.iloc[-1]
            
            if current > ma5 > ma20:
                result['trend'] = 'bullish'
                result['score'] = 8
                result['desc'] = '多头'
            elif current < ma5 < ma20:
                result['trend'] = 'bearish'
                result['score'] = 2
                result['desc'] = '空头'
            else:
                result['trend'] = 'neutral'
                result['score'] = 5
                result['desc'] = '震荡'
        except:
            pass
        
        return result


class SignalDetector:
    """入场信号检测器"""
    
    def __init__(self):
        self.mtf_analyzer = MultiTimeframeAnalyzer()
    
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
    
    def detect(self, symbol: str) -> List[Dict]:
        """
        检测入场信号
        
        Args:
            symbol: 股票代码
            
        Returns:
            [
                {
                    'signal': 'multi_timeframe_bullish',
                    'name': '多时间框架多头对齐',
                    'success_rate': 0.88,
                    'confidence': 0.85,
                    'action': 'buy',
                    'risk_level': 'low'
                }
            ]
        """
        signals = []
        
        try:
            # 1. 多时间框架信号
            mtf = self.mtf_analyzer.analyze(symbol)
            if mtf['signal']:
                signal_data = HIGH_CONFIDENCE_SIGNALS.get(mtf['signal'])
                if signal_data:
                    signals.append({
                        'signal': mtf['signal'],
                        'name': signal_data['name'],
                        'success_rate': signal_data['success_rate'],
                        'samples': signal_data['samples'],
                        'confidence': mtf['confidence'],
                        'action': signal_data['action'],
                        'risk_level': signal_data['risk_level'],
                        'description': signal_data['description']
                    })
            
            # 2. SMA + MACD 信号
            sma_macd = self._detect_sma_macd_signal(symbol)
            if sma_macd:
                signals.append(sma_macd)
            
            # 3. RSI 背离信号
            rsi_div = self._detect_rsi_divergence(symbol)
            if rsi_div:
                signals.append(rsi_div)
        
        except Exception as e:
            pass
        
        for signal in signals:
            signal['stats_verified'] = SIGNAL_STATS_VERIFIED
            signal['score_type'] = 'rule_library'
            signal['description'] = (
                f"{signal.get('description', '')} | "
                "未针对当前标的执行实时历史回测，需二次验证。"
            )
        
        return signals
    
    def _detect_sma_macd_signal(self, symbol: str) -> Optional[Dict]:
        """检测 SMA + MACD 组合信号"""
        try:
            import yfinance as yf
            
            # 标准化股票代码
            yf_symbol = self._normalize_for_yfinance(symbol)
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                return None
            
            close = hist['Close'] if 'Close' in hist else hist['收盘']
            
            # SMA
            ma5 = close.rolling(5).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            sma_bullish = ma5 > ma20
            
            # MACD
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            macd_bullish = macd.iloc[-1] > signal.iloc[-1]
            
            # 金叉检测
            golden_cross = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]
            
            if sma_bullish and macd_bullish:
                return {
                    'signal': 'sma_macd_bullish',
                    'name': 'SMA金叉 + MACD多头',
                    'success_rate': 0.82,
                    'samples': 184,
                    'confidence': 0.80 if golden_cross else 0.75,
                    'action': 'buy',
                    'risk_level': 'low',
                    'description': 'SMA crossover + bullish MACD'
                }
            
            # 空头信号
            sma_bearish = ma5 < ma20
            macd_bearish = macd.iloc[-1] < signal.iloc[-1]
            death_cross = macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]
            
            if sma_bearish and macd_bearish:
                return {
                    'signal': 'sma_macd_bearish',
                    'name': 'SMA死叉 + MACD空头',
                    'success_rate': 0.65,
                    'samples': 50,
                    'confidence': 0.80 if death_cross else 0.70,
                    'action': 'sell',
                    'risk_level': 'medium',
                    'description': 'SMA death cross + bearish MACD'
                }
        
        except:
            pass
        
        return None
    
    def _detect_rsi_divergence(self, symbol: str) -> Optional[Dict]:
        """检测 RSI 背离"""
        try:
            import yfinance as yf
            
            # 标准化股票代码
            yf_symbol = self._normalize_for_yfinance(symbol)
            
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="3mo")
            
            if hist.empty:
                return None
            
            close = hist['Close'] if 'Close' in hist else hist['收盘']
            
            # 计算 RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # 检测背离
            recent_close = close.tail(20)
            recent_rsi = rsi.tail(20)
            
            # 价格创新高但RSI未创新高 (顶背离)
            if recent_close.iloc[-1] > recent_close.iloc[:-1].max():
                if recent_rsi.iloc[-1] < recent_rsi.iloc[:-1].max():
                    return {
                        'signal': 'rsi_bearish_divergence',
                        'name': 'RSI顶背离',
                        'success_rate': 0.45,
                        'samples': 79,
                        'confidence': 0.60,
                        'action': 'watch',
                        'risk_level': 'high',
                        'description': 'Price makes new high but RSI does not'
                    }
            
            # 价格创新低但RSI未创新低 (底背离)
            if recent_close.iloc[-1] < recent_close.iloc[:-1].min():
                if recent_rsi.iloc[-1] > recent_rsi.iloc[:-1].min():
                    return {
                        'signal': 'rsi_bullish_divergence',
                        'name': 'RSI底背离',
                        'success_rate': 0.50,
                        'samples': 85,
                        'confidence': 0.60,
                        'action': 'watch',
                        'risk_level': 'medium',
                        'description': 'Price makes new low but RSI does not'
                    }
        
        except:
            pass
        
        return None


class SignalScorer:
    """信号评分器"""
    
    def calculate_overall_score(self, signals: List[Dict]) -> Dict:
        """
        计算综合信号评分
        
        Args:
            signals: 信号列表
            
        Returns:
            {
                'overall_score': 85,
                'confidence': 0.85,
                'action': 'buy',
                'risk_level': 'low',
                'signals_count': 2,
                'top_signal': '...'
            }
        """
        if not signals:
            return {
                'overall_score': 0,
                'confidence': 0,
                'action': 'hold',
                'risk_level': 'unknown',
                'signals_count': 0
            }
        
        # 按成功率排序
        sorted_signals = sorted(signals, key=lambda x: x['success_rate'], reverse=True)
        top_signal = sorted_signals[0]
        
        # 加权平均成功率
        total_weight = sum(s.get('samples', 100) for s in signals)
        weighted_success = sum(
            s['success_rate'] * s.get('samples', 100) 
            for s in signals
        ) / total_weight
        
        # 综合置信度
        avg_confidence = sum(s['confidence'] for s in signals) / len(signals)
        
        # 转换为 0-100 分
        overall_score = int(weighted_success * 100)
        
        # 确定操作
        if overall_score >= 80:
            action = 'buy'
            risk = 'low'
        elif overall_score >= 65:
            action = 'buy'
            risk = 'medium'
        elif overall_score >= 50:
            action = 'watch'
            risk = 'medium'
        elif overall_score >= 35:
            action = 'hold'
            risk = 'high'
        else:
            action = 'avoid'
            risk = 'very_high'
        
        return {
            'overall_score': overall_score,
            'confidence': round(avg_confidence, 2),
            'action': action,
            'risk_level': risk,
            'signals_count': len(signals),
            'top_signal': top_signal['name'],
            'all_signals': [s['name'] for s in signals],
            'stats_verified': SIGNAL_STATS_VERIFIED,
            'score_type': 'rule_library'
        }


def analyze_entry_signals(symbol: str) -> Dict:
    """
    入场信号分析入口
    
    Args:
        symbol: 股票代码
        
    Returns:
        {
            'symbol': 'AAPL',
            'signals': [...],
            'score': {...},
            'recommendation': '...'
        }
    """
    detector = SignalDetector()
    scorer = SignalScorer()
    
    # 检测信号
    signals = detector.detect(symbol)
    
    # 计算评分
    score = scorer.calculate_overall_score(signals)
    
    # 生成建议
    if score['action'] == 'buy':
        if score['confidence'] >= 0.80:
            recommendation = f"规则库偏多信号，规则分 {score['overall_score']}，置信度 {score['confidence']}；需针对当前标的回测验证"
        else:
            recommendation = f"规则库偏多信号，规则分 {score['overall_score']}，置信度 {score['confidence']}；需二次验证"
    elif score['action'] == 'sell':
        recommendation = f"规则库偏空信号，规则分 {score['overall_score']}，置信度 {score['confidence']}；需针对当前标的回测验证"
    elif score['action'] == 'watch':
        recommendation = f"观望信号，建议等待更好入场点"
    else:
        recommendation = f"不建议操作，风险较高"
    
    return {
        'symbol': symbol,
        'signals': signals,
        'score': score,
        'recommendation': recommendation,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='入场信号分析')
    parser.add_argument('symbol', help='股票代码')
    
    args = parser.parse_args()
    
    result = analyze_entry_signals(args.symbol)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
