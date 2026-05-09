#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报预测模块 - Earnings Preview
预测收入、利润、EPS等财务指标
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import importlib

# ============ 辅助函数 ============

def _num(value: Any) -> Optional[float]:
    """安全转换为数值"""
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "None", "nan", "NaN", "暂无数据", "-"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _detect_market(symbol: str) -> str:
    """检测市场"""
    if symbol.isdigit() and len(symbol) == 6:
        return "cn"
    if symbol.endswith(".HK") or symbol.isdigit():
        return "hk"
    return "us"


# ============ 数据获取 ============

def _fetch_financial_data(symbol: str, market: str) -> Dict:
    """获取历史财务数据"""
    result = {
        "quarterly": [],
        "annual": [],
        "warnings": [],
    }
    
    if market == "us":
        result.update(_fetch_us_financials(symbol))
    elif market == "cn":
        result.update(_fetch_cn_financials(symbol))
    
    return result


def _fetch_us_financials(symbol: str) -> Dict:
    """获取美股财务数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "annual": [],
        "warnings": [],
    }
    
    if find_spec("yfinance") is None:
        result["warnings"].append("yfinance 未安装")
        return result
    
    try:
        yf = importlib.import_module("yfinance")
        ticker = yf.Ticker(symbol)
        
        # 季度数据
        try:
            quarterly = ticker.quarterly_financials
            if quarterly is not None and not quarterly.empty:
                for col in quarterly.columns:
                    row = quarterly[col]
                    result["quarterly"].append({
                        "date": str(col)[:10],
                        "revenue": _num(row.get("Total Revenue")),
                        "gross_profit": _num(row.get("Gross Profit")),
                        "operating_income": _num(row.get("Operating Income")),
                        "net_income": _num(row.get("Net Income")),
                        "ebitda": _num(row.get("EBITDA")),
                    })
        except Exception as e:
            result["warnings"].append(f"季度财报获取失败: {e}")
        
        # 年度数据
        try:
            financials = ticker.financials
            if financials is not None and not financials.empty:
                for col in financials.columns:
                    row = financials[col]
                    result["annual"].append({
                        "date": str(col)[:10],
                        "revenue": _num(row.get("Total Revenue")),
                        "gross_profit": _num(row.get("Gross Profit")),
                        "operating_income": _num(row.get("Operating Income")),
                        "net_income": _num(row.get("Net Income")),
                        "ebitda": _num(row.get("EBITDA")),
                    })
        except Exception as e:
            result["warnings"].append(f"年度财报获取失败: {e}")
        
        # 共享数据
        try:
            shares = ticker.info.get("sharesOutstanding", 0)
            result["shares_outstanding"] = _num(shares)
            result["ticker_info"] = {
                "name": ticker.info.get("shortName", symbol),
                "sector": ticker.info.get("sector"),
                "industry": ticker.info.get("industry"),
            }
        except Exception:
            pass
        
    except Exception as e:
        result["warnings"].append(f"yfinance 错误: {e}")
    
    return result


def _fetch_cn_financials(symbol: str) -> Dict:
    """获取A股财务数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "annual": [],
        "warnings": [],
    }
    
    # A股暂时使用占位数据（需要 AkShare 或 Baostock）
    if find_spec("akshare") is None:
        result["warnings"].append("AkShare 未安装，无法获取A股财报数据")
    else:
        try:
            ak = importlib.import_module("akshare")
            # 尝试获取A股财报
            fin = ak.stock_financial_analysis_indicator(symbol=symbol)
            if fin is not None and not fin.empty:
                for idx, row in fin.head(8).iterrows():
                    result["quarterly"].append({
                        "date": str(idx)[:10],
                        "revenue": _num(row.get("营业总收入")),
                        "gross_profit": _num(row.get("销售毛利率")),
                        "operating_income": _num(row.get("营业利润")),
                        "net_income": _num(row.get("净利润")),
                        "roe": _num(row.get("净资产收益率")),
                    })
        except Exception as e:
            result["warnings"].append(f"A股财报获取失败: {e}")
    
    return result


