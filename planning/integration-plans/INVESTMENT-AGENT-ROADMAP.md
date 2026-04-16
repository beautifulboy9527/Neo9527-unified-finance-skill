# 金融 Skills 资源分析与整合建议

**分析时间**: 2026-04-15 21:20
**目标**: 打造多市场投资 Agent (A股/港股/美股/加密货币/贵金属)

---

## 📊 现有能力 vs 推荐资源对比

### 当前 unified-finance-skill 已有能力

| 类别 | 当前能力 | 数据源 |
|------|---------|--------|
| A股行情 | ✅ 已有 | agent-stock, akshare |
| 港股行情 | ✅ 已有 | yfinance |
| 美股行情 | ✅ 已有 | yfinance |
| 财务分析 | ✅ 已有 | akshare, yfinance |
| 技术分析 | ✅ 已有 | 本地计算 |
| 期权分析 | ✅ 已有 | Black-Scholes |
| 新闻聚合 | ✅ 已有 | NewsNow API |
| 情绪分析 | ✅ 已有 | 本地模型 |

### 推荐资源补充

| 类别 | 推荐资源 | GitHub URL | 整合价值 |
|------|---------|------------|---------|
| **A股/港股** | AkShare | https://github.com/akfamily/akshare | ⭐⭐⭐⭐⭐ 已整合 |
| **A股/港股** | TuShare Pro | https://github.com/waditu/tushare | ⭐⭐⭐⭐ 高质量数据 |
| **统一终端** | OpenBB | https://github.com/OpenBB-finance/OpenBBTerminal | ⭐⭐⭐⭐⭐ 架构参考 |
| **回测交易** | vn.py | https://github.com/vnpy/vnpy | ⭐⭐⭐⭐⭐ 实盘能力 |
| **加密货币** | ccxt | https://github.com/ccxt/ccxt | ⭐⭐⭐⭐⭐ 必备 |
| **贵金属** | Metals-API | https://metals-api.com | ⭐⭐⭐ 数据补充 |
| **金融LLM** | FinGPT | https://github.com/AI4Finance-Foundation/FinGPT | ⭐⭐⭐⭐⭐ 核心增强 |

---

## 🎯 整合优先级建议

### P0: 立即整合 (核心能力)

#### 1. ccxt - 加密货币交易
```python
# 已有数据源: 无
# 新增能力: 加密货币行情 + 交易
```

**整合方案**:
```python
# features/crypto.py
import ccxt

def get_crypto_quote(symbol: str, exchange: str = 'binance'):
    """获取加密货币行情"""
    exchange = getattr(ccxt, exchange)()
    ticker = exchange.fetch_ticker(symbol)
    return {
        'symbol': symbol,
        'price': ticker['last'],
        'volume': ticker['baseVolume'],
        'change_pct': ticker['percentage']
    }
```

#### 2. 贵金属价格
```python
# 已有数据源: 无
# 新增能力: 黄金/白银价格
```

**整合方案**:
```python
# features/metals.py
import requests

def get_metal_price(metal: str = 'XAU'):  # XAU=黄金, XAG=白银
    """获取贵金属价格"""
    # 使用免费 API
    url = f"https://api.metals.live/v1/spot/{metal}"
    response = requests.get(url)
    return response.json()
```

### P1: 近期整合 (增强能力)

#### 3. vn.py - 回测 + 实盘
**价值**: 从分析到交易的完整闭环

#### 4. OpenBB - 架构参考
**价值**: 学习专业终端的模块化设计

### P2: 长期整合 (LLM 增强)

#### 5. FinGPT - 金融大模型
**价值**: 提升分析和决策能力

---

## 🏗️ 投资Agent 架构建议

### 推荐架构: 四层设计

```
┌─────────────────────────────────────────────────┐
│              Layer 4: 执行层                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ 券商API │  │ 交易所API │  │ 风控模块 │          │
│  │ vn.py   │  │  ccxt    │  │         │          │
│  └─────────┘  └─────────┘  └─────────┘          │
└─────────────────────────────────────────────────┘
                       ↑
┌─────────────────────────────────────────────────┐
│              Layer 3: Agent 层                    │
│  ┌──────────────────────────────────────┐       │
│  │         FinGPT / LLM Core             │       │
│  │  - 意图理解  - 策略生成  - 风险评估    │       │
│  └──────────────────────────────────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 投研Agent │  │ 交易Agent │  │ 风控Agent │       │
│  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────┘
                       ↑
┌─────────────────────────────────────────────────┐
│              Layer 2: 工具层                      │
│  ┌──────────────────────────────────────┐       │
│  │       unified-finance-skill           │       │
│  │  - quote  - technical  - sentiment    │       │
│  │  - earnings  - news  - valuation      │       │
│  │  - options  - crypto  - metals        │       │
│  └──────────────────────────────────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 回测引擎 │  │ 订单管理 │  │ 持仓管理 │       │
│  │ backtest │  │ order    │  │ position │       │
│  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────┘
                       ↑
┌─────────────────────────────────────────────────┐
│              Layer 1: 数据层                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ AkShare  │  │ yfinance │  │  ccxt    │       │
│  │ (A股/港股)│  │ (美股)   │  │ (加密)   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ TuShare  │  │ MetalsAPI│  │ NewsAPI  │       │
│  │ (A股)    │  │ (贵金属) │  │ (新闻)   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────┘
```

