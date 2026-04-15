#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Skill - Main Entry
整合 yfinance-data, stock-market-pro, agent-stock, akshare-stock 的核心功能

输出目录：D:\OpenClaw\outputs\
- reports: 分析报告
- charts: 图表文件
- data: 数据文件
- logs: 日志文件
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加依赖路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 统一输出目录
OUTPUT_BASE = r'D:\OpenClaw\outputs'
OUTPUT_REPORTS = os.path.join(OUTPUT_BASE, 'reports')
OUTPUT_CHARTS = os.path.join(OUTPUT_BASE, 'charts')
OUTPUT_DATA = os.path.join(OUTPUT_BASE, 'data')
OUTPUT_LOGS = os.path.join(OUTPUT_BASE, 'logs')

# 确保输出目录存在
for dir_path in [OUTPUT_REPORTS, OUTPUT_CHARTS, OUTPUT_DATA, OUTPUT_LOGS]:
    os.makedirs(dir_path, exist_ok=True)

def get_parser():
    parser = argparse.ArgumentParser(description='Unified Finance Skill - 统一金融分析')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # quote 命令
    quote_parser = subparsers.add_parser('quote', help='查询实时行情')
    quote_parser.add_argument('symbol', help='股票代码')
    
    # chart 命令
    chart_parser = subparsers.add_parser('chart', help='生成图表')
    chart_parser.add_argument('symbol', help='股票代码')
    chart_parser.add_argument('period', nargs='?', default='3mo', help='时间周期')
    chart_parser.add_argument('--rsi', action='store_true', help='显示 RSI')
    chart_parser.add_argument('--macd', action='store_true', help='显示 MACD')
    chart_parser.add_argument('--bb', action='store_true', help='显示布林带')
    chart_parser.add_argument('--vwap', action='store_true', help='显示 VWAP')
    chart_parser.add_argument('--atr', action='store_true', help='显示 ATR')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成分析报告')
    report_parser.add_argument('symbol', help='股票代码')
    report_parser.add_argument('period', nargs='?', default='6mo', help='时间周期')
    
    # heatmap 命令
    heatmap_parser = subparsers.add_parser('heatmap', help='行业热力图')
    heatmap_parser.add_argument('market', choices=['ab', 'hk', 'us'], help='市场')
    
    # fundflow 命令
    fundflow_parser = subparsers.add_parser('fundflow', help='资金流向')
    fundflow_parser.add_argument('symbol', help='股票代码')
    
    # alert 命令
    alert_parser = subparsers.add_parser('alert', help='警报管理')
    alert_subparsers = alert_parser.add_subparsers(dest='alert_command')
    
    alert_add = alert_subparsers.add_parser('add', help='添加警报')
    alert_add.add_argument('symbol', help='股票代码')
    alert_add.add_argument('--target', type=float, help='目标价')
    alert_add.add_argument('--stop', type=float, help='止损价')
    
    alert_list = alert_subparsers.add_parser('list', help='列出警报')
    alert_check = alert_subparsers.add_parser('check', help='检查警报')
    
    # screener 命令
    screener_parser = subparsers.add_parser('screener', help='多条件选股')
    screener_parser.add_argument('--market', choices=['us', 'cn'], default='us', help='市场')
    screener_parser.add_argument('--pe-max', type=float, help='最大市盈率')
    screener_parser.add_argument('--pb-max', type=float, help='最大市净率')
    screener_parser.add_argument('--roe-min', type=float, help='最小 ROE')
    screener_parser.add_argument('--rsi-oversold', action='store_true', help='RSI 超卖')
    screener_parser.add_argument('--limit', type=int, default=20, help='返回数量')
    
    # portfolio 命令
    portfolio_parser = subparsers.add_parser('portfolio', help='投资组合管理')
    portfolio_parser.add_argument('action', choices=['add', 'remove', 'list', 'summary', 'analyze'], help='操作')
    portfolio_parser.add_argument('--symbol', help='股票代码')
    portfolio_parser.add_argument('--quantity', type=float, help='数量')
    portfolio_parser.add_argument('--cost', type=float, help='成本价')
    portfolio_parser.add_argument('--id', type=int, help='持仓 ID')
    
    # fundamentals 命令
    fundamentals_parser = subparsers.add_parser('fundamentals', help='基本面数据')
    fundamentals_parser.add_argument('symbol', help='股票代码')
    
    # valuation 命令
    valuation_parser = subparsers.add_parser('valuation', help='估值分析')
    valuation_parser.add_argument('symbol', help='股票代码')
    valuation_parser.add_argument('--mode', choices=['pe', 'pb', 'all'], default='all', help='分析模式')
    
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'quote':
        from data_fetcher import get_quote
        result = get_quote(args.symbol)
        print(result)
    
    elif args.command == 'chart':
        from chart_generator import generate_chart
        indicators = {
            'rsi': args.rsi,
            'macd': args.macd,
            'bb': args.bb,
            'vwap': args.vwap,
            'atr': args.atr
        }
        path = generate_chart(args.symbol, args.period, indicators)
        print(f"CHART_PATH: {path}")
    
    elif args.command == 'report':
        from chart_generator import generate_report
        generate_report(args.symbol, args.period)
    
    elif args.command == 'heatmap':
        from data_fetcher import get_heatmap
        result = get_heatmap(args.market)
        print(result)
    
    elif args.command == 'fundflow':
        from data_fetcher import get_fundflow
        result = get_fundflow(args.symbol)
        print(result)
    
    elif args.command == 'alert':
        from alert_manager import AlertManager
        manager = AlertManager()
        
        if args.alert_command == 'add':
            manager.add(args.symbol, target=args.target, stop=args.stop)
            print(f"[OK] 已添加警报：{args.symbol}")
        elif args.alert_command == 'list':
            alerts = manager.list()
            print(json.dumps(alerts, indent=2, ensure_ascii=False))
        elif args.alert_command == 'check':
            triggered = manager.check()
            if triggered:
                print("[ALERT] 触发警报:")
                for alert in triggered:
                    print(f"  - {alert['message']}")
            else:
                print("[OK] 无触发警报")
    
    elif args.command == 'screener':
        from stock_screener import StockScreener, format_table
        screener = StockScreener()
        
        if args.rsi_oversold:
            df = screener.screen_by_technical(
                market=args.market,
                rsi_oversold=True,
                limit=args.limit
            )
        else:
            if args.market == 'us':
                df = screener.screen_us_stocks(
                    pe_max=args.pe_max,
                    pb_max=args.pb_max,
                    roe_min=args.roe_min,
                    limit=args.limit
                )
            else:
                df = screener.screen_cn_stocks(
                    pe_max=args.pe_max,
                    limit=args.limit
                )
        
        print(format_table(df))
    
    elif args.command == 'portfolio':
        from portfolio_manager import PortfolioManager, format_portfolio_summary
        pm = PortfolioManager()
        
        if args.action == 'add' and args.symbol and args.quantity and args.cost:
            pm.add_position(args.symbol, args.quantity, args.cost)
        elif args.action == 'remove' and args.id:
            pm.remove_position(args.id)
        elif args.action == 'list':
            positions = pm.get_positions()
            if positions:
                print("\n当前持仓:")
                for pos in positions:
                    print(f"  {pos['id']}. {pos['symbol']} x {pos['quantity']} @ {pos['cost_price']}")
            else:
                print("无持仓")
        elif args.action == 'summary':
            summary = pm.get_summary()
            print(format_portfolio_summary(summary))
        elif args.action == 'analyze':
            allocation = pm.analyze_allocation()
            print("\n持仓配置分析:")
            for alloc in allocation['allocation']:
                print(f"  {alloc['symbol']:10} {alloc['weight']:>6.2f}%  ({alloc['market_value']:,.0f})")
    
    elif args.command == 'fundamentals':
        import yfinance as yf
        ticker = yf.Ticker(args.symbol)
        info = ticker.info
        
        print(f"\n{info.get('longName', args.symbol)} 基本面数据:")
        print("-" * 50)
        print(f"市值：{info.get('marketCap', 'N/A')}")
        print(f"市盈率 (Forward): {info.get('forwardPE', 'N/A')}")
        print(f"市净率：{info.get('priceToBook', 'N/A')}")
        print(f"ROE: {info.get('returnOnEquity', 'N/A')}")
        print(f"毛利率：{info.get('grossMargins', 'N/A')}")
        print(f"净利率：{info.get('profitMargins', 'N/A')}")
        print(f"股息率：{info.get('dividendYield', 'N/A')}")
        print(f"EPS (TTM): {info.get('trailingEps', 'N/A')}")
        print(f"52 周最高：{info.get('fiftyTwoWeekHigh', 'N/A')}")
        print(f"52 周最低：{info.get('fiftyTwoWeekLow', 'N/A')}")
        print(f"分析师目标价：{info.get('targetMeanPrice', 'N/A')}")
    
    elif args.command == 'valuation':
        from valuation_monitor import ValuationMonitor, format_valuation_report
        monitor = ValuationMonitor()
        
        if args.mode == 'all':
            result = monitor.get_comprehensive_valuation(args.symbol)
            print(format_valuation_report(result))
        elif args.mode == 'pe':
            result = monitor.get_pe_percentile(args.symbol)
            print(f"\n{args.symbol} PE 分析:")
            print(f"  当前 PE: {result.get('current_pe', 'N/A')}")
            print(f"  历史分位：{result.get('percentile', 'N/A')}%")
            print(f"  估值评级：{result.get('rating', 'N/A')}")
        else:
            result = monitor.get_pb_percentile(args.symbol)
            print(f"\n{args.symbol} PB 分析:")
            print(f"  当前 PB: {result.get('current_pb', 'N/A')}")
            print(f"  历史分位：{result.get('percentile', 'N/A')}%")
            print(f"  估值评级：{result.get('rating', 'N/A')}")

if __name__ == '__main__':
    main()
