#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Natural-language router for the finance CLI.

This module keeps the first user-facing upgrade intentionally deterministic:
it converts common Chinese/English finance requests into existing finance.py
commands without adding an LLM dependency or touching analysis internals.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


SYMBOL_PATTERN = re.compile(
    r"\b(?:\d{6}|\d{5}\.HK|[A-Z]{1,6}(?:-[A-Z]{2,5}|=X)?)\b",
    re.IGNORECASE,
)

STRATEGY_KEYWORDS = {
    "价值": "value",
    "value": "value",
    "成长": "growth",
    "growth": "growth",
    "高股息": "dividend",
    "股息": "dividend",
    "dividend": "dividend",
    "garp": "garp",
    "反转": "turnaround",
    "turnaround": "turnaround",
    "防御": "defensive",
    "defensive": "defensive",
    "质量": "quality",
    "quality": "quality",
}

TECHNICAL_KEYWORDS = {
    "金叉": "golden-cross",
    "golden": "golden-cross",
    "均线多头": "ma-bullish",
    "多头排列": "ma-bullish",
    "放量突破": "volume-breakout",
    "volume": "volume-breakout",
    "超卖": "rsi-oversold",
    "oversold": "rsi-oversold",
    "布林": "bollinger-squeeze",
    "bollinger": "bollinger-squeeze",
    "盘整突破": "consolidation-breakout",
}

# ── P1 Enhancement: Chinese Stock Name Mapping ──────────────────
CHINA_STOCK_NAMES = {
    "贵州茅台": "600519", "茅台": "600519",
    "宁德时代": "300750", "宁德": "300750",
    "比亚迪": "002594", 
    "中国平安": "601318", "平安": "601318",
    "招商银行": "600036", "招行": "600036",
    "工商银行": "601398", "工行": "601398",
    "建设银行": "601939", "建行": "601939",
    "中国石油": "601857", "中国移动": "600941",
    "隆基绿能": "601012", "隆基": "601012",
    "药明康德": "603259", "海天味业": "603288",
    "恒瑞医药": "600276", "迈瑞医疗": "300760",
    "科大讯飞": "002230", "中芯国际": "688981",
    "立讯精密": "002475", "歌尔股份": "002241",
    "三一重工": "600031", "东方财富": "300059",
    "韦尔股份": "603501", "汇川技术": "300124",
    "阳光电源": "300274", "五粮液": "000858",
    "泸州老窖": "000568", "山西汾酒": "600809",
    "伊利股份": "600887", "海尔智家": "600690",
    "美的集团": "000333", "格力电器": "000651",
    "万科A": "000002", "中信证券": "600030",
    "长江电力": "600900", "万华化学": "600309",
    "海尔": "600690", "美的": "000333", "格力": "000651",
    "万科": "000002", "平安银行": "000001",
}

# ── P1 Enhancement: Session Context ─────────────────────────────
_last_symbol = None

def set_context(symbol: str):
    global _last_symbol
    _last_symbol = symbol

def get_context() -> Optional[str]:
    return _last_symbol



@dataclass
class RoutedCommand:
    intent: str
    argv: List[str]
    confidence: float
    reason: str
    warnings: List[str] = field(default_factory=list)

    @property
    def command_text(self) -> str:
        if not self.argv:
            return ""
        return "python finance.py " + " ".join(self.argv)


