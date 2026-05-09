#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Technical Analysis Module - Phase 1
包含: VWAP, 斐波那契, 缠论中枢, K线形态, 趋势线, ADX
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import importlib

# ============ 辅助函数 ============

def _num(value: Any) -> Optional[float]:
    """安全转换为数值"""
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "None", "nan", "NaN", "暂无数据"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _pandas_module():
    """延迟导入 pandas"""
    try:
        import pandas as pd
        return pd
    except ImportError:
        return None


def _numpy_module():
    """延迟导入 numpy"""
    try:
        import numpy as np
        return np
    except ImportError:
        return None


# ============ VWAP 指标 ============

def calculate_vwap(hist: Any, open_col: str = "开盘", high_col: str = "最高", 
                   low_col: str = "最低", close_col: str = "收盘", volume_col: str = "成交量") -> Dict:
    """
    计算成交量加权平均价 (VWAP)
    
    VWAP = Σ(典型价格 × 成交量) / Σ成交量
    典型价格 = (最高 + 最低 + 收盘) / 3
    
    Returns:
        {
            "vwap": float,           # 当前VWAP
            "vwap_series": list,     # VWAP序列
            "position": str,         # 价格相对VWAP位置
            "interpretation": str    # 解读
        }
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        # 标准化列名
        df = hist.copy()
        col_map = {}
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in [open_col, "开盘", "open", "Open"]:
                col_map[col] = "open"
            elif col_str in [high_col, "最高", "high", "High"]:
                col_map[col] = "high"
            elif col_str in [low_col, "最低", "low", "Low"]:
                col_map[col] = "low"
            elif col_str in [close_col, "收盘", "close", "Close"]:
                col_map[col] = "close"
            elif col_str in [volume_col, "成交量", "volume", "Volume"]:
                col_map[col] = "volume"
        
        df = df.rename(columns=col_map)
        
        if not all(col in df.columns for col in ["high", "low", "close", "volume"]):
            return {"error": "缺少必要的K线字段"}
        
        # 转换数值
        for col in ["high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # 计算典型价格
        df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
        
        # 计算VWAP (累积方法)
        df["cumulative_tp_vol"] = (df["typical_price"] * df["volume"]).cumsum()
        df["cumulative_vol"] = df["volume"].cumsum()
        df["vwap"] = df["cumulative_tp_vol"] / df["cumulative_vol"]
        
        vwap_series = df["vwap"].tolist()
        current_vwap = float(df["vwap"].iloc[-1])
        current_price = float(df["close"].iloc[-1])
        
        # 判断位置
        if current_price > current_vwap * 1.01:
            position = "价格位于VWAP上方"
            interpretation = "多方占优，日内可能有支撑"
        elif current_price < current_vwap * 0.99:
            position = "价格位于VWAP下方"
            interpretation = "空方占优，日内可能有压力"
        else:
            position = "价格围绕VWAP波动"
            interpretation = "多空均衡，等待方向突破"
        
        return {
            "vwap": round(current_vwap, 2),
            "vwap_series": [round(v, 2) for v in vwap_series],
            "position": position,
            "interpretation": interpretation,
            "distance_pct": round((current_price / current_vwap - 1) * 100, 2) if current_vwap else None,
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ 斐波那契回撤/扩展 ============

def calculate_fibonacci_retracements(hist: Any, lookback: int = 60) -> Dict:
    """
    计算斐波那契回撤位
    
    关键回撤位: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
    
    Returns:
        {
            "swing_high": float,
            "swing_low": float,
            "retracements": [
                {"level": 0.236, "price": float, "type": "支撑/压力"},
                ...
            ],
            "current_position": str,
            "interpretation": str
        }
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        df = hist.tail(lookback).copy()
        
        # 标准化列名
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["收盘", "close", "Close"]:
                close_col = col
                break
        else:
            close_col = df.columns[-1]
        
        closes = pd.to_numeric(df[close_col], errors="coerce").dropna()
        if len(closes) < 20:
            return {"error": "数据不足，无法计算斐波那契回撤"}
        
        # 找到最近波段的高点和低点
        high_idx = closes.idxmax()
        low_idx = closes.idxmin()
        
        # 确保高低点顺序正确
        if high_idx > low_idx:
            swing_high = float(closes.max())
            swing_low = float(closes.min())
            trend = "上涨波段"
        else:
            swing_high = float(closes.max())
            swing_low = float(closes.min())
            trend = "下跌波段"
        
        diff = swing_high - swing_low
        
        # 斐波那契回撤位
        fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        retracements = []
        
        current_price = float(closes.iloc[-1])
        
        for level in fib_levels:
            if swing_high > swing_low:
                # 上涨波段：从低到高回撤
                price = swing_low + diff * level
                if level < 0.5:
                    fib_type = "支撑"
                else:
                    fib_type = "压力"
            else:
                # 下跌波段：从高到低回撤
                price = swing_high + diff * (1 - level)
                if level < 0.5:
                    fib_type = "压力"
                else:
                    fib_type = "支撑"
            
            # 判断当前价格与该位置的关系
            if abs(current_price - price) / price < 0.02:
                near_price = True
            else:
                near_price = False
            
            retracements.append({
                "level": level,
                "label": f"{int(level * 100)}%" if level in [0, 0.5, 1.0] else f"{level:.1%}",
                "price": round(price, 2),
                "type": fib_type,
                "near_current": near_price,
            })
        
        # 判断当前价格位置
        if current_price > swing_high * 0.786:
            position = "处于强势区域"
        elif current_price > swing_high * 0.5:
            position = "处于中间区域"
        else:
            position = "处于弱势区域"
        
        # 生成解读
        nearest_support = None
        nearest_resistance = None
        for retr in retracements:
            if retr["type"] == "支撑" and retr["price"] < current_price:
                if nearest_support is None or retr["price"] > nearest_support["price"]:
                    nearest_support = retr
            elif retr["type"] == "压力" and retr["price"] > current_price:
                if nearest_resistance is None or retr["price"] < nearest_resistance["price"]:
                    nearest_resistance = retr
        
        interpretation_parts = [f"基于{lookback}日波段（{trend}）计算"]
        if nearest_support:
            interpretation_parts.append(f"最近支撑位：{nearest_support['label']} ({nearest_support['price']})")
        if nearest_resistance:
            interpretation_parts.append(f"最近压力位：{nearest_resistance['label']} ({nearest_resistance['price']})")
        
        return {
            "swing_high": round(swing_high, 2),
            "swing_low": round(swing_low, 2),
            "trend": trend,
            "lookback_days": lookback,
            "retracements": retracements,
            "current_position": position,
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance,
            "interpretation": "，".join(interpretation_parts),
        }
        
    except Exception as e:
        return {"error": str(e)}


