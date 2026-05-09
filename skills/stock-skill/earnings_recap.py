#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报回顾模块 - Earnings Recap
分析实际财报与预期的差异，包括业绩达标检测、利润率变化、资产负债表健康度、现金流质量
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
    if symbol.endswith(".HK"):
        return "hk"
    return "us"


# ============ 数据获取 ============

def _fetch_earnings_data(symbol: str, market: str) -> Dict:
    """获取财报数据"""
    result = {
        "quarterly": [],
        "annual": [],
        "balance_sheet": [],
        "cash_flow": [],
        "warnings": [],
    }
    
    if market == "us":
        result.update(_fetch_us_earnings_data(symbol))
    elif market == "cn":
        result.update(_fetch_cn_earnings_data(symbol))
    
    return result


def _fetch_us_earnings_data(symbol: str) -> Dict:
    """获取美股财报数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "annual": [],
        "balance_sheet": [],
        "cash_flow": [],
        "warnings": [],
    }
    
    if find_spec("yfinance") is None:
        result["warnings"].append("yfinance 未安装")
        return result
    
    try:
        yf = importlib.import_module("yfinance")
        ticker = yf.Ticker(symbol)
        
        # 季度财报
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
                        "eps": _num(row.get("Basic EPS") or row.get("Diluted EPS")),
                    })
        except Exception as e:
            result["warnings"].append(f"季度财报获取失败: {e}")
        
        # 年度财报
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
                    })
        except Exception as e:
            result["warnings"].append(f"年度财报获取失败: {e}")
        
        # 资产负债表
        try:
            bs = ticker.quarterly_balance_sheet
            if bs is not None and not bs.empty:
                for col in bs.columns:
                    row = bs[col]
                    result["balance_sheet"].append({
                        "date": str(col)[:10],
                        "total_assets": _num(row.get("Total Assets")),
                        "total_liabilities": _num(row.get("Total Liabilities")),
                        "total_equity": _num(row.get("Total Stockholder Equity")),
                        "cash": _num(row.get("Cash And Cash Equivalents")),
                        "debt": _num(row.get("Short Long Term Debt") or row.get("Long Term Debt")),
                    })
        except Exception as e:
            result["warnings"].append(f"资产负债表获取失败: {e}")
        
        # 现金流量表
        try:
            cf = ticker.quarterly_cashflow
            if cf is not None and not cf.empty:
                for col in cf.columns:
                    row = cf[col]
                    result["cash_flow"].append({
                        "date": str(col)[:10],
                        "operating_cash_flow": _num(row.get("Total Cash From Operating Activities")),
                        "investing_cash_flow": _num(row.get("Total Cash From Investing Activities")),
                        "financing_cash_flow": _num(row.get("Total Cash From Financing Activities")),
                        "free_cash_flow": _num(row.get("Free Cash Flow")),
                        "capex": _num(row.get("Capital Expenditures")),
                    })
        except Exception as e:
            result["warnings"].append(f"现金流量表获取失败: {e}")
        
        # 基本信息
        try:
            info = ticker.info
            result["info"] = {
                "name": info.get("shortName", symbol),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "shares_outstanding": _num(info.get("sharesOutstanding")),
            }
        except Exception:
            pass
        
    except Exception as e:
        result["warnings"].append(f"yfinance 错误: {e}")
    
    return result


def _fetch_cn_earnings_data(symbol: str) -> Dict:
    """获取A股财报数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "annual": [],
        "balance_sheet": [],
        "cash_flow": [],
        "warnings": [],
    }
    
    if find_spec("akshare") is None:
        result["warnings"].append("AkShare 未安装，无法获取A股数据")
        return result
    
    # A股实现需要 AkShare
    result["warnings"].append("A股财报回顾需要 AkShare 支持")
    
    return result


# ============ 业绩分析函数 ============

