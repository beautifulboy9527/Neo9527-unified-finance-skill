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
from features.news import (
    fetch_hot_news,
    get_unified_trends,
    get_polymarket_summary,
    get_finance_brief
)
from features.reporter import (
    plan_report,
    write_section,
    generate_full_report
)
from features.signal_tracker import (
    create_signal,
    track_signal,
    get_active_signals,
    scan_hot_stocks,
    scan_rumors
)
from features.visualizer import (
    generate_transmission_chain,
    generate_signal_radar,
    generate_sentiment_trend
)
from features.search import (
    search_ddg,
    search_baidu,
    search_jina,
    aggregate_search,
    search_finance_news
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
    
    # news
    news_parser = subparsers.add_parser('news', help='新闻聚合')
    news_sub = news_parser.add_subparsers(dest='news_type', help='新闻类型')
    
    news_fetch = news_sub.add_parser('fetch', help='获取新闻')
    news_fetch.add_argument('--source', default='cls', help='新闻源')
    news_fetch.add_argument('--count', type=int, default=15, help='数量')
    
    news_trends = news_sub.add_parser('trends', help='统一趋势')
    news_trends.add_argument('--sources', nargs='+', help='新闻源列表')
    
    news_brief = news_sub.add_parser('brief', help='财经简报')
    
    # reporter
    report_parser = subparsers.add_parser('report', help='研报生成')
    report_parser.add_argument('topic', help='研报主题')
    report_parser.add_argument('--symbol', help='股票代码')
    
    # signal
    signal_parser = subparsers.add_parser('signal', help='信号追踪')
    signal_sub = signal_parser.add_subparsers(dest='signal_type', help='信号类型')
    
    signal_create = signal_sub.add_parser('create', help='创建信号')
    signal_create.add_argument('symbol', help='股票代码')
    signal_create.add_argument('--type', choices=['bullish', 'bearish', 'neutral'], default='bullish')
    signal_create.add_argument('--thesis', required=True, help='核心论点')
    signal_create.add_argument('--confidence', type=float, default=0.5)
    
    signal_list = signal_sub.add_parser('list', help='列出信号')
    signal_list.add_argument('--symbol', help='股票代码')
    
    signal_hot = signal_sub.add_parser('hot', help='热门扫描')
    signal_rumors = signal_sub.add_parser('rumors', help='谣言扫描')
    
    # visualizer
    viz_parser = subparsers.add_parser('viz', help='可视化')
    viz_sub = viz_parser.add_subparsers(dest='viz_type', help='图表类型')
    
    viz_chain = viz_sub.add_parser('chain', help='传导链路')
    viz_chain.add_argument('--nodes', help='节点 JSON')
    
    viz_radar = viz_sub.add_parser('radar', help='信号雷达')
    viz_radar.add_argument('--sentiment', type=float, default=0.5)
    viz_radar.add_argument('--confidence', type=float, default=0.7)
    viz_radar.add_argument('--intensity', type=int, default=3)
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--engine', choices=['ddg', 'baidu', 'jina', 'all'], default='all')
    search_parser.add_argument('--max', type=int, default=5)
    
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
    
    elif args.command == 'news':
        if args.news_type == 'fetch':
            result = fetch_hot_news(args.source, args.count)
        elif args.news_type == 'trends':
            result = get_unified_trends(args.sources)
        elif args.news_type == 'brief':
            result = get_finance_brief()
        else:
            result = get_finance_brief()
    
    elif args.command == 'report':
        data = {'symbol': args.symbol} if args.symbol else {}
        result = generate_full_report(args.topic, data)
    
    elif args.command == 'signal':
        if args.signal_type == 'create':
            result = create_signal(args.symbol, args.type, args.thesis, args.confidence)
        elif args.signal_type == 'list':
            result = get_active_signals(args.symbol)
        elif args.signal_type == 'hot':
            result = scan_hot_stocks()
        elif args.signal_type == 'rumors':
            result = scan_rumors()
        else:
            result = scan_hot_stocks()
    
    elif args.command == 'viz':
        if args.viz_type == 'chain':
            nodes = json.loads(args.nodes) if args.nodes else []
            result = generate_transmission_chain(nodes)
        elif args.viz_type == 'radar':
            result = generate_signal_radar(args.sentiment, args.confidence, args.intensity)
        else:
            result = {'error': '请指定图表类型'}
    
    elif args.command == 'search':
        if args.engine == 'all':
            result = aggregate_search(args.query, max_results=args.max)
        elif args.engine == 'ddg':
            result = search_ddg(args.query, args.max)
        elif args.engine == 'baidu':
            result = search_baidu(args.query, args.max)
        elif args.engine == 'jina':
            result = search_jina(args.query, args.max)
        else:
            result = aggregate_search(args.query)
    
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
