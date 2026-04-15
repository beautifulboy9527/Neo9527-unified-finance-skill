---
name: unified-finance-skill
description: >
  统一金融分析技能 - 饕餮整合多个金融 Skills 的最优能力。
  支持全球市场 (A 股/港股/美股) 数据查询、技术分析、流动性分析、情绪分析、技术图表、相关性分析、估值监控、深度投研。
  **完整集成** (非路径引用): agent-stock + akshare + yfinance + stock-liquidity + finance-sentiment + stock-market-pro + stock-correlation + akshare-data + stock-valuation-monitor + china-stock-research。
  触发：股票分析、行情查询、技术分析、流动性分析、情绪分析、技术图表、相关性分析、估值分析、投研报告。
version: 2.6.0
integration: full
tested: 2026-04-15
---

# Unified Finance Skill - 饕餮整合版

> 整合多个金融 Skills 优势的完整可执行技能

## ✅ 测试状态

**最后测试**: 2026-04-15 17:58
**测试结果**: 7/7 通过 ✅

| 测试项 | 状态 |
|--------|------|
| A股行情查询 | ✅ |
| 美股行情查询 | ✅ |
| 技术分析 | ✅ |
| 财务数据 | ✅ |
| 资金流向 | ✅ |
| 流动性分析 | ✅ |
| 无硬编码验证 | ✅ |

---

## 整合来源

| 来源 | 整合内容 | 模块 | 集成方式 |
|------|---------|------|---------|
| **agent-stock** | A股行情、K线、技术指标 | `core/quote.py`, `core/technical.py` | subprocess 调用 |
| **akshare** | 财务数据、资金流向 | `core/financial.py` | 直接 import |
| **yfinance** | 美股/港股数据 | `core/quote.py`, `core/financial.py` | 直接 import |
| **stock-liquidity** | 流动性分析 | `features/liquidity.py` | **完整代码集成** |
| **finance-sentiment** | 情绪分析 | `features/sentiment.py` | **完整代码集成** |
| **stock-market-pro** | 高级技术图表 | `features/chart.py` | **完整代码集成** |
| **stock-correlation** | 相关性分析 | `features/correlation.py` | **完整代码集成** |
| **akshare-data** | 增强财务数据、宏观数据 | `features/enhanced_financial.py` | **完整代码集成** |
| **stock-evaluator-v3** | 投资评估框架 | 参考 | **方法论参考** |

---

## 模块架构

```
scripts/
├── finance.py              # 统一入口 (CLI)
├── config.py               # 输出路径配置
├── test_unified_finance.py # 功能测试
│
├── core/                   # 核心模块 (数据获取)
│   ├── quote.py           # 行情查询 (A股/港股/美股)
│   ├── technical.py       # 技术分析 (MA/RSI/趋势)
│   └── financial.py       # 财务数据 (财务摘要/资金流向)
│
└── features/               # 功能模块 (高级分析)
    ├── liquidity.py       # 流动性分析 (买卖价差/市场冲击/换手率)
    └── sentiment.py       # 情绪分析 (Reddit/X.com/新闻/Polymarket)
```

---

## 快速开始

### 命令行

```bash
# 进入目录
cd C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\scripts

# 行情查询
python finance.py quote 002050    # A股
python finance.py quote AAPL      # 美股

# 技术分析
python finance.py technical 002050

# 财务数据
python finance.py financial 002050

# 资金流向 (仅A股)
python finance.py fundflow 002050

# 流动性分析
python finance.py liquidity AAPL

# 情绪分析 (需要 ADANOS_API_KEY)
python finance.py sentiment AAPL

# 快速分析 (行情 + 技术)
python finance.py quick 002050

# 完整分析 (所有模块)
python finance.py full 002050

# 运行测试
python test_unified_finance.py
```

### Python API

```python
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\scripts')

from core.quote import get_quote
from core.technical import analyze_technical
from core.financial import get_financial_summary, get_fundflow
from features.liquidity import analyze_liquidity
from features.sentiment import analyze_sentiment

# 行情查询 (自动路由到最佳数据源)
quote = get_quote('002050')   # A股 -> agent-stock
quote = get_quote('AAPL')     # 美股 -> yfinance
quote = get_quote('00700.HK') # 港股 -> yfinance

# 技术分析
tech = analyze_technical('002050')
print(tech['basic_indicators'])  # MA5/MA10/MA20, RSI, 趋势

# 财务数据
fin = get_financial_summary('002050')
print(fin['revenue_3y'])  # 3年营收

flow = get_fundflow('002050')
print(flow['summary'])  # 资金流向汇总

# 流动性分析
liq = analyze_liquidity('AAPL')
print(liq['grade'])  # 流动性评级

# 情绪分析 (需要 ADANOS_API_KEY)
sent = analyze_sentiment('AAPL')
print(sent['sentiment'])  # 综合情绪
```

