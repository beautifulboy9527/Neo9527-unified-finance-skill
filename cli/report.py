#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: report"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    # ── P1: Enhancement data collection ──
    enhanced_technical = {}
    evidence_ledger = {}
    entry_signals_data = {}
    risk_management_data = {}

    try:
        ti_module = load_module("technical_indicators", os.path.join("skills", "shared", "technical_indicators.py"))
        hist = technical.get("candles") or collected_data.get("market_data", {})
        if hist is not None:
            try:
                vwap = ti_module.calculate_vwap(hist) if hasattr(ti_module, 'calculate_vwap') else None
                fib = ti_module.calculate_fibonacci_retracements(hist) if hasattr(ti_module, 'calculate_fibonacci_retracements') else None
                sr = ti_module.calculate_confluence_support_resistance(hist) if hasattr(ti_module, 'calculate_confluence_support_resistance') else None
                enhanced_technical = {
                    "vwap": vwap,
                    "fibonacci": fib,
                    "support_resistance": sr,
                    "patterns": technical.get("patterns", []),
                }
            except Exception as e:
                print(f"  增强技术指标部分失败: {e}")
    except Exception as e:
        print(f"  技术指标模块加载失败: {e}")

    try:
        ev_module = load_module("evidence", os.path.join("skills", "shared", "evidence.py"))
        ledger = ev_module.EvidenceLedger()
        for src in data_sources.get("collection", {}).get("sources", []):
            ledger.add(source=src, field="行情数据", grade="B", note="外部数据源")
        if collected_data.get("success"):
            ledger.add(source="实时接口", field="行情采集", grade="A", note="采集成功")
        evidence_ledger = {"items": ledger.to_list()}
    except Exception as e:
        print(f"  数据溯源模块失败: {e}")

    try:
        es_module = load_module("entry_signals", os.path.join("skills", "stock-skill", "entry_signals.py"))
        signals = es_module.analyze_entry_signals(args.symbol)
        entry_signals_data = signals or {}
    except Exception as e:
        print(f"  入场信号模块失败: {e}")

    try:
        rm_module = load_module("risk_management_pro", os.path.join("skills", "stock-skill", "risk_management_pro.py"))
        rm = rm_module.RiskManagerPro()
        hist_data = technical.get("candles")
        if hist_data is not None:
            import pandas as pd
            if not isinstance(hist_data, pd.DataFrame):
                hist_data = None
            rm_result = {
                "var": {"var_95": None, "cvar": None, "max_drawdown": None},
                "stop_loss": {},
                "position_sizing": {},
            }
            try:
                if hist_data is not None and hasattr(hist_data, 'close'):
                    returns = hist_data['close'].pct_change().dropna()
                    if len(returns) > 20:
                        var_95 = rm.var_parametric(returns, confidence=0.95)
                        cvar = rm.cvar(returns, confidence=0.95)
                        rm_result["var"] = {"var_95": f"{var_95*100:.2f}", "cvar": f"{cvar*100:.2f}", "max_drawdown": None}
            except Exception:
                pass
            risk_management_data = rm_result
    except Exception as e:
        print(f"  风控模块失败: {e}")

    html_text = ReportClass().generate(
        args.symbol,
        display_name=stock_display_name(args.symbol, collected_data.get("profile", {})),
        financial_health=financial_health,
        valuation_workbench=valuation_workbench,
        risk_alerts=risk_alerts,
        technical_analysis=technical,
        fundamental_analysis=fundamental,
        data_sources=data_sources,
        enhanced_technical=enhanced_technical,
        evidence_ledger=evidence_ledger,
        entry_signals=entry_signals_data,
        risk_management=risk_management_data,
    )

    output_dir = Path(args.output_dir or os.path.join(SKILLS_DIR, "outputs", "html_reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"STOCK_{args.symbol}_{suffix}_{timestamp}.html"
    output_path.write_text(html_text, encoding="utf-8")

    print(f"报告已生成：{output_path}")
    print(f"数据源状态：{data_sources['status']}｜{data_sources['summary']}")
    print("提示：若正式使用，请补充真实数据源或外部可验证字段，并复核资料截止日期。")


