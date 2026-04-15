# 投资Agent 完整架构设计

**设计时间**: 2026-04-15 21:25
**路线**: 量化优先 + LLM 辅助（保守稳健）

---

## 🏗️ 四层架构设计

### Layer 1: 数据层 (Data Layer)

```
┌─────────────────────────────────────────────────────────┐
│                    Data Provider Hub                     │
├──────────────┬──────────────┬──────────────┬────────────┤
│   A股/港股    │    美股/全球   │   加密货币    │   贵金属    │
├──────────────┼──────────────┼──────────────┼────────────┤
│  AkShare     │   OpenBB     │    ccxt      │ Metals-API │
│  TuShare     │   yfinance   │  (100+ 交易所)│ metals.live│
│  agent-stock │              │              │            │
└──────────────┴──────────────┴──────────────┴────────────┘
                      ↓
         统一数据适配器 (Data Adapter)
                      ↓
         标准化输出格式:
         {
           "asset_type": "stock|crypto|metal",
           "exchange": "sh|us|binance",
           "symbol": "600519|AAPL|BTC/USDT|XAU",
           "data": {...}
         }
```

### Layer 2: 工具层 (Tool/Skill Layer)

```python
# 统一工具接口设计

class FinanceTool:
    """金融工具基类"""
    
    name: str                    # 工具名称
    description: str             # 工具描述
    input_schema: Dict           # 输入参数 Schema
    output_schema: Dict          # 输出参数 Schema
    
    def execute(self, **kwargs) -> Dict:
        """执行工具"""
        raise NotImplementedError

# 已实现的工具 (45+)
TOOLS = {
    # 行情类
    "get_cn_stock_quote": get_quote,           # A股行情
    "get_us_stock_quote": get_quote,           # 美股行情
    "get_crypto_quote": get_crypto_quote,      # 加密货币行情
    "get_metal_price": get_metal_price,        # 贵金属价格
    
    # 分析类
    "analyze_technical": analyze_technical,     # 技术分析
    "analyze_sentiment": analyze_sentiment,     # 情绪分析
    "analyze_liquidity": analyze_liquidity,     # 流动性分析
    "analyze_valuation": get_valuation_summary, # 估值分析
    "analyze_earnings": get_beat_miss_history,  # 财报分析
    "analyze_correlation": analyze_pair_correlation, # 相关性
    "analyze_options": calculate_all_greeks,    # 期权分析
    
    # 信息类
    "get_news": get_finance_brief,              # 新闻
    "get_trending": scan_hot_stocks,            # 热门
    "search": aggregate_search,                 # 搜索
    
    # 生成类
    "generate_report": generate_full_report,    # 研报
    "visualize_chain": generate_transmission_chain, # 可视化
    
    # 回测类 (待实现)
    "backtest_strategy": backtest_strategy,     # 回测
    "analyze_portfolio": analyze_portfolio,     # 组合分析
}
```

### Layer 3: Agent层 (LLM + Reasoning)

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                     │
│                   (FinGPT / LLM Core)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Router Agent │  │ Research    │  │ Trading     │    │
│  │              │  │ Agent       │  │ Agent       │    │
│  │ 意图理解     │  │ 投研分析    │  │ 信号生成    │    │
│  │ 任务拆解     │  │ 报告生成    │  │ 策略建议    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Risk Agent  │  │ Data Agent  │  │ Monitor     │    │
│  │             │  │             │  │ Agent       │    │
│  │ 风险评估    │  │ 数据检索    │  │ 实时监控    │    │
│  │ 合规检查    │  │ 多源聚合    │  │ 异常预警    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Layer 4: 执行层 (Execution & Risk)

```
┌─────────────────────────────────────────────────────────┐
│                  Execution & Risk Control                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Order Engine│  │ Risk Engine │  │ Audit Log   │    │
│  │             │  │             │  │             │    │
│  │ vn.py       │  │ 仓位限制    │  │ 操作记录    │    │
│  │ ccxt        │  │ 止损止盈    │  │ 决策追溯    │    │
│  │ 券商API     │  │ 滑点控制    │  │ 合规审计    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ⚠️ 第一版: 只生成建议，不自动交易                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Agent 角色设计

### 1. Router Agent (路由代理)

**职责**: 理解用户意图，路由到正确的子 Agent

```python
ROUTER_PROMPT = """
你是一个金融路由代理。根据用户的问题，选择最合适的代理：

1. research_agent - 研究分析类问题
   - "分析 AAPL 的基本面"
   - "生成茅台的投研报告"
   - "比较 BTC 和 ETH 的相关性"

2. trading_agent - 交易信号类问题
   - "生成 AAPL 的交易信号"
   - "设置 BTC 的价格警报"
   - "回测均线策略"

3. risk_agent - 风险评估类问题
   - "评估我的组合风险"
   - "分析 AAPL 的流动性"
   - "计算组合的 VaR"

4. data_agent - 数据查询类问题
   - "查询 BTC 价格"
   - "获取今日新闻"
   - "列出热门股票"

用户问题: {query}
选择代理: 
"""
```

### 2. Research Agent (投研代理)

**职责**: 深度研究分析

```python
RESEARCH_WORKFLOW = [
    "1. 收集基础数据 (行情 + 财务)",
    "2. 技术分析 (指标 + 趋势)",
    "3. 情绪分析 (新闻 + 社交媒体)",
    "4. 估值分析 (PE/PB/BAND)",
    "5. 风险评估 (流动性 + 波动率)",
    "6. 生成报告 (Markdown + 图表)"
]

