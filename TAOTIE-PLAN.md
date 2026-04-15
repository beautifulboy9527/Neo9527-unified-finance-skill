# 饕餮进化计划 - v2.6.0

> 目标: 将临时 Skills 的优势提炼合并到 unified-finance-skill
> 方法: 饕餮式整合 - 分析能力 → 提取优势 → 整合实现

---

## 📊 能力矩阵现状

### 已有完整实现 (无需整合)

| 能力 | Skill | 模块 | 状态 |
|------|-------|------|------|
| 数据-美股 | yfinance-data | `core/quote.py` | ✅ 完整 |
| 数据-A股 | akshare-data | `core/financial.py` | ✅ 完整 |
| 技术图表 | stock-market-pro | `features/chart.py` | ✅ 完整 |
| 情绪分析 | finance-sentiment | `features/sentiment.py` | ✅ 完整 |
| 相关性 | stock-correlation | `features/correlation.py` | ✅ 完整 |
| 流动性 | stock-liquidity | `features/liquidity.py` | ✅ 完整 |

### 临时 Skills (需饕餮整合)

| Skill | 描述 | 问题 | 整合方案 |
|-------|------|------|---------|
| china-stock-analysis | 8阶段投研框架 | ❌ 仅框架 | 实现代码 |
| china-stock-research | 深度投研执行器 | ❌ 仅框架 | 实现代码 |
| stock-valuation-monitor | 估值监控 | ❌ 仅框架 | 实现代码 |
| stock-cli | 命令行工具 | ❌ 仅框架 | 已有 finance.py |

---

## 🎯 整合目标

### Phase 1: 估值监控模块 ⭐⭐⭐⭐⭐
**来源**: stock-valuation-monitor
**目标文件**: `features/valuation.py`
**核心能力**:
- PE/PB 历史百分位计算
- ETF 溢价/折价监控
- BAND 分析 (股债利差)
- 个股估值跟踪

### Phase 2: 深度投研框架 ⭐⭐⭐⭐⭐
**来源**: china-stock-research, stock-research-executor
**目标文件**: `features/research.py`
**核心能力**:
- 8阶段投研流程
- 多代理并行分析
- 结构化报告生成

### Phase 3: 价值分析框架 ⭐⭐⭐⭐
**来源**: china-stock-analysis
**目标文件**: `features/value_analysis.py`
**核心能力**:
- DCF 估值模型
- DDM 估值模型
- 相对估值法
- 投资建议生成

---

## 📋 执行计划

### Step 1: 估值监控 (30分钟)
```
创建 features/valuation.py
├── PE/PB 百分位计算
├── ETF 溢价监控
├── BAND 分析
└── 估值跟踪
```

### Step 2: 深度投研 (45分钟)
```
创建 features/research.py
├── 8阶段框架
├── 数据采集
├── 分析执行
└── 报告生成
```

### Step 3: 价值分析 (45分钟)
```
创建 features/value_analysis.py
├── DCF 模型
├── DDM 模型
├── 相对估值
└── 综合建议
```

### Step 4: 统一入口更新 (15分钟)
```
更新 finance.py
├── valuation 命令
├── research 命令
└── value 命令
```

---

## 🔧 技术实现

### 数据源策略

| 功能 | 主数据源 | 备用数据源 |
|------|---------|-----------|
| PE/PB 百分位 | akshare | yfinance |
| 历史估值 | akshare | - |
| 宏观数据 | akshare | - |
| 财务数据 | akshare | yfinance |

### 输出标准

```
所有输出统一到: D:\OpenClaw\outputs\
├── reports/    # 分析报告
├── charts/     # 图表文件
├── data/       # 数据文件
└── logs/       # 日志文件
```

---

## ✅ 完成标准

1. **功能完整**: 所有核心功能可用
2. **零硬编码**: 数据从真实数据源获取
3. **错误处理**: 网络异常、数据缺失处理
4. **文档完善**: SKILL.md 更新
5. **测试通过**: 至少 5 个测试用例

---

**准备好开始执行了吗？**
