#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kami-inspired Chinese finance report generator."""

from __future__ import annotations

from datetime import datetime
import html
from typing import Dict, Iterable, List

from skills.shared import assert_report_quality, normalize_report_text, stock_display_name


COMPANY_PROFILES = {
    "002049": {
        "name": "紫光国微",
        "industry": "集成电路设计",
        "business_summary": (
            "紫光国微的业务核心是特种集成电路和智能安全芯片，同时覆盖石英晶体频率器件等领域。"
            "它更像是一家以安全、可靠、国产替代为关键词的芯片设计公司，而不是单纯消费电子周期股。"
        ),
        "segments": ["特种集成电路", "智能安全芯片", "石英晶体频率器件"],
        "segment_mix": [
            {"name": "特种集成电路", "revenue": "2025H1收入14.69亿元", "share": "48.20%", "margin": "毛利率71.12%"},
            {"name": "智能安全芯片", "revenue": "2025H1收入13.95亿元", "share": "45.78%", "margin": "毛利率44.16%"},
            {"name": "石英晶体频率器件", "revenue": "2025H1收入1.51亿元", "share": "4.96%", "margin": "毛利率11.13%"},
        ],
        "moat": "护城河主要来自高可靠芯片设计能力、细分市场客户认证、国产替代需求和安全芯片应用场景。",
        "drivers": [
            "特种集成电路需求和国产替代节奏",
            "智能安全芯片在政务、金融、通信、物联网等场景的放量",
            "高毛利业务占比变化和研发投入效率",
        ],
        "risks": [
            "半导体需求周期波动",
            "客户认证和项目节奏导致收入确认波动",
            "高研发投入能否持续转化为订单和现金流",
        ],
        "watch": [
            "特种集成电路订单和交付节奏",
            "智能安全芯片出货量与价格变化",
            "毛利率、应收账款和经营现金流是否同步改善",
        ],
        "source_note": "业务画像参考公司官网、公开经营分析和公开报告中的主营业务描述；正式对外前仍应以最新年报、季报和公告复核。",
    },
    "002050": {
        "name": "三花智控",
        "industry": "制冷控制与汽车热管理零部件",
        "business_summary": (
            "三花智控的主线是制冷空调控制元器件和汽车热管理零部件。"
            "传统制冷业务提供利润基本盘，新能源汽车热管理决定中期成长弹性，机器人/执行器更多属于远期业务期权。"
        ),
        "segments": ["制冷空调电器零部件", "汽车热管理零部件", "机器人/执行器等潜在增量"],
        "segment_mix": [
            {"name": "制冷空调电器零部件", "revenue": "2025年收入185.85亿元", "share": "59.93%", "margin": "毛利率28.77%"},
            {"name": "汽车零部件", "revenue": "2025年收入124.27亿元", "share": "40.07%", "margin": "毛利率约28.80%"},
            {"name": "机器人/执行器", "revenue": "仍以研发、试制、送样为主", "share": "尚未单独形成核心收入", "margin": "暂不适用"},
        ],
        "moat": "护城河主要来自全球客户体系、精密制造能力、热管理产品平台化和规模交付能力。",
        "drivers": [
            "制冷空调业务的全球份额和成本传导能力",
            "新能源汽车热管理单车价值量和客户放量",
            "机器人/执行器业务从验证走向量产的节奏",
        ],
        "risks": [
            "汽车链需求和客户排产波动",
            "原材料、汇率和价格年降对毛利率的压力",
            "机器人业务预期过高但短期利润贡献不足",
        ],
        "watch": [
            "汽车热管理订单、收入占比和毛利率",
            "经营现金流/净利润是否持续大于1",
            "制冷业务海外需求和机器人业务量产节点",
        ],
        "source_note": "业务画像参考公司官网、公开经营分析和公开研究资料中的主营业务描述；正式对外前仍应以最新年报、季报和公告复核。",
    },
}


