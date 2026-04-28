#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chinese localization helpers for finance reports."""

from __future__ import annotations

import re
from typing import Any, Dict


MISSING_TEXT = "暂无数据"


SECTOR_CN = {
    "Technology": "科技",
    "Healthcare": "医疗健康",
    "Financial Services": "金融服务",
    "Consumer Cyclical": "可选消费",
    "Consumer Defensive": "必选消费",
    "Energy": "能源",
    "Industrials": "工业",
    "Basic Materials": "基础材料",
    "Real Estate": "房地产",
    "Utilities": "公用事业",
    "Communication Services": "通信服务",
}


INDUSTRY_CN = {
    "Consumer Electronics": "消费电子",
    "Software - Infrastructure": "基础软件",
    "Software - Application": "应用软件",
    "Semiconductors": "半导体",
    "Internet Content & Information": "互联网内容与信息",
    "Auto Manufacturers": "汽车制造",
    "Banks - Diversified": "综合银行",
    "Credit Services": "信贷服务",
    "Asset Management": "资产管理",
    "Drug Manufacturers - General": "综合制药",
    "Biotechnology": "生物科技",
    "Medical Devices": "医疗器械",
    "Oil & Gas Integrated": "综合油气",
    "Specialty Industrial Machinery": "专用工业设备",
    "Aerospace & Defense": "航空航天与国防",
    "Household & Personal Products": "家庭与个人用品",
    "Beverages - Non-Alcoholic": "非酒精饮料",
}


STOCK_NAME_CN = {
    "AAPL": "苹果公司",
    "MSFT": "微软",
    "GOOG": "谷歌",
    "GOOGL": "谷歌",
    "AMZN": "亚马逊",
    "META": "Meta平台",
    "NVDA": "英伟达",
    "TSLA": "特斯拉",
    "BRK-B": "伯克希尔哈撒韦",
    "JPM": "摩根大通",
    "V": "维萨",
    "MA": "万事达",
    "NFLX": "奈飞",
    "AMD": "超威半导体",
    "INTC": "英特尔",
    "KO": "可口可乐",
    "PEP": "百事公司",
    "WMT": "沃尔玛",
    "DIS": "迪士尼",
    "BABA": "阿里巴巴",
    "PDD": "拼多多",
    "NIO": "蔚来",
    "LI": "理想汽车",
    "XPEV": "小鹏汽车",
}


RATING_CN = {
    "strong_buy": "积极关注",
    "buy": "偏积极",
    "hold": "中性观望",
    "sell": "偏谨慎",
    "strong_sell": "高度谨慎",
    "underperform": "弱于市场",
    "none": MISSING_TEXT,
}


ACTION_CN = {
    "buy": "偏积极",
    "strong_buy": "积极关注",
    "sell": "偏谨慎",
    "strong_sell": "高度谨慎",
    "hold": "中性观望",
    "exit": "降低风险暴露",
    "monitor": "持续跟踪",
    "strengthen": "加强验证",
}


def is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in {"", "N/A", "NA", "None", "null", "Unknown", "--"}
    return False


def safe_cn(value: Any, default: str = MISSING_TEXT) -> str:
    if is_missing(value):
        return default
    return str(value)


def translate_sector(sector: Any) -> str:
    text = safe_cn(sector)
    return SECTOR_CN.get(text, text if text != MISSING_TEXT else MISSING_TEXT)


def translate_industry(industry: Any) -> str:
    text = safe_cn(industry)
    return INDUSTRY_CN.get(text, text if text != MISSING_TEXT else MISSING_TEXT)


def translate_rating(rating: Any) -> str:
    key = safe_cn(rating, "").strip().lower().replace(" ", "_").replace("-", "_")
    return RATING_CN.get(key, safe_cn(rating))


def translate_action(action: Any) -> str:
    key = safe_cn(action, "").strip().lower().replace(" ", "_").replace("-", "_")
    return ACTION_CN.get(key, safe_cn(action))


def stock_display_name(symbol: str, info: Dict[str, Any] | None = None) -> str:
    info = info or {}
    code = safe_cn(symbol, "未知代码").upper()
    mapped = STOCK_NAME_CN.get(code)
    if mapped:
        return f"{mapped}（{code}）"

    for key in ("shortName", "longName", "displayName", "name"):
        value = safe_cn(info.get(key), "")
        if value and re.search(r"[\u4e00-\u9fff]", value):
            return f"{value}（{code}）"

    industry = translate_industry(info.get("industry"))
    if industry != MISSING_TEXT:
        return f"{industry}公司（{code}）"
    return f"上市公司（{code}）"


def normalize_report_text(text: str) -> str:
    replacements = {
        "N/A": MISSING_TEXT,
        "Unknown": MISSING_TEXT,
        "STRONG_BUY": "积极关注",
        "STRONG SELL": "高度谨慎",
        "STRONG_SELL": "高度谨慎",
        "BUY": "偏积极",
        "SELL": "偏谨慎",
        "HOLD": "中性观望",
        "buy": "偏积极",
        "sell": "偏谨慎",
        "hold": "中性观望",
    }
    result = text
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result
