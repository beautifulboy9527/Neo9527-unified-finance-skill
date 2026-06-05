import importlib.util
from pathlib import Path


def _load_module(name, relative):
    path = Path(__file__).resolve().parents[1] / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_investment_plan_builds_review_schedule_from_monitor(tmp_path):
    monitor_module = _load_module("watchlist_monitor", Path("skills") / "stock-skill" / "watchlist_monitor.py")
    plan_module = _load_module("investment_plan", Path("skills") / "stock-skill" / "investment_plan.py")
    csv_path = Path(__file__).resolve().parent / "fixtures" / "watchlist_sample.csv"
    monitor = monitor_module.WatchlistMonitor()
    monitor_result = monitor.monitor(monitor.load_csv(str(csv_path)))

    builder = plan_module.InvestmentPlanBuilder()
    plan = builder.build(monitor_result)
    html_path = tmp_path / "plan.html"
    csv_output = tmp_path / "plan.csv"
    html = builder.generate_html(plan, str(html_path))
    builder.write_csv(plan, str(csv_output))

    assert plan["plan_size"] == 3
    assert plan["items"][0]["priority"] == "立即复核"
    assert "投资跟踪计划" in html
    assert "下次复核" in html
    assert "失效条件" in html
    assert "BUY" not in html
    assert "SELL" not in html
    assert "N/A" not in html
    assert html_path.exists()
    assert csv_output.exists()
