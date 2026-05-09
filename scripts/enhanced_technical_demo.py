#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Technical Analysis Demo - Phase 1
展示如何将增强技术分析集成到 stock-skill 流程中
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd

try:
    from skills.stock_skill.stock_data_collector import collect_stock_data
except ImportError:
    collect_stock_data = None

from skills.shared.technical_indicators import (
    calculate_vwap,
    calculate_fibonacci_retracements,
    calculate_fibonacci_extensions,
    calculate_chan_segments,
    identify_candlestick_patterns,
    identify_trendlines,
    calculate_adx,
    enhanced_technical_analysis,
)


def _candles_to_dataframe(candles: list) -> pd.DataFrame:
    """将 K线数据转换为 DataFrame"""
    if not candles:
        return pd.DataFrame()
    df = pd.DataFrame(candles)
    df = df.rename(columns={
        "date": "日期", "open": "开盘", 
        "high": "最高", "low": "最低", 
        "close": "收盘", "volume": "成交量"
    })
    for col in ["开盘", "最高", "最低", "收盘", "成交量"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def analyze_symbol(symbol: str, use_live_data: bool = False):
    """
    综合技术分析演示
    
    Args:
        symbol: 股票代码 (如 "600519" 或 "AAPL")
        use_live_data: 是否使用实时数据 (需要网络)
    """
    print("=" * 70)
    print(f"📊 增强技术分析演示 - {symbol}")
    print("=" * 70)
    
    # 1. 收集基础数据
    if use_live_data:
        print("\n📡 正在获取实时数据...")
        data = collect_stock_data(symbol)
        candles = data.get("technical_analysis", {}).get("candles", [])
    else:
        print("\n📡 使用模拟数据进行演示...")
        # 生成模拟K线数据
        import numpy as np
        np.random.seed(hash(symbol) % 2**32)
        
        dates = pd.date_range("2025-01-01", periods=120, freq="D")
        base_price = 100
        prices = base_price + np.cumsum(np.random.randn(120) * 2)
        
        candles = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            open_price = close + np.random.randn() * 0.5
            high = close + abs(np.random.randn() * 1.5)
            low = close - abs(np.random.randn() * 1.5)
            volume = np.random.randint(1000000, 10000000)
            
            candles.append({
                "date": str(date.date()),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
            })
    
    # 2. 转换为 DataFrame
    df = _candles_to_dataframe(candles)
    
    if df.empty:
        print("❌ 无法获取K线数据")
        return
    
    print(f"✅ 获取到 {len(df)} 根K线数据")
    
    # 3. 执行各项分析
    print("\n" + "=" * 70)
    print("📈 逐项技术指标分析")
    print("=" * 70)
    
    # VWAP
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 VWAP 指标 (成交量加权平均价)                        │")
    print("└─────────────────────────────────────────────────────────┘")
    vwap = calculate_vwap(df)
    if "error" not in vwap:
        print(f"   当前VWAP: {vwap['vwap']:.2f}")
        print(f"   价格位置: {vwap['position']}")
        print(f"   解读: {vwap['interpretation']}")
    else:
        print(f"   ⚠️ {vwap['error']}")
    
    # 斐波那契回撤
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 斐波那契回撤位                                     │")
    print("└─────────────────────────────────────────────────────────┘")
    fib = calculate_fibonacci_retracements(df, lookback=60)
    if "error" not in fib:
        print(f"   波段区间: {fib['swing_low']:.2f} ~ {fib['swing_high']:.2f}")
        print(f"   趋势: {fib['trend']}")
        print(f"   当前: {fib['current_position']}")
        print("   回撤位:")
        for retr in fib["retracements"]:
            marker = " ← 当前附近" if retr["near_current"] else ""
            print(f"     {retr['label']:>6}: {retr['price']:>10.2f} ({retr['type']}){marker}")
        if fib.get("nearest_support"):
            print(f"   最近支撑: {fib['nearest_support']['label']} @ {fib['nearest_support']['price']:.2f}")
        if fib.get("nearest_resistance"):
            print(f"   最近压力: {fib['nearest_resistance']['label']} @ {fib['nearest_resistance']['price']:.2f}")
    else:
        print(f"   ⚠️ {fib['error']}")
    
    # K线形态
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 K线形态识别                                         │")
    print("└─────────────────────────────────────────────────────────┘")
    candle = identify_candlestick_patterns(df)
    if "error" not in candle:
        patterns = candle.get("patterns", [])
        print(f"   识别到 {len(patterns)} 个形态:")
        for p in patterns:
            emoji = "🟢" if "看涨" in p.get("type", "") else ("🔴" if "看跌" in p.get("type", "") else "⚪")
            print(f"   {emoji} {p['name']} - {p['type']} (强度: {p['strength']})")
            print(f"      {p['description']}")
            print(f"      建议: {p['action']}")
        if not patterns:
            print("   未识别到经典K线形态")
    else:
        print(f"   ⚠️ {candle['error']}")
    
    # ADX
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 ADX 趋势强度指标                                    │")
    print("└─────────────────────────────────────────────────────────┘")
    adx = calculate_adx(df)
    if "error" not in adx:
        print(f"   ADX: {adx['adx']:.1f} (趋势强度: {adx['trend_strength']})")
        print(f"   +DI: {adx['plus_di']:.1f}")
        print(f"   -DI: {adx['minus_di']:.1f}")
        print(f"   趋势: {adx['trend']}")
        print(f"   方向: {adx['direction']}")
        print(f"   解读: {adx['interpretation']}")
    else:
        print(f"   ⚠️ {adx['error']}")
    
    # 缠论中枢
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 缠论中枢分析 (简化版)                               │")
    print("└─────────────────────────────────────────────────────────┘")
    chan = calculate_chan_segments(df)
    if "error" not in chan:
        print(f"   笔段数量: {chan['segments_count']}")
        print(f"   当前状态: {chan['current_position']}")
        print(f"   解读: {chan['interpretation']}")
        if chan.get("centers"):
            print("   最近中枢:")
            for center in chan["centers"][-2:]:
                print(f"     区间: {center['range']}, 中点: {center['mid']:.2f}")
        else:
            print("   暂无中枢形成")
    else:
        print(f"   ⚠️ {chan['error']}")
    
    # 趋势线
    print("\n┌─────────────────────────────────────────────────────────┐")
    print("│ 📊 趋势线识别                                          │")
    print("└─────────────────────────────────────────────────────────┘")
    trendline = identify_trendlines(df)
    if "error" not in trendline:
        lines = trendline.get("trendlines", [])
        if lines:
            for line in lines:
                emoji = "📈" if "上升" in line.get("type", "") else "📉"
                print(f"   {emoji} {line['type']}")
                print(f"      斜率: {line['slope']:.4f}, R²: {line['r_squared']:.3f}")
                print(f"      当前值: {line['current_value']:.2f}")
                print(f"      状态: {line['status']}")
        else:
            print("   未识别到有效趋势线 (R² > 0.7)")
    else:
        print(f"   ⚠️ {trendline['error']}")
    
    # 4. 综合分析
    print("\n" + "=" * 70)
    print("📋 综合技术分析结论")
    print("=" * 70)
    
    analysis = enhanced_technical_analysis(df, symbol=symbol)
    summary = analysis.get("summary", {})
    
    print(f"\n   信号统计:")
    print(f"   • 总信号数: {summary.get('signal_count', 0)}")
    print(f"   • 看多信号: {summary.get('bullish_count', 0)}")
    print(f"   • 看空信号: {summary.get('bearish_count', 0)}")
    print(f"\n   🧭 综合判断: {summary.get('overall_bias', '中性')}")
    
    if summary.get("signals"):
        print("\n   详细信号:")
        for source, direction, desc in summary["signals"]:
            emoji = "🟢" if direction == "看多" else ("🔴" if direction == "看空" else "⚪")
            print(f"   {emoji} [{source}] {direction}: {desc}")
    
    print("\n" + "=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="增强技术分析演示")
    parser.add_argument("symbol", nargs="?", default="600519", help="股票代码")
    parser.add_argument("--live", action="store_true", help="使用实时数据")
    args = parser.parse_args()
    
    analyze_symbol(args.symbol, use_live_data=args.live)


if __name__ == "__main__":
    main()
