# Unified Finance Skill - 开发历程与迭代管理

> **项目状态**: ✅ 活跃开发中  
> **最后更新**: 2026-04-16 08:07
> **版本**: v3.1
> **GitHub**: https://github.com/beautifulboy9527/unified-finance-skill

---

## 📋 目录

- [[#项目概览]]
- [[#开发历程]]
- [[#整合项目清单]]
- [[#核心功能矩阵]]
- [[#竞争优势]]
- [[#架构设计]]
- [[#CLI命令手册]]
- [[#迭代计划]]
- [[#开发日志]]

---

## 项目概览

### 项目定位

**Unified Finance Skill** 是一个多市场、多资产类别的金融分析技能库，整合了传统股票市场、加密货币、贵金属等多个领域的分析能力，提供从数据获取到交易决策的完整解决方案。

### 核心特点

- 🌍 **多市场支持**: A股、港股、美股、加密货币、贵金属
- 📊 **三层分析框架**: 宏观 → 行业 → 个股 系统化分析
- 🎯 **信号验证**: 基于历史数据的成功率统计
- ⚙️ **风险管理**: ATR止损 + 仓位计算 + 目标价
- 🤖 **Agent协调**: 智能路由 + 多Agent协作
- 📈 **理念驱动**: 吸收大师级实战经验

### 技术栈

```
数据源层: AkShare + TuShare + yfinance + ccxt
分析层: pandas + numpy + ta-lib
AI层: 本地模型 + 可选API (DeepSeek/Gemini)
输出层: Markdown报告 + JSON数据
```

---

## 开发历程

### Phase 1: 基础能力建设 (Week 1-2)

**目标**: 建立核心数据获取和分析能力

**成果**:
- ✅ 行情数据模块 (A股/港股/美股)
- ✅ 技术分析模块 (MA/MACD/RSI/KDJ)
- ✅ 财务数据模块 (财务报表/资金流向)
- ✅ 基础CLI接口

**代码量**: ~5000行

---

### Phase 2: 能力扩展 (Week 3-4)

**目标**: 扩展到多市场和多资产类别

**成果**:
- ✅ 新闻聚合模块 (多源新闻/情绪分析)
- ✅ 期权分析模块 (Black-Scholes/Greeks)
- ✅ 相关性分析模块
- ✅ 估值分析模块
- ✅ 加密货币模块 (ccxt集成)
- ✅ 贵金属模块 (金银比等)

**代码量**: ~8000行

---

### Phase 3: 饕餮整合 - 系统化框架 (2026-04-16)

**目标**: 整合高价值外部 Skills，建立系统化分析框架

**整合来源**:
1. **sm-analyze** - 三层分析框架
2. **entry-signals** - 历史验证信号库
3. **sm-stock-daily-analysis** - 评分设计思路

**成果**:
- ✅ 三层分析框架 (宏观20分 + 行业20分 + 个股60分)
- ✅ 入场信号库 (30个验证信号，最高88%成功率)
- ✅ 风险管理模块 (ATR止损 + 仓位计算)
- ✅ 评分引擎 (0-100分综合评分)
- ✅ Agent协调器 (5种Agent协作)

**代码量**: +4200行

**文档**: [饕餮整合完成报告](file:///C:/Users/Administrator/.openclaw/workspace/.agents/skills/unified-finance-skill/TAOTIE-COMPLETION-REPORT.md)

---

### Phase 4: 理念提升 - 大师级智慧 (2026-04-16)

**目标**: 吸收技术分析大师的实战理念

**整合来源**:
- **technical-analysis** - 20,000+小时实战经验

**成果**:
- ✅ 成交量验证器 (突破有效性验证)
- ✅ 上下文过滤器 (趋势/位置分析)
- ✅ 失败模式检测器 (假突破/假跌破)

**核心理念**:
- 价格即真理
- 上下文胜过模式
- 成交量验证
- 失败模式也是信号

**代码量**: +2500行

---

### Phase 5: 待开发 (Future)

**目标**: 完善生态系统

**计划**:
- ⏳ 回测系统 (信号验证)
- ⏳ DEX数据集成 (等待API)
- ⏳ 智能钱包追踪 (等待API)
- ⏳ 自动化交易执行
- ⏳ Darwin Skill 正式评估

---

### Phase 5: 监管监控整合 (2026-04-16 06:40-06:50)

**目标**: 补充监管风险监控能力

**整合来源**:
- **regulation-monitor** (ClawHub 安全验证通过)

**成果**:
- ✅ 监管监控器 (NFRA/CSRC/PBOC)
- ✅ 公告抓取与解析
- ✅ 影响等级评估 (high/medium/low)
- ✅ 监管风险评分 (0-100)
- ✅ 投资组合影响分析

**代码量**: +1200行

**Commit**: 1362c9f

---

### Phase 6: 打板筛选整合 (2026-04-16 06:54-06:58)

**目标**: 补充短线打板能力

**整合来源**:
- **stock-board** (ClawHub 安全验证通过)

**成果**:
- ✅ 涨停板实时扫描
- ✅ 强势股筛选 (涨幅>7%)
- ✅ 连板数据统计
- ✅ 打板市场情绪分析
- ✅ 打板机会识别

**代码量**: +1700行

**Commit**: c1cfc57

---

### Phase 7: 地区化分析整合 (2026-04-16 07:04-07:16)

**目标**: 增强新闻分析能力

**整合来源**:
- **stock-recommend** 思路借鉴

**成果**:
- ✅ 地区分类 (美国/欧洲/亚洲/中国)
- ✅ 地区影响评估
- ✅ 新闻驱动推荐
- ✅ 行业影响分析
- ✅ 地区联动分析

**代码量**: +1400行

**Commit**: f6594dd

---

### Phase 8: 股票筛选器整合 (2026-04-16 07:56-08:02)

**目标**: 补充选股器能力

**整合来源**:
- **stock-screener-cn** (ClawHub 安全验证通过)

**成果**:
- ✅ 11种筛选策略
- ✅ A股/港股/美股支持
- ✅ 多策略组合筛选 (AND/OR)
- ✅ 技术指标计算
- ✅ 批量筛选

**代码量**: +1900行

**Commit**: d9bbc5b

---

## 整合项目清单

### 已整合项目

| 项目 | 类型 | 整合时间 | 核心价值 | 整合方式 |
|------|------|---------|---------|---------|
| **sm-analyze** | 分析框架 | 2026-04-16 | 三层分析框架 + 100分评分体系 | 代码重写 |
| **entry-signals** | 信号库 | 2026-04-16 | 30个验证信号，5095个样本 | 理念吸收 |
| **sm-stock-daily-analysis** | 技术分析 | 2026-04-16 | signal_score + target_price设计 | 部分借鉴 |
| **technical-analysis** | 大师理念 | 2026-04-16 | 20,000小时实战智慧 | 理念吸收 |
| **regulation-monitor** | 监管监控 | 2026-04-16 | 监管公告监控 + 风险评分 | 代码重写 |
| **stock-board** | 打板筛选 | 2026-04-16 | 涨停板/强势股/连板筛选 | Python重写 |
| **stock-recommend** | 地区化分析 | 2026-04-16 | 地区化新闻分析 + 推荐 | 思路借鉴 |
| **stock-screener-cn** | 股票筛选器 | 2026-04-16 | 11种筛选策略 | 代码重写 |

### 已评估暂缓项目

| 项目 | 类型 | 暂缓原因 | 未来计划 |
|------|------|---------|---------|
| **gmgn-market** | DEX数据 | 需要GMGN_API_KEY | 等待API配置 |
| **FinGPT** | 金融LLM | 需要GPU资源 | 可选增强 |

### 我们独有的能力

| 能力 | 说明 | 价值 |
|------|------|------|
| **传统市场覆盖** | A股/港股/美股完整支持 | ⭐⭐⭐⭐⭐ |
| **贵金属分析** | 金银比/金属价格 | ⭐⭐⭐⭐ |
| **期权分析** | Black-Scholes + Greeks | ⭐⭐⭐⭐ |
| **新闻聚合** | 多源新闻 + 情绪分析 | ⭐⭐⭐⭐ |
| **Agent协调器** | 智能路由 + 多Agent | ⭐⭐⭐⭐⭐ |

---

## 核心功能矩阵

### 市场覆盖

| 市场 | 行情 | 分析 | 信号 | 评分 | 风险 | 成交量 | 上下文 | 失败模式 | 监管 | 打板 | 筛选 |
|------|------|------|------|------|------|--------|--------|---------|------|------|------|
| **A股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **港股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **美股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| **加密货币** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **贵金属** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |

### 功能模块

```
unified-finance-skill/
├── scripts/
│   ├── core/                    # 核心模块
│   │   ├── quote.py            # 行情数据
│   │   ├── technical.py        # 技术分析
│   │   └── financial.py        # 财务数据
│   │
│   ├── features/                # 功能模块
│   │   ├── analysis_framework.py   # 三层分析框架 ⭐
│   │   ├── entry_signals.py        # 入场信号库 ⭐
│   │   ├── risk_management.py      # 风险管理 ⭐
│   │   ├── scoring_engine.py       # 评分引擎 ⭐
│   │   ├── volume_validator.py     # 成交量验证 ⭐
│   │   ├── context_filter.py       # 上下文过滤 ⭐
│   │   ├── failed_patterns.py      # 失败模式检测 ⭐
│   │   ├── crypto.py              # 加密货币
│   │   ├── metals.py              # 贵金属
│   │   ├── options.py             # 期权分析
│   │   ├── news.py                # 新闻聚合
│   │   ├── sentiment_enhanced.py  # 情绪分析
│   │   ├── valuation.py           # 估值分析
│   │   └── correlation.py         # 相关性分析
│   │
│   ├── agent/                   # Agent模块
│   │   └── orchestrator.py      # Agent协调器
│   │
│   └── finance.py               # 主入口
│
└── docs/                        # 文档
    ├── TAOTIE-INTEGRATION-PLAN.md
    ├── TAOTIE-COMPLETION-REPORT.md
    ├── TECHNICAL-ANALYSIS-EVALUATION.md
    ├── SM-ANALYZE-INTEGRATION-PLAN.md
    ├── ENTRY-SIGNALS-INTEGRATION-PLAN.md
    └── GMGN-MARKET-EVALUATION.md
```

---

## 竞争优势

### 1. 系统化分析框架

**三层分析** (来自 sm-analyze):
```
宏观 (20分) → 行业 (20分) → 个股 (60分)
    ↓              ↓              ↓
 大势判断      板块强度        技术形态
 市场周期      资金流向        量价配合
 北向资金      相对强度        位置评估
```

**优势**: 不只看技术，而是从宏观到微观的系统化分析

### 2. 历史验证信号库

**30个验证信号** (来自 entry-signals):

| 信号 | 成功率 | 样本 | 说明 |
|------|--------|------|------|
| 多时间框架多头对齐 | **88%** | 164 | 最高成功率 |
| SMA金叉 + MACD多头 | **82%** | 184 | 经典组合 |
| 加仓获胜仓位 | **80%** | 157 | 趋势跟踪 |

**优势**: 不是猜测，而是基于5095个真实样本的统计验证

### 3. 成交量验证

**核心原则** (来自 technical-analysis):
```
放量突破 → 高概率真实 ✅
缩量突破 → 假突破风险 ⚠️
巨量反转 → 高可靠性 ✅
```

**优势**: 突破信号必须成交量确认，避免假突破陷阱

### 4. 上下文过滤

**智能调整**:
```
趋势中的背离 → 置信度降低30% ⚠️
关键位置形态 → 置信度提升30% ✅
强趋势中反转 → 置信度降低40% ⚠️
```

**优势**: 同样的形态在不同位置含义不同，避免刻舟求剑

### 5. 失败模式检测

**反向思维**:
```
假突破 → 做空信号 📉
假跌破 → 做多信号 📈
失败旗形 → 反向交易 🔄
```

**优势**: 失败的模式本身就是交易机会

### 6. 多市场统一

**一个接口，多个市场**:
```python
# A股
python finance.py score 600519

# 美股
python finance.py score AAPL

# 加密货币
python finance.py crypto quote BTC/USDT

# 贵金属
python finance.py metals XAU
```

**优势**: 学习成本低，一套命令通吃所有市场

### 7. 专业级风险管理

**ATR止损**:
```
保守止损: 1倍ATR
标准止损: 2倍ATR (推荐)
激进止损: 3倍ATR
```

**仓位计算**:
```
单笔风险: 2%总资金
风险收益比: 1:2 (最低)
自动计算股数和金额
```

**优势**: 科学的仓位和止损管理，避免情绪化交易

---

## 架构设计

### 数据流

```
用户请求
    ↓
Agent协调器 (智能路由)
    ↓
┌─────────────────────────────────────┐
│  Data Agent  │ Research Agent │ ... │
│      ↓            ↓              ↓   │
│  数据获取     分析处理      决策生成  │
└─────────────────────────────────────┘
    ↓
结果整合 → Markdown报告 / JSON数据
```

### Agent类型

| Agent | 职责 | 工具 |
|-------|------|------|
| **Router** | 智能路由，判断意图 | - |
| **Data** | 数据获取 | quote, crypto, metals |
| **Research** | 深度研究 | framework, scoring |
| **Trading** | 交易决策 | signals, risk |
| **Reporter** | 报告生成 | report, visualization |

### 评分体系

**100分制综合评分**:

```
总分 = 宏观(20) + 行业(20) + 个股(60) + 信号加成(±10)

评级:
80-100: 强势 - 可积极参与
65-79:  偏强 - 可适度参与
50-64:  中性 - 观望为主
35-49:  偏弱 - 谨慎
0-34:   弱势 - 回避
```

---

## CLI命令手册

### 核心命令 (60+)

#### 行情查询
```bash
# 单只股票
python finance.py quote 600519

# 批量查询
python finance.py quote --batch 600519 000001 000002

# 加密货币
python finance.py crypto quote BTC/USDT --exchange kraken

# 贵金属
python finance.py metals XAU
python finance.py metals --ratio  # 金银比
```

#### 技术分析
```bash
# 技术指标
python finance.py technical AAPL

# 完整分析
python finance.py full 600519

# 快速分析
python finance.py quick AAPL
```

#### 综合分析 (饕餮整合)
```bash
# 综合评分 (0-100)
python finance.py score AAPL

# 三层分析框架
python finance.py framework 600519

# 入场信号检测
python finance.py signals AAPL

# 风险管理
python finance.py risk AAPL --capital 100000

# 完整报告
python finance.py report-full AAPL
```

#### 监管监控 (Phase 5)
```bash
# 查看监管公告
python finance.py regulation --days 7

# 检查股票监管风险
python finance.py regulation --symbol 600036

# 生成监管摘要
python finance.py regulation --summary
```

#### 打板筛选 (Phase 6)
```bash
# 涨停板扫描
python finance.py board --limit-up

# 强势股扫描
python finance.py board --strong

# 连板股扫描
python finance.py board --continuous

# 市场情绪分析
python finance.py board --market

# 打板机会
python finance.py board --opportunities
```

#### 地区化分析 (Phase 7)
```bash
# 地区化新闻分析
python finance.py regional-news --type regional

# 新闻驱动推荐
python finance.py regional-news --type recommend
```

#### 股票筛选器 (Phase 8)
```bash
# 单策略筛选
python finance.py screen --strategy ma_bull --market a

# 多策略组合
python finance.py screen --strategies ma_bull macd_golden --mode and

# 列出所有策略
python finance.py screen --list
```

#### 期权分析
```bash
# Greeks计算
python finance.py options --S 266 --K 270 --T 30 --sigma 0.3

# 期权链分析
python finance.py options --S 266 --chain
```

#### 新闻与情绪
```bash
# 热门新闻
python finance.py news fetch --source sina --count 10

# 情绪分析
python finance.py sentiment AAPL --days 7
```

---

## 迭代计划

### 短期 (本周)

- [ ] Darwin Skill 正式评估
- [ ] 信号模块与评分引擎深度集成
- [ ] CLI命令文档完善
- [ ] 单元测试补充

### 中期 (本月)

- [ ] 回测系统开发
- [ ] 成交量分析模块增强
- [ ] 失败模式检测优化
- [ ] Agent协调器性能优化

### 长期 (本季度)

- [ ] DEX数据集成 (等待API)
- [ ] 智能钱包追踪 (等待API)
- [ ] 自动化交易执行
- [ ] FinGPT 可选集成

---

## 开发日志

### 2026-04-16 - 饕餮整合 Phase 3 & 4

**工作内容**:
1. 评估了 4 个外部 Skills
2. 整合了 sm-analyze 的三层框架
3. 整合了 entry-signals 的信号库
4. 吸收了 technical-analysis 的大师理念
5. 创建了 7 个新模块

**代码变更**:
- 新增文件: 13个
- 代码行数: +6700行
- CLI命令: +5个

**测试结果**:
- A股分析: ✅ 57分中性
- 美股信号: ✅ 77分买入
- 风险管理: ✅ 正常
- 成交量验证: ✅ 正常
- 上下文过滤: ✅ 正常

**Commit**: f994dac

---

### 2026-04-15 - Phase 1 & 2

**工作内容**:
1. 建立核心数据获取能力
2. 实现技术分析模块
3. 扩展到多市场和多资产
4. 集成加密货币和贵金属

**代码变更**:
- 新增文件: 20+
- 代码行数: ~8000行

---

## 技术债务

### 待优化

- [ ] 部分 A股数据获取失败时缺少优雅降级
- [ ] 成交量验证模块需要更多测试案例
- [ ] Agent协调器路由逻辑可以更智能
- [ ] 缺少完整的单元测试覆盖

### 待文档化

- [ ] API文档生成
- [ ] 架构图绘制
- [ ] 最佳实践指南
- [ ] 故障排查手册

---

## 资源链接

### 项目资源

- **GitHub**: https://github.com/beautifulboy9527/unified-finance-skill
- **本地路径**: `C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\`

### 整合来源

- **sm-analyze**: https://skills.yangsir.net/skill/sm-analyze
- **entry-signals**: https://skills.yangsir.net/skill/sm-entry-signals
- **technical-analysis**: https://skills.yangsir.net/skill/ssh2-technical-analysis
- **gmgn-market**: https://skills.yangsir.net/skill/daily-gmgn-market
- **regulation-monitor**: https://clawhub.ai/gentleming/regulation-monitor
- **stock-board**: https://clawhub.ai/mrblarkerx/stock-board
- **stock-recommend**: https://clawhub.ai/violin/stock-recommend
- **stock-screener-cn**: https://clawhub.ai/otouman/stock-screener-cn

### 参考文档

- [饕餮整合方案](file:///C:/Users/Administrator/.openclaw/workspace/.agents/skills/unified-finance-skill/TAOTIE-INTEGRATION-PLAN.md)
- [饕餮整合报告](file:///C:/Users/Administrator/.openclaw/workspace/.agents/skills/unified-finance-skill/TAOTIE-COMPLETION-REPORT.md)
- [技术分析评估](file:///C:/Users/Administrator/.openclaw/workspace/.agents/skills/unified-finance-skill/TECHNICAL-ANALYSIS-EVALUATION.md)

---

## 贡献指南

### 开发规范

1. **代码风格**: 遵循 PEP 8
2. **文档**: 每个模块必须有 docstring
3. **测试**: 新功能必须添加测试
4. **提交**: 使用语义化提交信息

### 添加新模块

```bash
# 1. 创建模块文件
touch scripts/features/new_feature.py

# 2. 实现功能
# 3. 添加CLI命令到 finance.py
# 4. 更新文档
# 5. 提交代码
git add -A
git commit -m "feat: 新功能描述"
git push
```

---

## 常见问题

### Q: 如何添加新的数据源?

**A**: 在 `core/` 目录下创建新的数据获取模块，参考 `quote.py` 的实现。

### Q: 如何添加新的分析指标?

**A**: 在 `features/` 目录下创建新的分析模块，参考 `technical.py` 的实现。

### Q: 如何添加新的信号模式?

**A**: 在 `features/entry_signals.py` 中添加新的信号检测函数，并更新信号库。

### Q: 如何切换数据源?

**A**: 大部分模块支持 `source` 参数，可以指定数据源。

---

## 更新历史

| 日期 | 版本 | 主要更新 |
|------|------|---------|
| 2026-04-16 | v3.1 | Phase 5-8: 监控监控 + 打板筛选 + 地区化分析 + 股票筛选器 |
| 2026-04-16 | v3.0 | Phase 3-4: 三层框架 + 信号库 + 理念提升 |
| 2026-04-15 | v2.0 | 多市场扩展: 加密货币 + 贵金属 |
| 2026-04-14 | v1.0 | 基础版本: A股/港股/美股核心功能 |

---

## 联系方式

- **开发者**: Neo
- **项目**: Unified Finance Skill
- **创建时间**: 2026-04-14

---

*最后更新: 2026-04-16 06:05 GMT+1*
