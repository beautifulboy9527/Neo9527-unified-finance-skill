#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股特色数据命令 (P2): 龙虎榜/解禁/北向资金"""

import os
from datetime import datetime

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_a_share(args):
    """A股特色数据"""
    subcmd = args.a_share_subcmd

    if subcmd == "top-list":
        _cmd_top_list(args)
    elif subcmd == "lockup":
        _cmd_lockup(args)
    elif subcmd == "northbound":
        _cmd_northbound(args)
    else:
        print("未知子命令。使用: top-list, lockup, northbound")


def _cmd_top_list(args):
    """龙虎榜"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "a_share_special", os.path.join(SKILLS_DIR, "skills", "stock-skill", "a_share_special.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from skills.shared.ui import print_metric_table, print_section, get_console, HAS_RICH

    if args.recent:
        result = mod.fetch_top_list_recent(days=args.recent, symbol=args.symbol)
    else:
        result = mod.fetch_top_list(date=args.date, symbol=args.symbol)

    if not result.get("success"):
        print(f"❌ 龙虎榜获取失败: {result.get('error', result.get('message', '未知错误'))}")
        return

    console = get_console()

    # 热门股票
    if result.get("hot_stocks"):
        print_section("🔥 游资热门股", "")
        for s in result["hot_stocks"][:10]:
            print(f"  {s['symbol']} {s['name']} - 上榜 {s['count']} 次")

    # 龙虎榜明细
    items = result.get("items", [])
    if items:
        print_section(f"📋 龙虎榜明细 ({result.get('count', len(items))} 只)", "")
        for item in items[:15]:
            net = item.get("net_buy", 0)
            direction = "🟢净买入" if net and net > 0 else "🔴净卖出" if net and net < 0 else "—"
            print(f"  {item.get('symbol','')} {item.get('name','')} | {item.get('reason','')} | {direction} {abs(net or 0)/1e8:.2f}亿")
    else:
        print("  无龙虎榜数据")


def _cmd_lockup(args):
    """解禁日历"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "a_share_special", os.path.join(SKILLS_DIR, "skills", "stock-skill", "a_share_special.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from skills.shared.ui import print_section

    if args.symbol:
        result = mod.fetch_lockup_for_symbol(args.symbol)
    else:
        result = mod.fetch_lockup_calendar(days=args.days)

    if not result.get("success"):
        print(f"❌ 解禁数据获取失败: {result.get('error', result.get('message', '未知错误'))}")
        return

    items = result.get("items", [])
    if items:
        print_section(f"📅 解禁日历 ({result.get('count', len(items))} 条)", "")
        for item in items[:20]:
            shares = item.get("unlock_shares", 0)
            shares_str = f"{shares/1e4:.0f}万" if shares and shares > 1e4 else f"{shares or 0}"
            print(f"  {item.get('unlock_date','')} | {item.get('symbol', item.get('name',''))} | {shares_str}股 | {item.get('unlock_type','')}")
    else:
        print("  近期无解禁数据")


def _cmd_northbound(args):
    """北向资金"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "a_share_special", os.path.join(SKILLS_DIR, "skills", "stock-skill", "a_share_special.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from skills.shared.ui import print_metric_table, print_section

    if args.top:
        result = mod.fetch_northbound_top_stocks(date=args.date)
        if not result.get("success"):
            print(f"❌ 北向持仓获取失败: {result.get('error', '未知错误')}")
            return
        items = result.get("items", [])
        if items:
            print_section("🏦 北向资金十大持仓", "")
            for item in items[:10]:
                change = item.get("hold_change", 0)
                change_str = f"{'🟢+' if change and change > 0 else '🔴' if change and change < 0 else ''}{(change or 0)/1e4:.0f}万"
                print(f"  {item.get('symbol','')} {item.get('name','')} | 持仓变化: {change_str}")
        else:
            print("  无北向持仓数据")
    else:
        result = mod.fetch_northbound_flow(days=args.days)
        if not result.get("success"):
            print(f"❌ 北向资金获取失败: {result.get('error', '未知错误')}")
            return

        summary = result.get("summary", {})
        direction = summary.get("direction", "未知")
        total = summary.get("total_net_flow", 0)
        avg = summary.get("avg_daily_net", 0)

        direction_emoji = "🟢" if "流入" in direction else "🔴"
        print(f"\n{direction_emoji} 北向资金近 {result.get('count', 0)} 日: {direction} {abs(total)/1e8:.2f}亿 (日均 {abs(avg)/1e8:.2f}亿)")

        items = result.get("items", [])
        if items:
            for item in items[-5:]:
                net = item.get("net_flow", 0)
                emoji = "🟢" if net and net > 0 else "🔴"
                print(f"  {item.get('date','')} | {emoji} {abs(net or 0)/1e8:.2f}亿")
