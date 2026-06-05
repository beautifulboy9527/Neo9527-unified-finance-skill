import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_screener_data_source_does_not_fallback_to_fake_financial_defaults(monkeypatch):
    module = _load_module("screener_data_source", "skills/stock-skill/screener_data_source.py")
    manager = module.ScreenerDataSourceManager()

    monkeypatch.setattr(module, "AKSHARE_AVAILABLE", False)
    data = manager.get_financial_data_with_fallback("002050")

    assert data["data_quality"] == "unavailable"
    assert data["pe"] is None
    assert data["pb"] is None
    assert data["roe"] is None
    assert "未使用默认值" in data["missing_reason"]


def test_enhanced_screener_drops_unverified_financial_rows():
    module = _load_module("enhanced_screener", "skills/stock-skill/enhanced_screener.py")
    pandas = __import__("pandas")
    screener = module.EnhancedScreener(use_fallback=False)
    frame = pandas.DataFrame([
        {"code": "002050", "pe": None, "pb": None, "roe": None, "data_quality": "unavailable"},
        {"code": "600519", "pe": 22.0, "pb": 8.0, "roe": 28.0, "data_quality": "primary"},
    ])

    filtered = screener._drop_unverified_financial_rows(frame)

    assert filtered["code"].tolist() == ["600519"]