def analyze_actual_vs_expected(current: Dict, historical: List[Dict], consensus_estimates: Optional[Dict] = None) -> Dict:
    """
    业绩达标检测：实际 vs 预期
    
    Args:
        current: 最新季度数据
        historical: 历史数据
        consensus_estimates: 分析师一致预期 (可选)
    """
    if not historical or not current:
        return {"error": "数据不足"}
    
    result = {
        "actual": {},
        "vs_historical": {},
        "vs_consensus": {},
        "verdict": "unknown",
    }
    
    # 分析指标
    metrics = ["revenue", "net_income", "eps", "gross_profit"]
    
    for metric in metrics:
        current_val = current.get(metric)
        result["actual"][metric] = current_val
        
        # vs 历史 (上季度)
        if len(historical) >= 1:
            prev = historical[0].get(metric)
            if current_val and prev:
                change = (current_val - prev) / abs(prev) * 100
                result["vs_historical"][metric] = {
                    "previous": prev,
                    "change_pct": round(change, 2),
                    "direction": "up" if change > 0 else "down",
                }
        
        # vs 历史均值
        if len(historical) >= 2:
            hist_vals = [h.get(metric) for h in historical[1:] if h.get(metric)]
            if hist_vals and current_val:
                avg = sum(hist_vals) / len(hist_vals)
                vs_avg = (current_val - avg) / avg * 100 if avg else 0
                result["vs_historical"][f"{metric}_vs_avg"] = {
                    "average": round(avg, 2),
                    "vs_avg_pct": round(vs_avg, 2),
                }
    
    # vs 一致预期
    if consensus_estimates:
        for metric in metrics:
            estimate = consensus_estimates.get(metric)
            actual = current.get(metric)
            if estimate and actual:
                surprise = (actual - estimate) / estimate * 100
                result["vs_consensus"][metric] = {
                    "estimate": estimate,
                    "actual": actual,
                    "surprise_pct": round(surprise, 2),
                    "beat": surprise > 0,
                }
    
    # 综合判断
    beats = sum(1 for v in result["vs_consensus"].values() if v.get("beat", False))
    misses = len(result["vs_consensus"]) - beats
    
    if beats > misses and beats > 0:
        result["verdict"] = "beat"
        result["verdict_text"] = "业绩超预期"
    elif misses > beats:
        result["verdict"] = "miss"
        result["verdict_text"] = "业绩低于预期"
    else:
        result["verdict"] = "in_line"
        result["verdict_text"] = "业绩符合预期"
    
    return result


def analyze_margin_trends(quarterly_data: List[Dict]) -> Dict:
    """
    利润率变化分析
    
    分析毛利率、净利率的同比和环比变化
    """
    if not quarterly_data or len(quarterly_data) < 2:
        return {"error": "数据不足"}
    
    result = {
        "gross_margin": [],
        "net_margin": [],
        "operating_margin": [],
        "trends": {},
    }
    
    for i, quarter in enumerate(quarterly_data[:8]):  # 最多分析8个季度
        revenue = quarter.get("revenue")
        gross = quarter.get("gross_profit")
        net = quarter.get("net_income")
        op_income = quarter.get("operating_income")
        
        margin_data = {
            "date": quarter.get("date"),
            "period": i + 1,
        }
        
        if revenue and revenue > 0:
            if gross:
                margin_data["gross_margin"] = round(gross / revenue * 100, 2)
            if net:
                margin_data["net_margin"] = round(net / revenue * 100, 2)
            if op_income:
                margin_data["operating_margin"] = round(op_income / revenue * 100, 2)
        
        if margin_data.get("gross_margin"):
            result["gross_margin"].append(margin_data)
        if margin_data.get("net_margin"):
            result["net_margin"].append(margin_data)
        if margin_data.get("operating_margin"):
            result["operating_margin"].append(margin_data)
    
    # 计算趋势
    for margin_type in ["gross_margin", "net_margin", "operating_margin"]:
        if len(result[margin_type]) >= 4:
            recent = result[margin_type][:4]
            older = result[margin_type][4:]
            
            if older:
                recent_avg = sum(m.get(margin_type) for m in recent) / len(recent)
                older_avg = sum(m.get(margin_type) for m in older) / len(older)
                yoy_change = recent_avg - older_avg
                
                result["trends"][margin_type] = {
                    "recent_avg": round(recent_avg, 2),
                    "older_avg": round(older_avg, 2),
                    "yoy_change": round(yoy_change, 2),
                    "direction": "improving" if yoy_change > 1 else ("worsening" if yoy_change < -1 else "stable"),
                }
    
    # 当前季度状态
    if result["gross_margin"]:
        latest = result["gross_margin"][0]
        result["latest"] = {
            "gross_margin": latest.get("gross_margin"),
            "net_margin": latest.get("net_margin"),
            "operating_margin": latest.get("operating_margin"),
            "date": latest.get("date"),
        }
    
    return result


