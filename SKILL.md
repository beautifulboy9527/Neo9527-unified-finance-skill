---
name: unified-finance-skill
description: >
  Use this skill for professional multi-market financial analysis, valuation,
  financial anomaly checks, technical/signal review, on-chain crypto context,
  and structured investment research reports across stocks, crypto, forex,
  A-shares, US stocks, and HK stocks. The skill must cite data sources, label
  unverified or estimated data, disclose model assumptions, route analysis by
  market, and avoid presenting direct investment advice as fact.
---

# Unified Finance Skill

Version: 8.0.0 (Phase 5 Complete - 产品化功能). Tested: 2026-05-11. API and CLI supported.

This skill turns financial requests into auditable analysis. Prefer structured
outputs with data sources, model assumptions, confidence, caveats, and clear
separation between reported facts, estimates, and analyst interpretation.

## Workflow

1. If the user asks in natural language, route the request with `finance.py ask`
   or `scripts.features.nl_intent_router.route_query()` before asking them to
   memorize CLI commands.
2. Classify the requested market: `crypto`, `stock`, or `forex`.
3. Load built-ins with `load_builtin_skills()` or use `SkillRegistry.execute()`.
4. Route analysis by market:
   - `CryptoAnalysisSkill`: crypto market, technicals, market data, basic on-chain context.
   - `StockAnalysisSkill`: A-share, US stock, HK stock quick analysis.
   - `ForexAnalysisSkill`: FX pairs through yfinance symbols.
   - `SignalDetectionSkill`: market-aware signal grading.
   - `AICommentarySkill`: market-aware commentary.
   - `OnchainWhaleSkill`: DeFiLlama/Dune-style crypto ecosystem flow context.
5. For valuation or reports, include an evidence ledger, assumptions, warnings,
   and data quality score. Never hide fallback values.
6. Use professional language: state "view/bias/risk/invalidating condition";
   avoid unsupported "buy/sell" directives.
7. For Chinese reports, output Chinese stock names, Chinese industries/sectors,
   Chinese analyst ratings, explicit pattern timeframe, and clear missing-data
   disclosure. Do not use simulated data to fill unavailable fields.

## Commands

```bash
neo-finance ask "帮我看下 AAPL"
neo-finance ask "生成 002050 的正式研报" --dry-run
neo-finance analyze AAPL
neo-finance check 600519
neo-finance health AAPL
neo-finance health 002050 --gross-margin 28 --net-margin 12 --roe 18
neo-finance alerts AAPL MSFT
neo-finance doctor
neo-finance doctor --live --sample-symbol 002050
neo-finance discover --candidate-csv candidates.csv --top 10 --generate-reports --report-count 3
neo-finance monitor --watchlist-csv watchlist.csv --generate-review-reports --report-count 3 --generate-plan
neo-finance workbench AAPL --discount-rate 0.10 --peer-pe 25
neo-finance report 002050 --style kami --live-data-check --require-technical-data --strict-data --enforce-freshness
neo-finance value AAPL
neo-finance research AAPL --style value --depth standard
uvicorn api.server:app --reload
```

API report endpoints:

- `POST /api/report/preflight/{symbol}` checks whether a formal investor report has enough real inputs.
- `POST /api/report/html/{symbol}` returns investor-facing HTML and rejects incomplete strict reports.
- Both endpoints accept `price_rows` OHLCV arrays for real K-line data when the caller cannot provide a server-local CSV.
- Use `enforce_freshness=true` and `max_price_age_days` to reject stale K-line data in formal reports.

## Python Use

```python
from skills.base_skill import SkillInput, SkillRegistry, load_builtin_skills

load_builtin_skills()
output = SkillRegistry.execute(
    "StockAnalysisSkill",
    SkillInput(symbol="AAPL", market="stock")
)
```

## Report Rules

- Material numbers require source, fetched time, field name, unit, and quality.
- Estimates and model defaults must be marked as `estimated` or `assumption`.
- If a source is unavailable, return `unknown` or `unavailable`; do not invent data.
- Valuation output must show methods used, model assumptions, sensitivity where available,
  evidence summary, warnings, and confidence.
