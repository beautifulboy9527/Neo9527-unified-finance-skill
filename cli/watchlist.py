#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: watchlist"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cmd_watchlist(args):
    """自选股管理 (Phase 5)"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "watchlist_manager",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'watchlist_manager.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    skill = module.WatchlistSkill()
    
    if args.watchlist_action == 'list':
        result = skill.execute('list', group=args.group, priority=args.priority)
        print(f"\n📊 自选股列表 ({result['count']} 个):")
        for item in result['items']:
            target_str = f"目标:{item['target']}" if item['target'] else ""
            stop_str = f"止损:{item['stop']}" if item['stop'] else ""
            print(f"  [{item['id']}] {item['symbol']} | {target_str} {stop_str} | {item['group']} | {item['priority']}")
            if item['notes']:
                print(f"      备注: {item['notes']}")
    
    elif args.watchlist_action == 'add':
        result = skill.execute('add',
            symbol=args.symbol,
            target=args.target,
            stop=args.stop,
            notes=args.notes or "",
            group=args.group or "默认",
            priority=args.priority or "中"
        )
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"⚠️ {result['message']}")
    
    elif args.watchlist_action == 'remove':
        result = skill.execute('remove', id=args.id)
        print(f"{'✅' if result['success'] else '❌'} {result['message']}")
    
    elif args.watchlist_action == 'check':
        result = skill.execute('check')
        print(f"\n🔍 检查结果 ({result['checked_count']} 个已检查):")
        if result['triggered']:
            print(f"  ⚠️ 触发警报 ({result['triggered_count']} 个):")
            for t in result['triggered']:
                print(f"    [{t['priority']}] {t['symbol']}: {t['message']}")
        else:
            print("  ✓ 无触发警报")
        if result['errors']:
            print(f"  ❌ 检查失败 ({len(result['errors'])} 个):")
            for e in result['errors']:
                print(f"    {e['symbol']}: {e['error']}")
    
    elif args.watchlist_action == 'summary':
        result = skill.execute('summary')
        print(f"\n📊 自选股统计:")
        print(f"  总数: {result['total']} | 启用: {result['enabled']} | 禁用: {result['disabled']}")
        print(f"  优先级: 高 {result['priority_distribution']['高']} | 中 {result['priority_distribution']['中']} | 低 {result['priority_distribution']['低']}")
        print(f"  监控设置: 目标价 {result['monitoring']['has_target']} | 止损价 {result['monitoring']['has_stop']} | 双向 {result['monitoring']['has_both']}")
    
    elif args.watchlist_action == 'groups':
        result = skill.execute('list_groups')
        print(f"\n📁 分组列表:")
        for group in result['groups']:
            count = result['stats'].get(group, 0)
            print(f"  {group}: {count} 个")



def cmd_alerts(args):
    """股票风险预警"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "risk_alerts",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'risk_alerts.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    symbols = args.symbols
    print(f"\n🚨 风险预警: {', '.join(symbols)}")
    result = module.analyze_watchlist_alerts(symbols)

    for item in result.get('items', []):
        print(f"\n{'='*60}")
        print(f" {item['symbol']} | 最高级别: {item['highest_severity_cn']} | 告警数: {item['alert_count']}")
        print(f"{'='*60}")
        print(item.get('summary', '暂无摘要'))
        for alert in item.get('alerts', [])[:8]:
            verified = '已验证' if alert.get('verified') else '待验证'
            print(f"  - [{alert['severity_cn']}] {alert['title']} ({verified})")
            print(f"    {alert['message']}")



