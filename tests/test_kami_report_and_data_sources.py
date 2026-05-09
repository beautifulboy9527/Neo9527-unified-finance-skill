import importlib.util
from pathlib import Path

from skills.shared import check_data_sources, validate_chinese_report


def _load_kami_report():
    path = Path(__file__).resolve().parents[1] / "skills" / "stock-skill" / "kami_style_report.py"
    spec = importlib.util.spec_from_file_location("kami_style_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.KamiStyleStockReport


def test_data_source_health_reports_missing_core_sources_without_crashing():
    result = check_data_sources()

    assert result["success"] is True
    assert result["total_count"] >= 4
    assert "items" in result
    assert all("status" in item and "action" in item for item in result["items"])


def test_kami_style_report_is_complete_chinese_and_quality_gated():
    Report = _load_kami_report()
    html = Report().generate(
        "002050",
        financial_health={
            "health_score": 81,
            "health_grade": "良好",
            "data_completeness": 1.0,
            "conclusion": "财报健康分为81/100，盈利能力和成长质量较好，但仍需复核现金流和营运资本。",
            "dimensions": {
                "profitability": {"name": "盈利能力", "score": 83, "reason": "净资产收益率、净利率和毛利率处于较好水平"},
                "cashflow": {"name": "现金流质量", "score": 76, "reason": "经营现金流覆盖利润，但需持续跟踪回款"},
            },
        },
        valuation_workbench={
            "current_price": 25,
            "valuation_range": {"low": 23.59, "mid": 27.75, "high": 31.91},
            "conclusion": "当前价格位于情景估值区间内，需结合真实可比公司倍数进一步确认。",
            "scenarios": [
                {"name": "谨慎情景", "fair_value": 23.59, "upside": -0.057, "valuation_confidence": "medium"},
                {"name": "基准情景", "fair_value": 27.75, "upside": 0.11, "valuation_confidence": "medium"},
                {"name": "乐观情景", "fair_value": 31.91, "upside": 0.276, "valuation_confidence": "medium"},
            ],
        },
        risk_alerts={
            "highest_severity_cn": "低",
            "alert_count": 1,
            "summary": "当前最高预警级别为低，主要风险来自数据源和监管信息待验证。",
            "alerts": [
                {"severity_cn": "低", "title": "监管数据待验证", "message": "尚未接入可验证监管公告源。", "verified": False}
            ],
        },
        data_sources={
            "status": "需要处理",
            "summary": "存在核心数据源不可用，报告必须披露缺失来源。",
            "critical_missing": ["AkShare"],
            "items": [
                {"name": "AkShare", "purpose": "A股行情、财务指标、资金流向", "status": "不可用", "action": "安装或配置后再生成真实报告"}
            ],
        },
    )

    assert "三花智控（002050）" in html
    assert "综合结论" in html
    assert "综合观点" in html
    assert "关键依据" in html
    assert "风险与验证" in html
    assert "报告小结" in html
    assert "资料来源" not in html
    assert "后续验证清单" not in html
    assert "采集说明" not in html
    assert "财报健康分" not in html
    assert "81/100" not in html
    assert "报告不会用示意图" in html
    assert "????" not in html
    assert "BUY" not in html
    assert "SELL" not in html
    assert "Technology" not in html
    assert len(html) > 7500
    assert validate_chinese_report(html, require_layered_conclusion=True) == []


def test_kami_style_report_uses_professional_kline_svg_and_hides_empty_timeframes():
    Report = _load_kami_report()
    candles = []
    for index in range(20):
        close = 20 + index * 0.2
        candles.append({
            "date": f"2026-04-{index+1:02d}",
            "open": close - 0.08,
            "high": close + 0.16,
            "low": close - 0.18,
            "close": close,
            "volume": 100000 + index * 1000,
            "ma5": close - 0.4 if index >= 4 else None,
            "ma20": close - 1.2 if index >= 1 else None,
        })

    html = Report().generate(
        "002050",
        display_name="三花智控（002050）",
        valuation_workbench={"current_price": 25, "valuation_range": {"low": 23, "high": 31}},
        technical_analysis={
            "timeframe": "日线",
            "lookback": "最近20个交易日",
            "trend": "日线偏强",
            "current_price": 25,
            "change_20d": 0.12,
            "ma5": 24.5,
            "ma20": 23.2,
            "support_level": 23.8,
            "resistance_level": 25.4,
            "support_tests": 3,
            "resistance_tests": 2,
            "support_strength": "强",
            "resistance_strength": "中",
            "support_distance_pct": 0.05,
            "resistance_distance_pct": 0.016,
            "volume_price_signal": "放量上涨",
            "dominant_pattern": {"timeframe": "日线", "name": "上升趋势延续", "description": "日线收盘价位于均线上方。", "confidence": "中"},
            "candles": candles,
            "multi_timeframe": {
                "日线": {"trend": "日线偏强", "lookback": "最近20个交易日", "change": 0.12, "support_level": 23.8, "resistance_level": 25.4},
                "周线": {"trend": "样本不足，趋势待验证", "lookback": "最近3个交易日"},
            },
        },
        fundamental_analysis={"industry": "自动化控制设备"},
    )

    assert 'viewBox="0 0 900 360"' in html
    assert "MA5" in html
    assert "MA20" in html
    assert "成交量" in html
    assert "主形态" in html
    assert "上升趋势延续" in html
    assert "支撑强" in html
    assert "放量上涨" in html
    assert "行情应对框架" in html
    assert "后续走势" in html
    assert "复盘动作" in html
    assert "日线用于判断接下来几天的进退位置" in html
    assert "放量站上25.40" in html
    assert "收盘跌破23.80" in html
    assert "#b23b35" in html
    assert "#2f6f4e" in html
    assert "周线</td><td>样本不足" not in html
    assert "周线样本不足，暂不展示空值表格" in html


def test_kami_style_report_generates_company_specific_non_boilerplate_analysis():
    Report = _load_kami_report()
    html = Report().generate(
        "002050",
        display_name="三花智控（002050）",
        financial_health={
            "health_score": 81,
            "data_completeness": 1.0,
            "dimensions": {
                "profitability": {"name": "盈利能力", "score": 83, "status": "healthy", "reason": "ROE 18.0%，净利率 12.0%，毛利率 28.0%"},
                "cashflow": {"name": "现金流质量", "score": 85, "status": "healthy", "reason": "经营现金流/净利润为1.25"},
            },
        },
        valuation_workbench={
            "current_price": 25,
            "valuation_range": {"low": 25, "high": 25},
            "conclusion": "当前价格位于价格锚附近。",
            "scenarios": [
                {"name": "谨慎情景", "fair_value": 25, "upside": 0, "valuation_confidence": "none"},
                {"name": "基准情景", "fair_value": 25, "upside": 0, "valuation_confidence": "none"},
                {"name": "乐观情景", "fair_value": 25, "upside": 0, "valuation_confidence": "none"},
            ],
        },
        risk_alerts={"highest_severity_cn": "提示", "alert_count": 0, "alerts": []},
        fundamental_analysis={
            "industry": "自动化控制设备",
            "business_summary": "三花智控主营制冷空调电器零部件和汽车热管理相关产品，投资者需要重点观察新能源车热管理、机器人执行器等业务放量节奏。",
            "moat": "客户结构、规模制造、热管理技术积累和新品放量能力",
        },
    )

    assert "汽车热管理相关业务的关键不只是收入增速" in html
    assert "机器人或执行器线索更偏中长期期权" in html
    assert "传统制冷空调零部件业务提供基本盘" in html
    assert "不能把它解释为目标价" in html
    assert "不能把它当作完整目标价" in html
    assert "当前核心依据来自财务表现、价格位置和风险提示" in html
    assert "暂不展示谨慎、基准、乐观三情景表" in html
    assert "估值结论为" not in html
    assert ">none<" not in html


def test_kami_style_report_adds_concrete_trigger_table():
    Report = _load_kami_report()
    html = Report().generate(
        "002050",
        display_name="三花智控（002050）",
        financial_health={
            "health_score": 81,
            "data_completeness": 1.0,
            "dimensions": {
                "profitability": {"name": "盈利能力", "score": 83, "status": "healthy", "reason": "ROE 18.0%，净利率 12.0%，毛利率 28.0%"},
                "cashflow": {"name": "现金流质量", "score": 85, "status": "healthy", "reason": "经营现金流/净利润为1.25"},
                "growth": {"name": "成长质量", "score": 90, "status": "healthy", "reason": "收入增速 10.0%，利润增速 15.0%"},
            },
        },
        valuation_workbench={"current_price": 25, "valuation_range": {"low": 25, "high": 25}},
        risk_alerts={"highest_severity_cn": "中", "alert_count": 1, "alerts": [{"severity_cn": "中", "title": "估值假设", "message": "估值输入不足", "verified": True}]},
        technical_analysis={
            "timeframe": "日线",
            "trend": "日线偏强",
            "support_level": 25.48,
            "resistance_level": 26.36,
            "change_20d": 0.127,
            "rsi14": 82.8,
            "volume_status": "温和放量",
        },
        fundamental_analysis={
            "business_summary": "三花智控主营制冷空调电器零部件和汽车热管理相关产品。",
            "moat": "客户结构、规模制造、热管理技术积累",
        },
    )

    assert "关键数字与触发条件" in html
    assert "支撑25.48，压力26.36" in html
    assert "收盘跌破25.48说明趋势结构转弱" in html
    assert "放量站上26.36才说明压力位被有效消化" in html
    assert "经营现金流/净利润为1.25" in html
    assert "补充可比公司市盈率、市净率、EPS、自由现金流或分业务估值" in html
