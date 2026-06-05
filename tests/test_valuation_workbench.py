import importlib.util
from pathlib import Path


def _load_workbench():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "valuation_workbench.py"
    spec = importlib.util.spec_from_file_location("valuation_workbench", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ValuationWorkbench


class FakeCalculator:
    def calculate(self, symbol, methods="all", **params):
        discount_rate = params.get("discount_rate", 0.10)
        terminal_growth = params.get("terminal_growth", 0.025)
        peer_pe = params.get("peer_pe", 20)
        fair_value = 100 * (0.10 / discount_rate) * (1 + terminal_growth) * (peer_pe / 20)
        return {
            "success": True,
            "symbol": symbol,
            "current_price": 90,
            "fair_value": fair_value,
            "safe_price": fair_value * (1 - params.get("margin_of_safety", 0.30)),
            "valuation_confidence": "medium",
            "methods_used": ["dcf", "relative_pe"],
            "fallback_used": False,
            "assumptions": [
                {"name": "discount_rate", "value": discount_rate, "source": "user_input"},
                {"name": "terminal_growth", "value": terminal_growth, "source": "user_input"},
            ],
            "warnings": [],
            "evidence_summary": {"quality_score": 80},
        }


class MissingCalculator:
    def calculate(self, symbol, methods="all", **params):
        return {"success": False, "symbol": symbol, "error": "无法获取财务数据", "warnings": []}


def test_valuation_workbench_builds_three_scenarios_and_range():
    Workbench = _load_workbench()
    result = Workbench(calculator=FakeCalculator()).analyze(
        "AAPL",
        base_params={"discount_rate": 0.10, "terminal_growth": 0.025, "peer_pe": 20, "margin_of_safety": 0.3},
    )

    assert result["success"] is True
    assert len(result["scenarios"]) == 3
    assert result["valuation_range"]["low"] < result["valuation_range"]["high"]
    assert result["current_price"] == 90
    assert "估值区间" in result["conclusion"]
    assert all(item["assumptions"] for item in result["scenarios"])


def test_valuation_workbench_does_not_invent_when_data_missing():
    Workbench = _load_workbench()
    result = Workbench(calculator=MissingCalculator()).analyze("AAPL")

    assert result["success"] is False
    assert result["valuation_range"] == {"low": None, "mid": None, "high": None}
    assert "不能形成估值区间" in result["conclusion"]
    assert "无法获取财务数据" in result["warnings"]


def test_valuation_workbench_orders_bear_base_bull():
    Workbench = _load_workbench()
    result = Workbench(calculator=FakeCalculator()).analyze("AAPL", base_params={"peer_pe": 20})
    keys = [item["key"] for item in result["scenarios"]]

    assert keys == ["bear", "base", "bull"]
    assert result["scenarios"][0]["fair_value"] < result["scenarios"][1]["fair_value"]
    assert result["scenarios"][2]["fair_value"] > result["scenarios"][1]["fair_value"]


def test_valuation_workbench_accepts_manual_external_inputs_without_data_provider():
    Workbench = _load_workbench()
    result = Workbench().analyze(
        "002050",
        methods="relative",
        base_params={
            "current_price": 25,
            "eps": 1.2,
            "bps": 6,
            "pe": 20,
            "pb": 4,
            "peer_pe": 25,
            "peer_pb": 4,
            "sector": "Industrials",
        },
    )

    assert result["success"] is True
    assert result["current_price"] == 25
    assert result["valuation_range"]["low"] is not None
    assert any("外部传入估值字段" in warning for warning in result["warnings"])
    assert all(scenario["fair_value"] for scenario in result["scenarios"])
