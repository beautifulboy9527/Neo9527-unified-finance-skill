#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股特色数据源 (P2)

- 龙虎榜 (Top List): 游资动向、买卖席位
- 解禁日历 (Lockup Calendar): 限售股解禁
- 北向资金 (Northbound Flow): 沪深港通资金流向

数据源: AkShare (免费)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── 龙虎榜 ────────────────────────────────────────────────────

def fetch_top_list(date: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
    """
    获取龙虎榜数据
    
    Args:
        date: 日期 (YYYYMMDD), 默认今天
        symbol: 股票代码 (可选, 筛选特定股票)
    
    Returns:
        {success: bool, date: str, items: [{symbol, name, reason, buy_seats, sell_seats, net_buy}]}
    """
    result = {"success": False, "date": date or datetime.now().strftime("%Y%m%d"), "items": []}
    
    try:
        import akshare as ak
        import pandas as pd
        
        target_date = date or datetime.now().strftime("%Y%m%d")
        df = ak.stock_lhb_detail_em(start_date=target_date, end_date=target_date)
        
        if df is None or df.empty:
            result["message"] = f"{target_date} 无龙虎榜数据（可能非交易日）"
            return result
        
        items = []
        for _, row in df.iterrows():
            item = {
                "symbol": str(row.get("代码", "")),
                "name": str(row.get("名称", "")),
                "reason": str(row.get("上榜原因", "")),
                "close": _safe_float(row.get("收盘价")),
                "change_pct": _safe_float(row.get("涨跌幅")),
                "turnover": _safe_float(row.get("成交额")),
                "net_buy": _safe_float(row.get("买入额")) - _safe_float(row.get("卖出额")),
                "buy_seats": [],
                "sell_seats": [],
            }
            
            # 如果指定了股票代码，只返回该股票
            if symbol and item["symbol"] != symbol:
                continue
            
            items.append(item)
        
        result["success"] = True
        result["items"] = items
        result["count"] = len(items)
        
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"龙虎榜获取失败: {e}")
    
    return result


def fetch_top_list_recent(days: int = 5, symbol: Optional[str] = None) -> Dict[str, Any]:
    """获取最近 N 天龙虎榜数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        import akshare as ak
        df = ak.stock_lhb_detail_em(
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
        )
        
        if df is None or df.empty:
            return {"success": False, "items": [], "message": "近期无龙虎榜数据"}
        
        items = []
        for _, row in df.iterrows():
            item = {
                "symbol": str(row.get("代码", "")),
                "name": str(row.get("名称", "")),
                "date": str(row.get("日期", "")),
                "reason": str(row.get("上榜原因", "")),
                "net_buy": _safe_float(row.get("买入额")) - _safe_float(row.get("卖出额")),
            }
            if symbol and item["symbol"] != symbol:
                continue
            items.append(item)
        
        # 统计游资热度
        symbol_counts = {}
        for item in items:
            s = item["symbol"]
            symbol_counts[s] = symbol_counts.get(s, 0) + 1
        
        hot_stocks = sorted(symbol_counts.items(), key=lambda x: -x[1])[:10]
        
        return {
            "success": True,
            "period": f"{days}天",
            "items": items,
            "count": len(items),
            "hot_stocks": [{"symbol": s, "count": c, "name": next((i["name"] for i in items if i["symbol"] == s), "")} for s, c in hot_stocks],
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── 解禁日历 ──────────────────────────────────────────────────

def fetch_lockup_calendar(date: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    获取限售股解禁日历
    
    Args:
        date: 起始日期 (YYYYMMDD), 默认今天
        days: 查询天数, 默认30天
    
    Returns:
        {success: bool, items: [{symbol, name, unlock_date, unlock_shares, unlock_ratio, unlock_type}]}
    """
    result = {"success": False, "period": f"{days}天", "items": []}
    
    try:
        import akshare as ak
        
        start_date = date or datetime.now().strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y%m%d")
        
        df = ak.stock_restricted_release_queue_sina(symbol="")
        if df is None or df.empty:
            # Fallback: 使用股票列表逐个查询不现实，返回空结果
            result["message"] = "解禁数据暂不可用"
            return result
        
        items = []
        for _, row in df.iterrows():
            item = {
                "symbol": str(row.get("股票代码", "")),
                "name": str(row.get("股票名称", "")),
                "unlock_date": str(row.get("解禁日期", "")),
                "unlock_shares": _safe_float(row.get("解禁数量")),
                "unlock_ratio": _safe_float(row.get("解禁比例")),
                "unlock_type": str(row.get("解禁类型", "")),
            }
            items.append(item)
        
        result["success"] = True
        result["items"] = sorted(items, key=lambda x: x.get("unlock_date", ""))
        result["count"] = len(items)
        
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"解禁日历获取失败: {e}")
    
    return result


