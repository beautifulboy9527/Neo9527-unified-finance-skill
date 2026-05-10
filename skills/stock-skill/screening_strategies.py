#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股策略库 - Pre-built Screening Strategies
包含: 价值投资、成长股、高股息、GARP、困境反转、防御型
"""

from typing import Dict, List, Optional


# ============ 预设策略定义 ============

STRATEGIES = {
    "value": {
        "name": "价值投资",
        "description": "寻找低估值、高ROE的优质公司",
        "criteria": {
            "pe_max": 20,
            "pb_max": 3,
            "roe_min": 15,
            "debt_ratio_max": 60,
            "net_margin_min": 8,
        },
        "scoring_weights": {
            "valuation": 0.40,
            "profitability": 0.30,
            "safety": 0.20,
            "growth": 0.10,
        },
        "sort_by": "composite_score",
        "sort_ascending": False,
    },
    
    "growth": {
        "name": "成长股",
        "description": "寻找高增长、有潜力的成长型公司",
        "criteria": {
            "pe_max": 50,
            "revenue_growth_min": 20,
            "profit_growth_min": 20,
            "roe_min": 10,
        },
        "scoring_weights": {
            "growth": 0.45,
            "profitability": 0.25,
            "valuation": 0.20,
            "safety": 0.10,
        },
        "sort_by": "growth_score",
        "sort_ascending": False,
    },
    
    "dividend": {
        "name": "高股息",
        "description": "寻找稳定分红、股息率高的公司",
        "criteria": {
            "dividend_yield_min": 3,
            "pe_max": 25,
            "debt_ratio_max": 50,
            "net_margin_min": 10,
        },
        "scoring_weights": {
            "dividend": 0.40,
            "safety": 0.30,
            "valuation": 0.20,
            "profitability": 0.10,
        },
        "sort_by": "dividend_yield",
        "sort_ascending": False,
    },
    
    "garp": {
        "name": "GARP (成长+价值)",
        "description": "以合理价格买入成长股",
        "criteria": {
            "peg_max": 1.5,
            "roe_min": 12,
            "revenue_growth_min": 10,
            "pe_max": 35,
        },
        "scoring_weights": {
            "growth": 0.35,
            "valuation": 0.35,
            "profitability": 0.20,
            "safety": 0.10,
        },
        "sort_by": "peg_ratio",
        "sort_ascending": True,
    },
    
    "turnaround": {
        "name": "困境反转",
        "description": "寻找业绩拐点、即将反转的公司",
        "criteria": {
            "profit_growth_qoq_min": 10,  # 季度环比增长
            "roe_min": 5,
            "debt_ratio_max": 70,
        },
        "scoring_weights": {
            "growth": 0.50,
            "profitability": 0.25,
            "safety": 0.15,
            "valuation": 0.10,
        },
        "sort_by": "profit_growth_qoq",
        "sort_ascending": False,
    },
    
    "defensive": {
        "name": "防御型",
        "description": "低波动、稳定现金流的防御性股票",
        "criteria": {
            "beta_max": 0.8,
            "dividend_yield_min": 2,
            "debt_ratio_max": 40,
            "current_ratio_min": 1.5,
            "net_margin_min": 10,
        },
        "scoring_weights": {
            "safety": 0.40,
            "dividend": 0.30,
            "profitability": 0.20,
            "valuation": 0.10,
        },
        "sort_by": "safety_score",
        "sort_ascending": False,
    },
    
    "quality": {
        "name": "质量因子",
        "description": "寻找高质量、护城河深的公司",
        "criteria": {
            "roe_min": 15,
            "gross_margin_min": 30,
            "debt_ratio_max": 50,
            "current_ratio_min": 1.2,
        },
        "scoring_weights": {
            "profitability": 0.40,
            "safety": 0.30,
            "growth": 0.20,
            "valuation": 0.10,
        },
        "sort_by": "profitability_score",
        "sort_ascending": False,
    },
}


def get_strategy(strategy_name: str) -> Optional[Dict]:
    """获取预设策略"""
    return STRATEGIES.get(strategy_name)


def list_strategies() -> List[Dict]:
    """列出所有预设策略"""
    result = []
    for key, strategy in STRATEGIES.items():
        result.append({
            "id": key,
            "name": strategy["name"],
            "description": strategy["description"],
            "criteria": strategy["criteria"],
        })
    return result


def get_strategy_criteria(strategy_name: str) -> Dict:
    """获取策略的筛选条件"""
    strategy = STRATEGIES.get(strategy_name)
    if strategy:
        return strategy.get("criteria", {})
    return {}


def get_strategy_weights(strategy_name: str) -> Dict:
    """获取策略的评分权重"""
    strategy = STRATEGIES.get(strategy_name)
    if strategy:
        return strategy.get("scoring_weights", {})
    return {}


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print("选股策略库")
    print("=" * 60)
    
    for s in list_strategies():
        print(f"\n📌 {s['name']} ({s['id']})")
        print(f"   {s['description']}")
        print(f"   条件: {s['criteria']}")
