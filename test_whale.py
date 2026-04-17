#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OnchainWhaleSkill - ETH链上分析
"""

import sys
import os

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\skills\onchain-skill')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill')

from skills.base_skill import SkillInput
from whale import OnchainWhaleSkill

print("=" * 60)
print("🐋 ETH 链上鲸鱼分析")
print("=" * 60)

# 创建Skill
skill = OnchainWhaleSkill()

# 执行分析
result = skill.execute(SkillInput(symbol='ETH', market='crypto'))

print(f"\n✅ 分析成功: {result.success}")
print(f"📊 评分: {result.score}/100")
print(f"🎯 置信度: {result.confidence:.2%}")

# 鲸鱼摘要
whale = result.data.get('whale_summary', {})
print(f"\n🐋 鲸鱼动态:")
print(f"  偏向: {whale.get('whale_bias', 'unknown')}")
print(f"  匹配协议: {whale.get('matched_protocols', 0)} 个")
print(f"  生态TVL: ${whale.get('ecosystem_tvl', 0)/1e9:.2f}B")
print(f"  7日平均变化: {whale.get('avg_protocol_change_7d', 0):+.2f}%")

# 风险提示
risks = result.data.get('risk_flags', [])
if risks:
    print(f"\n⚠️  风险提示:")
    for risk in risks:
        print(f"  - {risk}")

# 专业解读
commentary = result.data.get('commentary', '')
if commentary:
    print(f"\n💡 专业解读:")
    print(f"  {commentary}")

# 信号
if result.signals:
    print(f"\n📈 信号:")
    for signal in result.signals:
        print(f"  [{signal['category']}] {signal['name']}: {signal['signal']} ({signal['strength']:+d})")

# 数据来源
print(f"\n📡 数据来源:")
for source in result.data_source:
    print(f"  - {source}")

print("\n" + "=" * 60)
