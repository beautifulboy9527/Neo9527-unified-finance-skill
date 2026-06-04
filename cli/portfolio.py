#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: portfolio"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cmd_portfolio(args):
    """组合分析 (Phase 5)"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "portfolio_skill",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'portfolio_skill.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    skill = module.PortfolioSkill()
    
    if args.portfolio_action == 'analyze':
        symbols = args.symbols.split(',')
        weights = [float(w) for w in args.weights.split(',')] if args.weights else None
        
        result = skill.execute('analyze', symbols=symbols, weights=weights, days=args.days)
        
        if result['success']:
            print(f"\n📊 组合分析结果:")
            print(f"  预期年化收益: {result['annual_return']}%")
            print(f"  波动率: {result['volatility']}%")
            print(f"  Sharpe: {result['sharpe_ratio']}")
            print(f"  VaR(95%): {result['var_95_pct']}%")
            print(f"  最大回撤: {result['max_drawdown_pct']}%")
            print(f"\n  健康度评分: {result['health_score']['total']} ({result['health_score']['rating']})")
        else:
            print(f"❌ {result.get('error', '分析失败')}")
    
    elif args.portfolio_action == 'optimize':
        symbols = args.symbols.split(',')
        
        result = skill.execute('optimize', symbols=symbols, method=args.method, days=args.days)
        
        if result['success']:
            print(f"\n📊 优化结果 ({result['method']}):")
            print(f"  预期收益: {result['expected_return_pct']}%")
            print(f"  波动率: {result['volatility_pct']}%")
            print(f"  Sharpe: {result['sharpe_ratio']}")
            print(f"\n  权重分配:")
            for symbol, weight in result['weight_allocation'].items():
                print(f"    {symbol}: {weight}")
        else:
            print(f"❌ {result.get('error', '优化失败')}")
    
    elif args.portfolio_action == 'kelly':
        result = skill.execute('kelly', symbol=args.symbol, days=args.days)
        
        if result['success']:
            print(f"\n📊 Kelly 仓位 ({result['symbol']}):")
            print(f"  胜率: {result['win_rate']}%")
            print(f"  盈亏比: {result['win_loss_ratio']}")
            print(f"  Kelly%: {result['kelly_pct']}%")
            print(f"  保守Kelly: {result['conservative_kelly_pct']}%")
            print(f"\n  建议: {result['recommendation']}")
        else:
            print(f"❌ {result.get('error', '计算失败')}")
    
    elif args.portfolio_action == 'warnings':
        symbols = args.symbols.split(',')
        weights = [float(w) for w in args.weights.split(',')] if args.weights else None
        
        result = skill.execute('warnings', symbols=symbols, weights=weights, days=args.days)
        
        print(f"\n⚠️ 风险预警 ({result['warning_count']} 个):")
        for warning in result['warnings']:
            print(f"  [{warning['severity']}] {warning['message']}")


