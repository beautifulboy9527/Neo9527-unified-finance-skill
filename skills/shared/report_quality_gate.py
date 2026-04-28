#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic quality checks for generated finance reports."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List


FORBIDDEN_ACTION_TERMS = (
    "BUY",
    "SELL",
    "HOLD",
    "STRONG_BUY",
    "STRONG_SELL",
)

ENGLISH_INDUSTRY_TERMS = (
    "Technology",
    "Healthcare",
    "Financial Services",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Communication Services",
    "Basic Materials",
    "Real Estate",
    "Utilities",
    "Industrials",
)

TIMEFRAME_TERMS = ("分钟", "小时", "日线", "周线", "月线", "季线", "年线")


@dataclass
class ReportQualityIssue:
    code: str
    message: str
    severity: str = "error"

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def validate_chinese_report(text: str, *, require_layered_conclusion: bool = False) -> List[ReportQualityIssue]:
    """Validate core Chinese-report constraints requested by finance users."""
    issues: List[ReportQualityIssue] = []
    content = text or ""

    for term in FORBIDDEN_ACTION_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", content):
            issues.append(ReportQualityIssue("english_action", f"报告包含英文评级或动作词：{term}"))

    if re.search(r"\bN/A\b|\bUnknown\b", content):
        issues.append(ReportQualityIssue("missing_placeholder", "报告包含英文缺失值占位，应使用“暂无数据”并说明缺失原因。"))

    for term in ENGLISH_INDUSTRY_TERMS:
        if term in content:
            issues.append(ReportQualityIssue("english_industry", f"报告包含英文行业或板块：{term}"))

    if "双顶" in content and "双底" in content:
        issues.append(ReportQualityIssue("pattern_conflict", "报告同时出现双顶和双底，应按信号强度或价格位置保留一个。"))

    for pattern in ("双顶", "双底", "头肩顶", "头肩底"):
        for match in re.finditer(pattern, content):
            window = content[max(0, match.start() - 30): match.end() + 50]
            if not any(term in window for term in TIMEFRAME_TERMS):
                issues.append(ReportQualityIssue("missing_pattern_timeframe", f"{pattern}未在邻近文本标注时间级别。"))
                break

    if require_layered_conclusion:
        required = ("综合观点", "关键依据", "风险与验证")
        missing = [section for section in required if section not in content]
        if missing:
            issues.append(ReportQualityIssue("weak_conclusion_structure", f"综合结论缺少层次：{', '.join(missing)}"))

    return issues


def assert_report_quality(text: str, *, require_layered_conclusion: bool = False) -> None:
    issues = validate_chinese_report(text, require_layered_conclusion=require_layered_conclusion)
    if issues:
        detail = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise ValueError(f"报告质量门禁未通过：{detail}")


def issues_to_dicts(issues: Iterable[ReportQualityIssue]) -> List[Dict[str, str]]:
    return [issue.to_dict() for issue in issues]