def fetch_lockup_for_symbol(symbol: str) -> Dict[str, Any]:
    """获取特定股票的解禁信息"""
    try:
        import akshare as ak
        df = ak.stock_restricted_release_queue_sina(symbol=symbol)
        if df is None or df.empty:
            return {"success": False, "symbol": symbol, "message": "该股票无解禁数据"}
        
        items = []
        for _, row in df.iterrows():
            items.append({
                "unlock_date": str(row.get("解禁日期", "")),
                "unlock_shares": _safe_float(row.get("解禁数量")),
                "unlock_type": str(row.get("解禁类型", "")),
            })
        
        return {"success": True, "symbol": symbol, "items": items, "count": len(items)}
        
    except Exception as e:
        return {"success": False, "symbol": symbol, "error": str(e)}


# ── 北向资金 ──────────────────────────────────────────────────

def fetch_northbound_flow(days: int = 10) -> Dict[str, Any]:
    """
    获取北向资金流向（沪深港通）
    
    Returns:
        {success: bool, items: [{date, sh_net, sz_net, total_net}]}
    """
    result = {"success": False, "items": []}
    
    try:
        import akshare as ak
        
        # 沪股通+深股通 净流入
        df = ak.stock_hsgt_north_net_flow_in_em(symbol="北向")
        if df is None or df.empty:
            result["message"] = "北向资金数据暂不可用"
            return result
        
        # 最近 N 天
        df = df.tail(days)
        
        items = []
        for _, row in df.iterrows():
            item = {
                "date": str(row.get("日期", "")),
                "net_flow": _safe_float(row.get("当日净流入")),
                "balance": _safe_float(row.get("当日余额")),
            }
            items.append(item)
        
        # 统计
        net_flows = [i["net_flow"] for i in items if i["net_flow"] is not None]
        total_net = sum(net_flows) if net_flows else 0
        avg_net = total_net / len(net_flows) if net_flows else 0
        
        result["success"] = True
        result["items"] = items
        result["count"] = len(items)
        result["summary"] = {
            "total_net_flow": round(total_net, 2),
            "avg_daily_net": round(avg_net, 2),
            "direction": "净流入" if total_net > 0 else "净流出",
        }
        
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"北向资金获取失败: {e}")
    
    return result


def fetch_northbound_top_stocks(date: Optional[str] = None) -> Dict[str, Any]:
    """获取北向资金十大成交股"""
    result = {"success": False, "items": []}
    
    try:
        import akshare as ak
        
        target_date = date or datetime.now().strftime("%Y%m%d")
        
        # 沪股通十大
        try:
            df_sh = ak.stock_hsgt_hold_stock_em(market="北向", indicator="今日排行")
            if df_sh is not None and not df_sh.empty:
                for _, row in df_sh.head(10).iterrows():
                    result["items"].append({
                        "symbol": str(row.get("股票代码", "")),
                        "name": str(row.get("股票名称", "")),
                        "close": _safe_float(row.get("收盘价")),
                        "change_pct": _safe_float(row.get("涨跌幅")),
                        "hold_shares": _safe_float(row.get("持股数量")),
                        "hold_change": _safe_float(row.get("持股变化")),
                    })
        except Exception:
            pass
        
        result["success"] = len(result["items"]) > 0
        result["count"] = len(result["items"])
        
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"北向持仓获取失败: {e}")
    
    return result


# ── 辅助函数 ──────────────────────────────────────────────────

def _safe_float(value) -> Optional[float]:
    """安全转换为 float"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


__all__ = [
    "fetch_top_list", "fetch_top_list_recent",
    "fetch_lockup_calendar", "fetch_lockup_for_symbol",
    "fetch_northbound_flow", "fetch_northbound_top_stocks",
]
