# Unified Finance Skill - 架构与迭代管理文档

> 版本: 2.2.0
> 更新时间: 2026-04-15
> 状态: 活跃开发中

---

## 🎯 定位与目标

**unified-finance-skill** 是金融 skills 的统一入口和融合产物，通过饕餮方法论整合所有金融 skills 的优势能力。

### 核心原则

1. **零硬编码** - 所有数据从真实数据源获取
2. **零模拟数据** - 数据源失败时返回 `null` 或明确错误
3. **完整集成** - 直接集成代码，而非路径引用
4. **模块化架构** - 每个功能独立可用，也可组合使用
5. **可持续迭代** - 架构支持后续功能扩展和优化

---

## 📊 金融 Skills 生态

### 已安装的金融 Skills

| Skill | 路径 | 核心能力 | 整合状态 |
|-------|------|---------|---------|
| **agent-stock** | `.agents\skills\agent-stock` | A股行情、K线、技术指标 | ✅ 已集成 |
| **akshare-stock** | `.agents\skills\akshare-stock` | A股财务数据、资金流向 | ✅ 已集成 |
| **akshare-data** | `.agents\skills\akshare-data` | 通用金融数据获取 | 📋 待评估 |
| **yfinance-data** | `.agents\skills\yfinance-data` | 美股/港股数据 | ✅ 已集成 |
| **akshare-data** | `.agents\skills\akshare-data` | 增强财务数据 | ✅ 已集成 (代码) |
| **stock-valuation-monitor** | `.agents\skills\stock-valuation-monitor` | 估值监控 | ✅ 已集成 (代码) |
| **china-stock-research** | `.agents\skills\china-stock-research` | 深度投研框架 | ✅ 已集成 (代码) |
| **stock-liquidity** | `.agents\skills\stock-liquidity` | 流动性分析 | ✅ 已集成 (代码) |
| **finance-sentiment** | `.agents\skills\finance-sentiment` | 情绪分析 | ✅ 已集成 (代码) |
| **stock-market-pro** | `.agents\skills\stock-market-pro` | 高级技术图表 | ✅ 已集成 (代码) |
| **stock-correlation** | `.agents\skills\stock-correlation` | 相关性分析 | ✅ 已集成 (代码) |
| **stock-evaluator-v3** | `C:\Users\Administrator\.agents\skills\stock-evaluator-v3` | 投资评估框架 | ✅ 已集成 (参考) |
| **stock-correlation** | `.agents\skills\stock-correlation` | 相关性分析 | 📋 待集成 |
| **stock-valuation-monitor** | `.agents\skills\stock-valuation-monitor` | 估值监控 | 📋 待集成 |
| **china-stock-analysis** | `.agents\skills\china-stock-analysis` | A股价值分析 | 📋 待集成 |
| **china-stock-research** | `.agents\skills\china-stock-research` | 8阶段投研框架 | 📋 待集成 |
| **earnings-preview** | `.agents\skills\earnings-preview` | 财报预览 | 📋 待评估 |
| **earnings-recap** | `.agents\skills\earnings-recap` | 财报回顾 | 📋 待评估 |
| **estimate-analysis** | `.agents\skills\estimate-analysis` | 估值分析 | 📋 待评估 |
| **funda-data** | `.agents\skills\funda-data` | 基本面数据 | 📋 待评估 |
| **stock-assistant** | `.agents\skills\stock-assistant` | 股票助手 | 📋 待评估 |
| **stock-cli** | `.agents\skills\stock-cli` | 命令行工具 | 📋 待评估 |

---

## 🏗️ 当前架构

```
unified-finance-skill/
├── SKILL.md                    # Skill 定义 (v2.2.0)
├── config/
│   ├── alerts.json            # 警报配置
│   └── portfolio.json         # 组合配置
└── scripts/
    ├── finance.py             # 🎯 统一入口 (CLI)
    ├── config.py              # 输出路径配置
    │
    ├── core/                  # 核心模块 (数据获取)
    │   ├── quote.py           # ✅ 行情查询
    │   ├── technical.py       # ✅ 技术分析
    │   └── financial.py       # ✅ 财务数据
    │
    └── features/              # 功能模块 (高级分析)
        ├── liquidity.py       # ✅ 流动性分析 (完整集成)
        ├── sentiment.py       # ✅ 情绪分析 (完整集成)
        └── chart.py           # ✅ 高级技术图表 (完整集成)
```

---

## 📋 功能覆盖矩阵

### 已实现 ✅

| 功能 | 模块 | 数据源 | 市场支持 |
|------|------|--------|----------|
| 行情查询 | `core/quote.py` | agent-stock, yfinance | A股/港股/美股 |
| 技术指标 | `core/technical.py` | agent-stock | A股 |
| 财务摘要 | `core/financial.py` | akshare, yfinance | A股/美股 |
| 资金流向 | `core/financial.py` | akshare | A股 |
| 流动性分析 | `features/liquidity.py` | yfinance | 全球 |
| 情绪分析 | `features/sentiment.py` | Adanos API | 美股 |
| 高级技术图表 | `features/chart.py` | yfinance + mplfinance | 全球 |
| 相关性分析 | `features/correlation.py` | yfinance | 全球 |
| 增强财务数据 | `features/enhanced_financial.py` | akshare | A股/港股/美股 |
| 估值监控 | `features/valuation.py` | yfinance | 全球 |
| 深度投研框架 | `features/research.py` | yfinance | 全球 |
| 技术指标 | `core/technical.py` | agent-stock | A股 |
| 财务摘要 | `core/financial.py` | akshare, yfinance | A股/美股 |
| 资金流向 | `core/financial.py` | akshare | A股 |
| 流动性分析 | `features/liquidity.py` | yfinance | 全球 |
| 情绪分析 | `features/sentiment.py` | Adanos API | 美股 |

