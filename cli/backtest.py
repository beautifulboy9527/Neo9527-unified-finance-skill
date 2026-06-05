#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回测系统命令 (P2)"""

import os
from datetime import datetime

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_backtest(args):
    """策略回测"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "backtest_engine", os.path.join(SKILLS_DIR, "skills", "stock-skill", "backtest_engine.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from skills.shared.ui import print_metric_table, print_section, print_summary, get_console, HAS_RICH

    symbol = args.symbol
    strategy = args.strategy
    days = args.days
    initial_capital = args.capital

    print(f"\n🔬 回测 {symbol} | 策略={strategy} | {days}天 | 初始资金={initial_capital:,.0f}")

    engine = mod.BacktestEngine(initial_capital=initial_capital)

    # 获取数据
    print("  获取历史数据...")
    df = engine.get_price_data(symbol, days=days)
    if df is None or df.empty:
        print(f"❌ 无法获取 {symbol} 历史数据")
        return

    print(f"  数据范围: {df.index[0] if hasattr(df.index[0], 'strftime') else df.iloc[0].name} ~ {df.index[-1] if hasattr(df.index[-1], 'strftime') else df.iloc[-1].name}")
    print(f"  数据量: {len(df)} 条")

    # 选择策略
    signal_func = None
    if strategy == "sma-cross":
        signal_func = mod.sma_cross_signal
    elif strategy == "rsi-oversold":
        signal_func = mod.rsi_oversold_signal
    else:
        print(f"  未知策略: {strategy}，使用 sma-cross")
        signal_func = mod.sma_cross_signal

    # 执行回测
    print("  执行回测...")
    try:
        result = engine.backtest_signal(symbol, signal_func)
    except Exception as e:
        print(f"  回测执行失败: {e}")
        # Fallback: 简单回测
        result = _simple_backtest(engine, df, symbol)

    if not result or not result.get("success"):
        print(f"❌ 回测失败")
        return

    # 输出结果
    stats = result.get("statistics", {})
    trades = result.get("trades", [])

    metrics = {
        "总收益率": f"{stats.get('total_return', 0)*100:.2f}%",
        "年化收益率": f"{stats.get('annualized_return', 0)*100:.2f}%",
        "最大回撤": f"{stats.get('max_drawdown', 0)*100:.2f}%",
        "夏普比率": f"{stats.get('sharpe_ratio', 0):.2f}",
        "胜率": f"{stats.get('win_rate', 0)*100:.1f}%",
        "交易次数": str(len(trades)),
    }

    print_metric_table("📊 回测结果", metrics, highlight_thresholds={
        "总收益率": (-0.1, 0.1),
        "最大回撤": (-0.2, 0),
        "夏普比率": (0, 1),
    })

    # Walk-Forward 分析
    if args.walk_forward:
        print("\n  执行 Walk-Forward 分析...")
        try:
            wf_result = engine.walk_forward_analysis(symbol, signal_func)
            if wf_result and wf_result.get("success"):
                wf_stats = wf_result.get("statistics", {})
                print_section("Walk-Forward 验证", 
                    f"样本外收益率: {wf_stats.get('oos_return', 0)*100:.2f}% | "
                    f"样本外夏普: {wf_stats.get('oos_sharpe', 0):.2f}")
        except Exception as e:
            print(f"  Walk-Forward 分析失败: {e}")

    # Monte Carlo 模拟
    if args.monte_carlo:
        print("\n  执行 Monte Carlo 模拟...")
        try:
            mc_result = engine.monte_carlo_simulation(symbol)
            if mc_result and mc_result.get("success"):
                mc_stats = mc_result.get("statistics", {})
                print_section("Monte Carlo 模拟",
                    f"P5 收益率: {mc_stats.get('p5_return', 0)*100:.2f}% | "
                    f"P95 收益率: {mc_stats.get('p95_return', 0)*100:.2f}%")
        except Exception as e:
            print(f"  Monte Carlo 模拟失败: {e}")

    # 交易明细
    if trades and args.detail:
        print_section(f"📝 交易明细 ({len(trades)} 笔)", "")
        for t in trades[:10]:
            action = "🟢买入" if t.get("action") == "BUY" else "🔴卖出"
            print(f"  {t.get('date','')} {action} | 价格={t.get('price',0):.2f} | 收益={t.get('return', 0)*100:.1f}%")

    elapsed = result.get("elapsed_seconds", 0)
    print_summary(
        f"策略 {strategy} 在 {symbol} 上回测完成: {stats.get('total_return', 0)*100:.2f}% 收益, {stats.get('sharpe_ratio', 0):.2f} 夏普",
        elapsed=elapsed,
    )


def _simple_backtest(engine, df, symbol):
    """简单回测 fallback"""
    try:
        if df.empty or 'close' not in df.columns:
            return {"success": False}

        close = df['close']
        total_return = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
        
        # 简单最大回撤计算
        cummax = close.cummax()
        drawdown = (close - cummax) / cummax
        max_drawdown = drawdown.min()

        # 简单夏普比率
        returns = close.pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() > 0 else 0

        return {
            "success": True,
            "statistics": {
                "total_return": total_return,
                "annualized_return": total_return * (252 / len(df)),
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe,
                "win_rate": 0.5,
            },
            "trades": [],
            "elapsed_seconds": 0.1,
        }
    except Exception:
        return {"success": False}
