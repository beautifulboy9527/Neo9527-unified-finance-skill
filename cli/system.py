#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: system"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cmd_data_health(args):
    """数据源健康检查 (Phase 4)"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "screener_data_source",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'screener_data_source.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    manager = module.get_screener_data_manager()
    
    print("\n" + "=" * 60)
    print("数据源健康报告")
    print("=" * 60)
    
    # 打印健康状态
    manager.print_health_report()
    
    # 测试连通性
    if args.test:
        print(f"\n测试获取股票池 ({args.scope})...")
        import time
        start = time.time()
        stocks = manager.get_stock_pool_with_fallback(args.scope)
        elapsed = time.time() - start
        
        print(f"  ✅ 成功获取 {len(stocks)} 只股票")
        print(f"  ⏱️ 响应时间: {elapsed:.2f}s")
    
    print("\n最佳数据源:", manager.get_best_source())



def cmd_doctor(args):
    """检查本地数据源状态"""
    from skills.shared import check_data_sources

    result = check_data_sources(live=args.live, sample_symbol=args.sample_symbol, suppress_proxy=args.no_proxy)
    print(f"\n数据源体检：{result['status']}")
    print(f"检查时间：{result['checked_at']}")
    print(f"摘要：{result['summary']}")
    print(f"可用数量：{result['available_count']}/{result['total_count']}")
    if result.get("live_checked"):
        print(f"实时请求成功数量：{result.get('live_success_count', 0)}")
    if result.get("proxy_suppressed"):
        print("诊断模式：已临时屏蔽 HTTP_PROXY/HTTPS_PROXY/ALL_PROXY 环境变量")
    for item in result.get("items", []):
        live_text = f"｜实时：{item.get('live_status')}｜{item.get('live_message')}" if args.live else ""
        print(f"  - {item['name']}：{item['status']}｜{item['purpose']}｜{item['action']}{live_text}")
        if args.live and item.get("live_status") == "请求失败":
            detail_parts = []
            if item.get("error_type"):
                detail_parts.append(f"类型：{item.get('error_type')}")
            if item.get("action_hint"):
                detail_parts.append(f"建议：{item.get('action_hint')}")
            if item.get("proxy_env_present"):
                detail_parts.append(f"检测到代理环境变量：{', '.join(item.get('proxy_env_vars', []))}")
            if detail_parts:
                print(f"      诊断：{'；'.join(detail_parts)}")



def cmd_ask(args):
    """自然语言金融入口"""
    from skills.shared.nl_intent_router import route_query

    routed = route_query(args.query)
    print("\n自然语言入口")
    print("=" * 60)
    print(f"识别意图: {routed.intent}")
    print(f"置信度: {routed.confidence:.0%}")
    print(f"说明: {routed.reason}")
    if routed.command_text:
        print(f"将执行: {routed.command_text}")

    for warning in routed.warnings:
        print(f"提示: {warning}")

    if args.dry_run or not routed.argv:
        return

    print("\n开始执行")
    print("=" * 60)
    original_argv = sys.argv
    sys.argv = [original_argv[0], *routed.argv]
    try:
        main()
    finally:
        sys.argv = original_argv



def cmd_workbench(args):
    """情景估值工作台"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "valuation_workbench",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'valuation_workbench.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    params = {
        'methods': args.methods,
        'discount_rate': args.discount_rate,
        'terminal_growth': args.terminal_growth,
        'fcf_growth': args.fcf_growth,
        'peer_pe': args.peer_pe,
        'peer_pb': args.peer_pb,
        'margin_of_safety': args.margin_of_safety,
        'current_price': args.current_price,
        'eps': args.eps,
        'bps': args.bps,
        'pe': args.pe,
        'pb': args.pb,
        'free_cash_flow': args.free_cash_flow,
        'shares_outstanding': args.shares_outstanding,
        'total_debt': args.total_debt,
        'cash': args.cash,
        'sector': args.sector,
        'industry': args.industry,
    }
    params = {key: value for key, value in params.items() if value is not None}
    result = module.analyze_valuation_workbench(args.symbol, **params)

    print(f"\n💼 估值工作台 {args.symbol}")
    print(f"{'='*60}")
    print(f"当前价格: {result.get('current_price') if result.get('current_price') is not None else '暂无数据'}")
    value_range = result.get('valuation_range', {})
    if result.get('success'):
        print(f"估值区间: {value_range.get('low'):.2f} - {value_range.get('high'):.2f}")
    else:
        print("估值区间: 未验证")
    print(f"结论: {result.get('conclusion')}")

    print("\n情景估值:")
    for scenario in result.get('scenarios', []):
        fair_value = scenario.get('fair_value')
        upside = scenario.get('upside')
        fair_value_text = f"{fair_value:.2f}" if fair_value is not None else "未验证"
        upside_text = f"{upside:.1%}" if upside is not None else "暂无数据"
        print(f"  - {scenario.get('name')}: 公允价值 {fair_value_text}, 上行空间 {upside_text}, 置信度 {scenario.get('valuation_confidence')}")

    warnings = result.get('warnings', [])
    if warnings:
        print("\n警告:")
        for warning in warnings[:6]:
            print(f"  - {warning}")