# ============ 预测算法 ============

def _linear_regression(values: List[float]) -> Dict:
    """简单线性回归"""
    if len(values) < 2:
        return {"slope": 0, "intercept": values[-1] if values else 0, "r_squared": 0}
    
    n = len(values)
    x = list(range(n))
    y = values
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)
    
    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        return {"slope": 0, "intercept": sum_y / n, "r_squared": 0}
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    # 计算 R²
    y_mean = sum_y / n
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
    }


def _calculate_growth_rate(values: List[float]) -> Optional[float]:
    """计算增长率"""
    if len(values) < 2:
        return None
    
    # 使用最近几个值计算平均增长率
    recent = values[-4:] if len(values) >= 4 else values
    growth_rates = []
    
    for i in range(1, len(recent)):
        if recent[i-1] and recent[i-1] != 0:
            rate = (recent[i] - recent[i-1]) / abs(recent[i-1])
            growth_rates.append(rate)
    
    return sum(growth_rates) / len(growth_rates) if growth_rates else None


def _moving_average(values: List[float], window: int = 4) -> float:
    """移动平均"""
    if not values:
        return 0
    recent = values[-window:] if len(values) >= window else values
    return sum(recent) / len(recent)


# ============ 预测函数 ============

def predict_revenue(historical: List[Dict], periods: int = 4) -> Dict:
    """
    预测收入
    
    Args:
        historical: 历史季度财报数据列表
        periods: 预测季度数
        
    Returns:
        收入预测结果
    """
    if not historical:
        return {"error": "无历史数据", "confidence": "低"}
    
    # 提取收入数据
    revenues = []
    for row in historical:
        rev = row.get("revenue")
        if rev is not None and rev > 0:
            revenues.append(rev)
    
    if len(revenues) < 2:
        return {"error": "收入数据不足", "confidence": "低"}
    
    # 计算增长率
    growth_rate = _calculate_growth_rate(revenues)
    
    # 线性回归
    regression = _linear_regression(revenues[-6:] if len(revenues) >= 6 else revenues)
    
    # 生成预测
    last_revenue = revenues[-1]
    predictions = []
    
    for i in range(1, periods + 1):
        # 使用线性回归预测
        linear_pred = regression["slope"] * len(revenues) + regression["intercept"]
        
        # 使用增长率预测
        growth_pred = last_revenue * (1 + growth_rate) ** i if growth_rate else last_revenue
        
        # 综合预测（加权平均）
        combined = linear_pred * 0.4 + growth_pred * 0.6
        
        predictions.append({
            "period": i,
            "linear": round(linear_pred, 2),
            "growth_based": round(growth_pred, 2),
            "combined": round(combined, 2),
        })
    
    # 计算置信度
    confidence = "低"
    if len(revenues) >= 8 and regression["r_squared"] > 0.7:
        confidence = "高"
    elif len(revenues) >= 4 and regression["r_squared"] > 0.5:
        confidence = "中"
    
    # 年化收入预测
    annual_prediction = sum(p["combined"] for p in predictions[-4:]) if len(predictions) >= 4 else predictions[-1]["combined"]
    
    return {
        "last_revenue": round(last_revenue, 2),
        "growth_rate": round(growth_rate * 100, 2) if growth_rate else None,
        "regression_r_squared": round(regression["r_squared"], 3),
        "predictions": predictions,
        "annual_prediction": round(annual_prediction, 2),
        "confidence": confidence,
        "assumptions": [
            f"基于{len(revenues)}个季度历史数据",
            f"平均增长率: {round(growth_rate * 100, 1) if growth_rate else 'N/A'}%" if growth_rate else "增长率无法计算",
            f"回归R²: {round(regression['r_squared'], 2)}",
        ],
    }


