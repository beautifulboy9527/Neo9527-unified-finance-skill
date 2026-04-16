# Unified Finance Skill

> 📊 多市场金融分析技能库 | v3.1

## 🎯 核心能力

- 🌍 **多市场支持**: A股、港股、美股、加密货币、贵金属
- 📊 **三层分析框架**: 宏观 → 行业 → 个股 系统化分析
- 🎯 **信号验证**: 30个历史验证信号，最高88%成功率
- ⚙️ **风险管理**: ATR止损 + 仓位计算 + 目标价
- 🤖 **Agent协调**: 智能路由 + 多Agent协作
- 🔍 **选股器**: 11种筛选策略 + 多策略组合

## 🚀 快速开始

```bash
# 综合评分
python finance.py score AAPL

# 完整分析报告
python finance.py report-full 600519

# 风险管理
python finance.py risk AAPL --capital 100000

# 股票筛选
python finance.py screen --strategy ma_bull --market a

# 打板机会
python finance.py board --opportunities
```

## 📁 目录结构

```
unified-finance-skill/
├── SKILL.md              # Skill 定义
├── scripts/              # 源代码
│   ├── core/            # 核心模块
│   ├── features/        # 功能模块
│   └── agent/           # Agent 模块
├── docs/                 # 文档
├── planning/             # 规划文档
├── tests/                # 测试
└── config/               # 配置
```

## 📖 文档

- [架构文档](docs/ARCHITECTURE.md)
- [CLI 参考](docs/Unified-Finance-Skill-快速参考.md)
- [开发历程](docs/Unified-Finance-Skill-开发历程.md)

## 📊 能力矩阵

| 市场 | 行情 | 分析 | 信号 | 评分 | 风险 | 监管 | 打板 | 筛选 |
|------|------|------|------|------|------|------|------|------|
| **A股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **港股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **美股** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | - | ✅ |
| **加密货币** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |
| **贵金属** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - | - |

## 🔧 整合来源

- [sm-analyze](https://skills.yangsir.net/skill/sm-analyze) - 三层分析框架
- [entry-signals](https://skills.yangsir.net/skill/sm-entry-signals) - 信号库
- [regulation-monitor](https://clawhub.ai/gentleming/regulation-monitor) - 监管监控
- [stock-board](https://clawhub.ai/mrblarkerx/stock-board) - 打板筛选
- [stock-screener-cn](https://clawhub.ai/otouman/stock-screener-cn) - 股票筛选器

## 📈 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|---------|
| v3.1 | 2026-04-16 | Phase 5-8: 监管监控 + 打板筛选 + 选股器 |
| v3.0 | 2026-04-16 | Phase 3-4: 三层框架 + 信号库 |
| v2.0 | 2026-04-15 | 多市场扩展: 加密货币 + 贵金属 |
| v1.0 | 2026-04-14 | 基础版本: A股/港股/美股 |

## 📄 许可证

MIT License

---

**GitHub**: https://github.com/beautifulboy9527/unified-finance-skill
