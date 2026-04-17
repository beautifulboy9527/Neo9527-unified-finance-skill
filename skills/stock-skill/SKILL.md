---
name: stock-analysis-skill
description: |
  股票多维度分析 - 技术指标、基本面、估值、资金流向。
  支持A股/港股/美股市场，输出标准JSON格式，可被Agent直接调用。
metadata:
  openclaw:
    emoji: "📈"
    triggers:
      - "股票分析"
      - "A股"
      - "美股"
      - "港股"
      - "技术指标"
      - "基本面"
      - "估值"
      - "资金流"
    inputs:
      symbol:
        type: string
        description: 股票代码 (如 002050, AAPL, 00700.HK)
        required: true
      market:
        type: string
        description: 市场类型
        default: stock
        enum: [stock]
    outputs:
      score:
        type: number
        description: 综合评分 (0-100)
      signals:
        type: array
        description: 信号列表
      valuation:
        type: object
        description: 估值数据
---

# Stock Analysis Skill

股票多维度分析 Skill，符合 OpenClaw Skills 规范。

## 快速开始

### Agent 调用

```python
from skills.base_skill import SkillInput, SkillRegistry

output = SkillRegistry.execute(
    'StockAnalysisSkill',
    SkillInput(symbol='002050', market='stock')
)

print(f"Score: {output.score}/100")
print(f"PE: {output.data['valuation']['pe']}")
```

### CLI 调用

```bash
neo-finance analyze-stock 002050
neo-finance analyze-stock AAPL
```

## 功能

| 功能 | A股 | 美股 | 港股 |
|------|-----|------|------|
| 行情数据 | ✅ agent-stock | ✅ yfinance | ✅ yfinance |
| 技术指标 | ✅ | ✅ | ✅ |
| 基本面 | ✅ akshare | ✅ yfinance | ✅ yfinance |
| 资金流向 | ✅ akshare | ❌ | ❌ |
| 估值分析 | ✅ | ✅ | ✅ |

## 市场检测

自动识别市场类型：
- 6位数字 → A股 (002050)
- 纯字母 → 美股 (AAPL)
- 数字.HK → 港股 (00700.HK)

## 输出示例

```json
{
  "skill_name": "StockAnalysisSkill",
  "success": true,
  "score": 72,
  "data": {
    "market": "cn",
    "name": "三花智控",
    "price": 45.11,
    "valuation": {
      "pe": 46.72,
      "pb": 5.98,
      "market_cap": 1898.24
    },
    "technical": {
      "ma5": 44.16,
      "ma10": 43.28,
      "rsi": 62.68,
      "trend": "uptrend"
    },
    "fundflow": {
      "main_inflow": 1234.56,
      "retail_inflow": -567.89
    }
  }
}
```

## 数据来源

- **A股**: agent-stock + akshare
- **美股/港股**: yfinance

## 依赖

```bash
pip install yfinance akshare pandas
```
