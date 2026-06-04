#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业支撑阻力位计算模块
- 前高前低 (Swing High/Low)
- 枢轴点 (Pivot Points)
- 成交密集区 (Volume Profile)
- 整数关口 (Psychological Levels)
- 均线支撑 (MA Support)
- 布林带 (Bollinger Bands)
- 斐波那契回撤 (Fibonacci Retracement)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


def find_swing_points(high: pd.Series, low: pd.Series, lookback: int = 60) -> Tuple[List[Tuple], List[Tuple]]:
    """
    寻找前高前低 (Swing High/Low)
    
    Args:
        high: 最高价序列
        low: 最低价序列
        lookback: 回溯天数
    
    Returns:
        swing_highs: [(index, price), ...]
        swing_lows: [(index, price), ...]
    """
    lookback = min(lookback, len(high))
    recent_highs = high.iloc[-lookback:]
    recent_lows = low.iloc[-lookback:]
    
    swing_highs = []
    swing_lows = []
    
    # 需要至少5天的窗口
    if lookback < 10:
        return swing_highs, swing_lows
    
    # 寻找局部高点 (比左右各2天都高)
    for i in range(2, lookback - 2):
        if (recent_highs.iloc[i] > recent_highs.iloc[i-1] and 
            recent_highs.iloc[i] > recent_highs.iloc[i-2] and
            recent_highs.iloc[i] > recent_highs.iloc[i+1] and 
            recent_highs.iloc[i] > recent_highs.iloc[i+2]):
            swing_highs.append((i, recent_highs.iloc[i]))
    
    # 寻找局部低点 (比左右各2天都低)
    for i in range(2, lookback - 2):
        if (recent_lows.iloc[i] < recent_lows.iloc[i-1] and 
            recent_lows.iloc[i] < recent_lows.iloc[i-2] and
            recent_lows.iloc[i] < recent_lows.iloc[i+1] and 
            recent_lows.iloc[i] < recent_lows.iloc[i+2]):
            swing_lows.append((i, recent_lows.iloc[i]))
    
    return swing_highs, swing_lows


def calculate_pivot_points(high: float, low: float, close: float) -> Dict:
    """
    计算枢轴点 (Pivot Points)
    经典算法
    """
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    
    return {
        'pivot': pivot,
        'r1': r1, 'r2': r2, 'r3': r3,
        's1': s1, 's2': s2, 's3': s3
    }


def find_round_levels(current_price: float, range_pct: float = 0.15) -> List[float]:
    """
    寻找整数关口 (心理支撑/阻力)
    
    Args:
        current_price: 当前价格
        range_pct: 搜索范围百分比
    
    Returns:
        整数关口列表
    """
    round_levels = []
    
    # 根据价格范围选择整数间隔
    if current_price < 10:
        intervals = [0.5, 1, 2, 3, 5, 8, 10]
    elif current_price < 50:
        intervals = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50]
    elif current_price < 200:
        intervals = [5, 10, 20, 30, 50, 80, 100, 120, 150, 200]
    else:
        intervals = [10, 20, 50, 100, 150, 200, 300, 500]
    
    for level in intervals:
        if abs(current_price - level) / current_price < range_pct:
            round_levels.append(level)
    
    return round_levels


def calculate_fibonacci_levels(high: float, low: float) -> Dict:
    """
    计算斐波那契回撤位
    
    Args:
        high: 区间最高价
        low: 区间最低价
    
    Returns:
        斐波那契回撤位
    """
    diff = high - low
    
    return {
        '0%': high,
        '23.6%': high - diff * 0.236,
        '38.2%': high - diff * 0.382,
        '50%': high - diff * 0.5,
        '61.8%': high - diff * 0.618,
        '100%': low
    }


