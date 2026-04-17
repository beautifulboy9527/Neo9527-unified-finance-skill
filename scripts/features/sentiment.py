#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鎯呯华鍒嗘瀽妯″潡 - 瀹屾暣闆嗘垚鑷?finance-sentiment skill
Reddit銆乆.com銆佹柊闂汇€丳olymarket 鎯呯华鍒嗘瀽
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List

# Windows 缂栫爜淇
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class SentimentAnalyzer:
    """
    鎯呯华鍒嗘瀽鍣?- 闆嗘垚鑷?finance-sentiment skill
    
    鏁版嵁婧?
    - Reddit (Reddit 鎯呯华)
    - X.com (Twitter 鎯呯华)
    - News (鏂伴椈鎯呯华)
    - Polymarket (棰勬祴甯傚満)
    
    API: Adanos Finance API
    渚濊禆: ADANOS_API_KEY 鐜鍙橀噺
    """
    
    API_BASE = "https://api.adanos.org"
    
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.api_key = os.getenv('ADANOS_API_KEY')
        
    def _make_request(self, endpoint: str, tickers: str, days: int = 7) -> Optional[List]:
        """
        鍙戦€?API 璇锋眰
        
        Args:
            endpoint: 绔偣璺緞
            tickers: 鑲＄エ浠ｇ爜 (閫楀彿鍒嗛殧)
            days: 澶╂暟
        """
        if not self.api_key:
            return None
        
        try:
            import requests
            
            url = f"{self.API_BASE}{endpoint}?tickers={tickers}&days={days}"
            headers = {'X-API-Key': self.api_key}
            
            resp = requests.get(url, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                return data
            else:
                return None
                
        except Exception:
            return None
    
    def analyze_reddit(self, days: int = 7) -> Dict:
        """
        Reddit 鎯呯华鍒嗘瀽
        
        Returns:
            {
                'source': 'reddit',
                'buzz': 鐑害鍒嗘暟 (0-100),
                'bullish_pct': 鐪嬫定鐧惧垎姣?
                'bearish_pct': 鐪嬭穼鐧惧垎姣?
                'mentions': 鎻愬強娆℃暟,
                'trend': 瓒嬪娍 (rising/falling/stable),
                'sentiment_score': 鎯呯华鍒嗘暟,
                'unique_posts': 鐙珛甯栧瓙鏁?
                'subreddit_count': 娑夊強鐨勫瓙鐗堝潡鏁?
                'total_upvotes': 鎬荤偣璧炴暟
            }
        """
        result = {
            'source': 'reddit',
            'symbol': self.symbol,
            'buzz': None,
            'bullish_pct': None,
            'bearish_pct': None,
            'mentions': None,
            'trend': None,
            'sentiment_score': None,
            'unique_posts': None,
            'subreddit_count': None,
            'total_upvotes': None,
            'data_source': 'none',
            'error': None
        }
        
        if not self.api_key:
            result['error'] = '闇€瑕佽缃?ADANOS_API_KEY 鐜鍙橀噺'
            return result
        
        data = self._make_request('/reddit/stocks/v1/compare', self.symbol, days)
        
        if data and len(data) > 0:
            item = data[0]
            result.update({
                'buzz': item.get('buzz_score'),
                'bullish_pct': item.get('bullish_pct'),
                'bearish_pct': item.get('bearish_pct'),
                'mentions': item.get('mentions'),
                'trend': item.get('trend'),
                'sentiment_score': item.get('sentiment_score'),
                'unique_posts': item.get('unique_posts'),
                'subreddit_count': item.get('subreddit_count'),
                'total_upvotes': item.get('total_upvotes'),
                'data_source': 'adanos_reddit'
            })
        else:
            result['error'] = '鏃犳硶鑾峰彇 Reddit 鏁版嵁'
        
        return result
    
    def analyze_x(self, days: int = 7) -> Dict:
        """
        X.com (Twitter) 鎯呯华鍒嗘瀽
        
        Returns:
            {
                'source': 'x',
                'buzz': 鐑害鍒嗘暟,
                'bullish_pct': 鐪嬫定鐧惧垎姣?
                'mentions': 鎺ㄦ枃鏁?
                'trend': 瓒嬪娍,
                'unique_tweets': 鐙珛鎺ㄦ枃鏁?
                'total_upvotes': 鎬荤偣璧炴暟
            }
        """
        result = {
            'source': 'x',
            'symbol': self.symbol,
            'buzz': None,
            'bullish_pct': None,
            'bearish_pct': None,
            'mentions': None,
            'trend': None,
            'sentiment_score': None,
            'unique_tweets': None,
            'total_upvotes': None,
            'data_source': 'none',
            'error': None
        }
        
        if not self.api_key:
            result['error'] = '闇€瑕佽缃?ADANOS_API_KEY 鐜鍙橀噺'
            return result
        
        data = self._make_request('/x/stocks/v1/compare', self.symbol, days)
        
        if data and len(data) > 0:
            item = data[0]
            result.update({
                'buzz': item.get('buzz_score'),
                'bullish_pct': item.get('bullish_pct'),
                'bearish_pct': item.get('bearish_pct'),
                'mentions': item.get('mentions'),
                'trend': item.get('trend'),
                'sentiment_score': item.get('sentiment_score'),
                'unique_tweets': item.get('unique_tweets'),
                'total_upvotes': item.get('total_upvotes'),
                'data_source': 'adanos_x'
            })
        else:
            result['error'] = '鏃犳硶鑾峰彇 X.com 鏁版嵁'
        
        return result
    
    def analyze_news(self, days: int = 7) -> Dict:
        """
        鏂伴椈鎯呯华鍒嗘瀽
        
        Returns:
            {
                'source': 'news',
                'buzz': 鐑害鍒嗘暟,
                'bullish_pct': 鐪嬫定鐧惧垎姣?
                'mentions': 鏂伴椈鏁?
                'trend': 瓒嬪娍,
                'source_count': 鏂伴椈鏉ユ簮鏁?            }
        """
        result = {
            'source': 'news',
            'symbol': self.symbol,
            'buzz': None,
            'bullish_pct': None,
            'bearish_pct': None,
            'mentions': None,
            'trend': None,
            'sentiment_score': None,
            'source_count': None,
            'data_source': 'none',
            'error': None
        }
        
        if not self.api_key:
            result['error'] = '闇€瑕佽缃?ADANOS_API_KEY 鐜鍙橀噺'
            return result
        
        data = self._make_request('/news/stocks/v1/compare', self.symbol, days)
        
        if data and len(data) > 0:
            item = data[0]
            result.update({
                'buzz': item.get('buzz_score'),
                'bullish_pct': item.get('bullish_pct'),
                'bearish_pct': item.get('bearish_pct'),
                'mentions': item.get('mentions'),
                'trend': item.get('trend'),
                'sentiment_score': item.get('sentiment_score'),
                'source_count': item.get('source_count'),
                'data_source': 'adanos_news'
            })
        else:
            result['error'] = '鏃犳硶鑾峰彇鏂伴椈鏁版嵁'
        
        return result
    
    def analyze_polymarket(self, days: int = 7) -> Dict:
        """
        Polymarket 棰勬祴甯傚満鍒嗘瀽
        
        Returns:
            {
                'source': 'polymarket',
                'buzz': 鐑害鍒嗘暟,
                'bullish_pct': 鐪嬫定鐧惧垎姣?
                'trade_count': 浜ゆ槗鏁?
                'trend': 瓒嬪娍,
                'market_count': 甯傚満鏁?
                'unique_traders': 鐙珛浜ゆ槗鑰呮暟,
                'total_liquidity': 鎬绘祦鍔ㄦ€?            }
        """
        result = {
            'source': 'polymarket',
            'symbol': self.symbol,
            'buzz': None,
            'bullish_pct': None,
            'bearish_pct': None,
            'trade_count': None,
            'trend': None,
            'sentiment_score': None,
            'market_count': None,
            'unique_traders': None,
            'total_liquidity': None,
            'data_source': 'none',
            'error': None
        }
        
        if not self.api_key:
            result['error'] = '闇€瑕佽缃?ADANOS_API_KEY 鐜鍙橀噺'
            return result
        
        data = self._make_request('/polymarket/stocks/v1/compare', self.symbol, days)
        
        if data and len(data) > 0:
            item = data[0]
            result.update({
                'buzz': item.get('buzz_score'),
                'bullish_pct': item.get('bullish_pct'),
                'bearish_pct': item.get('bearish_pct'),
                'trade_count': item.get('trade_count'),
                'trend': item.get('trend'),
                'sentiment_score': item.get('sentiment_score'),
                'market_count': item.get('market_count'),
                'unique_traders': item.get('unique_traders'),
                'total_liquidity': item.get('total_liquidity'),
                'data_source': 'adanos_polymarket'
            })
        else:
            result['error'] = '鏃犳硶鑾峰彇 Polymarket 鏁版嵁'
        
        return result
    
    def analyze_all(self, days: int = 7) -> Dict:
        """
        鍏ㄦ簮鎯呯华鍒嗘瀽
        
        Returns:
            鎵€鏈夋暟鎹簮鐨勬儏缁垎鏋愮粨鏋?        """
        return {
            'symbol': self.symbol,
            'reddit': self.analyze_reddit(days),
            'x': self.analyze_x(days),
            'news': self.analyze_news(days),
            'polymarket': self.analyze_polymarket(days),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_summary(self, days: int = 7) -> Dict:
        """
        鑾峰彇鎯呯华鎽樿 - 缁煎悎鎵€鏈夋暟鎹簮
        
        Returns:
            {
                'symbol': 鑲＄エ浠ｇ爜,
                'avg_bullish_pct': 骞冲潎鐪嬫定鐧惧垎姣?
                'avg_buzz': 骞冲潎鐑害,
                'sentiment': 缁煎悎鎯呯华,
                'alignment': 鏁版嵁婧愪竴鑷存€?
                'sources': 鍚勬暟鎹簮璇︽儏
            }
        """
        all_sources = self.analyze_all(days)
        
        # 缁煎悎璁＄畻
        bullish_scores = []
        buzz_scores = []
        sources_available = []
        
        for source_name in ['reddit', 'x', 'news', 'polymarket']:
            data = all_sources.get(source_name, {})
            if data.get('bullish_pct') is not None:
                bullish_scores.append(data['bullish_pct'])
                sources_available.append(source_name)
            if data.get('buzz') is not None:
                buzz_scores.append(data['buzz'])
        
        avg_bullish = sum(bullish_scores) / len(bullish_scores) if bullish_scores else None
        avg_buzz = sum(buzz_scores) / len(buzz_scores) if buzz_scores else None
        
        # 鎯呯华鍒ゆ柇
        if avg_bullish:
            if avg_bullish > 60:
                sentiment = 'bullish'
                sentiment_desc = '鐪嬫定'
            elif avg_bullish > 40:
                sentiment = 'neutral'
                sentiment_desc = '涓€?
            else:
                sentiment = 'bearish'
                sentiment_desc = '鐪嬭穼'
        else:
            sentiment = 'unknown'
            sentiment_desc = '鏈煡'
        
        # 鏁版嵁婧愪竴鑷存€?        if len(bullish_scores) >= 2:
            max_diff = max(bullish_scores) - min(bullish_scores)
            if max_diff < 10:
                alignment = 'aligned'
                alignment_desc = '鏁版嵁婧愪竴鑷?
            elif max_diff < 25:
                alignment = 'somewhat_aligned'
                alignment_desc = '鏁版嵁婧愬ぇ鑷翠竴鑷?
            else:
                alignment = 'diverging'
                alignment_desc = '鏁版嵁婧愬垎姝ц緝澶?
        else:
            alignment = 'insufficient_data'
            alignment_desc = '鏁版嵁涓嶈冻'
        
        return {
            'symbol': self.symbol,
            'avg_bullish_pct': round(avg_bullish, 2) if avg_bullish else None,
            'avg_buzz': round(avg_buzz, 2) if avg_buzz else None,
            'sentiment': sentiment,
            'sentiment_description': sentiment_desc,
            'alignment': alignment,
            'alignment_description': alignment_desc,
            'sources_available': sources_available,
            'sources': all_sources,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def compare_tickers(self, symbols: List[str], days: int = 7, source: str = 'reddit') -> Dict:
        """
        瀵规瘮澶氬彧鑲＄エ鐨勬儏缁?        
        Args:
            symbols: 鑲＄エ浠ｇ爜鍒楄〃
            days: 澶╂暟
            source: 鏁版嵁婧?        """
        result = {
            'symbols': symbols,
            'source': source,
            'comparison': [],
            'ranking': [],
            'data_source': 'none',
            'error': None
        }
        
        if not self.api_key:
            result['error'] = '闇€瑕佽缃?ADANOS_API_KEY 鐜鍙橀噺'
            return result
        
        endpoints = {
            'reddit': '/reddit/stocks/v1/compare',
            'x': '/x/stocks/v1/compare',
            'news': '/news/stocks/v1/compare',
            'polymarket': '/polymarket/stocks/v1/compare'
        }
        
        endpoint = endpoints.get(source, '/reddit/stocks/v1/compare')
        tickers = ','.join([s.upper() for s in symbols])
        
        data = self._make_request(endpoint, tickers, days)
        
        if data:
            result['comparison'] = data
            result['ranking'] = sorted(data, key=lambda x: x.get('buzz_score', 0), reverse=True)
            result['data_source'] = f'adanos_{source}'
        else:
            result['error'] = '鏃犳硶鑾峰彇瀵规瘮鏁版嵁'
        
        return result


def analyze_sentiment(symbol: str, days: int = 7) -> Dict:
    """鎯呯华鍒嗘瀽鍏ュ彛"""
    analyzer = SentimentAnalyzer(symbol)
    return analyzer.get_summary(days)


def analyze_reddit(symbol: str, days: int = 7) -> Dict:
    """Reddit 鎯呯华鍒嗘瀽"""
    analyzer = SentimentAnalyzer(symbol)
    return analyzer.analyze_reddit(days)


def analyze_x(symbol: str, days: int = 7) -> Dict:
    """X.com 鎯呯华鍒嗘瀽"""
    analyzer = SentimentAnalyzer(symbol)
    return analyzer.analyze_x(days)


def analyze_news(symbol: str, days: int = 7) -> Dict:
    """鏂伴椈鎯呯华鍒嗘瀽"""
    analyzer = SentimentAnalyzer(symbol)
    return analyzer.analyze_news(days)


def compare_sentiment(symbols: List[str], days: int = 7, source: str = 'reddit') -> Dict:
    """澶氳偂绁ㄦ儏缁姣?""
    analyzer = SentimentAnalyzer(symbols[0])
    return analyzer.compare_tickers(symbols, days, source)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='鎯呯华鍒嗘瀽 - 闆嗘垚鑷?finance-sentiment skill')
    parser.add_argument('--symbol', required=True, help='鑲＄エ浠ｇ爜')
    parser.add_argument('--days', type=int, default=7, help='鍒嗘瀽澶╂暟')
    parser.add_argument('--type', choices=['summary', 'reddit', 'x', 'news', 'polymarket'], default='summary')
    parser.add_argument('--compare', nargs='+', help='瀵规瘮澶氬彧鑲＄エ')
    parser.add_argument('--source', choices=['reddit', 'x', 'news', 'polymarket'], default='reddit')
    
    args = parser.parse_args()
    
    if args.compare:
        result = compare_sentiment(args.compare, args.days, args.source)
    else:
        analyzer = SentimentAnalyzer(args.symbol)
        
        if args.type == 'summary':
            result = analyzer.get_summary(args.days)
        elif args.type == 'reddit':
            result = analyzer.analyze_reddit(args.days)
        elif args.type == 'x':
            result = analyzer.analyze_x(args.days)
        elif args.type == 'news':
            result = analyzer.analyze_news(args.days)
        elif args.type == 'polymarket':
            result = analyzer.analyze_polymarket(args.days)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