def route_query(query: str) -> RoutedCommand:
    text = " ".join(query.strip().split())
    lowered = text.lower()
    symbols = _extract_symbols(text)

    if not text:
        return _fallback("输入为空，请描述你想分析、筛选、生成报告或监控的标的。")

    if _has_any(lowered, ["数据源", "data source", "doctor", "健康检查", "连通"]):
        argv = ["doctor"]
        if _has_any(lowered, ["实时", "live", "请求"]):
            argv.append("--live")
        return RoutedCommand("data_source_doctor", argv, 0.92, "检查金融数据源状态")

    if _has_any(lowered, ["自选", "watchlist"]):
        return _route_watchlist(text, lowered, symbols)

    if _has_any(lowered, ["组合", "portfolio", "仓位组合", "资产组合"]):
        return _route_portfolio(text, lowered, symbols)

    if _has_any(lowered, ["筛选", "选股", "screen", "找股票", "短名单"]):
        return _route_screen(text, lowered)

    if _has_any(lowered, ["报告", "研报", "html", "正式", "出一份"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("生成报告需要一个股票代码，例如 002050、600519 或 AAPL。")
        argv = [
            "report",
            symbol,
            "--style",
            "kami",
            "--live-data-check",
            "--require-technical-data",
            "--strict-data",
            "--enforce-freshness",
        ]
        return RoutedCommand("report", argv, 0.91, "生成正式投资者 HTML 研究报告")

    if _has_any(lowered, ["财报预测", "preview", "预测"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("财报预测需要一个股票代码。")
        return RoutedCommand("earnings_preview", ["preview", symbol], 0.88, "预测未来季度财报")

    if _has_any(lowered, ["财报回顾", "recap", "回顾"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("财报回顾需要一个股票代码。")
        return RoutedCommand("earnings_recap", ["recap", symbol], 0.88, "回顾历史财报表现")

    if _has_any(lowered, ["业绩比较", "compare", "对比", "比较"]) and len(symbols) >= 2:
        return RoutedCommand("earnings_compare", ["compare", *symbols], 0.86, "比较多只股票业绩")

    if _has_any(lowered, ["财报", "earnings"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("财报分析需要一个股票代码。")
        return RoutedCommand("earnings", ["earnings", symbol], 0.84, "执行完整财报分析")

    if _has_any(lowered, ["体检", "健康分", "财务健康", "health"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("财报体检需要一个股票代码。")
        return RoutedCommand("financial_health", ["health", symbol], 0.88, "生成财报体检评分")

    if _has_any(lowered, ["异常", "造假", "应收", "存货", "现金流背离", "check"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("财务异常检测需要一个股票代码。")
        return RoutedCommand("financial_check", ["check", symbol], 0.87, "检测财务异常")

    if _has_any(lowered, ["预警", "风险", "alerts", "alert"]):
        if not symbols:
            return _fallback("风险预警需要至少一个股票代码。")
        return RoutedCommand("risk_alerts", ["alerts", *symbols], 0.86, "聚合股票风险预警")

    if _has_any(lowered, ["估值工作台", "情景估值", "workbench"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("估值工作台需要一个股票代码。")
        return RoutedCommand("valuation_workbench", ["workbench", symbol], 0.86, "运行三情景估值工作台")

    if _has_any(lowered, ["估值", "value", "公允价值"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("估值计算需要一个股票代码。")
        return RoutedCommand("valuation", ["value", symbol], 0.83, "执行快速估值计算")

    if _has_any(lowered, ["深度", "research", "投研"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("深度研报需要一个股票代码。")
        return RoutedCommand("deep_research", ["research", symbol], 0.82, "执行深度投研分析")

    # P2: Backtest routing
    if _has_any(lowered, ["回测", "backtest", "策略验证"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("回测需要一个股票代码，例如：回测 300750")
        argv = ["backtest", symbol]
        if _has_any(lowered, ["walk-forward", "wf", "滚动"]):
            argv.append("--walk-forward")
        if _has_any(lowered, ["monte-carlo", "mc", "蒙特卡洛"]):
            argv.append("--monte-carlo")
        return RoutedCommand("backtest", argv, 0.88, "执行策略回测")

    # P2: A股特色数据路由
    if _has_any(lowered, ["龙虎榜", "游资", "top-list", "toplist"]):
        argv = ["a-share", "top-list"]
        if symbols:
            argv.extend(["--symbol", _first_symbol(symbols)])
        return RoutedCommand("a_share_toplist", argv, 0.90, "查看龙虎榜/游资动向")

    if _has_any(lowered, ["解禁", "限售", "lockup"]):
        argv = ["a-share", "lockup"]
        if symbols:
            argv.extend(["--symbol", _first_symbol(symbols)])
        return RoutedCommand("a_share_lockup", argv, 0.89, "查看解禁日历")

    if _has_any(lowered, ["北向", "北水", "northbound", "沪深港通"]):
        argv = ["a-share", "northbound"]
        if _has_any(lowered, ["十大", "持仓", "top"]):
            argv.append("--top")
        return RoutedCommand("a_share_northbound", argv, 0.89, "查看北向资金流向")

    # P1: Full-chain analysis routing
    if _has_any(lowered, ["全链路", "全面", "full", "完整分析", "深度分析", "综合分析", "全量分析"]):
        symbol = _first_symbol(symbols)
        if not symbol and _last_symbol:
            symbol = _last_symbol
        if symbol:
            set_context(symbol)
            return RoutedCommand("full_analyze", ["analyze", symbol, "--full"], 0.88, "执行全链路分析")

    # P1: Context continuation ("再看看估值")
    if _has_any(lowered, ["再", "继续", "接着", "也"]) and not symbols and _last_symbol:
        if _has_any(lowered, ["估值", "value"]):
            return RoutedCommand("valuation_continue", ["value", _last_symbol], 0.85, f"继续查看 {_last_symbol} 估值")
        if _has_any(lowered, ["报告", "研报"]):
            return RoutedCommand("report_continue", ["report", _last_symbol, "--style", "kami"], 0.85, f"继续生成 {_last_symbol} 报告")
        if _has_any(lowered, ["风险", "预警"]):
            return RoutedCommand("risk_continue", ["alerts", _last_symbol], 0.85, f"继续查看 {_last_symbol} 风险")

    symbol = _first_symbol(symbols)
    if symbol:
        set_context(symbol)
        return RoutedCommand("quick_analyze", ["analyze", symbol], 0.78, "默认执行快速分析")

    return _fallback("暂时无法识别意图。可以试试：帮我看贵州茅台、全链路分析 300750、再看看估值。")


def _route_watchlist(text: str, lowered: str, symbols: List[str]) -> RoutedCommand:
    if _has_any(lowered, ["检查", "风险", "触发", "check"]):
        return RoutedCommand("watchlist_check", ["watchlist", "check"], 0.91, "检查自选股触发条件")
    if _has_any(lowered, ["统计", "summary", "概览"]):
        return RoutedCommand("watchlist_summary", ["watchlist", "summary"], 0.88, "查看自选股统计")
    if _has_any(lowered, ["分组", "groups"]):
        return RoutedCommand("watchlist_groups", ["watchlist", "groups"], 0.86, "查看自选股分组")
    if _has_any(lowered, ["列表", "列出", "有哪些", "list"]):
        return RoutedCommand("watchlist_list", ["watchlist", "list"], 0.86, "列出自选股")

    if _has_any(lowered, ["添加", "加入", "加到", "add"]):
        symbol = _first_symbol(symbols)
        if not symbol:
            return _fallback("添加自选股需要一个股票代码。")
        argv = ["watchlist", "add", symbol]
        target = _extract_number_after(text, ["目标", "target"])
        stop = _extract_number_after(text, ["止损", "stop"])
        if target is not None:
            argv.extend(["--target", _format_number(target)])
        if stop is not None:
            argv.extend(["--stop", _format_number(stop)])
        return RoutedCommand("watchlist_add", argv, 0.9, "添加自选股并设置监控条件")

    return RoutedCommand("watchlist_list", ["watchlist", "list"], 0.72, "默认列出自选股")


def _route_portfolio(text: str, lowered: str, symbols: List[str]) -> RoutedCommand:
    if not symbols:
        return _fallback("组合分析需要股票代码列表，例如：600519 40%，002241 30%，000858 30%。")

    weights = _extract_percentages(text)
    symbol_arg = ",".join(symbols)

    if _has_any(lowered, ["优化", "optimize", "最优"]):
        return RoutedCommand("portfolio_optimize", ["portfolio", "optimize", symbol_arg], 0.86, "优化组合权重")

    argv = ["portfolio", "warnings" if _has_any(lowered, ["预警", "风险", "warning"]) else "analyze", symbol_arg]
    if len(weights) == len(symbols):
        argv.extend(["--weights", ",".join(_format_weight(weight) for weight in weights)])
    elif weights:
        warning = "识别到权重数量和股票数量不一致，已忽略权重。"
        return RoutedCommand("portfolio_analyze", argv, 0.75, "分析组合风险", [warning])

    return RoutedCommand("portfolio_analyze", argv, 0.86, "分析组合风险")


def _route_screen(text: str, lowered: str) -> RoutedCommand:
    argv = ["screen"]
    strategy = _match_first(lowered, STRATEGY_KEYWORDS)
    technical = _match_first(lowered, TECHNICAL_KEYWORDS)
    top = _extract_top_n(text)

    if strategy:
        argv.extend(["--strategy", strategy])
    if technical:
        argv.extend(["--technical", technical])
    if _has_any(lowered, ["评分", "打分", "排序", "scoring"]):
        argv.append("--scoring")
    if top:
        argv.extend(["--top", str(top)])

    if len(argv) == 1:
        argv.extend(["--strategy", "value", "--scoring"])
        reason = "未指定筛选条件，默认使用价值策略和多因子评分"
    else:
        reason = "按用户描述执行 A 股筛选"

    return RoutedCommand("screen", argv, 0.84, reason)


def _extract_symbols(text: str) -> List[str]:
    """提取股票代码 + P1: 识别中文股票名 + 上下文记忆"""
    symbols: List[str] = []
    for match in SYMBOL_PATTERN.findall(text.upper()):
        if match not in symbols:
            symbols.append(match)
    # P1: Chinese stock name resolution
    for name, code in CHINA_STOCK_NAMES.items():
        if name in text:
            if code not in symbols:
                symbols.append(code)
    # P1: Context memory fallback
    if not symbols and _last_symbol:
        symbols.append(_last_symbol)
    return symbols


def _first_symbol(symbols: List[str]) -> Optional[str]:
    return symbols[0] if symbols else None


def _has_any(text: str, keywords: List[str]) -> bool:
    return any(keyword.lower() in text for keyword in keywords)


def _match_first(text: str, mapping: dict) -> Optional[str]:
    for keyword, value in mapping.items():
        if keyword.lower() in text:
            return value
    return None


def _extract_number_after(text: str, labels: List[str]) -> Optional[float]:
    for label in labels:
        pattern = rf"{re.escape(label)}(?:价|价格)?\s*[:：]?\s*(\d+(?:\.\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def _extract_percentages(text: str) -> List[float]:
    return [float(value) / 100 for value in re.findall(r"(\d+(?:\.\d+)?)\s*%", text)]


def _extract_top_n(text: str) -> Optional[int]:
    match = re.search(r"(?:top|前)\s*(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else str(value)


def _format_weight(value: float) -> str:
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _fallback(message: str) -> RoutedCommand:
    return RoutedCommand("unknown", [], 0.0, message, [message])
