---
name: stock-analysis-skill
description: |
  股票多维度分析 - 技术指标、基本面、资金流向、异常检测。
  支持A股/港股/美股市场，包含快速分析、财报体检、风险预警、
  财务异常检测、估值分析和深度研报。
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

### 2. A股选股器 (screener.py)

多条件选股：
- 估值指标: PE/PB/PS
- 盈利指标: ROE/ROA/毛利率/净利率
- 成长指标: 营收增长率/净利润增长率
- 股息指标: 股息率
- 财务安全: 资产负债率/流动比率

```python
from skills.stock_skill.screener import screen_stocks

result = screen_stocks(
    scope='hs300',      # 沪深300
    pe_max=20,          # PE上限
    roe_min=15,         # ROE下限
    debt_ratio_max=50   # 负债率上限
)
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

### 6. 深度研报 (deep-research/)

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
├── screener.py           # A股选股器 (v1.0)
├── financial_check.py    # 财务异常检测 (v1.0)
├── financial_health.py   # 财报体检评分
├── risk_alerts.py        # 自选股风险预警
├── deep-research/        # 深度研报
│   ├── SKILL.md
│   ├── analyzer.py       # 8阶段分析
│   └── report_html.py    # HTML报告
└── __init__.py
```

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

---

*v2.2 - 恢复完整架构，支持快速分析 + 深度研报*