# 工具调用链
TOOLS_CHAIN = [
    ("get_quote", {"symbol": "AAPL"}),
    ("analyze_technical", {"symbol": "AAPL"}),
    ("analyze_sentiment", {"symbol": "AAPL"}),
    ("get_valuation_summary", {"symbol": "AAPL"}),
    ("analyze_liquidity", {"symbol": "AAPL"}),
    ("generate_report", {"topic": "AAPL投研报告", "symbol": "AAPL"})
]
```

### 3. Trading Agent (交易代理)

**职责**: 生成交易信号和建议

```python
TRADING_SIGNAL_SCHEMA = {
    "symbol": "string",
    "action": "buy|sell|hold",
    "confidence": "0.0-1.0",
    "entry_price": "float",
    "stop_loss": "float",
    "take_profit": "float",
    "position_size": "float (%)",
    "risk_reward_ratio": "float",
    "reasoning": ["reason1", "reason2"],
    "risks": ["risk1", "risk2"],
    "timestamp": "datetime"
}
```

### 4. Risk Agent (风险代理)

**职责**: 风险评估和合规检查

```python
RISK_CHECKLIST = {
    "position_limit": {
        "max_single_position": 0.2,  # 单标的最大 20%
        "max_sector_exposure": 0.4,   # 行业最大 40%
    },
    "liquidity_check": {
        "min_volume": 1000000,        # 最小成交量
        "max_spread_bps": 50,         # 最大买卖价差
    },
    "volatility_check": {
        "max_iv_percentile": 80,      # IV 最大百分位
        "max_beta": 2.0,              # 最大 Beta
    },
    "compliance": {
        "disclaimer": "非投资建议",
        "risk_warning": "投资有风险",
        "no_auto_trade": True         # 不自动交易
    }
}
```

---

## 📊 工具函数映射表

| 用户问题 | 工具调用链 | 数据源 |
|---------|-----------|--------|
| "分析 AAPL" | get_quote → analyze_technical → get_valuation_summary | yfinance |
| "BTC 价格" | get_crypto_quote | ccxt/Kraken |
| "黄金价格" | get_metal_price → get_gold_silver_ratio | metals.live |
| "热门股票" | scan_hot_stocks | yfinance |
| "财报分析" | get_beat_miss_history | yfinance |
| "组合风险" | analyze_portfolio (待实现) | 多源 |
| "回测策略" | backtest_strategy (待实现) | vn.py |

---

## 🔧 实施路线图

### Phase 1: 数据层 + 工具层 (已完成)

- ✅ A股/港股/美股行情
- ✅ 加密货币行情 (ccxt)
- ✅ 贵金属价格
- ✅ 45+ 工具函数

### Phase 2: Agent 层 (1-2周)

```python
# 实现 Agent 协调器

class InvestmentAgent:
    def __init__(self):
        self.tools = load_tools()
        self.router = RouterAgent()
        self.research = ResearchAgent()
        self.trading = TradingAgent()
        self.risk = RiskAgent()
    
    def process(self, query: str) -> Dict:
        # 1. 路由
        agent = self.router.route(query)
        
        # 2. 执行
        result = agent.execute(query, self.tools)
        
        # 3. 风险检查
        if agent.needs_risk_check:
            result = self.risk.check(result)
        
        # 4. 记录日志
        self.log(query, agent.name, result)
        
        return result
```

### Phase 3: 回测能力 (2-3周)

```python
# 整合 vn.py 回测

def backtest_strategy(
    symbol: str,
    strategy: str,  # "ma_cross", "rsi", "macd"
    params: Dict,
    period: str = "1y"
) -> Dict:
    """
    回测策略
    
    Returns:
        - total_return: 总收益
        - sharpe_ratio: 夏普比率
        - max_drawdown: 最大回撤
        - win_rate: 胜率
        - trades: 交易记录
    """
    pass
```

### Phase 4: 实盘接口 (4-6周)

- 🟡 券商 API (CTP/XTP)
- 🟡 加密交易所 (ccxt)
- 🟡 风控系统

---

## ⚠️ 安全与合规

### 免责声明模板

```
⚠️ 免责声明

本系统仅供研究和学习使用，不构成任何投资建议。

1. 所有分析结果仅供参考，不保证准确性
2. 历史数据不代表未来表现
3. 投资有风险，入市需谨慎
4. 请根据自身情况做出独立判断
5. 本系统不会自动执行任何交易

如有疑问，请咨询专业投资顾问。
```

### 风险控制规则

```python
RISK_RULES = {
    "no_auto_trade": True,          # 禁止自动交易
    "no_leverage": True,            # 禁止杠杆建议
    "no_margin": True,              # 禁止融资建议
    "max_confidence": 0.8,          # 最高置信度限制
    "require_confirmation": True,   # 需要人工确认
    "audit_all": True               # 全部审计
}
```

---

## 📝 下一步行动

### 立即可做

1. **实现 Agent 协调器**
   - Router Agent
   - 工具调度系统
   - 日志记录

2. **实现回测模块**
   - vn.py 集成
   - 策略模板
   - 绩效分析

### 需要资源

1. **FinGPT 部署** - LLM 核心
2. **TuShare Pro Token** - 高质量数据
3. **GPU资源** - LLM 推理

---

**结论**: 基于 unified-finance-skill 已有能力，按 Phase 1-4 逐步实施，先做"研究型Agent"，再做"交易型Agent"。
