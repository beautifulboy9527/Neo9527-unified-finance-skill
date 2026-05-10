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
        print(f" {symbol} - {result['data'].get('name', '暂无数据')}")
        print(f"{'='*60}")
        print(f"市场: {result['market']}")
        print(f"评分: {result['score']}/100")
        
        tech = result['data'].get('technical', {})
        if tech:
            print(f"\n技术指标:")
            print(f"  趋势: {tech.get('trend', '暂无数据')}")
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


def cmd_health(args):
    """财报体检评分"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "financial_health",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'financial_health.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    analyze_financial_health = module.analyze_financial_health

    symbol = args.symbol
    print(f"\n🧾 财报体检 {symbol}...")

    params = {
        'gross_margin': args.gross_margin,
        'net_margin': args.net_margin,
        'roe': args.roe,
        'debt_ratio': args.debt_ratio,
        'revenue_growth': args.revenue_growth,
        'profit_growth': args.profit_growth,
        'receivable_growth': args.receivable_growth,
        'inventory_growth': args.inventory_growth,
        'operating_cash_flow': args.operating_cash_flow,
        'net_income': args.net_income,
    }
    params = {key: value for key, value in params.items() if value is not None}
    result = analyze_financial_health(symbol, **params)
    print(f"\n{'='*60}")
    print(f" {symbol} 财报体检")
    print(f"{'='*60}")
    print(f"健康分: {result.get('health_score') if result.get('health_score') is not None else '未验证'}")
    print(f"等级: {result.get('health_grade')}")
    print(f"数据完整度: {result.get('data_completeness', 0):.0%}")
    print(f"结论: {result.get('conclusion')}")

    dimensions = result.get('dimensions', {})
    if dimensions:
        print("\n分项体检:")
        for item in dimensions.values():
            score = item.get('score') if item.get('score') is not None else '未验证'
            print(f"  - {item.get('name')}: {score} ({item.get('status')}) - {item.get('reason')}")

    flags = result.get('risk_flags', [])
    if flags:
        print("\n风险与验证:")
        for flag in flags[:6]:
            print(f"  - {flag}")


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


def cmd_doctor(args):
    """检查本地数据源状态"""
    from skills.shared import check_data_sources

    result = check_data_sources(live=args.live, sample_symbol=args.sample_symbol)
    print(f"\n数据源体检：{result['status']}")
    print(f"检查时间：{result['checked_at']}")
    print(f"摘要：{result['summary']}")
    print(f"可用数量：{result['available_count']}/{result['total_count']}")
    if result.get("live_checked"):
        print(f"实时请求成功数量：{result.get('live_success_count', 0)}")
    for item in result.get("items", []):
        live_text = f"｜实时：{item.get('live_status')}｜{item.get('live_message')}" if args.live else ""
        print(f"  - {item['name']}：{item['status']}｜{item['purpose']}｜{item['action']}{live_text}")


def cmd_report(args):
    """生成完整 HTML 研究报告"""
    import importlib.util
    from pathlib import Path

    from skills.shared import check_data_sources, stock_display_name

    def load_module(name, relative_path):
        spec = importlib.util.spec_from_file_location(
            name,
            os.path.join(SKILLS_DIR, relative_path)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    health_module = load_module("financial_health", os.path.join("skills", "stock-skill", "financial_health.py"))
    workbench_module = load_module("valuation_workbench", os.path.join("skills", "stock-skill", "valuation_workbench.py"))
    risk_module = load_module("risk_alerts", os.path.join("skills", "stock-skill", "risk_alerts.py"))
    collector_module = load_module("stock_data_collector", os.path.join("skills", "stock-skill", "stock_data_collector.py"))
    preflight_module = load_module("report_preflight", os.path.join("skills", "stock-skill", "report_preflight.py"))

    if args.style == "apple":
        report_module = load_module("apple_style_report", os.path.join("skills", "stock-skill", "apple_style_report.py"))
        ReportClass = report_module.AppleStyleStockReport
        suffix = "apple_full"
    else:
        report_module = load_module("kami_style_report", os.path.join("skills", "stock-skill", "kami_style_report.py"))
        ReportClass = report_module.KamiStyleStockReport
        suffix = "kami_full"

    health_params = {
        'gross_margin': args.gross_margin,
        'net_margin': args.net_margin,
        'roe': args.roe,
        'debt_ratio': args.debt_ratio,
        'revenue_growth': args.revenue_growth,
        'profit_growth': args.profit_growth,
        'receivable_growth': args.receivable_growth,
        'inventory_growth': args.inventory_growth,
        'operating_cash_flow': args.operating_cash_flow,
        'net_income': args.net_income,
    }
    health_params = {key: value for key, value in health_params.items() if value is not None}

    valuation_params = {
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
    valuation_params = {key: value for key, value in valuation_params.items() if value is not None}

    print(f"\n生成 {args.symbol} 完整 HTML 报告，风格：{args.style}")
    data_sources = check_data_sources(
        live=args.live_data_check,
        sample_symbol=args.symbol if str(args.symbol).isdigit() else "002050",
    )
    if args.offline_input_only:
        collected_data = {
            "success": False,
            "symbol": args.symbol,
            "market": "manual",
            "profile": {},
            "market_data": {},
            "technical_analysis": {},
            "financial_fields": {},
            "valuation_fields": {},
            "fundamental_analysis": {},
            "warnings": ["离线输入模式：未请求行情、财报和风险接口。"],
            "sources": ["外部输入字段"],
        }
    else:
        collected_data = collector_module.collect_stock_data(args.symbol)
    if args.price_csv:
        csv_data = collector_module.collect_price_csv(args.price_csv, symbol=args.symbol, timeframe=args.timeframe)
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
    if args.require_technical_data and not collected_data.get("technical_analysis", {}).get("candles"):
        print("未生成报告：没有取得可验证 K 线数据，无法展示技术面、支撑位和压力位。")
        print("可使用 --price-csv 传入真实 K 线 CSV，或先运行 doctor --live 检查实时接口。")
        return

    merged_health_params = dict(collected_data.get("financial_fields", {}))
    merged_health_params.update(health_params)
    merged_valuation_params = dict(collected_data.get("valuation_fields", {}))
    merged_valuation_params.update(valuation_params)
    if args.offline_input_only:
        merged_valuation_params["skip_external_data"] = True

    financial_health = health_module.analyze_financial_health(args.symbol, **merged_health_params)
    valuation_workbench = workbench_module.analyze_valuation_workbench(args.symbol, **merged_valuation_params)
    if args.offline_input_only:
        risk_alerts = {
            "symbol": args.symbol,
            "highest_severity_cn": "提示",
            "alert_count": 0,
            "alerts": [],
            "summary": "当前输入未显示突出风险，需结合公告和财报持续复核。",
        }
    else:
        alerts_result = risk_module.analyze_watchlist_alerts([args.symbol])
        risk_alerts = alerts_result.get("items", [{}])[0] if alerts_result.get("items") else {}
    risk_alerts = preflight_module.reconcile_risk_alerts_with_financials(risk_alerts, financial_health)

    fundamental = {
        **collected_data.get("fundamental_analysis", {}),
        "industry": args.industry or collected_data.get("fundamental_analysis", {}).get("industry") or "行业信息暂未验证",
        "business_summary": args.business_summary or collected_data.get("fundamental_analysis", {}).get("business_summary"),
        "moat": args.moat,
    }
    technical = dict(collected_data.get("technical_analysis", {}))
    if args.trend:
        technical.update({"timeframe": args.timeframe, "trend": args.trend})

    preflight_collected = {
        **collected_data,
        "financial_fields": merged_health_params,
        "valuation_fields": merged_valuation_params,
    }
    if merged_valuation_params.get("current_price") is not None:
        preflight_collected.setdefault("market_data", {})
        preflight_collected["market_data"] = {
            **preflight_collected.get("market_data", {}),
            "price": merged_valuation_params.get("current_price"),
        }
    preflight = preflight_module.assess_report_readiness(
        symbol=args.symbol,
        display_name=stock_display_name(args.symbol, collected_data.get("profile", {})),
        collected_data=preflight_collected,
        financial_health=financial_health,
        valuation_workbench=valuation_workbench,
        technical_analysis=technical,
        fundamental_analysis=fundamental,
        mode="full",
        enforce_freshness=args.enforce_freshness,
        max_price_age_days=args.max_price_age_days,
    )
    data_sources["preflight"] = preflight
    print(f"报告材料检查：{preflight['status']}｜{preflight['message']}")
    if preflight.get("blocking_issues"):
        for issue in preflight["blocking_issues"]:
            print(f"  - {issue}")
    if args.strict_data and not preflight.get("can_generate"):
        print("未生成报告：正式报告模式要求核心数据齐备。")
        return

    html_text = ReportClass().generate(
        args.symbol,
        display_name=stock_display_name(args.symbol, collected_data.get("profile", {})),
        financial_health=financial_health,
        valuation_workbench=valuation_workbench,
        risk_alerts=risk_alerts,
        technical_analysis=technical,
        fundamental_analysis=fundamental,
        data_sources=data_sources,
    )

    output_dir = Path(args.output_dir or os.path.join(SKILLS_DIR, "outputs", "html_reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"STOCK_{args.symbol}_{suffix}_{timestamp}.html"
    output_path.write_text(html_text, encoding="utf-8")

    print(f"报告已生成：{output_path}")
    print(f"数据源状态：{data_sources['status']}｜{data_sources['summary']}")
    print("提示：若正式使用，请补充真实数据源或外部可验证字段，并复核资料截止日期。")


def cmd_discover(args):
    """从真实候选池生成机会短名单"""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "opportunity_pipeline",
        os.path.join(SKILLS_DIR, "skills", "stock-skill", "opportunity_pipeline.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    pipeline = module.OpportunityPipeline()
    candidates = pipeline.load_csv(args.candidate_csv)
    ranked = pipeline.rank(candidates, top=args.top)

    output_dir = Path(args.output_dir or os.path.join(SKILLS_DIR, "outputs", "html_reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"STOCK_opportunity_shortlist_{timestamp}.html"
    pipeline.generate_html(ranked, str(output_path))

    print(f"\n机会短名单已生成：{output_path}")
    print(f"候选总数：{ranked.get('total_candidates', 0)}，短名单数量：{len(ranked.get('items', []))}")
    for index, item in enumerate(ranked.get("items", [])[:args.top], 1):
        reasons = "；".join(item.get("reasons", [])[:2]) or "暂无明确优势"
        print(f"  {index}. {item['display_name']}｜{item['view']}｜机会分 {item['score']:.0f}｜{reasons}")
    for warning in ranked.get("warnings", []):
        print(f"提示：{warning}")

    if args.generate_reports:
        generated = _generate_reports_from_shortlist(ranked, args, output_dir)
        if generated:
            print("\n已为短名单生成完整投研报告：")
            for path in generated:
                print(f"  - {path}")


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
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "deep_research_analyzer",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'deep-research', 'analyzer.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    StockAnalyzer = module.StockAnalyzer
    InvestmentStyle = module.InvestmentStyle
    
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


def cmd_board(args):
    """打板筛选"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "board_scanner",
        os.path.join(SKILLS_DIR, 'scripts', 'features', 'board_scanner.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    scan_type = args.type
    print(f"\n🎯 打板筛选 ({scan_type})...")
    
    if scan_type == 'limit-up':
        result = module.scan_limit_up()
    elif scan_type == 'strong':
        result = module.scan_strong_stocks()
    elif scan_type == 'continuous':
        result = module.scan_continuous_boards()
    elif scan_type == 'market':
        result = module.analyze_market_sentiment()
    elif scan_type == 'opportunities':
        result = module.identify_opportunities()
    else:
        result = module.analyze_market_sentiment()
    
    print(f"\n结果: {result}")


def cmd_earnings(args):
    """财报分析 - 完整财报分析 (预测 + 回顾 + 比较)"""
    import importlib.util
    
    # 设置正确的路径
    stock_skill_dir = os.path.join(SKILLS_DIR, 'skills', 'stock-skill')
    if stock_skill_dir not in sys.path:
        sys.path.insert(0, stock_skill_dir)
    
    # 动态导入 earnings_cli
    spec = importlib.util.spec_from_file_location(
        "earnings_cli",
        os.path.join(stock_skill_dir, 'earnings_cli.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    symbol = args.symbol.upper()
    
    print(f"\n{'='*60}")
    print(f"📊 完整财报分析 - {symbol}")
    print(f"{'='*60}\n")
    
    # 设置 sys.argv 并运行
    original_argv = sys.argv
    sys.argv = ['earnings_cli', 'all', symbol]
    try:
        module.main()
    finally:
        sys.argv = original_argv


def cmd_preview(args):
    """财报预测"""
    import importlib.util
    
    stock_skill_dir = os.path.join(SKILLS_DIR, 'skills', 'stock-skill')
    if stock_skill_dir not in sys.path:
        sys.path.insert(0, stock_skill_dir)
    
    spec = importlib.util.spec_from_file_location(
        "earnings_cli",
        os.path.join(stock_skill_dir, 'earnings_cli.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    symbol = args.symbol.upper()
    periods = args.periods if hasattr(args, 'periods') else 4
    
    original_argv = sys.argv
    sys.argv = ['earnings_cli', 'preview', symbol, str(periods)]
    try:
        module.main()
    finally:
        sys.argv = original_argv


def cmd_recap(args):
    """财报回顾"""
    import importlib.util
    
    stock_skill_dir = os.path.join(SKILLS_DIR, 'skills', 'stock-skill')
    if stock_skill_dir not in sys.path:
        sys.path.insert(0, stock_skill_dir)
    
    spec = importlib.util.spec_from_file_location(
        "earnings_cli",
        os.path.join(stock_skill_dir, 'earnings_cli.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    symbol = args.symbol.upper()
    
    original_argv = sys.argv
    sys.argv = ['earnings_cli', 'recap', symbol]
    try:
        module.main()
    finally:
        sys.argv = original_argv


def cmd_compare(args):
    """业绩比较"""
    import importlib.util
    
    stock_skill_dir = os.path.join(SKILLS_DIR, 'skills', 'stock-skill')
    if stock_skill_dir not in sys.path:
        sys.path.insert(0, stock_skill_dir)
    
    spec = importlib.util.spec_from_file_location(
        "earnings_cli",
        os.path.join(stock_skill_dir, 'earnings_cli.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    symbols = [s.upper() for s in args.symbols]
    
    original_argv = sys.argv
    sys.argv = ['earnings_cli', 'compare'] + symbols
    try:
        module.main()
    finally:
        sys.argv = original_argv


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

    # health 命令
    parser_health = subparsers.add_parser('health', help='财报体检评分')
    parser_health.add_argument('symbol', help='股票代码')
    parser_health.add_argument('--gross-margin', type=float, help='外部传入毛利率(%)')
    parser_health.add_argument('--net-margin', type=float, help='外部传入净利率(%)')
    parser_health.add_argument('--roe', type=float, help='外部传入ROE(%)')
    parser_health.add_argument('--debt-ratio', type=float, help='外部传入资产负债率(%)')
    parser_health.add_argument('--revenue-growth', type=float, help='外部传入收入增速(%)')
    parser_health.add_argument('--profit-growth', type=float, help='外部传入利润增速(%)')
    parser_health.add_argument('--receivable-growth', type=float, help='外部传入应收账款增速(%)')
    parser_health.add_argument('--inventory-growth', type=float, help='外部传入存货增速(%)')
    parser_health.add_argument('--operating-cash-flow', type=float, help='外部传入经营现金流')
    parser_health.add_argument('--net-income', type=float, help='外部传入净利润')
    parser_health.set_defaults(func=cmd_health)

    # alerts 命令
    parser_alerts = subparsers.add_parser('alerts', help='股票/自选股风险预警')
    parser_alerts.add_argument('symbols', nargs='+', help='股票代码，可输入多个')
    parser_alerts.set_defaults(func=cmd_alerts)

    # workbench 命令
    parser_workbench = subparsers.add_parser('workbench', help='情景估值工作台')
    parser_workbench.add_argument('symbol', help='股票代码')
    parser_workbench.add_argument('--methods', default='all', choices=['all', 'dcf', 'relative', 'ddm'], help='估值方法')
    parser_workbench.add_argument('--discount-rate', type=float, help='折现率/WACC，例如 0.10')
    parser_workbench.add_argument('--terminal-growth', type=float, help='永续增长率，例如 0.025')
    parser_workbench.add_argument('--fcf-growth', type=float, help='自由现金流增长率，例如 0.04')
    parser_workbench.add_argument('--peer-pe', type=float, help='可比公司PE中位数')
    parser_workbench.add_argument('--peer-pb', type=float, help='可比公司PB中位数')
    parser_workbench.add_argument('--margin-of-safety', type=float, help='安全边际，例如 0.30')
    parser_workbench.add_argument('--current-price', type=float, help='外部传入当前价格')
    parser_workbench.add_argument('--eps', type=float, help='外部传入每股收益')
    parser_workbench.add_argument('--bps', type=float, help='外部传入每股净资产')
    parser_workbench.add_argument('--pe', type=float, help='外部传入当前PE')
    parser_workbench.add_argument('--pb', type=float, help='外部传入当前PB')
    parser_workbench.add_argument('--free-cash-flow', type=float, help='外部传入自由现金流')
    parser_workbench.add_argument('--shares-outstanding', type=float, help='外部传入总股本')
    parser_workbench.add_argument('--total-debt', type=float, help='外部传入有息负债')
    parser_workbench.add_argument('--cash', type=float, help='外部传入现金及等价物')
    parser_workbench.add_argument('--sector', help='外部传入板块')
    parser_workbench.add_argument('--industry', help='外部传入行业')
    parser_workbench.set_defaults(func=cmd_workbench)

    # doctor 命令
    parser_doctor = subparsers.add_parser('doctor', help='检查本地数据源状态')
    parser_doctor.add_argument('--live', action='store_true', help='尝试请求真实数据接口，可能受网络、代理或限流影响')
    parser_doctor.add_argument('--sample-symbol', default='002050', help='实时接口探测使用的样本股票代码')
    parser_doctor.set_defaults(func=cmd_doctor)

    # discover 命令
    parser_discover = subparsers.add_parser('discover', help='从真实候选池生成机会短名单')
    parser_discover.add_argument('--candidate-csv', required=True, help='候选股CSV，支持代码/名称/行业/价格/估值/财务/技术字段')
    parser_discover.add_argument('--top', type=int, default=10, help='进入短名单的数量')
    parser_discover.add_argument('--output-dir', help='HTML 输出目录')
    parser_discover.add_argument('--generate-reports', action='store_true', help='为短名单前N只股票继续生成完整Kami投研报告')
    parser_discover.add_argument('--report-count', type=int, default=3, help='批量生成完整报告的股票数量')
    parser_discover.add_argument('--price-dir', help='按股票代码匹配真实K线CSV的目录，例如 002050.csv 或 002050_prices_sample.csv')
    parser_discover.set_defaults(func=cmd_discover)

    # monitor 命令
    parser_monitor = subparsers.add_parser('monitor', help='生成自选股监控面板')
    parser_monitor.add_argument('--watchlist-csv', required=True, help='自选股CSV，支持价格/估值/支撑压力/财务/技术触发字段')
    parser_monitor.add_argument('--top', type=int, default=20, help='CLI展示的股票数量')
    parser_monitor.add_argument('--output-dir', help='HTML 输出目录')
    parser_monitor.add_argument('--generate-review-reports', action='store_true', help='为触发高/中级监控条件的股票生成复核版Kami投研报告')
    parser_monitor.add_argument('--report-count', type=int, default=3, help='批量生成复核报告的股票数量')
    parser_monitor.add_argument('--price-dir', help='按股票代码匹配真实K线CSV的目录，例如 002050.csv 或 002050_prices_sample.csv')
    parser_monitor.add_argument('--generate-plan', action='store_true', help='根据监控结果生成投资跟踪计划HTML和CSV')
    parser_monitor.set_defaults(func=cmd_monitor)

    # report 命令
    parser_report = subparsers.add_parser('report', help='生成完整 HTML 研究报告')
    parser_report.add_argument('symbol', help='股票代码')
    parser_report.add_argument('--style', default='kami', choices=['kami', 'apple'], help='报告视觉风格')
    parser_report.add_argument('--output-dir', help='HTML 输出目录')
    parser_report.add_argument('--timeframe', default='日线', help='技术面时间级别')
    parser_report.add_argument('--trend', help='技术面趋势描述')
    parser_report.add_argument('--price-csv', help='真实K线CSV路径，支持日期/开盘/最高/最低/收盘/成交量或date/open/high/low/close/volume')
    parser_report.add_argument('--offline-input-only', action='store_true', help='只使用外部传入字段和本地K线CSV生成报告，不请求行情、财报和风险接口')
    parser_report.add_argument('--live-data-check', action='store_true', help='生成前探测实时数据接口，结果只用于命令行诊断，不写入投资者报告正文')
    parser_report.add_argument('--require-technical-data', action='store_true', help='没有可验证K线数据时不生成报告，避免输出缺少技术面的报告')
    parser_report.add_argument('--strict-data', action='store_true', help='正式报告模式：公司名称、价格、K线、财务和估值核心数据不足时不生成HTML')
    parser_report.add_argument('--enforce-freshness', action='store_true', help='正式报告模式：检查K线截止日期，过期则不生成HTML')
    parser_report.add_argument('--max-price-age-days', type=int, default=10, help='允许K线截止日期距离检查日的最大天数')
    parser_report.add_argument('--business-summary', help='外部传入公司业务摘要')
    parser_report.add_argument('--moat', help='外部传入竞争优势或护城河说明')
    parser_report.add_argument('--methods', default='all', choices=['all', 'dcf', 'relative', 'ddm'], help='估值方法')
    parser_report.add_argument('--discount-rate', type=float, help='折现率/WACC，例如 0.10')
    parser_report.add_argument('--terminal-growth', type=float, help='永续增长率，例如 0.025')
    parser_report.add_argument('--fcf-growth', type=float, help='自由现金流增长率，例如 0.04')
    parser_report.add_argument('--peer-pe', type=float, help='可比公司市盈率中位数')
    parser_report.add_argument('--peer-pb', type=float, help='可比公司市净率中位数')
    parser_report.add_argument('--margin-of-safety', type=float, help='安全边际，例如 0.30')
    parser_report.add_argument('--current-price', type=float, help='外部传入当前价格')
    parser_report.add_argument('--eps', type=float, help='外部传入每股收益')
    parser_report.add_argument('--bps', type=float, help='外部传入每股净资产')
    parser_report.add_argument('--pe', type=float, help='外部传入当前市盈率')
    parser_report.add_argument('--pb', type=float, help='外部传入当前市净率')
    parser_report.add_argument('--free-cash-flow', type=float, help='外部传入自由现金流')
    parser_report.add_argument('--shares-outstanding', type=float, help='外部传入总股本')
    parser_report.add_argument('--total-debt', type=float, help='外部传入有息负债')
    parser_report.add_argument('--cash', type=float, help='外部传入现金及等价物')
    parser_report.add_argument('--sector', help='外部传入板块')
    parser_report.add_argument('--industry', help='外部传入行业')
    parser_report.add_argument('--gross-margin', type=float, help='外部传入毛利率(%)')
    parser_report.add_argument('--net-margin', type=float, help='外部传入净利率(%)')
    parser_report.add_argument('--roe', type=float, help='外部传入ROE(%)')
    parser_report.add_argument('--debt-ratio', type=float, help='外部传入资产负债率(%)')
    parser_report.add_argument('--revenue-growth', type=float, help='外部传入收入增速(%)')
    parser_report.add_argument('--profit-growth', type=float, help='外部传入利润增速(%)')
    parser_report.add_argument('--receivable-growth', type=float, help='外部传入应收账款增速(%)')
    parser_report.add_argument('--inventory-growth', type=float, help='外部传入存货增速(%)')
    parser_report.add_argument('--operating-cash-flow', type=float, help='外部传入经营现金流')
    parser_report.add_argument('--net-income', type=float, help='外部传入净利润')
    parser_report.set_defaults(func=cmd_report)
    
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
    
    # board 命令 (打板筛选)
    parser_board = subparsers.add_parser('board', help='打板筛选 (短线)')
    parser_board.add_argument('--type', 
        choices=['limit-up', 'strong', 'continuous', 'market', 'opportunities'],
        default='market',
        help='筛选类型: limit-up(涨停板), strong(强势股), continuous(连板), market(市场情绪), opportunities(打板机会)')
    parser_board.set_defaults(func=cmd_board)
    
    # earnings 命令 (完整财报分析)
    parser_earnings = subparsers.add_parser('earnings', help='完整财报分析 (预测+回顾)')
    parser_earnings.add_argument('symbol', help='股票代码')
    parser_earnings.add_argument('--periods', type=int, default=4, help='预测季度数 (默认4)')
    parser_earnings.set_defaults(func=cmd_earnings)
    
    # preview 命令 (财报预测)
    parser_preview = subparsers.add_parser('preview', help='财报预测 (预测未来季度业绩)')
    parser_preview.add_argument('symbol', help='股票代码')
    parser_preview.add_argument('--periods', type=int, default=4, help='预测季度数 (默认4)')
    parser_preview.set_defaults(func=cmd_preview)
    
    # recap 命令 (财报回顾)
    parser_recap = subparsers.add_parser('recap', help='财报回顾 (分析历史业绩)')
    parser_recap.add_argument('symbol', help='股票代码')
    parser_recap.set_defaults(func=cmd_recap)
    
    # compare 命令 (业绩比较)
    parser_compare = subparsers.add_parser('compare', help='多股票业绩比较')
    parser_compare.add_argument('symbols', nargs='+', help='股票代码列表 (至少2个)')
    parser_compare.set_defaults(func=cmd_compare)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main()
