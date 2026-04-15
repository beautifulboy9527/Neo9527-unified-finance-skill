---
name: unified-finance-skill
description: >
  统一金融分析技能 - 饕餮整合多个金融 Skills 的最优能力。
  支持全球市场 (A 股/港股/美股) 数据查询、技术分析、图表生成、智能警报、
  8阶段深度投研框架、选股器、财务异常检测、估值监控。
  触发：股票分析、行情查询、投研报告、技术指标、估值计算、选股。
version: 2.0.0
---

# Unified Finance Skill - 饕餮整合版 v2.0

> 整合多个金融 Skills 优势的超级技能

## 饕餮整合来源

| 能力来源 | 整合内容 |
|---------|---------|
| **unified-finance-skill** | 全球市场数据、技术图表、警报、投资组合 |
| **stock-research-executor** | 8阶段投研框架、多Agent并行、引用评级体系 |
| **china-stock-analysis** | A股选股器、财务异常检测、DCF/DDM估值 |
| **stock-daily-analysis** | 日频技术分析、AI决策建议 |
| **stock-analysis** | 报告模板、对比分析框架 |

## 核心能力

| 能力模块 | 状态 | 来源 |
|---------|------|------|
| **全球市场数据** | ✅ | yfinance + akshare |
| **技术指标图表** | ✅ | stock-market-pro |
| **8阶段投研框架** | ✅ 新增 | stock-research-executor |
| **多Agent并行研究** | ✅ 新增 | stock-research-executor |
| **A股选股器** | ✅ 增强 | china-stock-analysis |
| **财务异常检测** | ✅ 新增 | china-stock-analysis |
| **DCF/DDM估值** | ✅ 新增 | china-stock-analysis |
| **日频技术分析** | ✅ 新增 | stock-daily-analysis |
| **AI决策建议** | ✅ 新增 | stock-daily-analysis |
| **行业热力图** | ✅ | agent-stock |
| **资金流向分析** | ✅ | agent-stock |
| **价格警报** | ✅ | stock-monitor |
| **相关性分析** | ✅ | stock-correlation |
| **流动性分析** | ✅ | stock-liquidity |
| **情绪分析** | ✅ | finance-sentiment |
| **引用评级体系** | ✅ 新增 | stock-research-executor |

## 快速开始

### 1. 查询行情

```bash
# A 股
python scripts/finance.py quote 600519

# 港股
python scripts/finance.py quote 00700.HK

# 美股
python scripts/finance.py quote AAPL
```

### 2. 生成图表

```bash
# 带技术指标的图表
python scripts/finance.py chart AAPL 3mo --rsi --macd --bb

# 一键报告
python scripts/finance.py report 600519 6mo
```

### 3. 行业热力图

```bash
python scripts/finance.py heatmap ab  # A 股
python scripts/finance.py heatmap hk  # 港股
python scripts/finance.py heatmap us  # 美股
```

### 4. 资金流向

```bash
python scripts/finance.py fundflow 600519
```

### 5. 设置警报

```bash
python scripts/finance.py alert add AAPL --target 200 --stop 150
python scripts/finance.py alert list
python scripts/finance.py alert check
```

## 8阶段深度投研框架

当用户请求深度投研分析时，使用以下框架：

### Phase 1: Business Foundation (公司事实底座)
- 核心业务和产品线
- 营收和利润构成
- 客户基础和应用场景
- 在产业链中的位置
- 近期战略变化

### Phase 2: Industry Analysis (行业周期分析)
- 行业周期阶段（复苏/扩张/衰退/收缩）
- 供需 dynamics 和驱动因素
- 价格机制和历史波动性
- 竞争格局 (CR5)
- 政策和外部变量

### Phase 3: Business Breakdown (业务拆解)
- 一句话业务本质
- 业务分部门量化
- 利润引擎和收入驱动因素
- 定价能力和客户经济
- 子公司和非经常性项目

