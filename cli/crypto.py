#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""加密货币 CLI 命令"""

import sys
import os

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_crypto(args):
    """加密货币命令"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "crypto_skill", os.path.join(SKILLS_DIR, "skills", "crypto-skill", "crypto.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    subcmd = args.crypto_subcmd

    if subcmd == "quote":
        symbol = args.symbol or "BTC/USDT"
        exchange = args.exchange or "binance"
        result = mod.get_crypto_quote(symbol, exchange)
        _print_crypto_quote(result, symbol)

    elif subcmd == "orderbook":
        symbol = args.symbol or "BTC/USDT"
        exchange = args.exchange or "binance"
        result = mod.get_orderbook(symbol, exchange)
        _print_orderbook(result, symbol)

    elif subcmd == "kline":
        symbol = args.symbol or "BTC/USDT"
        timeframe = args.timeframe or "1d"
        exchange = args.exchange or "binance"
        limit = args.limit or 30
        result = mod.get_ohlcv(symbol, timeframe, exchange, limit)
        _print_kline(result, symbol)

    elif subcmd == "trending":
        exchange = args.exchange or "binance"
        result = mod.get_trending(exchange)
        _print_trending(result)

    elif subcmd == "search":
        keyword = args.keyword or "bitcoin"
        exchange = args.exchange or "binance"
        result = mod.search_markets(keyword, exchange)
        _print_search(result)

    elif subcmd == "multi":
        symbol = args.symbol or "BTC/USDT"
        result = mod.get_multi_exchange_quote(symbol)
        _print_multi(result, symbol)

    elif subcmd == "analyze":
        symbol = args.symbol or "BTC/USDT"
        # Use complete_crypto_analyzer
        spec2 = importlib.util.spec_from_file_location(
            "complete_crypto",
            os.path.join(SKILLS_DIR, "skills", "crypto-skill", "complete_crypto_analyzer.py")
        )
        mod2 = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod2)
        result = mod2.analyze_complete(symbol)
        _print_analysis(result, symbol)

    else:
        print(f"未知子命令: {subcmd}")


def _print_crypto_quote(result, symbol):
    if not result or result.get("error"):
        print(f"❌ 无法获取 {symbol} 行情")
        if result and result.get("error"):
            print(f"   原因: {result['error']}")
        return
    print(f"\n📊 {symbol} 行情")
    print(f"  交易所: {result.get('exchange', 'N/A')}")
    price = result.get("price")
    print(f"  价格: {price if price is not None else 'N/A'}")
    print(f"  24h变化: {result.get('change_24h', 'N/A')}%")
    print(f"  24h成交量: {result.get('volume_24h', 'N/A')}")
    print(f"  数据来源: {result.get('source', 'N/A')}")


def _print_orderbook(result, symbol):
    if not result or result.get("error"):
        print(f"❌ 无法获取 {symbol} 订单簿")
        return
    print(f"\n📖 {symbol} 订单簿")
    bids = result.get("bids", [])[:5]
    asks = result.get("asks", [])[:5]
    if bids:
        print("  买盘 (Top 5):")
        for b in bids:
            print(f"    {b[0]:.2f} × {b[1]:.6f}")
    if asks:
        print("  卖盘 (Top 5):")
        for a in asks:
            print(f"    {a[0]:.2f} × {a[1]:.6f}")


def _print_kline(result, symbol):
    if not result or result.get("error"):
        print(f"❌ 无法获取 {symbol} K线")
        return
    print(f"\n📈 {symbol} K线")
    ohlcv = result.get("ohlcv", [])
    for row in ohlcv[-10:]:
        print(f"  {row}")


def _print_trending(result):
    if not result or result.get("error"):
        print("❌ 无法获取热门币种")
        return
    print("\n🔥 热门币种")
    for item in result.get("trending", [])[:10]:
        print(f"  {item.get('symbol', 'N/A')} - {item.get('name', 'N/A')}")


def _print_search(result):
    if not result or result.get("error"):
        print("❌ 搜索失败")
        return
    print("\n🔍 搜索结果")
    for item in result.get("markets", [])[:10]:
        print(f"  {item.get('symbol', 'N/A')} - {item.get('name', 'N/A')} ({item.get('exchange', 'N/A')})")


def _print_multi(result, symbol):
    if not result or result.get("error"):
        print(f"❌ 无法获取 {symbol} 多交易所行情")
        return
    print(f"\n💱 {symbol} 多交易所对比")
    for exchange, data in result.get("exchanges", {}).items():
        price = data.get("price")
        print(f"  {exchange}: {price if price is not None else 'N/A'}")


def _print_analysis(result, symbol):
    if not result or result.get("error"):
        print(f"❌ 无法分析 {symbol}")
        if result and result.get("error"):
            print(f"   原因: {result['error']}")
        return
    print(f"\n🔬 {symbol} 综合分析")
    market = result.get("market_data", {})
    tech = result.get("technical", {})
    signals = result.get("signals", [])
    conclusion = result.get("conclusion", {})

    print(f"  数据获取: {'✅' if result.get('data_fetched') else '❌'}")
    if market:
        price = market.get("price")
        print(f"  价格: {price if price is not None else 'N/A'}")
        print(f"  24h变化: {market.get('change_24h', 'N/A')}%")
    if tech:
        print(f"  RSI: {tech.get('rsi', 'N/A')}")
        print(f"  趋势: {tech.get('trend', 'N/A')}")
    if signals:
        print(f"  信号数: {len(signals)}")
        for s in signals[:3]:
            print(f"    • {s.get('type', 'N/A')}: {s.get('description', 'N/A')}")
    if conclusion:
        print(f"  结论: {conclusion.get('view', 'N/A')}")
        print(f"  风险: {conclusion.get('risk', 'N/A')}")
