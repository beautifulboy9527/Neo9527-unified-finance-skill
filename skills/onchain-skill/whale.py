#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OnchainWhaleSkill - 链上鲸鱼分析

数据源:
- DeFiLlama (主源)
- Dune Analytics (可选增强)

功能:
- 鲸鱼流向分析
- 协议TVL变化
- 链上风险评估
"""

import os
import sys
import time
import requests
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, register_skill


@register_skill
class OnchainWhaleSkill(BaseSkill):
    """
    On-chain whale activity analysis skill.
    Primary source: DeFiLlama
    Optional source: Dune Analytics
    """
    
    @property
    def description(self) -> str:
        return "Analyze whale flows, protocol TVL changes, large wallet activity, and smart-money signals for crypto assets."
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['crypto']
    
    DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"
    DEFILLAMA_CHAINS_URL = "https://api.llama.fi/v2/chains"
    DUNE_API_BASE = "https://api.dune.com/api/v1"
    
    def __init__(self, timeout: int = 15):
        super().__init__()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "neo9527-finance-skill/4.4.0",
            "Accept": "application/json",
        })
    
    def execute(self, skill_input: SkillInput) -> SkillOutput:
        symbol = (skill_input.symbol or "").upper().strip()
        params = getattr(skill_input, 'params', {}) or {}
        chain = self._normalize_chain(params.get("chain", ""))
        include_dune = bool(params.get("include_dune", False))
        
        if not symbol:
            return self._error("symbol is required")
        
        try:
            protocol_data = self._fetch_defillama_protocols(symbol)
            chain_data = self._fetch_defillama_chain_overview(chain)
            
            dune_data = None
            if include_dune:
                dune_data = self._fetch_dune_whale_example(symbol)
            
            whale_summary = self._build_whale_summary(
                symbol=symbol,
                protocol_data=protocol_data,
                chain_data=chain_data,
                dune_data=dune_data,
            )
            
            confidence = self._compute_confidence(protocol_data, chain_data, dune_data)
            risk_flags = self._build_risk_flags(protocol_data, dune_data)
            commentary = self._generate_commentary(whale_summary, risk_flags)
            
            return SkillOutput(
                success=True,
                skill_name=self.name,
                data={
                    "symbol": symbol,
                    "chain": chain,
                    "whale_summary": whale_summary,
                    "risk_flags": risk_flags,
                    "commentary": commentary,
                    "raw": {
                        "defillama_protocols": protocol_data[:5] if protocol_data else [],
                        "defillama_chain": chain_data,
                        "dune": dune_data,
                    },
                },
                signals=self._build_signals(whale_summary, risk_flags),
                confidence=confidence,
                score=self._score_whale_signal(whale_summary, risk_flags),
                data_source=self._build_sources(include_dune, protocol_data, chain_data, dune_data),
                timestamp=int(time.time()),
                error=None,
            )
        except Exception as e:
            return self._error(str(e))
    
    # --------------------------
    # Fetch layer
    # --------------------------
    
    def _fetch_defillama_protocols(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Heuristic match against protocols related to a symbol/project.
        Useful for TVL / volume / inflow changes around a token ecosystem.
        """
        resp = self.session.get(self.DEFILLAMA_PROTOCOLS_URL, timeout=self.timeout)
        resp.raise_for_status()
        items = resp.json()
        
        symbol_lower = symbol.lower()
        matched = []
        for item in items:
            name = str(item.get("name", "")).lower()
            category = str(item.get("category", "")).lower()
            chains = " ".join(item.get("chains", []) or []).lower()
            
            if symbol_lower in name or symbol_lower in category or symbol_lower in chains:
                matched.append({
                    "name": item.get("name"),
                    "category": item.get("category"),
                    "chains": item.get("chains"),
                    "tvl": item.get("tvl"),
                    "change_1d": self._safe_nested(item, ["change_1d"]),
                    "change_7d": self._safe_nested(item, ["change_7d"]),
                    "change_1m": self._safe_nested(item, ["change_1m"]),
                    "mcap": item.get("mcap"),
                    "url": item.get("url"),
                })
        
        matched.sort(key=lambda x: x.get("tvl") or 0, reverse=True)
        return matched[:10]
    
    def _fetch_defillama_chain_overview(self, chain: str) -> Optional[Dict[str, Any]]:
        if not chain:
            return None
        
        resp = self.session.get(self.DEFILLAMA_CHAINS_URL, timeout=self.timeout)
        resp.raise_for_status()
        items = resp.json()
        
        for item in items:
            if str(item.get("name", "")).lower() == chain.lower():
                return {
                    "name": item.get("name"),
                    "tvl": item.get("tvl"),
                    "tokenSymbol": item.get("tokenSymbol"),
                    "change_1d": item.get("change_1d"),
                    "change_7d": item.get("change_7d"),
                    "change_1m": item.get("change_1m"),
                }
        return None
    
    def _fetch_dune_whale_example(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Example for Dune integration.
        Requires:
          - DUNE_API_KEY
          - DUNE_QUERY_ID (public or your own query)
        """
        api_key = os.getenv("DUNE_API_KEY")
        query_id = os.getenv("DUNE_QUERY_ID")
        
        if not api_key or not query_id:
            return None
        
        url = f"{self.DUNE_API_BASE}/query/{query_id}/results"
        headers = {"X-Dune-API-Key": api_key}
        params = {"symbol": symbol}
        
        resp = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
        if resp.status_code != 200:
            return None
        
        payload = resp.json()
        rows = payload.get("result", {}).get("rows", [])
        if not rows:
            return None
        
        row = rows[0]
        return {
            "wallets_24h": row.get("wallets_24h"),
            "netflow_usd_24h": row.get("netflow_usd_24h"),
            "tx_count_24h": row.get("tx_count_24h"),
            "source": "dune",
        }
    
    # --------------------------
    # Build layer
    # --------------------------
    
    def _build_whale_summary(
        self,
        symbol: str,
        protocol_data: List[Dict[str, Any]],
        chain_data: Optional[Dict[str, Any]],
        dune_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        total_tvl = sum((p.get("tvl") or 0) for p in protocol_data)
        avg_7d = self._avg([p.get("change_7d") for p in protocol_data if p.get("change_7d") is not None])
        avg_1d = self._avg([p.get("change_1d") for p in protocol_data if p.get("change_1d") is not None])
        
        whale_bias = "neutral"
        if dune_data and isinstance(dune_data.get("netflow_usd_24h"), (int, float)):
            if dune_data["netflow_usd_24h"] > 0:
                whale_bias = "accumulation"
            elif dune_data["netflow_usd_24h"] < 0:
                whale_bias = "distribution"
        elif avg_7d is not None:
            if avg_7d > 3:
                whale_bias = "accumulation"
            elif avg_7d < -3:
                whale_bias = "distribution"
        
        return {
            "symbol": symbol,
            "matched_protocols": len(protocol_data),
            "ecosystem_tvl": round(total_tvl, 2),
            "avg_protocol_change_1d": avg_1d,
            "avg_protocol_change_7d": avg_7d,
            "chain_tvl": chain_data.get("tvl") if chain_data else None,
            "chain_change_7d": chain_data.get("change_7d") if chain_data else None,
            "whale_wallets_24h": dune_data.get("wallets_24h") if dune_data else None,
            "whale_netflow_usd_24h": dune_data.get("netflow_usd_24h") if dune_data else None,
            "whale_tx_count_24h": dune_data.get("tx_count_24h") if dune_data else None,
            "whale_bias": whale_bias,
        }
    
    def _build_signals(
        self,
        whale_summary: Dict[str, Any],
        risk_flags: List[str]
    ) -> List[Dict]:
        """构建信号列表"""
        signals = []
        
        bias = whale_summary.get("whale_bias", "neutral")
        avg_7d = whale_summary.get("avg_protocol_change_7d")
        
        # 鲸鱼偏向信号
        if bias == "accumulation":
            signals.append({
                "category": "链上数据",
                "name": "鲸鱼动向",
                "signal": "bullish",
                "strength": 4,
                "desc": "鲸鱼吸筹信号"
            })
        elif bias == "distribution":
            signals.append({
                "category": "链上数据",
                "name": "鲸鱼动向",
                "signal": "bearish",
                "strength": -4,
                "desc": "鲸鱼派发信号"
            })
        
        # TVL变化信号
        if isinstance(avg_7d, (int, float)):
            if avg_7d > 5:
                signals.append({
                    "category": "链上数据",
                    "name": "TVL增长",
                    "signal": "bullish",
                    "strength": 3,
                    "desc": f"生态TVL 7日增长 {avg_7d:.1f}%"
                })
            elif avg_7d < -5:
                signals.append({
                    "category": "链上数据",
                    "name": "TVL下降",
                    "signal": "bearish",
                    "strength": -3,
                    "desc": f"生态TVL 7日下降 {avg_7d:.1f}%"
                })
        
        return signals
    
    def _build_risk_flags(
        self,
        protocol_data: List[Dict[str, Any]],
        dune_data: Optional[Dict[str, Any]],
    ) -> List[str]:
        flags = []
        
        if not protocol_data:
            flags.append("No strongly matched DeFiLlama protocol data; ecosystem inference may be weak.")
        
        if protocol_data:
            negatives = [p for p in protocol_data if isinstance(p.get("change_7d"), (int, float)) and p["change_7d"] < -8]
            if len(negatives) >= 2:
                flags.append("Multiple related protocols show sharp 7d TVL decline.")
        
        if dune_data is None:
            flags.append("Dune whale wallet flow not enabled or unavailable; whale conclusions rely on ecosystem proxies.")
        
        return flags
    
    def _generate_commentary(self, whale_summary: Dict[str, Any], risk_flags: List[str]) -> str:
        bias = whale_summary.get("whale_bias", "neutral")
        avg7 = whale_summary.get("avg_protocol_change_7d")
        netflow = whale_summary.get("whale_netflow_usd_24h")
        
        if bias == "accumulation":
            base = "On-chain and ecosystem signals suggest whale accumulation is strengthening."
        elif bias == "distribution":
            base = "On-chain and ecosystem signals suggest whale distribution or risk-off behavior."
        else:
            base = "Whale activity appears mixed; the current signal is not decisive."
        
        details = []
        if avg7 is not None:
            details.append(f"Protocol 7d TVL trend: {avg7:.2f}%")
        if isinstance(netflow, (int, float)):
            details.append(f"Estimated whale netflow 24h: ${netflow:,.0f}")
        
        if risk_flags:
            details.append("Key caveat: " + risk_flags[0])
        
        return base + " " + " | ".join(details)
    
    def _score_whale_signal(self, whale_summary: Dict[str, Any], risk_flags: List[str]) -> int:
        score = 50
        bias = whale_summary.get("whale_bias")
        avg7 = whale_summary.get("avg_protocol_change_7d")
        
        if bias == "accumulation":
            score += 15
        elif bias == "distribution":
            score -= 15
        
        if isinstance(avg7, (int, float)):
            if avg7 > 5:
                score += 10
            elif avg7 < -5:
                score -= 10
        
        score -= min(len(risk_flags) * 5, 15)
        return max(0, min(100, score))
    
    def _compute_confidence(
        self,
        protocol_data: List[Dict[str, Any]],
        chain_data: Optional[Dict[str, Any]],
        dune_data: Optional[Dict[str, Any]],
    ) -> float:
        conf = 0.45
        if protocol_data:
            conf += 0.2
        if chain_data:
            conf += 0.15
        if dune_data:
            conf += 0.2
        return round(min(conf, 0.95), 2)
    
    def _build_sources(
        self,
        include_dune: bool,
        protocol_data: List[Dict[str, Any]],
        chain_data: Optional[Dict[str, Any]],
        dune_data: Optional[Dict[str, Any]],
    ) -> List[str]:
        sources = []
        if protocol_data:
            sources.append("DeFiLlama Protocols API")
        if chain_data:
            sources.append("DeFiLlama Chains API")
        if include_dune and dune_data:
            sources.append("Dune Analytics API")
        return sources
    
    # --------------------------
    # Helpers
    # --------------------------
    
    def _normalize_chain(self, chain: Optional[str]) -> str:
        if not chain:
            return ""
        mapping = {
            "eth": "Ethereum",
            "ethereum": "Ethereum",
            "btc": "Bitcoin",
            "bitcoin": "Bitcoin",
            "sol": "Solana",
            "solana": "Solana",
            "arb": "Arbitrum",
            "arbitrum": "Arbitrum",
        }
        return mapping.get(chain.lower(), chain)
    
    def _avg(self, values: List[Any]) -> Optional[float]:
        nums = [v for v in values if isinstance(v, (int, float))]
        if not nums:
            return None
        return round(sum(nums) / len(nums), 2)
    
    def _safe_nested(self, data: Dict[str, Any], path: List[str]) -> Any:
        cur = data
        for key in path:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(key)
        return cur
    
    def _error(self, message: str) -> SkillOutput:
        return SkillOutput(
            success=False,
            skill_name=self.name,
            data={},
            signals=[],
            confidence=0.0,
            score=0,
            data_source=[],
            timestamp=int(time.time()),
            error=message,
        )


if __name__ == '__main__':
    from skills.base_skill import SkillInput
    
    print("Testing OnchainWhaleSkill...")
    print("=" * 60)
    
    skill = OnchainWhaleSkill()
    
    # 测试BTC
    print("\n[Test 1: BTC Analysis]")
    result = skill.execute(SkillInput(symbol='BTC', market='crypto'))
    
    print(f"Success: {result.success}")
    print(f"Score: {result.score}/100")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Whale Bias: {result.data.get('whale_summary', {}).get('whale_bias', 'unknown')}")
    print(f"Data Sources: {', '.join(result.data_source)}")
    
    if result.data.get('commentary'):
        print(f"\nCommentary:\n{result.data['commentary']}")
    
    if result.data.get('risk_flags'):
        print(f"\nRisk Flags:")
        for flag in result.data['risk_flags']:
            print(f"  - {flag}")
    
    print("\n" + "=" * 60)
