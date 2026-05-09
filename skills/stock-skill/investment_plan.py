#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create investor-facing follow-up plans from watchlist monitoring results."""

from __future__ import annotations

from datetime import datetime, timedelta
import csv
import html
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from skills.shared import normalize_report_text


SEVERITY_DAYS = {"高": 1, "中": 3, "低": 7, "提示": 14}
SEVERITY_PRIORITY = {"高": "立即复核", "中": "重点跟踪", "低": "普通提醒", "提示": "常规观察"}


class InvestmentPlanBuilder:
    """Build a practical monitoring plan from triggered watchlist items."""

    def build(self, monitor_result: Dict, generated_at: Optional[datetime] = None) -> Dict:
        generated_at = generated_at or datetime.now()
        items = [self._plan_item(item, generated_at) for item in monitor_result.get("items", [])]
        return {
            "success": True,
            "generated_at": generated_at.isoformat(timespec="seconds"),
            "plan_size": len(items),
            "items": items,
            "summary": self._summary(items),
        }

    def generate_html(self, plan: Dict, output_path: str | None = None) -> str:
        rows = []
        for item in plan.get("items", []):
            rows.append(
                "<tr>"
                f"<td>{html.escape(item['display_name'])}</td>"
                f"<td>{html.escape(item['priority'])}</td>"
                f"<td>{html.escape(item['review_frequency'])}</td>"
                f"<td>{html.escape(item['next_review_date'])}</td>"
                f"<td>{html.escape(item['price_plan'])}</td>"
                f"<td>{html.escape(item['invalidation'])}</td>"
                f"<td>{html.escape(item['required_update'])}</td>"
                "</tr>"
            )
        html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>投资跟踪计划</title>
  <style>
    body {{ margin: 0; background: #f5f4ed; color: #171717; font-family: "PingFang SC", "Microsoft YaHei", serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 48px 64px; }}
    h1 {{ margin: 0 0 8px; font-size: 42px; }}
    .subtitle {{ color: #55534d; font-size: 16px; line-height: 1.7; margin-bottom: 24px; }}
    .summary {{ border-left: 5px solid #1b365d; background: rgba(255,255,255,.4); padding: 16px 20px; margin-bottom: 24px; line-height: 1.75; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd9cc; padding: 12px 10px; text-align: left; vertical-align: top; }}
    th {{ color: #1b365d; background: rgba(255,255,255,.42); }}
    .note {{ margin-top: 20px; color: #66645d; line-height: 1.75; font-size: 14px; }}
    @media (max-width: 760px) {{ main {{ padding: 28px 18px; }} h1 {{ font-size: 32px; }} table {{ font-size: 13px; }} }}
  </style>
</head>
<body>
  <main>
    <h1>投资跟踪计划</h1>
    <div class="subtitle">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}。本计划把监控触发条件转化为复核节奏、价格观察区和失效条件。</div>
    <div class="summary">{html.escape(plan.get('summary', '暂无计划摘要'))}</div>
    <table>
      <thead><tr><th>股票</th><th>优先级</th><th>复核频率</th><th>下次复核</th><th>价格计划</th><th>失效条件</th><th>需要更新</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="note">本计划用于管理研究流程，不构成投资建议。若价格、财报、公告或技术形态出现重大变化，应重新生成完整投研报告。</div>
  </main>
</body>
</html>"""
        html_text = normalize_report_text(html_text)
        if output_path:
            Path(output_path).write_text(html_text, encoding="utf-8")
        return html_text

    def write_csv(self, plan: Dict, output_path: str) -> None:
        fields = [
            "symbol",
            "display_name",
            "priority",
            "review_frequency",
            "next_review_date",
            "price_plan",
            "invalidation",
            "required_update",
            "trigger_reasons",
        ]
        with Path(output_path).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in plan.get("items", []):
                writer.writerow({key: item.get(key, "") for key in fields})

    def _plan_item(self, item: Dict, generated_at: datetime) -> Dict:
        severity = item.get("highest_severity", "提示")
        inputs = item.get("inputs", {}) or {}
        current_price = inputs.get("current_price") or item.get("current_price")
        fair_value = inputs.get("fair_value")
        days = SEVERITY_DAYS.get(severity, 14)
        next_review = generated_at + timedelta(days=days)
        trigger_reasons = "；".join(item.get("reasons", [])[:5]) or "暂无触发条件"
        return {
            "symbol": item.get("symbol", ""),
            "display_name": item.get("display_name", item.get("symbol", "")),
            "priority": SEVERITY_PRIORITY.get(severity, "常规观察"),
            "review_frequency": self._frequency(severity),
            "next_review_date": next_review.strftime("%Y-%m-%d"),
            "price_plan": self._price_plan(current_price, fair_value),
            "invalidation": self._invalidation(item),
            "required_update": self._required_update(item),
            "trigger_reasons": trigger_reasons,
        }

    def _frequency(self, severity: str) -> str:
        if severity == "高":
            return "每日复核，直到触发条件解除或完整报告更新"
        if severity == "中":
            return "每三日复核，并在价格或公告变化时提前更新"
        if severity == "低":
            return "每周复核，等待进一步确认"
        return "每两周复核"

    def _price_plan(self, current_price, fair_value) -> str:
        if current_price is None and fair_value is None:
            return "暂无真实价格或估值字段，先补充行情与估值数据"
        if current_price is not None and fair_value is not None and fair_value:
            gap = current_price / fair_value - 1
            if gap >= 0.15:
                return f"现价 {current_price:.2f} 高于估值中枢约 {gap:.0%}，优先等待估值回落或业绩上修"
            if gap <= -0.2:
                return f"现价 {current_price:.2f} 低于估值中枢约 {-gap:.0%}，进入重点复核区"
            return f"现价 {current_price:.2f} 接近估值中枢，重点看业绩和技术面确认"
        if current_price is not None:
            return f"现价 {current_price:.2f} 已记录，需补充估值中枢"
        return f"估值中枢 {fair_value:.2f} 已记录，需补充真实现价"

    def _invalidation(self, item: Dict) -> str:
        titles = item.get("reasons", [])
        if any("跌破" in title for title in titles):
            return "若价格不能快速收回关键位，原有观察逻辑需要降级"
        if any("动量过热" in title for title in titles):
            return "若放量滞涨或跌破短期均线，需降低短线乐观假设"
        if any("负债率" in title or "利润" in title for title in titles):
            return "若财务风险继续恶化，需重新评估基本面假设"
        return "若价格、财报或公告与原研究假设相反，需重新生成完整报告"

    def _required_update(self, item: Dict) -> str:
        titles = item.get("reasons", [])
        updates = ["最新行情"]
        if any("支撑" in title or "压力" in title or "动量" in title or "趋势" in title for title in titles):
            updates.append("技术面")
        if any("负债" in title or "利润" in title or "ROE" in title for title in titles):
            updates.append("财务字段")
        if any("估值" in title or "公允价值" in title for title in titles):
            updates.append("估值假设")
        return "、".join(dict.fromkeys(updates))

    def _summary(self, items: List[Dict]) -> str:
        urgent = sum(1 for item in items if item["priority"] == "立即复核")
        focus = sum(1 for item in items if item["priority"] == "重点跟踪")
        if urgent:
            return f"当前 {urgent} 只股票需要立即复核，{focus} 只需要重点跟踪。优先处理价格破位、财务风险和估值偏离。"
        if focus:
            return f"当前没有立即复核项，{focus} 只股票需要重点跟踪。"
        return "当前计划以常规观察为主，等待新的价格、财报或公告触发。"


def build_investment_plan(monitor_result: Dict) -> Dict:
    return InvestmentPlanBuilder().build(monitor_result)


__all__ = ["InvestmentPlanBuilder", "build_investment_plan"]
