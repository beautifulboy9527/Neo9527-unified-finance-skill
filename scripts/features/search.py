#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融搜索模块 - 饕餮整合自 alphaear-search
多引擎搜索、智能缓存、RAG 支持
"""

import sys
import os
import json
import hashlib
import time
import threading
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


class FinanceSearch:
    """
    金融搜索器 - 饕餮整合自 alphaear-search
    
    能力:
    - 多引擎搜索 (DuckDuckGo/Baidu/Jina)
    - 智能缓存 (1小时 TTL)
    - 搜索结果聚合
    - 本地文档搜索
    """
    
    # 速率限制配置
    _request_times = []
    _last_request_time = 0.0
    _lock = threading.Lock()
    _rate_limit = 20  # 每分钟最大请求数
    _rate_window = 60.0
    _min_interval = 2.0
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR / 'cache' / 'search'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self.cache_ttl = int(os.getenv("SEARCH_CACHE_TTL", "3600"))  # 默认1小时
    
    def _wait_for_rate_limit(self):
        """等待以满足速率限制"""
        with self._lock:
            current_time = time.time()
            self._request_times = [t for t in self._request_times if current_time - t < self._rate_window]
            
            if len(self._request_times) >= self._rate_limit:
                oldest = self._request_times[0]
                wait_time = self._rate_window - (current_time - oldest) + 1.0
                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time = time.time()
                    self._request_times = [t for t in self._request_times if current_time - t < self._rate_window]
            
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_interval:
                time.sleep(self._min_interval - time_since_last)
            
            self._request_times.append(time.time())
            self._last_request_time = time.time()
    
    def _get_cache_key(self, query: str, engine: str) -> str:
        """生成缓存键"""
        return hashlib.md5(f"{engine}:{query}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """从缓存获取"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查 TTL
                if time.time() - data.get('timestamp', 0) < self.cache_ttl:
                    return data.get('results', [])
            except:
                pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, results: List[Dict]):
        """保存到缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': time.time(),
                    'results': results
                }, f, ensure_ascii=False)
        except:
            pass
    
    def search_ddg(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        DuckDuckGo 搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        cache_key = self._get_cache_key(query, 'ddg')
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        results = []
        
        try:
            self._wait_for_rate_limit()
            
            # 使用 requests 直接搜索 DuckDuckGo
            import requests
            from urllib.parse import quote
            
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # 简单解析 HTML
                import re
                
                # 提取链接和标题
                pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>'
                matches = re.findall(pattern, response.text)
                
                for url, title in matches[:max_results]:
                    # DuckDuckGo 重定向 URL 解码
                    if 'uddg=' in url:
                        import urllib.parse
                        real_url = urllib.parse.unquote(url.split('uddg=')[-1].split('&')[0])
                    else:
                        real_url = url
                    
                    results.append({
                        'title': title.strip(),
                        'url': real_url,
                        'engine': 'duckduckgo'
                    })
            
        except Exception as e:
            results.append({'error': str(e)})
        
        if results and not results[0].get('error'):
            self._save_to_cache(cache_key, results)
        
        return results
    
    def search_baidu(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        百度搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        cache_key = self._get_cache_key(query, 'baidu')
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        results = []
        
        try:
            self._wait_for_rate_limit()
            
            import requests
            from urllib.parse import quote
            
            url = f"https://www.baidu.com/s?wd={quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                import re
                
                # 提取百度搜索结果
                pattern = r'<h3[^>]*><a[^>]*href="([^"]*)"[^>]*>([^<]*)</a></h3>'
                matches = re.findall(pattern, response.text)
                
                for url, title in matches[:max_results]:
                    results.append({
                        'title': title.strip(),
                        'url': url,
                        'engine': 'baidu'
                    })
            
        except Exception as e:
            results.append({'error': str(e)})
        
        if results and not results[0].get('error'):
            self._save_to_cache(cache_key, results)
        
        return results
    
    def search_jina(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Jina AI 搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        cache_key = self._get_cache_key(query, 'jina')
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        results = []
        
        try:
            self._wait_for_rate_limit()
            
            import requests
            from urllib.parse import quote
            
            url = f"https://s.jina.ai/{quote(query)}"
            headers = {
                'Accept': 'application/json',
                'X-Retain-Images': 'none'
            }
            
            # 检查 API Key
            api_key = os.getenv("JINA_API_KEY", "").strip()
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    for item in data[:max_results]:
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'content': item.get('content', '')[:500] if item.get('content') else '',
                            'engine': 'jina'
                        })
                elif isinstance(data, dict) and 'data' in data:
                    for item in data['data'][:max_results]:
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'content': item.get('content', '')[:500] if item.get('content') else '',
                            'engine': 'jina'
                        })
            
        except Exception as e:
            results.append({'error': str(e)})
        
        if results and not results[0].get('error'):
            self._save_to_cache(cache_key, results)
        
        return results
    
    def aggregate_search(
        self,
        query: str,
        engines: List[str] = None,
        max_results: int = 5
    ) -> Dict:
        """
        聚合搜索
        
        Args:
            query: 搜索关键词
            engines: 引擎列表 ['ddg', 'baidu', 'jina']
            max_results: 每个引擎最大结果数
            
        Returns:
            聚合结果
        """
        if engines is None:
            engines = ['ddg', 'jina']
        
        result = {
            'query': query,
            'engines': engines,
            'results': [],
            'by_engine': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        all_results = []
        
        if 'ddg' in engines:
            ddg_results = self.search_ddg(query, max_results)
            result['by_engine']['duckduckgo'] = ddg_results
            all_results.extend(ddg_results)
        
        if 'baidu' in engines:
            baidu_results = self.search_baidu(query, max_results)
            result['by_engine']['baidu'] = baidu_results
            all_results.extend(baidu_results)
        
        if 'jina' in engines:
            jina_results = self.search_jina(query, max_results)
            result['by_engine']['jina'] = jina_results
            all_results.extend(jina_results)
        
        # 去重
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get('url', '')
            if url and url not in seen_urls and not r.get('error'):
                seen_urls.add(url)
                unique_results.append(r)
        
        result['results'] = unique_results
        result['total'] = len(unique_results)
        
        return result
    
    def search_finance_news(
        self,
        keyword: str,
        max_results: int = 10
    ) -> Dict:
        """
        金融新闻搜索
        
        Args:
            keyword: 关键词
            max_results: 最大结果数
            
        Returns:
            新闻结果
        """
        # 构建金融相关搜索词
        finance_query = f"{keyword} 股票 财经"
        
        return self.aggregate_search(finance_query, ['ddg', 'jina'], max_results)


def search_ddg(query: str, max_results: int = 5) -> List[Dict]:
    """DuckDuckGo 搜索"""
    searcher = FinanceSearch()
    return searcher.search_ddg(query, max_results)


def search_baidu(query: str, max_results: int = 5) -> List[Dict]:
    """百度搜索"""
    searcher = FinanceSearch()
    return searcher.search_baidu(query, max_results)


def search_jina(query: str, max_results: int = 5) -> List[Dict]:
    """Jina AI 搜索"""
    searcher = FinanceSearch()
    return searcher.search_jina(query, max_results)


def aggregate_search(query: str, engines: List[str] = None, max_results: int = 5) -> Dict:
    """聚合搜索"""
    searcher = FinanceSearch()
    return searcher.aggregate_search(query, engines, max_results)


def search_finance_news(keyword: str, max_results: int = 10) -> Dict:
    """金融新闻搜索"""
    searcher = FinanceSearch()
    return searcher.search_finance_news(keyword, max_results)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='金融搜索 - 饕餮整合自 alphaear-search')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--engine', choices=['ddg', 'baidu', 'jina', 'all'], default='all', help='搜索引擎')
    parser.add_argument('--max', type=int, default=5, help='最大结果数')
    
    args = parser.parse_args()
    
    searcher = FinanceSearch()
    
    if args.engine == 'all':
        result = searcher.aggregate_search(args.query, max_results=args.max)
    elif args.engine == 'ddg':
        result = searcher.search_ddg(args.query, args.max)
    elif args.engine == 'baidu':
        result = searcher.search_baidu(args.query, args.max)
    elif args.engine == 'jina':
        result = searcher.search_jina(args.query, args.max)
    else:
        result = searcher.aggregate_search(args.query)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
