#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI commands: commentary (AI解读)"""

import os
import sys
import json
from typing import Dict, Optional

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cmd_commentary(args):
    """生成 AI 专业解读"""
    import importlib.util

    symbol = args.symbol
    market = getattr(args, 'market', 'stock')

    # 动态加载 commentary skill
    spec = importlib.util.spec_from_file_location(
        "commentary",
        os.path.join(SKILLS_DIR, "skills", "report-skill", "commentary.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 加载 base_skill 获取 SkillInput
    spec_base = importlib.util.spec_from_file_location(
        "base_skill",
        os.path.join(SKILLS_DIR, "skills", "base_skill.py")
    )
    base_module = importlib.util.module_from_spec(spec_base)
    spec_base.loader.exec_module(base_module)

    # 创建 SkillInput
    input_data = base_module.SkillInput(
        symbol=symbol,
        market=market,
        timeframe='1d',
        params={}
    )

    # 创建 skill 实例并执行
    skill = module.AICommentarySkill()
    output = skill.execute(input_data)

    # 输出结果
    if output.success:
        print("\n" + "=" * 60)
        print(f"📊 {symbol} AI 专业解读")
        print("=" * 60)

        data = output.data
        if data.get('title'):
            print(f"\n{data['title']}")
        if data.get('one_sentence'):
            print(f"\n💡 一句话: {data['one_sentence']}")
        if data.get('technical_summary'):
            print(f"\n📈 技术面: {data['technical_summary']}")
        if data.get('risk_warning'):
            print(f"\n⚠️ 风险提示: {data['risk_warning']}")
        if data.get('action_advice'):
            print(f"\n🎯 操作建议: {data['action_advice']}")

        print(f"\n评分: {output.score}/100 | 置信度: {output.confidence:.0%}")
        if output.data_source:
            print(f"数据源: {', '.join(output.data_source)}")
        print("=" * 60)
    else:
        print(f"❌ 解读失败: {output.error}")
        return 1

    return 0