def analyze_balance_sheet_health(balance_sheet_data: List[Dict]) -> Dict:
    """
    资产负债表健康度分析
    """
    if not balance_sheet_data or len(balance_sheet_data) < 2:
        return {"error": "数据不足"}
    
    result = {
        "current_ratio": [],
        "debt_to_equity": [],
        "asset_quality": [],
        "trends": {},
    }
    
    for i, bs in enumerate(balance_sheet_data[:8]):
        assets = bs.get("total_assets")
        liabilities = bs.get("total_liabilities")
        equity = bs.get("total_equity")
        cash = bs.get("cash")
        debt = bs.get("debt")
        
        health = {
            "date": bs.get("date"),
            "period": i + 1,
        }
        
        # 流动比率 (简化)
        if assets and liabilities and assets > 0:
            health["asset_to_liability"] = round(assets / liabilities, 2)
        
        # 负债权益比
        if liabilities and equity and equity > 0:
            health["debt_to_equity"] = round(liabilities / equity, 2)
        
        # 现金充足度
        if cash and liabilities and liabilities > 0:
            health["cash_to_liability"] = round(cash / liabilities * 100, 2)
        
        # 杠杆率
        if debt and equity and equity > 0:
            health["financial_leverage"] = round(debt / equity, 2)
        
        result["asset_quality"].append(health)
    
    # 计算趋势
    if len(result["asset_quality"]) >= 4:
        recent = result["asset_quality"][:4]
        older = result["asset_quality"][4:]
        
        if older:
            # 杠杆率趋势
            recent_leverage = [r.get("financial_leverage") for r in recent if r.get("financial_leverage")]
            older_leverage = [r.get("financial_leverage") for r in older if r.get("financial_leverage")]
            
            if recent_leverage and older_leverage:
                result["trends"]["leverage"] = {
                    "recent_avg": round(sum(recent_leverage) / len(recent_leverage), 2),
                    "older_avg": round(sum(older_leverage) / len(older_leverage), 2),
                    "direction": "increasing" if sum(recent_leverage) > sum(older_leverage) else "decreasing",
                }
    
    # 当前状态评估
    if result["asset_quality"]:
        latest = result["asset_quality"][0]
        result["latest"] = latest
        
        # 健康评分
        score = 0
        if latest.get("financial_leverage"):
            if latest["financial_leverage"] < 0.5:
                score += 30
            elif latest["financial_leverage"] < 1:
                score += 20
            else:
                score += 5
        
        if latest.get("cash_to_liability"):
            if latest["cash_to_liability"] > 50:
                score += 30
            elif latest["cash_to_liability"] > 20:
                score += 20
            else:
                score += 5
        
        if latest.get("asset_to_liability"):
            if latest["asset_to_liability"] > 1.5:
                score += 40
            elif latest["asset_to_liability"] > 1:
                score += 25
            else:
                score += 10
        
        result["health_score"] = min(100, score)
        result["health_rating"] = "优秀" if score >= 80 else ("良好" if score >= 60 else ("一般" if score >= 40 else "需关注"))
    
    return result


