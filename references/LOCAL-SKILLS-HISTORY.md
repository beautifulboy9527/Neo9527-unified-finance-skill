# 本地金融 Skills 完整历史

**更新日期**: 2026-04-07  
**整理者**: 小灰灰 🐕

---

## 一、原始本地 Skills (整合前)

### 1. stock-assistant ⭐ (调度层)
- **定位**: 金融分析统一入口，需求理解后分发到专业 Skills
- **功能**: 调度层/路由器
- **状态**: ✅ 保留，可与 unified-finance-skill 并存

### 2. yfinance-data
- **定位**: Yahoo Finance 数据获取
- **功能**: 美股价格、历史数据、财报、期权链、股息、分析师目标价
- **状态**: ✅ 保留，作为数据源底层

### 3. stock-correlation
- **定位**: 股票相关性分析
- **功能**: 配对交易、行业聚类、滚动相关性、regime 条件相关性
- **状态**: ✅ 保留，独立分析工具

### 4. stock-liquidity
- **定位**: 流动性分析
- **功能**: 买卖价差、成交量、市场冲击估算、换手率
- **状态**: ✅ 保留，独立分析工具

### 5. finance-sentiment
- **定位**: 情绪分析
- **功能**: Reddit/X.com/News/Polymarket 跨平台情绪
- **状态**: ✅ 保留，独立分析工具

---

## 二、新增 Skills (2026-04-07 整合)

### 6. stock-market-pro 🆕
- **来源**: ClawHub (LeoYeAI/openclaw-master-skills)
- **定位**: 图表生成专家
- **功能**: RSI/MACD/BB/VWAP/ATR 技术指标、高分辨率 PNG、一键报告
- **状态**: ✅ 已安装，能力集成到 unified-finance-skill

### 7. agent-stock 🆕
- **来源**: ClawHub (anoyix/agent-stock)
- **定位**: A 股/港股数据专家
- **功能**: 行业热力图、条件选股、资金流向、板块分析
- **状态**: ✅ 已安装，能力集成到 unified-finance-skill

### 8. akshare-stock 🆕
- **来源**: 手动创建 (基于 AkShare 库)
- **定位**: 免费 A 股数据源 (备用)
- **功能**: A 股/港股/美股全覆盖、财务指标、龙虎榜
- **状态**: ✅ 已安装，作为备用数据源

### 9. bggg-skill-taotie 🆕
- **来源**: ClawHub (binggandata/bggg-skill-taotie)
- **定位**: 技能进化引擎
- **功能**: 并行对标、反向工程、渐进注入、模式记忆
- **状态**: ✅ 已安装，用于未来优化

### 10. unified-finance-skill 🆕
- **来源**: 饕餮整合计划创建
- **定位**: 统一金融分析超级 skill
- **功能**: 整合所有上述 skills 的核心能力
- **状态**: ✅ 已创建，持续完善中

---

## 三、完整 Skills 列表 (当前)

| # | Skill 名称 | 类型 | 定位 | 状态 |
|---|-----------|------|------|------|
| 1 | **stock-assistant** | 原始 | 调度层/入口 | ✅ 保留 |
| 2 | **yfinance-data** | 原始 | 美股数据源 | ✅ 保留 |
| 3 | **stock-correlation** | 原始 | 相关性分析 | ✅ 保留 |
| 4 | **stock-liquidity** | 原始 | 流动性分析 | ✅ 保留 |
| 5 | **finance-sentiment** | 原始 | 情绪分析 | ✅ 保留 |
| 6 | **stock-market-pro** | 新增 | 图表生成 | ✅ 集成 |
| 7 | **agent-stock** | 新增 | A/H 股数据 | ✅ 集成 |
| 8 | **akshare-stock** | 新增 | 备用数据源 | ✅ 集成 |
| 9 | **bggg-skill-taotie** | 新增 | 进化引擎 | ✅ 保留 |
| 10 | **unified-finance-skill** | 新增 | 统一入口 | ✅ 使用中 |

---

## 四、整合关系图

```
原始架构 (整合前):
┌─────────────────┐
│ stock-assistant │ ← 调度层
└────────┬────────┘
         │ 分发到
    ┌────┼────┬────────┬──────────┐
    ▼    ▼    ▼        ▼          ▼
 yfinance  correlation  liquidity  sentiment
 (数据)   (分析)      (分析)      (分析)


新架构 (整合后):
┌─────────────────────────────────────────┐
│     unified-finance-skill (新入口)      │
│  ┌─────────────────────────────────┐    │
│  │ finance.py (统一 CLI)           │    │
│  │ - quote (行情)                 │    │
│  │ - chart (图表)                 │    │
│  │ - report (报告)                │    │
│  │ - heatmap (热力图)             │    │
│  │ - fundflow (资金流向)          │    │
│  │ - alert (警报)                 │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
         ▲
         │ 集成能力来自
    ┌────┼────┬────────┬──────────┐
    ▼    ▼    ▼        ▼          ▼
 yfinance  agent-stock  stock-market-pro  akshare
 (美股)   (A/H 股)     (图表)          (备用)


保留的独立 skills:
- stock-assistant (原始调度层，可并存)
- stock-correlation (相关性分析专用)
- stock-liquidity (流动性分析专用)
- finance-sentiment (情绪分析专用)
- bggg-skill-taotie (进化引擎)
```

---

## 五、能力归属

### unified-finance-skill 集成能力

| 能力 | 来源 | 状态 |
|------|------|------|
| 行情查询 | yfinance + agent-stock | ✅ |
| 图表生成 | stock-market-pro | ✅ |
| 行业热力图 | agent-stock | ✅ |
| 资金流向 | agent-stock | ✅ |
| 警报管理 | stock-monitor (参考) | ✅ |
| 报告生成 | stock-market-pro | ✅ |

### 保留独立 skills 能力

| Skill | 核心能力 | 是否可集成 |
|-------|---------|-----------|
| stock-correlation | 相关性分析、配对交易 | 🔄 可后续集成 |
| stock-liquidity | 流动性分析、市场冲击 | 🔄 可后续集成 |
| finance-sentiment | 跨平台情绪分析 | 🔄 可后续集成 |

---

## 六、使用建议

### 日常使用 (推荐)
```bash
# 使用 unified-finance-skill
python finance.py quote AAPL
python finance.py chart MSFT 3mo --rsi --macd
python finance.py report 600519 6mo
```

### 专业分析
```bash
# 使用独立 skills
stock-correlation: 分析 AMD/NVDA 相关性
stock-liquidity: 分析小盘股流动性
finance-sentiment: 查看 Reddit/X 情绪
```

### 调度层 (兼容旧用法)
```bash
# stock-assistant 仍可作为入口
它会分发到对应的专业 skills
```

---

## 七、下一步整合计划

### 已完成 (Phase 1)
- ✅ 统一入口 (unified-finance-skill)
- ✅ 数据层整合 (yfinance + agent-stock + akshare)
- ✅ 图表层整合 (stock-market-pro)
- ✅ 警报层整合 (基础功能)

### 待完成 (Phase 2+)
- 🔄 集成 stock-correlation (相关性分析)
- 🔄 集成 stock-liquidity (流动性分析)
- 🔄 集成 finance-sentiment (情绪分析)
- 🔄 集成 8 维评分 (stock-analysis)
- 🔄 集成 Hot/Rumor Scanner

---

*本地 Skills 完整历史记录 - 小灰灰 🐕 - 2026-04-07*
