#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业绩比较模块 - Performance Comparison
支持同比/环比/行业对比，多股票横向对比分析
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
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


def _safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """安全除法"""
    if b is None or b == 0:
        return default
    return a / b


def _format_large_number(num: float) -> str:
    """格式化大数字"""
    if num is None:
        return "N/A"
    abs_num = abs(num)
    if abs_num >= 1e12:
        return f"{num/1e12:.2f}T"
    elif abs_num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif abs_num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif abs_num >= 1e3:
        return f"{num/1e3:.2f}K"
    else:
        return f"{num:.2f}"


# ============ 数据获取 ============

def _fetch_single_stock_data(symbol: str, market: str) -> Dict:
    """获取单只股票数据"""
    result = {
        "quarterly": [],
        "info": {},
        "warnings": [],
    }
    
    if market == "us":
        result.update(_fetch_us_stock_data(symbol))
    elif market == "cn":
        result.update(_fetch_cn_stock_data(symbol))
    
    return result


def _fetch_us_stock_data(symbol: str) -> Dict:
    """获取美股数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "info": {},
        "warnings": [],
    }
    
    if find_spec("yfinance") is None:
        result["warnings"].append("yfinance 未安装")
        return result
    
    try:
        yf = importlib.import_module("yfinance")
        ticker = yf.Ticker(symbol)
        
        # 季度财务数据
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
                        "research_development": _num(row.get("Research And Development")),
                    })
        except Exception as e:
            result["warnings"].append(f"财务数据获取失败: {e}")
        
        # 基本信息
        try:
            info = ticker.info
            result["info"] = {
                "symbol": symbol,
                "name": info.get("shortName", symbol),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": _num(info.get("marketCap")),
                "pe_ratio": _num(info.get("trailingPE")),
                "forward_pe": _num(info.get("forwardPE")),
                "peg_ratio": _num(info.get("pegRatio")),
                "dividend_yield": _num(info.get("dividendYield")),
                "revenue_growth": _num(info.get("revenueGrowth")),
                "earnings_growth": _num(info.get("earningsGrowth")),
                "shares_outstanding": _num(info.get("sharesOutstanding")),
            }
        except Exception:
            pass
        
    except Exception as e:
        result["warnings"].append(f"yfinance 错误: {e}")
    
    return result


def _fetch_cn_stock_data(symbol: str) -> Dict:
    """获取A股数据"""
    from importlib.util import find_spec
    
    result = {
        "quarterly": [],
        "info": {},
        "warnings": [],
    }
    
    if find_spec("akshare") is None:
        result["warnings"].append("AkShare 未安装")
        return result
    
    result["warnings"].append("A股业绩比较需要 AkShare 支持")
    return result


# ============ 同比分析 ============

def year_over_year_analysis(quarterly_data: List[Dict]) -> List[Dict]:
    """
    同比分析 - 连续8个季度的同比增长率
    
    Returns:
        包含各指标同比变化的数据列表
    """
    if len(quarterly_data) < 5:
        return []
    
    results = []
    
    # 按日期排序（从旧到新）
    sorted_data = sorted(quarterly_data, key=lambda x: x.get("date", ""))
    
    for i in range(4, len(sorted_data)):  # 从第5个季度开始（需要4个季度前的数据做同比）
        current = sorted_data[i]
        year_ago = sorted_data[i - 4]
        
        entry = {
            "date": current.get("date"),
            "vs_year_ago_date": year_ago.get("date"),
        }
        
        # 各指标同比变化
        for metric in ["revenue", "net_income", "gross_profit", "operating_income", "eps"]:
            current_val = current.get(metric)
            year_ago_val = year_ago.get(metric)
            
            if current_val and year_ago_val and year_ago_val != 0:
                change = (current_val - year_ago_val) / abs(year_ago_val) * 100
                entry[f"{metric}_yoy"] = round(change, 2)
                entry[f"{metric}_direction"] = "up" if change > 0 else ("down" if change < 0 else "flat")
            else:
                entry[f"{metric}_yoy"] = None
        
        results.append(entry)
    
    return results


# ============ 环比分析 ============

def quarter_over_quarter_analysis(quarterly_data: List[Dict]) -> List[Dict]:
    """
    环比分析 - 连续季度的变化率
    """
    if len(quarterly_data) < 2:
        return []
    
    results = []
    
    for i in range(1, min(len(quarterly_data), 8)):
        current = quarterly_data[i - 1]
        prev = quarterly_data[i]
        
        entry = {
            "date": current.get("date"),
            "vs_prev_quarter_date": prev.get("date"),
        }
        
        for metric in ["revenue", "net_income", "gross_profit", "operating_income", "eps"]:
            current_val = current.get(metric)
            prev_val = prev.get(metric)
            
            if current_val and prev_val and prev_val != 0:
                change = (current_val - prev_val) / abs(prev_val) * 100
                entry[f"{metric}_qoq"] = round(change, 2)
                entry[f"{metric}_direction"] = "up" if change > 0 else ("down" if change < 0 else "flat")
            else:
                entry[f"{metric}_qoq"] = None
        
        results.append(entry)
    
    return results


# ============ 多股票对比 ============

def compare_stocks(symbols: List[str]) -> Dict:
    """
    多股票横向对比
    
    对比收入增长率、利润率、EPS等关键指标
    """
    results = {
        "stocks": [],
        "comparison": {},
        "generated_at": datetime.now().isoformat(),
    }
    
    for symbol in symbols:
        market = _detect_market(symbol)
        data = _fetch_single_stock_data(symbol, market)
        
        stock_result = {
            "symbol": symbol,
            "info": data.get("info", {}),
            "quarterly": data.get("quarterly", [])[:4],  # 最近4个季度
            "warnings": data.get("warnings", []),
        }
        
        # 计算汇总指标
        if data.get("quarterly"):
            q = data["quarterly"]
            
            # 最近季度
            latest = q[0]
            stock_result["latest"] = latest
            
            # 计算近4个季度平均
            if len(q) >= 4:
                avg_revenue = sum(x.get("revenue", 0) or 0 for x in q[:4]) / 4
                avg_net_income = sum(x.get("net_income", 0) or 0 for x in q[:4]) / 4
                
                stock_result["avg_quarterly_revenue"] = avg_revenue
                stock_result["avg_quarterly_net_income"] = avg_net_income
                
                # 平均毛利率
                margins = []
                for x in q[:4]:
                    if x.get("revenue") and x.get("gross_profit"):
                        margins.append(x["gross_profit"] / x["revenue"] * 100)
                if margins:
                    stock_result["avg_gross_margin"] = sum(margins) / len(margins)
                
                # 平均净利率
                net_margins = []
                for x in q[:4]:
                    if x.get("revenue") and x.get("net_income"):
                        net_margins.append(x["net_income"] / x["revenue"] * 100)
                if net_margins:
                    stock_result["avg_net_margin"] = sum(net_margins) / len(net_margins)
            
            # 增长率（如果有多期数据）
            if len(q) >= 5:
                yoy = year_over_year_analysis(q)
                if yoy:
                    stock_result["yoy_analysis"] = yoy[0]  # 最新季度同比
        
        results["stocks"].append(stock_result)
    
    # 对比分析
    if len(results["stocks"]) >= 2:
        results["comparison"] = _generate_comparison_table(results["stocks"])
    
    return results


def _generate_comparison_table(stocks: List[Dict]) -> Dict:
    """生成对比表格"""
    comparison = {
        "metrics": [],
        "rankings": {},
    }
    
    # 提取可对比的指标
    metrics_to_compare = [
        ("revenue_growth", "收入增长率", "info.revenue_growth"),
        ("earnings_growth", "盈利增长率", "info.earnings_growth"),
        ("pe_ratio", "市盈率", "info.pe_ratio"),
        ("forward_pe", "预期市盈率", "info.forward_pe"),
        ("peg_ratio", "PEG比率", "info.peg_ratio"),
        ("avg_gross_margin", "平均毛利率", "avg_quarterly_revenue"),
        ("avg_net_margin", "平均净利率", "avg_quarterly_revenue"),
    ]
    
    # 简化指标提取
    def get_metric(stock: Dict, path: str) -> Optional[float]:
        parts = path.split(".")
        val = stock
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return None
        return val if isinstance(val, (int, float)) else None
    
    # 收集各指标数据
    for metric_key, metric_name, data_path in metrics_to_compare:
        metric_data = []
        for stock in stocks:
            val = get_metric(stock, data_path)
            if val is not None:
                metric_data.append({
                    "symbol": stock["symbol"],
                    "value": val,
                })
        
        if metric_data:
            # 排序（根据指标类型）
            if metric_key in ["pe_ratio", "forward_pe", "peg_ratio"]:
                # 市盈率越低越好
                sorted_data = sorted(metric_data, key=lambda x: x["value"] if x["value"] > 0 else float("inf"))
            else:
                # 其他指标越高越好
                sorted_data = sorted(metric_data, key=lambda x: x["value"] or 0, reverse=True)
            
            comparison["metrics"].append({
                "name": metric_name,
                "key": metric_key,
                "data": sorted_data,
            })
            
            # 记录排名
            for i, item in enumerate(sorted_data):
                if item["symbol"] not in comparison["rankings"]:
                    comparison["rankings"][item["symbol"]] = []
                comparison["rankings"][item["symbol"]].append({
                    "metric": metric_name,
                    "rank": i + 1,
                    "value": item["value"],
                })
    
    # 计算综合得分
    if comparison["rankings"]:
        for symbol, ranks in comparison["rankings"].items():
            total_metrics = len(ranks)
            if total_metrics > 0:
                avg_rank = sum(r["rank"] for r in ranks) / total_metrics
                comparison["rankings"][symbol] = {
                    "ranks": ranks,
                    "avg_rank": round(avg_rank, 2),
                }
    
    return comparison


# ============ 行业对比 ============

def compare_with_industry(symbol: str, sector_peers: Optional[List[str]] = None) -> Dict:
    """
    与行业同行对比
    
    如果未提供同行列表，使用symbol的sector信息
    """
    market = _detect_market(symbol)
    data = _fetch_single_stock_data(symbol, market)
    
    result = {
        "target_stock": {
            "symbol": symbol,
            "info": data.get("info", {}),
            "quarterly": data.get("quarterly", [])[:4],
        },
        "peers": [],
        "comparison": {},
        "generated_at": datetime.now().isoformat(),
        "warnings": data.get("warnings", []),
    }
    
    # 如果有同行列表，进行对比
    if sector_peers:
        peer_data = compare_stocks(sector_peers)
        result["peers"] = peer_data.get("stocks", [])
        result["comparison"] = peer_data.get("comparison", {})
        
        # 计算target在同行中的位置
        result["position_in_peer_group"] = _calculate_peer_position(
            result["target_stock"],
            result["peers"]
        )
    elif data.get("info", {}).get("sector"):
        result["note"] = f"行业: {data['info']['sector']}。提供 peer symbols 可进行同行对比。"
    
    return result


def _calculate_peer_position(target: Dict, peers: List[Dict]) -> Dict:
    """计算目标股票在同行中的位置"""
    if not peers:
        return {"error": "无同行数据"}
    
    position = {
        "metrics_compared": 0,
        "above_peers_count": 0,
        "details": [],
    }
    
    target_info = target.get("info", {})
    
    for peer in peers:
        peer_info = peer.get("info", {})
        
        # 比较PE
        if target_info.get("pe_ratio") and peer_info.get("pe_ratio"):
            if target_info["pe_ratio"] < peer_info["pe_ratio"]:
                position["above_peers_count"] += 1
            position["metrics_compared"] += 1
            position["details"].append({
                "metric": "市盈率",
                "target": target_info["pe_ratio"],
                "peer": peer_info["pe_ratio"],
                "favor": "target" if target_info["pe_ratio"] < peer_info["pe_ratio"] else "peer",
            })
        
        # 比较收入增长
        if target_info.get("revenue_growth") and peer_info.get("revenue_growth"):
            if target_info["revenue_growth"] > peer_info["revenue_growth"]:
                position["above_peers_count"] += 1
            position["metrics_compared"] += 1
            position["details"].append({
                "metric": "收入增长",
                "target": target_info["revenue_growth"] * 100,
                "peer": peer_info["revenue_growth"] * 100,
                "favor": "target" if target_info["revenue_growth"] > peer_info["revenue_growth"] else "peer",
            })
    
    if position["metrics_compared"] > 0:
        position["percentile"] = round(position["above_peers_count"] / position["metrics_compared"] * 100, 1)
    
    return position


# ============ 主函数 ============

def compare_performance(
    symbols: List[str],
    period: str = "quarterly",
    metrics: Optional[List[str]] = None
) -> Dict:
    """
    业绩比较主函数
    
    Args:
        symbols: 股票代码列表
        period: 时间周期 ("quarterly" 或 "annual")
        metrics: 要比较的指标列表
        
    Returns:
        完整的业绩比较报告
    """
    if not symbols:
        return {"error": "请提供至少一个股票代码"}
    
    # 默认指标
    if metrics is None:
        metrics = ["revenue", "net_income", "gross_profit", "operating_income", "eps"]
    
    result = {
        "symbols": symbols,
        "period": period,
        "metrics": metrics,
        "stocks_data": [],
        "yoy_analysis": {},
        "qoq_analysis": {},
        "generated_at": datetime.now().isoformat(),
    }
    
    all_warnings = []
    
    # 获取每只股票数据
    for symbol in symbols:
        market = _detect_market(symbol)
        data = _fetch_single_stock_data(symbol, market)
        
        stock_data = {
            "symbol": symbol,
            "market": market,
            "info": data.get("info", {}),
            "quarterly": data.get("quarterly", []),
            "warnings": data.get("warnings", []),
        }
        
        all_warnings.extend(data.get("warnings", []))
        
        # 计算同比
        if len(stock_data["quarterly"]) >= 5:
            stock_data["yoy"] = year_over_year_analysis(stock_data["quarterly"])
        
        # 计算环比
        if len(stock_data["quarterly"]) >= 2:
            stock_data["qoq"] = quarter_over_quarter_analysis(stock_data["quarterly"])
        
        result["stocks_data"].append(stock_data)
    
    result["warnings"] = list(set(all_warnings))
    
    # 多股票对比
    if len(symbols) >= 2:
        result["cross_stock_comparison"] = compare_stocks(symbols).get("comparison", {})
    
    return result


# ============ 格式化输出 ============

def format_comparison_output(result: Dict) -> str:
    """格式化业绩比较输出"""
    if result.get("error"):
        return f"❌ {result['error']}"
    
    lines = []
    symbols = result.get("symbols", [])
    
    lines.append("=" * 60)
    lines.append(f"📊 业绩比较 - {', '.join(symbols)}")
    lines.append("=" * 60)
    lines.append(f"生成时间: {result.get('generated_at', '')[:10]}")
    lines.append(f"周期: {result.get('period', 'quarterly')}")
    
    # 多股票对比表格
    if result.get("cross_stock_comparison"):
        comparison = result["cross_stock_comparison"]
        
        lines.append("\n📈 关键指标对比:")
        
        for metric in comparison.get("metrics", [])[:5]:  # 最多显示5个指标
            lines.append(f"\n  {metric['name']}:")
            for item in metric["data"][:5]:  # 最多显示5个
                val = item["value"]
                if metric["key"] in ["revenue_growth", "earnings_growth"]:
                    val_str = f"{val*100:.1f}%" if val else "N/A"
                elif metric["key"] in ["pe_ratio", "forward_pe", "peg_ratio"]:
                    val_str = f"{val:.2f}" if val else "N/A"
                else:
                    val_str = f"{val:.2f}" if val else "N/A"
                lines.append(f"    {item['symbol']}: {val_str}")
    
    # 单只股票详情
    for stock in result.get("stocks_data", []):
        lines.append(f"\n{'─' * 50}")
        lines.append(f"📌 {stock['symbol']} - {stock.get('info', {}).get('name', '')}")
        lines.append(f"   行业: {stock.get('info', {}).get('industry', 'N/A')}")
        
        # 同比分析
        if stock.get("yoy") and len(stock["yoy"]) > 0:
            yoy = stock["yoy"][0]
            lines.append("\n   📅 同比变化 (vs 上年同期):")
            for metric in ["revenue", "net_income"]:
                key = f"{metric}_yoy"
                if yoy.get(key) is not None:
                    val = yoy[key]
                    emoji = "📈" if val > 0 else "📉"
                    lines.append(f"     {emoji} {metric}: {val:+.1f}%")
        
        # 环比分析
        if stock.get("qoq") and len(stock["qoq"]) > 0:
            qoq = stock["qoq"][0]
            lines.append("\n   📊 环比变化 (vs 上季度):")
            for metric in ["revenue", "net_income"]:
                key = f"{metric}_qoq"
                if qoq.get(key) is not None:
                    val = qoq[key]
                    emoji = "📈" if val > 0 else "📉"
                    lines.append(f"     {emoji} {metric}: {val:+.1f}%")
    
    # 警告
    if result.get("warnings"):
        unique_warnings = list(set(result["warnings"]))[:3]
        lines.append("\n⚠️ 数据警告:")
        for w in unique_warnings:
            lines.append(f"   • {w}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)


# ============ 测试 ============

if __name__ == "__main__":
    import sys
    
    # 默认对比股票
    default_stocks = ["AAPL", "MSFT", "GOOGL"]
    
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        symbols = default_stocks
    
    print(f"📊 业绩比较: {', '.join(symbols)}")
    print()
    
    result = compare_performance(symbols)
    print(format_comparison_output(result))
