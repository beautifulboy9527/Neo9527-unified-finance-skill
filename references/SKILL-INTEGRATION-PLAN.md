# 外部 Skills 整合计划

**评估日期**: 2026-04-07  
**评估者**: 小灰灰 🐕

---

## 一、发现的优质 Skills

### 1. stock-data-skill ⭐⭐⭐⭐⭐ (强烈推荐)

**来源**: https://github.com/openstockdata/stock-data-skill

**核心能力**:
- ✅ 47 个数据工具
- ✅ A 股/港股/美股/加密货币全覆盖
- ✅ 技术指标、财务数据、资金流向
- ✅ 筹码分布、持仓组合评估
- ✅ 板块轮动分析
- ✅ 交易信号生成

**数据源**:
- Tushare (需 Token)
- Alpha Vantage (需 API Key)
- AkShare (免费)
- OKX (加密货币)

**集成价值**: ⭐⭐⭐⭐⭐
- 补齐财报数据缺失
- 补齐筹码分布数据
- 补齐交易信号生成
- 补齐持仓组合分析

**集成成本**: 中
- 需要配置 Tushare Token
- CLI 工具需要安装

---

### 2. tradingview-screener ⭐⭐⭐⭐⭐ (强烈推荐)

**来源**: https://github.com/tradingview-screener

**核心能力**:
- ✅ 6 大类资产筛选 (股票/加密货币/外汇/债券/期货)
- ✅ 13,000+ 数据字段
- ✅ YAML 驱动的信号检测
- ✅ 预定义策略 (金叉/超卖/放量突破)
- ✅ 无需认证 (使用 TradingView 公开数据)

**数据源**:
- TradingView (免费公开数据)

**集成价值**: ⭐⭐⭐⭐⭐
- 补齐多条件选股功能
- 补齐基本面筛选
- 补齐技术面筛选
- 补齐策略回测

**集成成本**: 低
- 无需 API Key
- 自动创建虚拟环境

---

### 3. stock-evaluator ⭐⭐⭐⭐ (推荐)

**来源**: https://github.com/demandgap/stock-evaluator (404 无法访问)

**核心能力** (根据描述):
- ✅ 综合估值分析
- ✅ 基本面研究
- ✅ 投资价值评估

**集成价值**: ⭐⭐⭐⭐
- 补齐估值分位数功能
- 补齐深度基本面分析

**集成成本**: 未知 (需确认仓库状态)

---

## 二、整合优先级

### P0 - 立即整合

| Skill | 功能 | 预计工作量 |
|-------|------|-----------|
| **tradingview-screener** | 多条件选股 | 2-3 小时 |
| **stock-data-skill** | 财报数据 + 组合管理 | 3-4 小时 |

**理由**:
1. tradingview-screener 无需 API Key，立即可用
2. stock-data-skill 功能最全面，补齐最多短板

---

### P1 - 近期整合

| Skill | 功能 | 预计工作量 |
|-------|------|-----------|
| stock-evaluator (如可用) | 估值分析 | 2-3 小时 |
| 新闻聚合类 skill | 新闻推送 | 2-3 小时 |

---

### P2 - 后期整合

| 类型 | 功能 | 预计工作量 |
|------|------|-----------|
| 回测框架 | 策略验证 | 4-6 小时 |
| 产业链分析 | 供应链关系 | 3-4 小时 |

---

## 三、整合方案

### tradingview-screener 整合

**集成方式**: 作为独立子 skill 保留，通过 finance.py 调用

**集成点**:
```python
# finance.py 新增命令
python finance.py screen --pe-max 20 --roe-min 15 --market us
python finance.py signal golden-cross --market us
```

**功能映射**:
| 用户需求 | 功能 | 状态 |
|---------|------|------|
| 多条件选股 | screen 模式 | ✅ |
| 基本面筛选 | PE/PB/ROE 等字段 | ✅ |
| 技术面筛选 | RSI/MACD/SMA 等 | ✅ |
| 策略信号 | signal 模式 | ✅ |

