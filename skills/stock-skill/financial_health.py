#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Financial health scoring for stock reports and commercial APIs."""

from __future__ import annotations

from datetime import datetime
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

from skills.shared import EvidenceLedger

try:
    from .financial_check import FinancialAnomalyDetector
except ImportError:
    _financial_check_path = Path(__file__).resolve().parent / "financial_check.py"
    _spec = importlib.util.spec_from_file_location("stock_financial_check", _financial_check_path)
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    FinancialAnomalyDetector = _module.FinancialAnomalyDetector


class FinancialHealthAnalyzer:
    """Turn financial statements into an auditable health scorecard."""

    DIMENSION_WEIGHTS = {
        "profitability": 25,
        "cashflow_quality": 25,
        "balance_sheet": 20,
        "working_capital": 15,
        "growth_quality": 15,
    }

    def __init__(self):
        self.detector = FinancialAnomalyDetector()

    def analyze(self, symbol: str, financial_data: Optional[Dict] = None) -> Dict:
        data = financial_data or self.detector._get_financial_data(symbol)
        if not data:
            ledger = EvidenceLedger()
            ledger.add(
                "financial_health_unavailable",
                "unavailable",
                "unverified",
                quality="missing",
                verified=False,
                note="未获取到可验证财务数据，不能生成财报体检分。",
            )
            return self._unknown_result(symbol, ledger, ["未获取到可验证财务数据"])

        ledger = data.get("_ledger") or EvidenceLedger()
        unavailable = list(data.get("unavailable_checks", []))
        warnings = list(data.get("warnings", []))

        dimensions = {
            "profitability": self._score_profitability(data),
            "cashflow_quality": self._score_cashflow_quality(data),
            "balance_sheet": self._score_balance_sheet(data),
            "working_capital": self._score_working_capital(data),
            "growth_quality": self._score_growth_quality(data),
        }

        completeness = self._data_completeness(dimensions, unavailable)
        weighted_score = 0.0
        available_weight = 0
        for key, item in dimensions.items():
            if item["status"] == "unavailable":
                continue
            weight = self.DIMENSION_WEIGHTS[key]
            weighted_score += item["score"] * weight
            available_weight += weight

        if available_weight == 0 or completeness < 0.4:
            overall_score = None
            grade = "未验证"
            conclusion = "关键财务字段不足，不能给出确定性财报健康分。"
        else:
            raw_score = weighted_score / available_weight
            overall_score = int(round(raw_score * completeness + 50 * (1 - completeness)))
            grade = self._grade(overall_score, completeness)
            conclusion = self._conclusion(overall_score, grade, completeness)

        risk_flags = self._risk_flags(dimensions, unavailable, warnings)
        return {
            "success": overall_score is not None,
            "symbol": symbol,
            "health_score": overall_score,
            "health_grade": grade,
            "conclusion": conclusion,
            "dimensions": dimensions,
            "risk_flags": risk_flags,
            "data_completeness": completeness,
            "unavailable_checks": unavailable,
            "warnings": warnings,
            "evidence": ledger.to_list(),
            "evidence_summary": ledger.summary(),
            "timestamp": datetime.now().isoformat(),
        }

    def _unknown_result(self, symbol: str, ledger: EvidenceLedger, warnings: List[str]) -> Dict:
        return {
            "success": False,
            "symbol": symbol,
            "health_score": None,
            "health_grade": "未验证",
            "conclusion": "关键财务字段不足，不能给出确定性财报健康分。",
            "dimensions": {},
            "risk_flags": warnings,
            "data_completeness": 0,
            "unavailable_checks": ["financial_data"],
            "warnings": warnings,
            "evidence": ledger.to_list(),
            "evidence_summary": ledger.summary(),
            "timestamp": datetime.now().isoformat(),
        }

    def _score_profitability(self, data: Dict) -> Dict:
        summary = data.get("summary", {})
        roe = self._num(summary.get("roe"))
        net_margin = self._num(summary.get("net_margin"))
        gross_margin = self._num(summary.get("gross_margin"))
        if roe is None and net_margin is None and gross_margin is None:
            return self._unavailable("盈利能力", "ROE、净利率、毛利率均缺失")

        score = 50
        if roe is not None:
            score += 20 if roe >= 15 else 10 if roe >= 8 else -10 if roe < 0 else 0
        if net_margin is not None:
            score += 15 if net_margin >= 15 else 8 if net_margin >= 5 else -15 if net_margin < 0 else 0
        if gross_margin is not None:
            score += 10 if gross_margin >= 40 else 5 if gross_margin >= 20 else -5
        return self._dimension("盈利能力", score, f"ROE {self._fmt(roe)}，净利率 {self._fmt(net_margin)}，毛利率 {self._fmt(gross_margin)}")

    def _score_cashflow_quality(self, data: Dict) -> Dict:
        operating_cf = self._series(data.get("operating_cash_flow"))
        profits = self._series(data.get("net_income")) or self._series(data.get("profit"))
        net_margin = self._series(data.get("net_margin"))
        if operating_cf and profits and profits[0] != 0:
            ratio = operating_cf[0] / profits[0]
            score = 85 if ratio >= 1 else 70 if ratio >= 0.8 else 45 if ratio >= 0.5 else 25
            return self._dimension("现金流质量", score, f"经营现金流/净利润为{ratio:.2f}，用于验证利润含金量")
        if len(net_margin) >= 2:
            change = net_margin[0] - net_margin[1]
            score = 65 if abs(change) <= 5 else 50 if change > 0 else 45
            return self._dimension("现金流质量", score, f"现金流字段缺失，以净利率变化作为弱验证，变化{change:.1f}个百分点")
        return self._unavailable("现金流质量", "经营现金流或净利润字段缺失")

    def _score_balance_sheet(self, data: Dict) -> Dict:
        summary = data.get("summary", {})
        debt_ratio = self._num(summary.get("debt_ratio"))
        if debt_ratio is None or debt_ratio == 0:
            return self._unavailable("资产负债安全", "资产负债率缺失")
        score = 85 if debt_ratio <= 40 else 70 if debt_ratio <= 60 else 45 if debt_ratio <= 75 else 25
        return self._dimension("资产负债安全", score, f"资产负债率 {debt_ratio:.1f}%")

    def _score_working_capital(self, data: Dict) -> Dict:
        rev_growth = self._first(data.get("revenue_growth"))
        ar_growth = self._first(data.get("receivable_growth"))
        inv_growth = self._first(data.get("inventory_growth"))
        if rev_growth is None and ar_growth is None and inv_growth is None:
            return self._unavailable("营运资本质量", "收入、应收账款、存货增长率均缺失")

        score = 75
        reasons = []
        if ar_growth is not None and rev_growth is not None:
            if ar_growth > max(20, rev_growth * 1.5):
                score -= 25
                reasons.append("应收账款增速显著高于收入增速")
            else:
                reasons.append("应收账款增速与收入增速未明显背离")
        if inv_growth is not None and rev_growth is not None:
            if inv_growth > max(30, rev_growth * 2):
                score -= 25
                reasons.append("存货增速显著高于收入增速")
            else:
                reasons.append("存货增速未明显异常")
        if not reasons:
            reasons.append("营运资本字段不完整，仅能弱验证")
            score -= 15
        return self._dimension("营运资本质量", score, "；".join(reasons))

    def _score_growth_quality(self, data: Dict) -> Dict:
        revenue_growth = self._first(data.get("revenue_growth"))
        profit_growth = self._first(data.get("profit_growth"))
        if revenue_growth is None and profit_growth is None:
            return self._unavailable("成长质量", "收入增长率和利润增长率缺失")

        score = 55
        if revenue_growth is not None:
            score += 15 if revenue_growth >= 10 else 5 if revenue_growth >= 0 else -15
        if profit_growth is not None:
            score += 20 if profit_growth >= 10 else 8 if profit_growth >= 0 else -20
        if revenue_growth is not None and profit_growth is not None and profit_growth < revenue_growth - 20:
            score -= 10
        return self._dimension("成长质量", score, f"收入增速 {self._fmt(revenue_growth)}，利润增速 {self._fmt(profit_growth)}")

    def _data_completeness(self, dimensions: Dict, unavailable: List[str]) -> float:
        available = sum(1 for item in dimensions.values() if item["status"] != "unavailable")
        base = available / len(dimensions) if dimensions else 0
        penalty = min(0.3, len(set(unavailable)) * 0.05)
        return round(max(0, base - penalty), 2)

    def _risk_flags(self, dimensions: Dict, unavailable: List[str], warnings: List[str]) -> List[str]:
        flags = []
        for item in dimensions.values():
            if item.get("score") is not None and item["score"] < 50:
                flags.append(f"{item['name']}偏弱：{item['reason']}")
            if item.get("status") == "unavailable":
                flags.append(f"{item['name']}不可验证：{item['reason']}")
        flags.extend(warnings[:3])
        if unavailable:
            flags.append("存在缺失字段，健康分需要结合原始财报复核。")
        return list(dict.fromkeys(flags))

    def _dimension(self, name: str, score: float, reason: str) -> Dict:
        score = max(0, min(100, int(round(score))))
        status = "healthy" if score >= 75 else "watch" if score >= 50 else "risk"
        return {"name": name, "score": score, "status": status, "reason": reason}

    def _unavailable(self, name: str, reason: str) -> Dict:
        return {"name": name, "score": None, "status": "unavailable", "reason": reason}

    def _grade(self, score: int, completeness: float) -> str:
        if completeness < 0.6:
            return "待验证"
        if score >= 85:
            return "优秀"
        if score >= 70:
            return "良好"
        if score >= 55:
            return "一般"
        return "偏弱"

    def _conclusion(self, score: int, grade: str, completeness: float) -> str:
        return f"财报健康分为{score}/100，等级为{grade}；数据完整度为{completeness:.0%}，结论需结合公告和原始财报复核。"

    def _series(self, value) -> List[float]:
        if not value:
            return []
        if not isinstance(value, list):
            value = [value]
        return [float(v) for v in value if self._num(v) is not None]

    def _first(self, value) -> Optional[float]:
        series = self._series(value)
        return series[0] if series else None

    def _num(self, value) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _fmt(self, value) -> str:
        number = self._num(value)
        return "暂无数据" if number is None else f"{number:.1f}%"


def analyze_financial_health(symbol: str) -> Dict:
    analyzer = FinancialHealthAnalyzer()
    return analyzer.analyze(symbol)


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_financial_health("AAPL"), ensure_ascii=False, indent=2))
