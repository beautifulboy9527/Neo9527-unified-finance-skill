---
name: signal-detection-skill
description: |
  多因子信号检测 - S/A/B/C 分级系统 + 时间维度分析。
  支持多因子信号叠加、信号分级、时间维度分析、倾向判断。
  输出标准 JSON 格式，可被 Agent 直接调用。
metadata:
  openclaw:
    emoji: "🎯"
    triggers:
      - "信号"
      - "检测"
      - "评级"
      - "S级"
      - "A级"
      - "看涨"
      - "看跌"
      - "倾向"
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
      grade:
        type: string
        description: 信号等级 (S/A/B/C)
        enum: [S, A, B, C]
      bias:
        type: string
        description: 信号倾向
        enum: [bullish, bearish, neutral]
      total_strength:
        type: number
        description: 总强度
---

# Signal Detection Skill

多因子信号检测 Skill，符合 OpenClaw Skills 规范。

## 快速开始

### Agent 调用

```python
from skills.base_skill import SkillInput, SkillRegistry

output = SkillRegistry.execute(
    'SignalDetectionSkill',
    SkillInput(symbol='BTC-USD', market='crypto')
)

print(f"Grade: {output.data['grade']}")
print(f"Bias: {output.data['bias']}")
```

### CLI 调用

```bash
neo-finance signals BTC-USD
```

## 信号分级系统

| 等级 | 条件 | 说明 |
|------|------|------|
| **S** | 强度≥10 + 置信度≥75% | 强买/强卖 |
| **A** | 强度≥5 + 置信度≥60% | 偏多/偏空 |
| **B** | 强度 -5~5 | 观望 |
| **C** | 强度≤-5 或 置信度<40% | 风险 |

## 时间维度

| 维度 | 周期 | 指标 |
|------|------|------|
| short | 1-7天 | RSI/超买超卖 |
| medium | 1-3月 | 趋势判断 |
| long | 3月+ | MA20位置 |

## 输出示例

```json
{
  "skill_name": "SignalDetectionSkill",
  "success": true,
  "data": {
    "grade": "A",
    "bias": "bullish",
    "total_strength": 8,
    "bullish_count": 3,
    "bearish_count": 1,
    "timeframe": {
      "short": {"trend": "neutral", "strength": 0},
      "medium": {"trend": "bullish", "strength": 2},
      "long": {"trend": "bullish", "strength": 3}
    }
  }
}
```

## 信号来源

- 技术形态
- 趋势指标
- 经典形态
- 动量指标
