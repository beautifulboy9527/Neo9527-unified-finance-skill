#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据 Provider 层 - 统一数据接入 + 回退 + 缓存

职责:
- 统一数据源接口
- 自动回退链路
- 数据质量验证
- 字段级 provenance
"""

import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


@dataclass
class DataProvenance:
    """数据来源追踪"""
    source: str           # 数据源名称
    field: str            # 字段名
    timestamp: str        # 获取时间
    freshness: int        # 新鲜度 (秒)
    confidence: float     # 置信度 (0-1)
    is_primary: bool      # 是否主源
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'field': self.field,
            'timestamp': self.timestamp,
            'freshness': self.freshness,
            'confidence': self.confidence,
            'is_primary': self.is_primary
        }


@dataclass
class ProviderResult:
    """Provider 返回结果"""
    success: bool
    data: Dict
    provenance: List[DataProvenance]
    error: Optional[str] = None
    fallback_used: bool = False
    
    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'data': self.data,
            'provenance': [p.to_dict() for p in self.provenance],
            'error': self.error,
            'fallback_used': self.fallback_used
        }


class BaseProvider(ABC):
    """Provider 基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'Neo9527-Finance-Skill/4.3 ({name})'
        })
        self._cache = {}
        self._cache_ttl = 300  # 5分钟缓存
    
    @abstractmethod
    def fetch(self, symbol: str, **kwargs) -> ProviderResult:
        """获取数据"""
        pass
    
    def _get_cache(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """设置缓存"""
        self._cache[key] = (data, time.time())
    
    def _validate_data(self, data: Dict, required_fields: List[str]) -> bool:
        """验证数据完整性"""
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        return True
    
    def _create_provenance(
        self,
        field: str,
        confidence: float = 1.0,
        is_primary: bool = True
    ) -> DataProvenance:
        """创建数据来源记录"""
        return DataProvenance(
            source=self.name,
            field=field,
            timestamp=datetime.now().isoformat(),
            freshness=0,
            confidence=confidence,
            is_primary=is_primary
        )


class QuoteProvider(BaseProvider):
    """行情数据 Provider"""
    
    def __init__(self):
        super().__init__("QuoteProvider")
        self.providers = [
            CoinGeckoQuoteProvider(),
            YFinanceQuoteProvider()
        ]
    
    def fetch(self, symbol: str, market: str = 'crypto') -> ProviderResult:
        """获取行情数据，自动回退"""
        
        cache_key = f"quote:{symbol}:{market}"
        cached = self._get_cache(cache_key)
        if cached:
            return ProviderResult(
                success=True,
                data=cached,
                provenance=[self._create_provenance('cache', 0.9, False)]
            )
        
        # 尝试主源
        for provider in self.providers:
            if market in provider.supported_markets:
                result = provider.fetch(symbol)
                
                if result.success:
                    # 验证数据
                    if self._validate_data(result.data, ['price']):
                        self._set_cache(cache_key, result.data)
                        return result
        
        # 所有源都失败
        return ProviderResult(
            success=False,
            data={},
            provenance=[],
            error=f'All providers failed for {symbol}',
            fallback_used=True
        )


class CoinGeckoQuoteProvider(BaseProvider):
    """CoinGecko 行情 Provider"""
    
    supported_markets = ['crypto']
    
    def __init__(self):
        super().__init__("CoinGecko")
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def fetch(self, symbol: str) -> ProviderResult:
        """获取加密货币行情"""
        
        try:
            # 转换符号
            coin_id = self._symbol_to_id(symbol)
            
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            
            resp = self.session.get(url, params=params, timeout=10)
            
            if resp.status_code != 200:
                return ProviderResult(
                    success=False,
                    data={},
                    provenance=[],
                    error=f'API error: {resp.status_code}'
                )
            
            data = resp.json()
            
            if coin_id not in data:
                return ProviderResult(
                    success=False,
                    data={},
                    provenance=[],
                    error='Symbol not found'
                )
            
            coin_data = data[coin_id]
            
            return ProviderResult(
                success=True,
                data={
                    'price': coin_data.get('usd', 0),
                    'change_24h': coin_data.get('usd_24h_change', 0),
                    'volume_24h': coin_data.get('usd_24h_vol', 0),
                    'market_cap': coin_data.get('usd_market_cap', 0)
                },
                provenance=[
                    self._create_provenance('price', 0.95, True),
                    self._create_provenance('change_24h', 0.95, True),
                    self._create_provenance('volume_24h', 0.90, True),
                    self._create_provenance('market_cap', 0.90, True)
                ]
            )
            
        except Exception as e:
            return ProviderResult(
                success=False,
                data={},
                provenance=[],
                error=str(e)
            )
    
    def _symbol_to_id(self, symbol: str) -> str:
        """转换符号到ID"""
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple'
        }
        
        base = symbol.replace('-USD', '').replace('USD', '').upper()
        return mapping.get(base, base.lower())


