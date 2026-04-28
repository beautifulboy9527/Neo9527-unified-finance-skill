import importlib.util
from pathlib import Path


def load_regulation_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "skills" / "stock-skill" / "regulation_monitor.py"
    spec = importlib.util.spec_from_file_location("regulation_monitor_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_regulation_monitor_does_not_claim_low_risk_without_verified_data():
    module = load_regulation_module()

    result = module.check_regulation_risk("600519")

    assert result["success"] is True
    assert result["verified"] is False
    assert result["risk_level"] == "unknown"
    assert "未验证" in result["risk_description"]
