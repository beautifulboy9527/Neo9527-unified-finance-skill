import importlib.util
import sys
from pathlib import Path

import pytest

root = Path(__file__).resolve().parents[1]
path = root / "skills" / "stock-skill" / "regulation_monitor.py"

pytestmark = pytest.mark.skipif(
    not path.exists(),
    reason="regulation_monitor.py was removed in P1 cleanup"
)


def test_regulation_monitor_rejects_default_low_risk(monkeypatch):
    if not path.exists():
        pytest.skip("module removed")
    spec = importlib.util.spec_from_file_location("regulation_monitor_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    monitor = mod.RegulationMonitor()
    result = monitor.check({})
    assert result["risk_level"] != "low"


def test_regulation_monitor_does_not_claim_low_risk_without_verified_data():
    if not path.exists():
        pytest.skip("module removed")
    spec = importlib.util.spec_from_file_location("regulation_monitor_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    monitor = mod.RegulationMonitor()
    result = monitor.check({})
    assert result["risk_level"] in ("unknown", "medium", "high")