### Phase 4: Financial Quality (财务质量)
- 关键指标趋势 (CAGR, ROE, margins)
- 现金流 vs 盈利 cross-validation
- 异常筛查（应收账款、存货、非经常性项目）
- 财务风险识别

### Phase 5: Governance Analysis (股权与治理)
- 所有权结构和主要股东
- 股份 overhang（解禁、回购、二次发行）
- 管理层薪酬和激励
- 资本配置记录 (ROIC)

### Phase 6: Market Sentiment (市场分歧)
- 牛市逻辑和关键论点
- 熊市逻辑和关键论点
- 关键辩论点和数据验证节点
- 关键验证节点

### Phase 7: Valuation & Moat (估值与护城河)
- 护城河强度评级 (0-5) 及证据
- 相对估值（历史 + 同行）
- 绝对估值（reverse DCF, scenario analysis）
- 风险评估和失败模式

### Phase 8: Final Synthesis (综合报告)
- 信号灯评级 (🟢🟢🟢 / 🟡🟡🟡 / 🔴🔴)
- 投资逻辑链
- 关键财务数据表
- 监控清单（加强/退出条件）

## 引用评级体系 (A-E)

| 等级 | 来源 |
|------|------|
| **A** | 监管文件 (10-K, 20-F, 年报)、政府出版物 |
| **B** | 队列研究、行业协会报告、公司投资者关系材料 |
| **C** | 专家意见、公司新闻稿、知名媒体文章 |
| **D** | 预印本、会议摘要、博客文章 |
| **E** | 趣闻、理论推测、未经证实的谣言 |

## A股选股器

基于 china-stock-analysis 的多条件选股：

```python
python scripts/stock_screener.py \
  --scope "hs300" \
  --pe-max 15 \
  --roe-min 15 \
  --debt-ratio-max 60 \
  --dividend-min 2 \
  --output screening_result.json
```

### 选股条件

**估值指标**: PE, PB, PS, EV/EBITDA
**盈利**: ROE, ROA, 毛利率, 净利率
**成长性**: 营收增长率, 净利润增长率, 连续增长年数
**股息**: 股息率, 连续分红年数
**财务安全**: 资产负债率, 速动比率

## 财务异常检测

自动检测以下异常信号：

| 异常类型 | 检测规则 |
|---------|---------|
| 应收账款异常 | 应收账款增速 > 营收增速 × 1.5 |
| 现金流背离 | 净利润增长但经营现金流下降 |
| 存货异常 | 存货增速 > 营收增速 × 2 |
| 毛利率异常 | 波动 > 行业均值波动 × 2 |
| 关联交易 | 占比 > 30% |
| 股东/高管减持 | 近期减持公告 |

### 风险等级

- 🟢 低风险：无明显异常
- 🟡 中风险：1-2项轻微异常
- 🔴 高风险：多项异常或严重异常

## 估值计算器

支持 DCF、DDM、相对估值三种方法：

```python
python scripts/valuation_calculator.py \
  --code "600519" \
  --methods all \
  --discount-rate 10 \
  --terminal-growth 3 \
  --forecast-years 5 \
  --margin-of-safety 30 \
  --output valuation.json
```

### DCF 模型参数
- 折现率 (WACC): 默认 10%
- 预测期: 默认 5 年
- 永续增长率: 默认 3%

### DDM 模型参数
- 要求回报率: 默认 10%
- 股息增长率: 使用历史数据推算

## 日频技术分析

基于 stock-daily-analysis 的每日技术分析：

```python
from scripts.analyzer import analyze_stock

result = analyze_stock('600519')
print(result['ai_analysis']['operation_advice'])
```

### 技术指标
- MA5/10/20：移动平均线
- MACD：指数平滑异同移动平均线
- RSI：相对强弱指数
- 乖离率：价格偏离均线的程度

### AI 决策输出
```json
{
  "technical_indicators": {
    "trend_status": "强势多头",
    "ma5": 1500.0, "ma10": 1480.0, "ma20": 1450.0,
    "bias_ma5": 2.5,
    "macd_status": "金叉",
    "rsi_status": "强势买入",
    "buy_signal": "买入",
    "signal_score": 75
  },
  "ai_analysis": {
    "sentiment_score": 75,
    "operation_advice": "买入",
    "confidence_level": "高",
    "target_price": "1550",
    "stop_loss": "1420"
  }
}
```

