#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Watchlist risk alerts for commercial stock monitoring."""

from __future__ import annotations

from datetime import datetime
import importlib.util
from pathlib import Path
from typing import Dict, Iterable, List, Optional


SEVERITY_RANK = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
SEVERITY_CN = {
    "critical": "严重",
    "high": "高",
    "medium": "中",
    "low": "低",
    "info": "提示",
}


def _load_local_module(file_name: str, module_name: str):
    path = Path(__file__).resolve().parent / file_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise ImportError(f"无法加载模块：{file_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RiskAlertEngine:
    """Aggregate financial, valuation, regulatory, and technical risk signals."""

    def analyze_symbol(
        self,
        symbol: str,
        *,
        financial_health: Optional[Dict] = None,
        financial_check: Optional[Dict] = None,
        valuation: Optional[Dict] = None,
        technical: Optional[Dict] = None,
        regulatory: Optional[Dict] = None,
        fetch_live: bool = True,
    ) -> Dict:
        alerts: List[Dict] = []
        sources = {}

        if financial_health is None and fetch_live:
            financial_health = self._safe_call("financial_health.py", "analyze_financial_health", symbol)
        if financial_check is None and fetch_live:
            financial_check = self._safe_call("financial_check.py", "check_financial_anomaly", symbol)
        if regulatory is None and fetch_live:
            regulatory = self._safe_regulatory(symbol)

        for source_name, payload in {
            "financial_health": financial_health,
            "financial_check": financial_check,
            "valuation": valuation,
            "technical": technical,
            "regulatory": regulatory,
        }.items():
            if payload:
                sources[source_name] = payload

        alerts.extend(self._financial_health_alerts(financial_health or {}))
        alerts.extend(self._financial_check_alerts(financial_check or {}))
        alerts.extend(self._valuation_alerts(valuation or {}))
        alerts.extend(self._technical_alerts(technical or {}))
        alerts.extend(self._regulatory_alerts(regulatory or {}))

        alerts = self._dedupe_and_sort(alerts)
        return {
            "symbol": symbol,
            "alert_count": len(alerts),
            "highest_severity": alerts[0]["severity"] if alerts else "info",
            "highest_severity_cn": SEVERITY_CN.get(alerts[0]["severity"], "提示") if alerts else "提示",
            "alerts": alerts,
            "summary": self._summary(symbol, alerts),
            "sources_used": sorted(sources.keys()),
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_watchlist(self, symbols: Iterable[str], *, fetch_live: bool = True) -> Dict:
        items = [self.analyze_symbol(symbol, fetch_live=fetch_live) for symbol in symbols]
        items.sort(key=lambda item: SEVERITY_RANK.get(item["highest_severity"], 0), reverse=True)
        return {
            "watchlist_size": len(items),
            "items": items,
            "generated_at": datetime.now().isoformat(),
        }

    def _safe_call(self, file_name: str, function_name: str, symbol: str) -> Optional[Dict]:
        try:
            module = _load_local_module(file_name, f"risk_alert_{file_name.replace('.', '_')}")
            return getattr(module, function_name)(symbol)
        except Exception as exc:
            return {
                "success": False,
                "warnings": [f"{function_name}不可用：{exc}"],
                "unavailable_checks": [function_name],
            }

    def _safe_regulatory(self, symbol: str) -> Optional[Dict]:
        try:
            module = _load_local_module("regulation_monitor.py", "risk_alert_regulation")
            return module.RegulationMonitor().analyze_regulatory_impact(symbol)
        except Exception as exc:
            return {
                "risk_level": "unknown",
                "verified": False,
                "alerts": [f"监管数据不可用：{exc}"],
            }

    def _financial_health_alerts(self, result: Dict) -> List[Dict]:
        alerts = []
        grade = result.get("health_grade")
        score = result.get("health_score")
        completeness = result.get("data_completeness", 0)
        if grade == "未验证" or score is None:
            alerts.append(self._alert(
                "medium",
                "data_quality",
                "财报体检未验证",
                result.get("conclusion", "关键财务数据不足，不能形成确定性健康分。"),
                verified=False,
            ))
        elif score < 55:
            alerts.append(self._alert("high", "financial_health", "财报健康分偏弱", f"财报健康分为{score}/100，需优先复核盈利质量和资产负债风险。"))
        elif score < 70:
            alerts.append(self._alert("medium", "financial_health", "财报健康度一般", f"财报健康分为{score}/100，仍需跟踪分项短板。"))

        if completeness and completeness < 0.6:
            alerts.append(self._alert("medium", "data_quality", "财务数据完整度不足", f"数据完整度为{completeness:.0%}，报告结论应降权处理。", verified=False))

        for item in (result.get("dimensions") or {}).values():
            if item.get("status") == "risk":
                alerts.append(self._alert("high", "financial_health", f"{item.get('name')}偏弱", item.get("reason", "分项评分低于风险阈值。")))
            elif item.get("status") == "unavailable":
                alerts.append(self._alert("low", "data_quality", f"{item.get('name')}不可验证", item.get("reason", "字段缺失。"), verified=False))
        return alerts

    def _financial_check_alerts(self, result: Dict) -> List[Dict]:
        alerts = []
        for anomaly in result.get("anomalies", []) or []:
            severity = {"high": "high", "medium": "medium", "low": "low"}.get(anomaly.get("severity"), "medium")
            alerts.append(self._alert(severity, "financial_anomaly", anomaly.get("name", "财务异常"), anomaly.get("description", "发现财务异常。")))
        if result.get("risk_level") == "unknown":
            alerts.append(self._alert("medium", "data_quality", "财务异常检测未验证", "关键字段缺失，不能判断为低风险。", verified=False))
        return alerts

    def _valuation_alerts(self, result: Dict) -> List[Dict]:
        if not result:
            return []
        alerts = []
        current_price = self._num(result.get("current_price"))
        fair_value = self._num(result.get("fair_value"))
        confidence = str(result.get("valuation_confidence", "")).lower()
        if current_price and fair_value:
            premium = current_price / fair_value - 1
            if premium > 0.25:
                alerts.append(self._alert("high", "valuation", "估值溢价较高", f"当前价格较公允价值高{premium:.0%}，需复核增长和折现假设。"))
            elif premium > 0.1:
                alerts.append(self._alert("medium", "valuation", "估值安全边际不足", f"当前价格较公允价值高{premium:.0%}。"))
        if confidence in {"low", "unknown"}:
            alerts.append(self._alert("low", "valuation", "估值置信度偏低", "估值依赖缺失字段或模型默认假设。", verified=False))
        return alerts

    def _technical_alerts(self, result: Dict) -> List[Dict]:
        patterns = result.get("patterns", result) if result else {}
        alerts = []
        timeframe = patterns.get("形态时间级别") or patterns.get("timeframe") or "未标注时间级别"
        if patterns.get("double_top"):
            alerts.append(self._alert("high", "technical", "双顶形态风险", f"{timeframe}出现双顶形态，需等待跌破颈线或放量确认。"))
        if patterns.get("support_break"):
            alerts.append(self._alert("medium", "technical", "关键支撑被跌破", f"{timeframe}支撑位失守，需观察是否快速收复。"))
        if patterns.get("trend") in {"strong_downtrend", "downtrend"}:
            alerts.append(self._alert("medium", "technical", "趋势走弱", f"{timeframe}趋势偏弱，短中期风险暴露上升。"))
        return alerts

    def _regulatory_alerts(self, result: Dict) -> List[Dict]:
        if not result:
            return []
        risk_level = result.get("risk_level") or result.get("level")
        verified = bool(result.get("verified", False))
        if risk_level == "high":
            return [self._alert("high", "regulatory", "监管风险偏高", "存在需要优先复核的监管风险。", verified=verified)]
        if risk_level == "medium":
            return [self._alert("medium", "regulatory", "监管风险需关注", "监管或合规信息存在不确定性。", verified=verified)]
        if risk_level == "unknown" or not verified:
            return [self._alert("low", "regulatory", "监管数据未验证", "未接入可验证监管数据源，不能据此判断低风险。", verified=False)]
        return []

    def _alert(self, severity: str, category: str, title: str, message: str, *, verified: bool = True) -> Dict:
        return {
            "severity": severity,
            "severity_cn": SEVERITY_CN.get(severity, "提示"),
            "category": category,
            "title": title,
            "message": message,
            "verified": verified,
            "suggested_action": "复核原始数据并设置后续验证条件" if verified else "补充可验证数据后再下结论",
        }

    def _dedupe_and_sort(self, alerts: List[Dict]) -> List[Dict]:
        unique = {}
        for alert in alerts:
            unique[(alert["category"], alert["title"], alert["message"])] = alert
        return sorted(unique.values(), key=lambda item: SEVERITY_RANK.get(item["severity"], 0), reverse=True)

    def _summary(self, symbol: str, alerts: List[Dict]) -> str:
        if not alerts:
            return f"{symbol} 当前未触发重大风险预警，但仍需持续跟踪财报、估值和监管变化。"
        top = alerts[0]
        return f"{symbol} 当前最高预警级别为{top['severity_cn']}，主要风险来自{top['title']}。"

    def _num(self, value) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None


def analyze_risk_alerts(symbol: str) -> Dict:
    return RiskAlertEngine().analyze_symbol(symbol)


def analyze_watchlist_alerts(symbols: Iterable[str]) -> Dict:
    return RiskAlertEngine().analyze_watchlist(symbols)


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_risk_alerts("AAPL"), ensure_ascii=False, indent=2))
