#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Investor-facing stock opportunity shortlist pipeline."""

from __future__ import annotations

from datetime import datetime
import html
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from skills.shared import normalize_report_text, stock_display_name, translate_industry


def _num(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "N/A", "NA", "None", "nan", "暂无数据"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if text in {"", "--", "N/A", "NA", "None", "nan"}:
        return default
    return text


def _pandas_module():
    if find_spec("pandas") is None:
        return None
    import pandas as pd

    return pd


class OpportunityPipeline:
    """Turn a real candidate list into a ranked research shortlist."""

    COLUMN_ALIASES = {
        "symbol": {"symbol", "code", "股票代码", "代码", "证券代码"},
        "name": {"name", "股票名称", "名称", "简称"},
        "industry": {"industry", "行业", "所属行业"},
        "current_price": {"current_price", "price", "当前价格", "最新价", "收盘"},
        "fair_value": {"fair_value", "合理价值", "公允价值", "估值中枢"},
        "pe": {"pe", "PE", "市盈率"},
        "pb": {"pb", "PB", "市净率"},
        "roe": {"roe", "ROE", "净资产收益率"},
        "debt_ratio": {"debt_ratio", "资产负债率", "负债率"},
        "revenue_growth": {"revenue_growth", "收入增速", "营收增速"},
        "profit_growth": {"profit_growth", "利润增速", "净利润增速"},
        "gross_margin": {"gross_margin", "毛利率"},
        "net_margin": {"net_margin", "净利率"},
        "trend": {"trend", "趋势"},
        "rsi14": {"rsi14", "RSI", "RSI14"},
        "support_level": {"support_level", "支撑位"},
        "resistance_level": {"resistance_level", "压力位"},
    }

    def load_csv(self, path: str) -> List[Dict]:
        pd = _pandas_module()
        if pd is None:
            raise RuntimeError("pandas 未安装，无法读取候选股 CSV。")
        data = pd.read_csv(Path(path), dtype=str)
        rows = []
        for _, row in data.iterrows():
            normalized = self._normalize_row(row.to_dict())
            if normalized.get("symbol"):
                rows.append(normalized)
        return rows

    def rank(self, candidates: Iterable[Dict], top: int = 10) -> Dict:
        items = [self._score_candidate(item) for item in candidates]
        items.sort(key=lambda item: (item["score"], item["field_coverage"]), reverse=True)
        return {
            "success": bool(items),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total_candidates": len(items),
            "top": top,
            "items": items[:top],
            "warnings": self._warnings(items),
        }

    def generate_html(self, ranked: Dict, output_path: str | None = None) -> str:
        generated_at = datetime.now()
        rows = []
        for index, item in enumerate(ranked.get("items", []), 1):
            rows.append(
                "<tr>"
                f"<td>{index}</td>"
                f"<td>{html.escape(item['display_name'])}</td>"
                f"<td>{html.escape(item.get('industry_cn') or '暂无数据')}</td>"
                f"<td>{item['score']:.0f}</td>"
                f"<td>{html.escape(item['view'])}</td>"
                f"<td>{html.escape('；'.join(item['reasons'][:3]) or '暂无明确优势')}</td>"
                f"<td>{html.escape('；'.join(item['risks'][:3]) or '暂无突出风险')}</td>"
                "</tr>"
            )
        warning_text = "；".join(ranked.get("warnings", [])) or "候选池字段覆盖度满足初筛要求。"
        html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>股票机会短名单</title>
  <style>
    body {{ margin: 0; background: #f5f4ed; color: #171717; font-family: "PingFang SC", "Microsoft YaHei", serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 48px 64px; background: #f5f4ed; }}
    h1 {{ margin: 0 0 8px; font-size: 42px; }}
    .subtitle {{ color: #55534d; font-size: 16px; line-height: 1.7; margin-bottom: 28px; }}
    .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 22px 0 28px; }}
    .metric {{ border: 1px solid #ddd9cc; background: rgba(255,255,255,.36); padding: 16px 18px; border-radius: 6px; }}
    .value {{ font-size: 30px; font-weight: 800; color: #1b365d; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
    th, td {{ border-bottom: 1px solid #ddd9cc; padding: 12px 10px; text-align: left; vertical-align: top; }}
    th {{ color: #1b365d; background: rgba(255,255,255,.42); }}
    .note {{ margin-top: 22px; color: #66645d; line-height: 1.75; font-size: 14px; }}
    @media (max-width: 760px) {{ main {{ padding: 28px 18px; }} .summary {{ grid-template-columns: 1fr; }} h1 {{ font-size: 32px; }} }}
  </style>
</head>
<body>
  <main>
    <h1>股票机会短名单</h1>
    <div class="subtitle">生成时间：{generated_at.strftime('%Y-%m-%d %H:%M')}。本清单用于把候选池压缩为重点研究对象，后续应继续生成完整投研报告并复核真实数据。</div>
    <section class="summary">
      <div class="metric"><div class="value">{ranked.get('total_candidates', 0)}</div><div>候选总数</div></div>
      <div class="metric"><div class="value">{len(ranked.get('items', []))}</div><div>进入短名单</div></div>
      <div class="metric"><div class="value">真实字段</div><div>不使用模拟数据补齐</div></div>
    </section>
    <table>
      <thead><tr><th>排名</th><th>股票</th><th>行业</th><th>机会分</th><th>观察结论</th><th>入选理由</th><th>主要风险</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="note">下一步：优先对排名靠前且字段覆盖度较高的标的生成完整 HTML 投研报告，重点复核财报、估值假设、技术位置和风险触发条件。{html.escape(warning_text)}</div>
  </main>
</body>
</html>"""
        html_text = normalize_report_text(html_text)
        if output_path:
            Path(output_path).write_text(html_text, encoding="utf-8")
        return html_text

    def _normalize_row(self, row: Dict) -> Dict:
        normalized = {}
        for target, names in self.COLUMN_ALIASES.items():
            for key, value in row.items():
                if str(key).strip() in names:
                    normalized[target] = value
                    break
        return normalized

    def _score_candidate(self, row: Dict) -> Dict:
        symbol = _text(row.get("symbol"))
        name = _text(row.get("name"))
        industry = _text(row.get("industry"))
        current_price = _num(row.get("current_price"))
        fair_value = _num(row.get("fair_value"))
        pe = _num(row.get("pe"))
        pb = _num(row.get("pb"))
        roe = _num(row.get("roe"))
        debt_ratio = _num(row.get("debt_ratio"))
        revenue_growth = _num(row.get("revenue_growth"))
        profit_growth = _num(row.get("profit_growth"))
        gross_margin = _num(row.get("gross_margin"))
        net_margin = _num(row.get("net_margin"))
        rsi14 = _num(row.get("rsi14"))
        trend = _text(row.get("trend"))

        score = 50.0
        reasons: List[str] = []
        risks: List[str] = []
        fields_used = 0

        if fair_value is not None and current_price:
            fields_used += 1
            upside = fair_value / current_price - 1
            if upside >= 0.25:
                score += 15
                reasons.append(f"估值空间约{upside:.0%}")
            elif upside >= 0.1:
                score += 8
                reasons.append(f"估值仍有约{upside:.0%}空间")
            elif upside < 0:
                score -= 12
                risks.append("当前价格高于输入的公允价值")

        if pe is not None:
            fields_used += 1
            if 0 < pe <= 25:
                score += 8
                reasons.append("市盈率处于可研究区间")
            elif pe > 60:
                score -= 8
                risks.append("市盈率偏高")

        if pb is not None:
            fields_used += 1
            if 0 < pb <= 4:
                score += 5
            elif pb > 8:
                score -= 5
                risks.append("市净率偏高")

        if roe is not None:
            fields_used += 1
            if roe >= 18:
                score += 12
                reasons.append("ROE表现较强")
            elif roe < 8:
                score -= 8
                risks.append("ROE偏低")

        if debt_ratio is not None:
            fields_used += 1
            if debt_ratio <= 50:
                score += 6
                reasons.append("资产负债率相对可控")
            elif debt_ratio >= 70:
                score -= 10
                risks.append("资产负债率偏高")

        for label, value in (("收入增速", revenue_growth), ("利润增速", profit_growth)):
            if value is not None:
                fields_used += 1
                if value >= 15:
                    score += 6
                    reasons.append(f"{label}较快")
                elif value < 0:
                    score -= 8
                    risks.append(f"{label}为负")

        if gross_margin is not None:
            fields_used += 1
            if gross_margin >= 25:
                score += 4
                reasons.append("毛利率具备一定基础")
        if net_margin is not None:
            fields_used += 1
            if net_margin >= 10:
                score += 4
                reasons.append("净利率具备一定基础")

        if trend:
            fields_used += 1
            if "偏强" in trend or "多头" in trend:
                score += 5
                reasons.append("趋势偏强")
            elif "偏弱" in trend or "空头" in trend:
                score -= 5
                risks.append("趋势偏弱")

        if rsi14 is not None:
            fields_used += 1
            if rsi14 >= 75:
                score -= 4
                risks.append("RSI偏热，追高风险上升")
            elif 40 <= rsi14 <= 65:
                score += 3
                reasons.append("RSI未明显过热")

        score = max(0, min(100, score))
        field_coverage = fields_used / 12
        if field_coverage < 0.35:
            risks.append("候选字段覆盖不足，需补充真实数据")

        if score >= 75:
            view = "优先研究"
        elif score >= 60:
            view = "纳入观察"
        elif score >= 45:
            view = "谨慎跟踪"
        else:
            view = "暂缓研究"

        display_name = f"{name}（{symbol}）" if name else stock_display_name(symbol, {"industry": industry})
        return {
            "symbol": symbol,
            "display_name": display_name,
            "industry_cn": translate_industry(industry) if industry else "暂无数据",
            "score": round(score, 1),
            "view": view,
            "reasons": reasons,
            "risks": risks,
            "field_coverage": round(field_coverage, 2),
            "inputs": {
                "current_price": current_price,
                "fair_value": fair_value,
                "pe": pe,
                "pb": pb,
                "roe": roe,
                "debt_ratio": debt_ratio,
                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "trend": trend,
                "rsi14": rsi14,
                "industry": industry,
            },
        }

    def _warnings(self, items: List[Dict]) -> List[str]:
        if not items:
            return ["候选池为空，未生成短名单。"]
        low_coverage = sum(1 for item in items if item["field_coverage"] < 0.35)
        if low_coverage:
            return [f"{low_coverage} 只股票字段覆盖不足，短名单结论需降级为观察。"]
        return []


def rank_opportunities_from_csv(path: str, top: int = 10) -> Dict:
    pipeline = OpportunityPipeline()
    return pipeline.rank(pipeline.load_csv(path), top=top)


__all__ = ["OpportunityPipeline", "rank_opportunities_from_csv"]