class YFinanceQuoteProvider(BaseProvider):
    """YFinance 行情 Provider"""
    
    supported_markets = ['crypto', 'stock', 'forex']
    
    def __init__(self):
        super().__init__("YFinance")
    
    def fetch(self, symbol: str) -> ProviderResult:
        """获取行情数据"""
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return ProviderResult(
                    success=False,
                    data={},
                    provenance=[],
                    error='No data available'
                )
            
            return ProviderResult(
                success=True,
                data={
                    'price': info.get('regularMarketPrice', 0),
                    'change_24h': info.get('regularMarketChangePercent', 0),
                    'volume_24h': info.get('regularMarketVolume', 0),
                    'market_cap': info.get('marketCap', 0)
                },
                provenance=[
                    self._create_provenance('price', 0.90, False),
                    self._create_provenance('change_24h', 0.90, False),
                    self._create_provenance('volume_24h', 0.85, False),
                    self._create_provenance('market_cap', 0.85, False)
                ]
            )
            
        except Exception as e:
            return ProviderResult(
                success=False,
                data={},
                provenance=[],
                error=str(e)
            )


class OnchainProvider(BaseProvider):
    """链上数据 Provider"""
    
    def __init__(self):
        super().__init__("OnchainProvider")
        self.defillama = DeFiLlamaProvider()
    
    def fetch(self, chain: str = 'Ethereum') -> ProviderResult:
        """获取链上数据"""
        return self.defillama.fetch(chain)


class DeFiLlamaProvider(BaseProvider):
    """DeFiLlama Provider"""
    
    def __init__(self):
        super().__init__("DeFiLlama")
        self.base_url = "https://api.llama.fi"
    
    def fetch(self, chain: str) -> ProviderResult:
        """获取链级数据"""
        
        try:
            url = f"{self.base_url}/v2/chains"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code != 200:
                return ProviderResult(
                    success=False,
                    data={},
                    provenance=[],
                    error=f'API error: {resp.status_code}'
                )
            
            chains = resp.json()
            
            # 查找目标链
            target = None
            for c in chains:
                if c.get('name', '').lower() == chain.lower():
                    target = c
                    break
            
            if not target:
                return ProviderResult(
                    success=False,
                    data={},
                    provenance=[],
                    error=f'Chain not found: {chain}'
                )
            
            return ProviderResult(
                success=True,
                data={
                    'chain': target.get('name'),
                    'tvl': target.get('tvl', 0),
                    'tvl_change_1d': target.get('change_1d', 0),
                    'tvl_change_7d': target.get('change_7d', 0)
                },
                provenance=[
                    self._create_provenance('tvl', 0.95, True),
                    self._create_provenance('tvl_change_1d', 0.95, True),
                    self._create_provenance('tvl_change_7d', 0.95, True)
                ]
            )
            
        except Exception as e:
            return ProviderResult(
                success=False,
                data={},
                provenance=[],
                error=str(e)
            )


# ============ Provider 工厂 ============

class ProviderFactory:
    """Provider 工厂"""
    
    _providers = {
        'quote': QuoteProvider,
        'onchain': OnchainProvider
    }
    
    @classmethod
    def get(cls, provider_type: str) -> BaseProvider:
        """获取 Provider"""
        if provider_type not in cls._providers:
            raise ValueError(f'Unknown provider: {provider_type}')
        
        return cls._providers[provider_type]()


# ============ 便捷函数 ============

def get_quote(symbol: str, market: str = 'crypto') -> ProviderResult:
    """获取行情数据"""
    provider = ProviderFactory.get('quote')
    return provider.fetch(symbol, market)


def get_onchain(chain: str = 'Ethereum') -> ProviderResult:
    """获取链上数据"""
    provider = ProviderFactory.get('onchain')
    return provider.fetch(chain)


if __name__ == '__main__':
    print("Testing Providers...")
    print("=" * 60)
    
    # 测试行情
    print("\n[Quote Provider]")
    result = get_quote('BTC-USD', 'crypto')
    
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
    print(f"Provenance: {len(result.provenance)} fields")
    
    for p in result.provenance:
        print(f"  - {p.field}: {p.source} (confidence: {p.confidence:.2f})")
    
    # 测试链上
    print("\n[Onchain Provider]")
    result = get_onchain('Ethereum')
    
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")
    print(f"Provenance: {len(result.provenance)} fields")
    
    print("\n" + "=" * 60)
