import importlib.util
from pathlib import Path

from skills.shared import validate_chinese_report


def _load_apple_report():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "apple_style_report.py"
    spec = importlib.util.spec_from_file_location("apple_style_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AppleStyleStockReport


def test_apple_style_report_is_complete_and_chinese():
    Reporter = _load_apple_report()
    html = Reporter().generate(
        "002050",
        display_name="三花智控（002050）",
        financial_health={
            "health_score": 81,
            "health_grade": "良好",
            "conclusion": "财报健康分为81/100，等级为良好。",
            "dimensions": {
                "profitability": {"name": "盈利能力", "score": 83, "reason": "ROE 18.0%，净利率 12.0%，毛利率 28.0%"}
            },
        },
        valuation_workbench={
            "valuation_range": {"low": 23.59, "mid": 27.75, "high": 31.91},
            "conclusion": "002050 当前价格位于情景估值区间内。",
            "scenarios": [
                {"name": "谨慎情景", "fair_value": 23.59, "upside": -0.057, "valuation_confidence": "medium"},
                {"name": "基准情景", "fair_value": 27.75, "upside": 0.11, "valuation_confidence": "medium"},
                {"name": "乐观情景", "fair_value": 31.91, "upside": 0.276, "valuation_confidence": "medium"},
            ],
        },
        risk_alerts={
            "highest_severity_cn": "低",
            "summary": "002050 当前最高预警级别为低，主要风险来自监管数据未验证。",
            "alerts": [
                {"severity_cn": "低", "title": "监管数据未验证", "message": "未接入可验证监管数据源。", "verified": False}
            ],
        },
    )

    assert "三花智控（002050）" in html
    assert "综合结论" in html
    assert "综合观点" in html
    assert "关键依据" in html
    assert "估值情景" in html
    assert "风险与验证" in html
    assert "公司与数据口径" in html
    assert "财务体检解读" in html
    assert "估值方法与假设" in html
    assert "资料来源" in html
    assert "截止日期与警告" in html
    assert "报告小结" in html
    assert "???" not in html
    assert "谨慎情景" in html
    assert "基准情景" in html
    assert "乐观情景" in html
    assert "后续验证清单" in html
    assert len(html) > 9000
    assert validate_chinese_report(html, require_layered_conclusion=True) == []
