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

Version: 6.7.0 (Phase 1 Complete). Tested: 2026-05-09. API and CLI supported.

This skill turns financial requests into auditable analysis. Prefer structured
outputs with data sources, model assumptions, confidence, caveats, and clear
separation between reported facts, estimates, and analyst interpretation.

## Workflow

1. Classify the requested market: `crypto`, `stock`, or `forex`.
2. Load built-ins with `load_builtin_skills()` or use `SkillRegistry.execute()`.
3. Route analysis by market:
   - `CryptoAnalysisSkill`: crypto market, technicals, market data, basic on-chain context.
   - `StockAnalysisSkill`: A-share, US stock, HK stock quick analysis.
   - `ForexAnalysisSkill`: FX pairs through yfinance symbols.
   - `SignalDetectionSkill`: market-aware signal grading.
   - `AICommentarySkill`: market-aware commentary.
   - `OnchainWhaleSkill`: DeFiLlama/Dune-style crypto ecosystem flow context.
4. For valuation or reports, include an evidence ledger, assumptions, warnings,
   and data quality score. Never hide fallback values.
5. Use professional language: state "view/bias/risk/invalidating condition";
   avoid unsupported "buy/sell" directives.
6. For Chinese reports, output Chinese stock names, Chinese industries/sectors,
   Chinese analyst ratings, explicit pattern timeframe, and clear missing-data
   disclosure. Do not use simulated data to fill unavailable fields.

## Commands

```bash
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
| ADX | 趋势强度 + 方向 | ✅ |
| 综合分析 | 信号聚合 + 偏多/偏空判断 | ✅ |

## Validation

Run:

```bash
pytest -q
python -m py_compile skills/base_skill.py api/server.py
python scripts/quality_gate.py <report.html> --require-layered-conclusion
```
