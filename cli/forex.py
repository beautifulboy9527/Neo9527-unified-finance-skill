#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外汇 CLI 命令"""

import sys
import os

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_forex(args):
    """外汇命令"""
    subcmd = args.forex_subcmd

    if subcmd == "quote":
        _cmd_forex_quote(args)
    elif subcmd == "analyze":
        _cmd_forex_analyze(args)
    else:
        print(f"未知子命令: {subcmd}")


def _cmd_forex_quote(args):
    """获取汇率行情"""
    try:
        import yfinance as yf
    except ImportError:
        print("❌ yfinance 未安装，请运行: pip install yfinance")
        return

    pair = args.pair or "USD/CNY"
    # yfinance 格式: USDCNY=X
    yf_symbol = pair.replace("/", "") + "=X"

    try:
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period="5d")
        if hist.empty:
            print(f"❌ 无法获取 {pair} 汇率数据")
            return

        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change = ((current - prev) / prev) * 100

        print(f"\n💱 {pair} 汇率")
        print(f"  当前: {current:.4f}")
        print(f"  日变化: {change:+.2f}%")
        print(f"  5日最高: {hist['High'].max():.4f}")
        print(f"  5日最低: {hist['Low'].min():.4f}")
        print(f"  数据来源: yfinance")

    except Exception as e:
        print(f"❌ 获取汇率失败: {e}")


def _cmd_forex_analyze(args):
    """外汇技术分析"""
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print("❌ yfinance/pandas 未安装")
        return

    pair = args.pair or "USD/CNY"
    yf_symbol = pair.replace("/", "") + "=X"
    days = getattr(args, 'days', 60) or 60

    try:
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period=f"{days}d")
        if hist.empty:
            print(f"❌ 无法获取 {pair} 历史数据")
            return

        close = hist['Close']

        # 技术指标
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        current = close.iloc[-1]

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # 趋势判断
        if current > ma5 > ma10 > ma20:
            trend = "多头排列 ↑"
        elif current < ma5 < ma10 < ma20:
            trend = "空头排列 ↓"
        elif current > ma20:
            trend = "中期偏多 ↗"
        else:
            trend = "中期偏空 ↘"

        # 信号
        signals = []
        if rsi > 70:
            signals.append("⚠️ RSI超买 (>70)")
        elif rsi < 30:
            signals.append("💡 RSI超卖 (<30)")

        if current > ma20:
            signals.append("📈 站上20日均线")
        else:
            signals.append("📉 跌破20日均线")

        print(f"\n📊 {pair} 技术分析 ({days}日)")
        print(f"  当前: {current:.4f}")
        print(f"  MA5: {ma5:.4f}  MA10: {ma10:.4f}  MA20: {ma20:.4f}")
        print(f"  RSI(14): {rsi:.1f}")
        print(f"  趋势: {trend}")
        if signals:
            print(f"  信号:")
            for s in signals:
                print(f"    {s}")
        print(f"  数据来源: yfinance")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
