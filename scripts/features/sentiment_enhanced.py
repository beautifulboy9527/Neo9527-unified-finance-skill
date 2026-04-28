#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪分析模块 - 多数据源方案
支持免费本地模型 + Adanos API (付费)
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
    OUTPUT_DIR = Path(__file__).resolve().parents[2] / 'outputs'


class SentimentAnalyzer:
    """
    情绪分析器 - 多数据源方案
    
    数据源优先级:
    1. Adanos API (付费，需配置 ADANOS_API_KEY)
    2. 本地情感模型 (免费，TextBlob/VADER)
    3. 新闻标题分析 (免费)
    """
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR / 'cache' / 'sentiment'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.adanos_api_key = os.getenv('ADANOS_API_KEY', '').strip()
        self.has_adanos = bool(self.adanos_api_key)
    
    def analyze(self, symbol: str, days: int = 7) -> Dict:
        """
        综合情绪分析
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            情绪分析结果
        """
        result = {
            'symbol': symbol,
            'avg_bullish_pct': None,
            'avg_buzz': None,
            'sentiment': 'unknown',
            'sentiment_description': '未知',
            'alignment': 'insufficient_data',
            'alignment_description': '数据不足',
            'sources_available': [],
            'sources': {},
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 尝试 Adanos API
        if self.has_adanos:
            adanos_result = self._fetch_adanos(symbol, days)
            if adanos_result.get('success'):
                return adanos_result['data']
        
        # 降级到本地分析
        local_result = self._analyze_local(symbol, days)
        if local_result.get('success'):
            return local_result['data']
        
        return result
    
    def _fetch_adanos(self, symbol: str, days: int) -> Dict:
        """
        从 Adanos API 获取情绪数据
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            API 结果
        """
        result = {
            'success': False,
            'data': None,
            'error': None
        }
        
        try:
            import requests
            
            headers = {'X-API-Key': self.adanos_api_key}
            base_url = 'https://api.adanos.org'
            
            sources = ['reddit', 'x', 'news']
            all_data = {}
            
            for source in sources:
                url = f'{base_url}/{source}/stocks/v1/compare?tickers={symbol}&days={days}'
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        all_data[source] = data[0] if isinstance(data, list) else data
            
            if all_data:
                result['success'] = True
                result['data'] = self._process_adanos_data(symbol, all_data)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _process_adanos_data(self, symbol: str, data: Dict) -> Dict:
        """处理 Adanos 数据"""
        sources_available = list(data.keys())
        bullish_pcts = []
        buzz_scores = []
        
        sources_result = {}
        
        for source, item in data.items():
            bullish_pct = item.get('bullish_pct')
            buzz_score = item.get('buzz_score')
            
            if bullish_pct is not None:
                bullish_pcts.append(bullish_pct)
            if buzz_score is not None:
                buzz_scores.append(buzz_score)
            
            sources_result[source] = {
                'source': source,
                'symbol': symbol,
                'buzz': buzz_score,
                'bullish_pct': bullish_pct,
                'bearish_pct': 100 - bullish_pct if bullish_pct else None,
                'mentions': item.get('mentions'),
                'trend': item.get('trend'),
                'sentiment_score': bullish_pct / 100 if bullish_pct else None,
                'data_source': 'adanos',
                'error': None
            }
        
        avg_bullish = sum(bullish_pcts) / len(bullish_pcts) if bullish_pcts else None
        avg_buzz = sum(buzz_scores) / len(buzz_scores) if buzz_scores else None
        
        # 确定整体情绪
        if avg_bullish:
            if avg_bullish > 60:
                sentiment = 'bullish'
                sentiment_desc = '看涨'
            elif avg_bullish < 40:
                sentiment = 'bearish'
                sentiment_desc = '看跌'
            else:
                sentiment = 'neutral'
                sentiment_desc = '中性'
        else:
            sentiment = 'unknown'
            sentiment_desc = '未知'
        
        return {
            'symbol': symbol,
            'avg_bullish_pct': avg_bullish,
            'avg_buzz': avg_buzz,
            'sentiment': sentiment,
            'sentiment_description': sentiment_desc,
            'alignment': 'aligned' if len(set([s.get('trend') for s in sources_result.values()])) == 1 else 'mixed',
            'alignment_description': '一致' if len(set([s.get('trend') for s in sources_result.values()])) == 1 else '分歧',
            'sources_available': sources_available,
            'sources': sources_result,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_local(self, symbol: str, days: int) -> Dict:
        """
        本地情绪分析 (免费方案)
        
        使用:
        1. 新闻标题情感分析 (TextBlob/VADER)
        2. 社交媒体文本分析
        
        Args:
            symbol: 股票代码
            days: 天数
            
        Returns:
            本地分析结果
        """
        result = {
            'success': False,
            'data': None,
            'error': None
        }
        
        try:
            # 获取新闻标题
            news_headlines = self._fetch_news_headlines(symbol)
            
            if news_headlines:
                # 使用本地情感模型分析
                sentiment_scores = []
                
                for headline in news_headlines:
                    score = self._analyze_text_sentiment(headline)
                    sentiment_scores.append(score)
                
                if sentiment_scores:
                    avg_score = sum(sentiment_scores) / len(sentiment_scores)
                    
                    # 转换为 bullish_pct
                    bullish_pct = (avg_score + 1) / 2 * 100  # -1~1 -> 0~100
                    
                    result['success'] = True
                    result['data'] = {
                        'symbol': symbol,
                        'avg_bullish_pct': round(bullish_pct, 2),
                        'avg_buzz': len(news_headlines) * 10,  # 简单估算
                        'sentiment': 'bullish' if avg_score > 0.1 else ('bearish' if avg_score < -0.1 else 'neutral'),
                        'sentiment_description': '看涨' if avg_score > 0.1 else ('看跌' if avg_score < -0.1 else '中性'),
                        'alignment': 'local',
                        'alignment_description': '基于新闻标题分析',
                        'sources_available': ['news'],
                        'sources': {
                            'news': {
                                'source': 'news',
                                'symbol': symbol,
                                'buzz': len(news_headlines),
                                'bullish_pct': round(bullish_pct, 2),
                                'sentiment_score': round(avg_score, 4),
                                'headlines_count': len(news_headlines),
                                'data_source': 'local_textblob',
                                'error': None
                            },
                            'reddit': {
                                'source': 'reddit',
                                'symbol': symbol,
                                'data_source': 'none',
                                'error': '需配置 ADANOS_API_KEY'
                            },
                            'x': {
                                'source': 'x',
                                'symbol': symbol,
                                'data_source': 'none',
                                'error': '需配置 ADANOS_API_KEY'
                            }
                        },
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _fetch_news_headlines(self, symbol: str, max_headlines: int = 20) -> List[str]:
        """
        获取新闻标题
        
        Args:
            symbol: 股票代码
            max_headlines: 最大数量
            
        Returns:
            新闻标题列表
        """
        headlines = []
        
        try:
            # 使用 yfinance 获取相关新闻
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                for item in news[:max_headlines]:
                    title = item.get('title', '')
                    if title:
                        headlines.append(title)
            
        except Exception as e:
            headlines = []
        
        return headlines
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        分析文本情感
        
        Args:
            text: 文本内容
            
        Returns:
            情感分数 (-1 到 1)
        """
        try:
            # 尝试使用 TextBlob
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except ImportError:
            pass
        
        try:
            # 尝试使用 VADER
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(text)
            return scores['compound']
        except ImportError:
            pass
        
        # 简单关键词分析
        positive_words = ['buy', 'bullish', 'up', 'gain', 'profit', 'rise', 'positive', 
                         'growth', 'strong', 'surge', 'rally', 'jump', 'soar']
        negative_words = ['sell', 'bearish', 'down', 'loss', 'fall', 'drop', 'negative',
                         'weak', 'decline', 'crash', 'plunge', 'tumble', 'sink']
        
        text_lower = text.lower()
        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0
        
        return (positive_count - negative_count) / total


def analyze_sentiment(symbol: str, days: int = 7) -> Dict:
    """情绪分析入口"""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(symbol, days)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='情绪分析')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--days', type=int, default=7, help='天数')
    
    args = parser.parse_args()
    
    result = analyze_sentiment(args.symbol, args.days)
    print(json.dumps(result, indent=2, ensure_ascii=False))
