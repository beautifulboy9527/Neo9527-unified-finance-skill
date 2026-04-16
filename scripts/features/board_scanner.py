#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打板筛选器 - A股涨停板/强势股筛选
整合自 stock-board skill

功能:
- 涨停板实时扫描
- 强势股筛选 (涨幅>7%)
- 连板数据统计
- 打板市场情绪分析
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class BoardScanner:
    """
    打板筛选器
    
    数据源: 东方财富 API
    功能: 涨停板/强势股/连板/市场情绪
    """
    
    # 东方财富 API
    EASTMONEY_BASE = 'https://push2.eastmoney.com/api/qt/clist/get'
    
    # 市场分类
    MARKET_CODES = {
        'a_share': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股
        'sh': 'm:1+t:2,m:1+t:23',  # 上海
        'sz': 'm:0+t:6,m:0+t:80',  # 深圳
        'gem': 'm:0+t:80',         # 创业板
        'star': 'm:1+t:23'         # 科创板
    }
    
    # 字段映射
    FIELDS = {
        'symbol': 'f12',           # 代码
        'name': 'f14',             # 名称
        'price': 'f2',             # 价格
        'change_pct': 'f3',        # 涨跌幅
        'change': 'f4',            # 涨跌额
        'volume': 'f5',            # 成交量
        'amount': 'f6',            # 成交额
        'amplitude': 'f7',         # 振幅
        'high': 'f15',             # 最高
        'low': 'f16',              # 最低
        'open': 'f17',             # 开盘
        'prev_close': 'f18',       # 昨收
        'volume_ratio': 'f10',     # 量比
        'turnover_rate': 'f8',     # 换手率
        'pe': 'f9',                # 市盈率
        'pb': 'f23',               # 市净率
        'total_mv': 'f20',         # 总市值
        'circ_mv': 'f21',          # 流通市值
        'rise_speed': 'f22',       # 涨速
        'five_change': 'f11',      # 5日涨跌幅
        'continuous': 'f66',       # 连板数
        'board_time': 'f75',       # 首次涨停时间
        'open_count': 'f107',      # 开板次数
        'last_board': 'f168'       # 最后涨停时间
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://data.eastmoney.com/'
        })
    
    def scan_limit_up(
        self,
        market: str = 'a_share',
        limit: int = 100
    ) -> List[Dict]:
        """
        扫描涨停板
        
        Args:
            market: 市场类型 (a_share/sh/sz/gem/star)
            limit: 返回数量
            
        Returns:
            [
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'price': 1500.0,
                    'change_pct': 10.0,
                    'continuous': 1,
                    'board_time': '09:45:30',
                    'open_count': 0,
                    'volume_ratio': 2.5,
                    'turnover_rate': 5.2,
                    'amount': 500000000
                }
            ]
        """
        params = {
            'pn': 1,
            'pz': limit,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',  # 按涨跌幅排序
            'fs': self.MARKET_CODES.get(market, self.MARKET_CODES['a_share']),
            'fields': ','.join(self.FIELDS.values())
        }
        
        try:
            response = self.session.get(
                self.EASTMONEY_BASE,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_limit_up(data)
        
        except Exception as e:
            print(f"扫描涨停板失败: {str(e)}")
        
        return []
    
    def _parse_limit_up(self, data: Dict) -> List[Dict]:
        """解析涨停板数据"""
        results = []
        
        try:
            if 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    # 涨停判断 (涨幅 >= 9.9%)
                    change_pct = float(item.get('f3', 0)) / 100
                    
                    if change_pct >= 9.9:
                        results.append({
                            'symbol': item.get('f12', ''),
                            'name': item.get('f14', ''),
                            'price': float(item.get('f2', 0)) / 100,
                            'change_pct': round(change_pct, 2),
                            'change': float(item.get('f4', 0)) / 100,
                            'high': float(item.get('f15', 0)) / 100,
                            'low': float(item.get('f16', 0)) / 100,
                            'open': float(item.get('f17', 0)) / 100,
                            'volume_ratio': round(float(item.get('f10', 0)), 2),
                            'turnover_rate': round(float(item.get('f8', 0)), 2),
                            'amount': float(item.get('f6', 0)),
                            'continuous': int(item.get('f66', 0)),
                            'board_time': item.get('f75', ''),
                            'open_count': int(item.get('f107', 0)),
                            'rise_speed': float(item.get('f22', 0)) / 100,
                            'total_mv': float(item.get('f20', 0)) / 100000000,  # 亿元
                            'circ_mv': float(item.get('f21', 0)) / 100000000   # 亿元
                        })
        
        except Exception as e:
            print(f"解析涨停板数据失败: {str(e)}")
        
        return results
    
    def scan_strong(
        self,
        market: str = 'a_share',
        min_change: float = 7.0,
        max_change: float = 9.9,
        limit: int = 100
    ) -> List[Dict]:
        """
        扫描强势股 (涨幅 > 7% 且未涨停)
        
        Args:
            market: 市场类型
            min_change: 最小涨幅百分比
            max_change: 最大涨幅百分比
            limit: 返回数量
            
        Returns:
            [
                {
                    'symbol': '000001',
                    'name': '平安银行',
                    'price': 15.5,
                    'change_pct': 8.5,
                    'volume_ratio': 3.2,
                    'amount': 800000000
                }
            ]
        """
        params = {
            'pn': 1,
            'pz': limit,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': self.MARKET_CODES.get(market, self.MARKET_CODES['a_share']),
            'fields': ','.join(self.FIELDS.values())
        }
        
        try:
            response = self.session.get(
                self.EASTMONEY_BASE,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_strong(data, min_change, max_change)
        
        except Exception as e:
            print(f"扫描强势股失败: {str(e)}")
        
        return []
    
    def _parse_strong(
        self,
        data: Dict,
        min_change: float,
        max_change: float
    ) -> List[Dict]:
        """解析强势股数据"""
        results = []
        
        try:
            if 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    change_pct = float(item.get('f3', 0)) / 100
                    
                    # 筛选涨幅在指定范围内
                    if min_change <= change_pct < max_change:
                        results.append({
                            'symbol': item.get('f12', ''),
                            'name': item.get('f14', ''),
                            'price': float(item.get('f2', 0)) / 100,
                            'change_pct': round(change_pct, 2),
                            'change': float(item.get('f4', 0)) / 100,
                            'high': float(item.get('f15', 0)) / 100,
                            'low': float(item.get('f16', 0)) / 100,
                            'volume_ratio': round(float(item.get('f10', 0)), 2),
                            'turnover_rate': round(float(item.get('f8', 0)), 2),
                            'amount': float(item.get('f6', 0)),
                            'rise_speed': float(item.get('f22', 0)) / 100,
                            'total_mv': float(item.get('f20', 0)) / 100000000,
                            'circ_mv': float(item.get('f21', 0)) / 100000000
                        })
        
        except Exception as e:
            print(f"解析强势股数据失败: {str(e)}")
        
        return results
    
    def scan_continuous(
        self,
        min_continuous: int = 2,
        market: str = 'a_share'
    ) -> List[Dict]:
        """
        扫描连板股
        
        Args:
            min_continuous: 最小连板数
            market: 市场类型
            
        Returns:
            [
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'continuous': 3,
                    'change_pct': 10.0,
                    'board_count': 3
                }
            ]
        """
        # 先获取涨停板
        limit_up = self.scan_limit_up(market=market, limit=500)
        
        # 筛选连板
        continuous_boards = [
            stock for stock in limit_up
            if stock['continuous'] >= min_continuous
        ]
        
        # 按连板数排序
        continuous_boards.sort(key=lambda x: x['continuous'], reverse=True)
        
        return continuous_boards
    
    def analyze_market(self) -> Dict:
        """
        分析打板市场整体情况
        
        Returns:
            {
                'limit_up_count': 50,
                'strong_count': 120,
                'continuous_stats': {...},
                'market_sentiment': 'hot',
                'top_continuous': [...],
                'hot_sectors': [...]
            }
        """
        # 扫描涨停板和强势股
        limit_up = self.scan_limit_up(limit=500)
        strong = self.scan_strong(limit=500)
        continuous = self.scan_continuous(min_continuous=2)
        
        # 统计连板分布
        continuous_stats = {}
        for stock in limit_up:
            c = stock['continuous']
            continuous_stats[c] = continuous_stats.get(c, 0) + 1
        
        # 平均连板数
        avg_continuous = 0
        if limit_up:
            total_continuous = sum(s['continuous'] for s in limit_up)
            avg_continuous = total_continuous / len(limit_up)
        
        # 判断市场情绪
        limit_up_count = len(limit_up)
        if limit_up_count >= 100:
            sentiment = 'very_hot'
            sentiment_desc = '非常火热'
        elif limit_up_count >= 70:
            sentiment = 'hot'
            sentiment_desc = '火热'
        elif limit_up_count >= 40:
            sentiment = 'warm'
            sentiment_desc = '温和'
        elif limit_up_count >= 20:
            sentiment = 'cold'
            sentiment_desc = '冷清'
        else:
            sentiment = 'very_cold'
            sentiment_desc = '非常冷清'
        
        # Top 连板股
        top_continuous = continuous[:10]
        
        return {
            'limit_up_count': limit_up_count,
            'strong_count': len(strong),
            'continuous_count': len(continuous),
            'avg_continuous': round(avg_continuous, 2),
            'continuous_stats': continuous_stats,
            'market_sentiment': sentiment,
            'sentiment_desc': sentiment_desc,
            'top_continuous': top_continuous,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_board_opportunities(self) -> List[Dict]:
        """
        识别打板机会
        
        Returns:
            [
                {
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'opportunity_type': 'first_board',  # 首板/连板/开板回封
                    'confidence': 0.8,
                    'reason': '首次涨停，量比适中，封单坚决'
                }
            ]
        """
        opportunities = []
        
        # 获取涨停板
        limit_up = self.scan_limit_up(limit=200)
        
        for stock in limit_up:
            opportunity = None
            
            # 首板机会
            if stock['continuous'] == 1 and stock['open_count'] == 0:
                confidence = self._calculate_first_board_confidence(stock)
                if confidence >= 0.6:
                    opportunity = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'opportunity_type': 'first_board',
                        'confidence': confidence,
                        'reason': '首板，量比适中，封单坚决',
                        'price': stock['price'],
                        'continuous': stock['continuous']
                    }
            
            # 连板机会
            elif stock['continuous'] >= 2:
                confidence = self._calculate_continuous_confidence(stock)
                if confidence >= 0.5:
                    opportunity = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'opportunity_type': 'continuous_board',
                        'confidence': confidence,
                        'reason': f'{stock["continuous"]}连板，市场关注度高',
                        'price': stock['price'],
                        'continuous': stock['continuous']
                    }
            
            # 开板回封机会
            elif stock['open_count'] > 0:
                confidence = self._calculate_reseal_confidence(stock)
                if confidence >= 0.5:
                    opportunity = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'opportunity_type': 'reseal',
                        'confidence': confidence,
                        'reason': f'开板{stock["open_count"]}次后回封',
                        'price': stock['price'],
                        'continuous': stock['continuous']
                    }
            
            if opportunity:
                opportunities.append(opportunity)
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        return opportunities[:20]
    
    def _calculate_first_board_confidence(self, stock: Dict) -> float:
        """计算首板置信度"""
        score = 0.5
        
        # 量比适中 (1-3倍)
        if 1.0 <= stock['volume_ratio'] <= 3.0:
            score += 0.2
        
        # 换手率适中 (3-10%)
        if 3.0 <= stock['turnover_rate'] <= 10.0:
            score += 0.15
        
        # 封板早 (10:30之前)
        if stock['board_time'] and stock['board_time'] < '10:30':
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_continuous_confidence(self, stock: Dict) -> float:
        """计算连板置信度"""
        score = 0.4
        
        # 连板数越多，关注度越高，但风险也越大
        if stock['continuous'] == 2:
            score += 0.3
        elif stock['continuous'] == 3:
            score += 0.2
        else:
            score += 0.1  # 4板以上风险较大
        
        # 封板坚决
        if stock['open_count'] == 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_reseal_confidence(self, stock: Dict) -> float:
        """计算回封置信度"""
        score = 0.3
        
        # 开板次数少
        if stock['open_count'] == 1:
            score += 0.3
        elif stock['open_count'] == 2:
            score += 0.2
        else:
            score += 0.1
        
        # 有连板基础
        if stock['continuous'] >= 2:
            score += 0.2
        
        return min(score, 1.0)


