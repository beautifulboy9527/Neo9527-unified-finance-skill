import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_collector():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "stock_data_collector.py"
    spec = importlib.util.spec_from_file_location("stock_data_collector", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stock_data_collector_discloses_missing_provider_without_fake_data():
    module = _load_collector()
    result = module.collect_stock_data("002050")

    assert result["symbol"] == "002050"
    assert result["market"] == "cn"
    assert "financial_fields" in result
    assert "valuation_fields" in result
    assert "warnings" in result
    assert isinstance(result["sources"], list)
    if not result["success"]:
        assert result["financial_fields"] == {}
        assert result["valuation_fields"] == {}
        assert any("未安装" in warning or "未获得" in warning or "采集失败" in warning for warning in result["warnings"])


def test_stock_data_collector_technical_from_history():
    module = _load_collector()
    pandas = __import__("pandas")
    closes = [10 + i * 0.2 for i in range(40)]
    hist = pandas.DataFrame({
        "日期": [f"2026-04-{i+1:02d}" for i in range(40)],
        "开盘": [value - 0.08 for value in closes],
        "收盘": closes,
        "最高": [value + 0.15 for value in closes],
        "最低": [value - 0.18 for value in closes],
        "成交量": [1000 + i for i in range(40)],
    })

    technical = module.StockDataCollector()._technical_from_history(hist)

    assert technical["timeframe"] == "日线"
    assert technical["lookback"] == "最近20个交易日"
    assert technical["trend"] in {"日线偏强", "日线偏弱", "日线震荡"}
    assert technical["ma5"] > 0
    assert technical["support_level"] > 0
    assert technical["resistance_level"] > 0
    assert technical["support_level"] < technical["current_price"]
    assert technical["resistance_level"] >= technical["current_price"]
    assert technical["rsi14"] is not None
    assert technical["macd"]["status"] in {"金叉", "死叉", "多头区间", "空头区间", "中性"}
    assert technical["bollinger"]["position"] in {"突破上轨", "跌破下轨", "中轨上方", "中轨下方"}
    assert technical["atr14"] > 0
    assert technical["volume_status"] in {"明显放量", "温和放量", "量能平稳", "明显缩量"}
    assert technical["volume_price_signal"] in {"放量上涨", "放量下跌", "缩量反弹", "缩量回落", "量价配合一般", "量价关系暂无足够数据"}
    assert technical["support_strength"] in {"强", "中", "弱", "待确认"}
    assert technical["resistance_strength"] in {"强", "中", "弱", "待确认"}
    assert technical["support_distance_pct"] is not None
    assert technical["resistance_distance_pct"] is not None
    assert technical["dominant_pattern"]["timeframe"] == "日线"
    assert technical["dominant_pattern"]["name"] in {"上升趋势延续", "下跌趋势延续", "区间震荡", "双顶风险", "双顶雏形", "双底修复", "双底雏形", "形态不明确"}
    assert len(technical["candles"]) == 20
    assert {"open", "high", "low", "close", "date"}.issubset(technical["candles"][0])
    assert "volume" in technical["candles"][0]
    assert sum(1 for candle in technical["candles"] if candle.get("ma20") is not None) >= 2


def test_collect_price_csv_generates_real_technical_analysis(tmp_path):
    module = _load_collector()
    csv_path = tmp_path / "002050_prices.csv"
    rows = ["日期,开盘,最高,最低,收盘,成交量"]
    for index in range(40):
        close = 20 + index * 0.3
        rows.append(f"2026-04-{index+1:02d},{close-0.1},{close+0.2},{close-0.3},{close},{100000+index}")
    csv_path.write_text("\n".join(rows), encoding="utf-8")

    result = module.collect_price_csv(str(csv_path), symbol="002050", timeframe="日线")

    assert result["success"] is True
    assert result["technical_analysis"]["timeframe"] == "日线"
    assert result["technical_analysis"]["support_level"] > 0
    assert result["technical_analysis"]["resistance_level"] > 0
    assert result["technical_analysis"]["rsi14"] is not None
    assert result["technical_analysis"]["macd"]["status"]
    assert result["technical_analysis"]["bollinger"]["position"]
    assert result["technical_analysis"]["atr14"] > 0
    assert "multi_timeframe" in result["technical_analysis"]
    assert "日线" in result["technical_analysis"]["multi_timeframe"]
    assert "周线" in result["technical_analysis"]["multi_timeframe"]
    assert len(result["technical_analysis"]["candles"]) == 20
    assert result["market_data"]["price"] == result["technical_analysis"]["current_price"]


def test_collect_price_rows_generates_real_technical_analysis():
    module = _load_collector()
    rows = []
    for index in range(40):
        close = 20 + index * 0.25
        rows.append({
            "date": f"2026-04-{index+1:02d}",
            "open": close - 0.1,
            "high": close + 0.2,
            "low": close - 0.3,
            "close": close,
            "volume": 100000 + index,
        })

    result = module.collect_price_rows(rows, symbol="002050", timeframe="日线")

    assert result["success"] is True
    assert result["technical_analysis"]["timeframe"] == "日线"
    assert result["technical_analysis"]["support_level"] > 0
    assert result["technical_analysis"]["resistance_level"] > 0
    assert result["technical_analysis"]["candles"]
    assert result["market_data"]["price"] == result["technical_analysis"]["current_price"]
    assert any(source["name"] == "外部K线数组" and source["fields"] for source in result["sources"])


def test_cn_collector_uses_efinance_as_history_fallback(monkeypatch):
    module = _load_collector()
    pandas = __import__("pandas")
    closes = [18 + i * 0.15 for i in range(45)]
    hist = pandas.DataFrame({
        "日期": [f"2026-03-{i+1:02d}" for i in range(45)],
        "股票名称": ["三花智控"] * 45,
        "开盘": [value - 0.05 for value in closes],
        "收盘": closes,
        "最高": [value + 0.12 for value in closes],
        "最低": [value - 0.16 for value in closes],
        "成交量": [200000 + i * 1000 for i in range(45)],
    })

    fake_efinance = SimpleNamespace(
        stock=SimpleNamespace(get_quote_history=lambda symbol: hist)
    )

    real_find_spec = module.find_spec

    def fake_find_spec(name):
        if name == "akshare":
            return None
        if name == "efinance":
            return object()
        if name == "baostock":
            return None
        return real_find_spec(name)

    real_import_module = module.importlib.import_module

    def fake_import_module(name):
        if name == "efinance":
            return fake_efinance
        return real_import_module(name)

    monkeypatch.setattr(module, "find_spec", fake_find_spec)
    monkeypatch.setattr(module.importlib, "import_module", fake_import_module)

    result = module.collect_stock_data("002050")

    assert result["success"] is True
    assert result["profile"]["name"] == "三花智控"
    assert result["technical_analysis"]["timeframe"] == "日线"
    assert result["technical_analysis"]["support_level"] > 0
    assert result["technical_analysis"]["resistance_level"] > 0
    assert result["market_data"]["price"] == result["technical_analysis"]["current_price"]
    assert any(source["name"] == "efinance" and source["fields"] for source in result["sources"])


def test_cn_collector_merges_akshare_financial_extensions(monkeypatch):
    module = _load_collector()
    pandas = __import__("pandas")
    closes = [18 + i * 0.15 for i in range(45)]
    hist = pandas.DataFrame({
        "日期": [f"2026-03-{i+1:02d}" for i in range(45)],
        "开盘": [value - 0.05 for value in closes],
        "收盘": closes,
        "最高": [value + 0.12 for value in closes],
        "最低": [value - 0.16 for value in closes],
        "成交量": [200000 + i * 1000 for i in range(45)],
    })
    spot = pandas.DataFrame([{"代码": "002050", "名称": "三花智控", "最新价": 24.6, "市盈率-动态": 20.5, "市净率": 3.2}])
    indicator = pandas.DataFrame([{"销售毛利率": 28.0, "销售净利率": 12.0, "净资产收益率": 18.0, "资产负债率": 45.0}])
    abstract = pandas.DataFrame([{"营业收入同比增长率": 10.5, "净利润同比增长率": 15.2}])
    cashflow = pandas.DataFrame([{"经营活动产生的现金流量净额": 150.0, "净利润": 120.0}])

    fake_akshare = SimpleNamespace(
        stock_zh_a_spot_em=lambda: spot,
        stock_zh_a_hist=lambda symbol, period="daily", adjust="qfq": hist,
        stock_financial_analysis_indicator=lambda symbol: indicator,
        stock_financial_abstract=lambda symbol: abstract,
        stock_financial_report_sina=lambda stock, symbol: cashflow if symbol == "现金流量表" else pandas.DataFrame(),
    )

    real_find_spec = module.find_spec

    def fake_find_spec(name):
        if name == "akshare":
            return object()
        if name in {"efinance", "baostock"}:
            return None
        return real_find_spec(name)

    real_import_module = module.importlib.import_module

    def fake_import_module(name):
        if name == "akshare":
            return fake_akshare
        return real_import_module(name)

    monkeypatch.setattr(module, "find_spec", fake_find_spec)
    monkeypatch.setattr(module.importlib, "import_module", fake_import_module)

    result = module.collect_stock_data("002050")

    assert result["financial_fields"]["revenue_growth"] == 10.5
    assert result["financial_fields"]["profit_growth"] == 15.2
    assert result["financial_fields"]["operating_cash_flow"] == 150.0
    assert result["financial_fields"]["net_income"] == 120.0
    assert any("经营现金流" in source["fields"] for source in result["sources"] if source["name"] == "AkShare")
