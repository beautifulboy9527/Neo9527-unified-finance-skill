#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: earnings"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


