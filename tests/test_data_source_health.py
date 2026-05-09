from skills.shared import check_data_sources
from skills.shared import data_source_health


def test_data_source_health_separates_dependency_and_live_checks():
    result = check_data_sources(providers=["pandas"], live=False)

    assert result["success"] is True
    assert result["live_checked"] is False
    assert result["items"][0]["live_status"] == "未检查"
    assert "doctor --live" in result["items"][0]["live_message"]


def test_data_source_health_reports_live_failures_without_marking_dependency_missing(monkeypatch):
    def fake_probe(_symbol):
        return {
            "live_checked": True,
            "live_status": "请求失败",
            "live_message": "代理拒绝连接",
        }

    monkeypatch.setitem(data_source_health.LIVE_PROBES, "_probe_yfinance", fake_probe)
    result = check_data_sources(providers=["yfinance"], live=True)

    assert result["items"][0]["available"] is True
    assert result["items"][0]["live_checked"] is True
    assert result["items"][0]["live_status"] == "请求失败"
    assert result["status"] == "接口异常"
    assert "yfinance" in result["live_failures"]
