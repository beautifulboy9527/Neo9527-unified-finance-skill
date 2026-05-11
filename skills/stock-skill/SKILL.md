---
name: stock-analysis-skill
description: |
  股票多维度分析 - 技术指标、基本面、资金流向、异常检测。
  支持A股/港股/美股市场，包含快速分析、财报体检、风险预警、
  估值工作台、外部数据覆盖、财务异常检测和深度研报。
---

# Stock Analysis Skill

股票多维度分析 Skill，支持快速分析和深度研报两种模式。

## 功能模块

### 1. 快速分析 (analyzer.py)

| 功能 | A股 | 美股 | 港股 |
|------|-----|------|------|
| 行情数据 | ✅ akshare | ✅ yfinance | ✅ yfinance |
| 技术指标 | ✅ MA/RSI/MACD | ✅ | ✅ |
| 基本面 | ✅ PE/PB/ROE | ✅ | ✅ |
| 资金流向 | ✅ 主力资金 | ❌ | ❌ |
| 信号生成 | ✅ 买入/卖出 | ✅ | ✅ |
| 综合评分 | ✅ 0-100分 | ✅ | ✅ |

### 2. A股选股器 v2.0 (enhanced_screener.py)

Phase 3 增强版，支持预设策略、技术面筛选、多因子评分：

#### 预设策略 (7种)
| 策略 | 说明 | 核心条件 |
|------|------|----------|
| value | 价值投资 | PE<20, PB<3, ROE>15% |
| growth | 成长股 | 收益增长>20%, PE<40 |
| dividend | 高股息 | 股息率>3%, 连续分红 |
| garp | GARP | PEG<1.5, ROE>12% |
| turnaround | 困境反转 | 季度利润环比改善 |
| defensive | 防御型 | Beta<0.8, 现金流稳定 |
| quality | 质量因子 | ROE>15%, 毛利率>30% |

#### 技术面筛选 (6种)
| 条件 | 说明 |
|------|------|
| golden-cross | MACD金叉 |
| ma-bullish | 均线多头排列 |
| volume-breakout | 放量突破 |
| rsi-oversold | RSI超卖反弹 |
| bollinger-squeeze | 布林带收口 |
| consolidation-breakout | 盘整突破 |

#### 多因子评分
- 估值因子 (25%): PE/PB/PS/PEG
- 盈利因子 (25%): ROE/ROA/毛利率/净利率
- 成长因子 (20%): 收益增长/利润增长
- 安全因子 (15%): 负债率/现金流
- 动量因子 (15%): 近期涨幅/相对强弱

```python
from skills.stock_skill.enhanced_screener import EnhancedScreener

screener = EnhancedScreener()
result = screener.screen(
    scope='hs300',
    strategy='value',           # 预设策略
    technical_checks=['golden-cross', 'ma-bullish'],  # 技术面
    use_scoring=True,           # 多因子评分
    industry='银行',            # 行业筛选
    top=20
)
```

#### CLI 命令
```bash
# 预设策略
python finance.py screen --strategy value
python finance.py screen --strategy growth

# 技术面筛选
python finance.py screen --technical golden-cross ma-bullish

# 多因子评分
python finance.py screen --scoring --top 20

# 组合条件
python finance.py screen --strategy value --technical golden-cross --scoring
```

### 3. 财务异常检测 (financial_check.py)

自动检测：
- 🟡 应收账款异常: 增速超过营收增速1.5倍
- 🟡 现金流背离: 净利润增长但现金流下降
- 🟡 存货异常: 增速超过营收增速2倍
- 🟡 毛利率异常: 波动过大
- 🟡 关联交易: 占比过高

```python
from skills.stock_skill.financial_check import check_financial_anomaly

result = check_financial_anomaly('600519')
# → 风险等级: low/medium/high
```

### 4. 财报体检 (financial_health.py)

输出商业化可用的财务健康分：
- 盈利能力
- 现金流质量
- 资产负债安全
- 营运资本质量
- 成长质量
- 数据完整度和证据摘要

```python
from skills.stock_skill.financial_health import analyze_financial_health

result = analyze_financial_health('AAPL')
# → health_score / health_grade / dimensions / risk_flags
```

### 5. 风险预警 (risk_alerts.py)

统一聚合财报体检、财务异常、估值、监管和技术形态风险：
- 严重度: 严重 / 高 / 中 / 低 / 提示
- 类别: 财务健康、财务异常、估值、监管、技术、数据质量
- 输出验证状态和后续验证动作

