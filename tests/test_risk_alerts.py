import importlib.util
from pathlib import Path


def _load_risk_alerts():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "risk_alerts.py"
    spec = importlib.util.spec_from_file_location("risk_alerts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.RiskAlertEngine


def test_risk_alerts_aggregate_financial_health_and_anomalies():
    engine = _load_risk_alerts()()
    result = engine.analyze_symbol(
        "AAPL",
        fetch_live=False,
        financial_health={
            "health_score": 48,
            "health_grade": "偏弱",
            "data_completeness": 0.8,
            "dimensions": {
                "working_capital": {
                    "name": "营运资本质量",
                    "score": 35,
                    "status": "risk",
                    "reason": "应收账款增速显著高于收入增速",
                }
            },
        },
        financial_check={
            "risk_level": "high",
            "anomalies": [
                {"name": "应收账款异常", "severity": "high", "description": "应收账款增速显著高于营收增速"}
            ],
        },
    )

    titles = [alert["title"] for alert in result["alerts"]]
    assert result["highest_severity"] == "high"
    assert "财报健康分偏弱" in titles
    assert "营运资本质量偏弱" in titles
    assert "应收账款异常" in titles
    assert "buy" not in str(result).lower()
    assert "sell" not in str(result).lower()


def test_risk_alerts_do_not_hide_missing_data():
    engine = _load_risk_alerts()()
    result = engine.analyze_symbol(
        "MSFT",
        fetch_live=False,
        financial_health={
            "health_score": None,
            "health_grade": "未验证",
            "conclusion": "关键财务字段不足，不能给出确定性财报健康分。",
            "data_completeness": 0,
            "dimensions": {
                "cashflow_quality": {
                    "name": "现金流质量",
                    "score": None,
                    "status": "unavailable",
                    "reason": "经营现金流字段缺失",
                }
            },
        },
        regulatory={"risk_level": "unknown", "verified": False},
    )

    assert result["alert_count"] >= 2
    assert any(alert["verified"] is False for alert in result["alerts"])
    assert any("未验证" in alert["title"] or "不可验证" in alert["title"] for alert in result["alerts"])


def test_watchlist_alerts_sort_by_highest_severity():
    engine = _load_risk_alerts()()
    watchlist = [
        engine.analyze_symbol("LOW", fetch_live=False, regulatory={"risk_level": "unknown", "verified": False}),
        engine.analyze_symbol(
            "HIGH",
            fetch_live=False,
            financial_check={"risk_level": "high", "anomalies": [{"name": "现金流背离", "severity": "high", "description": "利润增长但现金流恶化"}]},
        ),
    ]
    watchlist.sort(key=lambda item: {"high": 4, "low": 2, "info": 1}.get(item["highest_severity"], 0), reverse=True)

    assert watchlist[0]["symbol"] == "HIGH"
