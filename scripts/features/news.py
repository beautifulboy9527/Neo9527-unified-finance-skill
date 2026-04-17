#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鏂伴椈鑱氬悎妯″潡 - 楗曢ぎ鏁村悎鑷?alphaear-news
瀹炴椂璐㈢粡鏂伴椈鑱氬悎銆佺粺涓€瓒嬪娍鎶ュ憡銆丳olymarket 棰勬祴鏁版嵁
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Windows 缂栫爜淇
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class NewsAggregator:
    """
    鏂伴椈鑱氬悎鍣?- 楗曢ぎ鏁村悎鑷?alphaear-news
    
    鑳藉姏:
    - 瀹炴椂璐㈢粡鏂伴椈鑱氬悎 (10+ 淇℃簮)
    - 缁熶竴瓒嬪娍鎶ュ憡
    - Polymarket 棰勬祴甯傚満鏁版嵁
    - 鏂伴椈缂撳瓨 (5鍒嗛挓)
    """
    
    # 鏂伴椈婧愰厤缃?    SOURCES = {
        # 閲戣瀺绫?        "cls": "璐㈣仈绀?,
        "wallstreetcn": "鍗庡皵琛楄闂?,
        "xueqiu": "闆悆鐑",
        # 缁煎悎/绀句氦
        "weibo": "寰崥鐑悳",
        "zhihu": "鐭ヤ箮鐑",
        "baidu": "鐧惧害鐑悳",
        "toutiao": "浠婃棩澶存潯",
        # 绉戞妧绫?        "36kr": "36姘?,
        "ithome": "IT涔嬪",
        "hackernews": "Hacker News",
    }
    
    # 榛樿閲戣瀺淇℃簮
    FINANCE_SOURCES = ["cls", "wallstreetcn", "xueqiu", "weibo", "zhihu"]
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR / 'cache' / 'news'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self.base_url = "https://newsnow.busiyi.world"
    
    def fetch_hot_news(
        self,
        source_id: str = "cls",
        count: int = 15
    ) -> Dict:
        """
        浠庢寚瀹氭柊闂绘簮鑾峰彇鐑偣鏂伴椈
        
        Args:
            source_id: 鏂伴椈婧?ID
            count: 鏁伴噺
            
        Returns:
            鏂伴椈鍒楄〃
        """
        result = {
            'source': source_id,
            'source_name': self.SOURCES.get(source_id, source_id),
            'news': [],
            'count': 0,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import requests
            import time
            
            # 妫€鏌ョ紦瀛?(5鍒嗛挓)
            cache_key = f"{source_id}_{count}"
            now = time.time()
            cached = self._cache.get(cache_key)
            
            if cached and (now - cached["time"] < 300):
                result['news'] = cached["data"]
                result['count'] = len(cached["data"])
                result['data_source'] = 'cache'
                return result
            
            # 璇锋眰 NewsNow API
            url = f"{self.base_url}/api/s?id={source_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])[:count]
                
                news_items = []
                for i, item in enumerate(items, 1):
                    news_items.append({
                        "rank": i,
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "publish_time": item.get("publish_time"),
                        "source": source_id
                    })
                
                # 鏇存柊缂撳瓨
                self._cache[cache_key] = {"time": now, "data": news_items}
                
                result['news'] = news_items
                result['count'] = len(news_items)
                result['data_source'] = 'newsnow_api'
                
            else:
                result['error'] = f'API 閿欒: {response.status_code}'
                # 浣跨敤杩囨湡缂撳瓨
                if cached:
                    result['news'] = cached["data"]
                    result['count'] = len(cached["data"])
                    result['data_source'] = 'stale_cache'
                    result['warning'] = '浣跨敤杩囨湡缂撳瓨'
            
        except ImportError as e:
            result['error'] = f'缂哄皯渚濊禆: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
            # 灏濊瘯浣跨敤缂撳瓨
            cached = self._cache.get(f"{source_id}_{count}")
            if cached:
                result['news'] = cached["data"]
                result['count'] = len(cached["data"])
                result['data_source'] = 'fallback_cache'
        
        return result
    
    def get_unified_trends(
        self,
        sources: List[str] = None,
        count_per_source: int = 5
    ) -> Dict:
        """
        鑾峰彇缁熶竴瓒嬪娍鎶ュ憡
        
        Args:
            sources: 鏂伴椈婧愬垪琛?            count_per_source: 姣忎釜婧愮殑鏁伴噺
            
        Returns:
            缁熶竴瓒嬪娍鎶ュ憡
        """
        if sources is None:
            sources = self.FINANCE_SOURCES
        
        result = {
            'sources': sources,
            'trends': [],
            'summary': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            all_news = []
            source_stats = {}
            
            for source_id in sources:
                news_result = self.fetch_hot_news(source_id, count_per_source)
                
                if news_result.get('news'):
                    all_news.extend(news_result['news'])
                    source_stats[source_id] = len(news_result['news'])
            
            # 鍘婚噸 (鎸夋爣棰?
            seen_titles = set()
            unique_news = []
            for news in all_news:
                title = news.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(news)
            
            # 鎸夌儹搴︽帓搴?(绠€鍗曟帓鍚?
            unique_news.sort(key=lambda x: x.get('rank', 999))
            
            result['trends'] = unique_news[:30]  # 杩斿洖鍓?0鏉?            result['summary'] = {
                'total_sources': len(sources),
                'total_news': len(unique_news),
                'source_stats': source_stats
            }
            result['data_source'] = 'multi_source'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_polymarket_summary(self, limit: int = 10) -> Dict:
        """
        鑾峰彇 Polymarket 棰勬祴甯傚満鏁版嵁
        
        Args:
            limit: 鏁伴噺闄愬埗
            
        Returns:
            棰勬祴甯傚満鏁版嵁
        """
        result = {
            'markets': [],
            'count': 0,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import requests
            
            # Polymarket API (绠€鍖栫増)
            url = "https://clob.polymarket.com/markets"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                markets = data[:limit] if isinstance(data, list) else []
                
                market_items = []
                for m in markets:
                    market_items.append({
                        "question": m.get("question") or m.get("condition", ""),
                        "yes_price": m.get("yes_price"),
                        "no_price": m.get("no_price"),
                        "volume": m.get("volume"),
                        "category": m.get("category", "")
                    })
                
                result['markets'] = market_items
                result['count'] = len(market_items)
                result['data_source'] = 'polymarket_api'
            else:
                result['error'] = f'API 閿欒: {response.status_code}'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_finance_brief(self) -> Dict:
        """
        鑾峰彇璐㈢粡绠€鎶?        
        Returns:
            璐㈢粡绠€鎶?        """
        result = {
            'brief': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 鑾峰彇閲戣瀺鏂伴椈
            cls_news = self.fetch_hot_news("cls", 5)
            wallstreetcn_news = self.fetch_hot_news("wallstreetcn", 5)
            
            # 鍚堝苟
            all_news = []
            if cls_news.get('news'):
                all_news.extend(cls_news['news'])
            if wallstreetcn_news.get('news'):
                all_news.extend(wallstreetcn_news['news'])
            
            # 鐢熸垚绠€鎶?            headlines = []
            for news in all_news[:10]:
                headlines.append(f"鈥?{news.get('title', '')}")
            
            result['brief'] = {
                'headlines': headlines,
                'total_news': len(all_news),
                'sources': {
                    'cls': cls_news.get('count', 0),
                    'wallstreetcn': wallstreetcn_news.get('count', 0)
                }
            }
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def fetch_hot_news(source_id: str = "cls", count: int = 15) -> Dict:
    """鑾峰彇鐑偣鏂伴椈"""
    aggregator = NewsAggregator()
    return aggregator.fetch_hot_news(source_id, count)


def get_unified_trends(sources: List[str] = None) -> Dict:
    """鑾峰彇缁熶竴瓒嬪娍"""
    aggregator = NewsAggregator()
    return aggregator.get_unified_trends(sources)


def get_polymarket_summary(limit: int = 10) -> Dict:
    """鑾峰彇 Polymarket 棰勬祴鏁版嵁"""
    aggregator = NewsAggregator()
    return aggregator.get_polymarket_summary(limit)


def get_finance_brief() -> Dict:
    """鑾峰彇璐㈢粡绠€鎶?""
    aggregator = NewsAggregator()
    return aggregator.get_finance_brief()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='鏂伴椈鑱氬悎 - 楗曢ぎ鏁村悎鑷?alphaear-news')
    subparsers = parser.add_subparsers(dest='command', help='鍛戒护')
    
    # news
    news_parser = subparsers.add_parser('news', help='鑾峰彇鐑偣鏂伴椈')
    news_parser.add_argument('--source', default='cls', help='鏂伴椈婧?)
    news_parser.add_argument('--count', type=int, default=15, help='鏁伴噺')
    
    # trends
    trends_parser = subparsers.add_parser('trends', help='缁熶竴瓒嬪娍鎶ュ憡')
    trends_parser.add_argument('--sources', nargs='+', help='鏂伴椈婧愬垪琛?)
    
    # polymarket
    pm_parser = subparsers.add_parser('polymarket', help='Polymarket 棰勬祴')
    pm_parser.add_argument('--limit', type=int, default=10, help='鏁伴噺')
    
    # brief
    subparsers.add_parser('brief', help='璐㈢粡绠€鎶?)
    
    args = parser.parse_args()
    
    aggregator = NewsAggregator()
    
    if args.command == 'news':
        result = aggregator.fetch_hot_news(args.source, args.count)
    elif args.command == 'trends':
        result = aggregator.get_unified_trends(args.sources)
    elif args.command == 'polymarket':
        result = aggregator.get_polymarket_summary(args.limit)
    elif args.command == 'brief':
        result = aggregator.get_finance_brief()
    else:
        # 榛樿鏄剧ず璐㈣仈绀炬柊闂?        result = aggregator.fetch_hot_news("cls", 10)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