---

## 📋 具体实施路线图

### Phase 1: 数据扩展 (1-2周)

#### 1.1 加密货币模块
```bash
# 安装
pip install ccxt

# 创建模块
# features/crypto.py
```

**功能**:
- 行情查询 (100+ 交易所)
- 订单簿深度
- 历史K线

#### 1.2 贵金属模块
```python
# features/metals.py
```

**功能**:
- 黄金/白银/铂金实时价格
- 历史价格
- 贵金属相关性分析

### Phase 2: 回测能力 (2-3周)

#### 2.1 整合 vn.py
```bash
# 安装
pip install vnpy

# 创建回测模块
# features/backtest.py
```

**功能**:
- 策略回测
- 绩效分析
- 风险指标

### Phase 3: Agent 智能化 (3-4周)

#### 3.1 整合 FinGPT
```bash
# 安装
pip install fingpt

# 创建 Agent 核心
# agent/core.py
```

**功能**:
- 自然语言查询
- 策略建议
- 风险提示

### Phase 4: 实盘交易 (4-6周)

#### 4.1 券商接口
- A股: CTP / XTP
- 美股: Interactive Brokers
- 加密: ccxt

---

## 🔍 现有开源 Agent 项目参考

### 1. OpenBB Terminal

**学习点**:
- 模块化架构
- 插件系统
- 多数据源适配

**架构图**:
```
openbb/
├── terminal/        # 终端界面
├── sdk/            # Python SDK
├── providers/      # 数据提供者
│   ├── alpha_vantage
│   ├── yahoo_finance
│   └── fmp
└── helpers/        # 工具函数
```

### 2. FinGPT Agent

**学习点**:
- LLM + 金融数据
- RAG 检索
- 多轮对话

**架构图**:
```
fingpt-agent/
├── llm/            # 语言模型
├── data/           # 数据处理
├── retrieval/      # 向量检索
├── chain/          # 对话链
└── tools/          # 工具调用
```

### 3. vn.py

**学习点**:
- 事件驱动架构
- 网关设计
- 策略引擎

**架构图**:
```
vnpy/
├── gateway/        # 交易网关
├── engine/         # 引擎
│   ├── event.py
│   ├── strategy.py
│   └── risk.py
└── app/           # 应用
```

---

## 💡 核心建议

### 1. 分层解耦
- 数据层、工具层、Agent层、执行层独立
- 便于替换和扩展

### 2. 插件化设计
- 参考 OpenBB 的 provider 模式
- 每个数据源独立封装

### 3. 风控优先
- vn.py 的风险引擎值得借鉴
- 在 Agent 层加入风险评估

### 4. LLM 增强
- FinGPT 提供金融领域专用能力
- 可作为 Agent 的"大脑"

### 5. 逐步迭代
- 先完善数据层 (crypto + metals)
- 再增强分析层 (backtest)
- 最后构建 Agent 层 (FinGPT)

---

## 📊 整合后能力矩阵

| 市场 | 行情 | 财务 | 新闻 | 情绪 | 交易 | 回测 |
|------|------|------|------|------|------|------|
| A股 | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 |
| 港股 | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 |
| 美股 | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 |
| 加密 | 🟡 | - | ✅ | ✅ | 🟡 | 🟡 |
| 贵金属 | 🟡 | - | ✅ | ✅ | 🟡 | 🟡 |

**图例**: ✅ 已有 | 🟡 计划中 | ❌ 不适用

---

## 🚀 下一步行动

### 立即可做

1. **整合 ccxt** - 加密货币行情
2. **整合贵金属 API** - 黄金白银价格
3. **创建 backtest 模块** - 回测框架

### 需要资源

1. **TuShare Pro Token** - 高质量A股数据
2. **券商API权限** - 实盘交易
3. **GPU资源** - FinGPT 微调

---

**结论**: 基于 unified-finance-skill 已有能力，结合 ccxt、vn.py、FinGPT 等开源项目，可以快速构建一个多市场投资Agent。建议按 Phase 1-4 逐步实施。