def cmd_monitor(args):
    """生成自选股监控面板"""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "watchlist_monitor",
        os.path.join(SKILLS_DIR, "skills", "stock-skill", "watchlist_monitor.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    monitor = module.WatchlistMonitor()
    result = monitor.monitor(monitor.load_csv(args.watchlist_csv))

    output_dir = Path(args.output_dir or os.path.join(SKILLS_DIR, "outputs", "html_reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"STOCK_watchlist_monitor_{timestamp}.html"
    monitor.generate_html(result, str(output_path))

    print(f"\n自选股监控面板已生成：{output_path}")
    print(result.get("summary", "暂无监控摘要"))
    for item in result.get("items", [])[:args.top]:
        alerts = "；".join(alert["title"] for alert in item.get("alerts", [])[:3]) or "暂无触发"
        print(f"  - {item['display_name']}｜{item['highest_severity']}｜{item['status']}｜{alerts}")

    if args.generate_review_reports:
        review_items = [
            item for item in result.get("items", [])
            if item.get("highest_severity") in {"高", "中"} and item.get("alert_count", 0) > 0
        ]
        args.report_source = "自选股监控"
        ranked = {"items": review_items}
        generated = _generate_reports_from_shortlist(ranked, args, output_dir)
        if generated:
            print("\n已为触发监控条件的股票生成复核版投研报告：")
            for path in generated:
                print(f"  - {path}")

    if args.generate_plan:
        plan_paths = _generate_investment_plan(result, output_dir)
        print("\n投资跟踪计划已生成：")
        for path in plan_paths:
            print(f"  - {path}")


def _generate_investment_plan(monitor_result, output_dir):
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "investment_plan",
        os.path.join(SKILLS_DIR, "skills", "stock-skill", "investment_plan.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    builder = module.InvestmentPlanBuilder()
    plan = builder.build(monitor_result)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = Path(output_dir) / f"STOCK_investment_plan_{timestamp}.html"
    csv_path = Path(output_dir) / f"STOCK_investment_plan_{timestamp}.csv"
    builder.generate_html(plan, str(html_path))
    builder.write_csv(plan, str(csv_path))
    return [html_path, csv_path]


def _generate_reports_from_shortlist(ranked, args, output_dir):
    import importlib.util
    from pathlib import Path

    from skills.shared import check_data_sources, stock_display_name

    def load_module(name, relative_path):
        spec = importlib.util.spec_from_file_location(name, os.path.join(SKILLS_DIR, relative_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    health_module = load_module("financial_health", os.path.join("skills", "stock-skill", "financial_health.py"))
    workbench_module = load_module("valuation_workbench", os.path.join("skills", "stock-skill", "valuation_workbench.py"))
    risk_module = load_module("risk_alerts", os.path.join("skills", "stock-skill", "risk_alerts.py"))
    collector_module = load_module("stock_data_collector", os.path.join("skills", "stock-skill", "stock_data_collector.py"))
    report_module = load_module("kami_style_report", os.path.join("skills", "stock-skill", "kami_style_report.py"))

    generated = []
    count = min(args.report_count, len(ranked.get("items", [])))
    for item in ranked.get("items", [])[:count]:
        symbol = item.get("symbol")
        inputs = item.get("inputs", {})
        if not symbol:
            continue

        data_sources = check_data_sources()
        collected_data = collector_module.collect_stock_data(symbol)
        price_csv = _find_price_csv_for_symbol(symbol, args.price_dir)
        if price_csv:
            csv_data = collector_module.collect_price_csv(str(price_csv), symbol=symbol, timeframe="日线")
            if csv_data.get("technical_analysis"):
                collected_data["technical_analysis"] = csv_data["technical_analysis"]
            if csv_data.get("market_data", {}).get("price") is not None:
                collected_data.setdefault("market_data", {}).update(csv_data.get("market_data", {}))
                collected_data.setdefault("valuation_fields", {}).update(csv_data.get("valuation_fields", {}))
            collected_data.setdefault("warnings", []).extend(csv_data.get("warnings", []))
            collected_data.setdefault("sources", []).extend(csv_data.get("sources", []))
            collected_data["success"] = collected_data.get("success") or csv_data.get("success", False)

        data_sources["collection"] = {
            "success": collected_data.get("success", False),
            "warnings": collected_data.get("warnings", []),
            "sources": collected_data.get("sources", []),
        }

        health_params = {
            "gross_margin": inputs.get("gross_margin"),
            "net_margin": inputs.get("net_margin"),
            "roe": inputs.get("roe"),
            "debt_ratio": inputs.get("debt_ratio"),
            "revenue_growth": inputs.get("revenue_growth"),
            "profit_growth": inputs.get("profit_growth"),
        }
        health_params = {key: value for key, value in health_params.items() if value is not None}
        valuation_params = {
            "current_price": inputs.get("current_price"),
            "pe": inputs.get("pe"),
            "pb": inputs.get("pb"),
            "peer_pe": inputs.get("pe"),
            "peer_pb": inputs.get("pb"),
            "sector": inputs.get("industry"),
            "industry": inputs.get("industry"),
        }
        valuation_params = {key: value for key, value in valuation_params.items() if value is not None}

        merged_health_params = dict(collected_data.get("financial_fields", {}))
        merged_health_params.update(health_params)
        merged_valuation_params = dict(collected_data.get("valuation_fields", {}))
        merged_valuation_params.update(valuation_params)

        financial_health = health_module.analyze_financial_health(symbol, **merged_health_params)
        valuation_workbench = workbench_module.analyze_valuation_workbench(symbol, **merged_valuation_params)
        alerts_result = risk_module.analyze_watchlist_alerts([symbol])
        risk_alerts = alerts_result.get("items", [{}])[0] if alerts_result.get("items") else {}
        report_source = getattr(args, "report_source", "机会短名单")
        fundamental = {
            **collected_data.get("fundamental_analysis", {}),
            "industry": inputs.get("industry") or collected_data.get("fundamental_analysis", {}).get("industry") or "行业信息暂未验证",
            "business_summary": f"{item.get('display_name')}来自{report_source}，触发或入选理由包括：" + "；".join(item.get("reasons", [])[:4]) + "。",
        }
        technical = dict(collected_data.get("technical_analysis", {}))
        if not technical and inputs.get("trend"):
            technical = {"timeframe": "日线", "trend": inputs.get("trend"), "rsi14": inputs.get("rsi14")}

        html_text = report_module.KamiStyleStockReport().generate(
            symbol,
            display_name=stock_display_name(symbol, {"name": item.get("display_name"), "industry": inputs.get("industry")}),
            financial_health=financial_health,
            valuation_workbench=valuation_workbench,
            risk_alerts=risk_alerts,
            technical_analysis=technical,
            fundamental_analysis=fundamental,
            data_sources=data_sources,
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(output_dir) / f"STOCK_{symbol}_kami_from_discover_{timestamp}.html"
        report_path.write_text(html_text, encoding="utf-8")
        generated.append(report_path)
    return generated


def _find_price_csv_for_symbol(symbol, price_dir):
    if not price_dir:
        return None
    from pathlib import Path

    directory = Path(price_dir)
    if not directory.exists():
        return None
    candidates = [
        directory / f"{symbol}.csv",
        directory / f"{symbol}_prices.csv",
        directory / f"{symbol}_prices_sample.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    matches = sorted(directory.glob(f"*{symbol}*.csv"))
    return matches[0] if matches else None


