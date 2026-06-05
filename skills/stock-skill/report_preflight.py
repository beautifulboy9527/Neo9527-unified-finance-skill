#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight checks for investor-facing stock reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "暂无数据", "未验证", "行业信息暂未验证"}
    return True


def _financial_field_count(collected_data: Dict, financial_health: Dict | None = None) -> int:
    fields = collected_data.get("financial_fields", {}) if collected_data else {}
    count = sum(1 for value in fields.values() if _has_value(value))
    dimensions = (financial_health or {}).get("dimensions") or {}
    available_dimensions = sum(1 for item in dimensions.values() if item.get("status") != "unavailable")
    return max(count, available_dimensions)


def _valuation_ready(valuation_workbench: Dict | None = None) -> bool:
    valuation = valuation_workbench or {}
    value_range = valuation.get("valuation_range") or {}
    return bool(
        valuation.get("success")
        or (_has_value(value_range.get("low")) and _has_value(value_range.get("high")))
        or _has_value(valuation.get("current_price"))
    )


def _technical_ready(technical_analysis: Dict | None = None) -> bool:
    technical = technical_analysis or {}
    candles = technical.get("candles") or []
    return bool(
        candles
        and _has_value(technical.get("support_level"))
        and _has_value(technical.get("resistance_level"))
    )


def _latest_candle_date(technical_analysis: Dict | None = None) -> str:
    technical = technical_analysis or {}
    candles = technical.get("candles") or []
    for candle in reversed(candles):
        date_value = candle.get("date") if isinstance(candle, dict) else None
        if _has_value(date_value):
            return str(date_value)[:10]
    return ""


def _price_freshness_ready(
    technical_analysis: Dict | None = None,
    *,
    enforce_freshness: bool = False,
    max_price_age_days: int = 10,
    as_of: datetime | None = None,
) -> tuple[bool, str]:
    latest_text = _latest_candle_date(technical_analysis)
    if not latest_text:
        return False, "K线缺少明确截止日期，无法确认技术面时效性。"
    if not enforce_freshness:
        return True, f"K线截止日期为{latest_text}。"
    try:
        latest = datetime.fromisoformat(latest_text)
    except ValueError:
        return False, f"K线截止日期格式无法识别：{latest_text}。"
    current = as_of or datetime.now()
    age_days = (current.date() - latest.date()).days
    if age_days < 0:
        return False, f"K线截止日期晚于当前检查日期：{latest_text}。"
    if age_days > max_price_age_days:
        return False, f"K线截止日期为{latest_text}，距检查日已超过{max_price_age_days}天。"
    return True, f"K线截止日期为{latest_text}，距检查日{age_days}天。"


def _ready_item(label: str, ready: bool, detail: str) -> Dict:
    return {"label": label, "ready": ready, "detail": detail}


def _missing_labels(items: Iterable[Dict]) -> List[str]:
    return [item["label"] for item in items if not item.get("ready")]


