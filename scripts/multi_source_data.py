#!/usr/bin/env python3
"""
Multi-Source Data Fetcher - 多数据源获取
支持 yfinance (主) + Alpha Vantage (备用)
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

# 尝试导入 yfinance
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    print("警告：yfinance 未安装")

# 尝试导入 requests (用于 Alpha Vantage)
try:
    import requests
    AV_AVAILABLE = True
except ImportError:
    AV_AVAILABLE = False
    print("警告：requests 未安装，Alpha Vantage 不可用")

# Alpha Vantage API Key (从环境变量读取)
ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')


class DataSourceError(Exception):
    """数据源异常"""
    pass


class MultiSourceData:
    """多数据源数据获取器"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.cache = {}
        self.cache_time = {}
        self.cache_ttl = 300  # 5 分钟缓存
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self.cache_time:
            return False
        age = time.time() - self.cache_time[key]
        return age < self.cache_ttl
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if self._is_cache_valid(key):
            return self.cache.get(key)
        return None
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self.cache[key] = data
        self.cache_time[key] = time.time()
    
    def get_quote_yfinance(self) -> Dict:
        """从 yfinance 获取行情"""
        if not YF_AVAILABLE:
            raise DataSourceError("yfinance 不可用")
        
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            current = info.get('regularMarketPrice') or info.get('currentPrice')
            if current is None:
                raise DataSourceError("无法获取当前价格")
            
            return {
                'source': 'yfinance',
                'symbol': self.symbol,
                'price': current,
                'currency': info.get('currency', 'USD'),
                'change': current - (info.get('regularMarketPreviousClose') or current),
                'change_percent': ((current - (info.get('regularMarketPreviousClose') or current)) / 
                                   (info.get('regularMarketPreviousClose') or current) * 100),
                'market_cap': info.get('marketCap'),
                'volume': info.get('volume'),
                'pe_ratio': info.get('forwardPE'),
                'high_52w': info.get('fiftyTwoWeekHigh'),
                'low_52w': info.get('fiftyTwoWeekLow'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise DataSourceError(f"yfinance 错误：{e}")
    
    def get_quote_alphavantage(self) -> Dict:
        """从 Alpha Vantage 获取行情"""
        if not AV_AVAILABLE:
            raise DataSourceError("requests 不可用")
        
        try:
            # GLOBAL_QUOTE endpoint
            url = f'https://www.alphavantage.co/query'
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': self.symbol,
                'apikey': ALPHA_VANTAGE_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' not in data:
                if 'Note' in data:
                    raise DataSourceError("API 调用频率限制")
                raise DataSourceError("无法获取数据")
            
            quote = data['Global Quote']
            price = float(quote.get('05. price', 0))
            
            return {
                'source': 'alphavantage',
                'symbol': self.symbol,
                'price': price,
                'currency': 'USD',
                'change': float(quote.get('09. change', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                'volume': int(quote.get('06. volume', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'open': float(quote.get('02. open', 0)),
                'previous_close': float(quote.get('07. previous close', 0)),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise DataSourceError(f"Alpha Vantage 错误：{e}")
    
    def get_quote(self, use_cache: bool = True) -> Dict:
        """
        获取行情 - 自动选择数据源
        
        Args:
            use_cache: 是否使用缓存
        
        Returns:
            行情数据字典
        """
        cache_key = f'quote_{self.symbol}'
        
        # 尝试从缓存获取
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                cached['cached'] = True
                return cached
        
        # 尝试主数据源 (yfinance)
        try:
            data = self.get_quote_yfinance()
            data['cached'] = False
            if use_cache:
                self._set_cache(cache_key, data)
            return data
        except DataSourceError as e:
            print(f"主数据源失败：{e}")
        
        # 尝试备用数据源 (Alpha Vantage)
        try:
            data = self.get_quote_alphavantage()
            data['cached'] = False
            if use_cache:
                self._set_cache(cache_key, data)
            return data
        except DataSourceError as e:
            print(f"备用数据源失败：{e}")
        
        raise DataSourceError("所有数据源都不可用")
    
    def get_historical_yfinance(self, period: str = '6mo') -> Optional[Any]:
        """从 yfinance 获取历史数据"""
        if not YF_AVAILABLE:
            return None
        
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception:
            return None
    
    def get_historical(self, period: str = '6mo') -> Optional[Any]:
        """获取历史数据 - 自动选择数据源"""
        cache_key = f'historical_{self.symbol}_{period}'
        
        if self._is_cache_valid(cache_key):
            return self._get_from_cache(cache_key)
        
        # 优先使用 yfinance
        data = self.get_historical_yfinance(period)
        if data is not None:
            self._set_cache(cache_key, data)
            return data
        
        return None
    
    def validate_data(self, data: Dict) -> Dict:
        """
        验证数据质量
        
        检查项:
        - 价格是否为正数
        - 涨跌幅是否合理 (< 50%)
        - 数据是否过期 (> 1 天)
        """
        issues = []
        
        # 检查价格
        if data.get('price', 0) <= 0:
            issues.append("价格无效")
        
        # 检查涨跌幅
        change_pct = abs(data.get('change_percent', 0))
        if change_pct > 50:
            issues.append(f"涨跌幅异常：{change_pct:.1f}%")
        
        # 检查时间戳
        if 'timestamp' in data:
            try:
                ts = datetime.fromisoformat(data['timestamp'])
                age_hours = (datetime.now() - ts).total_seconds() / 3600
                if age_hours > 24:
                    issues.append(f"数据过期：{age_hours:.1f}小时前")
            except:
                pass
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data': data
        }


def compare_sources(symbol: str) -> Dict:
    """
    对比多个数据源的数据
    
    Returns:
        包含各数据源数据和差异分析
    """
    result = {
        'symbol': symbol,
        'timestamp': datetime.now().isoformat(),
        'sources': {},
        'comparison': {}
    }
    
    msd = MultiSourceData(symbol)
    
    # yfinance
    try:
        yf_data = msd.get_quote_yfinance()
        result['sources']['yfinance'] = yf_data
    except Exception as e:
        result['sources']['yfinance'] = {'error': str(e)}
    
    # Alpha Vantage
    try:
        av_data = msd.get_quote_alphavantage()
        result['sources']['alphavantage'] = av_data
    except Exception as e:
        result['sources']['alphavantage'] = {'error': str(e)}
    
    # 对比分析
    if 'yfinance' in result['sources'] and 'alphavantage' in result['sources']:
        yf = result['sources']['yfinance']
        av = result['sources']['alphavantage']
        
        if 'error' not in yf and 'error' not in av:
            price_diff = abs(yf['price'] - av['price'])
            price_diff_pct = (price_diff / yf['price'] * 100) if yf['price'] else 0
            
            result['comparison'] = {
                'price_difference': price_diff,
                'price_difference_pct': round(price_diff_pct, 2),
                'data_quality': 'good' if price_diff_pct < 1 else 'warning'
            }
    
    return result


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python multi_source_data.py <股票代码> [compare|quote]")
        print("示例：python multi_source_data.py AAPL compare")
        sys.exit(1)
    
    symbol = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else 'quote'
    
    msd = MultiSourceData(symbol)
    
    if action == 'compare':
        print(f"对比数据源：{symbol}")
        print("=" * 60)
        result = compare_sources(symbol)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"获取行情：{symbol}")
        print("=" * 60)
        data = msd.get_quote()
        print(f"数据源：{data['source']}")
        print(f"价格：{data['price']} {data.get('currency', 'USD')}")
        print(f"涨跌：{data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        # 验证数据质量
        validation = msd.validate_data(data)
        if validation['valid']:
            print("数据质量：✅ 验证通过")
        else:
            print(f"数据质量：⚠️ {', '.join(validation['issues'])}")
