import importlib.util
from datetime import datetime
from pathlib import Path


def _load_preflight():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "report_preflight.py"
    spec = importlib.util.spec_from_file_location("report_preflight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_preflight_blocks_full_report_without_real_technical_data():
    module = _load_preflight()

    result = module.assess_report_readiness(
        symbol="002050",
        display_name="三花智控（002050）",
        collected_data={
            "profile": {"name": "三花智控"},
            "market_data": {"price": 25.0},
            "financial_fields": {"roe": 18, "gross_margin": 28, "debt_ratio": 45},
        },
        valuation_workbench={"current_price": 25, "valuation_range": {"low": 23, "high": 31}},
        technical_analysis={},
        fundamental_analysis={"industry": "自动化控制设备"},
    )

    assert result["status"] == "不建议生成"
    assert result["can_generate"] is False
    assert "K线与支撑压力" in result["missing_sections"]
    assert any("缺少K线与支撑压力" in issue for issue in result["blocking_issues"])


def test_report_preflight_allows_full_report_with_core_inputs():
    module = _load_preflight()

    result = module.assess_report_readiness(
        symbol="002050",
        display_name="三花智控（002050）",
        collected_data={
            "profile": {"name": "三花智控"},
            "market_data": {"price": 25.0},
            "financial_fields": {"roe": 18, "gross_margin": 28, "debt_ratio": 45},
        },
        valuation_workbench={"success": True, "current_price": 25, "valuation_range": {"low": 23, "high": 31}},
        technical_analysis={
            "candles": [{"date": "2026-05-06", "open": 24, "high": 26, "low": 23, "close": 25}],
            "support_level": 23,
            "resistance_level": 26,
        },
        fundamental_analysis={"industry": "自动化控制设备"},
    )

    assert result["status"] == "可生成"
    assert result["can_generate"] is True
    assert result["blocking_issues"] == []
    assert "K线与支撑压力" in result["ready_sections"]


def test_report_preflight_blocks_stale_kline_when_freshness_is_enforced():
    module = _load_preflight()

    result = module.assess_report_readiness(
        symbol="002050",
        display_name="三花智控（002050）",
        collected_data={
            "profile": {"name": "三花智控"},
            "market_data": {"price": 25.0},
            "financial_fields": {"roe": 18, "gross_margin": 28, "debt_ratio": 45},
        },
        valuation_workbench={"success": True, "current_price": 25, "valuation_range": {"low": 23, "high": 31}},
        technical_analysis={
            "candles": [{"date": "2026-04-01", "open": 24, "high": 26, "low": 23, "close": 25}],
            "support_level": 23,
            "resistance_level": 26,
        },
        fundamental_analysis={"industry": "自动化控制设备"},
        enforce_freshness=True,
        max_price_age_days=7,
        as_of=datetime(2026, 5, 7),
    )

    assert result["can_generate"] is False
    assert "K线截止日期" in result["missing_sections"]
    assert any("超过7天" in issue for issue in result["blocking_issues"])


def test_report_preflight_allows_recent_kline_when_freshness_is_enforced():
    module = _load_preflight()

    result = module.assess_report_readiness(
        symbol="002050",
        display_name="三花智控（002050）",
        collected_data={
            "profile": {"name": "三花智控"},
            "market_data": {"price": 25.0},
            "financial_fields": {"roe": 18, "gross_margin": 28, "debt_ratio": 45},
        },
        valuation_workbench={"success": True, "current_price": 25, "valuation_range": {"low": 23, "high": 31}},
        technical_analysis={
            "candles": [{"date": "2026-05-06", "open": 24, "high": 26, "low": 23, "close": 25}],
            "support_level": 23,
            "resistance_level": 26,
        },
        fundamental_analysis={"industry": "自动化控制设备"},
        enforce_freshness=True,
        max_price_age_days=7,
        as_of=datetime(2026, 5, 7),
    )

    assert result["can_generate"] is True
    assert "K线截止日期" in result["ready_sections"]


def test_reconcile_risk_alerts_removes_conflicting_financial_alerts():
    module = _load_preflight()

    reconciled = module.reconcile_risk_alerts_with_financials(
        {
            "highest_severity_cn": "高",
            "alert_count": 2,
            "alerts": [
                {"severity_cn": "高", "title": "成长质量偏弱", "message": "收入增速 -74.9%，利润增速 -76.8%", "verified": True},
                {"severity_cn": "中", "title": "估值波动", "message": "估值假设需要复核", "verified": True},
            ],
        },
        {"health_score": 81, "data_completeness": 1.0},
    )

    assert reconciled["alert_count"] == 1
    assert reconciled["highest_severity_cn"] == "中"
    assert reconciled["alerts"][0]["title"] == "估值波动"
    assert reconciled["reconciled_with_financial_health"] is True
