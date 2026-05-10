#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术面选股 - Technical Screener
基于技术指标筛选股票: MACD金叉、均线多头、放量突破等
"""

from typing import Dict, List, Optional, Any
import importlib


def _num(value: Any) -> Optional[float]:
    """安全转换为数值"""
    if value is None:
        return None
    try:
        text = str(value).replace(",", "").replace("%", "").strip()
        if text in {"", "--", "None", "nan", "NaN"}:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def check_ma_bullish(prices: List[float]) -> Dict:
    """
    检查均线多头排列
    MA5 > MA10 > MA20 > MA60
    """
    if len(prices) < 60:
        return {"signal": False, "reason": "数据不足60日"}
    
    def ma(data, n):
        return sum(data[:n]) / n
    
    ma5 = ma(prices, 5)
    ma10 = ma(prices, 10)
    ma20 = ma(prices, 20)
    ma60 = ma(prices, 60)
    
    bullish = ma5 > ma10 > ma20 > ma60
    
    return {
        "signal": bullish,
        "name": "均线多头排列",
        "description": "MA5>MA10>MA20>MA60，趋势向上",
        "values": {
            "MA5": round(ma5, 2),
            "MA10": round(ma10, 2),
            "MA20": round(ma20, 2),
            "MA60": round(ma60, 2),
        },
        "strength": "strong" if bullish else "none",
    }


def check_macd_golden_cross(prices: List[float]) -> Dict:
    """
    检查MACD金叉
    DIF上穿DEA
    """
    if len(prices) < 35:
        return {"signal": False, "reason": "数据不足35日"}
    
    # 计算EMA
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_val = data[-1]
        for price in reversed(data[-period*2:]):
            ema_val = (price - ema_val) * multiplier + ema_val
        return ema_val
    
    # 计算MACD
    ema12 = ema(prices, 12)
    ema26 = ema(prices, 26)
    dif = ema12 - ema26
    
    # 简化: 用当前DIF和前一日DIF判断
    prev_prices = prices[1:]
    prev_ema12 = ema(prev_prices, 12)
    prev_ema26 = ema(prev_prices, 26)
    prev_dif = prev_ema12 - prev_ema26
    
    # DEA (DIF的9日EMA)
    # 简化判断: DIF从负转正或从下向上穿越
    golden_cross = (prev_dif < 0 and dif >= 0) or (dif > prev_dif and dif > 0)
    
    return {
        "signal": golden_cross,
        "name": "MACD金叉",
        "description": "DIF上穿DEA，可能开启上涨",
        "values": {
            "DIF": round(dif, 4),
            "prev_DIF": round(prev_dif, 4),
        },
        "strength": "strong" if golden_cross else "none",
    }


def check_volume_breakout(volumes: List[float], prices: List[float]) -> Dict:
    """
    检查放量突破
    近5日成交量 > 20日均量的1.5倍
    且价格突破近20日高点
    """
    if len(volumes) < 20 or len(prices) < 20:
        return {"signal": False, "reason": "数据不足20日"}
    
    recent_vol = sum(volumes[:5]) / 5
    avg_vol_20 = sum(volumes[:20]) / 20
    
    current_price = prices[0]
    high_20d = max(prices[:20])
    
    volume_surge = recent_vol > avg_vol_20 * 1.5
    price_breakout = current_price >= high_20d * 0.98  # 接近或突破
    
    signal = volume_surge and price_breakout
    
    return {
        "signal": signal,
        "name": "放量突破",
        "description": "成交量放大+价格突破20日高点",
        "values": {
            "recent_volume": round(recent_vol, 0),
            "avg_volume_20d": round(avg_vol_20, 0),
            "volume_ratio": round(recent_vol / avg_vol_20, 2) if avg_vol_20 > 0 else 0,
            "current_price": round(current_price, 2),
            "high_20d": round(high_20d, 2),
        },
        "strength": "strong" if signal else ("moderate" if volume_surge or price_breakout else "none"),
    }


def check_rsi_oversold(prices: List[float], period: int = 14) -> Dict:
    """
    检查RSI超卖反弹
    RSI从<30回升
    """
    if len(prices) < period + 5:
        return {"signal": False, "reason": "数据不足"}
    
    # 计算RSI
    gains = []
    losses = []
    for i in range(len(prices) - 1):
        change = prices[i] - prices[i + 1]  # 注意: prices[0]是最新
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return {"signal": False, "reason": "数据不足"}
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    # 前一日RSI
    prev_avg_gain = sum(gains[1:period+1]) / period
    prev_avg_loss = sum(losses[1:period+1]) / period
    if prev_avg_loss == 0:
        prev_rsi = 100
    else:
        prev_rs = prev_avg_gain / prev_avg_loss
        prev_rsi = 100 - (100 / (1 + prev_rs))
    
    # RSI从超卖区回升
    signal = prev_rsi < 30 and rsi > 30
    
    return {
        "signal": signal,
        "name": "RSI超卖反弹",
        "description": "RSI从<30回升，可能反弹",
        "values": {
            "RSI": round(rsi, 2),
            "prev_RSI": round(prev_rsi, 2),
        },
        "strength": "strong" if signal else ("moderate" if rsi < 40 else "none"),
    }


def check_bollinger_squeeze(prices: List[float], period: int = 20) -> Dict:
    """
    检查布林带收口
    带宽<10%，准备突破
    """
    if len(prices) < period:
        return {"signal": False, "reason": "数据不足"}
    
    recent = prices[:period]
    middle = sum(recent) / period
    
    # 标准差
    variance = sum((p - middle) ** 2 for p in recent) / period
    std = variance ** 0.5
    
    upper = middle + 2 * std
    lower = middle - 2 * std
    
    bandwidth = (upper - lower) / middle * 100 if middle > 0 else 0
    
    signal = bandwidth < 10
    
    return {
        "signal": signal,
        "name": "布林带收口",
        "description": "带宽<10%，可能即将突破",
        "values": {
            "upper": round(upper, 2),
            "middle": round(middle, 2),
            "lower": round(lower, 2),
            "bandwidth": round(bandwidth, 2),
        },
        "strength": "strong" if bandwidth < 8 else ("moderate" if signal else "none"),
    }


def check_consolidation_breakout(prices: List[float], period: int = 20) -> Dict:
    """
    检查盘整突破
    价格突破近N日震荡区间上沿
    """
    if len(prices) < period:
        return {"signal": False, "reason": "数据不足"}
    
    recent = prices[:period]
    high = max(recent)
    low = min(recent)
    current = prices[0]
    
    # 盘整幅度
    range_pct = (high - low) / low * 100 if low > 0 else 0
    
    # 突破判断
    is_consolidation = range_pct < 15  # 震荡幅度<15%
    is_breakout = current >= high * 0.98  # 接近或突破高点
    
    signal = is_consolidation and is_breakout
    
    return {
        "signal": signal,
        "name": "盘整突破",
        "description": f"近{period}日盘整后突破上沿",
        "values": {
            "current": round(current, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "range_pct": round(range_pct, 2),
        },
        "strength": "strong" if signal else ("moderate" if is_breakout else "none"),
    }


# ============ 技术筛选注册表 ============

TECHNICAL_CHECKS = {
    "golden-cross": {
        "name": "MACD金叉",
        "func": check_macd_golden_cross,
        "data_needed": "prices",
    },
    "ma-bullish": {
        "name": "均线多头排列",
        "func": check_ma_bullish,
        "data_needed": "prices",
    },
    "volume-breakout": {
        "name": "放量突破",
        "func": check_volume_breakout,
        "data_needed": "both",
    },
    "rsi-oversold": {
        "name": "RSI超卖反弹",
        "func": check_rsi_oversold,
        "data_needed": "prices",
    },
    "bollinger-squeeze": {
        "name": "布林带收口",
        "func": check_bollinger_squeeze,
        "data_needed": "prices",
    },
    "consolidation-breakout": {
        "name": "盘整突破",
        "func": check_consolidation_breakout,
        "data_needed": "prices",
    },
}


def list_technical_checks() -> List[Dict]:
    """列出所有技术检查"""
    result = []
    for key, check in TECHNICAL_CHECKS.items():
        result.append({
            "id": key,
            "name": check["name"],
        })
    return result


def run_technical_check(check_id: str, prices: List[float], volumes: List[float] = None) -> Dict:
    """运行单个技术检查"""
    check = TECHNICAL_CHECKS.get(check_id)
    if not check:
        return {"signal": False, "error": f"未知检查: {check_id}"}
    
    if check["data_needed"] == "prices":
        return check["func"](prices)
    elif check["data_needed"] == "both":
        return check["func"](volumes, prices)
    else:
        return check["func"](prices)


def run_all_technical_checks(prices: List[float], volumes: List[float] = None) -> List[Dict]:
    """运行所有技术检查"""
    results = []
    for check_id in TECHNICAL_CHECKS:
        result = run_technical_check(check_id, prices, volumes)
        results.append(result)
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("技术面选股检查")
    print("=" * 60)
    
    for check in list_technical_checks():
        print(f"  • {check['id']}: {check['name']}")
