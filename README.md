# Neo9527 Unified Finance Skill

> 📊 可组合的金融AI能力平台 | v6.3 | by Neo9527

[![GitHub](https://img.shields.io/badge/GitHub-Neo9527--unified--finance--skill-blue)](https://github.com/beautifulboy9527/Neo9527-unified-finance-skill)
[![Version](https://img.shields.io/badge/version-v6.3-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()
[![PyPI](https://img.shields.io/pypi/v/neo9527-finance-skill?color=green)](https://pypi.org/project/neo9527-finance-skill/)

---

## 🎯 项目简介

**Neo9527 Unified Finance Skill v6.3** 是一个可组合的金融AI能力平台，采用Skills生态架构，支持加密货币、股票、外汇多市场分析，提供REST API服务，可被Agent直接调用。

### v6.3 核心特性

- 📊 **结构化报告**: 8部分逻辑递进框架，每章节独立小结
- 🔍 **数据来源标注**: 情绪/监管/财务完整信源说明
- 🧩 **Skills生态**: 6个独立Skills，可组合编排
- 🤖 **Agent调用**: 标准接口 + OpenAI Function Calling
- 🌐 **REST API**: FastAPI服务 + 自动文档
- 📈 **多市场支持**: 加密货币 + 股票 + 外汇
- 🎯 **交易周期**: 日内/短线/波段/中线/长线完整支持
- 🏦 **打板筛选**: 涨停板/强势股/连板统计

### v6.3 升级亮点

| 功能 | v6.2 | v6.3 |
|------|------|------|
| 报告结构 | ⚠️ 混乱 | ✅ 逻辑递进 |
| 数据来源 | ⚠️ 缺失 | ✅ 完整标注 |
| 新闻分析 | ⚠️ 无关 | ✅ 移至选股 |
| 情绪来源 | ❌ 无 | ✅ TextBlob/Adanos |
| 监管来源 | ❌ 无 | ✅ CSRC/PBOC/NFRA |
| 深度研报 | ⚠️ 不明确 | ✅ Phase验证 |

---

## 🚀 快速开始

### 方式1: PyPI安装 (推荐)

```bash
pip install neo9527-finance-skill

# 使用
neo-finance analyze AAPL
```

### 方式2: 源码安装

```bash
# 克隆仓库
git clone https://github.com/beautifulboy9527/Neo9527-unified-finance-skill.git
cd Neo9527-unified-finance-skill

# 安装依赖
pip install -r requirements.txt

# 使用
python finance.py analyze AAPL
```

---

## 💻 CLI命令

### 1. 综合分析

```bash
python finance.py analyze AAPL

# 输出:
# 第一部分: 基本面分析 (ROE/PE/PB)
# 第二部分: 估值分析 (DCF模型)
# 第三部分: 财务健康 (异常检测)
# 第四部分: 技术分析 (RSI/MACD/形态)
# 第五部分: 市场情绪 (数据来源标注)
# 第六部分: 监管风险 (CSRC/PBOC/NFRA)
# 第七部分: 深度研报 (Phase 4/5/7)
# 第八部分: 全局观点 (综合建议)
```

### 2. 打板筛选 (短线)

```bash
python finance.py board --type limit-up      # 涨停板
python finance.py board --type strong        # 强势股
python finance.py board --type continuous    # 连板统计
python finance.py board --type market        # 市场情绪
```

### 3. 财务异常检测

```bash
python finance.py check AAPL

# 输出:
# 风险等级: low
# 异常数量: 0
# 毛利率: 46.9%
# 净利率: 26.9%
# 数据来源: 财务报表（利润表/资产负债表）
```

### 4. 估值计算

```bash
python finance.py value AAPL

# 输出:
# 当前价格: $270.23
# 公允价值: $75.81
# 估值状态: 高估 71.9%
```

### 5. 深度研报

```bash
python finance.py research AAPL

# 输出:
# Phase 4... (财务数据获取)
# Phase 5... (分析计算)
# Phase 7... (评分生成)
# 评级: 🟡🟡🟡
# 建议: 基本面尚可，需进一步分析
```

---

## 📊 报告结构 (v6.3)

```
第一部分：基本面分析（投资根基）
├── 1.1 盈利能力 (ROE评级 ⭐⭐⭐⭐⭐)
├── 1.2 估值水平 (PE/PB行业对比)
└── 1.3 基本面小结

第二部分：估值分析（价格评估）
├── 2.1 估值模型 (DCF)
└── 2.2 估值信号

第三部分：财务健康（风险检查）
├── 3.1 异常检测 (信源标注)
├── 3.2 盈利质量
└── 3.3 财务小结

第四部分：技术分析（择时参考）
├── 4.1 趋势判断
├── 4.2 技术指标 (RSI仅一次)
├── 4.3 技术形态
└── 4.4 技术小结

第五部分：市场情绪（短期风向）
├── 5.1 情绪指标
├── 5.2 数据来源 (本地TextBlob/Adanos API)
└── 5.3 情绪小结

第六部分：监管风险（政策环境）
├── 6.1 风险评估
├── 6.2 数据来源 (CSRC/PBOC/NFRA)
├── 6.3 监控方法
└── 6.4 监管小结

第七部分：深度研报（综合研判）
├── 7.1 研报评级 (Phase验证)
└── 7.2 研报小结

第八部分：全局观点（最终建议）
├── 8.1 综合评价
├── 8.2 各维度评分 (权重)
└── 8.3 投资建议 (短/波/长)
```

---

## 🔧 核心模块

```
skills/
├── stock-skill/
│   ├── comprehensive_analyzer.py  # 综合分析器 ✨
│   ├── financial_check.py         # 财务异常检测 ✨
│   ├── regulation_monitor.py      # 监管风险监控 ✨
│   └── analyzer.py                # 快速分析
├── shared/
│   ├── report_enhancer.py         # 报告增强工具 ✨
│   ├── report_structure.py        # 报告结构优化器 ✨
│   └── finance_toolkit.py         # 金融工具包
└── crypto-skill/
    └── complete_crypto_analyzer.py

scripts/features/
├── board_scanner.py               # 打板筛选器 ✨
├── sentiment_enhanced.py          # 情绪分析 ✨
├── news.py                        # 新闻聚合 (选股用)
├── valuation.py                   # 估值计算
└── deep_research.py               # 深度研报
```

---

## 📈 数据来源

| 数据类型 | 来源 | 说明 | 状态 |
|---------|------|------|------|
| 市场数据 | yfinance | 免费 | ✅ |
| 技术指标 | yfinance | 免费 | ✅ |
| 财务数据 | yfinance | 利润表/资产负债表 | ✅ |
| 情绪分析 | TextBlob | 本地模型 | ✅ |
| 情绪分析 | Adanos API | 多数据源 | ⚠️ 需API Key |
| 监管数据 | CSRC/PBOC/NFRA | 官方公告 | ✅ |
| 打板数据 | 东方财富 | 实时行情 | ✅ |

---

## 🎨 特色功能

### 1. 数据来源完整标注

**市场情绪**:
```
数据来源: 本地TextBlob分析
判断方法: 通过新闻标题关键词分析，使用TextBlob库计算情感极性
```

**监管风险**:
```
数据来源: 中国证监会(CSRC)、人民银行(PBOC)、国家金融监督管理总局(NFRA)公开公告
监控方法: 实时监控三大监管机构官方网站公告、政策文件、处罚决定
评级说明: 近期无重大监管政策变化或处罚公告
```

### 2. 交易周期支持

| 周期 | 时间框架 | 模块 | CLI命令 |
|------|---------|------|---------|
| 日内 | 分钟级 | board_scanner | `board --type limit-up` |
| 短线 | 小时级 | signal_tracker | 待集成 |
| 波段 | 日级 | backtest_engine | 待集成 |
| 中线 | 周级 | comprehensive_analyzer | `analyze AAPL` |
| 长线 | 月级 | deep-research | `research AAPL` |

### 3. 报告增强工具

- **数字格式化**: `34.249683` → `34.2`, `3971820552192` → `$3.97万亿`
- **RSI解读**: 超买/超卖/中性 + 建议
- **PE解读**: 高估/合理/低估 + 行业对比
- **ROE评级**: ⭐⭐⭐⭐⭐ 评分系统
- **技术形态**: MACD金叉/死叉/RSI超买超卖

### 4. 深度研报验证

```
开始分析 AAPL (风格: value, 深度: quick)
  Phase 4... (财务数据获取)
    财务报表状态: fin=True, bs=True, cf=True
    数据获取: NI=112.0B, Equity=73.7B, OCF=111.5B
  Phase 5... (分析计算)
  Phase 7... (评分生成)
   ✅ 评级: 🟡🟡🟡
   ✅ 建议: 基本面尚可，需进一步分析
```

---

## 📝 更新日志

### v6.3 (2026-04-18)

- 📊 **报告结构优化**
  - 8部分逻辑递进框架
  - 每章节独立小结
  - 全局观点综合建议
- 🔍 **数据来源标注**
  - 情绪: TextBlob/Adanos + 判断方法
  - 监管: CSRC/PBOC/NFRA + 监控方法
  - 财务: 利润表/资产负债表
- ✨ **新增模块**
  - report_enhancer.py (8,627字节)
  - report_structure.py (12,612字节)
  - board_scanner.py (18,441字节)
  - regulation_monitor.py (5,444字节)
- 🔧 **功能改进**
  - 新闻分析移至选股使用
  - 财务异常检测支持美股
  - 估值评分逻辑修复
  - RSI仅分析一次
- 📈 **交易周期支持**
  - 日内/短线/波段/中线/长线
  - TRADING_CYCLES.md 文档

### v6.2 (2026-04-18)

- 📊 报告展示优化
- 🔧 估值逻辑修复
- 📈 打板模块恢复

### v6.1 (2026-04-18)

- 📊 报告全面优化
- 🔍 数据来源标注
- 💡 不同周期建议

### v6.0 (2026-04-17)

- 🧩 Skills生态架构
- 🤖 REST API服务
- 📈 多市场支持

### v4.4 (2026-04-17)

- 🐋 OnchainWhaleSkill真实数据
- 🔍 数据质量保证
- 📦 PyPI发布规范

---

## 🛠️ 开发指南

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/beautifulboy9527/Neo9527-unified-finance-skill.git
cd Neo9527-unified-finance-skill

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
# 综合分析测试
python skills/stock-skill/comprehensive_analyzer.py AAPL

# 打板筛选测试
python scripts/features/board_scanner.py --type limit-up
```

---

## 📄 License

MIT License

---

## 👤 Author

**Neo9527**

- GitHub: [@beautifulboy9527](https://github.com/beautifulboy9527)
- Email: beautifulboy9527@gmail.com

---

## 🙏 Acknowledgments

感谢以下开源项目:

- [yfinance](https://github.com/ranaroussi/yfinance)
- [pandas](https://pandas.pydata.org/)
- [TextBlob](https://textblob.readthedocs.io/)
- [DeFiLlama](https://defillama.com/)
- [CoinGecko API](https://www.coingecko.com/en/api)

---

## 🗺️ 路线图

- [ ] v6.4: PB行业对比数据
- [ ] v6.5: 结构化报告完全应用
- [ ] v7.0: ML增强预测
- [ ] v8.0: 移动端适配

---

**Star ⭐ 本项目以获取最新更新！**
