---
name: crypto-analysis-skill
description: |
  加密货币多维度分析 - K线形态、技术指标、信号检测、综合评分。
  支持市场数据获取、技术分析、形态识别、信号生成。
  输出标准 JSON 格式，可被 Agent 直接调用。
metadata:
  openclaw:
    emoji: "📊"
    triggers:
      - "分析"
      - "加密货币"
      - "BTC"
      - "ETH"
      - "行情分析"
      - "技术分析"
      - "K线"
      - "信号"
    inputs:
      symbol:
        type: string
        description: 交易对符号 (如 BTC-USD, ETH-USD)
        required: true
      market:
        type: string
        description: 市场类型
        default: crypto
        enum: [crypto, stock, forex]
      timeframe:
        type: string
        description: 时间维度
        default: medium
        enum: [short, medium, long]
    outputs:
      score:
        type: number
        description: 综合评分 (0-100)
      signals:
        type: array
        description: 信号列表
      confidence:
        type: number
        description: 置信度 (0-1)
---

# Crypto Analysis Skill

加密货币多维度分析 Skill，符合 OpenClaw Skills 规范。

## 快速开始

### Agent 调用

```python
from skills.base_skill import SkillInput, SkillRegistry

output = SkillRegistry.execute(
    'CryptoAnalysisSkill',
    SkillInput(symbol='BTC-USD', market='crypto')
)

print(f"Score: {output.score}/100")
print(f"Confidence: {output.confidence:.2%}")
```

### CLI 调用

```bash
neo-finance analyze BTC-USD
```

### REST API

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"BTC-USD"}'
```

## 功能

| 功能 | 说明 |
|------|------|
| 市场数据 | CoinGecko 实时数据 |
| 技术分析 | MA/RSI/MACD/趋势 |
| 形态识别 | 双底/头肩/突破 |
| 信号生成 | 多因子叠 buff |

## 输出示例

```json
{
  "skill_name": "CryptoAnalysisSkill",
  "success": true,
  "score": 75,
  "confidence": 0.78,
  "signals": [
    {
      "category": "技术形态",
      "name": "趋势",
      "signal": "bullish",
      "strength": 5
    }
  ],
  "data": {
    "market": {
      "price": 75000,
      "change_24h": 2.5
    }
  }
}
```

## 数据来源

- CoinGecko (免费)
- yfinance (免费)

## 依赖

```bash
pip install yfinance pandas
```
