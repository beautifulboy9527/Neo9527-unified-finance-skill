import importlib.util
from pathlib import Path


def _load_analyzer():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "analyzer.py"
    spec = importlib.util.spec_from_file_location("stock_analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quick_analyzer_does_not_emit_neutral_score_without_data(monkeypatch):
    module = _load_analyzer()
    monkeypatch.setattr(module.StockAnalysisSkill, "_analyze_cn_stock", lambda self, symbol: {"symbol": symbol, "market": "cn", "data_source": ["akshare"]})

    result = module.analyze_stock("002353")

    assert result["success"] is False
    assert result["score"] is None
    assert result["signals"] == []
    assert result["data_quality"]["status"] == "data_unavailable"
    assert "不生成中性占位评分" in result["summary"]


def test_quick_analyzer_scores_when_price_payload_exists(monkeypatch):
    module = _load_analyzer()
    monkeypatch.setattr(
        module.StockAnalysisSkill,
        "_analyze_cn_stock",
        lambda self, symbol: {"symbol": symbol, "market": "cn", "price": 10.0, "technical": {"trend": "日线偏强"}},
    )

    result = module.analyze_stock("002353")

    assert result["success"] is True
    assert isinstance(result["score"], int)
    assert result["data_quality"]["status"] == "verified"
