import importlib.util
from pathlib import Path


def _load_monitor():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "watchlist_monitor.py"
    spec = importlib.util.spec_from_file_location("watchlist_monitor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_watchlist_monitor_generates_investor_dashboard(tmp_path):
    module = _load_monitor()
    csv_path = Path(__file__).resolve().parent / "fixtures" / "watchlist_sample.csv"
    monitor = module.WatchlistMonitor()

    result = monitor.monitor(monitor.load_csv(str(csv_path)))
    html_path = tmp_path / "watchlist.html"
    html = monitor.generate_html(result, str(html_path))

    assert result["watchlist_size"] == 3
    assert result["items"][0]["highest_severity"] == "高"
    assert result["items"][0]["inputs"]["current_price"] is not None
    assert result["items"][0]["reasons"]
    assert any(item["display_name"] == "三花智控（002050）" for item in result["items"])
    assert "自选股监控面板" in html
    assert "触发条件" in html
    assert "下一步动作" in html
    assert "BUY" not in html
    assert "SELL" not in html
    assert "N/A" not in html
    assert "Technology" not in html
    assert html_path.exists()
