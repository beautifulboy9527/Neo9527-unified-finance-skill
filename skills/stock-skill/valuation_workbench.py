#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scenario valuation workbench for commercial stock tools."""

from __future__ import annotations

from datetime import datetime
import importlib.util
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def _load_valuation_calculator():
    try:
        from .valuation import ValuationCalculator
        return ValuationCalculator
    except ImportError:
        path = Path(__file__).resolve().parent / "valuation.py"
        spec = importlib.util.spec_from_file_location("stock_valuation", path)
        if not spec or not spec.loader:
            raise ImportError("无法加载 valuation.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.ValuationCalculator


class ValuationWorkbench:
    """Run auditable bull/base/bear valuation scenarios."""

    DEFAULT_SCENARIOS = [
        {
            "name": "谨慎情景",
            "key": "bear",
            "discount_rate_delta": 0.015,
            "terminal_growth_delta": -0.005,
            "fcf_growth_delta": -0.02,
            "peer_multiple_multiplier": 0.85,
            "description": "更高折现率、更低永续增长和更保守可比倍数。",
        },
        {
            "name": "基准情景",
            "key": "base",
            "discount_rate_delta": 0,
            "terminal_growth_delta": 0,
            "fcf_growth_delta": 0,
            "peer_multiple_multiplier": 1.0,
            "description": "使用用户输入或模型默认的中性假设。",
        },
        {
            "name": "乐观情景",
            "key": "bull",
            "discount_rate_delta": -0.01,
            "terminal_growth_delta": 0.005,
            "fcf_growth_delta": 0.02,
            "peer_multiple_multiplier": 1.15,
            "description": "更低折现率、更高增长和更积极可比倍数。",
        },
    ]

    def __init__(self, calculator=None):
        Calculator = _load_valuation_calculator()
        self.calculator = calculator or Calculator()

    def analyze(
        self,
        symbol: str,
        *,
        methods: str = "all",
        base_params: Optional[Dict] = None,
        scenarios: Optional[Iterable[Dict]] = None,
    ) -> Dict:
        base_params = dict(base_params or {})
        scenario_specs = list(scenarios or self.DEFAULT_SCENARIOS)
        scenario_results = []

        for spec in scenario_specs:
            params = self._scenario_params(base_params, spec)
            result = self.calculator.calculate(symbol, methods=methods, **params)
            scenario_results.append(self._summarize_scenario(spec, params, result))

        valid = [item for item in scenario_results if item["success"] and item.get("fair_value")]
        current_price = next((item.get("current_price") for item in valid if item.get("current_price")), None)
        matrix = self._valuation_matrix(valid)
        conclusion = self._conclusion(symbol, valid, current_price)

        return {
            "success": bool(valid),
            "symbol": symbol,
            "methods": methods,
            "current_price": current_price,
            "scenarios": scenario_results,
            "valuation_range": self._valuation_range(valid),
            "sensitivity_matrix": matrix,
            "conclusion": conclusion,
            "warnings": self._collect_warnings(scenario_results),
            "timestamp": datetime.now().isoformat(),
        }

    def _scenario_params(self, base: Dict, spec: Dict) -> Dict:
        params = dict(base)

        discount_rate = float(params.get("discount_rate", 0.10)) + float(spec.get("discount_rate_delta", 0))
        terminal_growth = float(params.get("terminal_growth", 0.025)) + float(spec.get("terminal_growth_delta", 0))
        params["discount_rate"] = round(max(0.001, discount_rate), 4)
        params["terminal_growth"] = round(max(-0.05, terminal_growth), 4)

        if "fcf_growth" in params and params["fcf_growth"] is not None:
            params["fcf_growth"] = round(float(params["fcf_growth"]) + float(spec.get("fcf_growth_delta", 0)), 4)

        multiple_multiplier = float(spec.get("peer_multiple_multiplier", 1.0))
        for key in ("peer_pe", "peer_pb"):
            if key in params and params[key] is not None:
                params[key] = round(float(params[key]) * multiple_multiplier, 4)

        return params

    def _summarize_scenario(self, spec: Dict, params: Dict, result: Dict) -> Dict:
        current_price = result.get("current_price") or None
        fair_value = result.get("fair_value") or None
        upside = None
        if current_price and fair_value:
            upside = fair_value / current_price - 1

        return {
            "key": spec.get("key"),
            "name": spec.get("name", spec.get("key", "情景")),
            "description": spec.get("description", ""),
            "success": bool(result.get("success") and fair_value),
            "current_price": current_price,
            "fair_value": fair_value,
            "safe_price": result.get("safe_price") or None,
            "upside": upside,
            "valuation_confidence": result.get("valuation_confidence", "none"),
            "methods_used": result.get("methods_used", []),
            "fallback_used": bool(result.get("fallback_used", False)),
            "assumptions": self._visible_assumptions(params, result.get("assumptions", [])),
            "warnings": result.get("warnings", []) + ([result.get("error")] if result.get("error") else []),
            "evidence_summary": result.get("evidence_summary", {}),
        }

    def _visible_assumptions(self, params: Dict, model_assumptions: List[Dict]) -> List[Dict]:
        assumption_map = {item.get("name"): item for item in model_assumptions if isinstance(item, dict)}
        visible = []
        for key in ("discount_rate", "terminal_growth", "fcf_growth", "peer_pe", "peer_pb", "margin_of_safety"):
            if key in params and params[key] is not None:
                source = assumption_map.get(key, {}).get("source", "scenario_input")
                visible.append({"name": key, "value": params[key], "source": source})
        return visible

    def _valuation_range(self, valid: List[Dict]) -> Dict:
        values = [item["fair_value"] for item in valid if item.get("fair_value")]
        if not values:
            return {"low": None, "mid": None, "high": None}
        return {
            "low": min(values),
            "mid": values[len(values) // 2] if len(values) == 3 else sum(values) / len(values),
            "high": max(values),
        }

    def _valuation_matrix(self, valid: List[Dict]) -> List[Dict]:
        rows = []
        for item in valid:
            rows.append({
                "scenario": item["name"],
                "fair_value": item["fair_value"],
                "safe_price": item.get("safe_price"),
                "upside": item.get("upside"),
                "confidence": item.get("valuation_confidence"),
            })
        return rows

    def _conclusion(self, symbol: str, valid: List[Dict], current_price: Optional[float]) -> str:
        if not valid:
            return f"{symbol} 缺少可验证估值结果，不能形成估值区间。"
        value_range = self._valuation_range(valid)
        if current_price:
            low = value_range["low"]
            high = value_range["high"]
            if current_price < low:
                position = "低于情景估值区间"
            elif current_price > high:
                position = "高于情景估值区间"
            else:
                position = "位于情景估值区间内"
            return f"{symbol} 当前价格{position}，估值区间为{low:.2f}至{high:.2f}，需结合数据质量和模型假设复核。"
        return f"{symbol} 已生成情景估值区间，但当前价格缺失，不能计算上行空间。"

    def _collect_warnings(self, scenarios: List[Dict]) -> List[str]:
        warnings = []
        for item in scenarios:
            warnings.extend(item.get("warnings", []))
            if item.get("fallback_used"):
                warnings.append(f"{item['name']}使用了回退估值，不能作为核心结论。")
        return list(dict.fromkeys([warning for warning in warnings if warning]))


def analyze_valuation_workbench(symbol: str, **params) -> Dict:
    methods = params.pop("methods", "all")
    return ValuationWorkbench().analyze(symbol, methods=methods, base_params=params)


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_valuation_workbench("AAPL"), ensure_ascii=False, indent=2))