def predict_profit_margin(historical: List[Dict], periods: int = 4) -> Dict:
    """
    预测利润率
    
    预测毛利率、净利率趋势
    """
    if not historical:
        return {"error": "无历史数据", "confidence": "低"}
    
    # 提取利润率数据
    gross_margins = []
    net_margins = []
    
    for row in historical:
        if row.get("gross_profit") is not None and row.get("revenue") and row["revenue"] > 0:
            gross_margins.append(row["gross_profit"])
        if row.get("net_income") is not None and row.get("revenue") and row["revenue"] > 0:
            net_margins.append(row["net_income"] / row["revenue"] * 100)
    
    result = {
        "gross_margin": {},
        "net_margin": {},
    }
    
    # 毛利率预测
    if len(gross_margins) >= 2:
        gm_avg = _moving_average(gross_margins)
        gm_trend = _linear_regression(gross_margins[-6:] if len(gross_margins) >= 6 else gross_margins)
        gm_predictions = []
        
        for i in range(1, periods + 1):
            pred = gm_trend["slope"] * len(gross_margins) + gm_trend["intercept"]
            # 限制在合理范围
            pred = max(0, min(100, pred))
            gm_predictions.append(round(pred, 2))
        
        result["gross_margin"] = {
            "current": round(gross_margins[-1], 2) if gross_margins else None,
            "average": round(gm_avg, 2),
            "trend_slope": round(gm_trend["slope"], 4),
            "predictions": gm_predictions,
            "trend": "扩张" if gm_trend["slope"] > 0.5 else ("收缩" if gm_trend["slope"] < -0.5 else "稳定"),
        }
    else:
        result["gross_margin"] = {"error": "数据不足"}
    
    # 净利率预测
    if len(net_margins) >= 2:
        nm_avg = _moving_average(net_margins)
        nm_trend = _linear_regression(net_margins[-6:] if len(net_margins) >= 6 else net_margins)
        nm_predictions = []
        
        for i in range(1, periods + 1):
            pred = nm_trend["slope"] * len(net_margins) + nm_trend["intercept"]
            pred = max(-50, min(50, pred))  # 净利率可能在负值
            nm_predictions.append(round(pred, 2))
        
        result["net_margin"] = {
            "current": round(net_margins[-1], 2) if net_margins else None,
            "average": round(nm_avg, 2),
            "trend_slope": round(nm_trend["slope"], 4),
            "predictions": nm_predictions,
            "trend": "改善" if nm_trend["slope"] > 0.2 else ("恶化" if nm_trend["slope"] < -0.2 else "稳定"),
        }
    else:
        result["net_margin"] = {"error": "数据不足"}
    
    # 置信度
    if len(gross_margins) >= 4 and len(net_margins) >= 4:
        result["confidence"] = "中"
    else:
        result["confidence"] = "低"
    
    return result


def predict_eps(historical: List[Dict], shares_outstanding: Optional[float] = None, periods: int = 4) -> Dict:
    """
    预测每股收益 (EPS)
    """
    if not historical:
        return {"error": "无历史数据", "confidence": "低"}
    
    # 提取净利润数据
    net_incomes = []
    for row in historical:
        ni = row.get("net_income")
        if ni is not None and ni > 0:
            net_incomes.append(ni)
    
    if len(net_incomes) < 2:
        return {"error": "净利润数据不足", "confidence": "低"}
    
    # 预测净利润
    regression = _linear_regression(net_incomes[-6:] if len(net_incomes) >= 6 else net_incomes)
    growth_rate = _calculate_growth_rate(net_incomes)
    
    last_income = net_incomes[-1]
    predictions = []
    
    for i in range(1, periods + 1):
        linear_pred = regression["slope"] * len(net_incomes) + regression["intercept"]
        growth_pred = last_income * (1 + growth_rate) ** i if growth_rate else last_income
        combined = linear_pred * 0.4 + growth_pred * 0.6
        
        predictions.append({
            "period": i,
            "predicted_net_income": round(combined, 2),
        })
    
    # 计算EPS
    if shares_outstanding and shares_outstanding > 0:
        for pred in predictions:
            pred["predicted_eps"] = round(pred["predicted_net_income"] / shares_outstanding, 2)
    
    # 趋势判断
    trend = "增长"
    if growth_rate and growth_rate < 0:
        trend = "下降"
    elif growth_rate and abs(growth_rate) < 0.02:
        trend = "持平"
    
    return {
        "last_eps": round(net_incomes[-1] / shares_outstanding, 2) if shares_outstanding else None,
        "last_net_income": round(last_income, 2),
        "shares_outstanding": shares_outstanding,
        "growth_rate": round(growth_rate * 100, 2) if growth_rate else None,
        "trend": trend,
        "predictions": predictions,
        "confidence": "中" if len(net_incomes) >= 4 else "低",
    }