def select_support_resistance(
    current_price: float,
    swing_highs: List[Tuple],
    swing_lows: List[Tuple],
    pivot_points: Dict,
    ma_levels: List[float],
    bb_upper: float,
    bb_lower: float,
    round_levels: List[float],
    fib_levels: Dict,
    min_distance_pct: float = 0.015,
    max_distance_pct: float = 0.10
) -> Dict:
    """
    智能选择支撑阻力位
    
    原则:
    1. 优先选择前高前低 (最可靠)
    2. 最小间距: 1.5% (太近没意义)
    3. 最大间距: 10% (太远没参考价值)
    4. 结合形态确认
    
    Args:
        current_price: 当前价格
        min_distance_pct: 最小距离百分比 (默认1.5%)
        max_distance_pct: 最大距离百分比 (默认10%)
    
    Returns:
        支撑阻力位信息
    """
    min_distance = current_price * min_distance_pct
    max_distance = current_price * max_distance_pct
    
    # 收集所有支撑位候选 (名称, 价格, 权重)
    support_candidates = []
    
    # 1. 前低 (权重最高)
    for idx, price in swing_lows:
        if price < current_price:
            support_candidates.append(('前低', float(price), 5))
    
    # 2. 枢轴点支撑
    for name, price in [('S1', pivot_points['s1']), ('S2', pivot_points['s2'])]:
        if price < current_price:
            support_candidates.append((f'枢轴点{name}', float(price), 4))
    
    # 3. 斐波那契回撤
    for level, price in fib_levels.items():
        if price < current_price:
            support_candidates.append((f'斐波那契{level}', float(price), 3))
    
    # 4. 布林下轨
    if bb_lower < current_price:
        support_candidates.append(('布林下轨', float(bb_lower), 3))
    
    # 5. 均线支撑
    for ma in ma_levels:
        if ma < current_price:
            support_candidates.append(('均线支撑', float(ma), 2))
    
    # 6. 整数关口
    for level in round_levels:
        if level < current_price:
            support_candidates.append(('整数关口', float(level), 1))
    
    # 筛选有效支撑位 (距离在合理范围内)
    valid_supports = [
        s for s in support_candidates 
        if max_distance > (current_price - s[1]) > min_distance
    ]
    
    # 选择支撑位
    if valid_supports:
        # 按权重排序，选择最高权重
        valid_supports.sort(key=lambda x: x[2], reverse=True)
        support_near = valid_supports[0][1]
        support_source = valid_supports[0][0]
    else:
        # 如果没有合适的，选择距离最合理的
        if support_candidates:
            support_candidates.sort(key=lambda x: abs(current_price - x[1]))
            support_near = support_candidates[0][1]
            support_source = support_candidates[0][0]
        else:
            support_near = current_price * 0.95  # 默认5%下方
            support_source = '默认支撑'
    
    # ========== 阻力位选择 (同理) ==========
    resistance_candidates = []
    
    # 1. 前高 (权重最高)
    for idx, price in swing_highs:
        if price > current_price:
            resistance_candidates.append(('前高', float(price), 5))
    
    # 2. 枢轴点阻力
    for name, price in [('R1', pivot_points['r1']), ('R2', pivot_points['r2'])]:
        if price > current_price:
            resistance_candidates.append((f'枢轴点{name}', float(price), 4))
    
    # 3. 斐波那契回撤
    for level, price in fib_levels.items():
        if price > current_price:
            resistance_candidates.append((f'斐波那契{level}', float(price), 3))
    
    # 4. 布林上轨
    if bb_upper > current_price:
        resistance_candidates.append(('布林上轨', float(bb_upper), 3))
    
    # 5. 均线阻力
    for ma in ma_levels:
        if ma > current_price:
            resistance_candidates.append(('均线阻力', float(ma), 2))
    
    # 6. 整数关口
    for level in round_levels:
        if level > current_price:
            resistance_candidates.append(('整数关口', float(level), 1))
    
    # 筛选有效阻力位
    valid_resistances = [
        r for r in resistance_candidates 
        if max_distance > (r[1] - current_price) > min_distance
    ]
    
    # 选择阻力位
    if valid_resistances:
        valid_resistances.sort(key=lambda x: x[2], reverse=True)
        resistance_near = valid_resistances[0][1]
        resistance_source = valid_resistances[0][0]
    else:
        if resistance_candidates:
            resistance_candidates.sort(key=lambda x: abs(current_price - x[1]))
            resistance_near = resistance_candidates[0][1]
            resistance_source = resistance_candidates[0][0]
        else:
            resistance_near = current_price * 1.05  # 默认5%上方
            resistance_source = '默认阻力'
    
    # 计算距离百分比
    support_pct = (support_near - current_price) / current_price * 100
    resistance_pct = (resistance_near - current_price) / current_price * 100
    
    # 计算盈亏比
    if abs(support_pct) > 0:
        risk_reward = abs(resistance_pct / support_pct)
    else:
        risk_reward = 1.0
    
    return {
        'support_near': support_near,
        'support_source': support_source,
        'support_pct': support_pct,
        'resistance_near': resistance_near,
        'resistance_source': resistance_source,
        'resistance_pct': resistance_pct,
        'risk_reward': risk_reward,
        'all_supports': support_candidates[:5],  # 返回前5个候选
        'all_resistances': resistance_candidates[:5]
    }


