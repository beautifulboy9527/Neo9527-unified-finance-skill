#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeFiLlama 链上数据增强 Skill
专注于 TVL、资金流、协议数据
"""

import requests
import sys
from typing import Dict, List, Optional
from datetime import datetime

if __name__ != '__main__':
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class DeFiLlamaSkill:
    """DeFiLlama 数据获取 Skill"""
    
    BASE_URL = "https://api.llama.fi"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Neo9527-Finance-Skill/4.2'
        })
    
    def get_chain_tvl(self, chain: str = "Ethereum") -> Dict:
        """
        获取链级 TVL 数据
        
        Args:
            chain: 链名称
            
        Returns:
            {
                'chain': str,
                'tvl': float,
                'tvl_change_1d': float,
                'tvl_change_7d': float,
                'token_symbol': str,
                'data_source': str
            }
        """
        try:
            url = f"{self.BASE_URL}/v2/chains"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'error': f'API error: {resp.status_code}'}
            
            chains = resp.json()
            
            # 查找目标链
            target_chain = None
            for c in chains:
                if c.get('name', '').lower() == chain.lower():
                    target_chain = c
                    break
            
            if not target_chain:
                return {'error': f'Chain not found: {chain}'}
            
            return {
                'chain': target_chain.get('name'),
                'tvl': target_chain.get('tvl', 0),
                'tvl_change_1d': target_chain.get('change_1d', 0),
                'tvl_change_7d': target_chain.get('change_7d', 0),
                'token_symbol': target_chain.get('tokenSymbol', 'ETH'),
                'chain_id': target_chain.get('chainId'),
                'data_source': 'DeFiLlama',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_protocol_flows(self, protocol: str, days: int = 7) -> Dict:
        """
        获取协议资金流数据
        
        Args:
            protocol: 协议名称
            days: 天数
            
        Returns:
            资金流数据
        """
        try:
            # 获取协议列表
            url = f"{self.BASE_URL}/protocols"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'error': f'API error: {resp.status_code}'}
            
            protocols = resp.json()
            
            # 查找目标协议
            target = None
            for p in protocols:
                if p.get('name', '').lower() == protocol.lower():
                    target = p
                    break
            
            if not target:
                return {'error': f'Protocol not found: {protocol}'}
            
            return {
                'protocol': target.get('name'),
                'tvl': target.get('tvl', 0),
                'tvl_change_1d': target.get('change_1d', 0),
                'tvl_change_7d': target.get('change_7d', 0),
                'chain': target.get('chain'),
                'category': target.get('category'),
                'forked_from': target.get('forkedFrom', []),
                'data_source': 'DeFiLlama'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_top_protocols(self, chain: str = "Ethereum", limit: int = 10) -> List[Dict]:
        """
        获取链上 Top 协议
        
        Args:
            chain: 链名称
            limit: 数量限制
            
        Returns:
            协议列表
        """
        try:
            url = f"{self.BASE_URL}/protocols"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return []
            
            protocols = resp.json()
            
            # 筛选链 + 排序
            chain_protocols = [
                p for p in protocols
                if p.get('chain') == chain or chain in p.get('chains', [])
            ]
            
            # 按 TVL 排序
            sorted_protocols = sorted(
                chain_protocols,
                key=lambda x: x.get('tvl', 0),
                reverse=True
            )[:limit]
            
            return [
                {
                    'name': p.get('name'),
                    'tvl': p.get('tvl', 0),
                    'change_1d': p.get('change_1d', 0),
                    'change_7d': p.get('change_7d', 0),
                    'category': p.get('category'),
                    'chain': p.get('chain'),
                    'data_source': 'DeFiLlama'
                }
                for p in sorted_protocols
            ]
            
        except Exception as e:
            return []
    
    def get_stablecoin_data(self) -> Dict:
        """
        获取稳定币数据
        
        Returns:
            稳定币统计
        """
        try:
            url = f"{self.BASE_URL}/stablecoins"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'error': f'API error: {resp.status_code}'}
            
            data = resp.json()
            
            return {
                'total_stablecoin_tvl': data.get('total', 0),
                'chains': data.get('chains', {}),
                'data_source': 'DeFiLlama'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_defi_health(self, chain: str = "Ethereum") -> Dict:
        """
        综合分析 DeFi 健康度
        
        Args:
            chain: 链名称
            
        Returns:
            {
                'trend': str,  # bullish/bearish/neutral
                'signals': list,
                'score': int
            }
        """
        result = {
            'chain': chain,
            'trend': 'neutral',
            'signals': [],
            'score': 50,
            'data_source': 'DeFiLlama'
        }
        
        # 获取 TVL 数据
        tvl_data = self.get_chain_tvl(chain)
        
        if 'error' in tvl_data:
            result['error'] = tvl_data['error']
            return result
        
        # 分析 TVL 变化
        tvl_change_1d = tvl_data.get('tvl_change_1d', 0)
        tvl_change_7d = tvl_data.get('tvl_change_7d', 0)
        
        signals = []
        score = 50
        
        # 1日变化
        if tvl_change_1d > 10:
            signals.append({
                'type': 'tvl_1d',
                'signal': 'bullish',
                'strength': 4,
                'desc': f'TVL 24h 大幅增长 {tvl_change_1d:.1f}%，资金快速流入'
            })
            score += 15
        elif tvl_change_1d > 3:
            signals.append({
                'type': 'tvl_1d',
                'signal': 'bullish',
                'strength': 2,
                'desc': f'TVL 24h 增长 {tvl_change_1d:.1f}%，资金持续流入'
            })
            score += 8
        elif tvl_change_1d < -10:
            signals.append({
                'type': 'tvl_1d',
                'signal': 'bearish',
                'strength': -4,
                'desc': f'TVL 24h 大幅下降 {tvl_change_1d:.1f}%，资金快速流出'
            })
            score -= 15
        elif tvl_change_1d < -3:
            signals.append({
                'type': 'tvl_1d',
                'signal': 'bearish',
                'strength': -2,
                'desc': f'TVL 24h 下降 {tvl_change_1d:.1f}%，资金流出'
            })
            score -= 8
        
        # 7日变化
        if tvl_change_7d > 20:
            signals.append({
                'type': 'tvl_7d',
                'signal': 'bullish',
                'strength': 3,
                'desc': f'TVL 7日大幅增长 {tvl_change_7d:.1f}%，长期趋势向上'
            })
            score += 10
        elif tvl_change_7d < -20:
            signals.append({
                'type': 'tvl_7d',
                'signal': 'bearish',
                'strength': -3,
                'desc': f'TVL 7日大幅下降 {tvl_change_7d:.1f}%，长期趋势向下'
            })
            score -= 10
        
        # 获取 Top 协议
        top_protocols = self.get_top_protocols(chain, 5)
        
        if top_protocols:
            # 分析协议集中度
            total_tvl = sum(p['tvl'] for p in top_protocols)
            top1_tvl = top_protocols[0]['tvl'] if top_protocols else 0
            concentration = (top1_tvl / total_tvl * 100) if total_tvl > 0 else 0
            
            if concentration > 60:
                signals.append({
                    'type': 'concentration',
                    'signal': 'bearish',
                    'strength': -2,
                    'desc': f'协议集中度过高 ({concentration:.1f}%)，系统性风险'
                })
                score -= 5
        
        result['tvl_data'] = tvl_data
        result['top_protocols'] = top_protocols
        result['signals'] = signals
        result['score'] = max(0, min(100, score))
        
        # 趋势判断
        if score >= 65:
            result['trend'] = 'bullish'
        elif score <= 35:
            result['trend'] = 'bearish'
        
        return result


def get_defillama_data(chain: str = "Ethereum") -> Dict:
    """便捷函数"""
    skill = DeFiLlamaSkill()
    return skill.analyze_defi_health(chain)


if __name__ == '__main__':
    print("Testing DeFiLlama Skill...")
    print("=" * 60)
    
    # 测试链级数据
    print("\n[Chain TVL Data]")
    result = get_defillama_data("Ethereum")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Chain: {result['chain']}")
        print(f"Score: {result['score']}/100")
        print(f"Trend: {result['trend']}")
        print(f"\nSignals ({len(result['signals'])}):")
        for s in result['signals']:
            print(f"  [{s['type']}] {s['signal']}: {s['desc']} (strength: {s['strength']:+d})")
        
        if result.get('tvl_data'):
            tvl = result['tvl_data']
            print(f"\nTVL Data:")
            print(f"  Total: ${tvl.get('tvl', 0):,.0f}")
            print(f"  24h: {tvl.get('tvl_change_1d', 0):+.2f}%")
            print(f"  7d: {tvl.get('tvl_change_7d', 0):+.2f}%")
        
        if result.get('top_protocols'):
            print(f"\nTop Protocols:")
            for i, p in enumerate(result['top_protocols'][:5], 1):
                print(f"  {i}. {p['name']}: ${p['tvl']:,.0f} ({p['change_1d']:+.2f}%)")
    
    print("\n" + "=" * 60)
