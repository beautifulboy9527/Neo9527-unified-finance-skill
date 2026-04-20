#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
形态检测模块 - 分周期检测
不同周期的形态含义不同，不能混为一谈
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def detect_patterns_by_timeframe(
    open_price: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    timeframe: str = 'daily'
) -> Dict:
    """
    分周期形态检测
    
    Args:
        timeframe: 'daily' (日线), 'weekly' (周线), 'intraday' (短线)
    
    Returns:
        检测到的形态
    """
    patterns = {
        'timeframe': timeframe,
        'trend': {},
        'reversal': {},
        'continuation': {},
        'signals': []
    }
    
    if len(close) < 20:
        return patterns
    
    current = close.iloc[-1]
    
    # ========== 趋势形态 ==========
    # 不同周期的趋势判断标准不同
    if timeframe == 'daily':
        # 日线: 使用MA5/MA10/MA20判断趋势
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        
        if current > ma5 > ma10 > ma20:
            patterns['trend'] = {
                'name': '多头排列',
                'signal': '看涨',
                'strength': 3,
                'desc': 'MA5>MA10>MA20，短期趋势向上'
            }
        elif current < ma5 < ma10 < ma20:
            patterns['trend'] = {
                'name': '空头排列',
                'signal': '看跌',
                'strength': -3,
                'desc': 'MA5<MA10<MA20，短期趋势向下'
            }
        elif current > ma20:
            patterns['trend'] = {
                'name': '偏多',
                'signal': '中性偏多',
                'strength': 1,
                'desc': '价格在MA20上方，趋势偏多'
            }
        elif current < ma20:
            patterns['trend'] = {
                'name': '偏空',
                'signal': '中性偏空',
                'strength': -1,
                'desc': '价格在MA20下方，趋势偏空'
            }
    
    # ========== 反转形态 ==========
    # 只在特定条件下检测，避免误判
    
    # 双顶检测 - 需要明确的上升趋势
    if timeframe == 'daily' and len(close) >= 30:
        # 只有在上升趋势中才检测双顶
        if close.iloc[-30:-10].mean() > close.iloc[-60:-30].mean() if len(close) >= 60 else True:
            # 检测最近20天内是否有两个相近的高点
            recent_highs = high.iloc[-20:]
            max_val = recent_highs.max()
            
            # 找出所有高点 (超过最高价95%的)
            peaks = recent_highs[recent_highs > max_val * 0.98]
            
            if len(peaks) >= 2:
                # 检查是否形成双顶 (两个高点差距<2%)
                peak_values = peaks.values
                if abs(peak_values[0] - peak_values[-1]) / peak_values[0] < 0.02:
                    # 确认两个高点之间有明显的低点
                    peak_indices = peaks.index
                    if len(peak_indices) >= 2:
                        between = low.loc[peak_indices[0]:peak_indices[-1]]
                        if between.min() < peak_values.mean() * 0.97:  # 低点低于高点3%
                            patterns['reversal']['double_top'] = {
                                'name': '双顶',
                                'signal': '看跌',
                                'strength': -3,
                                'neckline': float(between.min()),
                                'desc': f'双顶形态，颈线{between.min():.2f}，跌破确认反转'
                            }
                            patterns['signals'].append(('双顶', -3, '看跌'))
    
    # 双底检测 - 需要明确的下降趋势，且未检测到双顶
    # 排除逻辑：如果已检测到双顶，则不再检测双底
    if 'double_top' not in patterns['reversal'] and timeframe == 'daily' and len(close) >= 30:
        # 只有在下降趋势中才检测双底
        ma_short = close.iloc[-20:].mean()
        ma_long = close.iloc[-60:].mean() if len(close) >= 60 else close.iloc[-30:].mean()
        
        # 明确的下降趋势：短期均线 < 长期均线
        if ma_short < ma_long:
            recent_lows = low.iloc[-30:]
            min_val = recent_lows.min()
            
            # 找出所有低点 (低于最低价102%的)
            troughs = recent_lows[recent_lows < min_val * 1.015]
            
            if len(troughs) >= 2:
                trough_values = troughs.values
                # 两个低点接近 (差异<1.5%)
                if abs(trough_values[0] - trough_values[-1]) / trough_values[0] < 0.015:
                    trough_indices = troughs.index
                    if len(trough_indices) >= 2:
                        between = high.loc[trough_indices[0]:trough_indices[-1]]
                        # 中间高点明显高于低点 (至少3%)
                        if between.max() > trough_values.mean() * 1.03:
                            patterns['reversal']['double_bottom'] = {
                                'name': '双底',
                                'signal': '看涨',
                                'strength': 3,
                                'neckline': float(between.max()),
                                'desc': f'双底形态，颈线{between.max():.2f}，突破确认反转'
                            }
                            patterns['signals'].append(('双底', 3, '看涨'))
    
    # ========== 头肩形态 ==========
    # 需要60天以上数据，更严格
    
    # ========== 持续形态 ==========
    # 三角形整理、旗形等
    
    # 上升趋势中的三角形整理
    if timeframe == 'daily' and len(close) >= 30:
        recent_high = high.iloc[-20:].max()
        recent_low = low.iloc[-20:].min()
        range_pct = (recent_high - recent_low) / recent_low
        
        # 检查是否在收窄 (波动率下降)
        early_range = (high.iloc[-30:-20].max() - low.iloc[-30:-20].min()) / low.iloc[-30:-20].min()
        current_range = (high.iloc[-10:].max() - low.iloc[-10:].min()) / low.iloc[-10:].min()
        
        if range_pct < 0.05 and early_range > current_range * 1.5:
            patterns['continuation']['triangle'] = {
                'name': '三角形整理',
                'signal': '待突破',
                'strength': 0,
                'desc': f'波动收窄，关注突破方向'
            }
    
    return patterns


