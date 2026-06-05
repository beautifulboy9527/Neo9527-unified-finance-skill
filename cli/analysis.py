#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: analysis"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cmd_analyze(args):
    """快速分析股票"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "analyzer", 
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'analyzer.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    analyze_stock = module.analyze_stock
    
    symbol = args.symbol
    print(f"\n📊 分析 {symbol}...")
    
    result = analyze_stock(symbol)
    
    if result['success']:
        print(f"\n{'='*60}")
        print(f" {symbol} - {result['data'].get('name', '暂无数据')}")
        print(f"{'='*60}")
        print(f"市场: {result['market']}")
        print(f"评分: {result['score']}/100")
        
        tech = result['data'].get('technical', {})
        if tech:
            print(f"\n技术指标:")
            print(f"  趋势: {tech.get('trend', '暂无数据')}")
            print(f"  RSI: {tech.get('rsi', 0):.1f}")
            print(f"  MACD: {tech.get('macd_status', 'N/A')}")
        
        fund = result['data'].get('fundamentals', {})
        if fund:
            print(f"\n基本面:")
            print(f"  P/E: {fund.get('pe', 0):.1f}")
            print(f"  P/B: {fund.get('pb', 0):.1f}")
            print(f"  ROE: {fund.get('roe', 0):.1f}%")
        
        print(f"\n信号: {len(result['signals'])} 个")
        print(f"摘要: {result['summary']}")
    else:
        quality = result.get('data_quality', {})
        message = quality.get('message') or result.get('summary') or result.get('error') or '未知错误'
        print(f"❌ 分析失败: {message}")



def cmd_check(args):
    """财务异常检测"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "financial_check", 
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'financial_check.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    check_financial_anomaly = module.check_financial_anomaly
    
    symbol = args.symbol
    print(f"\n🔬 检测 {symbol}...")
    
    result = check_financial_anomaly(symbol)
    
    if result['success']:
        print(f"\n风险等级: {result['risk_description']}")
        print(f"异常数量: {result['anomaly_count']}")
        
        if result['anomalies']:
            print(f"\n异常详情:")
            for anomaly in result['anomalies']:
                print(f"  - {anomaly['name']}: {anomaly['description']}")
        
        summary = result.get('financial_data', {})
        if summary:
            print(f"\n财务摘要:")
            print(f"  毛利率: {summary.get('gross_margin', 0):.1f}%")
            print(f"  净利率: {summary.get('net_margin', 0):.1f}%")
    else:
        print(f"❌ 检测失败: {result.get('error', '未知错误')}")



def cmd_health(args):
    """财报体检评分"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "financial_health",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'financial_health.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    analyze_financial_health = module.analyze_financial_health

    symbol = args.symbol
    print(f"\n🧾 财报体检 {symbol}...")

    params = {
        'gross_margin': args.gross_margin,
        'net_margin': args.net_margin,
        'roe': args.roe,
        'debt_ratio': args.debt_ratio,
        'revenue_growth': args.revenue_growth,
        'profit_growth': args.profit_growth,
        'receivable_growth': args.receivable_growth,
        'inventory_growth': args.inventory_growth,
        'operating_cash_flow': args.operating_cash_flow,
        'net_income': args.net_income,
    }
    params = {key: value for key, value in params.items() if value is not None}
    result = analyze_financial_health(symbol, **params)
    print(f"\n{'='*60}")
    print(f" {symbol} 财报体检")
    print(f"{'='*60}")
    print(f"健康分: {result.get('health_score') if result.get('health_score') is not None else '未验证'}")
    print(f"等级: {result.get('health_grade')}")
    print(f"数据完整度: {result.get('data_completeness', 0):.0%}")
    print(f"结论: {result.get('conclusion')}")

    dimensions = result.get('dimensions', {})
    if dimensions:
        print("\n分项体检:")
        for item in dimensions.values():
            score = item.get('score') if item.get('score') is not None else '未验证'
            print(f"  - {item.get('name')}: {score} ({item.get('status')}) - {item.get('reason')}")

    flags = result.get('risk_flags', [])
    if flags:
        print("\n风险与验证:")
        for flag in flags[:6]:
            print(f"  - {flag}")



def cmd_value(args):
    """估值计算"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "valuation", 
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'valuation.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calculate_valuation = module.calculate_valuation
    
    symbol = args.symbol
    print(f"\n💰 计算 {symbol} 估值...")
    
    result = calculate_valuation(symbol)
    
    if result['success']:
        print(f"\n{'='*60}")
        print(f" {symbol} 估值分析")
        print(f"{'='*60}")
        print(f"当前价格: ${result['current_price']:.2f}")
        print(f"公允价值: ${result['fair_value']:.2f}")
        print(f"安全价格: ${result['safe_price']:.2f} (安全边际 {result['margin_of_safety']*100:.0f}%)")
        
        valuations = result.get('valuations', {})
        if 'relative' in valuations:
            print(f"\n相对估值:")
            rel = valuations['relative']
            if 'pe_based' in rel:
                print(f"  PE估值: ${rel['pe_based']['fair_value']:.2f}")
    else:
        print(f"❌ 估值失败: {result.get('error', '未知错误')}")



def cmd_research(args):
    """深度研报"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "deep_research_analyzer",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'deep-research', 'analyzer.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    StockAnalyzer = module.StockAnalyzer
    InvestmentStyle = module.InvestmentStyle
    
    symbol = args.symbol
    style = args.style if args.style else 'value'
    depth = args.depth if args.depth else 'standard'
    
    print(f"\n📈 生成 {symbol} 深度研报 ({style}风格, {depth}深度)...")
    
    analyzer = StockAnalyzer(style=style)
    result = analyzer.analyze(symbol, depth=depth)
    
    print(f"\n{'='*60}")
    print(f" {symbol} 深度研报")
    print(f"{'='*60}")
    print(f"综合评级: {result['rating']['rating']}")
    print(f"评分: {result['rating']['score']}/{result['rating']['max_score']}")
    print(f"建议: {result['rating']['recommendation']}")


