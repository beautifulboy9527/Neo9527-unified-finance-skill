import importlib.util
from pathlib import Path


def _load_shared_module():
    path = Path(__file__).resolve().parents[1] / "skills" / "shared" / "technical_indicators.py"
    spec = importlib.util.spec_from_file_location("technical_indicators", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_collector_module():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "stock_data_collector.py"
    spec = importlib.util.spec_from_file_location("stock_data_collector", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sample_ohlcv():
    pandas = __import__("pandas")
    rows = []
    price = 100.0
    for index in range(110):
        if index in {20, 42, 66}:
            close = 96.0 + (index % 2) * 0.15
            low = 95.6
            high = 99.2
        elif index in {30, 54, 78}:
            close = 111.0 - (index % 2) * 0.15
            low = 107.5
            high = 111.5
        elif index == 104:
            close = 96.4
            low = 94.0
            high = 99.0
        elif index == 106:
            close = 110.4
            low = 107.0
            high = 113.0
        else:
            price += 0.08 if index < 80 else -0.03
            close = price
            low = close - 1.2
            high = close + 1.4
        volume = 5000
        if 98 <= close <= 102:
            volume = 25000
        rows.append({
            "date": f"2026-01-{index + 1:02d}",
            "open": close - 0.4,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
    return pandas.DataFrame(rows)


def test_volume_profile_calculates_poc_and_value_area():
    module = _load_shared_module()
    result = module.calculate_volume_profile(_sample_ohlcv(), bins=32, lookback=100)

    assert "error" not in result
    assert result["val"] < result["poc"] < result["vah"]
    assert 97 <= result["poc"] <= 104
    assert result["high_volume_nodes"]


def test_liquidity_pools_and_confluence_levels_are_detected():
    module = _load_shared_module()
    data = _sample_ohlcv()

    liquidity = module.identify_liquidity_pools(data, tolerance=0.01, lookback=100)
    confluence = module.calculate_confluence_support_resistance(data, lookback=100)

    assert liquidity["equal_lows"]
    assert liquidity["equal_highs"]
    assert any(sweep["type"] == "support" for sweep in liquidity["sweeps"])
    assert any(sweep["type"] == "resistance" for sweep in liquidity["sweeps"])
    assert confluence["supports"]
    assert confluence["resistances"]
    assert confluence["nearest_support"]["price"] <= confluence["current_price"]
    assert confluence["nearest_resistance"]["price"] >= confluence["current_price"]
    assert any("成交量" in source or "流动性" in source for source in confluence["nearest_support"]["sources"])


def test_stock_collector_exposes_confluence_support_resistance():
    module = _load_collector_module()
    result = module.StockDataCollector()._technical_from_history(_sample_ohlcv(), timeframe="日线")

    assert result["support_level"] < result["current_price"]
    assert result["resistance_level"] >= result["current_price"]
    assert result["support_source"]
    assert result["resistance_source"]
    assert result["support_confidence"] in {"高", "中", "低", "强", "弱", "待确认"}
    enhanced = result["enhanced"]
    assert "volume_profile" in enhanced
    assert "liquidity_pools" in enhanced
    assert "dynamic_levels" in enhanced
    assert "confluence_support_resistance" in enhanced
