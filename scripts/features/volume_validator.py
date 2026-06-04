#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成交量验证器 - 整合自 technical-analysis
核心原则: "Volume Validates - Volume confirms or denies price moves"
"""

import sys
import os
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class VolumeValidator:
    """
    成交量验证器
    
    来自 technical-analysis:
    - "Breakout on low volume = likely false"
    - "Reversal on climactic volume = likely real"
    """
    
    VOLUME_THRESHOLDS = {
        'very_low': 0.5,
        'low': 0.8,
        'normal': 1.0,
        'high': 1.5,
        'very_high': 2.0,
        'climactic': 3.0
    }
    
    def validate_signal(self, symbol: str, signal: Dict, ohlcv: pd.DataFrame = None) -> Dict:
        result = {
            'symbol': symbol,
            'is_valid': True,
            'volume_ratio': 1.0,
            'validation_type': None,
            'confidence_adjustment': 1.0,
            'warnings': [],
            'strengths': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            if ohlcv is None:
                ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is None or ohlcv.empty:
                result['warnings'].append('无法获取成交量数据')
                return result
            
            volume_analysis = self._analyze_volume(ohlcv)
            result['volume_ratio'] = volume_analysis['ratio']
            result['volume_trend'] = volume_analysis['trend']
            
            signal_type = signal.get('signal', '')
            
            if 'breakout' in signal_type.lower() or signal.get('action') == 'buy':
                result['validation_type'] = 'breakout'
                result.update(self._validate_breakout(volume_analysis, signal))
            elif 'breakdown' in signal_type.lower() or signal.get('action') == 'sell':
                result['validation_type'] = 'breakdown'
                result.update(self._validate_breakdown(volume_analysis, signal))
            elif 'reversal' in signal_type.lower():
                result['validation_type'] = 'reversal'
                result.update(self._validate_reversal(volume_analysis, signal))
            else:
                result.update(self._validate_general(volume_analysis, signal))
        
        except Exception as e:
            result['warnings'].append(f'验证异常: {str(e)}')
        
        return result
    
    def _get_ohlcv(self, symbol: str):
        try:
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="3mo")
            else:
                import akshare as ak
                return ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        except:
            return None
    
    def _analyze_volume(self, ohlcv: pd.DataFrame) -> Dict:
        volume = ohlcv['Volume'] if 'Volume' in ohlcv else ohlcv['成交量']
        close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
        
        current_volume = volume.iloc[-1]
        avg_volume = volume.rolling(20).mean().iloc[-1]
        ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        recent_avg = volume.tail(5).mean()
        previous_avg = volume.iloc[-10:-5].mean()
        volume_trend = 'increasing' if recent_avg > previous_avg else 'decreasing'
        
        price_change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
        
        return {
            'ratio': round(ratio, 2),
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'trend': volume_trend,
            'price_change': round(price_change, 2),
            'level': self._get_volume_level(ratio)
        }
    
    def _get_volume_level(self, ratio: float) -> str:
        if ratio >= self.VOLUME_THRESHOLDS['climactic']:
            return 'climactic'
        elif ratio >= self.VOLUME_THRESHOLDS['very_high']:
            return 'very_high'
        elif ratio >= self.VOLUME_THRESHOLDS['high']:
            return 'high'
        elif ratio >= self.VOLUME_THRESHOLDS['normal']:
            return 'normal'
        elif ratio >= self.VOLUME_THRESHOLDS['low']:
            return 'low'
        else:
            return 'very_low'
    
    def _validate_breakout(self, volume_analysis: Dict, signal: Dict) -> Dict:
        result = {'is_valid': True, 'confidence_adjustment': 1.0, 'warnings': [], 'strengths': []}
        ratio = volume_analysis['ratio']
        
        if ratio >= self.VOLUME_THRESHOLDS['high']:
            result['confidence_adjustment'] = 1.3
            result['strengths'].append(f'放量突破 (量比{ratio:.2f})')
        elif ratio >= self.VOLUME_THRESHOLDS['normal']:
            result['confidence_adjustment'] = 1.0
            result['strengths'].append('正常量突破')
        elif ratio >= self.VOLUME_THRESHOLDS['low']:
            result['confidence_adjustment'] = 0.7
            result['warnings'].append(f'缩量突破 (量比{ratio:.2f})，假突破风险高')
        else:
            result['is_valid'] = False
            result['confidence_adjustment'] = 0.4
            result['warnings'].append(f'极缩量突破 (量比{ratio:.2f})，强烈建议观望')
        
        if ratio >= self.VOLUME_THRESHOLDS['climactic']:
            result['warnings'].append('巨量突破，注意是否短期过热')
            result['confidence_adjustment'] *= 0.9
        
        return result
    
    def _validate_breakdown(self, volume_analysis: Dict, signal: Dict) -> Dict:
        result = {'is_valid': True, 'confidence_adjustment': 1.0, 'warnings': [], 'strengths': []}
        ratio = volume_analysis['ratio']
        
        if ratio >= self.VOLUME_THRESHOLDS['high']:
            result['confidence_adjustment'] = 1.2
            result['strengths'].append(f'放量跌破 (量比{ratio:.2f})')
        elif ratio >= self.VOLUME_THRESHOLDS['low']:
            result['confidence_adjustment'] = 1.0
            result['strengths'].append('正常量跌破')
        else:
            result['confidence_adjustment'] = 0.6
            result['warnings'].append(f'缩量跌破 (量比{ratio:.2f})，可能是假跌破')
        
        return result
    
    def _validate_reversal(self, volume_analysis: Dict, signal: Dict) -> Dict:
        result = {'is_valid': True, 'confidence_adjustment': 1.0, 'warnings': [], 'strengths': []}
        ratio = volume_analysis['ratio']
        
        if ratio >= self.VOLUME_THRESHOLDS['climactic']:
            result['confidence_adjustment'] = 1.5
            result['strengths'].append(f'巨量反转 (量比{ratio:.2f})，可靠性极高')
        elif ratio >= self.VOLUME_THRESHOLDS['high']:
            result['confidence_adjustment'] = 1.3
            result['strengths'].append(f'放量反转 (量比{ratio:.2f})')
        elif ratio >= self.VOLUME_THRESHOLDS['normal']:
            result['confidence_adjustment'] = 1.0
            result['strengths'].append('正常量反转')
        else:
            result['confidence_adjustment'] = 0.5
            result['warnings'].append(f'缩量反转 (量比{ratio:.2f})，可靠性低')
        
        return result
    
    def _validate_general(self, volume_analysis: Dict, signal: Dict) -> Dict:
        ratio = volume_analysis['ratio']
        result = {'is_valid': True, 'confidence_adjustment': 1.0, 'warnings': [], 'strengths': []}
        
        if ratio >= self.VOLUME_THRESHOLDS['high']:
            result['confidence_adjustment'] = 1.2
            result['strengths'].append(f'成交量活跃 (量比{ratio:.2f})')
        elif ratio < self.VOLUME_THRESHOLDS['low']:
            result['confidence_adjustment'] = 0.8
            result['warnings'].append(f'成交量低迷 (量比{ratio:.2f})')
        
        return result


def validate_signal_volume(symbol: str, signal: Dict, ohlcv: pd.DataFrame = None) -> Dict:
    validator = VolumeValidator()
    return validator.validate_signal(symbol, signal, ohlcv)


if __name__ == '__main__':
    test_signal = {
        'signal': 'multi_timeframe_bullish',
        'action': 'buy',
        'name': '多时间框架多头对齐'
    }
    
    result = validate_signal_volume('AAPL', test_signal)
    
    print("=" * 60)
    print("成交量验证结果")
    print("=" * 60)
    print(f"股票: {result['symbol']}")
    print(f"量比: {result['volume_ratio']}")
    print(f"验证类型: {result['validation_type']}")
    print(f"是否有效: {result['is_valid']}")
    print(f"置信度调整: {result['confidence_adjustment']}")
    print(f"优势: {result['strengths']}")
    print(f"警告: {result['warnings']}")
