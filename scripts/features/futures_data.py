#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合约数据获取模块 (CCXT)
获取 Funding Rate, Long/Short Ratio, Open Interest
"""

import sys
import os
from typing import Dict, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class FuturesDataFetcher:
    """合约数据获取器"""
    
    def __init__(self):
        self.cache = {}
    
    def fetch_futures_data(self, symbol: str) -> Dict:
        """
        获取合约数据
        
        Args:
            symbol: 交易对 (BTC-USD -> BTC/USDT:USDT)
            
        Returns:
            合约数据字典
        """
        result = {
            'symbol': symbol,
            'funding_rate': None,
            'long_short_ratio': None,
            'open_interest': None,
            'data_source': 'CCXT (Binance)',
            'error': None
        }
        
        try:
            import ccxt
            
            # 转换符号格式: BTC-USD -> BTC/USDT:USDT
            base = symbol.split('-')[0]
            ccxt_symbol = f"{base}/USDT:USDT"
            
            # 使用 Binance
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'
                }
            })
            
            # 1. Funding Rate
            try:
                funding = exchange.fetch_funding_rate(ccxt_symbol)
                result['funding_rate'] = funding.get('fundingRate', 0) * 100  # 转为百分比
                result['funding_timestamp'] = funding.get('timestamp')
            except Exception as e:
                print(f"⚠️ Funding Rate 获取失败: {e}")
            
            # 2. Long/Short Ratio (部分交易所支持)
            try:
                # Binance 需要特殊API
                # 简化版: 使用 ticker 信息推算
                ticker = exchange.fetch_ticker(ccxt_symbol)
                result['ticker_price'] = ticker.get('last')
            except Exception as e:
                print(f"⚠️ Ticker 获取失败: {e}")
            
            result['data_source'] = 'CCXT (Binance Public API)'
            
        except ImportError:
            result['error'] = "需要安装 ccxt: pip install ccxt"
        except Exception as e:
            result['error'] = str(e)
        
        return result


def get_futures_data(symbol: str) -> Dict:
    """
    便捷函数：获取合约数据
    
    Args:
        symbol: 交易对
        
    Returns:
        合约数据
    """
    fetcher = FuturesDataFetcher()
    return fetcher.fetch_futures_data(symbol)


if __name__ == '__main__':
    print("测试合约数据获取...")
    print("=" * 60)
    
    result = get_futures_data('BTC-USD')
    
    print(f"Symbol: {result['symbol']}")
    print(f"Funding Rate: {result['funding_rate']}%")
    print(f"Data Source: {result['data_source']}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    
    print("=" * 60)
