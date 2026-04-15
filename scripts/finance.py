#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Skill - 统一入口
整合所有金融分析能力的超级入口
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

# 导入模块
from core.quote import get_quote, get_quotes, detect_market
from core.technical import analyze_technical
from core.financial import get_financial_summary, get_fundflow
from features.liquidity import analyze_liquidity
from features.sentiment import analyze_sentiment
from features.chart import generate_chart, generate_full_chart
from features.correlation import (
    discover_correlated,
    analyze_pair_correlation,
    analyze_cluster,
    analyze_rolling_correlation
)
from features.enhanced_financial import (
    get_stock_list,
    get_realtime_quotes,
    get_historical_data,
    get_financial_statements,
    get_macro_data,
    get_index_data,
    get_industry_data
)
from features.valuation import (
    calculate_percentile,
    analyze_etf_premium,
    calculate_band,
    get_valuation_summary
)
from features.research import (
    run_research,
    ResearchFramework
)
from features.earnings import (
    generate_earnings_preview,
    generate_earnings_recap,
    get_beat_miss_history
)


def full_analysis(symbol: str) -> Dict:
    """
    完整分析 - 整合所有模块
    """
    return {
        'symbol': symbol,
        'market': detect_market(symbol),
        'quote': get_quote(symbol),
        'technical': analyze_technical(symbol),
        'financial': get_financial_summary(symbol),
        'fundflow': get_fundflow(symbol) if detect_market(symbol) == 'cn' else None,
        'liquidity': analyze_liquidity(symbol),
        'sentiment': analyze_sentiment(symbol),
        'chart': generate_chart(symbol, rsi=True, macd=True),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def quick_analysis(symbol: str) -> Dict:
    """
    快速分析 - 仅核心数据
    """
    return {
        'symbol': symbol,
        'market': detect_market(symbol),
        'quote': get_quote(symbol),
        'technical': analyze_technical(symbol),
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


# CLI 接口
def main():
    parser = argparse.ArgumentParser(
        description='Unified Finance Skill - 统一金融分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 行情查询
  python finance.py quote 002050
  python finance.py quote AAPL
  
  # 技术分析
  python finance.py technical 002050
  
  # 财务数据
  python finance.py financial 002050
  python finance.py fundflow 002050
  
  # 流动性分析
  python finance.py liquidity AAPL
  
  # 情绪分析
  python finance.py sentiment AAPL
  
  # 完整分析
  python finance.py full 002050
  
  # 快速分析
  python finance.py quick 002050
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # quote
    quote_parser = subparsers.add_parser('quote', help='行情查询')
    quote_parser.add_argument('symbol', help='股票代码')
    quote_parser.add_argument('--batch', nargs='+', help='批量查询')
    
    # technical
    tech_parser = subparsers.add_parser('technical', help='技术分析')
    tech_parser.add_argument('symbol', help='股票代码')
    
    # financial
    fin_parser = subparsers.add_parser('financial', help='财务数据')
    fin_parser.add_argument('symbol', help='股票代码')
    
    # fundflow
    flow_parser = subparsers.add_parser('fundflow', help='资金流向')
    flow_parser.add_argument('symbol', help='股票代码')
    flow_parser.add_argument('--days', type=int, default=10, help='天数')
    
    # liquidity
    liq_parser = subparsers.add_parser('liquidity', help='流动性分析')
    liq_parser.add_argument('symbol', help='股票代码')
    liq_parser.add_argument('--period', default='3mo', help='分析周期')
    
    # sentiment
    sent_parser = subparsers.add_parser('sentiment', help='情绪分析')
    sent_parser.add_argument('symbol', help='股票代码')
    sent_parser.add_argument('--days', type=int, default=7, help='分析天数')
    
    # chart
    chart_parser = subparsers.add_parser('chart', help='技术图表')
    chart_parser.add_argument('symbol', help='股票代码')
    chart_parser.add_argument('--period', default='3mo', help='周期')
    chart_parser.add_argument('--rsi', action='store_true', help='显示 RSI')
    chart_parser.add_argument('--macd', action='store_true', help='显示 MACD')
    chart_parser.add_argument('--bb', action='store_true', help='显示布林带')
    chart_parser.add_argument('--vwap', action='store_true', help='显示 VWAP')
    chart_parser.add_argument('--atr', action='store_true', help='显示 ATR')
    chart_parser.add_argument('--full', action='store_true', help='显示所有指标')
    
    # correlation
    corr_parser = subparsers.add_parser('corr', help='相关性分析')
    corr_sub = corr_parser.add_subparsers(dest='corr_type', help='相关性类型')
    
    corr_discover = corr_sub.add_parser('discover', help='发现相关股票')
    corr_discover.add_argument('--target', required=True, help='目标股票')
    corr_discover.add_argument('--peers', nargs='+', required=True, help='候选股票')
    
    corr_pair = corr_sub.add_parser('pair', help='配对相关性')
    corr_pair.add_argument('--ticker-a', required=True, help='股票A')
    corr_pair.add_argument('--ticker-b', required=True, help='股票B')
    
    corr_cluster = corr_sub.add_parser('cluster', help='聚类分析')
    corr_cluster.add_argument('--tickers', nargs='+', required=True, help='股票列表')
    
    corr_rolling = corr_sub.add_parser('rolling', help='滚动相关性')
    corr_rolling.add_argument('--ticker-a', required=True, help='股票A')
    corr_rolling.add_argument('--ticker-b', required=True, help='股票B')
    
    # valuation
    val_parser = subparsers.add_parser('val', help='估值分析')
    val_sub = val_parser.add_subparsers(dest='val_type', help='估值类型')
    
    val_pct = val_sub.add_parser('percentile', help='估值百分位')
    val_pct.add_argument('symbol', help='股票代码')
    val_pct.add_argument('--metric', default='pe', help='指标 (pe/pb)')
    
    val_band = val_sub.add_parser('band', help='BAND分析')
    val_band.add_argument('symbol', help='股票代码')
    
    val_sum = val_sub.add_parser('summary', help='估值摘要')
    val_sum.add_argument('symbol', help='股票代码')
    
    # research
    research_parser = subparsers.add_parser('research', help='深度投研')
    research_parser.add_argument('symbol', help='股票代码')
    research_parser.add_argument('--phase', type=int, choices=range(1, 9), help='执行指定阶段')
    research_parser.add_argument('--full', action='store_true', help='完整分析')
    
    # earnings
    earn_parser = subparsers.add_parser('earnings', help='财报分析')
    earn_sub = earn_parser.add_subparsers(dest='earn_type', help='财报类型')
    
    earn_preview = earn_sub.add_parser('preview', help='财报预览')
    earn_preview.add_argument('symbol', help='股票代码')
    
    earn_recap = earn_sub.add_parser('recap', help='财报回顾')
    earn_recap.add_argument('symbol', help='股票代码')
    
    earn_history = earn_sub.add_parser('history', help='历史 beat/miss')
    earn_history.add_argument('symbol', help='股票代码')
    earn_history.add_argument('--quarters', type=int, default=8, help='季度数')
    
    # full
    full_parser = subparsers.add_parser('full', help='完整分析')
    full_parser.add_argument('symbol', help='股票代码')
    
    # quick
    quick_parser = subparsers.add_parser('quick', help='快速分析')
    quick_parser.add_argument('symbol', help='股票代码')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    if args.command == 'quote':
        if args.batch:
            result = get_quotes(args.batch)
        else:
            result = get_quote(args.symbol)
    
    elif args.command == 'technical':
        result = analyze_technical(args.symbol)
    
    elif args.command == 'financial':
        result = get_financial_summary(args.symbol)
    
    elif args.command == 'fundflow':
        result = get_fundflow(args.symbol, args.days)
    
    elif args.command == 'liquidity':
        result = analyze_liquidity(args.symbol, args.period)
    
    elif args.command == 'sentiment':
        result = analyze_sentiment(args.symbol, args.days)
    
    elif args.command == 'chart':
        if args.full:
            result = generate_full_chart(args.symbol, args.period)
        else:
            result = generate_chart(
                args.symbol,
                period=args.period,
                rsi=args.rsi,
                macd=args.macd,
                bb=args.bb,
                vwap=args.vwap,
                atr=args.atr
            )
    
    elif args.command == 'corr':
        if args.corr_type == 'discover':
            result = discover_correlated(args.target, args.peers)
        elif args.corr_type == 'pair':
            result = analyze_pair_correlation(args.ticker_a, args.ticker_b)
        elif args.corr_type == 'cluster':
            result = analyze_cluster(args.tickers)
        elif args.corr_type == 'rolling':
            result = analyze_rolling_correlation(args.ticker_a, args.ticker_b)
        else:
            result = {'error': '请指定相关性类型'}
    
    elif args.command == 'val':
        if args.val_type == 'percentile':
            result = calculate_percentile(args.symbol, args.metric)
        elif args.val_type == 'band':
            result = calculate_band(args.symbol)
        elif args.val_type == 'summary':
            result = get_valuation_summary(args.symbol)
        else:
            result = {'error': '请指定估值类型'}
    
    elif args.command == 'research':
        if args.full:
            result = run_research(args.symbol)
        elif args.phase:
            result = run_research(args.symbol, args.phase)
        else:
            result = run_research(args.symbol)
    
    elif args.command == 'earnings':
        if args.earn_type == 'preview':
            result = generate_earnings_preview(args.symbol)
        elif args.earn_type == 'recap':
            result = generate_earnings_recap(args.symbol)
        elif args.earn_type == 'history':
            result = get_beat_miss_history(args.symbol, args.quarters)
        else:
            result = generate_earnings_preview(args.symbol)
    
    elif args.command == 'full':
        result = full_analysis(args.symbol)
    
    elif args.command == 'quick':
        result = quick_analysis(args.symbol)
    
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