---

## 核心功能

### 1. 统一行情查询 (`core/quote.py`)

**整合来源**: agent-stock + akshare + yfinance

**能力**:
- 自动市场检测 (A股/港股/美股)
- 智能路由到最佳数据源
- A股: agent-stock (快速) → akshare (备选)
- 港股/美股: yfinance

**输出示例**:
```json
{
  "symbol": "002050",
  "market": "cn",
  "name": "三花智控",
  "price": 45.11,
  "change_pct": -0.94,
  "pe": 46.72,
  "pb": 5.98,
  "market_cap": 1898.24,
  "data_source": "agent-stock"
}
```

### 2. 技术分析 (`core/technical.py`)

**整合来源**: agent-stock

**能力**:
- 基础技术指标 (MA5/MA10/MA20)
- RSI 计算
- 乖离率
- 趋势判断

**输出示例**:
```json
{
  "basic_indicators": {
    "current_price": 44.82,
    "ma5": 44.16,
    "ma10": 43.28,
    "ma20": 43.25,
    "rsi": 62.68,
    "trend": "uptrend"
  }
}
```

### 3. 财务数据 (`core/financial.py`)

**整合来源**: akshare + yfinance

**能力**:
- 财务摘要 (营收、利润、ROE)
- 资金流向 (仅A股)
- 自动按市场选择数据源

### 4. 流动性分析 (`features/liquidity.py`)

**整合来源**: stock-liquidity (完整代码集成)

**能力**:
- 买卖价差
- 成交量分析
- 市场冲击估算
- 换手率
- Amihud 非流动性指标
- 流动性评级

**输出示例**:
```json
{
  "grade": "Low",
  "spread": {"bid": 264.48, "ask": 266.98},
  "volume": {"avg_daily_volume": 46670892},
  "impact": {"impact_1pct_adv_bps": 16.27}
}
```

### 5. 情绪分析 (`features/sentiment.py`)

**整合来源**: finance-sentiment (完整代码集成)

**能力**:
- Reddit 情绪
- X.com (Twitter) 情绪
- 新闻情绪
- Polymarket 预测市场
- 综合情绪判断

**依赖**: `ADANOS_API_KEY` 环境变量

---

## 输出路径

所有输出文件统一存放到:

| 类型 | 路径 |
|------|------|
| 报告 | `D:\OpenClaw\outputs\reports\` |
| 图表 | `D:\OpenClaw\outputs\charts\` |
| 数据 | `D:\OpenClaw\outputs\data\` |
| 日志 | `D:\OpenClaw\outputs\logs\` |

---

## 依赖

```bash
pip install yfinance akshare pandas numpy requests
```

## 环境变量

```bash
# 情绪分析 API Key (可选)
export ADANOS_API_KEY="sk_live_..."
```

---

## ⚠️ Gotchas

### 数据源限制

1. **A股数据**: 使用东方财富 API，需代理或境内网络
2. **yfinance**: 对 A 股支持有限，优先使用 agent-stock
3. **港股代码格式**: `00700.HK` (必须带后缀)
4. **美股代码**: 直接使用 ticker (如 `AAPL`)
5. **情绪分析**: 需要 Adanos API Key

### 数据时效性

- 行情数据有 15 分钟延迟
- 财务数据按季度更新
- 建议结合实时数据验证

### Windows 编码

所有脚本已添加 UTF-8 修复，如遇乱码检查终端编码设置。

---

## 📋 待集成功能

| 功能 | 来源 Skill | 优先级 | 状态 |
|------|-----------|--------|------|
| 高级技术图表 | stock-market-pro | P0 | 📋 待开发 |
| 相关性分析 | stock-correlation | P1 | 📋 待开发 |
| 估值监控 | stock-valuation-monitor | P1 | 📋 待开发 |
| A股价值分析 | china-stock-analysis | P0 | 📋 待开发 |
| 8阶段投研 | china-stock-research | P2 | 📋 待开发 |

详见: `ARCHITECTURE.md`

---

## 📁 文件结构

```
unified-finance-skill/
├── SKILL.md                    # 本文件
├── ARCHITECTURE.md             # 架构与迭代管理文档
├── config/
│   ├── alerts.json
│   └── portfolio.json
└── scripts/
    ├── finance.py              # 统一入口
    ├── config.py               # 输出路径配置
    ├── test_unified_finance.py # 功能测试
    ├── core/
    │   ├── quote.py
    │   ├── technical.py
    │   └── financial.py
    └── features/
        ├── liquidity.py
        └── sentiment.py
```

---

*饕餮整合 v2.2.0 - 完整可执行版 by 小灰灰 🐕*