- Regulatory risk must not be reported as "low" unless verified against real sources.
- Backtest/win-rate claims must include sample source and scope; otherwise mark unverified.

## References

- Report quality rules: `references/report_quality.md`
- Valuation methodology: `references/valuation_methodology.md`
- Finance skill/tool catalog for future development: `references/finance_skill_catalog.md`
- Product strategy and monetization workflow: `references/product_strategy.md`
- Enhanced technical analysis module: `skills/shared/technical_indicators.py`
- Detailed project usage and packaging notes: `README.md`

## v6.7.0 Phase 1 - 增强技术分析

### 新增功能

| 指标 | 说明 | 状态 |
|------|------|------|
| VWAP | 成交量加权平均价 | ✅ |
| 斐波那契回撤 | 23.6%/38.2%/50%/61.8%/78.6%/100% | ✅ |
| 斐波那契扩展 | 61.8%/100%/161.8%/261.8%/423.6% | ✅ |
| 缠论中枢 | 笔段识别 + 中枢计算 | ✅ |
| K线形态 | 锤子/射击/吞没/早晨/黄昏/十字星 | ✅ |
| 趋势线 | 自动识别 + R²检验 | ✅ |
|| ADX | 趋势强度 + 方向 | ✅ |
|| 综合分析 | 信号聚合 + 偏多/偏空判断 | ✅ |

## v6.8.0 Phase 2 - 财报预测与回顾

### 新增功能

| 模块 | 说明 | CLI 命令 |
|------|------|---------|
| 财报预测 (earnings_preview) | 收入/利润/EPS预测，基于线性回归和增长率模型 | `python earnings_cli.py preview AAPL 4` |
| 财报回顾 (earnings_recap) | 业绩达标检测、利润率趋势、资产负债表、现金流质量 | `python earnings_cli.py recap AAPL` |
| 业绩比较 (performance_comparison) | 同比/环比分析、多股票横向对比、行业内对比 | `python earnings_cli.py compare AAPL MSFT` |
| 统一 CLI (earnings_cli) | 三大功能集成，一站式财报分析 | `python earnings_cli.py all AAPL` |

### 核心函数

```python
from skills.stock_skill.earnings_preview import earnings_preview, format_preview_output
from skills.stock_skill.earnings_recap import earnings_recap, format_recap_output
from skills.stock_skill.performance_comparison import compare_performance, format_comparison_output

# 财报预测
result = earnings_preview("AAPL", periods=4)
print(format_preview_output(result))

# 财报回顾
result = earnings_recap("AAPL")
print(format_recap_output(result))

# 业绩比较
result = compare_performance(["AAPL", "MSFT", "GOOGL"])
print(format_comparison_output(result))
```

### 数据依赖
- 美股: `yfinance` (pip install yfinance)
- A股: `akshare` (pip install akshare)

## Validation

Run:

```bash
pytest -q
python -m py_compile skills/base_skill.py api/server.py
python scripts/quality_gate.py <report.html> --require-layered-conclusion
```

## v6.9.0 Phase 3 - 智能选股增强

### 新增功能

| 模块 | 说明 | CLI/API |
|------|------|---------|
| 预设策略 | 7种策略: value/growth/dividend/garp/turnaround/defensive/quality | ✅ |
| 技术面筛选 | 6种条件: golden-cross/ma-bullish/volume-breakout/rsi-oversold/bollinger-squeeze/consolidation-breakout | ✅ |
| 多因子评分 | 估值25%/盈利25%/成长20%/安全15%/动量15% | ✅ |
| 行业筛选 | 按行业/板块筛选 | ✅ |

### 核心函数

```python
from skills.stock_skill.enhanced_screener import EnhancedScreener

screener = EnhancedScreener()
result = screener.screen(
    scope='hs300',           # 股票池范围
    strategy='value',        # 预设策略
    technical_checks=['golden-cross'],  # 技术面条件
    use_scoring=True,        # 多因子评分
    top=20                   # 返回TOP N
)
```

### CLI 命令

