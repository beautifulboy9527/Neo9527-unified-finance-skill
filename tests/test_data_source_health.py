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


def test_classify_live_error_identifies_proxy_refusal(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:7890")

    result = data_source_health.classify_live_error(
        "ProxyError: Cannot connect to proxy. WinError 10061"
    )

    assert result["error_type"] == "proxy_connection_refused"
    assert result["proxy_env_present"] is True
    assert "HTTPS_PROXY" in result["proxy_env_vars"]
    assert "代理" in result["action_hint"]


def test_classify_live_error_identifies_remote_disconnect():
    result = data_source_health.classify_live_error(
        "RemoteDisconnected: Remote end closed connection without response"
    )

    assert result["error_type"] == "remote_disconnected"
    assert "切换备用源" in result["action_hint"]


def test_classify_live_error_identifies_local_cache_error():
    result = data_source_health.classify_live_error("unable to open database file")

    assert result["error_type"] == "local_cache_error"
    assert "缓存" in result["action_hint"]


def test_live_check_can_temporarily_suppress_proxy(monkeypatch):
    seen = {}

    def fake_probe(_symbol):
        import os

        seen["during_probe"] = os.environ.get("HTTPS_PROXY")
        return {
            "live_checked": True,
            "live_status": "请求成功",
            "live_message": "ok",
        }

    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:7890")
    monkeypatch.setitem(data_source_health.LIVE_PROBES, "_probe_yfinance", fake_probe)

    result = check_data_sources(providers=["yfinance"], live=True, suppress_proxy=True)

    assert seen["during_probe"] is None
    assert result["proxy_suppressed"] is True
    assert result["items"][0]["proxy_suppressed"] is True
    assert data_source_health.os.environ.get("HTTPS_PROXY") == "http://127.0.0.1:7890"
