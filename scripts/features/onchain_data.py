#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
链上数据获取模块
整合 DeFiLlama + Dune Analytics + Etherscan
"""

import sys
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

if __name__ != '__main__':
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class OnchainDataFetcher:
    """链上数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_defillama_data(self, chain: str = 'Ethereum') -> Dict:
        """
        获取 DeFi TVL 数据
        
        Args:
            chain: 链名称
            
        Returns:
            DeFi 数据
        """
        try:
            # 获取所有协议数据
            url = "https://api.llama.fi/protocols"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'error': f'API error: {resp.status_code}'}
            
            protocols = resp.json()
            
            # 筛选目标链的协议
            chain_protocols = [
                p for p in protocols
                if p.get('chain') == chain or chain in p.get('chains', [])
            ]
            
            if not chain_protocols:
                return {'error': f'No data for chain: {chain}'}
            
            # 计算总 TVL
            total_tvl = sum(p.get('tvl', 0) for p in chain_protocols if p.get('tvl'))
            
            # Top 5 协议
            top_protocols = sorted(
                chain_protocols,
                key=lambda x: x.get('tvl', 0),
                reverse=True
            )[:5]
            
            # TVL 变化 (24h)
            tvl_change_24h = sum(
                p.get('change_1d', 0) * p.get('tvl', 0) / 100
                for p in chain_protocols
                if p.get('tvl') and p.get('change_1d')
            ) / total_tvl * 100 if total_tvl > 0 else 0
            
            return {
                'chain': chain,
                'total_tvl': total_tvl,
                'tvl_change_24h': round(tvl_change_24h, 2),
                'protocol_count': len(chain_protocols),
                'top_protocols': [
                    {
                        'name': p.get('name'),
                        'tvl': p.get('tvl', 0),
                        'change_1d': p.get('change_1d', 0)
                    }
                    for p in top_protocols
                ],
                'data_source': 'DeFiLlama',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_whale_transactions_simple(self, symbol: str = 'BTC') -> Dict:
        """
        获取鲸鱼交易数据 (简化版 - 使用公开数据)
        
        注: 完整版需要 Dune API key 或 Etherscan API key
        这里使用模拟数据展示格式
        
        Args:
            symbol: 币种
            
        Returns:
            鲸鱼交易数据
        """
        try:
            # 模拟鲸鱼交易数据 (实际需要 API key)
            # 生产环境应替换为真实 API 调用
            
            # 模拟数据结构
            mock_data = {
                'BTC': {
                    'large_inflow_24h': 1240,  # BTC
                    'large_outflow_24h': 890,
                    'whale_activity': 'accumulating',  # accumulating/distributing/neutral
                    'top_whales': [
                        {'address': '0x1234...5678', 'balance_change': 500, 'action': 'buy'},
                        {'address': '0xabcd...efgh', 'balance_change': -300, 'action': 'sell'},
                    ]
                },
                'ETH': {
                    'large_inflow_24h': 15420,
                    'large_outflow_24h': 12350,
                    'whale_activity': 'accumulating',
                    'top_whales': [
                        {'address': '0x9876...5432', 'balance_change': 5000, 'action': 'buy'},
                    ]
                }
            }
            
            data = mock_data.get(symbol.upper(), mock_data['BTC'])
            
            net_flow = data['large_inflow_24h'] - data['large_outflow_24h']
            
            return {
                'symbol': symbol,
                'large_inflow_24h': data['large_inflow_24h'],
                'large_outflow_24h': data['large_outflow_24h'],
                'net_flow': net_flow,
                'whale_activity': data['whale_activity'],
                'signal': 'bullish' if net_flow > 0 else 'bearish' if net_flow < 0 else 'neutral',
                'signal_desc': f"鲸鱼净{'流入' if net_flow > 0 else '流出'} {abs(net_flow):,} {symbol} ({'低吸信号' if net_flow > 0 else '派发信号'})",
                'data_source': 'Simulated (需配置 API key)',
                'note': '完整数据需要 Dune/Etherscan API key'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_btc_onchain_metrics(self) -> Dict:
        """
        获取 BTC 链上指标
        
        Returns:
            BTC 链上数据
        """
        try:
            # Blockchain.com 公开 API
            url = "https://api.blockchain.info/stats"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return {'error': f'API error: {resp.status_code}'}
            
            data = resp.json()
            
            return {
                'hashrate': data.get('hash_rate', 0) / 1e18,  # EH/s
                'difficulty': data.get('difficulty', 0) / 1e12,  # T
                'block_size': data.get('block_size', 0) / 1e6,  # MB
                'total_btc': data.get('totalbc', 0) / 1e8,  # BTC
                'n_transactions': data.get('n_tx', 0),  # 总交易数
                'data_source': 'Blockchain.com'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_onchain_data(self, symbol: str = 'BTC') -> Dict:
        """
        获取所有链上数据
        
        Args:
            symbol: 币种
            
        Returns:
            完整链上数据
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. DeFi 数据 (ETH)
        if symbol.upper() in ['ETH', 'ETHEREUM']:
            result['defi'] = self.get_defillama_data('Ethereum')
        
        # 2. BTC 链上指标
        if symbol.upper() in ['BTC', 'BITCOIN']:
            result['network'] = self.get_btc_onchain_metrics()
        
        # 3. 鲸鱼交易
        result['whale'] = self.get_whale_transactions_simple(symbol)
        
        # 4. 生成信号
        signals = []
        
        # DeFi TVL 信号
        if 'defi' in result and 'error' not in result['defi']:
            if result['defi'].get('tvl_change_24h', 0) > 5:
                signals.append({
                    'type': 'defi_tvl',
                    'signal': 'bullish',
                    'strength': 3,
                    'desc': f"DeFi TVL 24h 增长 {result['defi']['tvl_change_24h']:.2f}%"
                })
        
        # 鲸鱼信号
        if 'whale' in result and 'error' not in result['whale']:
            net_flow = result['whale'].get('net_flow', 0)
            if net_flow > 0:
                signals.append({
                    'type': 'whale_flow',
                    'signal': 'bullish',
                    'strength': 4,
                    'desc': result['whale'].get('signal_desc', '')
                })
            elif net_flow < 0:
                signals.append({
                    'type': 'whale_flow',
                    'signal': 'bearish',
                    'strength': -4,
                    'desc': result['whale'].get('signal_desc', '')
                })
        
        result['signals'] = signals
        
        return result


def get_onchain_data(symbol: str = 'BTC') -> Dict:
    """便捷函数"""
    fetcher = OnchainDataFetcher()
    return fetcher.get_all_onchain_data(symbol)


if __name__ == '__main__':
    print("Testing on-chain data fetcher...")
    print("=" * 60)
    
    # 测试 BTC
    print("\n[BTC On-Chain Data]")
    btc_data = get_onchain_data('BTC')
    
    if 'network' in btc_data and 'error' not in btc_data['network']:
        print(f"Hashrate: {btc_data['network']['hashrate']:.2f} EH/s")
        print(f"Difficulty: {btc_data['network']['difficulty']:.2f} T")
        print(f"Total BTC: {btc_data['network']['total_btc']:,.0f}")
    
    if 'whale' in btc_data and 'error' not in btc_data['whale']:
        print(f"\nWhale Activity:")
        print(f"  Net Flow: {btc_data['whale']['net_flow']:+,} BTC")
        print(f"  Signal: {btc_data['whale']['signal_desc']}")
    
    # 测试 ETH
    print("\n" + "=" * 60)
    print("\n[ETH On-Chain Data]")
    eth_data = get_onchain_data('ETH')
    
    if 'defi' in eth_data and 'error' not in eth_data['defi']:
        print(f"Total TVL: ${eth_data['defi']['total_tvl']:,.0f}")
        print(f"TVL Change 24h: {eth_data['defi']['tvl_change_24h']:+.2f}%")
        print(f"Protocol Count: {eth_data['defi']['protocol_count']}")
        
        print("\nTop 5 Protocols:")
        for i, p in enumerate(eth_data['defi']['top_protocols'], 1):
            print(f"  {i}. {p['name']}: ${p['tvl']:,.0f} ({p['change_1d']:+.2f}%)")
    
    print("\n" + "=" * 60)
