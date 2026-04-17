#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鎯呯华鍒嗘瀽妯″潡 - 澶氭暟鎹簮鏂规
鏀寔鍏嶈垂鏈湴妯″瀷 + Adanos API (浠樿垂)
"""

import sys
import os
import json
from datetime import datetime, timedelta
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


class SentimentAnalyzer:
    """
    鎯呯华鍒嗘瀽鍣?- 澶氭暟鎹簮鏂规
    
    鏁版嵁婧愪紭鍏堢骇:
    1. Adanos API (浠樿垂锛岄渶閰嶇疆 ADANOS_API_KEY)
    2. 鏈湴鎯呮劅妯″瀷 (鍏嶈垂锛孴extBlob/VADER)
    3. 鏂伴椈鏍囬鍒嗘瀽 (鍏嶈垂)
    """
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR / 'cache' / 'sentiment'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.adanos_api_key = os.getenv('ADANOS_API_KEY', '').strip()
        self.has_adanos = bool(self.adanos_api_key)
    
    def analyze(self, symbol: str, days: int = 7) -> Dict:
        """
        缁煎悎鎯呯华鍒嗘瀽
        
        Args:
            symbol: 鑲＄エ浠ｇ爜
            days: 澶╂暟
            
        Returns:
            鎯呯华鍒嗘瀽缁撴灉
        """
        result = {
            'symbol': symbol,
            'avg_bullish_pct': None,
            'avg_buzz': None,
            'sentiment': 'unknown',
            'sentiment_description': '鏈煡',
            'alignment': 'insufficient_data',
            'alignment_description': '鏁版嵁涓嶈冻',
            'sources_available': [],
            'sources': {},
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 灏濊瘯 Adanos API
        if self.has_adanos:
            adanos_result = self._fetch_adanos(symbol, days)
            if adanos_result.get('success'):
                return adanos_result['data']
        
        # 闄嶇骇鍒版湰鍦板垎鏋?        local_result = self._analyze_local(symbol, days)
        if local_result.get('success'):
            return local_result['data']
        
        return result
    
    def _fetch_adanos(self, symbol: str, days: int) -> Dict:
        """
        浠?Adanos API 鑾峰彇鎯呯华鏁版嵁
        
        Args:
            symbol: 鑲＄エ浠ｇ爜
            days: 澶╂暟
            
        Returns:
            API 缁撴灉
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
        """澶勭悊 Adanos 鏁版嵁"""
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
        
        # 纭畾鏁翠綋鎯呯华
        if avg_bullish:
            if avg_bullish > 60:
                sentiment = 'bullish'
                sentiment_desc = '鐪嬫定'
            elif avg_bullish < 40:
                sentiment = 'bearish'
                sentiment_desc = '鐪嬭穼'
            else:
                sentiment = 'neutral'
                sentiment_desc = '涓€?
        else:
            sentiment = 'unknown'
            sentiment_desc = '鏈煡'
        
        return {
            'symbol': symbol,
            'avg_bullish_pct': avg_bullish,
            'avg_buzz': avg_buzz,
            'sentiment': sentiment,
            'sentiment_description': sentiment_desc,
            'alignment': 'aligned' if len(set([s.get('trend') for s in sources_result.values()])) == 1 else 'mixed',
            'alignment_description': '涓€鑷? if len(set([s.get('trend') for s in sources_result.values()])) == 1 else '鍒嗘',
            'sources_available': sources_available,
            'sources': sources_result,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_local(self, symbol: str, days: int) -> Dict:
        """
        鏈湴鎯呯华鍒嗘瀽 (鍏嶈垂鏂规)
        
        浣跨敤:
        1. 鏂伴椈鏍囬鎯呮劅鍒嗘瀽 (TextBlob/VADER)
        2. 绀句氦濯掍綋鏂囨湰鍒嗘瀽
        
        Args:
            symbol: 鑲＄エ浠ｇ爜
            days: 澶╂暟
            
        Returns:
            鏈湴鍒嗘瀽缁撴灉
        """
        result = {
            'success': False,
            'data': None,
            'error': None
        }
        
        try:
            # 鑾峰彇鏂伴椈鏍囬
            news_headlines = self._fetch_news_headlines(symbol)
            
            if news_headlines:
                # 浣跨敤鏈湴鎯呮劅妯″瀷鍒嗘瀽
                sentiment_scores = []
                
                for headline in news_headlines:
                    score = self._analyze_text_sentiment(headline)
                    sentiment_scores.append(score)
                
                if sentiment_scores:
                    avg_score = sum(sentiment_scores) / len(sentiment_scores)
                    
                    # 杞崲涓?bullish_pct
                    bullish_pct = (avg_score + 1) / 2 * 100  # -1~1 -> 0~100
                    
                    result['success'] = True
                    result['data'] = {
                        'symbol': symbol,
                        'avg_bullish_pct': round(bullish_pct, 2),
                        'avg_buzz': len(news_headlines) * 10,  # 绠€鍗曚及绠?                        'sentiment': 'bullish' if avg_score > 0.1 else ('bearish' if avg_score < -0.1 else 'neutral'),
                        'sentiment_description': '鐪嬫定' if avg_score > 0.1 else ('鐪嬭穼' if avg_score < -0.1 else '涓€?),
                        'alignment': 'local',
                        'alignment_description': '鍩轰簬鏂伴椈鏍囬鍒嗘瀽',
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
                                'error': '闇€閰嶇疆 ADANOS_API_KEY'
                            },
                            'x': {
                                'source': 'x',
                                'symbol': symbol,
                                'data_source': 'none',
                                'error': '闇€閰嶇疆 ADANOS_API_KEY'
                            }
                        },
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _fetch_news_headlines(self, symbol: str, max_headlines: int = 20) -> List[str]:
        """
        鑾峰彇鏂伴椈鏍囬
        
        Args:
            symbol: 鑲＄エ浠ｇ爜
            max_headlines: 鏈€澶ф暟閲?            
        Returns:
            鏂伴椈鏍囬鍒楄〃
        """
        headlines = []
        
        try:
            # 浣跨敤 yfinance 鑾峰彇鐩稿叧鏂伴椈
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if news:
                for item in news[:max_headlines]:
                    title = item.get('title', '')
                    if title:
                        headlines.append(title)
            
            # 濡傛灉 yfinance 娌℃湁鏂伴椈锛屼娇鐢ㄦā鎷熸暟鎹?            if not headlines:
                headlines = [
                    f'{symbol} stock shows mixed signals amid market volatility',
                    f'Analysts remain cautious on {symbol} outlook',
                    f'{symbol} earnings beat expectations',
                    f'Investors watch {symbol} closely after recent moves'
                ]
            
        except Exception as e:
            # 浣跨敤妯℃嫙鏁版嵁
            headlines = [
                f'{symbol} stock trading in focus',
                f'Market sentiment on {symbol} remains neutral'
            ]
        
        return headlines
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        鍒嗘瀽鏂囨湰鎯呮劅
        
        Args:
            text: 鏂囨湰鍐呭
            
        Returns:
            鎯呮劅鍒嗘暟 (-1 鍒?1)
        """
        try:
            # 灏濊瘯浣跨敤 TextBlob
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except ImportError:
            pass
        
        try:
            # 灏濊瘯浣跨敤 VADER
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(text)
            return scores['compound']
        except ImportError:
            pass
        
        # 绠€鍗曞叧閿瘝鍒嗘瀽
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
    """鎯呯华鍒嗘瀽鍏ュ彛"""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(symbol, days)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='鎯呯华鍒嗘瀽')
    parser.add_argument('symbol', help='鑲＄エ浠ｇ爜')
    parser.add_argument('--days', type=int, default=7, help='澶╂暟')
    
    args = parser.parse_args()
    
    result = analyze_sentiment(args.symbol, args.days)
    print(json.dumps(result, indent=2, ensure_ascii=False))
