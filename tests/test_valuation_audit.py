import importlib.util
from pathlib import Path

from skills.shared.evidence import EvidenceLedger


def load_valuation_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "skills" / "stock-skill" / "valuation.py"
    spec = importlib.util.spec_from_file_location("valuation_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dcf_uses_reported_shares_not_hardcoded_share_count():
    module = load_valuation_module()
    calc = module.ValuationCalculator()
    ledger = EvidenceLedger()

    result = calc._dcf_valuation(
        {
            "free_cash_flow": 1_000.0,
            "free_cash_flow_history": [1_000.0, 900.0, 810.0],
            "shares_outstanding": 100.0,
            "cash": 50.0,
            "total_debt": 25.0,
        },
        {
            "discount_rate": 0.10,
            "terminal_growth": 0.025,
            "forecast_years": 5,
            "fcf_growth": 0.03,
        },
        ledger,
    )

    assert result["fair_value"] > 0
    assert result["shares_outstanding"] == 100.0
    assert result["sensitivity"]
    assert result["fair_value"] > 1.0


def test_dcf_refuses_to_use_missing_share_count_placeholder():
    module = load_valuation_module()
    calc = module.ValuationCalculator()

    result = calc._dcf_valuation(
        {"free_cash_flow": 1_000.0, "shares_outstanding": 0},
        {
            "discount_rate": 0.10,
            "terminal_growth": 0.025,
            "forecast_years": 5,
            "fcf_growth": 0.03,
        },
        EvidenceLedger(),
    )

    assert result["fair_value"] == 0
    assert "股本" in result["error"]


def test_calculate_returns_evidence_and_assumption_audit(monkeypatch):
    module = load_valuation_module()
    calc = module.ValuationCalculator()

    def fake_data(symbol, market):
        ledger = EvidenceLedger()
        ledger.add("price", 10.0, "yfinance/Yahoo Finance", field="currentPrice")
        return {
            "_ledger": ledger,
            "warnings": [],
            "price": 10.0,
            "eps": 1.0,
            "bps": 5.0,
            "pe": 10.0,
            "pb": 2.0,
            "free_cash_flow": 1_000.0,
            "free_cash_flow_history": [1_000.0, 900.0],
            "shares_outstanding": 100.0,
            "cash": 50.0,
            "total_debt": 25.0,
            "dividend": 0.2,
            "sector": "Technology",
        }

    monkeypatch.setattr(calc, "_get_financial_data", fake_data)

    result = calc.calculate("TEST", peer_pe=20, peer_pb=3, fcf_growth=0.03)

    assert result["success"] is True
    assert result["evidence"]
    assert result["assumptions"]
    assert result["evidence_summary"]["quality_score"] > 0
    assert result["valuation_confidence"] in {"low", "medium", "high"}
    assert result["fallback_used"] is False
