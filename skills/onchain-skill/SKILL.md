---
name: onchain-whale
description: |
  Analyze crypto whale flows, ecosystem TVL changes, smart-money signals, and on-chain risk for tokens, protocols, and chains.
  Use when the user asks about whale accumulation, distribution, smart money movement, large wallet activity, protocol inflows or outflows, DeFi ecosystem strength, or on-chain confirmation for crypto trading and investment decisions.
metadata:
  openclaw:
    emoji: "🐋"
    triggers:
      - "鲸鱼"
      - "吸筹"
      - "派发"
      - "链上"
      - "大户"
      - "主力资金"
      - "资金流"
      - "异动"
      - "smart money"
      - "whale"
      - "onchain flow"
      - "netflow"
      - "accumulation"
      - "distribution"
    inputs:
      symbol:
        type: string
        description: Crypto symbol (BTC, ETH, SOL)
        required: true
      metadata.chain:
        type: string
        description: Chain name (Ethereum, Solana, Arbitrum)
        required: false
      metadata.include_dune:
        type: boolean
        description: Enable Dune enrichment (requires DUNE_API_KEY)
        required: false
        default: false
    outputs:
      success:
        type: boolean
        description: Whether the analysis succeeded
      score:
        type: number
        description: Overall score (0-100)
      confidence:
        type: number
        description: Confidence level (0.0-1.0)
      data_source:
        type: array
        description: List of data sources used
      data.whale_summary:
        type: object
        description: Whale activity summary
      data.risk_flags:
        type: array
        description: Risk warnings
      data.commentary:
        type: string
        description: Professional analyst commentary
---

# Onchain Whale Skill

Use this skill to analyze whale-related on-chain signals for crypto assets using lightweight public data sources.

## Inputs

Expected input fields:

- `symbol`: crypto symbol, such as `BTC`, `ETH`, `SOL`
- `metadata.chain`: optional chain name, such as `Ethereum`, `Solana`, `Arbitrum`
- `metadata.include_dune`: optional boolean to enable Dune enrichment if API credentials are available

## Output Contract

Always return a structured object with:

- `success`
- `skill_name`
- `score` (0-100)
- `confidence` (0.0-1.0)
- `data_source`
- `timestamp`
- `data.whale_summary`
- `data.risk_flags`
- `data.commentary`

## Trigger Phrases

This skill should be used for prompts such as:

- "BTC 鲸鱼最近在买还是在卖？"
- "ETH 最近有大户吸筹吗"
- "看看 SOL 链上资金流"
- "有没有 smart money 信号"
- "这个币的 onchain 表现支持做多吗"
- "协议 TVL 最近有没有明显异动"

## Data Sources

### Primary
- **DeFiLlama Protocols API**
  - Use for protocol TVL, 1d/7d/1m TVL changes, ecosystem breadth
- **DeFiLlama Chains API**
  - Use for chain-level TVL and recent trend confirmation

### Secondary
- **Dune Analytics API**
  - Use for whale wallet count, large transfer activity, exchange inflow/outflow, smart-money netflow
  - Treat as optional enrichment, not a hard dependency

## Analysis Rules

1. Prefer direct whale wallet flow data when Dune is available.
2. If direct whale data is unavailable, infer ecosystem accumulation or distribution from DeFiLlama protocol and chain trend proxies.
3. Never claim exact whale behavior unless the source directly provides wallet or transfer evidence.
4. Always include at least one caveat when Dune data is unavailable.
5. Always expose source names in `data_source`.
6. If data is weak, reduce `confidence` instead of forcing a strong conclusion.

## Scoring Guidance

Use a base score near neutral and adjust gradually:

- Positive whale netflow or strong ecosystem TVL growth: increase score
- Negative whale netflow or broad TVL deterioration: decrease score
- Missing direct whale evidence: reduce confidence
- Multiple risk flags: cap score upside

## Commentary Style

The commentary should sound like a concise institutional analyst note:

- State the current whale bias: accumulation, distribution, or neutral
- Mention the strongest supporting metric
- Mention one risk or uncertainty
- Avoid hype language
- Avoid making execution advice sound certain

Example:

> On-chain conditions suggest moderate accumulation, supported by improving protocol TVL breadth over the past 7 days. However, direct whale wallet flow is unavailable, so this remains a proxy-based signal rather than hard confirmation.

## Failure Behavior

If the skill cannot retrieve usable data:

- return `success=false`
- keep `score=0`
- keep `confidence=0.0`
- provide a short `error` message
- do not fabricate fallback metrics

## Notes

- Keep this skill lightweight and API-friendly
- Do not hardcode strategy advice
- Keep all conclusions traceable to source data