```bash
# 预设策略选股
python finance.py screen --strategy value

# 技术面筛选
python finance.py screen --technical golden-cross ma-bullish

# 多因子评分排序
python finance.py screen --scoring --top 20

# 组合条件
python finance.py screen --strategy value --technical golden-cross --scoring
```

### API 端点

```
POST /api/screen {"scope": "hs300", "strategy": "value", "scoring": true}
GET /api/screen/strategies     # 列出预设策略
GET /api/screen/technical-checks  # 列出技术面条件
```

## v7.0.0 Phase 4 - 数据源稳定性

### 新增功能

| 模块 | 说明 | CLI/API |
|------|------|---------|
| 数据源健康检查 | 跟踪每个数据源的成功/失败状态 | ✅ |
| 自动降级 | 主源失败自动切换备用源 | ✅ |
| 数据缓存 | 5分钟 TTL，减少重复请求 | ✅ |
| 数据质量评分 | 为选股结果添加置信度标签 | ✅ |

### 数据源优先级

```
1. akshare (主源) - A股专用
2. eastmoney (备用) - 东方财富
3. sina (兜底) - 新浪财经

降级逻辑:
- 连续失败3次 → 标记不可用
- 成功后 → 恢复优先级
- 自动选择健康分数最高的源
```

### CLI 命令

```bash
# 查看数据源健康报告
python finance.py data-health

# 测试数据源连通性
python finance.py data-health --test

# 禁用自动降级（直接使用主源）
python finance.py screen --strategy value --no-fallback
```

### API 端点

```
GET /api/data-source/health    # 数据源健康报告
GET /api/data-source/status    # 当前可用/不可用源
POST /api/data-source/test     # 测试指定数据源
```

## v8.0.0 Phase 5 - 产品化功能

### 新增功能

| 模块 | 说明 | CLI/API |
|------|------|---------|
| 自选股管理 | 增删改查、分组、备注、优先级 | ✅ |
| 监控告警 | 目标价/止损价触发检查 | ✅ |
| 组合风险分析 | VaR/CVaR、Sharpe、最大回撤 | ✅ |
| Markowitz优化 | max_sharpe/min_volatility/risk_parity | ✅ |
| Kelly仓位 | 胜率、盈亏比、仓位建议 | ✅ |
| 风险预警 | 集中度、相关性预警 | ✅ |
| 健康度评分 | 组合综合评分 (0-100) | ✅ |

### CLI 命令

```bash
# 自选股管理
python finance.py watchlist list                     # 列出自选股
python finance.py watchlist add 002241 --target 28 --stop 18 --notes "歌尔股份"
python finance.py watchlist remove 1                 # 移除自选股
python finance.py watchlist check                    # 检查触发条件
python finance.py watchlist summary                  # 统计报告
python finance.py watchlist groups                   # 列出分组

# 组合分析
python finance.py portfolio analyze 600519,002241,000858 --weights 0.4,0.3,0.3
python finance.py portfolio optimize 600519,002241,000858 --method max_sharpe
python finance.py portfolio kelly 600519             # Kelly仓位计算
python finance.py portfolio warnings 600519,002241   # 风险预警
```

### API 端点

```
# 自选股管理
GET  /api/watchlist              # 列出自选股
POST /api/watchlist              # 添加自选股
DELETE /api/watchlist/{id}       # 移除自选股
PATCH /api/watchlist/{id}        # 更新自选股
POST /api/watchlist/check        # 检查触发条件
GET  /api/watchlist/summary      # 统计报告
GET  /api/watchlist/groups       # 列出分组

# 组合分析
POST /api/portfolio/analyze      # 组合风险分析
POST /api/portfolio/optimize     # 组合优化
POST /api/portfolio/kelly        # Kelly仓位计算
POST /api/portfolio/warnings     # 风险预警
```

### 参考模块

| 功能 | 参考文件 |
|------|----------|
| 警报管理 | `scripts/alert_manager.py` |
| 组合管理 | `scripts/features/portfolio_manager.py` |
| 投资计划 | `skills/stock-skill/investment_plan.py` |
| 机会短名单 | `skills/stock-skill/opportunity_pipeline.py` |