def calculate_fibonacci_extensions(hist: Any, lookback: int = 120) -> Dict:
    """
    计算斐波那契扩展位（用于预测目标位）
    
    关键扩展位: 61.8%, 100%, 161.8%, 261.8%, 423.6%
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        df = hist.tail(lookback).copy()
        
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["收盘", "close", "Close"]:
                close_col = col
                break
        else:
            close_col = df.columns[-1]
        
        closes = pd.to_numeric(df[close_col], errors="coerce").dropna()
        if len(closes) < 30:
            return {"error": "数据不足"}
        
        # 找最近的高低点
        high_idx = closes.idxmax()
        low_idx = closes.idxmin()
        
        if high_idx > low_idx:
            swing_low = float(closes.min())
            swing_high = float(closes.max())
            direction = "上涨"
        else:
            swing_low = float(closes.min())
            swing_high = float(closes.max())
            direction = "下跌"
        
        diff = swing_high - swing_low
        current_price = float(closes.iloc[-1])
        
        # 扩展位计算
        extensions = []
        extension_levels = [0.618, 1.0, 1.618, 2.618, 4.236]
        labels = ["61.8%", "100%", "161.8%", "261.8%", "423.6%"]
        
        for level, label in zip(extension_levels, labels):
            if direction == "上涨":
                price = swing_high + diff * level
                ext_type = "目标位"
            else:
                price = swing_low - diff * level
                ext_type = "目标位"
            
            distance = (price / current_price - 1) * 100 if current_price else None
            
            extensions.append({
                "level": level,
                "label": label,
                "price": round(price, 2),
                "type": ext_type,
                "upside_pct": round(distance, 2) if distance and distance > 0 else None,
                "downside_pct": round(abs(distance), 2) if distance and distance < 0 else None,
            })
        
        return {
            "swing_low": round(swing_low, 2),
            "swing_high": round(swing_high, 2),
            "direction": direction,
            "extensions": extensions,
            "interpretation": f"基于{direction}波段测算的目标扩展位",
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ 缠论中枢/笔段 ============

def calculate_chan_segments(hist: Any, min_bars: int = 5) -> Dict:
    """
    缠中说禅笔段识别（简化版）
    
    笔：至少5根连续K线，顶底交替
    笔识别后可以进一步计算中枢
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        df = hist.tail(100).copy()
        
        # 标准化列
        cols = {}
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["最高", "high", "High"]:
                cols[col] = "high"
            elif col_str in ["最低", "low", "Low"]:
                cols[col] = "low"
            elif col_str in ["收盘", "close", "Close"]:
                cols[col] = "close"
        df = df.rename(columns=cols)
        
        if not all(c in df.columns for c in ["high", "low", "close"]):
            return {"error": "缺少必要的K线字段"}
        
        for col in ["high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # 找出顶底分型
        tops, bottoms = [], []
        
        for i in range(1, len(df) - 1):
            # 顶分型
            if (df["high"].iloc[i] > df["high"].iloc[i-1] and 
                df["high"].iloc[i] > df["high"].iloc[i+1]):
                tops.append((i, float(df["high"].iloc[i])))
            
            # 底分型
            if (df["low"].iloc[i] < df["low"].iloc[i-1] and 
                df["low"].iloc[i] < df["low"].iloc[i+1]):
                bottoms.append((i, float(df["low"].iloc[i])))
        
        # 合并相近的顶底（过滤噪音）
        def merge_nearby(points, tolerance=0.02):
            if not points:
                return []
            merged = [points[0]]
            for point in points[1:]:
                if abs(point[1] - merged[-1][1]) / merged[-1][1] <= tolerance:
                    # 保留更高/低的点
                    if point[1] > merged[-1][1]:
                        merged[-1] = point
                else:
                    merged.append(point)
            return merged
        
        tops = merge_nearby(tops)
        bottoms = merge_nearby(bottoms)
        
        # 生成笔段
        segments = []
        all_points = sorted(tops + bottoms, key=lambda x: x[0])
        
        # 过滤短于min_bars的笔
        prev_type = None
        for idx, price in all_points:
            if not segments:
                segments.append({"type": "start", "price": price, "bars": 0})
                prev_type = "top" if (idx, price) in tops else "bottom"
                continue
            
            last = segments[-1]
            bars = idx - last.get("end_idx", idx)
            
            if bars >= min_bars:
                # 确定笔的方向
                if price > last["price"] and prev_type == "bottom":
                    seg_type = "上涨笔"
                elif price < last["price"] and prev_type == "top":
                    seg_type = "下跌笔"
                else:
                    continue
                
                segments.append({
                    "type": seg_type,
                    "start_price": round(last["price"], 2),
                    "end_price": round(price, 2),
                    "start_idx": last.get("end_idx", 0),
                    "end_idx": idx,
                    "bars": bars,
                    "change_pct": round((price / last["price"] - 1) * 100, 2),
                })
                prev_type = "top" if seg_type == "上涨笔" else "bottom"
        
        # 计算中枢（简化版：取重叠区间）
        centers = []
        if len(segments) >= 3:
            for i in range(len(segments) - 2):
                segs = segments[i:i+3]
                highs = [s["end_price"] for s in segs if "上涨" in s["type"]]
                lows = [s["end_price"] for s in segs if "下跌" in s["type"]]
                
                if highs and lows:
                    center_high = max(highs)
                    center_low = min(lows)
                    if center_high > center_low:
                        center_mid = (center_high + center_low) / 2
                        centers.append({
                            "range": f"{round(center_low, 2)} - {round(center_high, 2)}",
                            "mid": round(center_mid, 2),
                            "width_pct": round((center_high / center_low - 1) * 100, 2),
                            "start_seg": i,
                            "end_seg": i + 2,
                        })
        
        # 当前状态
        current_price = float(df["close"].iloc[-1])
        if centers:
            latest_center = centers[-1]
            center_mid = latest_center["mid"]
            if current_price > center_mid * 1.01:
                position = "价格位于中枢上方（强势）"
            elif current_price < center_mid * 0.99:
                position = "价格位于中枢下方（弱势）"
            else:
                position = "价格位于中枢区间内"
        else:
            position = "尚未形成有效中枢"
        
        return {
            "segments_count": len(segments),
            "recent_segments": segments[-5:] if segments else [],
            "centers": centers[-3:] if centers else [],
            "current_position": position,
            "interpretation": f"识别到{len(segments)}个笔段，{len(centers)}个中枢" if segments else "笔段数据不足",
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ K线形态识别 ============

def identify_candlestick_patterns(hist: Any) -> Dict:
    """
    识别常见K线形态
    
    支持:
    - 锤子线 (Hammer)
    - 吞没形态 (Engulfing)
    - 十字星 (Doji)
    - 早晨之星 (Morning Star)
    - 黄昏之星 (Evening Star)
    - 射击之星 (Shooting Star)
    - 纺锤线 (Spinning Top)
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        df = hist.tail(10).copy()
        
        # 标准化列
        cols = {}
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["开盘", "open", "Open"]:
                cols[col] = "open"
            elif col_str in ["最高", "high", "High"]:
                cols[col] = "high"
            elif col_str in ["最低", "low", "Low"]:
                cols[col] = "low"
            elif col_str in ["收盘", "close", "Close"]:
                cols[col] = "close"
        df = df.rename(columns=cols)
        
        if not all(c in df.columns for c in ["open", "high", "low", "close"]):
            return {"error": "缺少必要的K线字段"}
        
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        patterns_found = []
        
        # 最后一根K线分析
        last = df.iloc[-1]
        body_size = abs(last["close"] - last["open"])
        upper_shadow = last["high"] - max(last["open"], last["close"])
        lower_shadow = min(last["open"], last["close"]) - last["low"]
        total_range = last["high"] - last["low"]
        
        is_bullish = last["close"] > last["open"]
        is_bearish = last["close"] < last["open"]
        
        # 锤子线 (Hammer) - 下跌趋势末端的反转信号
        if len(df) >= 2 and body_size > 0 and total_range > 0:
            prev_trend_down = df["close"].iloc[-2] < df["close"].iloc[-3] if len(df) >= 3 else True
            if (lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5 and prev_trend_down):
                patterns_found.append({
                    "name": "锤子线",
                    "type": "看涨反转",
                    "strength": "中等",
                    "description": "下影线较长，上影线极短，出现在下跌趋势末端，是潜在的底部反转信号",
                    "action": "观察是否形成早晨之星等确认形态",
                })
        
        # 射击之星 (Shooting Star) - 上涨趋势末端的反转信号
        if len(df) >= 2 and body_size > 0 and total_range > 0:
            prev_trend_up = df["close"].iloc[-2] > df["close"].iloc[-3] if len(df) >= 3 else False
            if (upper_shadow > body_size * 2 and lower_shadow < body_size * 0.5 and prev_trend_up):
                patterns_found.append({
                    "name": "射击之星",
                    "type": "看跌反转",
                    "strength": "中等",
                    "description": "上影线较长，下影线极短，出现在上涨趋势末端，是潜在的顶部反转信号",
                    "action": "观察是否形成黄昏之星等确认形态",
                })
        
        # 十字星 (Doji)
        if body_size < total_range * 0.1 and total_range > 0:
            patterns_found.append({
                "name": "十字星",
                "type": "中性/犹豫",
                "strength": "需确认",
                "description": "开盘价与收盘价接近，表示多空力量暂时均衡，等待方向突破",
                "action": "等待后续K线确认趋势",
            })
        
        # 吞没形态 (Engulfing)
        if len(df) >= 2 and body_size > 0:
            prev = df.iloc[-2]
            prev_body = abs(prev["close"] - prev["open"])
            
            # 看涨吞没
            if (prev["close"] < prev["open"] and is_bullish and
                last["close"] > prev["open"] and last["open"] < prev["close"]):
                patterns_found.append({
                    "name": "看涨吞没",
                    "type": "看涨反转",
                    "strength": "较强",
                    "description": "阴线后出现阳线完全吞没前一根阴线，表示买盘强势，可能反转下跌趋势",
                    "action": "等待量能确认",
                })
            
            # 看跌吞没
            elif (prev["close"] > prev["open"] and is_bearish and
                  last["close"] < prev["open"] and last["open"] > prev["close"]):
                patterns_found.append({
                    "name": "看跌吞没",
                    "type": "看跌反转",
                    "strength": "较强",
                    "description": "阳线后出现阴线完全吞没前一根阳线，表示卖盘强势，可能反转上涨趋势",
                    "action": "注意获利了结",
                })
        
        # 早晨之星 (Morning Star) - 三日形态
        if len(df) >= 3:
            first, second, third = df.iloc[-3], df.iloc[-2], df.iloc[-1]
            first_body = abs(first["close"] - first["open"])
            second_body = abs(second["close"] - second["open"])
            third_body = abs(third["close"] - third["open"])
            
            if (first["close"] < first["open"] and  # 第一天：下跌
                second_body < first_body * 0.5 and   # 第二天：星体
                third["close"] > third["open"] and    # 第三天：上涨
                third["close"] > (first["open"] + first["close"]) / 2):  # 收盘高于第一天中点
                patterns_found.append({
                    "name": "早晨之星",
                    "type": "强烈看涨反转",
                    "strength": "强",
                    "description": "三K线组合：阴线-星体-阳线，是经典的底部反转信号",
                    "action": "可考虑分批建仓",
                })
        
        # 黄昏之星 (Evening Star) - 三日形态
        if len(df) >= 3:
            first, second, third = df.iloc[-3], df.iloc[-2], df.iloc[-1]
            first_body = abs(first["close"] - first["open"])
            second_body = abs(second["close"] - second["open"])
            third_body = abs(third["close"] - third["open"])
            
            if (first["close"] > first["open"] and   # 第一天：上涨
                second_body < first_body * 0.5 and   # 第二天：星体
                third["close"] < third["open"] and    # 第三天：下跌
                third["close"] < (first["open"] + first["close"]) / 2):  # 收盘低于第一天中点
                patterns_found.append({
                    "name": "黄昏之星",
                    "type": "强烈看跌反转",
                    "strength": "强",
                    "description": "三K线组合：阳线-星体-阴线，是经典的顶部反转信号",
                    "action": "注意风险控制",
                })
        
        # 纺锤线 (Spinning Top)
        if body_size < total_range * 0.3 and (upper_shadow > body_size and lower_shadow > body_size):
            patterns_found.append({
                "name": "纺锤线",
                "type": "中性",
                "strength": "弱",
                "description": "上下影线较长，实体较小，表示市场犹豫不决，可能预示趋势反转",
                "action": "等待确认信号",
            })
        
        if not patterns_found:
            return {
                "patterns": [],
                "interpretation": "近期未识别出经典K线形态",
            }
        
        # 按强度排序
        strength_order = {"强": 0, "较强": 1, "中等": 2, "弱": 3, "需确认": 4}
        patterns_found.sort(key=lambda x: strength_order.get(x["strength"], 5))
        
        return {
            "patterns": patterns_found,
            "dominant_pattern": patterns_found[0] if patterns_found else None,
            "interpretation": f"识别到{len(patterns_found)}个K线形态，最显著的是{patterns_found[0]['name'] if patterns_found else '无'}",
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ 趋势线识别 ============

def identify_trendlines(hist: Any, lookback: int = 60) -> Dict:
    """
    自动识别趋势线
    
    识别上升趋势线（连接更多低点）
    识别下降趋势线（连接更多高点）
    """
    pd = _pandas_module()
    np = _numpy_module()
    
    if pd is None or np is None:
        return {"error": "需要 pandas 和 numpy"}
    
    try:
        df = hist.tail(lookback).copy()
        
        # 标准化列
        cols = {}
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["最高", "high", "High"]:
                cols[col] = "high"
            elif col_str in ["最低", "low", "Low"]:
                cols[col] = "low"
            elif col_str in ["收盘", "close", "Close"]:
                cols[col] = "close"
        df = df.rename(columns=cols)
        
        if not all(c in df.columns for c in ["high", "low", "close"]):
            return {"error": "缺少必要的K线字段"}
        
        for col in ["high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        closes = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        
        # 找局部极值点
        def find_peaks(values, order=3):
            peaks = []
            for i in range(order, len(values) - order):
                if values[i] == max(values[i-order:i+order+1]):
                    peaks.append((i, values[i]))
            return peaks
        
        def find_valleys(values, order=3):
            valleys = []
            for i in range(order, len(values) - order):
                if values[i] == min(values[i-order:i+order+1]):
                    valleys.append((i, values[i]))
            return valleys
        
        high_peaks = find_peaks(highs)
        low_valleys = find_valleys(lows)
        
        trendlines = []
        
        # 上升趋势线（连接谷底）
        if len(low_valleys) >= 2:
            # 选择最近的几个谷底拟合趋势线
            recent_valleys = low_valleys[-4:] if len(low_valleys) >= 4 else low_valleys
            x = np.array([v[0] for v in recent_valleys])
            y = np.array([v[1] for v in recent_valleys])
            
            # 线性回归
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            intercept = coeffs[1]
            
            # 计算拟合优度
            y_pred = np.polyval(coeffs, x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            current_idx = len(df) - 1
            current_trendline_value = slope * current_idx + intercept
            current_price = closes[-1]
            
            if slope > 0 and r_squared > 0.7:
                # 价格在趋势线上方
                if current_price > current_trendline_value:
                    trend_status = "价格位于趋势线上方（强势）"
                else:
                    trend_status = "价格跌破趋势线（警惕）"
                
                trendlines.append({
                    "type": "上升趋势线",
                    "direction": "上涨",
                    "slope": round(slope, 4),
                    "r_squared": round(r_squared, 3),
                    "current_value": round(current_trendline_value, 2),
                    "price_vs_trendline": round((current_price / current_trendline_value - 1) * 100, 2),
                    "status": trend_status,
                    "points_count": len(recent_valleys),
                })
        
        # 下降趋势线（连接峰值）
        if len(high_peaks) >= 2:
            recent_peaks = high_peaks[-4:] if len(high_peaks) >= 4 else high_peaks
            x = np.array([p[0] for p in recent_peaks])
            y = np.array([p[1] for p in recent_peaks])
            
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            intercept = coeffs[1]
            
            y_pred = np.polyval(coeffs, x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            current_idx = len(df) - 1
            current_trendline_value = slope * current_idx + intercept
            current_price = closes[-1]
            
            if slope < 0 and r_squared > 0.7:
                if current_price < current_trendline_value:
                    trend_status = "价格位于趋势线下方（弱势）"
                else:
                    trend_status = "价格突破趋势线（关注）"
                
                trendlines.append({
                    "type": "下降趋势线",
                    "direction": "下跌",
                    "slope": round(slope, 4),
                    "r_squared": round(r_squared, 3),
                    "current_value": round(current_trendline_value, 2),
                    "price_vs_trendline": round((current_price / current_trendline_value - 1) * 100, 2),
                    "status": trend_status,
                    "points_count": len(recent_peaks),
                })
        
        if not trendlines:
            return {
                "trendlines": [],
                "interpretation": "未识别出有效的趋势线（R² > 0.7）",
            }
        
        return {
            "trendlines": trendlines,
            "interpretation": f"识别到{len(trendlines)}条趋势线",
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ ADX 指标 ============

def calculate_adx(hist: Any, period: int = 14) -> Dict:
    """
    计算平均趋向指数 (ADX)
    
    ADX > 25: 趋势明显
    ADX < 20: 趋势弱/盘整
    +DI > -DI: 多头趋势
    -DI > +DI: 空头趋势
    """
    pd = _pandas_module()
    if pd is None:
        return {"error": "pandas 未安装"}
    
    try:
        df = hist.tail(100).copy()
        
        # 标准化列
        cols = {}
        for col in df.columns:
            col_str = str(col).strip()
            if col_str in ["最高", "high", "High"]:
                cols[col] = "high"
            elif col_str in ["最低", "low", "Low"]:
                cols[col] = "low"
            elif col_str in ["收盘", "close", "Close"]:
                cols[col] = "close"
        df = df.rename(columns=cols)
        
        if not all(c in df.columns for c in ["high", "low", "close"]):
            return {"error": "缺少必要的K线字段"}
        
        for col in ["high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        if len(df) < period + 1:
            return {"error": f"数据不足{period + 1}根K线"}
        
        # 计算 True Range 和 Directional Movement
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        prev_high = high.shift(1)
        prev_low = low.shift(1)
        prev_close = close.shift(1)
        
        # +DM 和 -DM
        up_move = high - prev_high
        down_move = prev_low - low
        
        plus_dm = ((up_move > down_move) & (up_move > 0)) * up_move
        minus_dm = ((down_move > up_move) & (down_move > 0)) * down_move
        
        # True Range
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 平滑
        atr = tr.rolling(period).mean()
        plus_dm_smooth = plus_dm.rolling(period).mean()
        minus_dm_smooth = minus_dm.rolling(period).mean()
        
        # +DI 和 -DI
        plus_di = 100 * (plus_dm_smooth / atr)
        minus_di = 100 * (minus_dm_smooth / atr)
        
        # DX
        di_sum = plus_di + minus_di
        dx = 100 * (plus_di - minus_di).abs() / di_sum
        
        # ADX
        adx = dx.rolling(period).mean()
        
        current_adx = float(adx.iloc[-1])
        current_plus_di = float(plus_di.iloc[-1])
        current_minus_di = float(minus_di.iloc[-1])
        
        # 趋势判断
        if current_adx > 25:
            if current_plus_di > current_minus_di:
                trend = "明确上升趋势"
            else:
                trend = "明确下降趋势"
        elif current_adx < 20:
            trend = "趋势不明显（盘整）"
        else:
            if current_plus_di > current_minus_di:
                trend = "趋势转强（偏多）"
            else:
                trend = "趋势转强（偏空）"
        
        return {
            "adx": round(current_adx, 2),
            "plus_di": round(current_plus_di, 2),
            "minus_di": round(current_minus_di, 2),
            "trend": trend,
            "trend_strength": "强" if current_adx > 30 else "中" if current_adx > 20 else "弱",
            "direction": "多头" if current_plus_di > current_minus_di else "空头",
            "interpretation": f"ADX={current_adx:.1f}，{'趋势明显' if current_adx > 25 else '趋势较弱'}，当前为{trend}",
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============ 综合技术分析 ============

def enhanced_technical_analysis(hist: Any, symbol: str = "", lookback: int = 100) -> Dict:
    """
    综合技术分析 - 整合所有增强指标
    """
    result = {
        "symbol": symbol,
        "lookback": lookback,
        "indicators": {},
        "summary": {},
    }
    
    # VWAP
    vwap_result = calculate_vwap(hist)
    if "error" not in vwap_result:
        result["indicators"]["vwap"] = vwap_result
    
    # 斐波那契回撤
    fib_result = calculate_fibonacci_retracements(hist, lookback=60)
    if "error" not in fib_result:
        result["indicators"]["fibonacci_retracements"] = fib_result
    
    # 斐波那契扩展
    fib_ext_result = calculate_fibonacci_extensions(hist, lookback=120)
    if "error" not in fib_ext_result:
        result["indicators"]["fibonacci_extensions"] = fib_ext_result
    
    # 缠论中枢
    chan_result = calculate_chan_segments(hist)
    if "error" not in chan_result:
        result["indicators"]["chan_analysis"] = chan_result
    
    # K线形态
    candle_result = identify_candlestick_patterns(hist)
    if "error" not in candle_result:
        result["indicators"]["candlestick_patterns"] = candle_result
    
    # 趋势线
    trendline_result = identify_trendlines(hist)
    if "error" not in trendline_result:
        result["indicators"]["trendlines"] = trendline_result
    
    # ADX
    adx_result = calculate_adx(hist)
    if "error" not in adx_result:
        result["indicators"]["adx"] = adx_result
    
    # 生成综合解读
    signals = []
    
    # VWAP信号
    if "vwap" in result["indicators"]:
        vwap_pos = result["indicators"]["vwap"].get("position", "")
        if "上方" in vwap_pos:
            signals.append(("VWAP", "看多", "价格位于VWAP上方"))
        elif "下方" in vwap_pos:
            signals.append(("VWAP", "看空", "价格位于VWAP下方"))
    
    # ADX信号
    if "adx" in result["indicators"]:
        adx_trend = result["indicators"]["adx"].get("trend", "")
        signals.append(("ADX", "趋势", adx_trend))
    
    # K线形态信号
    if "candlestick_patterns" in result["indicators"]:
        patterns = result["indicators"]["candlestick_patterns"].get("patterns", [])
        if patterns:
            dominant = patterns[0]
            if "看涨" in dominant.get("type", ""):
                signals.append(("K线形态", "看多", f"出现{dominant['name']}"))
            elif "看跌" in dominant.get("type", ""):
                signals.append(("K线形态", "看空", f"出现{dominant['name']}"))
    
    # 趋势线信号
    if "trendlines" in result["indicators"]:
        lines = result["indicators"]["trendlines"].get("trendlines", [])
        for line in lines:
            status = line.get("status", "")
            if "跌破" in status or "弱势" in status:
                signals.append(("趋势线", "看空", status))
            elif "突破" in status or "强势" in status:
                signals.append(("趋势线", "看多", status))
    
    result["summary"]["signals"] = signals
    result["summary"]["signal_count"] = len(signals)
    result["summary"]["bullish_count"] = sum(1 for s in signals if "看多" in s[1])
    result["summary"]["bearish_count"] = sum(1 for s in signals if "看空" in s[1])
    
    # 综合判断
    bullish = result["summary"]["bullish_count"]
    bearish = result["summary"]["bearish_count"]
    
    if bullish > bearish:
        result["summary"]["overall_bias"] = "偏多"
    elif bearish > bullish:
        result["summary"]["overall_bias"] = "偏空"
    else:
        result["summary"]["overall_bias"] = "中性"
    
    return result


# ============ CLI 测试 ============

if __name__ == "__main__":
    import sys
    
    pd = _pandas_module()
    if pd is None:
        print("❌ 需要安装 pandas: pip install pandas")
        sys.exit(1)
    
    # 模拟测试数据
    print("=" * 60)
    print("Enhanced Technical Analysis 测试")
    print("=" * 60)
    
    # 生成模拟K线数据
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    import numpy as np
    np.random.seed(42)
    
    base_price = 100
    prices = base_price + np.cumsum(np.random.randn(100) * 2)
    
    test_data = pd.DataFrame({
        "日期": dates,
        "开盘": prices + np.random.randn(100) * 0.5,
        "最高": prices + np.abs(np.random.randn(100) * 1.5),
        "最低": prices - np.abs(np.random.randn(100) * 1.5),
        "收盘": prices,
        "成交量": np.random.randint(1000000, 10000000, 100),
    })
    
    # 测试各项指标
    print("\n📊 VWAP 指标:")
    vwap = calculate_vwap(test_data)
    if "error" not in vwap:
        print(f"  VWAP: {vwap['vwap']}")
        print(f"  位置: {vwap['position']}")
    else:
        print(f"  错误: {vwap['error']}")
    
    print("\n📊 斐波那契回撤:")
    fib = calculate_fibonacci_retracements(test_data)
    if "error" not in fib:
        print(f"  波段: {fib['swing_low']} - {fib['swing_high']}")
        print(f"  当前: {fib['current_position']}")
    else:
        print(f"  错误: {fib['error']}")
    
    print("\n📊 K线形态:")
    candle = identify_candlestick_patterns(test_data)
    if "error" not in candle:
        print(f"  识别: {len(candle.get('patterns', []))}个形态")
        if candle.get("patterns"):
            print(f"  主形态: {candle['patterns'][0]['name']}")
    else:
        print(f"  错误: {candle['error']}")
    
    print("\n📊 ADX 指标:")
    adx = calculate_adx(test_data)
    if "error" not in adx:
        print(f"  ADX: {adx['adx']}")
        print(f"  趋势: {adx['trend']}")
    else:
        print(f"  错误: {adx['error']}")
    
    print("\n📊 综合分析:")
    summary = enhanced_technical_analysis(test_data, "TEST")
    print(f"  信号数: {summary['summary']['signal_count']}")
    print(f"  看多: {summary['summary']['bullish_count']}")
    print(f"  看空: {summary['summary']['bearish_count']}")
    print(f"  综合判断: {summary['summary']['overall_bias']}")
    
    print("\n✅ 测试完成")
