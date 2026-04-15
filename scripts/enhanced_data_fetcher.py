#!/usr/bin/env python3
"""
Enhanced Data Fetcher - 增强数据获取器
支持多数据源、自动重试、故障转移
"""

import time
import random
from typing import Optional, Dict, Any


class EnhancedDataFetcher:
    """增强数据获取器"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        self.sources = ['akshare', 'yfinance']
    
    def fetch_with_retry(self, func, *args, **kwargs) -> Optional[Any]:
        """
        带重试的数据获取
        
        Args:
            func: 数据获取函数
            *args, **kwargs: 函数参数
        
        Returns:
            数据或 None
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # 添加随机延迟避免并发冲突
                if attempt > 0:
                    delay = self.retry_delay * attempt + random.uniform(0.5, 1.5)
                    print(f"  重试 {attempt}/{self.max_retries} (等待 {delay:.1f}秒)...")
                    time.sleep(delay)
                
                result = func(*args, **kwargs)
                
                if result is not None:
                    return result
                
                print(f"  尝试 {attempt + 1}: 返回空值")
                
            except Exception as e:
                last_error = e
                print(f"  尝试 {attempt + 1}: 失败 - {str(e)[:100]}")
                
                # 如果是网络错误，等待后重试
                if 'Connection' in str(e) or 'Timeout' in str(e):
                    continue
                else:
                    # 其他错误直接返回
                    break
        
        if last_error:
            print(f"所有重试失败：{last_error}")
        return None
    
    def fetch_from_multiple_sources(self, symbol: str, data_type: str) -> Optional[Dict]:
        """
        从多个数据源获取数据
        
        Args:
            symbol: 股票代码
            data_type: 数据类型 (quote, fundamentals, etc.)
        
        Returns:
            数据字典或 None
        """
        print(f"正在获取 {symbol} 的{data_type}数据...")
        
        for source in self.sources:
            try:
                print(f"  尝试数据源：{source}")
                
                if source == 'akshare':
                    data = self._fetch_akshare(symbol, data_type)
                elif source == 'yfinance':
                    data = self._fetch_yfinance(symbol, data_type)
                else:
                    continue
                
                if data:
                    print(f"  ✓ {source} 成功")
                    return {'source': source, 'data': data}
                
            except Exception as e:
                print(f"  [FAIL] {source} 失败：{str(e)[:80]}")
                continue
        
        print(f"  所有数据源都失败")
        return None
    
    def _fetch_akshare(self, symbol: str, data_type: str) -> Optional[Dict]:
        """从 AkShare 获取数据"""
        try:
            import akshare as ak
            from symbol_utils import SymbolNormalizer
            
            clean_symbol = SymbolNormalizer.to_akshare_format(symbol)
            _, market = SymbolNormalizer.normalize(symbol)
            
            if data_type == 'quote':
                if market == 'CN':
                    df = ak.stock_zh_a_spot_em()
                    result = df[df['代码'] == clean_symbol]
                    if not result.empty:
                        return result.iloc[0].to_dict()
                elif market == 'HK':
                    df = ak.stock_hk_spot_em()
                    result = df[df['代码'] == clean_symbol]
                    if not result.empty:
                        return result.iloc[0].to_dict()
            
            elif data_type == 'history':
                if market == 'CN':
                    df = ak.stock_zh_a_hist(symbol=clean_symbol, period="6mo", adjust="qfq")
                    return {'history': df.to_dict('records'), 'count': len(df)}
            
            return None
            
        except Exception as e:
            raise Exception(f"AkShare 错误：{e}")
    
    def _fetch_yfinance(self, symbol: str, data_type: str) -> Optional[Dict]:
        """从 yfinance 获取数据"""
        try:
            import yfinance as yf
            from symbol_utils import SymbolNormalizer
            
            yf_symbol = SymbolNormalizer.to_yfinance_format(symbol)
            
            if data_type == 'quote':
                ticker = yf.Ticker(yf_symbol)
                info = ticker.info
                if info.get('regularMarketPrice') or info.get('currentPrice'):
                    return info
            
            elif data_type == 'history':
                ticker = yf.Ticker(yf_symbol)
                hist = ticker.history(period='6mo')
                if not hist.empty:
                    return {'history': hist.to_dict('records'), 'count': len(hist)}
            
            return None
            
        except Exception as e:
            raise Exception(f"yfinance 错误：{e}")


# 快捷函数
def get_quote_enhanced(symbol: str) -> Optional[Dict]:
    """增强版行情获取"""
    fetcher = EnhancedDataFetcher()
    result = fetcher.fetch_from_multiple_sources(symbol, 'quote')
    return result['data'] if result else None

def get_history_enhanced(symbol: str) -> Optional[Dict]:
    """增强版历史数据获取"""
    fetcher = EnhancedDataFetcher()
    result = fetcher.fetch_from_multiple_sources(symbol, 'history')
    return result['data'] if result else None


if __name__ == '__main__':
    """测试"""
    print("=" * 60)
    print("增强数据获取器测试")
    print("=" * 60)
    
    fetcher = EnhancedDataFetcher()
    
    # 测试 1: 歌尔股份
    print("\n[测试 1] 歌尔股份 (002241) 行情")
    result = fetcher.fetch_from_multiple_sources('002241', 'quote')
    if result:
        print(f"数据源：{result['source']}")
        print(f"成功获取数据")
    else:
        print("获取失败")
    
    # 测试 2: 腾讯控股
    print("\n[测试 2] 腾讯控股 (00700.HK) 行情")
    result = fetcher.fetch_from_multiple_sources('00700.HK', 'quote')
    if result:
        print(f"数据源：{result['source']}")
        print(f"成功获取数据")
    else:
        print("获取失败")
    
    # 测试 3: Apple
    print("\n[测试 3] Apple (AAPL) 行情")
    result = fetcher.fetch_from_multiple_sources('AAPL', 'quote')
    if result:
        print(f"数据源：{result['source']}")
        print(f"成功获取数据")
    else:
        print("获取失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
