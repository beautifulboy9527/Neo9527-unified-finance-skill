#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻聚合模块 - 饕餮整合自 alphaear-news
实时财经新闻聚合、统一趋势报告、Polymarket 预测数据
"""

import sys
import os
import json
from datetime import datetime
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


class NewsAggregator:
    """
    新闻聚合器 - 饕餮整合自 alphaear-news
    
    能力:
    - 实时财经新闻聚合 (10+ 信源)
    - 统一趋势报告
    - Polymarket 预测市场数据
    - 新闻缓存 (5分钟)
    """
    
    # 新闻源配置
    SOURCES = {
        # 金融类
        "cls": "财联社",
        "wallstreetcn": "华尔街见闻",
        "xueqiu": "雪球热榜",
        # 综合/社交
        "weibo": "微博热搜",
        "zhihu": "知乎热榜",
        "baidu": "百度热搜",
        "toutiao": "今日头条",
        # 科技类
        "36kr": "36氪",
        "ithome": "IT之家",
        "hackernews": "Hacker News",
    }
    
    # 默认金融信源
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
        从指定新闻源获取热点新闻
        
        Args:
            source_id: 新闻源 ID
            count: 数量
            
        Returns:
            新闻列表
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
            
            # 检查缓存 (5分钟)
            cache_key = f"{source_id}_{count}"
            now = time.time()
            cached = self._cache.get(cache_key)
            
            if cached and (now - cached["time"] < 300):
                result['news'] = cached["data"]
                result['count'] = len(cached["data"])
                result['data_source'] = 'cache'
                return result
            
            # 请求 NewsNow API
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
                
                # 更新缓存
                self._cache[cache_key] = {"time": now, "data": news_items}
                
                result['news'] = news_items
                result['count'] = len(news_items)
                result['data_source'] = 'newsnow_api'
                
            else:
                result['error'] = f'API 错误: {response.status_code}'
                # 使用过期缓存
                if cached:
                    result['news'] = cached["data"]
                    result['count'] = len(cached["data"])
                    result['data_source'] = 'stale_cache'
                    result['warning'] = '使用过期缓存'
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
            # 尝试使用缓存
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
        获取统一趋势报告
        
        Args:
            sources: 新闻源列表
            count_per_source: 每个源的数量
            
        Returns:
            统一趋势报告
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
            
            # 去重 (按标题)
            seen_titles = set()
            unique_news = []
            for news in all_news:
                title = news.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(news)
            
            # 按热度排序 (简单排名)
            unique_news.sort(key=lambda x: x.get('rank', 999))
            
            result['trends'] = unique_news[:30]  # 返回前30条
            result['summary'] = {
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
        获取 Polymarket 预测市场数据
        
        Args:
            limit: 数量限制
            
        Returns:
            预测市场数据
        """
        result = {
            'markets': [],
            'count': 0,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import requests
            
            # Polymarket API (简化版)
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
                result['error'] = f'API 错误: {response.status_code}'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_finance_brief(self) -> Dict:
        """
        获取财经简报
        
        Returns:
            财经简报
        """
        result = {
            'brief': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 获取金融新闻
            cls_news = self.fetch_hot_news("cls", 5)
            wallstreetcn_news = self.fetch_hot_news("wallstreetcn", 5)
            
            # 合并
            all_news = []
            if cls_news.get('news'):
                all_news.extend(cls_news['news'])
            if wallstreetcn_news.get('news'):
                all_news.extend(wallstreetcn_news['news'])
            
            # 生成简报
            headlines = []
            for news in all_news[:10]:
                headlines.append(f"• {news.get('title', '')}")
            
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
    """获取热点新闻"""
    aggregator = NewsAggregator()
    return aggregator.fetch_hot_news(source_id, count)


def get_unified_trends(sources: List[str] = None) -> Dict:
    """获取统一趋势"""
    aggregator = NewsAggregator()
    return aggregator.get_unified_trends(sources)


def get_polymarket_summary(limit: int = 10) -> Dict:
    """获取 Polymarket 预测数据"""
    aggregator = NewsAggregator()
    return aggregator.get_polymarket_summary(limit)


def get_finance_brief() -> Dict:
    """获取财经简报"""
    aggregator = NewsAggregator()
    return aggregator.get_finance_brief()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='新闻聚合 - 饕餮整合自 alphaear-news')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # news
    news_parser = subparsers.add_parser('news', help='获取热点新闻')
    news_parser.add_argument('--source', default='cls', help='新闻源')
    news_parser.add_argument('--count', type=int, default=15, help='数量')
    
    # trends
    trends_parser = subparsers.add_parser('trends', help='统一趋势报告')
    trends_parser.add_argument('--sources', nargs='+', help='新闻源列表')
    
    # polymarket
    pm_parser = subparsers.add_parser('polymarket', help='Polymarket 预测')
    pm_parser.add_argument('--limit', type=int, default=10, help='数量')
    
    # brief
    subparsers.add_parser('brief', help='财经简报')
    
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
        # 默认显示财联社新闻
        result = aggregator.fetch_hot_news("cls", 10)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
