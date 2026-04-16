# Neo9527 Unified Finance Skill

> 📊 多市场金融分析技能库 | v3.2 | by Neo9527

[![GitHub](https://img.shields.io/badge/GitHub-Neo9527--unified--finance--skill-blue)](https://github.com/beautifulboy9527/Neo9527-unified-finance-skill)
[![Version](https://img.shields.io/badge/version-v3.2-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()

---

## 🎯 项目简介

**Neo9527 Unified Finance Skill v3.2** 是一个生产级 AI 金融 Agent 技能集，整合了插件系统、信号验证、组合优化等核心能力，提供从个股分析到组合管理的完整解决方案。

### v3.2 核心升级

- 🔌 **插件系统**: 动态注册、优先级调度、7个内置插件
- 📊 **FinanceToolkit**: 150+财务比率、DuPont分析、Altman Z-Score、DCF估值
- ✅ **回测验证**: Walk-Forward + Monte Carlo + 信号评级(A/B/C/D)
- 💼 **组合优化**: Markowitz优化、风险平价、Kelly仓位、VaR/CVaR
- 🎯 **长中短线**: 分层分析框架，不同周期不同逻辑

### 核心特点

- 🌍 **多市场支持**: A股、港股、美股、加密货币、贵金属
- 🔌 **插件化架构**: 可扩展、易维护、动态加载
- ✅ **信号验证**: 30个信号 + 回测验证 + 样本外评估
- 💼 **组合优化**: Markowitz、风险平价、Kelly仓位
- 🎯 **投资框架**: 长中短线分层分析
- 🤖 **Agent友好**: 清晰API、轻量模块、易于集成

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/beautifulboy9527/Neo9527-unified-finance-skill.git

# 安装依赖
pip install -r requirements.txt
```

### 基础使用

```bash
# 综合评分 (推荐)
python finance.py score AAPL
# → 88分 | 强势 | 建议买入

# 完整分析报告
python finance.py report-full 600519
# → Markdown格式完整报告

# 风险管理
python finance.py risk AAPL --capital 100000
# → 止损价 | 目标价 | 建议仓位

# 入场信号
python finance.py signals AAPL
# → 检测到的信号 + 成功率
```

### 高级功能

```bash
# 股票筛选
python finance.py screen --strategy ma_bull --market a

# 多策略组合
python finance.py screen --strategies ma_bull macd_golden --mode and

# 打板机会
python finance.py board --opportunities

# 监管监控
python finance.py regulation --days 7

# 地区化新闻分析
python finance.py regional-news --type regional
```

---

## 📊 能力矩阵

### 市场覆盖

| 市场 | 行情 | 分析 | 信号 | 评分 | 风险 | 监管 | 打板 | 筛选 |
|------|------|------|------|------|------|------|------|------|
| **A股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **港股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **美股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| **加密货币** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **贵金属** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |

### 核心模块

| 模块 | 功能 | 文件 | 行数 |
|------|------|------|------|
| **插件系统** | 动态注册 + 调度 | `plugin_system.py` | 485 |
| **FinanceToolkit** | 150+比率 + DCF | `finance_toolkit.py` | 520 |
| **回测引擎** | 信号验证 + 评级 | `backtest_engine.py` | 563 |
| **组合管理** | Markowitz + Kelly | `portfolio_manager.py` | 488 |
| **投资框架** | 长中短线分析 | `investment_framework.py` | 560 |
| **可视化报告** | HTML/PDF + 图表 | `report_generator.py` | 597 |
| **信号库** | 30个验证信号 | `entry_signals.py` | - |
| **风险管理** | ATR止损 + 仓位 | `risk_management.py` | - |

---

## 📁 目录结构

```
Neo9527-unified-finance-skill/
├── SKILL.md              # Skill 定义
├── README.md             # 项目说明
├── requirements.txt      # 依赖列表
│
├── scripts/              # 源代码
│   ├── finance.py       # 主入口 (60+ 命令)
│   ├── core/            # 核心模块
│   │   ├── quote.py    # 行情获取
│   │   ├── news.py     # 新闻数据
│   │   └── technical.py # 技术分析
│   ├── features/        # 功能模块 (15+)
│   │   ├── analysis_framework.py
│   │   ├── entry_signals.py
│   │   ├── stock_screener.py
│   │   └── ...
│   └── agent/           # Agent 模块
│       └── orchestrator.py
│
├── docs/                 # 文档
│   ├── ARCHITECTURE.md  # 架构文档
│   ├── CLI-Reference.md # CLI 参考
│   └── guides/          # 使用指南
│
├── planning/             # 规划文档
│   ├── evaluations/     # Skills 评估
│   └── integration-plans/ # 整合计划
│
├── tests/                # 测试
├── config/               # 配置
└── references/           # 参考资料
```

---

## 🔧 整合来源

本项目整合了多个高价值 Skills 的核心能力：

| 来源 | 整合内容 | 整合方式 |
|------|---------|---------|
| [sm-analyze](https://skills.yangsir.net/skill/sm-analyze) | 三层分析框架 | 代码重写 |
| [entry-signals](https://skills.yangsir.net/skill/sm-entry-signals) | 信号库 | 理念吸收 |
| [technical-analysis](https://skills.yangsir.net/skill/ssh2-technical-analysis) | 成交量验证 | 理念吸收 |
| [regulation-monitor](https://clawhub.ai/gentleming/regulation-monitor) | 监管监控 | 代码重写 |
| [stock-board](https://clawhub.ai/mrblarkerx/stock-board) | 打板筛选 | Python重写 |
| [stock-recommend](https://clawhub.ai/violin/stock-recommend) | 地区化分析 | 思路借鉴 |
| [stock-screener-cn](https://clawhub.ai/otouman/stock-screener-cn) | 股票筛选器 | 代码重写 |

---

## 📈 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|---------|
| **v3.1** | 2026-04-16 | Phase 5-8: 监管监控 + 打板筛选 + 地区化分析 + 选股器 |
| **v3.0** | 2026-04-16 | Phase 3-4: 三层框架 + 信号库 + 风险管理 |
| **v2.0** | 2026-04-15 | 多市场扩展: 加密货币 + 贵金属 |
| **v1.0** | 2026-04-14 | 基础版本: A股/港股/美股核心功能 |

详见 [CHANGELOG.md](CHANGELOG.md)

---

## 📊 统计数据

| 指标 | 数量 |
|------|------|
| **代码行数** | 20,000+ |
| **功能模块** | 15+ |
| **CLI命令** | 60+ |
| **筛选策略** | 11种 |
| **验证信号** | 30个 |
| **支持市场** | 5个 |

---

## 📖 文档

- [架构文档](docs/ARCHITECTURE.md)
- [CLI 参考](docs/Unified-Finance-Skill-快速参考.md)
- [开发历程](docs/Unified-Finance-Skill-开发历程.md)
- [Agent 架构](docs/AGENT-ARCHITECTURE.md)

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

[MIT License](LICENSE)

---

## 👤 作者

**Neo9527** (一辉)

- GitHub: [@beautifulboy9527](https://github.com/beautifulboy9527)
- 项目: [Neo9527-unified-finance-skill](https://github.com/beautifulboy9527/Neo9527-unified-finance-skill)

---

## 🙏 致谢

感谢以下项目和社区的支持：

- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 框架
- [AkShare](https://github.com/akfamily/akshare) - 金融数据接口
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- [FinanceToolkit](https://github.com/JerBouma/FinanceToolkit) - 财务分析工具
- [ClawHub](https://clawhub.ai) - Skills 市场

---

## 📖 v3.2 完整使用示例

### 1. 个股分析 (长中短线)

```python
from features.investment_framework import analyze_investment

# 长线分析 (基本面优先)
result = analyze_investment('002241', 'long')
print(f"决策: {result['decision']['action']}")
print(f"置信度: {result['decision']['confidence']}/100")

# 中线分析 (趋势优先)
result = analyze_investment('002241', 'medium')

# 短线分析 (信号优先)
result = analyze_investment('002241', 'short')
```

### 2. 信号回测验证

```python
from features.backtest_engine import validate_signal_performance
from features.backtest_engine import sma_cross_signal

# 验证 SMA 交叉信号
validation = validate_signal_performance('002241', sma_cross_signal, "SMA交叉")

print(f"评分: {validation['validation_score']}/100")
print(f"评级: {validation['grade']}")
print(f"胜率: {validation['backtest']['win_rate']*100:.1f}%")
print(f"夏普: {validation['backtest']['sharpe_ratio']:.2f}")
```

### 3. 组合优化

```python
from features.portfolio_manager import analyze_portfolio

# 分析组合
symbols = ['002241', '600519', '000858']
report = analyze_portfolio(symbols)

print(f"组合评分: {report['portfolio']['score']}/100")
print(f"最优权重: {report['optimal_weights']['weight_allocation']}")
print(f"VaR(95%): {report['risk_metrics']['var_95']*100:.2f}%")
```

### 4. 基本面深度分析

```python
from features.finance_toolkit import analyze_fundamentals_deep

# 深度基本面分析
fundamentals = analyze_fundamentals_deep('002241')

print(f"评分: {fundamentals['score']}/100")
print(f"ROE: {fundamentals['profitability']['roe']}")
print(f"DuPont: {fundamentals['dupont']}")
print(f"Z-Score: {fundamentals['zscore']}")
```

### 5. 可视化报告生成

```python
from features.report_generator import generate_report

# HTML 报告 (推荐)
html_path = generate_report('002241', 'medium', 'html')
print(f"报告已生成: {html_path}")

# PDF 报告
pdf_path = generate_report('002241', 'medium', 'pdf')

# Markdown 报告
md_path = generate_report('002241', 'medium', 'markdown')
```

**输出示例**:
- HTML: `D:\OpenClaw\outputs\reports\002241_report.html`
- PDF: `D:\OpenClaw\outputs\reports\002241_report.pdf`
- Markdown: `D:\OpenClaw\outputs\reports\002241_report.md`

---

## 🏗️ 架构图

```
Unified Finance Skill v3.2
│
├─ 投资框架 (investment_framework.py)
│  └─ 长中短线分层分析
│
├─ 插件系统 (plugin_system.py)
│  ├─ PluginRegistry (动态注册)
│  ├─ PluginOrchestrator (执行编排)
│  └─ 7个内置插件
│
├─ FinanceToolkit (finance_toolkit.py)
│  ├─ 150+ 财务比率
│  ├─ DuPont分析
│  ├─ Altman Z-Score
│  └─ DCF估值
│
├─ 回测引擎 (backtest_engine.py)
│  ├─ 信号回测
│  ├─ Walk-Forward
│  ├─ Monte Carlo
│  └─ 信号验证 (A/B/C/D评级)
│
└─ 组合管理 (portfolio_manager.py)
   ├─ 组合风险 (VaR/CVaR)
   ├─ Markowitz优化
   ├─ 风险平价
   └─ Kelly仓位
```

---

## 🎯 Phase 3 成果

| Phase | 内容 | 文件 | 行数 | 提交 |
|-------|------|------|------|------|
| Phase 0 | Darwin优化 + 投资框架 | investment_framework.py | 560 | 10746b8 |
| Phase 1 | 插件系统重构 | plugin_system.py | 485 | 8fc6854 |
| Phase 2 | FinanceToolkit集成 | finance_toolkit.py | 520 | 8fc6854 |
| Phase 2 | 回测验证引擎 | backtest_engine.py | 563 | 83b3f74 |
| Phase 3 | 组合优化 | portfolio_manager.py | 488 | d474f84 |

**总新增代码**: 3,213 行 (6个核心模块)

---

## 📊 Phase 4: 可视化报告系统

### 新增能力对比

| 维度 | Phase 3 | Phase 4 | 改进 |
|------|---------|---------|------|
| 报告格式 | ❌ 仅 Markdown | ✅ Markdown/HTML/PDF | 3种格式 |
| 可视化 | ❌ 无 | ✅ 4种图表 | 雷达/K线/热力/Monte Carlo |
| 排版质量 | ⚠️ 纯文本 | ✅ 专业CSS | 美观度大幅提升 |
| 图表嵌入 | ❌ 无 | ✅ Base64嵌入 | 无需外部文件 |

### 支持的图表类型

1. **雷达图** - 综合评分可视化
2. **K线图** - 价格走势 + 成交量
3. **相关性热力图** - 组合相关性矩阵
4. **Monte Carlo 分布图** - 价格模拟路径 + 终值分布

### 报告格式

#### HTML 格式 (推荐)
```python
from features.report_generator import generate_report

html_path = generate_report('002241', 'medium', 'html')
# → D:\OpenClaw\outputs\reports\002241_report.html
```

**特点**:
- ✅ 专业 CSS 样式
- ✅ 嵌入 Base64 图表
- ✅ 响应式布局
- ✅ 无需外部依赖

#### Markdown 格式
```python
md_path = generate_report('002241', 'medium', 'markdown')
```

**特点**:
- ✅ 纯文本
- ✅ 版本控制友好
- ⚠️ 无图表

#### PDF 格式
```python
pdf_path = generate_report('002241', 'medium', 'pdf')
# 需要先安装: pip install weasyprint
```

**特点**:
- ✅ 适合打印
- ✅ 正式文档
- ⚠️ 需要安装 weasyprint (Windows/Mac/Linux 系统依赖不同)

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！⭐**
