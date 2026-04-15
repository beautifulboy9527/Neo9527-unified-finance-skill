#!/usr/bin/env python3
"""
Symbol Utils - 股票代码标准化工具
统一股票代码格式，自动识别市场
"""

import re
from typing import Tuple, Optional


class SymbolNormalizer:
    """股票代码标准化器"""
    
    @staticmethod
    def normalize(symbol: str) -> Tuple[str, str]:
        """
        统一股票代码格式
        
        Args:
            symbol: 原始股票代码
        
        Returns:
            (normalized_symbol, market)
            market: CN (A 股), HK (港股), US (美股), UNKNOWN
        """
        if not symbol:
            return "", "UNKNOWN"
        
        symbol = str(symbol).upper().strip()
        
        # A 股识别：6 位数字
        if re.match(r'^[0-9]{6}$', symbol):
            if symbol.startswith('6'):
                return f"{symbol}.SS", "CN"
            elif symbol.startswith(('0', '3')):
                return f"{symbol}.SZ", "CN"
            else:
                return f"{symbol}.SS", "CN"  # 默认沪市
        
        # 港股识别：5 位数字 + .HK
        if re.match(r'^[0-9]{5}\.HK$', symbol):
            return symbol, "HK"
        if re.match(r'^[0-9]{5}$', symbol):
            return f"{symbol}.HK", "HK"
        
        # 美股识别：纯字母
        if re.match(r'^[A-Z]{1,5}$', symbol):
            return symbol, "US"
        
        # 已标准化格式
        if symbol.endswith('.SS'):
            return symbol, "CN"
        if symbol.endswith('.SZ'):
            return symbol, "CN"
        if symbol.endswith('.HK'):
            return symbol, "HK"
        
        return symbol, "UNKNOWN"
    
    @staticmethod
    def to_akshare_format(symbol: str) -> str:
        """
        转换为 AkShare 格式 (去掉后缀)
        
        Args:
            symbol: 股票代码
        
        Returns:
            纯数字股票代码
        """
        normalized, market = SymbolNormalizer.normalize(symbol)
        
        # 去掉后缀
        clean = normalized.replace('.SS', '').replace('.SZ', '').replace('.HK', '')
        return clean
    
    @staticmethod
    def to_yfinance_format(symbol: str) -> str:
        """
        转换为 yfinance 格式
        
        Args:
            symbol: 股票代码
        
        Returns:
            带后缀的股票代码
        """
        normalized, market = SymbolNormalizer.normalize(symbol)
        return normalized
    
    @staticmethod
    def is_a_share(symbol: str) -> bool:
        """判断是否为 A 股"""
        _, market = SymbolNormalizer.normalize(symbol)
        return market == "CN"
    
    @staticmethod
    def is_hk_share(symbol: str) -> bool:
        """判断是否为港股"""
        _, market = SymbolNormalizer.normalize(symbol)
        return market == "HK"
    
    @staticmethod
    def is_us_stock(symbol: str) -> bool:
        """判断是否为美股"""
        _, market = SymbolNormalizer.normalize(symbol)
        return market == "US"


# 快捷函数
def normalize_symbol(symbol: str) -> Tuple[str, str]:
    """快捷函数：标准化股票代码"""
    return SymbolNormalizer.normalize(symbol)

def to_akshare(symbol: str) -> str:
    """快捷函数：转换为 AkShare 格式"""
    return SymbolNormalizer.to_akshare_format(symbol)

def to_yfinance(symbol: str) -> str:
    """快捷函数：转换为 yfinance 格式"""
    return SymbolNormalizer.to_yfinance_format(symbol)


if __name__ == '__main__':
    """测试"""
    test_symbols = [
        '002241',
        '600519',
        '00700.HK',
        '700',
        'AAPL',
        'MSFT',
        '002241.SZ',
        '600519.SS',
    ]
    
    print("股票代码标准化测试")
    print("=" * 60)
    
    for symbol in test_symbols:
        normalized, market = SymbolNormalizer.normalize(symbol)
        akshare_fmt = SymbolNormalizer.to_akshare_format(symbol)
        yf_fmt = SymbolNormalizer.to_yfinance_format(symbol)
        
        print(f"\n原始：{symbol:15} -> 标准化：{normalized:15} 市场：{market}")
        print(f"  AkShare 格式：{akshare_fmt:10} | yfinance 格式：{yf_fmt}")
