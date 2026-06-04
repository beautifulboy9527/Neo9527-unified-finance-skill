#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI UI 渲染层 (P2: Rich-based terminal output)

提供统一的终端美化输出:
- 彩色表格 (Table)
- 进度条 (Progress)
- 数据新鲜度标注 (FreshnessBadge)
- 分析结果卡片 (AnalysisCard)
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Fallback: plain text output when rich is not available
if not HAS_RICH:
    class _FakeConsole:
        def print(self, *args, **kwargs):
            print(*args)

    Console = _FakeConsole


# ── Freshness Badge ───────────────────────────────────────────

FRESHNESS_STYLES = {
    "realtime": ("🟢 实时", "green"),
    "delayed":  ("🟡 延迟", "yellow"),
    "stale":    ("🔴 过期", "red"),
    "closed":   ("⏹ 休市", "dim"),
    "unknown":  ("⚪ 未知", "white"),
}

def freshness_label(phase: str, cache_age: float = 0.0, is_stale: bool = False) -> str:
    """获取数据新鲜度标签"""
    if phase == "closed":
        return FRESHNESS_STYLES["closed"][0]
    if is_stale or cache_age > 300:
        return FRESHNESS_STYLES["stale"][0]
    if cache_age < 60:
        return FRESHNESS_STYLES["realtime"][0]
    return FRESHNESS_STYLES["delayed"][0]


# ── Rich Console Singleton ────────────────────────────────────

_console: Optional[Console] = None

def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console(force_terminal=True)
    return _console


# ── Progress Bar Helper ───────────────────────────────────────

def create_progress() -> Any:
    """创建进度条"""
    if HAS_RICH:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TimeElapsedColumn(),
            console=get_console(),
        )
    return None


# ── Analysis Card ─────────────────────────────────────────────

def print_analysis_header(symbol: str, display_name: str = "", freshness: str = ""):
    """打印分析结果头部"""
    console = get_console()
    if HAS_RICH:
        title = Text()
        title.append(f" {display_name or symbol} ", style="bold white on blue")
        title.append(f" {freshness} ", style="dim")
        console.print(Panel(title, box=box.ROUNDED))
    else:
        print(f"\n{'='*60}")
        print(f" {display_name or symbol} {freshness}")
        print(f"{'='*60}")


def print_metric_table(title: str, metrics: Dict[str, Any], highlight_thresholds: Dict = None):
    """打印指标表格"""
    console = get_console()
    if not HAS_RICH:
        print(f"\n{title}:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        return

    table = Table(title=title, box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("指标", style="cyan")
    table.add_column("值", justify="right")
    table.add_column("状态", justify="center")

    for key, value in metrics.items():
        status = ""
        style = ""
        if highlight_thresholds and key in highlight_thresholds:
            threshold = highlight_thresholds[key]
            try:
                num_val = float(str(value).replace('%', '').replace('亿', 'e8').replace('万', 'e4'))
                if isinstance(threshold, tuple):
                    low, high = threshold
                    if num_val < low:
                        status = "⚠️"
                        style = "red"
                    elif num_val > high:
                        status = "✅"
                        style = "green"
                    else:
                        status = "—"
                        style = "yellow"
            except (ValueError, TypeError):
                pass

        table.add_row(str(key), str(value), status, style=style or None)

    console.print(table)


def print_section(title: str, content: str, style: str = "bold"):
    """打印分节"""
    console = get_console()
    if HAS_RICH:
        console.print(f"\n[bold]▸ {title}[/bold]")
        console.print(f"  {content}")
    else:
        print(f"\n▸ {title}")
        print(f"  {content}")


def print_signal_cards(signals: List[Dict]):
    """打印入场信号卡片"""
    console = get_console()
    if not signals:
        console.print("  无信号", style="dim")
        return

    if HAS_RICH:
        table = Table(title="🎯 入场信号", box=box.SIMPLE)
        table.add_column("信号", style="cyan")
        table.add_column("类型")
        table.add_column("强度", justify="center")
        table.add_column("建议")

        for s in signals[:5]:
            strength = str(s.get("strength", ""))
            strength_style = "green" if "强" in strength else "yellow" if "中" in strength else "red" if "弱" in strength else None
            table.add_row(
                str(s.get("name", "")),
                str(s.get("type", "")),
                f"[{strength_style}]{strength}[/{strength_style}]" if strength_style else strength,
                str(s.get("action", "")),
            )
        console.print(table)
    else:
        print("🎯 入场信号:")
        for s in signals[:5]:
            print(f"  {s.get('name','')} | {s.get('type','')} | {s.get('strength','')} | {s.get('action','')}")


def print_risk_panel(risk: Dict):
    """打印风险面板"""
    console = get_console()
    severity = risk.get("highest_severity_cn", "提示")
    alert_count = risk.get("alert_count", 0)

    if HAS_RICH:
        severity_style = "red" if "高" in severity else "yellow" if "中" in severity else "green"
        panel_content = Text()
        panel_content.append(f"风险等级: ", style="bold")
        panel_content.append(f"{severity}", style=f"bold {severity_style}")
        panel_content.append(f"  |  预警数: {alert_count}")

        alerts = risk.get("alerts", [])
        if alerts:
            panel_content.append("\n")
            for a in alerts[:3]:
                panel_content.append(f"\n  • {a.get('title', a.get('type', '未知'))}", style=severity_style)

        console.print(Panel(panel_content, title="⚠️ 风险", border_style=severity_style))
    else:
        print(f"⚠️ 风险: {severity} | 预警数: {alert_count}")


def print_summary(summary: str, elapsed: float = 0.0, stages_done: int = 0, stages_total: int = 0):
    """打印综合结论"""
    console = get_console()
    if HAS_RICH:
        console.print()
        info = f"⏱ {elapsed:.1f}s | 阶段 {stages_done}/{stages_total}" if stages_total else f"⏱ {elapsed:.1f}s"
        console.print(Panel(summary, title="📋 综合结论", subtitle=info, border_style="blue"))
    else:
        print(f"\n📋 综合结论: {summary}")
        if elapsed:
            print(f"  ⏱ {elapsed:.1f}s")


def print_watchlist_table(stocks: List[Dict]):
    """打印自选股表格"""
    console = get_console()
    if not HAS_RICH or not stocks:
        for s in stocks[:10]:
            print(f"  {s.get('symbol','')} {s.get('name','')} 价格={s.get('price','N/A')}")
        return

    table = Table(title="📋 自选股", box=box.SIMPLE)
    table.add_column("代码", style="cyan")
    table.add_column("名称")
    table.add_column("价格", justify="right")
    table.add_column("涨跌", justify="right")
    table.add_column("状态", justify="center")

    for s in stocks[:15]:
        change = s.get("change_pct", 0)
        change_style = "red" if change and float(change) < 0 else "green" if change and float(change) > 0 else None
        status = "✅" if s.get("target_hit") else "⏳" if s.get("active") else "—"
        table.add_row(
            str(s.get("symbol", "")),
            str(s.get("name", "")),
            str(s.get("price", "N/A")),
            f"[{change_style}]{change}%[/{change_style}]" if change_style else f"{change}%",
            status,
        )
    console.print(table)


__all__ = [
    "HAS_RICH", "get_console", "create_progress",
    "freshness_label", "print_analysis_header",
    "print_metric_table", "print_section",
    "print_signal_cards", "print_risk_panel",
    "print_summary", "print_watchlist_table",
]
