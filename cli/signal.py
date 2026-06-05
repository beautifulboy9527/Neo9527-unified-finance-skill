#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""信号检测 CLI 命令"""

import sys
import os

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_signal(args):
    """信号检测命令"""
    symbol = args.symbol
    market = args.market or "stock"

    if not symbol:
        print("❌ 请提供标的代码")
        return

    print(f"\n📡 {symbol} 信号检测 ({market})")

    # 根据市场类型选择分析器
    if market == "crypto":
        _detect_crypto_signals(symbol)
    elif market == "forex":
        _detect_forex_signals(symbol)
    else:
        _detect_stock_signals(symbol)


def _detect_stock_signals(symbol):
    """A股信号检测"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "entry_signals",
            os.path.join(SKILLS_DIR, "skills", "stock-skill", "entry_signals.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # 尝试调用信号检测
        if hasattr(mod, 'detect_entry_signals'):
            result = mod.detect_entry_signals(symbol)
            _print_signals(result, symbol)
        else:
            print("  ⚠️ entry_signals 模块无 detect_entry_signals 函数")
            print("  使用快速分析模式...")
            _fallback_analysis(symbol)

    except ImportError as e:
        print(f"  ❌ 模块加载失败: {e}")
        _fallback_analysis(symbol)
    except Exception as e:
        print(f"  ❌ 信号检测失败: {e}")
        _fallback_analysis(symbol)


def _detect_crypto_signals(symbol):
    """加密货币信号检测"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "crypto_skill",
            os.path.join(SKILLS_DIR, "skills", "crypto-skill", "crypto.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.get_crypto_quote(symbol)
        if result and not result.get("error"):
            price = result.get("price")
            change = result.get("change_24h")
            print(f"  价格: {price}" if price is not None else "  价格: N/A")
            print(f"  24h变化: {change}%" if change is not None else "  24h变化: N/A")

            if change is not None:
                if change > 5:
                    print("  🔴 信号: 短期涨幅较大，注意回调风险")
                elif change < -5:
                    print("  🟢 信号: 短期跌幅较大，关注反弹机会")
                else:
                    print("  🟡 信号: 波动正常，无明显信号")
        else:
            print(f"  ❌ 无法获取 {symbol} 行情")

    except Exception as e:
        print(f"  ❌ 加密货币信号检测失败: {e}")


def _detect_forex_signals(symbol):
    """外汇信号检测"""
    try:
        import yfinance as yf
        yf_symbol = symbol.replace("/", "") + "=X"
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period="30d")
        if hist.empty:
            print(f"  ❌ 无法获取 {symbol} 数据")
            return

        close = hist['Close']
        ma20 = close.rolling(20).mean().iloc[-1]
        current = close.iloc[-1]

        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        print(f"  当前: {current:.4f}  MA20: {ma20:.4f}  RSI: {rsi:.1f}")
        if current > ma20:
            print("  📈 信号: 站上20日均线，偏多")
        else:
            print("  📉 信号: 跌破20日均线，偏空")

        if rsi > 70:
            print("  ⚠️ RSI超买")
        elif rsi < 30:
            print("  💡 RSI超卖")

    except Exception as e:
        print(f"  ❌ 外汇信号检测失败: {e}")


def _fallback_analysis(symbol):
    """兜底分析 — 使用 analysis pipeline"""
    try:
        from skills.shared.analysis_pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline()
        result = pipeline.run(symbol)
        signals = result.data.get("signals", [])
        if signals:
            print(f"  检测到 {len(signals)} 个信号:")
            for s in signals[:5]:
                print(f"    • {s.get('type', 'N/A')}: {s.get('description', 'N/A')}")
        else:
            print("  🟡 暂无明显信号")
    except Exception:
        print("  ❌ 兜底分析也失败，请检查数据源")


def _print_signals(result, symbol):
    """打印信号结果"""
    if not result:
        print(f"  🟡 {symbol} 暂无信号")
        return

    signals = result.get("signals", []) if isinstance(result, dict) else []
    if signals:
        print(f"  检测到 {len(signals)} 个信号:")
        for s in signals[:5]:
            if isinstance(s, dict):
                grade = s.get("grade", "")
                desc = s.get("description", str(s))
                icon = {"S": "🔴", "A": "🟠", "B": "🟡", "C": "⚪"}.get(grade, "📡")
                print(f"    {icon} [{grade}] {desc}")
            else:
                print(f"    📡 {s}")
    else:
        print(f"  🟡 {symbol} 暂无明显信号")
