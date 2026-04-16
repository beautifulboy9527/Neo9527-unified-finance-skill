#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance CLI - 统一命令行接口
"""

import sys
import os
import argparse
from datetime import datetime

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def cmd_report(args):
    """生成报告"""
    from features.report_generator_v4 import generate_crypto_report_v4
    from features.report_generator import generate_report
    
    symbol = args.symbol
    format_type = args.format
    period = args.period
    
    print(f"\n{'='*60}")
    print(f"Neo9527 Finance - Report Generation")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Period: {period}")
    print(f"Format: {format_type}")
    print(f"{'='*60}\n")
    
    # 判断资产类型
    if '-' in symbol and symbol.split('-')[1] in ['USD', 'USDT']:
        # 加密货币
        print("Detected: Cryptocurrency")
        report_path = generate_crypto_report_v4(symbol, period, format_type)
    else:
        # 股票
        print("Detected: Stock")
        report_path = generate_report(symbol, period, format_type)
    
    print(f"\n{'='*60}")
    print(f"✅ Report Generated Successfully!")
    print(f"Path: {report_path}")
    print(f"{'='*60}\n")
    
    return report_path


def cmd_analyze(args):
    """快速分析"""
    from features.complete_crypto_analyzer import analyze_complete
    
    symbol = args.symbol
    
    print(f"\n{'='*60}")
    print(f"Neo9527 Finance - Quick Analysis")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"{'='*60}\n")
    
    result = analyze_complete(symbol)
    
    # 市场数据
    market = result.get('market', {})
    if market:
        print("Market Data:")
        print(f"  Price: ${market.get('price', 0):,.2f}")
        print(f"  24h Change: {market.get('change_24h', 0):+.2f}%")
        print(f"  Volume: ${market.get('volume_24h', 0)/1e9:.2f}B")
        print(f"  Market Cap: ${market.get('market_cap', 0)/1e9:.2f}B")
    
    # 结论
    conclusion = result.get('conclusion', {})
    print(f"\nConclusion:")
    print(f"  Score: {conclusion.get('score', 0)}/100")
    print(f"  Decision: {conclusion.get('decision', 'HOLD')}")
    print(f"  Confidence: {conclusion.get('confidence', 0)}%")
    print(f"  Signals: {conclusion.get('signals_count', {})}")
    print(f"\n{conclusion.get('narrative', '')}")
    
    print(f"\n{'='*60}\n")


def cmd_signals(args):
    """信号检测"""
    from features.complete_crypto_analyzer import analyze_complete
    
    symbol = args.symbol
    
    print(f"\n{'='*60}")
    print(f"Neo9527 Finance - Signal Detection")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"{'='*60}\n")
    
    result = analyze_complete(symbol)
    signals = result.get('signals', [])
    
    if not signals:
        print("No signals detected.")
        return
    
    print(f"Total Signals: {len(signals)}\n")
    
    # 分类信号
    bullish = [s for s in signals if s['strength'] > 0]
    bearish = [s for s in signals if s['strength'] < 0]
    
    if bullish:
        print(f"📈 Bullish Signals ({len(bullish)}):")
        for s in bullish:
            print(f"  [{s['category']}] {s['name']}: {s['signal']}")
            print(f"    → {s['desc']} (strength: {s['strength']:+d})")
        print()
    
    if bearish:
        print(f"📉 Bearish Signals ({len(bearish)}):")
        for s in bearish:
            print(f"  [{s['category']}] {s['name']}: {s['signal']}")
            print(f"    → {s['desc']} (strength: {s['strength']:+d})")
        print()
    
    # 总结
    total_strength = sum(s['strength'] for s in signals)
    print(f"Total Strength: {total_strength:+d}")
    print(f"Overall: {'Bullish' if total_strength > 0 else 'Bearish' if total_strength < 0 else 'Neutral'}")
    
    print(f"\n{'='*60}\n")


def cmd_kline(args):
    """K线图数据"""
    from features.kline_chart import get_kline_data
    import json
    
    symbol = args.symbol
    period = args.period
    
    print(f"\n{'='*60}")
    print(f"Neo9527 Finance - K-Line Data")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Period: {period}")
    print(f"{'='*60}\n")
    
    data = get_kline_data(symbol, period)
    
    if 'error' in data:
        print(f"Error: {data['error']}")
        return
    
    metadata = data.get('metadata', {})
    print(f"Data Points: {metadata.get('data_points', 0)}")
    print(f"Time Range: {metadata.get('start_time', '')} ~ {metadata.get('end_time', '')}")
    print(f"Latest Price: ${metadata.get('latest_price', 0):,.2f}")
    print(f"Price Change: {metadata.get('price_change', 0):+.2f}%")
    
    print(f"\nData Summary:")
    print(f"  Candlesticks: {len(data.get('candlestick', []))}")
    print(f"  MA5: {len(data.get('ma5', []))}")
    print(f"  MA10: {len(data.get('ma10', []))}")
    print(f"  MA20: {len(data.get('ma20', []))}")
    print(f"  Volume: {len(data.get('volume', []))}")
    
    if args.save:
        output_file = f"{symbol}_kline_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Data saved to: {output_file}")
    
    print(f"\n{'='*60}\n")


def cmd_onchain(args):
    """链上数据"""
    from features.onchain_data import get_onchain_data
    
    symbol = args.symbol
    
    print(f"\n{'='*60}")
    print(f"Neo9527 Finance - On-Chain Data")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"{'='*60}\n")
    
    data = get_onchain_data(symbol)
    
    # 网络数据
    if 'network' in data and 'error' not in data['network']:
        network = data['network']
        print("Network Metrics:")
        print(f"  Hashrate: {network.get('hashrate', 0):.2f} EH/s")
        print(f"  Difficulty: {network.get('difficulty', 0):.2f} T")
        print(f"  Total Supply: {network.get('total_btc', 0):,.0f}")
        print()
    
    # DeFi 数据
    if 'defi' in data and 'error' not in data['defi']:
        defi = data['defi']
        print("DeFi Metrics:")
        print(f"  Total TVL: ${defi.get('total_tvl', 0):,.0f}")
        print(f"  TVL Change: {defi.get('tvl_change_24h', 0):+.2f}%")
        print(f"  Protocols: {defi.get('protocol_count', 0)}")
        print()
    
    # 鲸鱼数据
    if 'whale' in data and 'error' not in data['whale']:
        whale = data['whale']
        print("Whale Activity:")
        print(f"  Net Flow: {whale.get('net_flow', 0):+,}")
        print(f"  Status: {whale.get('whale_activity', 'N/A')}")
        print(f"  Signal: {whale.get('signal_desc', 'N/A')}")
        print()
    
    print(f"{'='*60}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Neo9527 Finance - Unified Finance Analysis CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report
  python finance.py report BTC-USD --format html
  
  # Quick analysis
  python finance.py analyze ETH-USD
  
  # Signal detection
  python finance.py signals BTC-USD
  
  # K-line data
  python finance.py kline BTC-USD --period 3mo --save
  
  # On-chain data
  python finance.py onchain BTC
        """
    )
    
    parser.add_argument('--version', action='version', version='Neo9527 Finance v4.2')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='Generate analysis report')
    report_parser.add_argument('symbol', help='Symbol (e.g., BTC-USD, AAPL)')
    report_parser.add_argument('--format', '-f', default='html', choices=['html', 'markdown', 'pdf'], help='Output format')
    report_parser.add_argument('--period', '-p', default='medium', choices=['short', 'medium', 'long'], help='Investment period')
    report_parser.set_defaults(func=cmd_report)
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='Quick analysis')
    analyze_parser.add_argument('symbol', help='Symbol')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # signals 命令
    signals_parser = subparsers.add_parser('signals', help='Signal detection')
    signals_parser.add_argument('symbol', help='Symbol')
    signals_parser.set_defaults(func=cmd_signals)
    
    # kline 命令
    kline_parser = subparsers.add_parser('kline', help='K-line chart data')
    kline_parser.add_argument('symbol', help='Symbol')
    kline_parser.add_argument('--period', '-p', default='3mo', help='Time period (e.g., 1mo, 3mo, 6mo)')
    kline_parser.add_argument('--save', '-s', action='store_true', help='Save to JSON file')
    kline_parser.set_defaults(func=cmd_kline)
    
    # onchain 命令
    onchain_parser = subparsers.add_parser('onchain', help='On-chain data')
    onchain_parser.add_argument('symbol', help='Symbol (BTC, ETH)')
    onchain_parser.set_defaults(func=cmd_onchain)
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # 执行命令
    args.func(args)


if __name__ == '__main__':
    main()