def assess_report_readiness(
    *,
    symbol: str,
    display_name: str = "",
    collected_data: Dict | None = None,
    financial_health: Dict | None = None,
    valuation_workbench: Dict | None = None,
    technical_analysis: Dict | None = None,
    fundamental_analysis: Dict | None = None,
    mode: str = "full",
    enforce_freshness: bool = False,
    max_price_age_days: int = 10,
    as_of: datetime | None = None,
) -> Dict:
    """Assess whether a report has enough real inputs to be investor-usable.

    The result is intended for CLI/API diagnostics. Investor-facing HTML should
    not print this checklist as a report section.
    """

    collected_data = collected_data or {}
    profile = collected_data.get("profile") or {}
    market_data = collected_data.get("market_data") or {}
    fundamental = fundamental_analysis or collected_data.get("fundamental_analysis") or {}
    technical = technical_analysis or collected_data.get("technical_analysis") or {}

    company_name = display_name or profile.get("name") or market_data.get("name")
    financial_count = _financial_field_count(collected_data, financial_health)
    technical_ready = _technical_ready(technical)
    valuation_ready = _valuation_ready(valuation_workbench)
    price_ready = _has_value(market_data.get("price")) or _has_value((valuation_workbench or {}).get("current_price"))
    industry_ready = _has_value(fundamental.get("industry")) or _has_value(profile.get("industry"))
    freshness_ready, freshness_detail = _price_freshness_ready(
        technical,
        enforce_freshness=enforce_freshness,
        max_price_age_days=max_price_age_days,
        as_of=as_of,
    )

    items = [
        _ready_item("公司名称", _has_value(company_name), "用于避免只有股票代码、没有股票名称的报告标题。"),
        _ready_item("当前价格", price_ready, "用于估值区间、上涨空间和风险收益位置判断。"),
        _ready_item("K线与支撑压力", technical_ready, "需要真实日线或外部CSV，不能使用示意图替代。"),
        _ready_item("K线截止日期", freshness_ready, freshness_detail),
        _ready_item("财务字段", financial_count >= 3, "至少需要盈利能力、资产负债或成长质量等多项真实字段。"),
        _ready_item("估值输入", valuation_ready, "至少需要当前价格、估值区间或可计算估值参数。"),
        _ready_item("行业口径", industry_ready, "用于解释利润率、估值倍数和业务景气度。"),
    ]

    blocking = []
    warnings = []
    required_labels = {"公司名称", "当前价格", "K线与支撑压力"} if mode == "technical" else {
        "公司名称",
        "当前价格",
        "K线与支撑压力",
        "K线截止日期",
        "财务字段",
        "估值输入",
    }
    for item in items:
        if item["ready"]:
            continue
        if item["label"] in required_labels:
            blocking.append(f"缺少{item['label']}：{item['detail']}")
        else:
            warnings.append(f"建议补充{item['label']}：{item['detail']}")

    if blocking:
        status = "不建议生成"
        message = "关键数据不足，继续生成会降低报告可信度。请先补充真实数据或使用外部CSV。"
    elif warnings:
        status = "可生成但需补充"
        message = "核心报告可以生成，但部分解释维度仍需补充，正式对外前建议复核。"
    else:
        status = "可生成"
        message = "核心行情、技术面、财务和估值输入已具备，可以生成正式研究报告。"

    return {
        "success": True,
        "symbol": symbol,
        "mode": mode,
        "status": status,
        "can_generate": not blocking,
        "message": message,
        "ready_sections": [item["label"] for item in items if item.get("ready")],
        "missing_sections": _missing_labels(items),
        "blocking_issues": blocking,
        "warnings": warnings,
        "items": items,
    }


def reconcile_risk_alerts_with_financials(risk_alerts: Dict | None, financial_health: Dict | None) -> Dict:
    """Remove financial-risk alerts that contradict higher-completeness report inputs."""

    alerts = dict(risk_alerts or {})
    health = financial_health or {}
    score = health.get("health_score")
    completeness = health.get("data_completeness", 0)
    if score is None or float(score) < 70 or float(completeness or 0) < 0.8:
        return alerts

    filtered = []
    removed = []
    conflict_markers = ("财务结论偏弱", "成长质量偏弱", "财报健康分", "收入增速", "利润增速")
    for item in alerts.get("alerts", []) or []:
        text = f"{item.get('title', '')} {item.get('message', '')}"
        if any(marker in text for marker in conflict_markers):
            removed.append(item)
            continue
        filtered.append(item)

    if not removed:
        return alerts

    alerts["alerts"] = filtered
    alerts["alert_count"] = len(filtered)
    if filtered:
        severity_order = {"高": 3, "中": 2, "低": 1, "提示": 0}
        highest = max(filtered, key=lambda item: severity_order.get(str(item.get("severity_cn", "提示")), 0))
        alerts["highest_severity_cn"] = highest.get("severity_cn", "提示")
        alerts["summary"] = "风险提示已按本报告财务口径复核，保留非冲突事项。"
    else:
        alerts["highest_severity_cn"] = "提示"
        alerts["summary"] = "风险提示已按本报告财务口径复核，未保留与财务结论相冲突的自动风险项。"
    alerts["reconciled_with_financial_health"] = True
    return alerts


__all__ = ["assess_report_readiness", "reconcile_risk_alerts_with_financials"]