def predict_earnings(historical: List[Dict], shares_outstanding: Optional[float] = None, periods: int = 4) -> Dict:
    """
    综合财报预测
    
    整合收入、利润、EPS预测
    """
    result = {
        "generated_at": datetime.now().isoformat(),
        "periods": periods,
        "components": {},
        "warnings": [],
        "confidence": "低",
    }
    
    # 收入预测
    revenue_result = predict_revenue(historical, periods)
    if "error" not in revenue_result:
        result["components"]["revenue"] = revenue_result
    else:
        result["warnings"].append(revenue_result["error"])
    
    # 利润率预测
    margin_result = predict_profit_margin(historical, periods)
    result["components"]["margins"] = margin_result
    
    # EPS预测
    eps_result = predict_eps(historical, shares_outstanding, periods)
    if "error" not in eps_result:
        result["components"]["eps"] = eps_result
    else:
        result["warnings"].append(eps_result["error"])
    
    # 综合置信度
    confidences = []
    if "confidence" in revenue_result:
        confidences.append(revenue_result["confidence"])
    if margin_result.get("confidence"):
        confidences.append(margin_result["confidence"])
    if "confidence" in eps_result:
        confidences.append(eps_result["confidence"])
    
    if "高" in confidences:
        result["confidence"] = "高"
    elif "中" in confidences:
        result["confidence"] = "中"
    
    # 生成摘要
    if "revenue" in result["components"]:
        rev = result["components"]["revenue"]
        result["summary"] = {
            "next_quarter_revenue": rev["predictions"][0]["combined"] if rev.get("predictions") else None,
            "annual_revenue_estimate": rev.get("annual_prediction"),
            "revenue_growth_rate": rev.get("growth_rate"),
            "revenue_confidence": rev.get("confidence"),
        }
    
    if "eps" in result["components"]:
        eps = result["components"]["eps"]
        if "summary" not in result:
            result["summary"] = {}
        result["summary"]["next_quarter_eps"] = eps["predictions"][0].get("predicted_eps") if eps.get("predictions") else None
        result["summary"]["eps_trend"] = eps.get("trend")
    
    return result


# ============ 主函数 ============

def earnings_preview(symbol: str, periods: int = 4) -> Dict:
    """
    财报预测主函数
    
    Args:
        symbol: 股票代码
        periods: 预测季度数 (默认4个季度)
        
    Returns:
        完整的财报预测报告
    """
    market = _detect_market(symbol)
    financial_data = _fetch_financial_data(symbol, market)
    
    result = {
        "symbol": symbol,
        "market": market,
        "generated_at": datetime.now().isoformat(),
        "data_source": "yfinance" if market == "us" else "AkShare/Baostock",
        "data_points": {
            "quarterly": len(financial_data["quarterly"]),
            "annual": len(financial_data["annual"]),
        },
        "warnings": financial_data["warnings"],
    }
    
    if not financial_data["quarterly"] and not financial_data["annual"]:
        result["error"] = "无法获取财务数据"
        result["note"] = "预测需要至少2个季度的历史财报数据"
        return result
    
    # 使用季度数据优先
    historical = financial_data["quarterly"] if financial_data["quarterly"] else financial_data["annual"]
    shares = financial_data.get("shares_outstanding")
    info = financial_data.get("ticker_info", {})
    
    # 执行预测
    predictions = predict_earnings(historical, shares, periods)
    result.update(predictions)
    
    if info:
        result["company"] = info
    
    # 添加风险提示
    result["disclaimer"] = (
        "⚠️ 本预测基于历史数据统计模型，不代表实际业绩。"
        "股市有风险，投资需谨慎。预测结果仅供参考，不构成投资建议。"
    )
    
    return result


