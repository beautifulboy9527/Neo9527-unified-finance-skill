#!/usr/bin/env python3
"""
Chart Generator - 统一图表生成器
美股：stock-market-pro (yfinance)
A 股/港股：akshare_chart
"""

import sys
import os
import subprocess

# stock-market-pro 脚本路径
STOCK_MARKET_PRO_SCRIPT = r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\stock-market-pro\scripts\yf.py'
AKSHARE_CHART_SCRIPT = os.path.join(os.path.dirname(__file__), 'akshare_chart.py')

def _is_a_share(symbol):
    """判断是否为 A 股"""
    sym = str(symbol).upper()
    return sym.isdigit() or sym.endswith('.SS') or sym.endswith('.SZ')

def _is_hk_share(symbol):
    """判断是否为港股"""
    return str(symbol).endswith('.HK')

def _is_us_stock(symbol):
    """判断是否为美股"""
    return not _is_a_share(symbol) and not _is_hk_share(symbol)

def generate_chart(symbol, period='3mo', indicators=None):
    """
    生成带技术指标的图表 - 自动选择数据源
    
    Args:
        symbol: 股票代码
        period: 时间周期
        indicators: 指标字典 {'rsi': True, 'macd': True, 'bb': True}
    
    Returns:
        图表文件路径
    """
    indicators = indicators or {'rsi': True, 'macd': True, 'bb': True}
    
    # 根据市场选择数据源
    if _is_a_share(symbol) or _is_hk_share(symbol):
        return _generate_akshare_chart(symbol, period, indicators)
    else:
        return _generate_yf_chart(symbol, period, indicators)

def _generate_akshare_chart(symbol, period='3mo', indicators=None):
    """使用 AkShare 生成 A 股/港股图表"""
    cmd = ['python', AKSHARE_CHART_SCRIPT, symbol, period]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90
        )
        
        if result.returncode == 0:
            # 解析输出获取图表路径
            for line in result.stdout.split('\n'):
                if '图表已保存' in line or '图表路径' in line:
                    if ':' in line:
                        return line.split(':')[-1].strip()
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def _generate_yf_chart(symbol, period='3mo', indicators=None):
    """使用 yfinance 生成美股图表"""
    cmd = ['python', STOCK_MARKET_PRO_SCRIPT, 'pro', symbol, period]
    
    if indicators.get('rsi'): cmd.append('--rsi')
    if indicators.get('macd'): cmd.append('--macd')
    if indicators.get('bb'): cmd.append('--bb')
    if indicators.get('vwap'): cmd.append('--vwap')
    if indicators.get('atr'): cmd.append('--atr')
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('CHART_PATH:'):
                    return line.replace('CHART_PATH:', '').strip()
            return "图表生成成功，但未返回路径"
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_report(symbol, period='6mo'):
    """
    生成一键分析报告 (文本摘要 + 图表)
    仅支持美股 (yfinance)
    """
    cmd = ['python', STOCK_MARKET_PRO_SCRIPT, 'report', symbol, period]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(result.stdout)
            for line in result.stdout.split('\n'):
                if line.startswith('CHART_PATH:'):
                    chart_path = line.replace('CHART_PATH:', '').strip()
                    print(f"\n图表已保存：{chart_path}")
                    break
        else:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    print("=" * 60)
    print("图表生成器测试")
    print("=" * 60)
    
    # 测试 A 股
    print("\n[测试 1] A 股图表 (600519):")
    path = generate_chart('600519', '3mo', {'rsi': True, 'macd': True, 'bb': True})
    print(f"结果：{path}")
    
    # 测试港股
    print("\n[测试 2] 港股图表 (00700.HK):")
    path = generate_chart('00700.HK', '3mo', {'rsi': True, 'macd': True})
    print(f"结果：{path}")
    
    # 测试美股
    print("\n[测试 3] 美股图表 (AAPL):")
    path = generate_chart('AAPL', '3mo', {'rsi': True, 'macd': True, 'bb': True})
    print(f"结果：{path}")