## 脚本列表

| 脚本 | 功能 |
|------|------|
| `finance.py` | 主入口，支持 quote/chart/report/heatmap/fundflow/alert |
| `chart_generator.py` | 图表生成 (集成 stock-market-pro) |
| `data_fetcher.py` | 数据获取 (集成 yfinance + akshare) |
| `alert_manager.py` | 警报管理 (集成 stock-monitor) |
| `stock_screener.py` | A股选股器 (新增 china-stock-analysis) |
| `valuation_calculator.py` | 估值计算器 (新增 DCF/DDM) |
| `financial_analyzer.py` | 财务分析器 (新增 异常检测) |
| `analyzer.py` | 日频技术分析 (新增 stock-daily-analysis) |

## Gotchas

> ⚠️ 环境特定的坑，使用前必读

### 数据源限制
- **A股数据**：使用东方财富 API，需代理或境内网络
- **yfinance 限制**：对 A 股支持有限，优先使用 akshare
- **港股代码格式**：`00700.HK`（必须带后缀）
- **美股代码**：直接使用 ticker（如 `AAPL`）

### 编码问题（Windows）
- Windows 默认 GBK，所有脚本已添加 UTF-8 修复
- 如遇乱码，检查终端编码设置

### 选股器网络依赖
- A股选股器依赖东方财富 API，网络不稳定时可能失败
- 美股选股器使用 yfinance，速度较慢（需遍历多只股票）
- 建议在网络稳定时使用

### 图表输出
- 图表默认保存到 `D:\OpenClaw\outputs\charts\`
- 确保目录存在或脚本会自动创建

### 数据时效性
- 行情数据有 15 分钟延迟
- 财务数据按季度更新
- 建议结合实时数据验证

## 测试工作流

### 快速验证

```bash
# 1. 测试行情查询
python scripts/finance.py quote 600519

# 2. 测试图表生成
python scripts/finance.py chart 600519 3mo --rsi

# 3. 测试技术分析
python scripts/analyzer.py --code 600519
```

### 完整测试

```bash
# 运行所有测试
python scripts/test_all.py

# 测试选股器（需网络）
python scripts/stock_screener.py cn --pe-max 20 --limit 10

# 测试估值计算
python scripts/valuation_calculator.py --code 600519 --methods dcf

# 测试财务异常检测
python scripts/financial_analyzer.py --code 600519
```

### 预期输出

- 行情查询：返回 JSON 格式的实时价格
- 图表生成：PNG 文件保存到输出目录
- 技术分析：JSON 文件包含技术指标和 AI 建议
- 估值计算：DCF/DDM 估值结果

## 依赖

```bash
pip install yfinance akshare pandas numpy matplotlib mplfinance rich plotille
```

## 数据源

| 市场 | 数据源 |
|------|--------|
| A 股 | 东方财富 + AkShare |
| 港股 | 东方财富 + AkShare |
| 美股 | Yahoo Finance (yfinance) |

## 文件结构

```
unified-finance-skill/
├── SKILL.md                    # 饕餮整合版 v2.0
├── scripts/
│   ├── finance.py              # 主入口
│   ├── chart_generator.py      # 图表生成
│   ├── data_fetcher.py         # 数据获取
│   ├── alert_manager.py        # 警报管理
│   ├── stock_screener.py       # A股选股器
│   ├── valuation_calculator.py # 估值计算器
│   ├── financial_analyzer.py    # 财务异常检测
│   ├── analyzer.py             # 日频技术分析
│   └── complete_report.py      # 完整报告生成
├── references/
│   └── integration-log.md      # 整合日志
└── config/
    └── alerts.json             # 警报配置
```

---

*饕餮整合 v2.0 - 集众家之长 by 小灰灰 🐕*
