#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报分析 CLI - Earnings CLI
集成财报预测、财报回顾、业绩比较三大功能
"""

import sys
import os

# 添加skills路径
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

try:
    from skills.stock_skill.earnings_preview import earnings_preview, format_preview_output
    from skills.stock_skill.earnings_recap import earnings_recap, format_recap_output
    from skills.stock_skill.performance_comparison import compare_performance, format_comparison_output
except ImportError:
    # 兼容本地导入
    from earnings_preview import earnings_preview, format_preview_output
    from earnings_recap import earnings_recap, format_recap_output
    from performance_comparison import compare_performance, format_comparison_output


def print_help():
    """打印帮助信息"""
    help_text = """
📊 财报分析 CLI
==============

用法:
    python earnings_cli.py <command> [args]

命令:
    preview <symbol> [periods]   - 财报预测 (预测未来季度业绩)
                                   例: python earnings_cli.py preview AAPL 4
    
    recap <symbol>               - 财报回顾 (分析历史业绩 vs 预期)
                                   例: python earnings_cli.py recap AAPL
    
    compare <symbol1> [symbol2] [symbol3] ...
                                   - 多股票业绩比较
                                   例: python earnings_cli.py compare AAPL MSFT GOOGL
    
    all <symbol>                 - 完整财报分析 (预测 + 回顾 + 比较)
                                   例: python earnings_cli.py all AAPL

示例:
    # 预测苹果未来4个季度的收入和EPS
    python earnings_cli.py preview AAPL 4
    
    # 分析苹果最新财报表现
    python earnings_cli.py recap AAPL
    
    # 对比苹果、微软、谷歌三家的财务表现
    python earnings_cli.py compare AAPL MSFT GOOGL
    
    # 对某只股票进行完整的财报分析
    python earnings_cli.py all AAPL

说明:
    - preview: 基于历史财报数据，使用线性回归和增长率模型预测未来业绩
    - recap: 分析最新财报与历史/预期的差异，评估业绩是否达标
    - compare: 支持同环比分析、行业内对比、多股票横向比较

依赖:
    - yfinance (美股数据)
    - AkShare (A股数据，未安装时显示警告)
"""
    print(help_text)


def cmd_preview(args):
    """财报预测命令"""
    if not args:
        print("❌ 请提供股票代码")
        print("   例: python earnings_cli.py preview AAPL 4")
        return
    
    symbol = args[0].upper()
    periods = int(args[1]) if len(args) > 1 else 4
    
    print(f"\n{'='*60}")
    print(f"📈 财报预测 - {symbol}")
    print(f"{'='*60}\n")
    
    result = earnings_preview(symbol, periods)
    print(format_preview_output(result))


def cmd_recap(args):
    """财报回顾命令"""
    if not args:
        print("❌ 请提供股票代码")
        print("   例: python earnings_cli.py recap AAPL")
        return
    
    symbol = args[0].upper()
    
    print(f"\n{'='*60}")
    print(f"📊 财报回顾 - {symbol}")
    print(f"{'='*60}\n")
    
    result = earnings_recap(symbol)
    print(format_recap_output(result))


def cmd_compare(args):
    """业绩比较命令"""
    if not args:
        print("❌ 请提供至少一个股票代码")
        print("   例: python earnings_cli.py compare AAPL MSFT")
        return
    
    symbols = [s.upper() for s in args]
    
    print(f"\n{'='*60}")
    print(f"📈 业绩比较 - {', '.join(symbols)}")
    print(f"{'='*60}\n")
    
    result = compare_performance(symbols)
    print(format_comparison_output(result))


def cmd_all(args):
    """完整财报分析命令"""
    if not args:
        print("❌ 请提供股票代码")
        print("   例: python earnings_cli.py all AAPL")
        return
    
    symbol = args[0].upper()
    
    print(f"\n{'='*60}")
    print(f"📊 完整财报分析 - {symbol}")
    print(f"{'='*60}\n")
    
    # 财报预测
    print("\n" + "─"*60)
    print("📈 财报预测")
    print("─"*60)
    preview_result = earnings_preview(symbol, 4)
    print(format_preview_output(preview_result))
    
    # 财报回顾
    print("\n" + "─"*60)
    print("📊 财报回顾")
    print("─"*60)
    recap_result = earnings_recap(symbol)
    print(format_recap_output(recap_result))
    
    # 完整输出
    print("\n" + "="*60)
    print("✅ 完整财报分析完成")
    print("="*60)


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # 命令路由
    commands = {
        "preview": cmd_preview,
        "recap": cmd_recap,
        "compare": cmd_compare,
        "all": cmd_all,
        "help": lambda _: print_help(),
        "-h": lambda _: print_help(),
        "--help": lambda _: print_help(),
    }
    
    if command in commands:
        commands[command](args)
    else:
        print(f"❌ 未知命令: {command}")
        print_help()


if __name__ == "__main__":
    main()
