import importlib.util
from pathlib import Path

from skills.shared import (
    normalize_pattern_report,
    normalize_report_text,
    stock_display_name,
    translate_rating,
    translate_sector,
)


def _load_deep_research_analyzer():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "deep-research" / "analyzer.py"
    spec = importlib.util.spec_from_file_location("deep_research_analyzer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.StockAnalyzer


def test_localization_avoids_english_stock_identity_and_actions():
    name = stock_display_name(
        "AAPL",
        {"longName": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
    )

    assert name == "苹果公司（AAPL）"
    assert "Apple" not in name
    assert translate_sector("Technology") == "科技"
    assert translate_rating("buy") == "偏积极"
    assert "BUY" not in normalize_report_text("BUY SELL HOLD N/A")
    assert "暂无数据" in normalize_report_text("N/A")


def test_pattern_report_is_mutually_exclusive_and_timeframe_labelled():
    patterns = normalize_pattern_report(
        {
            "double_top": True,
            "double_bottom": True,
            "double_top_strength": 3,
            "double_bottom_strength": 2,
            "double_top_desc": "双顶形态（看跌）",
            "double_bottom_desc": "双底形态（看涨）",
        },
        timeframe="日线",
        lookback="最近30个交易日",
    )

    assert patterns["double_top"] is True
    assert patterns["double_bottom"] is False
    assert "double_bottom_desc" not in patterns
    assert patterns["形态时间级别"] == "日线"
    assert "最近30个交易日" in patterns["double_top_desc"]


def test_deep_research_html_conclusion_is_chinese_and_layered():
    StockAnalyzer = _load_deep_research_analyzer()
    analyzer = StockAnalyzer()
    results = {
        "symbol": "AAPL",
        "display_name": "苹果公司（AAPL）",
        "style": "value",
        "timestamp": "2026-04-28T10:00:00",
        "rating": {"rating": "🟡🟡🟡", "score": 3, "max_score": 5, "recommendation": "基本面尚可，需进一步分析"},
        "phases": {
            1: {
                "name": "公司事实底座",
                "data": {"公司基本信息": {"所属板块": "科技", "所属行业": "消费电子"}},
            },
            4: {
                "name": "财务质量分析",
                "data": {"现金流验证": {"判断": "良好"}, "异常排查": ["现金流健康"]},
            },
            7: {
                "name": "估值与护城河",
                "data": {"估值水平": {"判断": "合理"}, "护城河评分": {"评级": "中等护城河"}},
            },
        },
    }

    markdown = analyzer.generate_report_markdown(results)
    output_dir = Path(__file__).resolve().parents[1] / "outputs" / "test_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = analyzer.generate_report_html(results, str(output_dir))
    html = Path(html_path).read_text(encoding="utf-8")

    assert "# 苹果公司（AAPL）投资尽调报告" in markdown
    assert "股票名称" in markdown
    assert "综合结论" in html
    assert "一、综合观点" in html
    assert "二、关键依据" in html
    assert "三、风险与验证" in html
    assert "Apple" not in markdown + html
    assert "BUY" not in markdown + html
    assert "SELL" not in markdown + html
    assert "N/A" not in markdown + html
