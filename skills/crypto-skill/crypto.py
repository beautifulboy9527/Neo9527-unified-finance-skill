#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币模块 - 基于 ccxt
支持 100+ 交易所的加密货币行情、深度、历史数据
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


class CryptoAnalyzer:
    """
    加密货币分析器 - 基于 ccxt
    
    支持:
    - 100+ 交易所 (Binance, OKX, Coinbase, Kraken...)
    - 行情查询
    - 订单簿深度
    - 历史K线
    - 交易对搜索
    """
    
    # 热门交易所
    POPULAR_EXCHANGES = ['binance', 'okx', 'coinbase', 'kraken', 'bybit', 'huobi']
    
    def __init__(self, exchange: str = 'binance'):
        self.exchange_name = exchange
        self._exchange = None
        self.cache_dir = OUTPUT_DIR / 'cache' / 'crypto'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def exchange(self):
        """懒加载交易所实例"""
        if self._exchange is None:
            try:
                import ccxt
                self._exchange = getattr(ccxt, self.exchange_name)({
                    'enableRateLimit': True,  # 启用速率限制
                })
            except ImportError:
                raise ImportError("请安装 ccxt: pip install ccxt")
        return self._exchange
    
    def get_quote(self, symbol: str) -> Dict:
        """
        获取加密货币行情
        
        Args:
            symbol: 交易对 (如 'BTC/USDT')
            
        Returns:
            行情数据
        """
        result = {
            'symbol': symbol,
            'exchange': self.exchange_name,
            'price': None,
            'change_24h': None,
            'change_pct_24h': None,
            'volume_24h': None,
            'high_24h': None,
            'low_24h': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'ccxt',
            'error': None
        }
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            
            result.update({
                'price': ticker.get('last'),
                'change_24h': ticker.get('change'),
                'change_pct_24h': ticker.get('percentage'),
                'volume_24h': ticker.get('baseVolume'),
                'high_24h': ticker.get('high'),
                'low_24h': ticker.get('low'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'vwap': ticker.get('vwap')
            })
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        获取订单簿深度
        
        Args:
            symbol: 交易对
            limit: 深度限制
            
        Returns:
            订单簿数据
        """
        result = {
            'symbol': symbol,
            'exchange': self.exchange_name,
            'bids': [],
            'asks': [],
            'spread': None,
            'spread_pct': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            
            bids = orderbook.get('bids', [])[:limit]
            asks = orderbook.get('asks', [])[:limit]
            
            result['bids'] = [{'price': b[0], 'amount': b[1]} for b in bids]
            result['asks'] = [{'price': a[0], 'amount': a[1]} for a in asks]
            
            if bids and asks:
                best_bid = bids[0][0]
                best_ask = asks[0][0]
                spread = best_ask - best_bid
                result['spread'] = spread
                result['spread_pct'] = (spread / best_ask) * 100 if best_ask else None
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 100
    ) -> Dict:
        """
        获取历史K线数据
        
        Args:
            symbol: 交易对
            timeframe: 时间周期 ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
            limit: 数量限制
            
        Returns:
            K线数据
        """
        result = {
            'symbol': symbol,
            'exchange': self.exchange_name,
            'timeframe': timeframe,
            'ohlcv': [],
            'count': 0,
            'data_source': 'ccxt',
            'error': None
        }
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            candles = []
            for candle in ohlcv:
                candles.append({
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            result['ohlcv'] = candles
            result['count'] = len(candles)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_trending(self, limit: int = 20) -> Dict:
        """
        获取热门交易对
        
        Args:
            limit: 数量限制
            
        Returns:
            热门交易对列表
        """
        result = {
            'exchange': self.exchange_name,
            'trending': [],
            'count': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 获取所有交易对的行情
            tickers = self.exchange.fetch_tickers()
            
            # 按成交量排序
            sorted_tickers = sorted(
                tickers.items(),
                key=lambda x: x[1].get('quoteVolume', 0) or 0,
                reverse=True
            )
            
            trending = []
            for symbol, ticker in sorted_tickers[:limit]:
                trending.append({
                    'symbol': symbol,
                    'price': ticker.get('last'),
                    'change_pct_24h': ticker.get('percentage'),
                    'volume_24h': ticker.get('quoteVolume')
                })
            
            result['trending'] = trending
            result['count'] = len(trending)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def search_markets(self, keyword: str) -> Dict:
        """
        搜索交易对
        
        Args:
            keyword: 关键词
            
        Returns:
            匹配的交易对列表
        """
        result = {
            'keyword': keyword,
            'exchange': self.exchange_name,
            'markets': [],
            'count': 0,
            'error': None
        }
        
        try:
            markets = self.exchange.load_markets()
            
            keyword_upper = keyword.upper()
            matches = []
            
            for symbol, market in markets.items():
                if keyword_upper in symbol.upper():
                    matches.append({
                        'symbol': symbol,
                        'base': market.get('base'),
                        'quote': market.get('quote'),
                        'active': market.get('active')
                    })
            
            result['markets'] = matches[:50]  # 最多返回50个
            result['count'] = len(result['markets'])
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_multi_exchange_quote(
        self,
        symbol: str,
        exchanges: List[str] = None
    ) -> Dict:
        """
        获取多交易所比价
        
        Args:
            symbol: 交易对
            exchanges: 交易所列表
            
        Returns:
            多交易所比价结果
        """
        if exchanges is None:
            exchanges = self.POPULAR_EXCHANGES
        
        result = {
            'symbol': symbol,
            'exchanges': {},
            'best_price': None,
            'best_exchange': None,
            'price_range': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        prices = []
        
        for exchange_name in exchanges:
            try:
                import ccxt
                ex = getattr(ccxt, exchange_name)({'enableRateLimit': True})
                ticker = ex.fetch_ticker(symbol)
                
                price = ticker.get('last')
                if price:
                    result['exchanges'][exchange_name] = {
                        'price': price,
                        'volume': ticker.get('baseVolume'),
                        'change_pct': ticker.get('percentage')
                    }
                    prices.append((exchange_name, price))
                    
            except Exception:
                pass
        
        if prices:
            # 找最优价格
            prices.sort(key=lambda x: x[1])
            result['best_price'] = prices[0][1]
            result['best_exchange'] = prices[0][0]
            result['price_range'] = {
                'min': prices[0][1],
                'max': prices[-1][1],
                'spread': prices[-1][1] - prices[0][1],
                'spread_pct': (prices[-1][1] - prices[0][1]) / prices[0][1] * 100
            }
        
        return result


def get_crypto_quote(symbol: str, exchange: str = 'binance') -> Dict:
    """获取加密货币行情"""
    analyzer = CryptoAnalyzer(exchange)
    return analyzer.get_quote(symbol)


def get_orderbook(symbol: str, exchange: str = 'binance', limit: int = 20) -> Dict:
    """获取订单簿"""
    analyzer = CryptoAnalyzer(exchange)
    return analyzer.get_orderbook(symbol, limit)


def get_ohlcv(symbol: str, timeframe: str = '1d', exchange: str = 'binance', limit: int = 100) -> Dict:
    """获取K线数据"""
    analyzer = CryptoAnalyzer(exchange)
    return analyzer.get_ohlcv(symbol, timeframe, limit)


def get_trending(exchange: str = 'binance', limit: int = 20) -> Dict:
    """获取热门交易对"""
    analyzer = CryptoAnalyzer(exchange)
    return analyzer.get_trending(limit)


def search_markets(keyword: str, exchange: str = 'binance') -> Dict:
    """搜索交易对"""
    analyzer = CryptoAnalyzer(exchange)
    return analyzer.search_markets(keyword)


def get_multi_exchange_quote(symbol: str, exchanges: List[str] = None) -> Dict:
    """多交易所比价"""
    analyzer = CryptoAnalyzer()
    return analyzer.get_multi_exchange_quote(symbol, exchanges)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='加密货币分析')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # quote
    quote_parser = subparsers.add_parser('quote', help='获取行情')
    quote_parser.add_argument('symbol', help='交易对')
    quote_parser.add_argument('--exchange', default='binance', help='交易所')
    
    # orderbook
    ob_parser = subparsers.add_parser('orderbook', help='订单簿')
    ob_parser.add_argument('symbol', help='交易对')
    ob_parser.add_argument('--exchange', default='binance')
    ob_parser.add_argument('--limit', type=int, default=20)
    
    # trending
    trend_parser = subparsers.add_parser('trending', help='热门交易对')
    trend_parser.add_argument('--exchange', default='binance')
    trend_parser.add_argument('--limit', type=int, default=20)
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索交易对')
    search_parser.add_argument('keyword', help='关键词')
    search_parser.add_argument('--exchange', default='binance')
    
    args = parser.parse_args()
    
    if args.command == 'quote':
        result = get_crypto_quote(args.symbol, args.exchange)
    elif args.command == 'orderbook':
        result = get_orderbook(args.symbol, args.exchange, args.limit)
    elif args.command == 'trending':
        result = get_trending(args.exchange, args.limit)
    elif args.command == 'search':
        result = search_markets(args.keyword, args.exchange)
    else:
        # 默认获取 BTC 行情
        result = get_crypto_quote('BTC/USDT', 'binance')
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
