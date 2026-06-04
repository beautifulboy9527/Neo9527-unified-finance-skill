#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一行情查询模块 - 整合 agent-stock + akshare + yfinance
取长补短，按市场自动路由到最佳数据源
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 导入缓存装饰器
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from features.cache_layer import cache_quote


def detect_market(symbol: str) -> str:
    """
    检测市场类型
    
    Returns:
        'cn': A股
        'hk': 港股
        'us': 美股
    """
    symbol = str(symbol).upper()
    
    # A股判断
    if symbol.startswith(('6', '0', '3', '688', '300')):
        if '.' not in symbol or symbol.endswith(('.SS', '.SZ')):
            return 'cn'
    
    # 港股判断
    if symbol.endswith('.HK') or (symbol.isdigit() and len(symbol) == 5):
        return 'hk'
    
    # 默认美股
    return 'us'


def quote_cn(symbol: str) -> Dict:
    """
    A股行情查询 (agent-stock 优先，akshare 备选)
    """
    result = {
        'symbol': symbol,
        'market': 'cn',
        'data_source': 'none',
        'update_time': None,
        'error': None
    }
    
    # 尝试数据源1: agent-stock (快速)
    try:
        import subprocess
        
        proc = subprocess.run(
            ['python', '-m', 'stock', 'quote', symbol],
            capture_output=True,
            text=True,
            cwd=r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\agent-stock',
            timeout=30
        )
        
        if proc.returncode == 0:
            output = proc.stdout
            
            # 解析输出
            import re
            name_match = re.search(r'名称:\s*(\S+)', output)
            price_match = re.search(r'价格:\s*([\d.]+)', output)
            change_match = re.search(r'涨跌幅:\s*([\d.-]+)%', output)
            pe_match = re.search(r'市盈率:\s*([\d.]+)', output)
            pb_match = re.search(r'市净率:\s*([\d.]+)', output)
            cap_match = re.search(r'总市值:\s*([\d.]+)亿', output)
            
            result.update({
                'name': name_match.group(1) if name_match else symbol,
                'price': float(price_match.group(1)) if price_match else None,
                'change_pct': float(change_match.group(1)) if change_match else None,
                'pe': float(pe_match.group(1)) if pe_match else None,
                'pb': float(pb_match.group(1)) if pb_match else None,
                'market_cap': float(cap_match.group(1)) if cap_match else None,
                'data_source': 'agent-stock',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return result
            
    except Exception as e:
        result['error'] = f'agent-stock失败: {str(e)}'
    
    # 尝试数据源2: akshare (全面)
    try:
        import akshare as ak
        
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == symbol]
        
        if len(stock) > 0:
            row = stock.iloc[0]
            result.update({
                'name': str(row.get('名称', symbol)),
                'price': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
                'pe': float(row.get('市盈率-动态', 0)) if row.get('市盈率-动态') else None,
                'pb': float(row.get('市净率', 0)) if row.get('市净率') else None,
                'market_cap': float(row.get('总市值', 0)) / 1e8 if row.get('总市值') else None,
                'volume': int(row.get('成交量', 0)),
                'turnover': float(row.get('换手率', 0)),
                'data_source': 'akshare',
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return result
            
    except Exception as e:
        if result.get('error'):
            result['error'] += f'; akshare失败: {str(e)}'
        else:
            result['error'] = f'akshare失败: {str(e)}'
    
    return result


def quote_hk(symbol: str) -> Dict:
    """
    港股行情查询 (yfinance)
    """
    result = {
        'symbol': symbol,
        'market': 'hk',
        'data_source': 'none',
        'update_time': None,
        'error': None
    }
    
    try:
        import yfinance as yf
        
        # 确保格式正确
        if not symbol.endswith('.HK'):
            symbol = symbol.zfill(5) + '.HK'
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        result.update({
            'name': info.get('longName') or info.get('shortName', symbol),
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'change_pct': info.get('regularMarketChangePercent'),
            'pe': info.get('trailingPE'),
            'pb': info.get('priceToBook'),
            'market_cap': info.get('marketCap', 0) / 1e8 if info.get('marketCap') else None,
            'volume': info.get('regularMarketVolume'),
            'data_source': 'yfinance',
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def quote_us(symbol: str) -> Dict:
    """
    美股行情查询 (yfinance)
    """
    result = {
        'symbol': symbol,
        'market': 'us',
        'data_source': 'none',
        'update_time': None,
        'error': None
    }
    
    try:
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        result.update({
            'name': info.get('longName') or info.get('shortName', symbol),
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'change_pct': info.get('regularMarketChangePercent'),
            'pe': info.get('trailingPE'),
            'pb': info.get('priceToBook'),
            'market_cap': info.get('marketCap', 0) / 1e8 if info.get('marketCap') else None,
            'volume': info.get('regularMarketVolume'),
            'beta': info.get('beta'),
            'dividend_yield': info.get('dividendYield'),
            'data_source': 'yfinance',
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def get_quote(symbol: str) -> Dict:
    """
    统一行情查询接口 - 自动路由到最佳数据源
    
    Args:
        symbol: 股票代码
        
    Returns:
        {
            'symbol': '股票代码',
            'market': '市场类型',
            'name': '股票名称',
            'price': 当前价格,
            'change_pct': 涨跌幅(%),
            'pe': 市盈率,
            'pb': 市净率,
            'market_cap': 市值(亿),
            'data_source': '数据源',
            'update_time': '更新时间'
        }
    """
    market = detect_market(symbol)
    
    if market == 'cn':
        return quote_cn(symbol)
    elif market == 'hk':
        return quote_hk(symbol)
    else:
        return quote_us(symbol)


def get_quotes(symbols: list) -> Dict[str, Dict]:
    """
    批量行情查询
    
    Args:
        symbols: 股票代码列表
        
    Returns:
        {symbol: quote_result}
    """
    results = {}
    for symbol in symbols:
        results[symbol] = get_quote(symbol)
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='统一行情查询')
    parser.add_argument('--symbol', required=True, help='股票代码')
    parser.add_argument('--batch', nargs='+', help='批量查询')
    
    args = parser.parse_args()
    
    if args.batch:
        result = get_quotes(args.batch)
    else:
        result = get_quote(args.symbol)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
