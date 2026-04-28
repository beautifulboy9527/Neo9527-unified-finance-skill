#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pattern-report consistency helpers."""

from __future__ import annotations

from typing import Dict, MutableMapping


def normalize_pattern_report(
    patterns: MutableMapping[str, object],
    timeframe: str = "日线",
    lookback: str = "最近20个交易日",
) -> Dict[str, object]:
    """Ensure pattern outputs are mutually consistent and timeframe-labelled."""
    normalized = dict(patterns or {})
    normalized["形态时间级别"] = timeframe
    normalized["形态观察窗口"] = lookback

    has_top = bool(normalized.get("double_top"))
    has_bottom = bool(normalized.get("double_bottom"))
    if has_top and has_bottom:
        top_strength = abs(float(normalized.get("double_top_strength", 0) or 0))
        bottom_strength = abs(float(normalized.get("double_bottom_strength", 0) or 0))
        if top_strength >= bottom_strength:
            normalized["double_bottom"] = False
            normalized.pop("double_bottom_desc", None)
            kept = "双顶"
        else:
            normalized["double_top"] = False
            normalized.pop("double_top_desc", None)
            kept = "双底"
        normalized["形态冲突处理"] = f"原始检测同时出现双顶和双底，已按信号强度仅保留{kept}。"

    for key in ("double_top_desc", "double_bottom_desc"):
        desc = normalized.get(key)
        if isinstance(desc, str) and desc:
            if timeframe not in desc:
                desc = f"{desc}（{timeframe}）"
            if lookback not in desc:
                desc = f"{desc}，观察窗口：{lookback}"
            normalized[key] = desc

    return normalized