def analyze_cash_flow_quality(cash_flow_data: List[Dict], net_income_data: List[Dict]) -> Dict:
    """
    现金流质量分析
    
    检查经营现金流与净利润的关系
    """
    if not cash_flow_data:
        return {"error": "无现金流数据"}
    
    result = {
        "operating_vs_net_income": [],
        "free_cash_flow": [],
        "quality_indicators": {},
    }
    
    # 匹配现金流和净利润数据
    for cf in cash_flow_data[:8]:
        ocf = cf.get("operating_cash_flow")
        fcf = cf.get("free_cash_flow")
        capex = cf.get("capex")
        date = cf.get("date")
        
        # 找对应的净利润
        matching_ni = None
        for ni_data in net_income_data:
            if ni_data.get("date") == date:
                matching_ni = ni_data.get("net_income")
                break
        
        entry = {
            "date": date,
            "operating_cash_flow": ocf,
            "free_cash_flow": fcf,
        }
        
        if matching_ni and ocf and matching_ni > 0:
            ratio = ocf / matching_ni
            entry["ocf_to_ni_ratio"] = round(ratio, 2)
            
            # 质量评估
            if ratio > 1.0:
                entry["quality"] = "excellent"
                entry["quality_text"] = "经营现金流超过净利润"
            elif ratio > 0.8:
                entry["quality"] = "good"
                entry["quality_text"] = "经营现金流与净利润匹配良好"
            elif ratio > 0.5:
                entry["quality"] = "fair"
                entry["quality_text"] = "经营现金流低于净利润"
            else:
                entry["quality"] = "concerning"
                entry["quality_text"] = "经营现金流显著低于净利润，需关注"
        
        result["operating_vs_net_income"].append(entry)
        
        if fcf is not None:
            result["free_cash_flow"].append({
                "date": date,
                "free_cash_flow": fcf,
                "direction": "positive" if fcf > 0 else "negative",
            })
    
    # 整体质量评估
    excellent_count = sum(1 for e in result["operating_vs_net_income"] if e.get("quality") == "excellent")
    good_count = sum(1 for e in result["operating_vs_net_income"] if e.get("quality") == "good")
    concerning_count = sum(1 for e in result["operating_vs_net_income"] if e.get("quality") == "concerning")
    
    total = len(result["operating_vs_net_income"])
    
    if total > 0:
        excellent_ratio = excellent_count / total
        good_ratio = good_count / total
        concerning_ratio = concerning_count / total
        
        if concerning_ratio > 0.5:
            result["overall_quality"] = "concerning"
            result["overall_quality_text"] = "现金流质量需关注"
        elif excellent_ratio > 0.5:
            result["overall_quality"] = "excellent"
            result["overall_quality_text"] = "现金流质量优秀"
        elif good_ratio + excellent_ratio > 0.6:
            result["overall_quality"] = "good"
            result["overall_quality_text"] = "现金流质量良好"
        else:
            result["overall_quality"] = "fair"
            result["overall_quality_text"] = "现金流质量一般"
    
    return result


# ============ 综合财报回顾 ============

def earnings_recap(symbol: str) -> Dict:
    """
    财报回顾主函数
    
    整合所有财报分析维度
    """
    market = _detect_market(symbol)
    data = _fetch_earnings_data(symbol, market)
    
    result = {
        "symbol": symbol,
        "market": market,
        "generated_at": datetime.now().isoformat(),
        "data_source": "yfinance" if market == "us" else "AkShare",
        "warnings": data.get("warnings", []),
    }
    
    if not data.get("quarterly") and not data.get("annual"):
        result["error"] = "无法获取财报数据"
        return result
    
    # 提取数据
    quarterly = data.get("quarterly", [])
    annual = data.get("annual", [])
    balance_sheet = data.get("balance_sheet", [])
    cash_flow = data.get("cash_flow", [])
    
    if not quarterly and annual:
        quarterly = annual
    
    if not quarterly:
        result["error"] = "无季度财报数据"
        return result
    
    result["latest_quarter"] = quarterly[0] if quarterly else None
    result["data_points"] = {
        "quarterly": len(quarterly),
        "annual": len(annual),
        "balance_sheet": len(balance_sheet),
        "cash_flow": len(cash_flow),
    }
    
    # 1. 业绩达标检测
    if len(quarterly) >= 2:
        result["actual_vs_expected"] = analyze_actual_vs_expected(
            quarterly[0], 
            quarterly[1:]
        )
    else:
        result["actual_vs_expected"] = {"error": "历史数据不足"}
    
    # 2. 利润率趋势
    result["margin_analysis"] = analyze_margin_trends(quarterly)
    
    # 3. 资产负债表健康度
    if balance_sheet:
        result["balance_sheet_health"] = analyze_balance_sheet_health(balance_sheet)
    else:
        result["balance_sheet_health"] = {"error": "无资产负债表数据"}
    
    # 4. 现金流质量
    if cash_flow:
        result["cash_flow_quality"] = analyze_cash_flow_quality(
            cash_flow, 
            quarterly
        )
    else:
        result["cash_flow_quality"] = {"error": "无现金流数据"}
    
    # 综合评分
    scores = []
    if "verdict" in result.get("actual_vs_expected", {}):
        v = result["actual_vs_expected"]["verdict"]
        if v == "beat":
            scores.append(85)
        elif v == "in_line":
            scores.append(70)
        else:
            scores.append(50)
    
    if "health_rating" in result.get("balance_sheet_health", {}):
        h = result["balance_sheet_health"]["health_rating"]
        if h == "优秀":
            scores.append(100)
        elif h == "良好":
            scores.append(80)
        elif h == "一般":
            scores.append(60)
        else:
            scores.append(40)
    
    if "overall_quality" in result.get("cash_flow_quality", {}):
        q = result["cash_flow_quality"]["overall_quality"]
        if q == "excellent":
            scores.append(100)
        elif q == "good":
            scores.append(80)
        elif q == "fair":
            scores.append(60)
        else:
            scores.append(40)
    
    if scores:
        result["overall_score"] = round(sum(scores) / len(scores), 1)
        if result["overall_score"] >= 80:
            result["overall_rating"] = "优秀"
        elif result["overall_score"] >= 65:
            result["overall_rating"] = "良好"
        elif result["overall_score"] >= 50:
            result["overall_rating"] = "一般"
        else:
            result["overall_rating"] = "需关注"
    
    # 公司信息
    if data.get("info"):
        result["company"] = data["info"]
    
    # 免责声明
    result["disclaimer"] = (
        "⚠️ 本分析基于历史财报数据，不代表未来表现。"
        "股市有风险，投资需谨慎。分析结果仅供参考，不构成投资建议。"
    )
    
    return result