def scan_limit_up(market: str = 'a_share') -> List[Dict]:
    """涨停板扫描入口"""
    scanner = BoardScanner()
    return scanner.scan_limit_up(market=market)


def scan_strong_stocks(min_change: float = 7.0) -> List[Dict]:
    """强势股扫描入口"""
    scanner = BoardScanner()
    return scanner.scan_strong(min_change=min_change)


def scan_continuous_boards(min_continuous: int = 2) -> List[Dict]:
    """连板股扫描入口"""
    scanner = BoardScanner()
    return scanner.scan_continuous(min_continuous=min_continuous)


def analyze_board_market() -> Dict:
    """打板市场分析入口"""
    scanner = BoardScanner()
    return scanner.analyze_market()


def get_board_opportunities() -> List[Dict]:
    """打板机会入口"""
    scanner = BoardScanner()
    return scanner.get_board_opportunities()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='打板筛选')
    parser.add_argument('--type', 
        choices=['limit-up', 'strong', 'continuous', 'market', 'opportunities'], 
        default='limit-up', 
        help='筛选类型')
    parser.add_argument('--market', default='a_share', help='市场类型')
    parser.add_argument('--min-change', type=float, default=7.0, help='最小涨幅')
    parser.add_argument('--min-continuous', type=int, default=2, help='最小连板数')
    
    args = parser.parse_args()
    
    if args.type == 'limit-up':
        result = scan_limit_up(args.market)
    elif args.type == 'strong':
        result = scan_strong_stocks(args.min_change)
    elif args.type == 'continuous':
        result = scan_continuous_boards(args.min_continuous)
    elif args.type == 'market':
        result = analyze_board_market()
    else:
        result = get_board_opportunities()
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
