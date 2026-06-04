#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: screening"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cmd_screen(args):
    """A股选股 (v3.0 增强版 - Phase 4)"""
    import importlib.util
    
    # 动态导入增强选股器
    spec = importlib.util.spec_from_file_location(
        "enhanced_screener",
        os.path.join(SKILLS_DIR, 'skills', 'stock-skill', 'enhanced_screener.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Phase 4: use_fallback 参数
    use_fallback = not args.no_fallback
    screener = module.EnhancedScreener(use_fallback=use_fallback)
    
    # 构建筛选参数
    criteria = {}
    if args.pe_max:
        criteria['pe_max'] = args.pe_max
    if args.pb_max:
        criteria['pb_max'] = args.pb_max
    if args.roe_min:
        criteria['roe_min'] = args.roe_min
    if args.debt_max:
        criteria['debt_ratio_max'] = args.debt_max
    if args.margin_min:
        criteria['net_margin_min'] = args.margin_min
    
    # 执行筛选
    result = screener.screen(
        scope=args.scope,
        strategy=args.strategy,
        criteria=criteria if criteria else None,
        technical_checks=args.technical if args.technical else None,
        use_scoring=args.scoring,
        industry=args.industry,
        top=args.top,
    )
    
    print(module.format_screening_output(result))



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


