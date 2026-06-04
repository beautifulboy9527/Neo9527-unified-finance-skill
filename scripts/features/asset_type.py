#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产类型识别模块
智能识别股票/加密货币/港股/美股，并选择合适的数据源和分析逻辑
"""

import sys
import re
from typing import Dict, List

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# 加密货币列表
CRYPTO_SYMBOLS = {
    # 主流币
    'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT', 'MATIC', 'LTC',
    'SHIB', 'AVAX', 'LINK', 'ATOM', 'UNI', 'XMR', 'ETC', 'XLM', 'BCH', 'ALGO',
    # DeFi
    'AAVE', 'COMP', 'MKR', 'SUSHI', 'CRV', 'YFI', 'SNX',
    # Layer2
    'ARB', 'OP', 'IMX', 'MNT',
    # 稳定币
    'USDT', 'USDC', 'DAI', 'BUSD',
}

# 港股代码特征
HK_PATTERNS = [
    r'^\d{4,5}\.HK$',  # 00700.HK, 09988.HK
    r'^\d{5}$',        # 5位数字（无后缀时可能是港股）
]

# A股代码特征
CN_PATTERNS = [
    r'^[036]\d{5}$',   # 6位数字，0/3/6开头
    r'^\d{6}\.(SS|SZ)$', # 带后缀
]


def detect_asset_type(symbol: str) -> Dict:
    """
    智能识别资产类型
    
    Args:
        symbol: 资产代码
        
    Returns:
        {
            'type': 'crypto' | 'stock_cn' | 'stock_hk' | 'stock_us',
            'market': 'crypto' | 'cn' | 'hk' | 'us',
            'symbol_normalized': 标准化后的代码,
            'data_sources': 推荐的数据源列表,
            'features': 可用的分析功能列表
        }
    """
    symbol_upper = symbol.upper().strip()
    
    # 1. 加密货币识别
    # 格式: BTC-USD, ETH-USD, BTCUSDT, 或纯 BTC
    base_symbol = symbol_upper.split('-')[0].replace('USDT', '').replace('USDC', '')
    
    if base_symbol in CRYPTO_SYMBOLS or symbol_upper.endswith(('-USD', '-USDT', '-USDC', '-EUR')):
        return {
            'type': 'crypto',
            'market': 'crypto',
            'symbol_normalized': symbol_upper,
            'data_sources': ['yfinance', 'coingecko', 'binance'],
            'features': ['technical', 'signals', 'onchain', 'sentiment'],
            'limitations': [
                '无传统财务报表',
                '不适用ROE/负债率等指标',
                '建议使用链上数据分析'
            ]
        }
    
    # 2. A股识别
    # 格式: 002241, 002241.SZ, 600519.SS
    for pattern in CN_PATTERNS:
        if re.match(pattern, symbol_upper):
            return {
                'type': 'stock_cn',
                'market': 'cn',
                'symbol_normalized': _normalize_cn_symbol(symbol_upper),
                'data_sources': ['akshare', 'eastmoney', 'yfinance'],
                'features': ['fundamental', 'technical', 'signals', 'fundflow', 'valuation'],
                'limitations': []
            }
    
    # 3. 港股识别
    # 格式: 00700.HK, 09988.HK
    for pattern in HK_PATTERNS:
        if re.match(pattern, symbol_upper):
            return {
                'type': 'stock_hk',
                'market': 'hk',
                'symbol_normalized': symbol_upper,
                'data_sources': ['yfinance', 'akshare'],
                'features': ['fundamental', 'technical', 'signals'],
                'limitations': ['港股数据源较少']
            }
    
    # 4. 美股识别 (默认)
    # 格式: AAPL, MSFT, GOOGL
    if re.match(r'^[A-Z]{1,5}$', symbol_upper):
        return {
            'type': 'stock_us',
            'market': 'us',
            'symbol_normalized': symbol_upper,
            'data_sources': ['yfinance', 'financetoolkit', 'fmp'],
            'features': ['fundamental', 'technical', 'signals', 'valuation'],
            'limitations': []
        }
    
    # 5. 未知类型，按美股处理
    return {
        'type': 'stock_us',
        'market': 'us',
        'symbol_normalized': symbol_upper,
        'data_sources': ['yfinance'],
        'features': ['technical', 'signals'],
        'limitations': ['资产类型未知，功能可能受限']
    }


def _normalize_cn_symbol(symbol: str) -> str:
    """
    标准化A股代码
    
    Args:
        symbol: 原始代码
        
    Returns:
        标准化后的代码 (带后缀)
    """
    symbol = symbol.upper()
    
    # 已有后缀
    if symbol.endswith(('.SS', '.SZ')):
        return symbol
    
    # 纯数字，添加后缀
    if symbol.isdigit() and len(symbol) == 6:
        if symbol.startswith('6'):
            return f"{symbol}.SS"  # 上海
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"  # 深圳
    
    return symbol


def get_analysis_config(asset_type: str) -> Dict:
    """
    获取不同资产类型的分析配置
    
    Args:
        asset_type: 资产类型
        
    Returns:
        分析配置（权重、指标等）
    """
    configs = {
        'crypto': {
            'weights': {
                'technical': 0.50,      # 技术面权重高
                'signals': 0.25,        # 信号权重
                'onchain': 0.15,        # 链上数据
                'sentiment': 0.10       # 市场情绪
            },
            'radar_dimensions': [
                '技术面', '信号强度', '链上活跃度', 
                '市场情绪', '流动性'
            ],
            'technical_params': {
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'atr_multiplier': 3.0,  # 加密货币波动大
            },
            'skip_modules': ['financetoolkit', 'fundflow', 'valuation'],
            'risk_warning': '加密货币波动率极高，建议小仓位+严格止损'
        },
        
        'stock_cn': {
            'weights': {
                'fundamental': 0.30,
                'technical': 0.35,
                'signals': 0.20,
                'valuation': 0.15
            },
            'radar_dimensions': [
                '基本面', '技术面', '信号验证', 
                '估值水平', '资金流向'
            ],
            'technical_params': {
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'atr_multiplier': 2.0,
            },
            'skip_modules': [],
            'risk_warning': None
        },
        
        'stock_hk': {
            'weights': {
                'fundamental': 0.30,
                'technical': 0.40,
                'signals': 0.20,
                'valuation': 0.10
            },
            'radar_dimensions': [
                '基本面', '技术面', '信号验证', 
                '估值水平', '流动性'
            ],
            'technical_params': {
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'atr_multiplier': 2.0,
            },
            'skip_modules': ['fundflow'],
            'risk_warning': None
        },
        
        'stock_us': {
            'weights': {
                'fundamental': 0.35,
                'technical': 0.35,
                'signals': 0.20,
                'valuation': 0.10
            },
            'radar_dimensions': [
                '基本面', '技术面', '信号验证', 
                '估值水平', '成长性'
            ],
            'technical_params': {
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'atr_multiplier': 2.0,
            },
            'skip_modules': ['fundflow'],
            'risk_warning': None
        }
    }
    
    return configs.get(asset_type, configs['stock_us'])


if __name__ == '__main__':
    # 测试
    test_symbols = [
        'BTC-USD',
        'ETH-USD',
        '002241',
        '600519.SS',
        '00700.HK',
        'AAPL',
        'MSFT'
    ]
    
    print("=" * 60)
    print("资产类型识别测试")
    print("=" * 60)
    
    for symbol in test_symbols:
        result = detect_asset_type(symbol)
        print(f"\n{symbol}:")
        print(f"  类型: {result['type']}")
        print(f"  市场: {result['market']}")
        print(f"  标准化: {result['symbol_normalized']}")
        print(f"  数据源: {result['data_sources']}")
        print(f"  可用功能: {result['features']}")
        if result['limitations']:
            print(f"  ⚠️ 限制: {result['limitations']}")