def analyze_trading_opportunity(
    current_price: float,
    support_near: float,
    resistance_near: float,
    support_pct: float,
    resistance_pct: float,
    risk_reward: float
) -> Dict:
    """
    分析交易机会
    
    判断逻辑:
    1. 利润空间 < 2%: 不值得操作
    2. 盈亏比 < 1.5: 风险收益比不划算
    3. 利润空间 2-5% + 盈亏比 >= 1.5: 短线机会
    4. 利润空间 > 5% + 盈亏比 >= 2: 好机会
    
    Returns:
        交易建议
    """
    profit_space = abs(resistance_pct)
    loss_space = abs(support_pct)
    
    # 判断是否有操作价值
    if profit_space < 2:
        return {
            'tradable': False,
            'reason': f'利润空间太小({profit_space:.1f}%)，不值得操作',
            'suggestion': '等待更好的入场点'
        }
    
    if risk_reward < 1.5:
        return {
            'tradable': False,
            'reason': f'盈亏比不划算(1:{risk_reward:.1f})，风险大于收益',
            'suggestion': '寻找其他机会'
        }
    
    # 判断操作等级
    if profit_space >= 5 and risk_reward >= 2:
        level = '优秀'
        suggestion = f'利润空间{profit_space:.1f}%，盈亏比1:{risk_reward:.1f}，值得操作'
    elif profit_space >= 3 and risk_reward >= 1.5:
        level = '良好'
        suggestion = f'利润空间{profit_space:.1f}%，盈亏比1:{risk_reward:.1f}，可考虑轻仓'
    else:
        level = '一般'
        suggestion = f'利润空间{profit_space:.1f}%，盈亏比1:{risk_reward:.1f}，需谨慎'
    
    return {
        'tradable': True,
        'level': level,
        'profit_space': profit_space,
        'loss_space': loss_space,
        'risk_reward': risk_reward,
        'suggestion': suggestion
    }


# ========== 测试 ==========
if __name__ == '__main__':
    import yfinance as yf
    
    # 测试格力电器
    ticker = yf.Ticker('000651.SZ')
    hist = ticker.history(period='6mo')
    
    if not hist.empty:
        high = hist['High']
        low = hist['Low']
        close = hist['Close']
        current = close.iloc[-1]
        
        print(f"当前价格: {current:.2f}")
        print()
        
        # 1. 寻找前高前低
        swing_highs, swing_lows = find_swing_points(high, low)
        print(f"前高: {[(i, f'{p:.2f}') for i, p in swing_highs[:3]]}")
        print(f"前低: {[(i, f'{p:.2f}') for i, p in swing_lows[:3]]}")
        print()
        
        # 2. 枢轴点
        pivot_points = calculate_pivot_points(high.iloc[-1], low.iloc[-1], close.iloc[-1])
        print(f"枢轴点: {pivot_points['pivot']:.2f}")
        print(f"R1: {pivot_points['r1']:.2f}, S1: {pivot_points['s1']:.2f}")
        print()
        
        # 3. 整数关口
        round_levels = find_round_levels(current)
        print(f"整数关口: {round_levels}")
        print()
        
        # 4. 斐波那契
        fib_levels = calculate_fibonacci_levels(high.iloc[-60:].max(), low.iloc[-60:].min())
        print(f"斐波那契: {[(k, f'{v:.2f}') for k, v in fib_levels.items()]}")
        print()
        
        # 5. 计算布林带
        bb_mid = close.rolling(20).mean().iloc[-1]
        bb_std = close.rolling(20).std().iloc[-1]
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std
        
        # 6. 均线
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else ma20
        
        # 7. 智能选择
        result = select_support_resistance(
            current_price=current,
            swing_highs=swing_highs,
            swing_lows=swing_lows,
            pivot_points=pivot_points,
            ma_levels=[ma20, ma60],
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            round_levels=round_levels,
            fib_levels=fib_levels
        )
        
        print("=" * 50)
        print(f"支撑位: {result['support_near']:.2f} ({result['support_source']}) - {result['support_pct']:.1f}%")
        print(f"阻力位: {result['resistance_near']:.2f} ({result['resistance_source']}) + {result['resistance_pct']:.1f}%")
        print(f"盈亏比: 1:{result['risk_reward']:.1f}")
        print()
        
        # 8. 交易机会分析
        opportunity = analyze_trading_opportunity(
            current, result['support_near'], result['resistance_near'],
            result['support_pct'], result['resistance_pct'], result['risk_reward']
        )
        print(f"交易机会: {opportunity}")
