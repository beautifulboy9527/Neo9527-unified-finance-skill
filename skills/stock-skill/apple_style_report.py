#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apple-style Chinese stock HTML report."""

from __future__ import annotations

from datetime import datetime
import html
from typing import Dict, Iterable, List

from skills.shared import assert_report_quality, normalize_report_text, stock_display_name


class AppleStyleStockReport:
    """Generate a polished Apple-style HTML report from audited module outputs."""

    def generate(
        self,
        symbol: str,
        *,
        display_name: str = "",
        financial_health: Dict | None = None,
        valuation_workbench: Dict | None = None,
        risk_alerts: Dict | None = None,
        technical_analysis: Dict | None = None,
        fundamental_analysis: Dict | None = None,
        data_sources: Dict | None = None,
    ) -> str:
        display_name = display_name or stock_display_name(symbol, {})
        financial_health = financial_health or {}
        valuation_workbench = valuation_workbench or {}
        risk_alerts = risk_alerts or {}
        technical_analysis = technical_analysis or {}
        fundamental_analysis = fundamental_analysis or {}
        data_sources = data_sources or {}

        score = financial_health.get("health_score")
        grade = financial_health.get("health_grade", "未验证")
        valuation_range = valuation_workbench.get("valuation_range", {})
        alerts = risk_alerts.get("alerts", [])

        html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(display_name)} 投资研究报告</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            color: #f5f5f7;
            background: #000;
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
            letter-spacing: 0;
        }}
        .page {{ max-width: 1180px; margin: 0 auto; padding: 56px 24px; }}
        .hero {{
            min-height: 72vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            border-bottom: 1px solid #1d1d1f;
        }}
        .eyebrow {{ color: #86868b; font-size: 15px; margin-bottom: 16px; }}
        h1 {{ font-size: clamp(44px, 8vw, 92px); line-height: 1.02; margin: 0; font-weight: 700; }}
        .hero-subtitle {{ color: #a1a1a6; font-size: 22px; line-height: 1.5; max-width: 820px; margin-top: 24px; }}
        .section {{ padding: 56px 0; border-bottom: 1px solid #1d1d1f; }}
        .section-title {{ font-size: 34px; line-height: 1.15; margin: 0 0 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
        .card {{ background: #161617; border: 1px solid #2b2b2f; border-radius: 18px; padding: 24px; min-height: 150px; }}
        .label {{ color: #86868b; font-size: 14px; margin-bottom: 10px; }}
        .value {{ font-size: 30px; font-weight: 700; line-height: 1.15; }}
        .muted {{ color: #a1a1a6; line-height: 1.75; }}
        .accent {{ color: #2997ff; }}
        .warning {{ color: #ffd60a; }}
        .danger {{ color: #ff453a; }}
        .pill {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: #242426; color: #d2d2d7; font-size: 13px; margin-bottom: 12px; }}
        .list {{ display: grid; gap: 12px; }}
        .alert {{ padding: 16px 18px; background: #161617; border: 1px solid #2b2b2f; border-radius: 14px; }}
        .alert-title {{ font-weight: 700; margin-bottom: 6px; }}
        .footer {{ color: #86868b; font-size: 13px; line-height: 1.7; padding-top: 32px; }}
        .narrative {{ background: #101012; border: 1px solid #2b2b2f; border-radius: 18px; padding: 24px; margin-bottom: 16px; }}
        .narrative h3 {{ margin: 0 0 12px; font-size: 20px; }}
        .narrative p {{ margin: 0; }}
        .table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 14px; }}
        .table th, .table td {{ border-bottom: 1px solid #2b2b2f; padding: 14px 12px; text-align: left; vertical-align: top; }}
        .table th {{ color: #86868b; font-weight: 500; background: #161617; }}
        .table td {{ color: #d2d2d7; }}
        @media (max-width: 720px) {{
            .page {{ padding: 32px 18px; }}
            .hero {{ min-height: 62vh; }}
            .section-title {{ font-size: 28px; }}
        }}
    </style>
</head>
<body>
    <main class="page">
        <section class="hero">
            <div class="eyebrow">Neo9527 Finance Skill · 股票研究报告 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            <h1>{html.escape(display_name)}</h1>
            <p class="hero-subtitle">{html.escape(self._hero_summary(financial_health, valuation_workbench, risk_alerts))}</p>
        </section>

        <section class="section">
            <h2 class="section-title">综合结论</h2>
            <div class="card" style="margin-bottom:16px;">
                <div class="label">综合观点</div>
                <p class="muted">{html.escape(self._hero_summary(financial_health, valuation_workbench, risk_alerts))}</p>
            </div>
            <div class="grid">
                <div class="card">
                    <div class="label">财报健康</div>
                    <div class="value">{self._score_text(score)}</div>
                    <p class="muted">等级：{html.escape(str(grade))}</p>
                </div>
                <div class="card">
                    <div class="label">估值区间</div>
                    <div class="value">{self._valuation_range_text(valuation_range)}</div>
                    <p class="muted">{html.escape(valuation_workbench.get('conclusion', '估值结论暂不可用'))}</p>
                </div>
                <div class="card">
                    <div class="label">最高预警</div>
                    <div class="value">{html.escape(risk_alerts.get('highest_severity_cn', '提示'))}</div>
                    <p class="muted">{html.escape(risk_alerts.get('summary', '当前未形成可验证预警摘要'))}</p>
                </div>
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">公司与数据口径</h2>
            <div class="grid">
                <div class="card">
                    <div class="label">标的名称</div>
                    <div class="value">{html.escape(display_name)}</div>
                    <p class="muted">股票代码：{html.escape(symbol)}。报告按外部已验证字段和本地分析模块生成。</p>
                </div>
                <div class="card">
                    <div class="label">数据截止</div>
                    <div class="value">{datetime.now().strftime('%Y-%m-%d')}</div>
                    <p class="muted">本地未联网核验公告或行情实时更新，使用外部输入字段时需确认报告期和口径。</p>
                </div>
                <div class="card">
                    <div class="label">数据完整度</div>
                    <div class="value">{self._percent_text(financial_health.get('data_completeness'))}</div>
                    <p class="muted">完整度低时，健康分和估值区间应降权处理。</p>
                </div>
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">关键依据</h2>
            <div class="narrative">
                <h3>财务体检解读</h3>
                <p class="muted">{html.escape(self._financial_interpretation(financial_health))}</p>
            </div>
            <div class="grid">
                {self._dimension_cards(financial_health.get('dimensions', {}))}
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">基本面与行业逻辑</h2>
            {self._fundamental_section(fundamental_analysis, financial_health)}
        </section>

        <section class="section">
            <h2 class="section-title">技术面分析</h2>
            {self._technical_section(technical_analysis)}
        </section>

        <section class="section">
            <h2 class="section-title">估值情景</h2>
            <div class="narrative">
                <h3>估值方法与假设</h3>
                <p class="muted">{html.escape(self._valuation_interpretation(valuation_workbench))}</p>
            </div>
            <div class="grid">
                {self._scenario_cards(valuation_workbench.get('scenarios', []))}
            </div>
            {self._scenario_table(valuation_workbench.get('scenarios', []))}
        </section>

        <section class="section">
            <h2 class="section-title">风险与验证</h2>
            <div class="narrative">
                <h3>风险解释</h3>
                <p class="muted">{html.escape(self._risk_interpretation(risk_alerts))}</p>
            </div>
            <div class="list">
                {self._alert_rows(alerts)}
            </div>
        </section>

        <section class="section">
            <h2 class="section-title">数据来源与局限</h2>
            {self._source_and_warning_block(financial_health, valuation_workbench, risk_alerts, data_sources)}
        </section>

        <section class="section">
            <h2 class="section-title">报告小结</h2>
            <div class="narrative">
                <h3>后续验证清单</h3>
                <p class="muted">第一，核对最近一期年报或季报中的收入、利润、现金流、股本和负债口径；第二，使用真实同行公司中位数替换示例 PE/PB 假设；第三，补充监管公告、订单景气度和行业价格变化；第四，若价格突破估值区间或财务指标明显恶化，应重新运行财报体检和风险预警。</p>
            </div>
            <p class="muted">本报告按财报健康、情景估值、风险预警逐层形成结论。若数据来自外部输入，系统会保留字段来源和验证提示；若关键数据缺失，结论保持为待验证，不使用模拟数据补齐。</p>
        </section>

        <div class="footer">
            本报告仅供研究参考，不构成投资建议。所有判断依赖公开数据或外部传入数据，需结合公告、财报原文和个人风险承受能力复核。
        </div>
    </main>
</body>
</html>"""
        html_text = normalize_report_text(html_text)
        assert_report_quality(html_text, require_layered_conclusion=True)
        return html_text

    def _hero_summary(self, health: Dict, valuation: Dict, alerts: Dict) -> str:
        health_text = health.get("conclusion", "财报体检暂不可用")
        valuation_text = valuation.get("conclusion", "估值区间暂不可用")
        alert_text = alerts.get("summary", "风险预警暂不可用")
        return f"{health_text} {valuation_text} {alert_text}"

    def _score_text(self, score) -> str:
        return "未验证" if score is None else f"{score}/100"

    def _valuation_range_text(self, valuation_range: Dict) -> str:
        low = valuation_range.get("low")
        high = valuation_range.get("high")
        if low is None or high is None:
            return "未验证"
        return f"{low:.2f} - {high:.2f}"

    def _percent_text(self, value) -> str:
        if value is None:
            return "未验证"
        try:
            return f"{float(value):.0%}"
        except (TypeError, ValueError):
            return "未验证"

    def _financial_interpretation(self, health: Dict) -> str:
        score = health.get("health_score")
        grade = health.get("health_grade", "未验证")
        if score is None:
            return "关键财务字段不足，当前不能形成确定性财报健康分。报告不会用模拟数据补齐缺失字段。"
        return f"财报健康分为{score}/100，等级为{grade}。该分数综合盈利能力、现金流质量、资产负债安全、营运资本质量和成长质量；其中现金流与净利润匹配度用于判断利润含金量，营运资本用于观察应收和存货是否偏离收入增长。"

    def _valuation_interpretation(self, valuation: Dict) -> str:
        value_range = valuation.get("valuation_range", {})
        low = value_range.get("low")
        high = value_range.get("high")
        if low is None or high is None:
            return "缺少可验证估值方法，当前不生成估值区间。需要补充当前价格、每股收益、每股净资产、自由现金流、股本或可比公司倍数等字段。"
        return f"估值工作台使用谨慎、基准、乐观三种情景形成区间，当前区间为{low:.2f}至{high:.2f}。谨慎情景提高折现率并降低可比倍数，乐观情景降低折现率并提高增长或倍数，用于观察假设变化对公允价值的影响。"

    def _risk_interpretation(self, alerts: Dict) -> str:
        count = alerts.get("alert_count", 0)
        severity = alerts.get("highest_severity_cn", "提示")
        if not count:
            return "当前未触发重大风险预警，但这不等于无风险，仍需持续跟踪财报、估值和监管信息。"
        return f"当前共触发{count}条预警，最高级别为{severity}。预警按财务健康、财务异常、估值、监管、技术和数据质量归类，并区分已验证与待验证。"

    def _dimension_cards(self, dimensions: Dict) -> str:
        if not dimensions:
            return self._card("数据不足", "未验证", "关键财务字段不足，无法展示分项体检。")
        cards = []
        for item in dimensions.values():
            score = self._score_text(item.get("score"))
            cards.append(self._card(item.get("name", "分项体检"), score, item.get("reason", "暂无说明")))
        return "\n".join(cards)

    def _scenario_cards(self, scenarios: Iterable[Dict]) -> str:
        cards = []
        for item in scenarios:
            fair_value = item.get("fair_value")
            upside = item.get("upside")
            fair_value_text = "未验证" if fair_value is None else f"{fair_value:.2f}"
            upside_text = "暂无数据" if upside is None else f"{upside:.1%}"
            detail = f"上行空间：{upside_text}；置信度：{item.get('valuation_confidence', 'none')}"
            cards.append(self._card(item.get("name", "估值情景"), fair_value_text, detail))
        if not cards:
            return self._card("估值情景", "未验证", "缺少可用估值方法，未生成伪造区间。")
        return "\n".join(cards)

    def _scenario_table(self, scenarios: Iterable[Dict]) -> str:
        rows = []
        for item in scenarios:
            fair_value = item.get("fair_value")
            safe_price = item.get("safe_price")
            upside = item.get("upside")
            rows.append(f"""
                <tr>
                    <td>{html.escape(str(item.get('name', '情景')))}</td>
                    <td>{'未验证' if fair_value is None else f'{fair_value:.2f}'}</td>
                    <td>{'暂无数据' if safe_price is None else f'{safe_price:.2f}'}</td>
                    <td>{'暂无数据' if upside is None else f'{upside:.1%}'}</td>
                    <td>{html.escape(str(item.get('valuation_confidence', 'none')))}</td>
                    <td>{html.escape('；'.join(item.get('methods_used', [])) or '暂无')}</td>
                </tr>
            """)
        if not rows:
            return ""
        return f"""
            <div style="overflow-x:auto; margin-top: 18px;">
                <table class="table">
                    <thead>
                        <tr><th>情景</th><th>公允价值</th><th>安全价</th><th>上行空间</th><th>置信度</th><th>方法</th></tr>
                    </thead>
                    <tbody>{''.join(rows)}</tbody>
                </table>
            </div>
        """

    def _fundamental_section(self, fundamental: Dict, health: Dict) -> str:
        industry = fundamental.get("industry", "汽车热管理与工业控制部件")
        position = fundamental.get("position", "需结合年报、客户结构和产品结构进一步验证")
        business = fundamental.get("business", "公司基本面分析应覆盖主营业务、下游需求、客户集中度、产品价格、毛利率变化和资本开支周期。")
        growth = fundamental.get("growth", "成长质量需结合收入增速、利润增速、订单景气度和现金流兑现情况交叉验证。")
        health_text = self._financial_interpretation(health)
        return f"""
            <div class="narrative">
                <h3>行业与定位</h3>
                <p class="muted">所属方向：{html.escape(str(industry))}。{html.escape(str(position))}</p>
            </div>
            <div class="narrative">
                <h3>经营逻辑</h3>
                <p class="muted">{html.escape(str(business))}</p>
            </div>
            <div class="narrative">
                <h3>成长与质量</h3>
                <p class="muted">{html.escape(str(growth))} {html.escape(health_text)}</p>
            </div>
        """

    def _technical_section(self, technical: Dict) -> str:
        timeframe = technical.get("timeframe", "日线")
        trend = technical.get("trend", "未接入真实K线，趋势暂不可验证")
        support = technical.get("support", "暂无数据")
        resistance = technical.get("resistance", "暂无数据")
        momentum = technical.get("momentum", "暂无数据")
        volume = technical.get("volume", "暂无数据")
        pattern = technical.get("pattern", "暂无可验证形态")
        conclusion = technical.get("conclusion", "技术面需要真实K线、成交量和多周期指标确认；未接入数据时不输出确定性趋势判断。")
        return f"""
            <div class="grid">
                {self._card('时间级别', timeframe, '所有技术形态必须标注时间级别，避免把短线信号误读为中长期趋势。')}
                {self._card('趋势状态', trend, '趋势判断需结合均线、价格结构和成交量确认。')}
                {self._card('动量指标', momentum, 'RSI、MACD等指标应作为辅助验证，不单独构成结论。')}
                {self._card('量能状态', volume, '突破或跌破若无量能配合，可信度需要下调。')}
                {self._card('支撑区间', support, '支撑位用于观察风险暴露和失效条件。')}
                {self._card('压力区间', resistance, '压力位用于观察估值和情绪是否兑现。')}
            </div>
            <div class="narrative" style="margin-top:16px;">
                <h3>形态与结论</h3>
                <p class="muted">形态：{html.escape(str(pattern))}。{html.escape(str(conclusion))}</p>
            </div>
        """

    def _alert_rows(self, alerts: List[Dict]) -> str:
        if not alerts:
            return '<div class="alert"><div class="alert-title">暂无重大预警</div><div class="muted">仍需持续跟踪财报、估值和监管变化。</div></div>'
        rows = []
        for alert in alerts[:8]:
            status = "已验证" if alert.get("verified") else "待验证"
            rows.append(f"""
                <div class="alert">
                    <div class="pill">{html.escape(alert.get('severity_cn', '提示'))} · {status}</div>
                    <div class="alert-title">{html.escape(alert.get('title', '风险提示'))}</div>
                    <div class="muted">{html.escape(alert.get('message', '暂无说明'))}</div>
                </div>
            """)
        return "\n".join(rows)

    def _source_and_warning_block(self, health: Dict, valuation: Dict, alerts: Dict, data_sources: Dict | None = None) -> str:
        data_sources = data_sources or {}
        warnings = []
        warnings.extend(health.get("warnings", []) or [])
        warnings.extend(valuation.get("warnings", []) or [])
        for alert in alerts.get("alerts", []) or []:
            if not alert.get("verified"):
                warnings.append(f"{alert.get('title', '待验证事项')}：{alert.get('message', '')}")
        warnings = list(dict.fromkeys([str(item) for item in warnings if item]))
        if not warnings:
            warnings = ["未发现额外数据警告；仍需结合公告、财报原文和行情源复核。"]
        items = "".join(f"<li>{html.escape(item)}</li>" for item in warnings[:10])
        source_rows = []
        default_sources = {
            "A股行情接口": data_sources.get("quote", "未调用成功：本地缺少 AkShare/yfinance 或未传入行情源"),
            "A股财务接口": data_sources.get("financials", "未调用成功：本地缺少 AkShare，已使用外部传入字段示例"),
            "技术K线接口": data_sources.get("technical", "未调用成功：未接入真实K线，技术面仅展示框架或外部说明"),
            "估值输入": data_sources.get("valuation", "外部传入当前价、EPS、BPS、PE/PB等字段，并写入证据账本"),
            "监管数据": data_sources.get("regulatory", "未接入可验证监管数据源，相关结论为待验证"),
        }
        for name, status in default_sources.items():
            source_rows.append(f"<tr><td>{html.escape(name)}</td><td>{html.escape(str(status))}</td></tr>")
        return f"""
            <div class="narrative">
                <h3>资料来源</h3>
                <p class="muted">本报告使用 Neo9527 Finance Skill 本地模块生成。财务和估值字段可来自内置数据源或外部传入的已验证字段；本次报告若使用外部字段，需以最近一期公告、年报或季报原文复核。</p>
            </div>
            <div style="overflow-x:auto; margin-bottom:16px;">
                <table class="table">
                    <thead><tr><th>接口/数据源</th><th>调用状态与口径</th></tr></thead>
                    <tbody>{''.join(source_rows)}</tbody>
                </table>
            </div>
            <div class="narrative">
                <h3>截止日期与警告</h3>
                <ul class="muted">{items}</ul>
            </div>
        """

    def _card(self, title: str, value: str, detail: str) -> str:
        return f"""
            <div class="card">
                <div class="label">{html.escape(str(title))}</div>
                <div class="value">{html.escape(str(value))}</div>
                <p class="muted">{html.escape(str(detail))}</p>
            </div>
        """


def generate_apple_style_stock_report(symbol: str, **kwargs) -> str:
    return AppleStyleStockReport().generate(symbol, **kwargs)
