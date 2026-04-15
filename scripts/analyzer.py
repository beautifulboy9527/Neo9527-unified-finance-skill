#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析模块 - 技术分析决策建议
"""

import sys
import os
from typing import Dict, Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def analyze_technical_signals(
    price: float,
    ma5: float,
    ma10: float,
    ma20: float,
    rsi: float,
    macd: Dict = None,
    volume_ratio: float = None
) -> Dict:
    """
    基于技术指标生成 AI 决策建议
    
    Args:
        price: 当前价格
        ma5: 5日均线
        ma10: 10日均线
        ma20: 20日均线
        rsi: RSI 指标
        macd: MACD 数据
        volume_ratio: 量比
        
    Returns:
        AI 决策建议
    """
    result = {
        'recommendation': 'hold',
        'confidence': 0.5,
        'signals': [],
        'reasoning': []
    }
    
    # 均线分析
    ma_signals = []
    
    # 价格与均线关系
    if price > ma5 and price > ma10 and price > ma20:
        ma_signals.append({'signal': 'bullish', 'reason': '价格位于所有均线之上'})
        result['reasoning'].append('多头排列，趋势向上')
    elif price < ma5 and price < ma10 and price < ma20:
        ma_signals.append({'signal': 'bearish', 'reason': '价格位于所有均线之下'})
        result['reasoning'].append('空头排列，趋势向下')
    else:
        ma_signals.append({'signal': 'neutral', 'reason': '价格与均线交织'})
        result['reasoning'].append('趋势不明确')
    
    # 均线交叉
    if ma5 > ma10 and ma10 > ma20:
        ma_signals.append({'signal': 'bullish', 'reason': '均线多头排列'})
    elif ma5 < ma10 and ma10 < ma20:
        ma_signals.append({'signal': 'bearish', 'reason': '均线空头排列'})
    
    result['signals'].extend(ma_signals)
    
    # RSI 分析
    rsi_signal = 'neutral'
    if rsi > 80:
        rsi_signal = 'overbought'
        result['reasoning'].append('RSI 超买，可能回调')
    elif rsi > 70:
        rsi_signal = 'bullish'
        result['reasoning'].append('RSI 偏强')
    elif rsi < 20:
        rsi_signal = 'oversold'
        result['reasoning'].append('RSI 超卖，可能反弹')
    elif rsi < 30:
        rsi_signal = 'bearish'
        result['reasoning'].append('RSI 偏弱')
    else:
        result['reasoning'].append('RSI 中性')
    
    result['signals'].append({'signal': rsi_signal, 'indicator': 'RSI', 'value': rsi})
    
    # MACD 分析
    if macd:
        macd_signal = 'neutral'
        macd_val = macd.get('macd', 0)
        signal_val = macd.get('signal', 0)
        hist = macd.get('histogram', 0)
        
        if macd_val > signal_val and hist > 0:
            macd_signal = 'bullish'
            result['reasoning'].append('MACD 金叉，多头信号')
        elif macd_val < signal_val and hist < 0:
            macd_signal = 'bearish'
            result['reasoning'].append('MACD 死叉，空头信号')
        
        result['signals'].append({'signal': macd_signal, 'indicator': 'MACD'})
    
    # 成交量分析
    if volume_ratio:
        if volume_ratio > 2.0:
            result['reasoning'].append('放量明显，关注趋势方向')
        elif volume_ratio < 0.5:
            result['reasoning'].append('缩量明显，市场观望')
    
    # 综合评分
    bullish_count = sum(1 for s in result['signals'] if s.get('signal') == 'bullish')
    bearish_count = sum(1 for s in result['signals'] if s.get('signal') == 'bearish')
    
    # 决策建议
    if bullish_count >= 3:
        result['recommendation'] = 'buy'
        result['confidence'] = min(0.9, 0.5 + bullish_count * 0.1)
    elif bearish_count >= 3:
        result['recommendation'] = 'sell'
        result['confidence'] = min(0.9, 0.5 + bearish_count * 0.1)
    elif bullish_count > bearish_count:
        result['recommendation'] = 'buy'
        result['confidence'] = 0.6
    elif bearish_count > bullish_count:
        result['recommendation'] = 'sell'
        result['confidence'] = 0.6
    else:
        result['recommendation'] = 'hold'
        result['confidence'] = 0.5
    
    return result


def analyze_stock(
    symbol: str,
    basic_indicators: Dict,
    additional_data: Dict = None
) -> Dict:
    """
    综合分析股票
    
    Args:
        symbol: 股票代码
        basic_indicators: 基础指标
        additional_data: 附加数据
        
    Returns:
        综合分析结果
    """
    result = {
        'symbol': symbol,
        'analysis': {},
        'recommendation': 'hold',
        'confidence': 0.5,
        'risk_level': 'medium'
    }
    
    # 技术分析
    tech_analysis = analyze_technical_signals(
        price=basic_indicators.get('current_price', 0),
        ma5=basic_indicators.get('ma5', 0),
        ma10=basic_indicators.get('ma10', 0),
        ma20=basic_indicators.get('ma20', 0),
        rsi=basic_indicators.get('rsi', 50),
        macd=basic_indicators.get('macd'),
        volume_ratio=basic_indicators.get('volume_ratio')
    )
    
    result['analysis']['technical'] = tech_analysis
    result['recommendation'] = tech_analysis['recommendation']
    result['confidence'] = tech_analysis['confidence']
    
    # 风险评估
    rsi = basic_indicators.get('rsi', 50)
    if rsi > 80 or rsi < 20:
        result['risk_level'] = 'high'
    elif rsi > 70 or rsi < 30:
        result['risk_level'] = 'medium'
    else:
        result['risk_level'] = 'low'
    
    return result


if __name__ == '__main__':
    import json
    
    # 测试
    basic = {
        'current_price': 1450,
        'ma5': 1440,
        'ma10': 1430,
        'ma20': 1400,
        'rsi': 65,
        'volume_ratio': 1.2
    }
    
    result = analyze_stock('600519', basic)
    print(json.dumps(result, indent=2, ensure_ascii=False))
