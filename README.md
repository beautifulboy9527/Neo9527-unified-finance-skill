# Neo9527 Unified Finance Skill

> 📊 多维度金融分析技能库 | v4.0 | by Neo9527

[![GitHub](https://img.shields.io/badge/GitHub-Neo9527--unified--finance--skill-blue)](https://github.com/beautifulboy9527/Neo9527-unified-finance-skill)
[![Version](https://img.shields.io/badge/version-v4.0-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()

---

## 🎯 项目简介

**Neo9527 Unified Finance Skill v4.0** 是一个生产级金融分析系统，整合了多维度数据分析、形态识别、信号叠加等专业能力，提供从市场数据到投资决策的完整解决方案。

### v4.0 核心升级

- 🎨 **HTML报告重构**: 专业卡片式布局 + 响应式设计
- 📊 **叠buff逻辑**: 多因子信号叠加 + 综合评分系统
- 🔍 **形态识别**: 头肩顶/底、双顶/底、趋势判断
- 📝 **专业解读**: 技术面文字分析 + 结论详细说明
- 🔗 **链上数据**: 算力/难度/流通量 (BTC专用)
- ⚡ **完整闭环**: 数据 → 分析 → 信号 → 结论

### 核心特点

- 🌍 **多市场支持**: A股、港股、美股、加密货币、贵金属
- 📊 **多维度分析**: 市场数据 + 技术指标 + 链上数据 + 合约数据
- 🎯 **形态识别**: 经典技术形态自动检测
- 📈 **叠buff系统**: 看涨看跌信号可视化汇总
- 💡 **专业解读**: 每个环节都有文字分析
- 🎨 **现代报告**: 专业HTML模板 + 响应式设计

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/beautifulboy9527/Neo9527-unified-finance-skill.git

# 安装依赖
pip install yfinance pandas requests matplotlib mplfinance
```

### 基础使用

```python
# 加密货币分析 (推荐)
python scripts/features/report_generator_v4.py
# → BTC-USD_report_v4.html (完整专业报告)

# 股票分析
python scripts/finance.py score AAPL
# → 88分 | 强势 | 建议买入
```

---

## 📊 能力矩阵

### 报告结构 (v4.0)

```
一、综合评分 (70/100)
二、市场数据 (实时价格/涨跌/成交量)
三、技术分析
    3.1 核心指标 (RSI/MACD/ADX/布林带)
    3.2 支撑阻力 (阻力位/支撑位)
    3.3 形态识别 (趋势/双顶双底/头肩)
    3.4 技术面专业解读 ← 新增
四、链上数据 (算力/难度/流通量)
五、信号汇总 (多因子共振)
    - 看涨信号卡片 (绿色)
    - 看跌信号卡片 (红色)
六、最终结论与操作建议
    - 综合分析 ← 新增
    - 核心支撑因素 ← 新增
    - 风险提示 ← 新增
    - 入场策略
    - 止损位/目标位
七、风险提示
```

### 形态识别

| 形态 | 识别方法 | 信号强度 |
|------|---------|---------|
| 趋势判断 | MA排列 | ±5分 |
| 头肩顶 | 三峰检测 | -5分 |
| 双顶双底 | 两峰/谷相近 | ±4分 |
| RSI超买超卖 | >70/<30 | -2/+3分 |
| MACD金叉死叉 | 柱状图 | +3/-3分 |
| 布林带突破 | 价格位置 | ±2分 |

### 叠buff逻辑

```python
# 示例: BTC-USD
信号汇总:
  [技术形态] 趋势: 强烈看涨 (strength=+5)
  [动量指标] RSI: 超买回调 (strength=-2)
  [趋势指标] MACD: 金叉看涨 (strength=+3)
  [波动指标] 布林带: 突破上轨 (strength=+2)
  [经典形态] 双底: 看涨 (strength=+4)

总强度: +12
综合评分: 50 + (12/max)*50 = 70/100
决策: BUY
置信度: 83%
```

---

## 📁 项目结构

```
unified-finance-skill/
├── scripts/
│   ├── features/              # 功能模块
│   │   ├── complete_crypto_analyzer.py  # 完整分析器 ✨
│   │   ├── report_generator_v4.py       # 报告生成器 v4 ✨
│   │   ├── investment_framework.py      # 投资框架
│   │   ├── finance_toolkit.py           # 金融工具包
│   │   ├── backtest_engine.py           # 回测引擎
│   │   ├── futures_data.py              # 合约数据
│   │   └── templates/
│   │       └── crypto_report_v4.html    # HTML模板 ✨
│   ├── core/                   # 核心模块
│   │   ├── technical.py         # 技术分析
│   │   └── quote.py             # 行情数据
│   ├── agent/                  # Agent模块
│   │   └── smart_orchestrator.py
│   └── finance.py              # 主入口
├── config/                     # 配置文件
├── docs/                       # 文档
│   ├── ARCHITECTURE.md         # 架构文档
│   └── STATUS-REPORT.md        # 状态报告
├── README.md                   # 说明文档
└── SKILL.md                    # Skill 定义
```

---

## 🎨 HTML报告特点

### 视觉设计

- ✅ 响应式布局 (手机/平板/桌面)
- ✅ 卡片式信号展示
- ✅ 渐变色视觉效果
- ✅ 看涨看跌颜色区分 (绿/红)
- ✅ 专业排版层次清晰

### 内容特点

- ✅ 多维度数据分析
- ✅ 形态识别可视化
- ✅ 叠buff信号汇总
- ✅ 专业文字解读
- ✅ 操作建议明确

---

## 📈 数据来源

| 数据类型 | 来源 | API |
|---------|------|-----|
| 市场数据 | CoinGecko | 免费 |
| 技术指标 | yfinance | 免费 |
| 链上数据 | Blockchain.com | 免费 |
| 情绪指数 | alternative.me | 免费 |
| 合约数据 | CCXT (可选) | 免费 |

---

## 🔧 技术栈

- **Python 3.8+**
- **yfinance** - 金融数据
- **pandas** - 数据处理
- **matplotlib** - 图表绘制
- **requests** - API调用

---

## 📝 更新日志

### v4.0 (2026-04-16)

- ✨ HTML报告重构 (卡片式 + 响应式)
- ✨ 叠buff信号系统
- ✨ 形态识别 (头肩/双顶双底)
- ✨ 技术面专业解读
- ✨ 结论详细分析
- ✨ 链上数据集成
- 🗑️ 清理冗余文件

### v3.2 (2026-04-15)

- 🔌 插件系统重构
- 📊 FinanceToolkit集成
- ✅ 回测验证引擎
- 💼 组合优化器
- 🎯 缓存加速

---

## 📄 License

MIT License

---

## 👤 Author

**Neo9527**

- GitHub: [@beautifulboy9527](https://github.com/beautifulboy9527)

---

## 🙏 Acknowledgments

感谢以下开源项目:

- [yfinance](https://github.com/ranaroussi/yfinance)
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [CoinGecko API](https://www.coingecko.com/en/api)
