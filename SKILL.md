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

Version: 6.6.4. Tested: 2026-04-28. API and CLI supported.

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
neo-finance value AAPL
neo-finance research AAPL --style value --depth standard
uvicorn api.server:app --reload
```

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
- Detailed project usage and packaging notes: `README.md`

## Validation

Run:

```bash
pytest -q
python -m py_compile skills/base_skill.py api/server.py
python scripts/quality_gate.py <report.html> --require-layered-conclusion
```
