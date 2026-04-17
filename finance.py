#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance CLI
统一金融分析命令行工具
"""

import sys
import os
import argparse
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
SKILLS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILLS_DIR)


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
        print(f" {symbol} - {result['data'].get('name', 'N/A')}")
        print(f"{'='*60}")
        print(f"市场: {result['market']}")
        print(f"评分: {result['score']}/100")
        
        tech = result['data'].get('technical', {})
        if tech:
            print(f"\n技术指标:")
            print(f"  趋势: {tech.get('trend', 'N/A')}")
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
        print(f"❌ 分析失败: {result.get('error', '未知错误')}")


def cmd_screen(args):
    """A股选股"""
    from stock_skill.screener import screen_stocks
    
    print(f"\n🔍 选股 ({args.scope})...")
    
    criteria = {}
    if args.pe_max:
        criteria['pe_max'] = args.pe_max
    if args.roe_min:
        criteria['roe_min'] = args.roe_min
    if args.debt_max:
        criteria['debt_ratio_max'] = args.debt_max
    
    result = screen_stocks(args.scope, criteria if criteria else None)
    
    if result['success']:
        print(f"\n选股结果: {result['matched_stocks']}/{result['total_stocks']} 只")
        
        if result['stocks']:
            print(f"\n符合条件股票:")
            for i, stock in enumerate(result['stocks'][:20], 1):
                print(f"  {i}. {stock['code']} - ROE: {stock['roe']:.1f}%, PE: {stock['pe']:.1f}")
    else:
        print(f"❌ 选股失败: {result.get('error', '未知错误')}")


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
    from stock_skill.deep_research.analyzer import StockAnalyzer, InvestmentStyle
    
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


def main():
    parser = argparse.ArgumentParser(
        description='Neo9527 Finance CLI - 统一金融分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    parser_analyze = subparsers.add_parser('analyze', help='快速分析股票')
    parser_analyze.add_argument('symbol', help='股票代码')
    parser_analyze.set_defaults(func=cmd_analyze)
    
    # screen 命令
    parser_screen = subparsers.add_parser('screen', help='A股选股')
    parser_screen.add_argument('--scope', default='hs300', help='选股范围 (hs300/zz500/a50)')
    parser_screen.add_argument('--pe-max', type=float, help='PE上限')
    parser_screen.add_argument('--roe-min', type=float, help='ROE下限')
    parser_screen.add_argument('--debt-max', type=float, help='负债率上限')
    parser_screen.set_defaults(func=cmd_screen)
    
    # check 命令
    parser_check = subparsers.add_parser('check', help='财务异常检测')
    parser_check.add_argument('symbol', help='股票代码')
    parser_check.set_defaults(func=cmd_check)
    
    # value 命令
    parser_value = subparsers.add_parser('value', help='估值计算')
    parser_value.add_argument('symbol', help='股票代码')
    parser_value.set_defaults(func=cmd_value)
    
    # research 命令
    parser_research = subparsers.add_parser('research', help='深度研报')
    parser_research.add_argument('symbol', help='股票代码')
    parser_research.add_argument('--style', choices=['value', 'growth', 'turnaround', 'dividend'], help='投资风格')
    parser_research.add_argument('--depth', choices=['quick', 'standard', 'deep'], help='分析深度')
    parser_research.set_defaults(func=cmd_research)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main()
