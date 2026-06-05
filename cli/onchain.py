#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""链上数据 CLI 命令"""

import sys
import os
import importlib.util

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_onchain_module():
    """动态加载 onchain_data 模块"""
    spec = importlib.util.spec_from_file_location(
        "onchain_data",
        os.path.join(SKILLS_DIR, "skills", "onchain-skill", "onchain_data.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_onchain(args):
    """链上数据命令"""
    subcmd = args.onchain_subcmd

    if subcmd == "tvl":
        _cmd_tvl(args)
    elif subcmd == "protocol":
        _cmd_protocol(args)
    elif subcmd == "whale":
        _cmd_whale(args)
    else:
        print(f"未知子命令: {subcmd}")


def _cmd_tvl(args):
    """DeFi TVL 数据"""
    chain = args.chain or "Ethereum"
    try:
        mod = _load_onchain_module()
        fetcher = mod.OnchainDataFetcher()
        result = fetcher.get_defillama_data(chain)

        if result.get("error"):
            print(f"❌ 获取TVL失败: {result['error']}")
            return

        print(f"\n🏗️ {chain} DeFi 数据")
        tvl = result.get("total_tvl")
        print(f"  总TVL: " if tvl else "  总TVL: N/A")
        print(f"  24h变化: {result.get('tvl_change_24h', 'N/A')}%")
        print(f"  协议数: {result.get('protocol_count', 'N/A')}")

        top = result.get("top_protocols", [])
        if top:
            print(f"  Top协议:")
            for p in top[:5]:
                name = p.get("name", "N/A")
                ptvl = p.get("tvl")
                print(f"    • {name}: " if ptvl else f"    • {name}: N/A")

        print(f"  数据来源: DeFiLlama")

    except Exception as e:
        print(f"❌ TVL查询失败: {e}")


def _cmd_protocol(args):
    """协议详情"""
    protocol = args.protocol_name or "aave"
    try:
        import requests
        resp = requests.get(f"https://api.llama.fi/protocol/{protocol}", timeout=10)
        if resp.status_code != 200:
            print(f"❌ 协议 {protocol} 未找到")
            return
        data = resp.json()

        print(f"\n📋 {data.get('name', protocol)}")
        tvl = data.get("tvl")
        print(f"  TVL: " if tvl else "  TVL: N/A")
        print(f"  链: {', '.join(data.get('chains', [])[:5])}")
        print(f"  类别: {data.get('category', 'N/A')}")
        change_1d = data.get("change_1d")
        if change_1d is not None:
            print(f"  24h变化: {change_1d:+.2f}%")
        print(f"  数据来源: DeFiLlama")

    except Exception as e:
        print(f"❌ 协议查询失败: {e}")


def _cmd_whale(args):
    """鲸鱼追踪"""
    symbol = args.symbol or "ETH"
    chain = args.chain or "Ethereum"

    try:
        mod = _load_onchain_module()
        fetcher = mod.OnchainDataFetcher()
        result = fetcher.get_defillama_data(chain)

        if result.get("error"):
            print(f"❌ 鲸鱼数据获取失败: {result['error']}")
            return

        print(f"\n🐋 {symbol} 链上概览 ({chain})")
        tvl = result.get("total_tvl")
        print(f"  链TVL: " if tvl else "  链TVL: N/A")

        top = result.get("top_protocols", [])
        if top:
            # 大额协议 = 鲸鱼聚集
            print(f"  大额协议(鲸鱼可能聚集):")
            for p in top[:3]:
                name = p.get("name", "N/A")
                ptvl = p.get("tvl")
                print(f"    • {name}: " if ptvl else f"    • {name}")

        print(f"  ⚠️ 注意: 鲸鱼追踪需要 Etherscan/WhaleAlert API Key")
        print(f"  数据来源: DeFiLlama")

    except Exception as e:
        print(f"❌ 鲸鱼查询失败: {e}")