---

### stock-data-skill 整合

**集成方式**: 作为数据源层补充

**集成点**:
```python
# data_fetcher.py 新增数据源
from stock_data import get_financials, get_chip_distribution

# 财报数据
financials = get_financials('600519')

# 筹码分布
chip = get_chip_distribution('300058')
```

**功能映射**:
| 用户需求 | 功能 | 状态 |
|---------|------|------|
| 财报数据 | stock_fundamentals | ✅ |
| 筹码分布 | stock_chip | ✅ |
| 持仓组合 | portfolio_analyze | ✅ |
| 交易信号 | trading_signals | ✅ |
| 板块轮动 | sector_analyze | ✅ |

---

## 四、执行步骤

### 步骤 1: 安装 tradingview-screener

```bash
# 克隆到 skills 目录
git clone https://github.com/tradingview-screener/tradingview-screener.git \
  C:\Users\Administrator\.openclaw\workspace\.agents\skills\tradingview-screener

# 运行安装脚本
cd tradingview-screener
.\install.sh  # 或手动创建 venv
```

### 步骤 2: 安装 stock-data-skill

```bash
# 克隆到 skills 目录
git clone https://github.com/openstockdata/stock-data-skill.git \
  C:\Users\Administrator\.openclaw\workspace\.agents\skills\stock-data

# 安装 CLI 工具
cd stock-data
pip install -e .

# 配置环境变量 (可选，增强功能)
# TUSHARE_TOKEN=xxx
# ALPHA_VANTAGE_API_KEY=xxx
```

### 步骤 3: 集成到统一入口

修改 `finance.py`:
- 添加 `screen` 命令
- 添加 `signal` 命令
- 添加 `portfolio` 命令
- 添加 `fundamentals` 命令

### 步骤 4: 测试验证

```bash
# 测试选股
python finance.py screen --pe-max 20 --roe-min 15

# 测试信号
python finance.py signal golden-cross

# 测试财报
python finance.py fundamentals 600519

# 测试持仓
python finance.py portfolio
```

---

## 五、预期效果

### 功能补齐

| 缺失功能 | 补齐 skill | 状态 |
|---------|-----------|------|
| 多条件选股 | tradingview-screener | ✅ |
| 财报数据 | stock-data-skill | ✅ |
| 估值分析 | stock-data-skill | ✅ |
| 持仓管理 | stock-data-skill | ✅ |
| 交易信号 | stock-data-skill | ✅ |
| 板块轮动 | stock-data-skill | ✅ |

### 数据源增强

| 数据类型 | 新增来源 | 说明 |
|---------|---------|------|
| 财报数据 | Tushare | A 股深度数据 |
| 技术指标 | TradingView | 13,000+ 字段 |
| 加密货币 | OKX | 实时价格 |

### 整体完成度提升

**当前**: 80%  
**整合后**: **95%+** 🚀

---

## 六、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Tushare Token 限制 | 中 | 使用免费版 + 缓存 |
| TradingView 反爬 | 低 | 限流 + 缓存 |
| 依赖冲突 | 低 | 独立 venv 隔离 |
| 维护成本 | 中 | 文档化 + 自动化测试 |

---

## 七、建议

### 立即执行

1. ✅ 安装 tradingview-screener (无依赖，立即可用)
2. ✅ 安装 stock-data-skill (补齐最多短板)
3. ✅ 集成到 finance.py 统一入口

### 配置建议

1. **Tushare Token**: 注册免费账号获取 (支持 1000 次/天)
2. **Alpha Vantage Key**: 注册免费账号获取 (5 次/分钟)
3. **缓存策略**: 财报数据缓存 24 小时，行情数据缓存 5 分钟

---

*外部 Skills 整合计划 - 小灰灰 🐕 - 2026-04-07*
