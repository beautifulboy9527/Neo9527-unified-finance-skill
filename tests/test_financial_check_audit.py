import importlib.util
from pathlib import Path

from skills.shared.evidence import EvidenceLedger


def load_financial_check_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "skills" / "stock-skill" / "financial_check.py"
    spec = importlib.util.spec_from_file_location("financial_check_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_critical_financial_fields_are_unknown_not_low_risk(monkeypatch):
    module = load_financial_check_module()
    detector = module.FinancialAnomalyDetector()
    ledger = EvidenceLedger()
    ledger.add("revenue_0", 100.0, "yfinance/Yahoo Finance", field="Total Revenue")

    def fake_data(symbol):
        return {
            "_ledger": ledger,
            "warnings": ["应收账款和存货字段缺失"],
            "unavailable_checks": ["receivable", "inventory", "roe"],
            "revenue_growth": [10.0, 0, 0],
            "profit_growth": [5.0, 0, 0],
            "receivable_growth": [],
            "inventory_growth": [],
            "gross_margin": [30.0, 30.0, 30.0],
            "net_margin": [10.0, 10.0, 10.0],
            "summary": {"gross_margin": 30.0, "net_margin": 10.0, "roe": 0, "debt_ratio": 0},
        }

    monkeypatch.setattr(detector, "_get_financial_data", fake_data)

    result = detector.detect("AAPL")

    assert result["success"] is True
    assert result["risk_level"] == "unknown"
    assert result["verified"] is False
    assert result["evidence"]
    assert result["evidence_summary"]["quality_score"] > 0


def test_detected_anomaly_keeps_risk_verified_with_evidence(monkeypatch):
    module = load_financial_check_module()
    detector = module.FinancialAnomalyDetector()
    ledger = EvidenceLedger()
    ledger.add("receivable_growth_latest", 40.0, "AkShare", field="应收账款同比")
    ledger.add("revenue_growth_latest", 10.0, "AkShare", field="营业收入同比")

    def fake_data(symbol):
        return {
            "_ledger": ledger,
            "warnings": [],
            "unavailable_checks": [],
            "revenue_growth": [10.0, 0, 0],
            "profit_growth": [5.0, 0, 0],
            "receivable_growth": [40.0, 0, 0],
            "inventory_growth": [0.0, 0, 0],
            "gross_margin": [30.0, 30.0, 30.0],
            "net_margin": [10.0, 10.0, 10.0],
            "summary": {"gross_margin": 30.0, "net_margin": 10.0, "roe": 12, "debt_ratio": 30},
        }

    monkeypatch.setattr(detector, "_get_financial_data", fake_data)

    result = detector.detect("600519")

    assert result["risk_level"] in {"medium", "high"}
    assert result["verified"] is True
    assert result["anomaly_count"] == 1
    assert result["anomalies"][0]["type"] == "receivable"