def merge_timeframe_patterns(
    daily_patterns: Dict,
    weekly_patterns: Optional[Dict] = None,
    intraday_patterns: Optional[Dict] = None
) -> Dict:
    """
    合并不同周期的形态
    
    原则:
    - 周线形态 > 日线形态 > 短线形态
    - 不同周期的信号需要一致才有效
    """
    merged = {
        'trend': daily_patterns.get('trend', {}),
        'reversal': {},
        'continuation': {},
        'signals': [],
        'confidence': 0.5
    }
    
    # 如果周线也确认，提高置信度
    if weekly_patterns:
        weekly_trend = weekly_patterns.get('trend', {})
        daily_trend = daily_patterns.get('trend', {})
        
        if weekly_trend.get('signal') == daily_trend.get('signal'):
            merged['confidence'] = 0.8
            merged['signals'].append(('周线确认', 2, '置信度提高'))
        else:
            merged['confidence'] = 0.3
            merged['signals'].append(('周线背离', -2, '需谨慎'))
    
    # 合并反转形态
    for name, pattern in daily_patterns.get('reversal', {}).items():
        merged['reversal'][name] = pattern
        merged['signals'].append((name, pattern['strength'], pattern['signal']))
    
    # 合并持续形态
    for name, pattern in daily_patterns.get('continuation', {}).items():
        merged['continuation'][name] = pattern
    
    return merged


# ========== 测试 ==========
if __name__ == '__main__':
    import yfinance as yf
    
    # 测试格力电器
    ticker = yf.Ticker('000651.SZ')
    hist = ticker.history(period='6mo')
    
    if not hist.empty:
        open_price = hist['Open']
        high = hist['High']
        low = hist['Low']
        close = hist['Close']
        volume = hist['Volume']
        
        print("=" * 50)
        print("日线形态检测:")
        print("=" * 50)
        
        daily_patterns = detect_patterns_by_timeframe(
            open_price, high, low, close, volume, 'daily'
        )
        
        print(f"趋势: {daily_patterns['trend']}")
        print()
        print(f"反转形态: {daily_patterns['reversal']}")
        print()
        print(f"持续形态: {daily_patterns['continuation']}")
        print()
        print(f"信号: {daily_patterns['signals']}")
