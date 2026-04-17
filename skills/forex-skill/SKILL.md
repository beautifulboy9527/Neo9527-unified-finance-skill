---
name: forex-analysis-skill
description: |
  外汇多维度分析 - 汇率、技术指标、趋势分析。
  支持主要货币对，输出标准JSON格式，可被Agent直接调用。
metadata:
  openclaw:
    emoji: "💱"
    triggers:
      - "外汇"
      - "汇率"
      - "货币对"
      - "EUR/USD"
      - "GBP/USD"
      - "USD/JPY"
    inputs:
      symbol:
        type: string
        description: 货币对 (如 EURUSD=X, GBPUSD=X)
        required: true
      market:
        type: string
        description: 市场类型
        default: forex
        enum: [forex]
    outputs:
      score:
        type: number
        description: 综合评分 (0-100)
      signals:
        type: array
        description: 信号列表
---

# Forex Analysis Skill

外汇多维度分析 Skill，符合 OpenClaw Skills 规范。

## 快速开始

### Agent 调用

```python
from skills.base_skill import SkillInput, SkillRegistry

output = SkillRegistry.execute(
    'ForexAnalysisSkill',
    SkillInput(symbol='EURUSD=X', market='forex')
)

print(f"Rate: {output.data['rate']}")
print(f"Trend: {output.data['trend']}")
```

### CLI 调用

```bash
neo-finance analyze-forex EURUSD=X
```

## 支持货币对

| 货币对 | 说明 |
|--------|------|
| EURUSD=X | 欧元/美元 |
| GBPUSD=X | 英镑/美元 |
| USDJPY=X | 美元/日元 |
| AUDUSD=X | 澳元/美元 |
| USDCAD=X | 美元/加元 |

## 输出示例

```json
{
  "skill_name": "ForexAnalysisSkill",
  "success": true,
  "score": 65,
  "data": {
    "symbol": "EURUSD=X",
    "rate": 1.0856,
    "change_pct": 0.15,
    "technical": {
      "ma5": 1.0845,
      "ma20": 1.0820,
      "rsi": 58.3,
      "trend": "uptrend"
    }
  }
}
```

## 数据来源

- yfinance (免费)

## 依赖

```bash
pip install yfinance pandas
```