### 待实现 📋

| 功能 | 来源 Skill | 优先级 | 预计工作量 |
|------|-----------|--------|-----------|
| 高级技术图表 | stock-market-pro | P0 | 中 |
| 相关性分析 | stock-correlation | P1 | 低 |
| 估值监控 | stock-valuation-monitor | P1 | 中 |
| A股价值分析 | china-stock-analysis | P0 | 高 |
| 8阶段投研 | china-stock-research | P2 | 高 |
| 财报预览 | earnings-preview | P2 | 低 |
| 财报回顾 | earnings-recap | P2 | 低 |

---

## 🔄 集成方式说明

### 完整代码集成 ✅ (推荐)

将原 skill 的核心代码完整复制到 unified-finance-skill 中，消除外部依赖。

**已应用**:
- `stock-liquidity` → `features/liquidity.py`
- `finance-sentiment` → `features/sentiment.py`

**优点**:
- 无外部依赖
- 可独立运行
- 易于维护和优化

### Subprocess 调用

通过命令行调用其他 skill 的脚本。

**已应用**:
- `agent-stock` → `core/quote.py`, `core/technical.py`

**优点**:
- 利用现有能力
- 不重复开发

**缺点**:
- 依赖外部 skill 安装
- 调用开销

### 直接 Import

直接导入 Python 库。

**已应用**:
- `akshare` → `core/financial.py`
- `yfinance` → `core/quote.py`, `core/financial.py`

**优点**:
- 性能最优
- 无额外依赖

---

## 🛠️ 后续迭代计划

### Phase 1: 核心功能完善 (本周)

| 任务 | 来源 | 目标模块 | 状态 |
|------|------|---------|------|
| 高级技术图表 | stock-market-pro | `features/chart.py` | ✅ 已完成 |
| A股价值分析 | china-stock-analysis | `features/valuation.py` | 📋 待开发 |
| AI决策建议 | stock-daily-analysis | `core/technical.py` | 📋 待集成 |

### Phase 2: 高级功能扩展 (下周)

| 任务 | 来源 | 目标模块 | 状态 |
|------|------|---------|------|
| 相关性分析 | stock-correlation | `features/correlation.py` | 📋 待开发 |
| 估值监控 | stock-valuation-monitor | `features/valuation_monitor.py` | 📋 待开发 |
| 财报分析 | earnings-preview/recap | `features/earnings.py` | 📋 待开发 |

### Phase 3: 深度投研 (后续)

| 任务 | 来源 | 目标模块 | 状态 |
|------|------|---------|------|
| 8阶段投研框架 | china-stock-research | `reports/deep_research.py` | 📋 待开发 |
| DCF估值 | china-stock-analysis | `reports/valuation.py` | 📋 待开发 |
| 财务异常检测 | china-stock-analysis | `features/anomaly.py` | 📋 待开发 |

---

## 📁 输出路径规范

所有输出统一到 `D:\OpenClaw\outputs\`:

```
D:\OpenClaw\outputs\
├── reports\           # 分析报告
├── charts\            # 图表文件
├── data\              # 数据文件
├── logs\              # 日志文件
└── cache\             # 缓存数据
```

---

## ⚠️ 数据质量保障

### 禁止事项

1. **禁止硬编码** - 任何股票的特定数据
2. **禁止模拟数据** - 数据源失败时返回 `null`
3. **禁止默认值** - 不用默认值替代真实数据

### 数据源失败处理

```python
# 正确做法
def get_data(symbol):
    result = try_source_1(symbol)
    if result is None:
        result = try_source_2(symbol)
    if result is None:
        return {'data': None, 'error': '所有数据源失败'}
    return result

# 错误做法
def get_data(symbol):
    return {'pe': 15.0}  # 禁止使用默认值
```

### 数据时效性标注

所有数据必须标注:
- `data_source`: 数据来源
- `update_time`: 更新时间
- `error`: 错误信息 (如有)

---

## 📝 更新日志

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-04-15 | v2.6.0 | 饕餮整合 stock-valuation-monitor + china-stock-research (估值监控+深度投研) |
| 2026-04-15 | v2.5.0 | 完整集成 akshare-data (增强财务数据、宏观数据) |
| 2026-04-15 | v2.4.0 | 完整集成 stock-correlation (相关性分析) |
| 2026-04-15 | v2.3.0 | 完整集成 stock-market-pro (高级技术图表) |
| 2026-04-15 | v2.2.0 | 完整集成 stock-liquidity, finance-sentiment |
| 2026-04-15 | v2.1.0 | 创建模块化架构 |
| 2026-04-15 | v2.0.0 | 饕餮整合启动 |

---

*by 小灰灰 🐕 | unified-finance-skill 架构文档*
