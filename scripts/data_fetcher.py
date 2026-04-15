#!/usr/bin/env python3
"""
Data Fetcher - 整合多个数据源
- A 股/港股：agent-stock (东方财富) + akshare
- 美股：yfinance
"""

import sys
import os
import subprocess
import json

def get_quote(symbol):
    """获取实时行情"""
    symbol = str(symbol).upper()
    
    # 判断市场
    if symbol.startswith('6') or symbol.startswith('0') or symbol.startswith('3'):
        # A 股 - 使用 agent-stock
        return _get_quote_agent_stock(symbol)
    elif symbol.endswith('.HK') or (len(symbol) == 5 and symbol.isdigit()):
        # 港股
        return _get_quote_agent_stock(symbol)
    else:
        # 美股 - 使用 yfinance
        return _get_quote_yfinance(symbol)

def _get_quote_agent_stock(symbol):
    """使用 agent-stock 获取 A 股/港股行情"""
    try:
        # 清理股票代码
        clean_symbol = symbol.replace('.HK', '').replace('.SS', '').replace('.SZ', '')
        
        result = subprocess.run(
            ['python', '-m', 'stock', 'quote', clean_symbol],
            capture_output=True,
            text=True,
            cwd=r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\agent-stock',
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def _get_quote_yfinance(symbol):
    """使用 yfinance 获取美股行情"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        current = info.get('regularMarketPrice') or info.get('currentPrice')
        prev_close = info.get('regularMarketPreviousClose') or info.get('previousClose')
        
        if current is None:
            return f"未找到股票：{symbol}"
        
        change = current - prev_close
        pct_change = (change / prev_close) * 100 if prev_close else 0
        
        color = "green" if change >= 0 else "red"
        sign = "+" if change >= 0 else ""
        
        return f"""
┌────────────────────────────────┐
│  {info.get('longName', symbol)}
├────────────────────────────────┤
│  当前价：{current:,.2f} {info.get('currency', 'USD')}
│  涨跌：{sign}{change:,.2f} ({sign}{pct_change:.2f}%)
│  市值：{info.get('marketCap', 0)/1e9:,.1f}B
│  市盈率：{info.get('forwardPE', 'N/A')}
└────────────────────────────────┘
"""
    except Exception as e:
        return f"Error: {str(e)}"

def get_heatmap(market):
    """获取行业热力图"""
    try:
        result = subprocess.run(
            ['python', '-m', 'stock', 'heatmap', '--market', market],
            capture_output=True,
            text=True,
            cwd=r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\agent-stock',
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_fundflow(symbol):
    """获取资金流向"""
    try:
        clean_symbol = str(symbol).replace('.HK', '').replace('.SS', '').replace('.SZ', '')
        
        result = subprocess.run(
            ['python', '-m', 'stock', 'fundflow', clean_symbol],
            capture_output=True,
            text=True,
            cwd=r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\agent-stock',
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # 测试
    print("测试 A 股行情:")
    print(get_quote('600519'))
    
    print("\n测试美股行情:")
    print(get_quote('AAPL'))
    
    print("\n测试行业热力图:")
    print(get_heatmap('ab'))