class KamiStyleStockReport:
    """Generate a paper-like, research-note HTML report from audited outputs."""

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
        enhanced_technical: Dict | None = None,
        evidence_ledger: Dict | None = None,
        entry_signals: Dict | None = None,
        risk_management: Dict | None = None,
        generated_at: datetime | None = None,
    ) -> str:
        generated_at = generated_at or datetime.now()
        display_name = display_name or stock_display_name(symbol, {})
        financial_health = financial_health or {}
        valuation_workbench = valuation_workbench or {}
        risk_alerts = risk_alerts or {}
        technical_analysis = technical_analysis or {}
        fundamental_analysis = fundamental_analysis or {}
        data_sources = data_sources or {}
        enhanced_technical = enhanced_technical or {}
        evidence_ledger = evidence_ledger or {}
        entry_signals = entry_signals or {}
        risk_management = risk_management or {}
        fundamental_analysis = self._enrich_fundamental(symbol, fundamental_analysis)

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
      background: #f5f4ed;
      color: #171717;
      font-family: "PingFang SC", "Microsoft YaHei", "Noto Serif SC", serif;
      letter-spacing: 0;
    }}
    .sheet {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 56px 72px 64px;
      background:
        linear-gradient(rgba(27, 54, 93, 0.035) 1px, transparent 1px),
        #f5f4ed;
      background-size: 100% 36px;
    }}
    .header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 36px;
      align-items: start;
      padding-bottom: 28px;
      border-bottom: 1px solid #ddd9cc;
    }}
    .title-block {{
      border-left: 5px solid #1b365d;
      padding-left: 22px;
    }}
    .kicker {{
      color: #1b365d;
      font-size: 16px;
      letter-spacing: 2px;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0;
      font-size: 46px;
      line-height: 1.12;
      font-weight: 800;
    }}
    .subtitle {{
      margin: 12px 0 0;
      color: #4b4b45;
      font-size: 18px;
      line-height: 1.7;
    }}
    .price-card {{
      text-align: right;
      color: #1b365d;
    }}
    .big-number {{
      font-size: 44px;
      font-weight: 800;
      line-height: 1.05;
    }}
    .small {{
      color: #66645d;
      font-size: 14px;
      line-height: 1.7;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 20px;
      padding: 22px 0 26px;
      border-bottom: 1px solid #ddd9cc;
    }}
    .metric-value {{
      color: #1b365d;
      font-size: 30px;
      font-weight: 800;
    }}
    .metric-label {{
      color: #55534d;
      font-size: 15px;
      margin-top: 4px;
    }}
    section {{ padding: 28px 0; }}
    h2 {{
      margin: 0 0 16px;
      font-size: 31px;
      line-height: 1.25;
    }}
    h3 {{
      margin: 0 0 10px;
      font-size: 19px;
      color: #1b365d;
    }}
    p {{
      margin: 0 0 13px;
      font-size: 17px;
      line-height: 1.85;
    }}
    .lead {{
      font-size: 19px;
      line-height: 1.85;
      font-weight: 650;
    }}
    .callout {{
      margin: 22px 0 0;
      padding: 18px 22px;
      border-left: 5px solid #1b365d;
      background: rgba(255, 255, 255, 0.48);
      border-radius: 4px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    .panel {{
      background: rgba(255, 255, 255, 0.36);
      border: 1px solid #e1ddd0;
      border-radius: 6px;
      padding: 18px 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 15px;
    }}
    th, td {{
      border-bottom: 1px solid #ddd9cc;
      padding: 13px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #1b365d;
      font-weight: 800;
      background: rgba(255, 255, 255, 0.42);
    }}
    .risk-row {{
      padding: 14px 0;
      border-bottom: 1px solid #ddd9cc;
    }}
    .figure {{
      margin: 20px 0 0;
      padding: 18px 20px;
      border: 1px solid #ddd9cc;
      background: rgba(255, 255, 255, 0.32);
      border-radius: 6px;
    }}
    .chart-wrap {{
      width: 100%;
      overflow: hidden;
      margin-top: 14px;
    }}
    svg.candle-chart {{
      display: block;
      width: 100%;
      height: auto;
      min-height: 250px;
    }}
    .caption {{
      margin-top: 12px;
      color: #68665e;
      font-size: 14px;
      line-height: 1.65;
      text-align: center;
    }}
    .footer {{
      border-top: 1px solid #ddd9cc;
      color: #66645d;
      font-size: 13px;
      line-height: 1.75;
      padding-top: 18px;
    }}
    @media (max-width: 760px) {{
      .sheet {{ padding: 32px 20px; }}
      .header {{ grid-template-columns: 1fr; }}
      .price-card {{ text-align: left; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 36px; }}
    }}
  </style>
</head>
<body>
  <main class="sheet">
    <header class="header">
      <div class="title-block">
        <div class="kicker">投资研究报告</div>
        <h1>{html.escape(display_name)}</h1>
        <p class="subtitle">资料截止：{generated_at.strftime('%Y-%m-%d %H:%M')}；面向投资者的公司、财务、估值与风险分析。</p>
      </div>
      <div class="price-card">
        <div class="big-number">{self._price_text(valuation_workbench)}</div>
        <div class="small">当前价格或外部传入价格</div>
        <div class="small">{self._source_status_text(data_sources)}</div>
      </div>
    </header>

    <div class="metrics">
      {self._metric("当前价格", self._price_text(valuation_workbench), "价格口径见页脚")}
      {self._metric("财务观察", self._financial_metric_text(financial_health), "盈利、现金流、负债")}
      {self._metric("估值状态", self._valuation_metric_text(valuation_workbench), self._valuation_metric_note(valuation_workbench))}
      {self._metric("风险等级", risk_alerts.get("highest_severity_cn", "提示"), self._risk_metric_note(risk_alerts))}
    </div>

    <section>
      <h2>综合结论</h2>
      <p class="lead"><strong>综合观点：</strong>{html.escape(self._integrated_view(financial_health, valuation_workbench, risk_alerts, technical_analysis, fundamental_analysis))}</p>
      <p><strong>关键依据：</strong>{html.escape(self._key_evidence(financial_health, valuation_workbench, data_sources, technical_analysis, fundamental_analysis))}</p>
      <p><strong>风险与验证：</strong>{html.escape(self._risk_summary(risk_alerts, data_sources))}</p>
      <div class="callout">{html.escape(self._decision_note(financial_health, valuation_workbench, risk_alerts, technical_analysis, fundamental_analysis))}</div>
      {self._action_table(financial_health, valuation_workbench, risk_alerts, technical_analysis, fundamental_analysis)}
    </section>

    <section>
      <h2>投资逻辑</h2>
      <p>{html.escape(self._investment_logic(fundamental_analysis, financial_health, valuation_workbench))}</p>
      <div class="grid">
        <div class="panel">
          <h3>基本面判断</h3>
          <p>{html.escape(self._fundamental_text(fundamental_analysis, financial_health))}</p>
        </div>
        <div class="panel">
          <h3>财务分析</h3>
          <p>{html.escape(self._financial_text(financial_health))}</p>
        </div>
      </div>
    </section>

    <section>
      <h2>公司与行业</h2>
      <p>{html.escape(self._company_context(fundamental_analysis, data_sources))}</p>
      {self._business_map_block(fundamental_analysis)}
      <div class="callout">{html.escape(self._assumption_text(valuation_workbench, financial_health))}</div>
    </section>

    <section>
      <h2>近期价格走势</h2>
      <p>{html.escape(self._technical_text(technical_analysis))}</p>
      {self._price_figure_block(technical_analysis)}
      {self._multi_timeframe_block(technical_analysis)}
      {self._technical_playbook_block(technical_analysis)}
    </section>
<section>      <h2>增强技术分析</h2>      {self._enhanced_technical_block(enhanced_technical, technical_analysis)}      {self._entry_signals_block(entry_signals)}    </section>

    <section>
      <h2>财务概览</h2>
      {self._dimension_table(financial_health.get("dimensions", {}))}
      <p>{html.escape(self._financial_followup(financial_health))}</p>
    </section>

    <section>
      <h2>估值情景</h2>
      <p>{html.escape(self._valuation_text(valuation_workbench))}</p>
      {self._scenario_table(valuation_workbench.get("scenarios", []))}
    </section>

    <section>
      <h2>主要风险</h2>
      {self._alerts_block(risk_alerts.get("alerts", []))}
    </section>
<section>      <h2>风控建议</h2>      {self._risk_management_block(risk_management)}    </section>    <section>      <h2>数据溯源</h2>      {self._evidence_block(evidence_ledger)}    </section>

    <section>
      <h2>报告小结</h2>
      <p>{html.escape(self._closing_summary(financial_health, valuation_workbench, risk_alerts, data_sources))}</p>
    </section>

    <div class="footer">
      本报告仅用于研究和信息整理，不构成投资建议。当前部分行情、财报和行业字段需要以正式公告或授权行情数据进一步确认；报告不使用模拟数据补齐。
    </div>
  </main>
</body>
</html>"""
        html_text = normalize_report_text(html_text)
        assert_report_quality(html_text, require_layered_conclusion=True)
        return html_text

    def _metric(self, label: str, value: str, note: str) -> str:
        return f'<div><div class="metric-value">{html.escape(str(value))}</div><div class="metric-label">{html.escape(label)} · {html.escape(str(note))}</div></div>'

    def _enrich_fundamental(self, symbol: str, fundamental: Dict) -> Dict:
        code = str(symbol).upper().replace(".SZ", "").replace(".SH", "")
        profile = COMPANY_PROFILES.get(code, {})
        enriched = dict(fundamental or {})
        for key in ("industry", "business_summary", "moat"):
            if not enriched.get(key) or str(enriched.get(key)).startswith("行业信息暂未验证"):
                if profile.get(key):
                    enriched[key] = profile[key]
        for key in ("segments", "drivers", "risks", "watch", "source_note", "name"):
            if profile.get(key) and not enriched.get(key):
                enriched[key] = profile[key]
        enriched["symbol"] = code
        return enriched

    def _data_basis_value(self, data_sources: Dict) -> str:
        collection = data_sources.get("collection") if data_sources else None
        if collection and collection.get("success"):
            return "已采集"
        if collection:
            return "接口缺失"
        return data_sources.get("status", "待检查")

    def _data_basis_note(self, data_sources: Dict) -> str:
        collection = data_sources.get("collection") if data_sources else None
        if collection and collection.get("success"):
            names = [item.get("name") for item in collection.get("sources", []) if item.get("status") == "已调用"]
            return "、".join(names) if names else "自动数据源"
        if collection:
            return "报告仅展示外部输入和分析框架"
        return data_sources.get("summary", "数据源状态未检查")

    def _field_coverage_text(self, health: Dict) -> str:
        dimensions = health.get("dimensions") or {}
        available = sum(1 for item in dimensions.values() if item.get("status") != "unavailable")
        total = len(dimensions) or 5
        return f"{available}/{total}项"

    def _financial_metric_text(self, health: Dict) -> str:
        if health.get("health_score") is None:
            return "资料不足"
        dimensions = health.get("dimensions") or {}
        strong = sum(1 for item in dimensions.values() if item.get("score") is not None and item.get("score") >= 75)
        weak = sum(1 for item in dimensions.values() if item.get("score") is not None and item.get("score") < 60)
        if weak:
            return "需审慎"
        if strong >= 2:
            return "相对稳健"
        return "中性"

    def _risk_metric_note(self, alerts: Dict) -> str:
        count = alerts.get("alert_count", len(alerts.get("alerts", [])))
        return "暂无突出事项" if not count else f"{count}项关注点"

    def _price_text(self, valuation: Dict) -> str:
        price = valuation.get("current_price")
        return "暂无数据" if price is None else f"{float(price):.2f}"

    def _score_text(self, score) -> str:
        return "未验证" if score is None else f"{score}/100"

    def _percent_text(self, value) -> str:
        if value is None:
            return "未验证"
        try:
            return f"{float(value):.0%}"
        except (TypeError, ValueError):
            return "未验证"

    def _valuation_range_text(self, valuation_range: Dict) -> str:
        low = valuation_range.get("low")
        high = valuation_range.get("high")
        if low is None or high is None:
            return "暂无区间"
        if abs(float(high) - float(low)) < 0.01:
            return f"{float(low):.2f}"
        return f"{float(low):.2f}-{float(high):.2f}"

    def _valuation_metric_text(self, valuation: Dict) -> str:
        value_range = valuation.get("valuation_range", {})
        if self._is_single_point_valuation(value_range):
            return "待补充"
        return self._valuation_range_text(value_range)

    def _valuation_metric_note(self, valuation: Dict) -> str:
        value_range = valuation.get("valuation_range", {})
        if self._is_single_point_valuation(value_range):
            price = valuation.get("current_price")
            price_text = "暂无当前价" if price is None else f"当前价{float(price):.2f}"
            return f"{price_text}，缺EPS/FCF/可比倍数"
        if self._valuation_range_text(value_range) == "暂无区间":
            return "缺少估值输入"
        return "谨慎至乐观情景"

    def _is_single_point_valuation(self, valuation_range: Dict) -> bool:
        low = valuation_range.get("low")
        high = valuation_range.get("high")
        if low is None or high is None:
            return False
        return abs(float(high) - float(low)) < 0.01

    def _valuation_position_text(self, current_price, valuation_range: Dict) -> str:
        if current_price is None:
            return "估值端缺少当前价格，暂不能判断价格位置"
        if self._is_single_point_valuation(valuation_range):
            return f"目前只确认到市场价格约{float(current_price):.2f}，还没有形成可验证估值区间"
        low = valuation_range.get("low")
        high = valuation_range.get("high")
        if low is None or high is None:
            return f"当前价格为{float(current_price):.2f}，但估值区间尚未形成"
        price = float(current_price)
        low_value = float(low)
        high_value = float(high)
        if price < low_value:
            return "当前价格低于谨慎情景，需要确认市场是否已经过度折价"
        if price > high_value:
            return "当前价格高于乐观情景，风险回报对业绩兑现要求更高"
        return "当前价格位于情景估值带内，需要通过财务和技术面确认风险回报是否合适"

    def _company_angle(self, fundamental: Dict) -> str:
        drivers = fundamental.get("drivers") or []
        risks = fundamental.get("risks") or []
        if drivers:
            driver_text = "、".join(str(item) for item in drivers[:3])
            risk_text = "、".join(str(item) for item in risks[:2]) if risks else "订单、利润率和现金流变化"
            return f"这家公司的分析重点应放在{driver_text}。主要反向验证点是{risk_text}。"
        text = f"{fundamental.get('business_summary', '')} {fundamental.get('industry', '')} {fundamental.get('moat', '')}"
        points = []
        if "新能源" in text or "热管理" in text or "汽车" in text:
            points.append("汽车热管理相关业务的关键不只是收入增速，还包括客户结构、单车价值量和毛利率能否稳定。")
        if "机器人" in text or "执行器" in text:
            points.append("机器人或执行器线索更偏中长期期权，短期不能只按题材定价，需要看到订单、产品验证和利润贡献。")
        if "制冷" in text or "空调" in text:
            points.append("传统制冷空调零部件业务提供基本盘，重点看行业周期、海外需求和成本传导能力。")
        if "规模" in text or "制造" in text:
            points.append("规模制造优势只有在毛利率和现金流同时稳定时才算真正兑现。")
        if not points:
            return "公司特定分析应围绕业务结构、客户质量、利润率和现金流展开。"
        return "".join(points)

    def _action_table(self, health: Dict, valuation: Dict, alerts: Dict, technical: Dict, fundamental: Dict) -> str:
        rows = [
            self._business_action_row(fundamental),
            self._financial_action_row(health),
            self._technical_action_row(technical),
            self._valuation_action_row(valuation),
            self._risk_action_row(alerts),
        ]
        html_rows = "".join(
            "<tr>"
            f"<td>{html.escape(row[0])}</td>"
            f"<td>{html.escape(row[1])}</td>"
            f"<td>{html.escape(row[2])}</td>"
            f"<td>{html.escape(row[3])}</td>"
            "</tr>"
            for row in rows
        )
        return (
            '<div class="figure">'
            '<h3>关键数字与触发条件</h3>'
            '<table><thead><tr><th>分析线索</th><th>当前读数</th><th>可以说明什么</th><th>下一次复盘触发条件</th></tr></thead><tbody>'
            + html_rows
            + '</tbody></table>'
            '<div class="caption">该表把结论落到可观察指标上；触发条件用于复盘，不构成交易指令。</div>'
            '</div>'
        )

    def _business_map_block(self, fundamental: Dict) -> str:
        segments = fundamental.get("segments") or []
        drivers = fundamental.get("drivers") or []
        risks = fundamental.get("risks") or []
        watch = fundamental.get("watch") or []
        source_note = fundamental.get("source_note")
        if not any([segments, drivers, risks, watch]):
            return ""

        def list_items(items: list) -> str:
            if not items:
                return "<li>暂无明确条目，需补充公司公告和财报。</li>"
            return "".join(f"<li>{html.escape(str(item))}</li>" for item in items[:5])

        source_html = f'<p class="small">{html.escape(str(source_note))}</p>' if source_note else ""
        return (
            '<div class="figure">'
            '<h3>业务画像：读报告前先看懂这家公司靠什么赚钱</h3>'
            '<div class="grid">'
            '<div class="panel"><h3>业务板块</h3><ul>' + list_items(segments) + '</ul></div>'
            '<div class="panel"><h3>增长驱动</h3><ul>' + list_items(drivers) + '</ul></div>'
            '<div class="panel"><h3>反向风险</h3><ul>' + list_items(risks) + '</ul></div>'
            '<div class="panel"><h3>复盘抓手</h3><ul>' + list_items(watch) + '</ul></div>'
            '</div>'
            + source_html +
            '</div>'
        )

    def _business_action_row(self, fundamental: Dict) -> tuple[str, str, str, str]:
        segments = fundamental.get("segments") or []
        drivers = fundamental.get("drivers") or []
        watch = fundamental.get("watch") or []
        if segments:
            reading = " / ".join(str(item) for item in segments[:3])
            meaning = "利润弹性主要取决于哪些业务放量、哪些业务守住毛利率，而不是只看股票题材。"
            trigger = "；".join(str(item) for item in watch[:3]) or "复盘分产品收入、客户结构和区域结构"
        elif drivers:
            reading = "、".join(str(item) for item in drivers[:3])
            meaning = "这些驱动决定公司未来收入和利润弹性。"
            trigger = "复盘驱动因素是否兑现到收入、毛利率和现金流。"
        else:
            reading = "业务结构需要继续拆分"
            meaning = "当前只知道行业口径，尚不能判断利润弹性来自哪里"
            trigger = "补充分产品收入、客户结构和区域结构"
        return ("业务主线", reading, meaning, trigger)

    def _financial_action_row(self, health: Dict) -> tuple[str, str, str, str]:
        dimensions = health.get("dimensions") or {}
        profitability = self._dimension_reason(dimensions, "盈利能力")
        cashflow = self._dimension_reason(dimensions, "现金流质量")
        growth = self._dimension_reason(dimensions, "成长质量")
        reading_parts = [item for item in (profitability, cashflow, growth) if item]
        reading = "；".join(reading_parts[:3]) or self._financial_metric_text(health)
        if "经营现金流/净利润" in reading or "现金流" in reading:
            meaning = "利润质量有现金流支撑，财务侧不是单纯纸面增长"
        else:
            meaning = "财务结论仍需要现金流和营运资本交叉验证"
        trigger = "若经营现金流/净利润跌破1，或利润增速持续低于收入增速，应重新评估增长质量"
        return ("财务质量", reading, meaning, trigger)

    def _technical_action_row(self, technical: Dict) -> tuple[str, str, str, str]:
        support = self._price_or_missing(technical.get("support_level"))
        resistance = self._price_or_missing(technical.get("resistance_level"))
        rsi = technical.get("rsi14")
        change = technical.get("change_20d")
        volume = technical.get("volume_status", "量能待观察")
        volume_price = technical.get("volume_price_signal")
        pattern = self._pattern_name_text(technical.get("dominant_pattern", {}))
        rsi_text = "暂无RSI"
        if rsi is not None:
            rsi_text = f"RSI {float(rsi):.1f}"
        change_text = "区间涨跌待观察" if change is None else f"20日涨跌{float(change):.1%}"
        reading = f"支撑{support}，压力{resistance}，{change_text}，{rsi_text}，{volume}"
        if volume_price:
            reading += f"，{volume_price}"
        if pattern != "暂无数据":
            reading += f"，{pattern}"
        if rsi is not None and float(rsi) >= 70:
            meaning = "短线已经偏热，靠近压力位时继续上行对量能要求更高"
        else:
            meaning = "技术面主要用于观察价格是否仍守住趋势结构"
        trigger = f"收盘跌破{support}说明趋势结构转弱；放量站上{resistance}才说明压力位被有效消化"
        return ("价格位置", reading, meaning, trigger)

    def _valuation_action_row(self, valuation: Dict) -> tuple[str, str, str, str]:
        price = valuation.get("current_price")
        range_text = self._valuation_range_text(valuation.get("valuation_range", {}))
        if self._is_single_point_valuation(valuation.get("valuation_range", {})):
            reading = f"仅有当前价{self._price_or_missing(price)}，缺少完整估值输入"
            meaning = "现在不能判断便宜或昂贵，只能把价格与业务兑现、财务质量和技术位置放在一起观察"
            trigger = "补充可比公司市盈率、市净率、EPS、自由现金流或分业务估值后再形成估值带"
        else:
            reading = f"当前价格{self._price_or_missing(price)}，估值区间{range_text}"
            meaning = self._valuation_position_text(price, valuation.get("valuation_range", {}))
            trigger = "当价格离开估值区间或核心假设变化时，重新计算情景估值"
        return ("估值约束", reading, meaning, trigger)

    def _risk_action_row(self, alerts: Dict) -> tuple[str, str, str, str]:
        severity = alerts.get("highest_severity_cn", "提示")
        count = alerts.get("alert_count", len(alerts.get("alerts", [])))
        reading = f"风险级别{severity}，保留{count}项可见风险提示"
        if count:
            meaning = "风险项会影响估值置信度，不能只看技术面强弱"
            trigger = "若新增监管、订单、客户集中度或财报异常，应优先复核风险假设"
        else:
            meaning = "当前没有突出风险项，但仍需要跟踪公告和财报变化"
            trigger = "出现公告、财报或行业价格异常时重新生成报告"
        return ("风险约束", reading, meaning, trigger)

    def _dimension_reason(self, dimensions: Dict, name: str) -> str:
        for item in dimensions.values():
            if item.get("name") == name and item.get("reason"):
                return str(item.get("reason"))
        return ""

    def _source_status_text(self, data_sources: Dict) -> str:
        if not data_sources:
            return "数据源状态未检查"
        return data_sources.get("summary", data_sources.get("status", "数据源状态未检查"))

    def _integrated_view(self, health: Dict, valuation: Dict, alerts: Dict, technical: Dict, fundamental: Dict) -> str:
        financial = self._financial_metric_text(health)
        price = valuation.get("current_price")
        severity = alerts.get("highest_severity_cn", "提示")
        business_name = fundamental.get("name") or "公司"
        drivers = fundamental.get("drivers") or []
        driver = str(drivers[0]) if drivers else "核心业务能否持续放量"
        support = self._price_or_missing(technical.get("support_level"))
        resistance = self._price_or_missing(technical.get("resistance_level"))
        valuation_judgement = self._valuation_position_text(price, valuation.get("valuation_range", {}))
        return (
            f"{business_name}当前更适合按“业务兑现度”而不是按单一价格信号来跟踪。"
            f"核心问题是{driver}能否转化为收入、毛利率和经营现金流；当前财务侧呈现{financial}，"
            f"价格侧{valuation_judgement}，风险提示级别为{severity}。"
            f"技术上可把{support}视为短线强弱观察位、{resistance}视为压力验证位；"
            "只有业务数据、现金流和价格突破三者相互印证，结论才应从“观察”上调。"
        )

    def _key_evidence(self, health: Dict, valuation: Dict, data_sources: Dict, technical: Dict, fundamental: Dict) -> str:
        financial = self._financial_metric_text(health)
        segments = fundamental.get("segments") or []
        business = "、".join(str(item) for item in segments[:3]) if segments else "主营业务结构"
        support = self._price_or_missing(technical.get("support_level"))
        resistance = self._price_or_missing(technical.get("resistance_level"))
        rsi = technical.get("rsi14")
        rsi_text = "暂无RSI" if rsi is None else f"RSI {float(rsi):.1f}"
        if self._is_single_point_valuation(valuation.get("valuation_range", {})):
            return (
                f"当前依据分三层：第一，业务层看{business}，它决定收入弹性来自哪里；"
                f"第二，财务层观察为{financial}，重点看利润是否有现金流支撑；"
                f"第三，价格层看支撑{support}、压力{resistance}和{rsi_text}。"
                "估值模型还缺EPS、自由现金流或可比倍数，因此不能把当前价包装成目标价。"
            )
        range_text = self._valuation_range_text(valuation.get("valuation_range", {}))
        return f"当前核心依据来自财务表现、情景估值和风险提示。财务观察为{financial}，估值区间为{range_text}，主要风险见后文。"

    def _risk_summary(self, alerts: Dict, data_sources: Dict) -> str:
        severity = alerts.get("highest_severity_cn", "提示")
        count = alerts.get("alert_count", len(alerts.get("alerts", [])))
        if count:
            return f"当前最高风险提示级别为{severity}，主要关注财报、估值假设、监管事项和行情波动。"
        return f"当前最高风险提示级别为{severity}，暂未形成突出风险事项。"

    def _decision_note(self, health: Dict, valuation: Dict, alerts: Dict, technical: Dict, fundamental: Dict) -> str:
        if health.get("health_score") is None or not valuation.get("valuation_range"):
            return "结论应保持审慎：关键财务或估值数据不足时，只能给出方向性观察，不应形成确定性判断。"
        if self._is_single_point_valuation(valuation.get("valuation_range", {})):
            watches = fundamental.get("watch") or []
            watch_text = "；".join(str(item) for item in watches[:3]) or "分业务收入、现金流和支撑位变化"
            return f"这份报告当前不能回答“目标价是多少”，但可以回答“接下来该盯什么”：{watch_text}。这些观察项比单日涨跌更能决定投资逻辑是否成立。"
        return "当前结论应围绕盈利质量、估值位置和主要风险三条线交叉确认；若后续财报或价格显著偏离，应重新评估。"

    def _investment_logic(self, fundamental: Dict, health: Dict, valuation: Dict) -> str:
        business = fundamental.get("business_summary") or "公司业务、订单、客户结构和行业景气度需要结合最新公告进一步判断。"
        angle = self._company_angle(fundamental)
        financial = self._financial_metric_text(health)
        valuation_position = self._valuation_position_text(valuation.get("current_price"), valuation.get("valuation_range", {}))
        watch = "；".join(str(item) for item in (fundamental.get("watch") or [])[:3])
        watch_sentence = f"后续最关键的验证项是：{watch}。" if watch else ""
        return (
            f"{business} {angle}"
            "投资逻辑应拆成三步：先判断业务增量来自哪里，再确认利润率和经营现金流是否同步，最后才看当前价格是否给出足够风险补偿。"
            f"目前财务侧为{financial}；{valuation_position}。{watch_sentence}"
        )

    def _fundamental_text(self, fundamental: Dict, health: Dict) -> str:
        industry = fundamental.get("industry") or "行业信息需结合最新公告确认"
        moat = str(fundamental.get("moat") or "竞争优势需要结合客户结构、产品价格和毛利率变化判断").rstrip("。")
        drivers = "、".join(str(item) for item in (fundamental.get("drivers") or [])[:3])
        driver_text = f"主要驱动：{drivers}。" if drivers else ""
        return f"行业口径：{industry}。核心关注点：{moat}。{driver_text}"

    def _company_context(self, fundamental: Dict, data_sources: Dict) -> str:
        industry = fundamental.get("industry") or "行业信息需结合最新公告确认"
        business = fundamental.get("business_summary") or "主营业务、收入结构和区域结构需要结合最新年报或季报判断。"
        angle = self._company_angle(fundamental)
        return (
            f"公司分析先以业务口径为起点：{business} 行业口径当前记录为{industry}。"
            f"{angle}"
            "对投资者而言，更重要的是分产品收入、主要客户、订单变化和产能利用率是否能解释未来利润弹性。"
            "只有当收入增长、利润率变化和现金流表现能够互相印证时，经营改善才具有较强含金量。"
        )

    def _assumption_text(self, valuation: Dict, health: Dict) -> str:
        value_range = self._valuation_range_text(valuation.get("valuation_range", {}))
        if self._is_single_point_valuation(valuation.get("valuation_range", {})):
            return (
                "当前估值模块只拿到了市场价格，尚未拿到足够的每股收益、自由现金流、可比公司倍数或分业务估值输入。"
                "正式投研需要继续补充可比公司倍数、每股收益、自由现金流或股本口径。"
                "在估值输入不足时，报告只能说明“当前价格处在什么技术位置”，不能说明“公司合理价值是多少”。"
            )
        return (
            f"估值区间为{value_range}，其含义是不同盈利、倍数和折现假设下的可能价格带。"
            "投资者应重点关注两个问题：一是利润增长能否兑现，二是市场愿意给予的估值倍数是否能维持。"
            "如果后续财报显示毛利率、现金流或订单景气明显变化，估值区间也应随之调整。"
        )

    def _financial_text(self, health: Dict) -> str:
        if health.get("health_score") is None:
            return "当前财务信息不足，尚不能对盈利能力、现金流和资产负债结构形成完整判断。"
        dimensions = health.get("dimensions") or {}
        strong = [
            item.get("name")
            for item in dimensions.values()
            if item.get("score") is not None and item.get("score") >= 75
        ]
        weak = [
            item.get("name")
            for item in dimensions.values()
            if item.get("score") is not None and item.get("score") < 60
        ]
        strong_text = "、".join(str(item) for item in strong[:3]) or "没有形成突出的单项优势"
        if weak:
            weak_text = "、".join(str(item) for item in weak[:3])
            return f"已覆盖的财务信息显示，较强项包括{strong_text}；短板集中在{weak_text}。这意味着分析重点应放在短板是否会侵蚀利润兑现，而不是只看收入增长。"
        return f"已覆盖的财务信息显示，较强项包括{strong_text}，暂未出现明显短板。更重要的是观察利润率、经营现金流和营运资本能否继续同步改善，因为这决定增长是否有质量。"

    def _technical_text(self, technical: Dict) -> str:
        if not technical:
            return "当前没有足够行情序列，因此不输出日线、周线或月线形态判断。投资者可重点观察股价是否重新站上主要均线，以及成交量能否配合。"
        timeframe = technical.get("timeframe", "日线")
        trend = technical.get("trend", "趋势待验证")
        support = self._price_or_missing(technical.get("support_level"))
        resistance = self._price_or_missing(technical.get("resistance_level"))
        indicator_text = self._technical_indicator_text(technical)
        pattern_text = self._pattern_text(technical.get("dominant_pattern", {}))
        position_text = self._technical_position_text(technical)
        return (
            f"技术面按{timeframe}观察，当前趋势描述为{trend}，最近观察窗口内的支撑位约为{support}，压力位约为{resistance}。"
            f"{position_text}{pattern_text}{indicator_text}这些信号用于判断价格所处位置和风险回报，不单独构成投资结论。"
        )

    def _price_figure_block(self, technical: Dict) -> str:
        if not technical or technical.get("change_20d") is None:
            return (
                '<div class="figure">'
                '<p>价格图暂不展示：当前没有足够真实 K 线数据。报告不会用示意图、随机走势或财务分项图替代价格走势。</p>'
                '<div class="caption">价格走势需结合真实日线或周线数据观察。</div>'
                '</div>'
            )
        change = float(technical.get("change_20d"))
        ma5 = technical.get("ma5")
        ma20 = technical.get("ma20")
        rows = (
            f"<tr><td>观察窗口</td><td>{html.escape(str(technical.get('lookback', '最近20个交易日')))}</td></tr>"
            f"<tr><td>区间涨跌幅</td><td>{change:.1%}</td></tr>"
            f"<tr><td>五日均线</td><td>{'暂无数据' if ma5 is None else f'{float(ma5):.2f}'}</td></tr>"
            f"<tr><td>二十日均线</td><td>{'暂无数据' if ma20 is None else f'{float(ma20):.2f}'}</td></tr>"
            f"<tr><td>支撑位</td><td>{self._price_or_missing(technical.get('support_level'))}</td></tr>"
            f"<tr><td>压力位</td><td>{self._price_or_missing(technical.get('resistance_level'))}</td></tr>"
            f"<tr><td>支撑可信度</td><td>{html.escape(self._level_strength_text(technical, 'support'))}</td></tr>"
            f"<tr><td>压力可信度</td><td>{html.escape(self._level_strength_text(technical, 'resistance'))}</td></tr>"
            f"<tr><td>量价关系</td><td>{html.escape(str(technical.get('volume_price_signal', '暂无数据')))}</td></tr>"
            f"<tr><td>主形态</td><td>{html.escape(self._pattern_name_text(technical.get('dominant_pattern', {})))}</td></tr>"
            f"<tr><td>成交量状态</td><td>{html.escape(str(technical.get('volume_status', '暂无数据')))}</td></tr>"
            f"<tr><td>RSI 14</td><td>{self._number_or_missing(technical.get('rsi14'))}</td></tr>"
            f"<tr><td>MACD</td><td>{html.escape(self._macd_text(technical.get('macd', {})))}</td></tr>"
            f"<tr><td>布林带位置</td><td>{html.escape(self._bollinger_text(technical.get('bollinger', {})))}</td></tr>"
            f"<tr><td>ATR 14</td><td>{self._atr_text(technical)}</td></tr>"
        )
        return (
            '<div class="figure">'
            + self._candlestick_svg(technical.get("candles", []), technical)
            + '<table><thead><tr><th>价格字段</th><th>数值</th></tr></thead><tbody>'
            + rows
            + '</tbody></table><div class="caption">图 1. 基于真实K线数据生成的价格摘要，支撑位和压力位按最近20个交易日高低点、枢轴点和触达次数综合计算。</div></div>'
        )

    def _price_or_missing(self, value) -> str:
        if value is None:
            return "暂无数据"
        return f"{float(value):.2f}"

    def _multi_timeframe_block(self, technical: Dict) -> str:
        frames = technical.get("multi_timeframe") if technical else None
        if not frames:
            return ""
        ordered = [item for item in ("日线", "周线", "月线") if item in frames]
        if not ordered:
            return ""
        rows = []
        skipped = []
        for label in ordered:
            item = frames.get(label) or {}
            has_core_values = item.get("support_level") is not None or item.get("resistance_level") is not None or item.get("change") is not None
            if "样本不足" in str(item.get("trend", "")) and not has_core_values:
                skipped.append(label)
                continue
            change = item.get("change")
            change_text = "暂无数据" if change is None else f"{float(change):.1%}"
            rows.append(
                "<tr>"
                f"<td>{html.escape(label)}</td>"
                f"<td>{html.escape(str(item.get('trend') or '趋势待验证'))}</td>"
                f"<td>{html.escape(str(item.get('lookback') or '暂无数据'))}</td>"
                f"<td>{change_text}</td>"
                f"<td>{self._price_or_missing(item.get('support_level'))}</td>"
                f"<td>{self._price_or_missing(item.get('resistance_level'))}</td>"
                f"<td>{self._number_or_missing(item.get('rsi14'))}</td>"
                f"<td>{html.escape(str(item.get('macd_status') or '暂无数据'))}</td>"
                "</tr>"
            )
        if not rows:
            return (
                '<div class="figure">'
                '<h3>多周期共振</h3>'
                '<p>当前仅日线样本达到可分析要求，周线和月线样本不足，暂不输出多周期强结论。</p>'
                '<div class="caption">多周期分析需要更长历史区间；样本不足时不使用空表格补位。</div>'
                '</div>'
            )
        conclusion = self._multi_timeframe_text(frames)
        skipped_text = ""
        if skipped:
            skipped_text = f'<p class="small">{"、".join(skipped)}样本不足，暂不展示空值表格。</p>'
        return (
            '<div class="figure">'
            '<h3>多周期共振</h3>'
            f'<p>{html.escape(conclusion)}</p>'
            '<table><thead><tr><th>周期</th><th>趋势</th><th>观察窗口</th><th>区间涨跌</th><th>支撑位</th><th>压力位</th><th>RSI 14</th><th>MACD</th></tr></thead><tbody>'
            + "".join(rows)
            + "</tbody></table>"
            + skipped_text
            + '<div class="caption">多周期表由真实日线数据重采样生成。周线和月线样本不足时，只用于方向观察，不输出强结论。</div>'
            + "</div>"
        )

    def _multi_timeframe_text(self, frames: Dict) -> str:
        daily = frames.get("日线", {})
        weekly = frames.get("周线", {})
        monthly = frames.get("月线", {})
        trends = [str(item.get("trend", "")) for item in (daily, weekly, monthly)]
        strong_count = sum("偏强" in item for item in trends)
        weak_count = sum("偏弱" in item for item in trends)
        hot = daily.get("rsi14") is not None and float(daily.get("rsi14")) >= 70
        if strong_count >= 2 and not hot:
            return "短中期趋势存在一定共振，若估值和基本面同时支持，技术面可作为继续跟踪的辅助依据。"
        if strong_count >= 2 and hot:
            return "短中期趋势偏强，但日线动量已经偏热，更适合等待回撤或量价重新确认。"
        if weak_count >= 2:
            return "多个周期偏弱，技术面尚未形成有利位置，优先观察止跌和重新站上均线的证据。"
        return "多周期信号尚未形成清晰共振，应结合估值位置和基本面变化继续观察。"

    def _technical_playbook_block(self, technical: Dict) -> str:
        if not technical:
            return ""
        support = self._price_or_missing(technical.get("support_level"))
        resistance = self._price_or_missing(technical.get("resistance_level"))
        current = self._price_or_missing(technical.get("current_price"))
        trend = str(technical.get("trend") or "趋势待观察")
        rsi = technical.get("rsi14")
        rsi_text = "动量暂无足够数据"
        if rsi is not None:
            rsi_value = float(rsi)
            if rsi_value >= 70:
                rsi_text = f"RSI为{rsi_value:.1f}，短线偏热，追高容错率较低"
            elif rsi_value <= 30:
                rsi_text = f"RSI为{rsi_value:.1f}，短线偏冷，需观察是否止跌"
            else:
                rsi_text = f"RSI为{rsi_value:.1f}，动量处于中性区间"
        volume_price = str(technical.get("volume_price_signal") or "量价关系暂无足够数据")
        pattern = self._pattern_name_text(technical.get("dominant_pattern", {}))
        timeframe_note = self._timeframe_plain_guide(technical.get("multi_timeframe") or {})
        rows = [
            (
                f"放量站上{resistance}",
                "说明前期抛压被资金承接，趋势延续的概率上升。",
                "观察收盘价是否连续站稳压力位上方，成交量是否高于20日均量；若只是盘中冲高回落，不视为有效突破。",
            ),
            (
                f"回踩{support}附近但未跌破",
                "说明资金仍愿意在关键位置承接，适合把它当作强弱分界线复盘。",
                "观察缩量回踩后能否重新收回五日均线；若量能放大但价格不再下破，说明承接质量较好。",
            ),
            (
                f"收盘跌破{support}",
                "说明原有趋势结构被破坏，短线应先降低乐观假设。",
                "优先等待重新站回支撑位或形成新的低点抬高结构；若同时出现放量下跌，风险级别应上调。",
            ),
            (
                f"继续在{support}至{resistance}之间震荡",
                "说明市场暂时没有形成新方向，技术面更多是位置管理，而不是趋势判断。",
                "重点比较每次反弹量能和回落幅度；若高点抬高、低点抬高，震荡可能向上演化，反之则防守优先。",
            ),
        ]
        html_rows = "".join(
            "<tr>"
            f"<td>{html.escape(row[0])}</td>"
            f"<td>{html.escape(row[1])}</td>"
            f"<td>{html.escape(row[2])}</td>"
            "</tr>"
            for row in rows
        )
        summary = (
            f"当前价格约{current}，{trend}；{rsi_text}，量价关系为{volume_price}，主形态为{pattern}。"
            f"{timeframe_note}下面的应对框架用于复盘行情，不构成买卖建议。"
        )
        return (
            '<div class="figure">'
            '<h3>行情应对框架</h3>'
            f'<p>{html.escape(summary)}</p>'
            '<table><thead><tr><th>后续走势</th><th>含义</th><th>复盘动作</th></tr></thead><tbody>'
            + html_rows
            + '</tbody></table>'
            '<div class="caption">小白投资者可以先记住：压力位看能不能有效突破，支撑位看跌破后是否能快速收回，成交量决定突破和跌破的可信度。</div>'
            '</div>'
        )

    def _timeframe_plain_guide(self, frames: Dict) -> str:
        if not frames:
            return " 当前只有单一周期数据，主要用于短线位置判断。"
        daily = frames.get("日线", {})
        weekly = frames.get("周线", {})
        monthly = frames.get("月线", {})
        parts = []
        if daily:
            parts.append(f"日线用于判断接下来几天的进退位置，当前为{daily.get('trend', '趋势待观察')}")
        if weekly and "样本不足" not in str(weekly.get("trend", "")):
            parts.append(f"周线用于判断中短期方向，当前为{weekly.get('trend', '趋势待观察')}")
        if monthly and "样本不足" not in str(monthly.get("trend", "")):
            parts.append(f"月线用于判断大级别趋势，当前为{monthly.get('trend', '趋势待观察')}")
        if not parts:
            return " 当前主要依赖日线样本，周线和月线样本不足时不输出强结论。"
        return " " + "；".join(parts) + "。"

    def _number_or_missing(self, value, digits: int = 2) -> str:
        if value is None:
            return "暂无数据"
        return f"{float(value):.{digits}f}"

    def _technical_indicator_text(self, technical: Dict) -> str:
        parts = []
        rsi = technical.get("rsi14")
        if rsi is not None:
            rsi_value = float(rsi)
            if rsi_value >= 70:
                parts.append(f"RSI 14 为{rsi_value:.1f}，短线偏热")
            elif rsi_value <= 30:
                parts.append(f"RSI 14 为{rsi_value:.1f}，短线偏冷")
            else:
                parts.append(f"RSI 14 为{rsi_value:.1f}，处于中性区间")
        macd = technical.get("macd") or {}
        if macd.get("status"):
            parts.append(f"MACD处于{macd.get('status')}")
        bollinger = technical.get("bollinger") or {}
        if bollinger.get("position"):
            parts.append(f"价格位于布林带{bollinger.get('position')}")
        volume_status = technical.get("volume_status")
        if volume_status and volume_status != "成交量数据不足":
            parts.append(f"成交量表现为{volume_status}")
        if not parts:
            return ""
        return " 动量和波动率方面，" + "；".join(parts) + "。"

    def _technical_position_text(self, technical: Dict) -> str:
        parts = []
        support_distance = technical.get("support_distance_pct")
        resistance_distance = technical.get("resistance_distance_pct")
        if support_distance is not None:
            parts.append(f"距离支撑位约{float(support_distance):.1%}")
        if resistance_distance is not None:
            parts.append(f"距离压力位约{float(resistance_distance):.1%}")
        volume_price = technical.get("volume_price_signal")
        if volume_price:
            parts.append(f"量价关系为{volume_price}")
        if not parts:
            return ""
        return " 位置层面，" + "，".join(parts) + "。"

    def _pattern_text(self, pattern: Dict) -> str:
        if not pattern:
            return ""
        name = pattern.get("name")
        description = pattern.get("description")
        timeframe = pattern.get("timeframe")
        if not name or name in {"样本不足", "形态不明确"}:
            return ""
        prefix = f"{timeframe}主形态为{name}" if timeframe else f"主形态为{name}"
        if description:
            return f" {prefix}：{description}"
        return f" {prefix}。"

    def _pattern_name_text(self, pattern: Dict) -> str:
        if not pattern:
            return "暂无数据"
        name = str(pattern.get("name") or "暂无数据")
        timeframe = pattern.get("timeframe")
        confidence = pattern.get("confidence")
        details = [name]
        if timeframe:
            details.append(str(timeframe))
        if confidence:
            details.append(f"可信度{confidence}")
        return "，".join(details)

    def _level_strength_text(self, technical: Dict, side: str) -> str:
        if side == "support":
            level = technical.get("support_level")
            tests = technical.get("support_tests", 0)
            strength = technical.get("support_strength", "待确认")
            label = "支撑"
        else:
            level = technical.get("resistance_level")
            tests = technical.get("resistance_tests", 0)
            strength = technical.get("resistance_strength", "待确认")
            label = "压力"
        if level is None:
            return "暂无数据"
        return f"{label}{strength}，近20个交易日触达{int(tests or 0)}次"

    def _macd_text(self, macd: Dict) -> str:
        if not macd:
            return "暂无数据"
        status = macd.get("status", "暂无数据")
        dif = macd.get("dif")
        dea = macd.get("dea")
        if dif is None or dea is None:
            return str(status)
        return f"{status}，DIF {float(dif):.4f}，DEA {float(dea):.4f}"

    def _bollinger_text(self, bollinger: Dict) -> str:
        if not bollinger:
            return "暂无数据"
        position = bollinger.get("position", "暂无数据")
        upper = bollinger.get("upper")
        mid = bollinger.get("mid")
        lower = bollinger.get("lower")
        if upper is None or mid is None or lower is None:
            return str(position)
        return f"{position}，上轨 {float(upper):.2f}，中轨 {float(mid):.2f}，下轨 {float(lower):.2f}"

    def _atr_text(self, technical: Dict) -> str:
        atr = technical.get("atr14")
        if atr is None:
            return "暂无数据"
        pct = technical.get("atr14_pct")
        if pct is None:
            return f"{float(atr):.2f}"
        return f"{float(atr):.2f}（约为现价的{float(pct):.1%}）"

    def _candlestick_svg(self, candles: Iterable[Dict], technical: Dict) -> str:
        candles = list(candles or [])[-20:]
        if len(candles) < 5:
            return ""
        highs = [float(item["high"]) for item in candles]
        lows = [float(item["low"]) for item in candles]
        max_price = max(highs)
        min_price = min(lows)
        if max_price <= min_price:
            return ""
        price_padding = max((max_price - min_price) * 0.06, 0.01)
        max_price += price_padding
        min_price -= price_padding

        width, height = 900, 360
        left, right, top, bottom = 58, 24, 20, 34
        volume_top = 276
        price_bottom = 258
        plot_w = width - left - right
        plot_h = price_bottom - top

        def y(price: float) -> float:
            return top + (max_price - price) / (max_price - min_price) * plot_h

        candle_w = max(7, min(22, plot_w / len(candles) * 0.56))
        gap = plot_w / len(candles)
        elements = []
        grid_values = [min_price + (max_price - min_price) * step / 4 for step in range(5)]
        for value in grid_values:
            yy = y(value)
            elements.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#ddd9cc" stroke-width="1"/>')
            elements.append(f'<text x="8" y="{yy+4:.1f}" font-size="12" fill="#66645d">{value:.2f}</text>')

        ma5_points = self._ma_points(candles, "ma5", 5, y, left, gap)
        ma20_points = self._ma_points(candles, "ma20", 20, y, left, gap)
        if ma20_points:
            elements.append(f'<polyline points="{ma20_points}" fill="none" stroke="#8c6d1f" stroke-width="1.8" opacity="0.9"/>')
        if ma5_points:
            elements.append(f'<polyline points="{ma5_points}" fill="none" stroke="#2a6f97" stroke-width="1.8" opacity="0.9"/>')

        support = technical.get("support_level")
        resistance = technical.get("resistance_level")
        for label, value, color in (("支撑", support, "#2f6f4e"), ("压力", resistance, "#9b3d32")):
            if value is not None:
                yy = y(float(value))
                elements.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="{color}" stroke-width="1.5" stroke-dasharray="5 4"/>')
                elements.append(f'<text x="{width-right-52}" y="{yy-6:.1f}" font-size="12" fill="{color}">{label} {float(value):.2f}</text>')

        for idx, item in enumerate(candles):
            x = left + idx * gap + gap / 2
            open_price = float(item["open"])
            close_price = float(item["close"])
            high_price = float(item["high"])
            low_price = float(item["low"])
            color = "#b23b35" if close_price >= open_price else "#2f6f4e"
            y_open = y(open_price)
            y_close = y(close_price)
            y_high = y(high_price)
            y_low = y(low_price)
            rect_y = min(y_open, y_close)
            rect_h = max(2, abs(y_close - y_open))
            elements.append(f'<line x1="{x:.1f}" y1="{y_high:.1f}" x2="{x:.1f}" y2="{y_low:.1f}" stroke="{color}" stroke-width="1.4"/>')
            fill = "none" if close_price >= open_price else color
            elements.append(f'<rect x="{x-candle_w/2:.1f}" y="{rect_y:.1f}" width="{candle_w:.1f}" height="{rect_h:.1f}" fill="{fill}" stroke="{color}" stroke-width="1.4" opacity="0.95"/>')

        volumes = [float(item.get("volume") or 0) for item in candles]
        max_volume = max(volumes) if any(volumes) else 0
        if max_volume:
            volume_h = height - bottom - volume_top
            elements.append(f'<line x1="{left}" y1="{volume_top}" x2="{width-right}" y2="{volume_top}" stroke="#ddd9cc" stroke-width="1"/>')
            for idx, item in enumerate(candles):
                volume = float(item.get("volume") or 0)
                if not volume:
                    continue
                x = left + idx * gap + gap / 2
                open_price = float(item["open"])
                close_price = float(item["close"])
                color = "#b23b35" if close_price >= open_price else "#2f6f4e"
                bar_h = max(1, volume / max_volume * volume_h)
                elements.append(f'<rect x="{x-candle_w/2:.1f}" y="{height-bottom-bar_h:.1f}" width="{candle_w:.1f}" height="{bar_h:.1f}" fill="{color}" opacity="0.32"/>')

        first_date = html.escape(str(candles[0].get("date", "")))
        last_date = html.escape(str(candles[-1].get("date", "")))
        elements.append(f'<text x="{left}" y="{height-8}" font-size="12" fill="#66645d">{first_date}</text>')
        elements.append(f'<text x="{width-right-72}" y="{height-8}" font-size="12" fill="#66645d">{last_date}</text>')
        if ma5_points:
            elements.append(f'<text x="{width-right-164}" y="{height-8}" font-size="12" fill="#2a6f97">MA5</text>')
        if ma20_points:
            elements.append(f'<text x="{width-right-118}" y="{height-8}" font-size="12" fill="#8c6d1f">MA20</text>')
        elements.append(f'<text x="{left}" y="{volume_top-6}" font-size="12" fill="#66645d">价格</text>')
        if max_volume:
            elements.append(f'<text x="{left}" y="{volume_top+16}" font-size="12" fill="#66645d">成交量</text>')
        return '<div class="chart-wrap"><svg class="candle-chart" viewBox="0 0 900 360" role="img" aria-label="最近20个交易日日线K线图">' + "".join(elements) + "</svg></div>"

    def _ma_points(self, candles: list[Dict], field: str, window: int, y_func, left: float, gap: float) -> str:
        points = []
        for index, candle in enumerate(candles):
            average = candle.get(field)
            if average is None:
                continue
            x = left + index * gap + gap / 2
            points.append(f"{x:.1f},{y_func(float(average)):.1f}")
        if len(points) >= 2:
            return " ".join(points)

        closes = [float(item["close"]) for item in candles]
        if len(closes) < window:
            return ""
        fallback = []
        for index in range(window - 1, len(closes)):
            average = sum(closes[index - window + 1:index + 1]) / window
            x = left + index * gap + gap / 2
            fallback.append(f"{x:.1f},{y_func(average):.1f}")
        return " ".join(fallback) if len(fallback) >= 2 else ""

    def _dimension_table(self, dimensions: Dict) -> str:
        if not dimensions:
            return '<p>财务分项暂无可验证数据。正式报告应补充盈利能力、现金流质量、资产负债安全、营运资本质量和成长质量。</p>'
        rows = []
        for item in dimensions.values():
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('name', '分项')))}</td>"
                f"<td>{html.escape(self._dimension_status(item))}</td>"
                f"<td>{html.escape(str(item.get('reason', '暂无解释')))}</td>"
                "</tr>"
            )
        return "<table><thead><tr><th>指标</th><th>状态</th><th>解释</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

    def _dimension_status(self, item: Dict) -> str:
        if item.get("status") == "unavailable" or item.get("score") is None:
            return "字段缺失"
        score = item.get("score")
        if score >= 75:
            return "相对较强"
        if score >= 60:
            return "基本可用"
        return "需要复核"

    def _financial_followup(self, health: Dict) -> str:
        warnings = health.get("warnings") or health.get("risk_flags") or []
        if not warnings:
            return "财务复核重点是确认利润是否由现金流支撑，以及应收账款、存货是否与收入增长相匹配。"
        return "需要优先复核：" + "；".join(str(item) for item in warnings[:4])

    def _valuation_text(self, valuation: Dict) -> str:
        value_range = valuation.get("valuation_range", {})
        range_text = self._valuation_range_text(value_range)
        if range_text == "暂无区间":
            return "估值工作台缺少可验证输入，暂不形成区间。需要补充当前价格、每股收益、每股净资产、自由现金流、总股本、现金、负债和真实可比公司倍数。"
        if self._is_single_point_valuation(value_range):
            return (
                f"当前估值模块只确认到市场价格约{range_text}，这不是完整估值模型，也不是目标价。"
                "这种情况下更合理的用法是把当前价和技术位、财务质量放在一起判断风险回报。"
                "下一步应补充至少一种可复核估值口径，例如可比公司倍数、每股收益、自由现金流或分业务估值。"
            )
        return f"估值工作台给出的谨慎至乐观区间为{range_text}。该区间用于展示假设敏感性，不应被理解为单点价格判断。"

    def _scenario_table(self, scenarios: Iterable[Dict]) -> str:
        scenarios = list(scenarios or [])
        if not scenarios:
            return "<p>暂无情景估值表。</p>"
        values = [item.get("fair_value") for item in scenarios if item.get("fair_value") is not None]
        if values and max(float(item) for item in values) - min(float(item) for item in values) < 0.01:
            return "<p>当前估值输入只形成单点市场价格，暂不展示谨慎、基准、乐观三情景表，避免把同一价格包装成多个估值结论。</p>"
        rows = []
        for item in scenarios:
            fair_value = item.get("fair_value")
            upside = item.get("upside")
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('name', '情景')))}</td>"
                f"<td>{'暂无数据' if fair_value is None else f'{float(fair_value):.2f}'}</td>"
                f"<td>{'暂无数据' if upside is None else f'{float(upside):.1%}'}</td>"
                f"<td>{html.escape(self._confidence_cn(item.get('valuation_confidence')))}</td>"
                "</tr>"
            )
        return "<table><thead><tr><th>情景</th><th>公允价值</th><th>相对空间</th><th>置信度</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

    def _confidence_cn(self, value) -> str:
        mapping = {"low": "低", "medium": "中", "high": "高", "none": "需补充来源"}
        return mapping.get(str(value).lower(), str(value or "需补充来源"))

    def _alerts_block(self, alerts: Iterable[Dict]) -> str:
        alerts = list(alerts or [])
        if not alerts:
            return "<p>暂未识别出突出风险。仍需关注财报异常、价格波动、行业景气和监管事项。</p>"
        rows = []
        data_gap_count = sum(1 for item in alerts if self._is_data_gap_alert(item))
        if data_gap_count:
            rows.append(
                '<div class="risk-row">'
                "<strong>信息不足｜部分风险事项需要继续观察</strong>"
                f"<p>共有{data_gap_count}项风险检查缺少足够公开信息，当前不单独放大为具体风险。投资者应重点关注财报、监管公告和行业景气变化。</p>"
                "</div>"
            )
        visible_alerts = [item for item in alerts if not self._is_data_gap_alert(item)]
        for item in visible_alerts[:6]:
            verified = "已核验" if item.get("verified") else "需补充来源"
            rows.append(
                '<div class="risk-row">'
                f"<strong>{html.escape(str(item.get('severity_cn', '提示')))}｜{html.escape(self._clean_alert_text(str(item.get('title', '风险事项'))))}</strong>"
                f"<p>{html.escape(self._clean_alert_text(str(item.get('message', '暂无说明'))))}（{verified}）</p>"
                "</div>"
            )
        return "".join(rows)

    def _is_data_gap_alert(self, item: Dict) -> bool:
        text = f"{item.get('title', '')} {item.get('message', '')}"
        markers = ("未验证", "待验证", "不可验证", "字段缺失", "关键字段缺失", "不能给出确定性财报健康分")
        return (not item.get("verified")) and any(marker in text for marker in markers)

    def _clean_alert_text(self, text: str) -> str:
        replacements = {
            "财报健康分": "财务结论",
            "未验证": "数据不足",
            "待验证": "需补充来源",
            "不可验证": "缺少来源",
            "不能给出确定性": "暂不能形成",
        }
        result = text
        for source, target in replacements.items():
            result = result.replace(source, target)
        return result

    def _data_source_table(self, data_sources: Dict) -> str:
        items = data_sources.get("items", []) if data_sources else []
        if not items:
            return "<p>数据源状态未检查。建议先运行数据源体检，再生成正式报告。</p>"
        rows = []
        for item in items:
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('name', '数据源')))}</td>"
                f"<td>{html.escape(str(item.get('purpose', '用途待确认')))}</td>"
                f"<td>{html.escape(str(item.get('status', '待检查')))}</td>"
                f"<td>{html.escape(str(item.get('action', '暂无处理建议')))}</td>"
                "</tr>"
            )
        return "<table><thead><tr><th>来源</th><th>用途</th><th>状态</th><th>处理建议</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"

    def _collection_source_block(self, data_sources: Dict) -> str:
        collection = data_sources.get("collection") if data_sources else None
        if not collection:
            return ""
        sources = collection.get("sources", [])
        warnings = collection.get("warnings", [])
        rows = []
        for item in sources:
            fields = "、".join(item.get("fields", [])) if item.get("fields") else "暂无字段"
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(item.get('name', '采集源')))}</td>"
                f"<td>{html.escape(str(item.get('status', '待检查')))}</td>"
                f"<td>{html.escape(fields)}</td>"
                "</tr>"
            )
        warning_text = "；".join(self._clean_alert_text(str(item)) for item in warnings[:5]) if warnings else "暂无采集警告。"
        table = ""
        if rows:
            table = "<table><thead><tr><th>实际采集源</th><th>调用状态</th><th>已采集字段</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        return table + f'<p class="small">采集说明：{html.escape(warning_text)}</p>'

    def _verification_table(self, data_sources: Dict) -> str:
        missing = data_sources.get("critical_missing", []) if data_sources else []
        rows = [
            ("行情数据", "确认当前价格、成交量、复权口径和最近二十个交易日走势", "交易所行情或授权行情源"),
            ("财报数据", "确认收入、利润、现金流、资产负债率、应收账款和存货口径", "公司公告、年报、季报"),
            ("估值参数", "确认可比公司样本、市盈率、市净率、自由现金流和总股本", "同业公司公告和行情数据"),
            ("风险事件", "确认监管公告、诉讼、订单变化、客户集中度和行业价格变化", "交易所公告、公司公告、行业数据"),
        ]
        if missing:
            rows.append(("数据源修复", "优先处理：" + "、".join(missing), "本地依赖或外部数据服务"))
        html_rows = "".join(
            f"<tr><td>{html.escape(name)}</td><td>{html.escape(task)}</td><td>{html.escape(source)}</td></tr>"
            for name, task, source in rows
        )
        return "<table><thead><tr><th>验证项</th><th>需要确认的问题</th><th>建议来源</th></tr></thead><tbody>" + html_rows + "</tbody></table>"

    def _verification_note(self) -> str:
        return (
            "后续验证的顺序建议从数据完整性开始，而不是直接调整结论。先确认行情和财报字段，再确认估值样本，最后检查风险事件。"
            "如果任一关键来源不可用，报告结论应降级为数据不足，并保留原因说明；如果新数据改变利润率、现金流或估值倍数，应重新生成完整报告。"
        )

    def _closing_summary(self, health: Dict, valuation: Dict, alerts: Dict, data_sources: Dict) -> str:
        valuation_summary = self._valuation_position_text(valuation.get("current_price"), valuation.get("valuation_range", {}))
        if self._is_single_point_valuation(valuation.get("valuation_range", {})):
            valuation_summary += "，因此后续必须补充分业务估值、可比公司倍数或现金流假设后，才能讨论合理价值"
        return (
            "本报告的判断链条是：业务线索是否真实放量，财务质量是否承接增长，价格位置是否给出合适风险回报。"
            f"当前财务观察为{self._financial_metric_text(health)}；{valuation_summary}；"
            f"风险结论为{alerts.get('highest_severity_cn', '提示')}。"
            "下一次复盘应优先更新订单/收入结构、毛利率、经营现金流和有效支撑位。"
        )


    # ── P1 Enhancement Methods ────────────────────────────────

    def _enhanced_technical_block(self, enhanced: Dict, technical: Dict) -> str:
        """增强技术分析区块: VWAP/斐波那契/K线形态"""
        if not enhanced:
            return "<p>增强技术指标暂无数据。</p>"
        parts = []
        if enhanced.get("vwap"):
            vwap = enhanced["vwap"]
            parts.append(f'<div class="panel"><h3>VWAP 机构成本线</h3><p>VWAP: {self._num_text(vwap.get("vwap"))}｜偏离: {self._num_text(vwap.get("deviation_pct"), "%")}</p><p class="small">{html.escape(vwap.get("interpretation", ""))}</p></div>')
        if enhanced.get("fibonacci"):
            fib = enhanced["fibonacci"]
            levels = fib.get("levels", {})
            if levels:
                parts.append('<div class="panel"><h3>斐波那契关键位</h3><table><thead><tr><th>级别</th><th>价格</th><th>含义</th></tr></thead><tbody>')
                for name, price in sorted(levels.items(), key=lambda x: float(x[1]) if x[1] else 0, reverse=True):
                    parts.append(f'<tr><td>{html.escape(str(name))}</td><td>{self._num_text(price)}</td><td>{"阻力" if float(price or 0) > float(technical.get("close", 0) or 0) else "支撑"}</td></tr>')
                parts.append('</tbody></table></div>')
        if enhanced.get("patterns"):
            patterns = enhanced["patterns"]
            if patterns:
                parts.append('<div class="panel"><h3>K线形态识别</h3><table><thead><tr><th>形态</th><th>信号</th><th>可靠性</th></tr></thead><tbody>')
                for p in patterns[:5]:
                    parts.append(f'<tr><td>{html.escape(str(p.get("name", "")))}</td><td>{html.escape(str(p.get("signal", "")))}</td><td>{html.escape(str(p.get("reliability", "")))}</td></tr>')
                parts.append('</tbody></table></div>')
        if enhanced.get("support_resistance"):
            sr = enhanced["support_resistance"]
            parts.append(f'<div class="panel"><h3>支撑阻力聚合</h3><p>关键支撑: {self._num_text(sr.get("nearest_support"))}｜关键阻力: {self._num_text(sr.get("nearest_resistance"))}</p></div>')
        return "\n".join(parts) if parts else "<p>增强技术指标暂无数据。</p>"

    def _entry_signals_block(self, signals: Dict) -> str:
        """入场信号区块"""
        if not signals or not signals.get("signals"):
            return ""
        items = signals.get("signals", [])
        if not items:
            return ""
        rows = []
        for s in items[:5]:
            rows.append(f'<tr><td>{html.escape(str(s.get("name", "")))}</td><td>{html.escape(str(s.get("type", "")))}</td><td>{html.escape(str(s.get("strength", "")))}</td><td>{html.escape(str(s.get("action", "")))}</td></tr>')
        return f'<div class="panel"><h3>入场信号</h3><table><thead><tr><th>信号</th><th>类型</th><th>强度</th><th>建议</th></tr></thead><tbody>{"".join(rows)}</tbody></table><p class="small">综合评分: {html.escape(str(signals.get("overall_score", "N/A")))}</p></div>'

    def _risk_management_block(self, rm: Dict) -> str:
        """风控建议区块"""
        if not rm:
            return "<p>风控数据暂无。</p>"
        parts = []
        if rm.get("stop_loss"):
            sl = rm["stop_loss"]
            parts.append(f'<div class="panel"><h3>止损建议</h3><p>ATR 止损位: {self._num_text(sl.get("atr_stop"))}｜固定比例止损: {self._num_text(sl.get("pct_stop"))}</p></div>')
        if rm.get("position_sizing"):
            ps = rm["position_sizing"]
            parts.append(f'<div class="panel"><h3>仓位建议</h3><p>Kelly 比例: {self._num_text(ps.get("kelly_pct"), "%")}｜建议仓位: {self._num_text(ps.get("suggested_pct"), "%")}</p></div>')
        if rm.get("var"):
            var = rm["var"]
            parts.append(f'<div class="panel"><h3>风险度量</h3><p>VaR(95%): {self._num_text(var.get("var_95"), "%")}｜CVaR: {self._num_text(var.get("cvar"), "%")}｜最大回撤: {self._num_text(var.get("max_drawdown"), "%")}</p></div>')
        return "\n".join(parts) if parts else "<p>风控数据暂无。</p>"

    def _evidence_block(self, evidence: Dict) -> str:
        """数据溯源区块"""
        if not evidence or not evidence.get("items"):
            return "<p>数据溯源信息暂无。</p>"
        items = evidence.get("items", [])
        rows = []
        for e in items[:10]:
            grade = e.get("grade", "N/A")
            grade_class = "grade-a" if grade in ("A", "B") else "grade-c" if grade in ("D", "E") else "grade-b"
            rows.append(f'<tr><td>{html.escape(str(e.get("field", "")))}</td><td>{html.escape(str(e.get("source", "")))}</td><td class="{grade_class}">{html.escape(str(grade))}</td><td>{html.escape(str(e.get("note", "")))}</td></tr>')
        return f'<table><thead><tr><th>数据项</th><th>来源</th><th>评级</th><th>说明</th></tr></thead><tbody>{"".join(rows)}</tbody></table><p class="small">评级: A=实时验证 B=官方来源 C=第三方 D=估算 E=假设</p>'

    def _num_text(self, value, suffix: str = "") -> str:
        """格式化数字"""
        if value is None:
            return "N/A"
        try:
            v = float(value)
            if abs(v) >= 1e8:
                return f"{v/1e8:.2f}亿{suffix}"
            if abs(v) >= 1e4:
                return f"{v/1e4:.2f}万{suffix}"
            return f"{v:.2f}{suffix}"
        except (ValueError, TypeError):
            return str(value) if value else "N/A"


__all__ = ["KamiStyleStockReport"]
