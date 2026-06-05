#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Watchlist monitoring dashboard for investor workflows."""

from __future__ import annotations

from datetime import datetime
import html
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from skills.shared import normalize_report_text, stock_display_name, translate_industry


SEVERITY_ORDER = {"高": 3, "中": 2, "低": 1, "提示": 0}


def _pandas_module():
    if find_spec("pandas") is None:
        return None
    import pandas as pd

    return pd


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


class WatchlistMonitor:
    """Evaluate watchlist triggers from real imported fields."""

    COLUMN_ALIASES = {
        "symbol": {"symbol", "code", "股票代码", "代码", "证券代码"},
        "name": {"name", "股票名称", "名称", "简称"},
        "industry": {"industry", "行业", "所属行业"},
        "current_price": {"current_price", "price", "当前价格", "最新价", "收盘"},
        "target_price": {"target_price", "目标价", "提醒价", "止盈价"},
        "stop_loss": {"stop_loss", "止损价", "风控价"},
        "fair_value": {"fair_value", "公允价值", "合理价值", "估值中枢"},
        "support_level": {"support_level", "支撑位"},
        "resistance_level": {"resistance_level", "压力位"},
        "rsi14": {"rsi14", "RSI", "RSI14"},
        "trend": {"trend", "趋势"},
        "roe": {"roe", "ROE", "净资产收益率"},
        "debt_ratio": {"debt_ratio", "资产负债率", "负债率"},
        "profit_growth": {"profit_growth", "利润增速", "净利润增速"},
    }

    def load_csv(self, path: str) -> List[Dict]:
        pd = _pandas_module()
        if pd is None:
            raise RuntimeError("pandas 未安装，无法读取自选股 CSV。")
        data = pd.read_csv(Path(path), dtype=str)
        rows = []
        for _, row in data.iterrows():
            item = self._normalize_row(row.to_dict())
            if item.get("symbol"):
                rows.append(item)
        return rows

    def monitor(self, watchlist: Iterable[Dict]) -> Dict:
        items = [self._monitor_item(item) for item in watchlist]
        items.sort(key=lambda item: (SEVERITY_ORDER.get(item["highest_severity"], 0), item["alert_count"]), reverse=True)
        return {
            "success": True,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "watchlist_size": len(items),
            "items": items,
            "summary": self._summary(items),
        }

    def generate_html(self, result: Dict, output_path: str | None = None) -> str:
        rows = []
        for item in result.get("items", []):
            alerts = "；".join(alert["title"] for alert in item.get("alerts", [])[:4]) or "暂无触发"
            rows.append(
                "<tr>"
                f"<td>{html.escape(item['display_name'])}</td>"
                f"<td>{html.escape(item.get('industry_cn') or '暂无数据')}</td>"
                f"<td>{self._price_text(item.get('current_price'))}</td>"
                f"<td>{html.escape(item['highest_severity'])}</td>"
                f"<td>{html.escape(item['status'])}</td>"
                f"<td>{html.escape(alerts)}</td>"
                f"<td>{html.escape(item['next_action'])}</td>"
                "</tr>"
            )
        html_text = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>自选股监控面板</title>
  <style>
    body {{ margin: 0; background: #f5f4ed; color: #171717; font-family: "PingFang SC", "Microsoft YaHei", serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 48px 64px; }}
    h1 {{ margin: 0 0 8px; font-size: 42px; }}
    .subtitle {{ color: #55534d; font-size: 16px; line-height: 1.7; margin-bottom: 26px; }}
    .summary {{ border-left: 5px solid #1b365d; background: rgba(255,255,255,.4); padding: 16px 20px; margin-bottom: 24px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 15px; }}
    th, td {{ border-bottom: 1px solid #ddd9cc; padding: 12px 10px; text-align: left; vertical-align: top; }}
    th {{ color: #1b365d; background: rgba(255,255,255,.42); }}
    .note {{ margin-top: 20px; color: #66645d; line-height: 1.75; font-size: 14px; }}
    @media (max-width: 760px) {{ main {{ padding: 28px 18px; }} h1 {{ font-size: 32px; }} }}
  </style>
</head>
<body>
  <main>
    <h1>自选股监控面板</h1>
    <div class="subtitle">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}。本面板用于持续跟踪价格、估值、技术面和财务风险触发条件。</div>
    <div class="summary">{html.escape(result.get('summary', '暂无监控摘要'))}</div>
    <table>
      <thead><tr><th>股票</th><th>行业</th><th>现价</th><th>级别</th><th>状态</th><th>触发条件</th><th>下一步动作</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="note">监控面板只提示需要复核的条件，不构成买卖建议。正式决策前应重新生成完整投研报告，并复核真实行情、财报和公告。</div>
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

    def _monitor_item(self, row: Dict) -> Dict:
        symbol = _text(row.get("symbol"))
        name = _text(row.get("name"))
        industry = _text(row.get("industry"))
        current_price = _num(row.get("current_price"))
        alerts = self._alerts(row, current_price)
        alerts.sort(key=lambda item: SEVERITY_ORDER.get(item["severity"], 0), reverse=True)
        highest = alerts[0]["severity"] if alerts else "提示"
        status = self._status(highest, alerts)
        return {
            "symbol": symbol,
            "display_name": f"{name}（{symbol}）" if name else stock_display_name(symbol, {"industry": industry}),
            "industry_cn": translate_industry(industry) if industry else "暂无数据",
            "current_price": current_price,
            "highest_severity": highest,
            "alert_count": len(alerts),
            "alerts": alerts,
            "status": status,
            "next_action": self._next_action(highest, alerts),
            "reasons": [alert["title"] for alert in alerts],
            "inputs": {
                "current_price": current_price,
                "fair_value": _num(row.get("fair_value")),
                "roe": _num(row.get("roe")),
                "debt_ratio": _num(row.get("debt_ratio")),
                "profit_growth": _num(row.get("profit_growth")),
                "trend": _text(row.get("trend")),
                "rsi14": _num(row.get("rsi14")),
                "industry": industry,
            },
        }

    def _alerts(self, row: Dict, current_price: Optional[float]) -> List[Dict]:
        alerts: List[Dict] = []
        target_price = _num(row.get("target_price"))
        stop_loss = _num(row.get("stop_loss"))
        fair_value = _num(row.get("fair_value"))
        support = _num(row.get("support_level"))
        resistance = _num(row.get("resistance_level"))
        rsi14 = _num(row.get("rsi14"))
        roe = _num(row.get("roe"))
        debt_ratio = _num(row.get("debt_ratio"))
        profit_growth = _num(row.get("profit_growth"))
        trend = _text(row.get("trend"))

        if current_price is None:
            alerts.append(self._alert("中", "行情价格缺失", "没有真实现价，无法判断价格触发条件。"))
            return alerts

        if target_price is not None and current_price >= target_price:
            alerts.append(self._alert("中", "到达目标观察价", f"现价 {current_price:.2f} 已达到或超过目标价 {target_price:.2f}。"))
        if stop_loss is not None and current_price <= stop_loss:
            alerts.append(self._alert("高", "跌破风控价", f"现价 {current_price:.2f} 已低于风控价 {stop_loss:.2f}。"))
        if support is not None and current_price < support:
            alerts.append(self._alert("高", "跌破支撑位", f"现价 {current_price:.2f} 低于支撑位 {support:.2f}，需要复核趋势是否破坏。"))
        if resistance is not None and current_price >= resistance:
            alerts.append(self._alert("低", "接近或突破压力位", f"现价 {current_price:.2f} 已接近压力位 {resistance:.2f}，观察放量确认。"))
        if fair_value is not None and fair_value > 0:
            premium = current_price / fair_value - 1
            if premium >= 0.15:
                alerts.append(self._alert("中", "估值溢价偏高", f"现价较公允价值高约 {premium:.0%}。"))
            elif premium <= -0.2:
                alerts.append(self._alert("低", "价格低于估值中枢", f"现价较公允价值低约 {-premium:.0%}，可进入复核清单。"))
        if rsi14 is not None:
            if rsi14 >= 75:
                alerts.append(self._alert("中", "短线动量过热", f"RSI 14 为 {rsi14:.1f}，追高风险上升。"))
            elif rsi14 <= 30:
                alerts.append(self._alert("低", "短线动量偏冷", f"RSI 14 为 {rsi14:.1f}，观察是否止跌。"))
        if "偏弱" in trend or "空头" in trend:
            alerts.append(self._alert("中", "趋势偏弱", "趋势字段显示偏弱，需等待重新站上关键均线。"))
        if roe is not None and roe < 8:
            alerts.append(self._alert("中", "ROE偏低", f"ROE 为 {roe:.1f}%，盈利质量需要复核。"))
        if debt_ratio is not None and debt_ratio >= 70:
            alerts.append(self._alert("高", "资产负债率偏高", f"资产负债率为 {debt_ratio:.1f}%，财务风险需要优先复核。"))
        if profit_growth is not None and profit_growth < 0:
            alerts.append(self._alert("中", "利润增速转负", f"利润增速为 {profit_growth:.1f}%，需要复核业绩趋势。"))
        return alerts

    def _alert(self, severity: str, title: str, message: str) -> Dict:
        return {"severity": severity, "title": title, "message": message}

    def _status(self, severity: str, alerts: List[Dict]) -> str:
        if not alerts:
            return "正常跟踪"
        if severity == "高":
            return "立即复核"
        if severity == "中":
            return "重点观察"
        return "纳入提醒"

    def _next_action(self, severity: str, alerts: List[Dict]) -> str:
        if not alerts:
            return "维持监控，等待价格、财报或技术面新触发。"
        if severity == "高":
            return "重新生成完整报告，优先复核价格破位、财务风险和公告变化。"
        if severity == "中":
            return "更新行情和财务字段，确认触发条件是否持续。"
        return "加入观察清单，等待进一步确认。"

    def _summary(self, items: List[Dict]) -> str:
        high = sum(1 for item in items if item["highest_severity"] == "高")
        medium = sum(1 for item in items if item["highest_severity"] == "中")
        if high:
            return f"当前 {high} 只股票触发高优先级风险，建议立即复核；另有 {medium} 只需要重点观察。"
        if medium:
            return f"当前没有高优先级风险，{medium} 只股票需要重点观察。"
        return "当前自选池没有明显高优先级触发条件，维持常规跟踪。"

    def _price_text(self, value: Optional[float]) -> str:
        return "暂无数据" if value is None else f"{value:.2f}"


def monitor_watchlist_from_csv(path: str) -> Dict:
    monitor = WatchlistMonitor()
    return monitor.monitor(monitor.load_csv(path))


__all__ = ["WatchlistMonitor", "monitor_watchlist_from_csv"]
