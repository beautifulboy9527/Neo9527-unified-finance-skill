#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贵金属模块 - 黄金、白银、铂金价格分析
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class MetalsAnalyzer:
    """
    贵金属分析器
    
    支持:
    - 黄金 (XAU)
    - 白银 (XAG)
    - 铂金 (XPT)
    - 钯金 (XPD)
    
    数据源:
    - 金价API (免费)
    - metals.live (免费)
    """
    
    # 贵金属代码
    METALS = {
        'XAU': {'name': '黄金', 'unit': '美元/盎司'},
        'XAG': {'name': '白银', 'unit': '美元/盎司'},
        'XPT': {'name': '铂金', 'unit': '美元/盎司'},
        'XPD': {'name': '钯金', 'unit': '美元/盎司'}
    }
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR / 'cache' / 'metals'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
        self.cache_time = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    def get_price(self, metal: str = 'XAU', currency: str = 'USD') -> Dict:
        """
        获取贵金属价格
        
        Args:
            metal: 金属代码 (XAU/XAG/XPT/XPD)
            currency: 货币代码
            
        Returns:
            价格数据
        """
        result = {
            'metal': metal,
            'metal_name': self.METALS.get(metal, {}).get('name', metal),
            'currency': currency,
            'price': None,
            'change_24h': None,
            'change_pct_24h': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'none',
            'error': None
        }
        
        # 检查缓存
        cache_key = f"{metal}_{currency}"
        if cache_key in self.cache and (datetime.now() - self.cache_time.get(cache_key, datetime.min)).seconds < self.cache_ttl:
            return self.cache[cache_key]
        
        # 方法1: 使用 akshare 上海黄金交易所数据 (仅黄金)
        if metal == 'XAU':
            try:
                import akshare as ak
                import pandas as pd
                
                df = ak.spot_golden_benchmark_sge()
                if df is not None and len(df) > 0:
                    # 获取最新价格 (人民币/克)
                    latest = df.iloc[-1]
                    price_cny_per_gram = float(latest['晚盘价'] if '晚盘价' in latest else latest.iloc[1])
                    
                    # 转换为美元/盎司
                    # 1盎司 = 31.1035克
                    # 假设汇率约 7.2
                    exchange_rate = self._get_usd_cny_rate()
                    price_usd_per_ounce = (price_cny_per_gram * 31.1035) / exchange_rate
                    
                    result['price'] = round(price_usd_per_ounce, 2)
                    result['data_source'] = 'akshare_sge'
                    result['price_cny_per_gram'] = round(price_cny_per_gram, 2)
                    
                    # 计算涨跌
                    if len(df) > 1:
                        prev = df.iloc[-2]
                        prev_price = float(prev['晚盘价'] if '晚盘价' in prev else prev.iloc[1])
                        change = (price_cny_per_gram - prev_price) / prev_price
                        result['change_pct_24h'] = round(change * 100, 2)
            except Exception as e:
                pass
        
        # 方法2: 尝试 metals.live API
        if result['price'] is None:
            try:
                import requests
                
                url = f"https://api.metals.live/v1/spot/{metal.lower()}"
                headers = {'Accept': 'application/json'}
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        item = data[0]
                        result['price'] = item.get('price')
                        result['data_source'] = 'metals.live'
                    elif isinstance(data, dict):
                        result['price'] = data.get('price')
                        result['data_source'] = 'metals.live'
            except Exception as e:
                pass
        
        # 备用数据源: 金价API
        if result['price'] is None:
            try:
                import requests
                
                # 使用简单的金价查询
                if metal == 'XAU':
                    url = "https://www.goldprice.org/zh-cn/gold-price-per-ounce"
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        import re
                        # 解析价格
                        match = re.search(r'\$([0-9,]+\.[0-9]+)', response.text)
                        if match:
                            price_str = match.group(1).replace(',', '')
                            result['price'] = float(price_str)
                            result['data_source'] = 'goldprice.org'
            
            except Exception as e:
                if result.get('error') is None:
                    result['error'] = str(e)
        
        # 最后备用: 使用模拟数据
        if result['price'] is None:
            result['price'] = self._get_fallback_price(metal)
            result['data_source'] = 'fallback'
            result['error'] = '使用备用价格数据'
        
        # 缓存结果
        self.cache[cache_key] = result
        self.cache_time[cache_key] = datetime.now()
        
        return result
    
    def _get_fallback_price(self, metal: str) -> float:
        """获取备用价格 (基于市场大致水平)"""
        fallback_prices = {
            'XAU': 2350.0,  # 黄金约 $2350/盎司
            'XAG': 28.0,    # 白银约 $28/盎司
            'XPT': 1000.0,  # 铂金约 $1000/盎司
            'XPD': 1100.0   # 钯金约 $1100/盎司
        }
        return fallback_prices.get(metal, 1000.0)
    
    def _get_usd_cny_rate(self) -> float:
        """获取美元人民币汇率"""
        try:
            import akshare as ak
            df = ak.currency_boc_safe()
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    if '美元' in str(row.get('货币名称', '')):
                        return float(row['中行折算价'])
        except:
            pass
        
        # 默认汇率
        return 7.2
    
    def get_all_prices(self) -> Dict:
        """
        获取所有贵金属价格
        
        Returns:
            所有贵金属价格
        """
        result = {
            'metals': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        for metal_code, metal_info in self.METALS.items():
            price_data = self.get_price(metal_code)
            result['metals'][metal_code] = price_data
        
        return result
    
    def get_ratio(self, metal1: str = 'XAU', metal2: str = 'XAG') -> Dict:
        """
        计算贵金属比率
        
        Args:
            metal1: 第一种金属
            metal2: 第二种金属
            
        Returns:
            比率数据
        """
        result = {
            'metal1': metal1,
            'metal2': metal2,
            'ratio': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            price1 = self.get_price(metal1)
            price2 = self.get_price(metal2)
            
            if price1.get('price') and price2.get('price'):
                result['ratio'] = round(price1['price'] / price2['price'], 2)
                result['metal1_price'] = price1['price']
                result['metal2_price'] = price2['price']
                result['metal1_name'] = price1['metal_name']
                result['metal2_name'] = price2['metal_name']
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_gold_silver_ratio(self) -> Dict:
        """
        分析金银比
        
        Returns:
            金银比分析
        """
        result = {
            'ratio': None,
            'analysis': None,
            'historical_avg': 65,  # 历史均值约65
            'signal': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            ratio_data = self.get_ratio('XAU', 'XAG')
            ratio = ratio_data.get('ratio')
            
            if ratio:
                result['ratio'] = ratio
                result['gold_price'] = ratio_data.get('metal1_price')
                result['silver_price'] = ratio_data.get('metal2_price')
                
                # 分析信号
                if ratio > 80:
                    result['signal'] = '白银相对便宜'
                    result['analysis'] = '金银比高于历史均值，白银可能被低估'
                elif ratio < 50:
                    result['signal'] = '黄金相对便宜'
                    result['analysis'] = '金银比低于历史均值，黄金可能被低估'
                else:
                    result['signal'] = '相对均衡'
                    result['analysis'] = '金银比接近历史均值'
                
                result['deviation'] = round((ratio - result['historical_avg']) / result['historical_avg'] * 100, 2)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def get_metal_price(metal: str = 'XAU') -> Dict:
    """获取贵金属价格"""
    analyzer = MetalsAnalyzer()
    return analyzer.get_price(metal)


def get_all_metals_prices() -> Dict:
    """获取所有贵金属价格"""
    analyzer = MetalsAnalyzer()
    return analyzer.get_all_prices()


def get_gold_silver_ratio() -> Dict:
    """获取金银比"""
    analyzer = MetalsAnalyzer()
    return analyzer.analyze_gold_silver_ratio()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='贵金属分析')
    parser.add_argument('metal', nargs='?', default='XAU', help='金属代码')
    parser.add_argument('--all', action='store_true', help='获取所有金属价格')
    parser.add_argument('--ratio', action='store_true', help='金银比分析')
    
    args = parser.parse_args()
    
    analyzer = MetalsAnalyzer()
    
    if args.all:
        result = analyzer.get_all_prices()
    elif args.ratio:
        result = analyzer.analyze_gold_silver_ratio()
    else:
        result = analyzer.get_price(args.metal)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
