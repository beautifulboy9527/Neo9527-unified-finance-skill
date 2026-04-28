import importlib.util
from pathlib import Path

from skills.shared import EvidenceLedger


def _load_financial_health():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "financial_health.py"
    spec = importlib.util.spec_from_file_location("financial_health", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FinancialHealthAnalyzer


def _sample_data():
    ledger = EvidenceLedger()
    ledger.add("revenue_0", 120, "unit-test", field="revenue", unit="USD")
    ledger.add("net_income_0", 18, "unit-test", field="net_income", unit="USD")
    return {
        "_ledger": ledger,
        "summary": {"gross_margin": 45, "net_margin": 15, "roe": 18, "debt_ratio": 35},
        "revenue_growth": [12, 8, 5],
        "profit_growth": [18, 10, 7],
        "receivable_growth": [8, 6, 4],
        "inventory_growth": [5, 4, 3],
        "net_margin": [15, 14, 13],
        "warnings": [],
        "unavailable_checks": [],
    }


def test_financial_health_scorecard_scores_complete_data():
    analyzer = _load_financial_health()()
    result = analyzer.analyze("AAPL", _sample_data())

    assert result["success"] is True
    assert result["health_score"] >= 70
    assert result["health_grade"] in {"良好", "优秀"}
    assert result["data_completeness"] == 1
    assert set(result["dimensions"]) == {
        "profitability",
        "cashflow_quality",
        "balance_sheet",
        "working_capital",
        "growth_quality",
    }
    assert result["evidence_summary"]["items"] >= 2


def test_financial_health_marks_missing_critical_fields_unverified():
    analyzer = _load_financial_health()()
    data = {
        "_ledger": EvidenceLedger(),
        "summary": {},
        "warnings": ["资产负债表缺失"],
        "unavailable_checks": ["financial_data", "cashflow", "roe", "debt_ratio"],
    }
    result = analyzer.analyze("AAPL", data)

    assert result["success"] is False
    assert result["health_score"] is None
    assert result["health_grade"] == "未验证"
    assert "不能给出确定性财报健康分" in result["conclusion"]
    assert any("不可验证" in flag for flag in result["risk_flags"])


def test_financial_health_flags_working_capital_deterioration():
    analyzer = _load_financial_health()()
    data = _sample_data()
    data["receivable_growth"] = [45, 10, 5]
    data["inventory_growth"] = [60, 8, 4]
    result = analyzer.analyze("AAPL", data)

    assert result["dimensions"]["working_capital"]["score"] < 50
    assert any("营运资本质量偏弱" in flag for flag in result["risk_flags"])