```python
from skills.stock_skill.risk_alerts import analyze_watchlist_alerts

result = analyze_watchlist_alerts(['AAPL', 'MSFT'])
```

### 6. 估值工作台 (valuation_workbench.py)

运行谨慎、基准、乐观三套估值情景：
- 输出估值区间和安全价
- 展示上行空间、方法、置信度和模型假设
- 缺少可验证估值数据时不生成伪区间

```python
from skills.stock_skill.valuation_workbench import analyze_valuation_workbench

result = analyze_valuation_workbench('AAPL', discount_rate=0.10, peer_pe=25)
```

### 7. 深度研报 (deep-research/)

8阶段投研框架：
- Phase 1: 公司事实底座
- Phase 2: 行业周期分析
- Phase 3: 业务拆解
- Phase 4: 财务质量分析
- Phase 5: 股权治理分析
- Phase 6: 市场分歧分析
- Phase 7: 估值与护城河
- Phase 8: 综合报告

```python
from skills.stock_skill.deep_research.analyzer import StockAnalyzer

analyzer = StockAnalyzer(style='value')
result = analyzer.analyze('AAPL')
```

## 使用方式

### 快速分析

```python
from skills.stock_skill.analyzer import analyze_stock

result = analyze_stock('AAPL')
print(f"评分: {result['score']}/100")
print(f"趋势: {result['data']['technical']['trend']}")
print(f"信号: {len(result['signals'])}个")
```

### A股选股

```python
from skills.stock_skill.screener import screen_stocks

result = screen_stocks(
    scope='hs300',
    pe_max=15,
    roe_min=15
)

for stock in result['stocks'][:10]:
    print(f"{stock['code']} - ROE: {stock['roe']:.1f}%")
```

### 财务异常检测

```python
from skills.stock_skill.financial_check import check_financial_anomaly

result = check_financial_anomaly('600519')
print(f"风险等级: {result['risk_level']}")
print(f"异常数量: {result['anomaly_count']}")
```

## 市场检测

自动识别市场类型：
- 6位数字 → A股 (002050, 600519)
- 纯字母 → 美股 (AAPL, MSFT)
- 数字.HK → 港股 (00700.HK)

## 输出示例

### 快速分析

```json
{
  "symbol": "AAPL",
  "market": "us",
  "score": 60,
  "signals": [
    {"type": "technical", "name": "趋势向上", "signal": "buy"},
    {"type": "technical", "name": "MACD金叉", "signal": "buy"}
  ],
  "data": {
    "technical": {
      "ma5": 268.5,
      "ma10": 265.2,
      "ma20": 260.1,
      "rsi": 62.5,
      "trend": "强势多头"
    },
    "fundamentals": {
      "pe": 28.5,
      "pb": 45.1,
      "roe": 152.0
    }
  }
}
```

## 文件结构

```
stock-skill/
├── SKILL.md              # 本文档
├── analyzer.py           # 快速分析 (v2.1)
├── screener.py           # A股选股器 (v1.0 基础版)
├── enhanced_screener.py  # 选股器 v2.0 (Phase 3 增强版) ✨
├── screening_strategies.py # 预设策略库 (7种策略) ✨
├── technical_screener.py # 技术面筛选 (6种条件) ✨
├── financial_check.py    # 财务异常检测 (v1.0)
├── financial_health.py   # 财报体检评分
├── risk_alerts.py        # 自选股风险预警
├── valuation_workbench.py # 情景估值工作台
├── earnings_preview.py   # 财报预测 (Phase 2) ✨
├── earnings_recap.py     # 财报回顾 (Phase 2) ✨
├── performance_comparison.py # 业绩比较 (Phase 2) ✨
├── deep-research/        # 深度研报
│   ├── SKILL.md
│   ├── analyzer.py       # 8阶段分析
│   └── report_html.py    # HTML报告
└── __init__.py
```

---

*v3.0 - Phase 3 选股器增强完成，支持预设策略、技术面筛选、多因子评分*

## 依赖

```bash
pip install yfinance akshare pandas numpy
```

## 参考资料

### 核心框架
- **FinanceToolkit** - 150+财务比率、DCF、VaR等
- **pandas-ta** - 130+技术指标
- **backtesting.py** - 轻量回测引擎

### 数据源
- **AkShare** - A股专用 (免费)
- **yfinance** - 美股/港股通用
- **CoinGecko** - 加密货币数据
- **DeFiLlama** - 链上数据

### Agent框架
- **Claude-Code-Stock-Deep-Research-Agent** - 8阶段投研框架

详细资料包见: `📊 金融Skills开发资料包.md`