# ============ 格式化输出 ============

def format_recap_output(result: Dict) -> str:
    """格式化财报回顾输出"""
    if result.get("error"):
        return f"❌ {result['error']}"
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"📊 财报回顾 - {result.get('symbol', 'N/A')}")
    lines.append("=" * 60)
    lines.append(f"生成时间: {result.get('generated_at', '')[:10]}")
    
    if result.get("company"):
        lines.append(f"公司: {result['company'].get('name', 'N/A')}")
    
    # 综合评分
    if result.get("overall_score"):
        lines.append(f"\n🏆 综合评分: {result['overall_score']} ({result.get('overall_rating', '')})")
    
    # 业绩达标
    ave = result.get("actual_vs_expected", {})
    if "verdict_text" in ave:
        lines.append(f"\n📈 业绩表现: {ave['verdict_text']}")
        if ave.get("vs_consensus"):
            for metric, data in ave["vs_consensus"].items():
                emoji = "✅" if data.get("beat") else "❌"
                lines.append(f"  {emoji} {metric}: 预期 {data.get('estimate', 0):,.0f} vs 实际 {data.get('actual', 0):,.0f} ({data.get('surprise_pct', 0):+.1f}%)")
    
    # 利润率
    margins = result.get("margin_analysis", {})
    if margins.get("latest"):
        lines.append("\n📉 利润率:")
        lines.append(f"  毛利率: {margins['latest'].get('gross_margin', 'N/A')}%")
        lines.append(f"  净利率: {margins['latest'].get('net_margin', 'N/A')}%")
        lines.append(f"  营业利润率: {margins['latest'].get('operating_margin', 'N/A')}%")
    
    # 资产负债表
    bs_health = result.get("balance_sheet_health", {})
    if "health_rating" in bs_health:
        lines.append(f"\n🏦 资产负债: {bs_health['health_rating']} (评分: {bs_health.get('health_score', 'N/A')})")
        if bs_health.get("latest"):
            lines.append(f"  负债权益比: {bs_health['latest'].get('debt_to_equity', 'N/A')}")
            lines.append(f"  现金/负债: {bs_health['latest'].get('cash_to_liability', 'N/A')}%")
    
    # 现金流
    cf = result.get("cash_flow_quality", {})
    if "overall_quality_text" in cf:
        lines.append(f"\n💰 现金流: {cf['overall_quality_text']}")
    
    # 警告
    if result.get("warnings"):
        lines.append("\n⚠️ 数据警告:")
        for w in result["warnings"][:3]:
            lines.append(f"  • {w}")
    
    lines.append("\n" + "=" * 60)
    lines.append(result.get("disclaimer", ""))
    
    return "\n".join(lines)


# ============ 测试 ============

if __name__ == "__main__":
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    print(f"📊 财报回顾: {symbol}")
    print()
    
    result = earnings_recap(symbol)
    print(format_recap_output(result))
