#!/usr/bin/env python3
"""
Complete Stock Report Generator
生成股票完整分析报告 - 整合所有数据源
"""

import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def generate_complete_report(symbol, period='6mo'):
    """
    生成股票完整分析报告
    
    包含:
    1. 实时行情
    2. 技术指标图表
    3. 基本面数据
    4. 资金流向 (A 股/港股)
    5. 行业对比
    6. 警报建议
    """
    
    print("=" * 70)
    print(f"  {symbol} 完整分析报告")
    print(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 1. 实时行情
    print("\n【1. 实时行情】")
    print("-" * 50)
    from data_fetcher import get_quote
    quote = get_quote(symbol)
    print(quote)
    
    # 2. 技术指标图表
    print("\n【2. 技术指标图表】")
    print("-" * 50)
    from chart_generator import generate_chart
    indicators = {'rsi': True, 'macd': True, 'bb': True, 'vwap': True, 'atr': True}
    chart_path = generate_chart(symbol, period, indicators)
    print(f"图表路径：{chart_path}")
    
    # 3. 基本面数据
    print("\n【3. 基本面数据】")
    print("-" * 50)
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        print(f"市值：{info.get('marketCap', 'N/A')}")
        print(f"市盈率 (Forward PE): {info.get('forwardPE', 'N/A')}")
        print(f"市净率 (PB): {info.get('priceToBook', 'N/A')}")
        print(f"股息率：{info.get('dividendYield', 'N/A')}")
        print(f"EPS (TTM): {info.get('trailingEps', 'N/A')}")
        print(f"52 周最高：{info.get('fiftyTwoWeekHigh', 'N/A')}")
        print(f"52 周最低：{info.get('fiftyTwoWeekLow', 'N/A')}")
        print(f"分析师目标价：{info.get('targetMeanPrice', 'N/A')}")
    except Exception as e:
        print(f"基本面数据获取失败：{e}")
    
    # 4. 资金流向 (仅 A 股/港股)
    if symbol.isdigit() or symbol.endswith('.HK') or symbol.endswith('.SS') or symbol.endswith('.SZ'):
        print("\n【4. 资金流向】")
        print("-" * 50)
        from data_fetcher import get_fundflow
        fundflow = get_fundflow(symbol.replace('.HK', '').replace('.SS', '').replace('.SZ', ''))
        print(fundflow)
    
    # 5. 行业对比
    print("\n【5. 行业热力图对比】")
    print("-" * 50)
    from data_fetcher import get_heatmap
    if symbol.isdigit() or symbol.endswith('.SS') or symbol.endswith('.SZ'):
        market = 'ab'
    elif symbol.endswith('.HK'):
        market = 'hk'
    else:
        market = 'us'
    
    heatmap = get_heatmap(market)
    print(heatmap[:1000] if len(heatmap) > 1000 else heatmap)
    
    # 6. 技术信号解读
    print("\n【6. 技术信号解读】")
    print("-" * 50)
    try:
        import yfinance as yf
        import pandas as pd
        import numpy as np
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if not hist.empty:
            close = hist['Close']
            
            # RSI
            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
            avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
            rs = avg_gain / avg_loss.replace(0, pd.NA)
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # MACD
            ema_fast = close.ewm(span=12, adjust=False, min_periods=12).mean()
            ema_slow = close.ewm(span=26, adjust=False, min_periods=26).mean()
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            
            # 布林带
            ma = close.rolling(window=20, min_periods=20).mean()
            std = close.rolling(window=20, min_periods=20).std()
            upper = ma + 2 * std
            lower = ma - 2 * std
            current_price = close.iloc[-1]
            bb_position = (current_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100
            
            print(f"RSI(14): {current_rsi:.1f}", end="")
            if current_rsi > 70:
                print(" [超买 - 考虑减仓]")
            elif current_rsi < 30:
                print(" [超卖 - 考虑建仓]")
            else:
                print(" [中性]")
            
            print(f"MACD: {current_macd:.2f} vs Signal: {current_signal:.2f}", end="")
            if current_macd > current_signal:
                print(" [金叉 - 看涨信号]")
            else:
                print(" [死叉 - 看跌信号]")
            
            print(f"布林带位置：{bb_position:.1f}%", end="")
            if bb_position > 80:
                print(" [接近上轨 - 可能回调]")
            elif bb_position < 20:
                print(" [接近下轨 - 可能反弹]")
            else:
                print(" [中轨附近]")
    except Exception as e:
        print(f"技术分析失败：{e}")
    
    # 7. 警报建议
    print("\n【7. 警报设置建议】")
    print("-" * 50)
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info.get('regularMarketPrice') or info.get('currentPrice')
        high_52 = info.get('fiftyTwoWeekHigh', current * 1.2)
        low_52 = info.get('fiftyTwoWeekLow', current * 0.8)
        
        target = high_52 * 1.05  # 突破 52 周高点 5%
        stop = low_52 * 0.95     # 跌破 52 周低点 5%
        
        print(f"当前价格：{current:.2f}")
        print(f"建议目标价：{target:.2f} (+{(target-current)/current*100:.1f}%)")
        print(f"建议止损价：{stop:.2f} (-{(current-stop)/current*100:.1f}%)")
        print(f"\n使用命令设置警报:")
        print(f"  python finance.py alert add {symbol} --target {target:.0f} --stop {stop:.0f}")
    except Exception as e:
        print(f"警报建议生成失败：{e}")
    
    # 保存报告到统一输出目录
    report_dir = r'D:\OpenClaw\outputs\reports'
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f'{symbol}_Complete_Report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"  {symbol} 完整分析报告\n")
        f.write("=" * 70 + "\n")
        # ... (省略详细内容)
    
    print(f"\n报告已保存：{report_file}")
    print("=" * 70)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python complete_report.py <股票代码> [周期]")
        print("示例：python complete_report.py AAPL 6mo")
        sys.exit(1)
    
    symbol = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else '6mo'
    generate_complete_report(symbol, period)
