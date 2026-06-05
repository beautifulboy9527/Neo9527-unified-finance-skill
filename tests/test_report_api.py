import asyncio
from types import SimpleNamespace


def test_report_preflight_api_returns_diagnostic_without_html(monkeypatch):
    from api import server

    def fake_context(symbol, request):
        return {
            "display_name": "三花智控（002050）",
            "preflight": {"status": "不建议生成", "can_generate": False},
            "data_sources": {
                "status": "正常",
                "collection": {"success": False, "warnings": ["没有K线"], "sources": []},
            },
        }

    monkeypatch.setattr(server, "_build_stock_report_context", fake_context)
    response = asyncio.run(server.report_preflight("002050", server.StockReportRequest()))

    assert response.status_code == 200
    assert b"preflight" in response.body
    assert b"html" not in response.body.lower()


def test_report_html_api_blocks_strict_report_when_preflight_fails(monkeypatch):
    from api import server

    def fake_context(symbol, request):
        return {
            "display_name": "三花智控（002050）",
            "preflight": {
                "status": "不建议生成",
                "can_generate": False,
                "blocking_issues": ["缺少K线与支撑压力"],
            },
            "technical_analysis": {},
        }

    monkeypatch.setattr(server, "_build_stock_report_context", fake_context)
    response = asyncio.run(server.report_html("002050", server.StockReportRequest(strict_data=True)))

    assert response.status_code == 422
    assert "没有取得可验证K线数据" in response.body.decode("utf-8")


def test_report_html_api_returns_investor_html_when_preflight_passes(monkeypatch):
    from api import server

    def fake_context(symbol, request):
        return {
            "display_name": "三花智控（002050）",
            "preflight": {"status": "可生成", "can_generate": True},
            "data_sources": {"status": "正常", "collection": {"success": True}},
            "financial_health": {},
            "valuation_workbench": {"current_price": 25, "valuation_range": {"low": 23, "high": 31}},
            "risk_alerts": {},
            "fundamental_analysis": {"industry": "自动化控制设备"},
            "technical_analysis": {
                "candles": [{"date": "2026-05-06", "open": 24, "high": 26, "low": 23, "close": 25}],
                "support_level": 23,
                "resistance_level": 26,
            },
        }

    class FakeReport:
        def generate(self, symbol, **kwargs):
            return "<html><body><h1>三花智控（002050）</h1><p>投资研究报告</p></body></html>"

    monkeypatch.setattr(server, "_build_stock_report_context", fake_context)
    monkeypatch.setattr(
        server,
        "load_stock_module",
        lambda file_name, module_name: SimpleNamespace(KamiStyleStockReport=FakeReport),
    )

    request = server.StockReportRequest(strict_data=True, require_technical_data=True)
    response = asyncio.run(server.report_html("002050", request))

    assert response.status_code == 200
    assert response.media_type == "text/html"
    assert "三花智控" in response.body.decode("utf-8")


def test_stock_report_request_accepts_price_rows_payload():
    from api import server

    request = server.StockReportRequest(
        price_rows=[
            {
                "date": "2026-05-06",
                "open": 24,
                "high": 26,
                "low": 23,
                "close": 25,
                "volume": 100000,
            }
        ]
    )

    assert request.price_rows[0].date == "2026-05-06"
    assert request.price_rows[0].close == 25


def test_report_context_uses_price_rows_for_technical_analysis(monkeypatch):
    from api import server

    class FakeCollector:
        @staticmethod
        def collect_stock_data(symbol):
            return {
                "success": False,
                "profile": {"name": "三花智控"},
                "market_data": {},
                "financial_fields": {},
                "valuation_fields": {},
                "fundamental_analysis": {},
                "technical_analysis": {},
                "warnings": [],
                "sources": [],
            }

        @staticmethod
        def collect_price_rows(rows, symbol="", timeframe="日线"):
            assert rows[0]["close"] == 25
            return {
                "success": True,
                "market_data": {"price": 25},
                "valuation_fields": {"current_price": 25},
                "technical_analysis": {
                    "candles": rows,
                    "support_level": 23,
                    "resistance_level": 26,
                },
                "warnings": [],
                "sources": [{"name": "外部K线数组", "status": "已读取", "fields": ["K线"]}],
            }

    class FakeHealth:
        @staticmethod
        def analyze_financial_health(symbol, **kwargs):
            return {"dimensions": {}}

    class FakeWorkbench:
        @staticmethod
        def analyze_valuation_workbench(symbol, **kwargs):
            return {"current_price": kwargs.get("current_price"), "valuation_range": {"low": 23, "high": 31}}

    class FakeRisk:
        @staticmethod
        def analyze_watchlist_alerts(symbols):
            return {"items": [{"highest_severity_cn": "提示"}]}

    class FakePreflight:
        @staticmethod
        def assess_report_readiness(**kwargs):
            assert kwargs["technical_analysis"]["support_level"] == 23
            return {"status": "可生成", "can_generate": True}

        @staticmethod
        def reconcile_risk_alerts_with_financials(risk_alerts, financial_health):
            return risk_alerts

    def fake_load(file_name, module_name):
        mapping = {
            "stock_data_collector.py": FakeCollector,
            "financial_health.py": FakeHealth,
            "valuation_workbench.py": FakeWorkbench,
            "risk_alerts.py": FakeRisk,
            "report_preflight.py": FakePreflight,
        }
        return mapping[file_name]

    monkeypatch.setattr(server, "load_stock_module", fake_load)

    request = server.StockReportRequest(
        current_price=25,
        price_rows=[{"date": "2026-05-06", "open": 24, "high": 26, "low": 23, "close": 25}],
    )
    context = server._build_stock_report_context("002050", request)

    assert context["technical_analysis"]["support_level"] == 23
    assert context["data_sources"]["collection"]["success"] is True
    assert context["preflight"]["can_generate"] is True
