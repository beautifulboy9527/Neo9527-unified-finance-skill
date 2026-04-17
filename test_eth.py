#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETH快速分析测试
"""

import sys
import os

# 添加路径
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\scripts')

from features.complete_crypto_analyzer import analyze_complete

print("=" * 60)
print("ETH-USD 完整分析")
print("=" * 60)

# 执行分析
result = analyze_complete('ETH-USD')

# 显示结果
print(f"\n📊 市场数据:")
market = result.get('market', {})
print(f"  价格: ${market.get('price', 0):,.2f}")
print(f"  24h涨跌: {market.get('change_24h', 0):+.2f}%")
print(f"  成交量: ${market.get('volume_24h', 0)/1e9:.2f}B")
print(f"  市值: ${market.get('market_cap', 0)/1e9:.2f}B")

# 技术分析
tech = result.get('technical', {})
patterns = tech.get('patterns', {})
indicators = tech.get('indicators', {})

print(f"\n📈 技术分析:")
print(f"  趋势: {patterns.get('trend_desc', 'unknown')}")
print(f"  RSI: {indicators.get('rsi', 0):.1f}")
print(f"  MACD: {patterns.get('macd_signal', 'unknown')}")

# 信号
signals = result.get('signals', [])
bullish = [s for s in signals if s['strength'] > 0]
bearish = [s for s in signals if s['strength'] < 0]

print(f"\n🎯 信号汇总:")
print(f"  看涨: {len(bullish)} 项")
for s in bullish:
    print(f"    [{s['category']}] {s['name']}: {s['signal']} ({s['strength']:+d})")

print(f"  看跌: {len(bearish)} 项")
for s in bearish:
    print(f"    [{s['category']}] {s['name']}: {s['signal']} ({s['strength']:+d})")

# 结论
conclusion = result.get('conclusion', {})
print(f"\n💡 综合结论:")
print(f"  评分: {conclusion.get('score', 0)}/100")
print(f"  决策: {conclusion.get('decision', 'HOLD')}")
print(f"  置信度: {conclusion.get('confidence', 0)}%")
print(f"  解读: {conclusion.get('narrative', '')}")

print("\n" + "=" * 60)
