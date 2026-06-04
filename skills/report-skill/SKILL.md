---
name: ai-commentary-skill
description: |
  AI专业解读 - 分析师语言生成、技术面总结、风险提示、操作建议。
  让报告"活起来"，像人写的而不是程序拼的。
  输出标准 JSON 格式，可被 Agent 直接调用。
metadata:
  openclaw:
    emoji: "🤖"
    triggers:
      - "解读"
      - "评论"
      - "分析"
      - "分析师"
      - "专业"
      - "风险提示"
      - "操作建议"
    inputs:
      symbol:
        type: string
        description: 交易对符号
        required: true
      market:
        type: string
        description: 市场类型
        default: crypto
    outputs:
      title:
        type: string
        description: 标题
      technical_summary:
        type: string
        description: 技术面总结
      risk_warning:
        type: string
        description: 风险提示
      action_advice:
        type: string
        description: 操作建议
      one_sentence:
        type: string
        description: 一句话总结
---

# AI Commentary Skill

AI专业解读 Skill，符合 OpenClaw Skills 规范。

## 快速开始

### Agent 调用

```python
from skills.base_skill import SkillInput, SkillRegistry

output = SkillRegistry.execute(
    'AICommentarySkill',
    SkillInput(symbol='BTC-USD', market='crypto')
)

print(output.data['title'])
print(output.data['one_sentence'])
```

### CLI 调用

```bash
neo-finance commentary BTC-USD
```

## 功能

| 功能 | 说明 |
|------|------|
| 标题生成 | 综合评分 + 决策 |
| 技术面总结 | 趋势 + RSI + MACD |
| 风险提示 | 超买/超卖/集中度 |
| 操作建议 | 仓位管理 + 止损 |
| 一句话总结 | 多空对比 + 评分 |

## 输出示例

```json
{
  "skill_name": "AICommentarySkill",
  "success": true,
  "data": {
    "title": "BTC-USD 强势看多信号 - 综合评分 75/100",
    "technical_summary": "趋势向上，多头排列。RSI为76.5偏强。MACD金叉确认。",
    "risk_warning": "RSI超买风险，警惕高位回落。",
    "action_advice": "综合评分75/100，建议积极布局。分批建仓。",
    "one_sentence": "BTC-USD 当前呈现3项看多信号 vs 1项看空信号，建议买入。"
  }
}
```

## 语言风格

- ✅ 专业但不生硬
- ✅ 有观点有逻辑
- ✅ 风险提示明确
- ✅ 操作建议具体
- ❌ 避免 AI 味
- ❌ 避免废话套话
