#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整分析报告生成器
结合插件系统 + 投资框架 + FinanceToolkit
"""

import sys
import os
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def generate_complete_report(symbol: str, period: str = 'medium') -> str:
    """
    生成完整分析报告
    
    Args:
        symbol: 股票代码
        period: 投资周期 (long/medium/short)
        
    Returns:
        Markdown 格式的完整报告
    """
    
    # 导入模块
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from features.plugin_system import analyze_with_plugins
    from features.investment_framework import analyze_investment
    
    # 运行分析
    plugin_result = analyze_with_plugins(symbol, period)
    investment_result = analyze_investment(symbol, period)
    
    # 生成报告
    period_names = {
        'long': '长线投资 (1-3年+)',
        'medium': '中线投资 (1-6个月)',
        'short': '短线交易 (数天-数周)'
    }
    
    report = f"""# {symbol} 完整分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**投资周期**: {period_names.get(period, period)}  
**分析框架**: 插件系统 + 投资框架

---

## 📊 一、投资框架分析

"""
    
    # 投资框架结果
    decision = investment_result.get('decision', {})
    analysis = investment_result.get('analysis', {})
    
    action_emoji = {
        'buy': '✅ 买入',
        'hold': '🟡 观望',
        'avoid': '❌ 回避',
        'wait': '⏳ 等待',
        'reduce': '📉 减仓'
    }
    
    report += f"""### 最终决策

| 项目 | 结果 |
|------|------|
| **建议操作** | {action_emoji.get(decision.get('action'), decision.get('action', '未知'))} |
| **置信度** | {decision.get('confidence', 0)}/100 |

"""
    
    if decision.get('reasons'):
        report += "### 决策依据:\n\n"
        for reason in decision['reasons']:
            report += f"- ✅ {reason}\n"
        report += "\n"
    
    if decision.get('risks'):
        report += "### 风险提示:\n\n"
        for risk in decision['risks']:
            report += f"- ⚠️ {risk}\n"
        report += "\n"
    
    # 插件分析结果
    report += """---

## 🔌 二、插件系统分析

### 已执行插件:

"""
    
    plugin_results = plugin_result.get('results', {})
    
    for plugin_name, result in plugin_results.items():
        if 'error' in result:
            report += f"**{plugin_name}**: ❌ {result['error']}\n\n"
        else:
            # 根据插件类型显示不同内容
            if plugin_name == 'macro':
                report += f"**{plugin_name}**: 评分 {result.get('score', 0)}/20\n\n"
            elif plugin_name == 'sector':
                report += f"**{plugin_name}**: 评分 {result.get('score', 0)}/20, 强度 {result.get('strength', '未知')}\n\n"
            elif plugin_name == 'technical':
                report += f"**{plugin_name}**: 趋势 {result.get('trend', '未知')}, RSI {result.get('rsi', 0):.1f}, 建议 {result.get('recommendation', 'hold')}\n\n"
            elif plugin_name == 'signals':
                report += f"**{plugin_name}**: 评分 {result.get('score', 0)}/100, 信号 {result.get('signals', [])}\n\n"
            elif plugin_name == 'risk':
                report += f"**{plugin_name}**: 入场价 {result.get('entry_price')}, 止损 {result.get('stop_loss')}, 目标 {result.get('target_price')}\n\n"
            elif plugin_name == 'fundamental':
                report += f"**{plugin_name}**: 评分 {result.get('score', 0)}/100\n\n"
            else:
                report += f"**{plugin_name}**: ✅ 完成\n\n"
    
    # 分析维度
    dimensions = analysis.get('dimensions', {})
    
    if dimensions:
        report += """---

## 📈 三、分析维度详解

"""
        
        for dim_name, dim_data in dimensions.items():
            report += f"### {dim_name}\n\n"
            report += f"**权重**: {dim_data.get('weight', 0)*100:.0f}%\n\n"
            
            questions = dim_data.get('questions', [])
            if questions:
                report += "**核心问题**:\n\n"
                for q in questions:
                    report += f"- {q}\n"
                report += "\n"
    
    # 操作指南
    report += f"""---

## 💡 四、操作建议

"""
    
    action = decision.get('action', 'hold')
    
    if action == 'buy':
        report += """### 操作流程:

1. ✅ 确认信号已触发
2. 📌 设置止损价 (重要!)
3. 📌 控制仓位 (建议不超过总资金 10-20%)
4. 📌 设定目标价
5. ⚠️ 严格执行止损纪律

"""
    elif action == 'hold':
        report += """### 观望建议:

1. 📌 继续观察，等待更明确信号
2. 📌 可小仓位试探
3. ⚠️ 必须设置止损保护

"""
    elif action == 'avoid':
        report += """### 回避建议:

1. ❌ 不建议入场
2. 📌 如有持仓考虑减仓
3. ⚠️ 等待基本面改善

"""
    else:
        report += """### 建议:

1. 📌 保持谨慎
2. ⚠️ 严格控制风险

"""
    
    # 风险提示
    report += """---

## ⚠️ 重要声明

1. **本报告仅供参考**，不构成投资建议
2. **股市有风险**，投资需谨慎
3. **历史表现不代表未来**，信号仅供参考
4. **严格执行止损**是风险控制的关键
5. **建议结合其他数据源**验证分析结果

---

## 📋 系统信息

| 项目 | 信息 |
|------|------|
| 分析框架 | 插件系统 v1.0 + 投资框架 v1.0 |
| 数据源 | yfinance, akshare |
| 插件数量 | {len(plugin_results)} 个 |
| 分析耗时 | 实时 |

---

*报告生成: 小灰灰 🐕*  
*更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report


if __name__ == '__main__':
    import json
    
    symbol = '002241'
    
    print("=" * 60)
    print(f"完整分析报告: {symbol}")
    print("=" * 60)
    
    for period in ['long', 'medium', 'short']:
        print(f"\n投资周期: {period}")
        print("-" * 60)
        
        report = generate_complete_report(symbol, period)
        print(report[:500])  # 只显示前500字符
        print("...")