# ============ CLI 友好输出 ============

def format_preview_output(result: Dict) -> str:
    """格式化预测结果输出"""
    if result.get("error"):
        return f"❌ {result['error']}\n\n{result.get('note', '')}"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 财报预测报告 - {result.get('symbol', 'N/A')}")
    lines.append("=" * 60)
    lines.append(f"生成时间: {result.get('generated_at', '')[:10]}")
    lines.append(f"数据来源: {result.get('data_source', 'N/A')}")
    lines.append(f"数据点数: {result.get('data_points', {}).get('quarterly', 0)} 个季度")
    lines.append(f"置信度: {result.get('confidence', '低')}")
    
    if result.get("warnings"):
        lines.append("\n⚠️ 警告:")
        for w in result["warnings"]:
            lines.append(f"  • {w}")
    
    # 收入预测
    if "components" in result and "revenue" in result["components"]:
        rev = result["components"]["revenue"]
        lines.append("\n📈 收入预测:")
        lines.append(f"  当前收入: {rev.get('last_revenue', 'N/A'):,.0f}" if rev.get('last_revenue') else "  当前收入: N/A")
        lines.append(f"  增长率: {rev.get('growth_rate', 'N/A')}%")
        lines.append(f"  回归R²: {rev.get('regression_r_squared', 'N/A')}")
        if rev.get("predictions"):
            lines.append("  未来预测:")
            for p in rev["predictions"][:2]:
                lines.append(f"    Q{p['period']}: {p['combined']:,.0f} (线性: {p['linear']:,.0f})")
    
    # 利润率预测
    if "components" in result and "margins" in result["components"]:
        margins = result["components"]["margins"]
        if "gross_margin" in margins and "current" in margins["gross_margin"]:
            lines.append("\n📉 利润率预测:")
            lines.append(f"  毛利率: {margins['gross_margin']['current']}% (趋势: {margins['gross_margin'].get('trend', 'N/A')})")
        if "net_margin" in margins and "current" in margins["net_margin"]:
            lines.append(f"  净利率: {margins['net_margin']['current']}% (趋势: {margins['net_margin'].get('trend', 'N/A')})")
    
    # EPS预测
    if "components" in result and "eps" in result["components"]:
        eps = result["components"]["eps"]
        lines.append("\n💰 EPS预测:")
        lines.append(f"  当前EPS: {eps.get('last_eps', 'N/A')}")
        lines.append(f"  趋势: {eps.get('trend', 'N/A')}")
        lines.append(f"  增长率: {eps.get('growth_rate', 'N/A')}%")
        if eps.get("predictions") and eps["predictions"][0].get("predicted_eps"):
            lines.append(f"  下季度EPS预测: {eps['predictions'][0]['predicted_eps']}")
    
    lines.append("\n" + "=" * 60)
    lines.append(result.get("disclaimer", ""))
    
    return "\n".join(lines)


# ============ 测试 ============

if __name__ == "__main__":
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    periods = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    print(f"📊 财报预测: {symbol} (预测 {periods} 个季度)")
    print()
    
    result = earnings_preview(symbol, periods)
    print(format_preview_output(result))
