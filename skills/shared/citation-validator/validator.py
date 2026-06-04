#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
引用验证体系 - Python实现
用于金融分析报告的数据来源评级和引用规范化
"""

from typing import Dict, List, Optional
from datetime import datetime


class CitationValidator:
    """引用验证器"""
    
    # 数据来源评级映射
    SOURCE_RATINGS = {
        # A级 - 最权威
        'etherscan': 'A',
        'solscan': 'A',
        'blockchain.com': 'A',
        'bscscan': 'A',
        'polygonscan': 'A',
        'sec.gov': 'A',
        'annual report': 'A',
        'whitepaper': 'A',
        'smart contract': 'A',
        
        # B级 - 高可信
        'defillama': 'B',
        'coingecko': 'B',
        'coinmarketcap': 'B',
        'dune analytics': 'B',
        'dune': 'B',
        'glassnode': 'B',
        'messari': 'B',
        'nansen': 'B',
        'tradingview': 'B',
        'yahoo finance': 'B',
        'yfinance': 'B',
        'bloomberg': 'B',
        'reuters': 'B',
        'wind': 'B',
        
        # C级 - 中等可信
        'coindesk': 'C',
        'the block': 'C',
        'decrypt': 'C',
        'cointelegraph': 'C',
        'analyst report': 'C',
        'research report': 'C',
        'investopedia': 'C',
        
        # D级 - 低可信
        'twitter': 'D',
        'x.com': 'D',
        'telegram': 'D',
        'discord': 'D',
        'reddit': 'D',
        'medium': 'D',
        'substack': 'D',
        'youtube': 'D',
        
        # E级 - 未验证
        'unverified': 'E',
        'anonymous': 'E',
        'unknown': 'E',
    }
    
    # 评级颜色映射 (用于HTML)
    RATING_COLORS = {
        'A': '#10b981',  # 绿色
        'B': '#3b82f6',  # 蓝色
        'C': '#f59e0b',  # 黄色
        'D': '#ef4444',  # 红色
        'E': '#6b7280',  # 灰色
    }
    
    # 评级描述
    RATING_DESC = {
        'A': '最权威 (Primary)',
        'B': '高可信 (Secondary)',
        'C': '中等可信 (Tertiary)',
        'D': '低可信 (Informal)',
        'E': '未验证 (Unverified)',
    }
    
    def __init__(self):
        pass
    
    def get_rating(self, source: str) -> str:
        """
        获取数据来源评级
        
        Args:
            source: 数据来源名称
            
        Returns:
            评级 (A/B/C/D/E)
        """
        source_lower = source.lower().strip()
        
        # 直接匹配
        if source_lower in self.SOURCE_RATINGS:
            return self.SOURCE_RATINGS[source_lower]
        
        # 部分匹配
        for key, rating in self.SOURCE_RATINGS.items():
            if key in source_lower:
                return rating
        
        # 默认E级
        return 'E'
    
    def get_rating_color(self, rating: str) -> str:
        """获取评级对应的颜色"""
        return self.RATING_COLORS.get(rating, '#6b7280')
    
    def get_rating_desc(self, rating: str) -> str:
        """获取评级描述"""
        return self.RATING_DESC.get(rating, '未验证')
    
    def cite(
        self, 
        source: str, 
        url: str = '', 
        date: str = '',
        include_warning: bool = True
    ) -> str:
        """
        生成引用标注
        
        Args:
            source: 数据来源名称
            url: 数据来源URL
            date: 数据日期
            include_warning: 是否包含低评级警告
            
        Returns:
            格式化的引用文本
        """
        rating = self.get_rating(source)
        
        parts = [f"> 来源: {source} ({rating}级)"]
        
        if date:
            parts.append(date)
        
        if url:
            parts.append(f"[链接]({url})")
        
        # 低评级警告
        if include_warning and rating in ['D', 'E']:
            parts.append("⚠️ 需要交叉验证")
        
        return " | ".join(parts)
    
    def cite_html(
        self,
        source: str,
        url: str = '',
        date: str = '',
        data_point: str = ''
    ) -> str:
        """
        生成HTML格式的引用卡片
        
        Args:
            source: 数据来源名称
            url: 数据来源URL
            date: 数据日期
            data_point: 数据点描述
            
        Returns:
            HTML格式的引用卡片
        """
        rating = self.get_rating(source)
        color = self.get_rating_color(rating)
        desc = self.get_rating_desc(rating)
        
        html = f'''
        <div class="citation-card" style="background: #1a1a1a; border-radius: 8px; padding: 12px; margin: 8px 0;">
            {f'<div class="data-point" style="color: #fff; margin-bottom: 8px;">{data_point}</div>' if data_point else ''}
            <div class="source-info" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="source-name" style="color: #9ca3af;">{source}</span>
                    <span class="source-rating" style="color: {color}; margin-left: 8px;">({rating}级)</span>
                </div>
                {f'<a href="{url}" target="_blank" style="color: #3b82f6;">查看来源</a>' if url else ''}
            </div>
            {f'<div class="citation-date" style="color: #6b7280; font-size: 12px; margin-top: 4px;">{date}</div>' if date else ''}
            {f'<div class="warning" style="color: #f59e0b; font-size: 12px; margin-top: 4px;">⚠️ 需要交叉验证</div>' if rating in ['D', 'E'] else ''}
        </div>
        '''
        
        return html
    
    def batch_rate(self, sources: List[str]) -> Dict[str, str]:
        """
        批量获取来源评级
        
        Args:
            sources: 来源名称列表
            
        Returns:
            {source: rating} 映射
        """
        return {source: self.get_rating(source) for source in sources}
    
    def validate_core_data(self, source: str) -> Dict:
        """
        验证核心数据来源
        
        Args:
            source: 数据来源名称
            
        Returns:
            验证结果
        """
        rating = self.get_rating(source)
        
        if rating in ['E', 'D']:
            return {
                'valid': False,
                'rating': rating,
                'warning': '核心数据必须来自A/B级来源',
                'suggestion': '请使用官方数据或专业数据平台'
            }
        
        return {
            'valid': True,
            'rating': rating
        }
    
    def validate_conclusion(self, sources: List[str]) -> Dict:
        """
        验证结论是否有足够来源支撑
        
        Args:
            sources: 来源名称列表
            
        Returns:
            验证结果
        """
        unique_sources = set(sources)
        
        if len(unique_sources) < 2:
            return {
                'valid': False,
                'warning': '关键结论需要至少2个独立来源',
                'current_sources': list(unique_sources)
            }
        
        # 检查评级分布
        ratings = [self.get_rating(s) for s in unique_sources]
        high_quality = sum(1 for r in ratings if r in ['A', 'B'])
        
        return {
            'valid': True,
            'source_count': len(unique_sources),
            'high_quality_count': high_quality,
            'ratings': dict(zip(unique_sources, ratings))
        }
    
    def cross_validate(
        self,
        data_point: str,
        sources: List[Dict]
    ) -> Dict:
        """
        交叉验证数据点
        
        Args:
            data_point: 数据点描述
            sources: 来源列表 [{source, url, date, value}, ...]
            
        Returns:
            验证结果
        """
        if not sources:
            return {
                'valid': False,
                'warning': '无数据来源'
            }
        
        # 检查数值一致性
        values = [s.get('value') for s in sources if s.get('value')]
        if values:
            max_val = max(values)
            min_val = min(values)
            variance = (max_val - min_val) / min_val if min_val else 0
            
            if variance > 0.05:  # 5%差异
                return {
                    'valid': False,
                    'warning': f'来源数据差异过大 ({variance*100:.1f}%)',
                    'values': values
                }
        
        # 检查来源评级
        ratings = [self.get_rating(s.get('source', '')) for s in sources]
        if all(r in ['D', 'E'] for r in ratings):
            return {
                'valid': False,
                'warning': '所有来源都是低可信度',
                'ratings': ratings
            }
        
        return {
            'valid': True,
            'source_count': len(sources),
            'best_rating': min(ratings),  # A最好
            'citations': [self.cite(s['source'], s.get('url', ''), s.get('date', '')) for s in sources]
        }


# 便捷函数
def cite(source: str, url: str = '', date: str = '') -> str:
    """快速生成引用"""
    validator = CitationValidator()
    return validator.cite(source, url, date)


def get_rating(source: str) -> str:
    """快速获取评级"""
    validator = CitationValidator()
    return validator.get_rating(source)


# 测试
if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    validator = CitationValidator()
    
    print("=" * 60)
    print("引用验证体系测试")
    print("=" * 60)
    
    # 测试评级
    sources = ['DeFiLlama', 'CoinGecko', 'Twitter @user', 'Etherscan', 'Unknown']
    print("\n来源评级:")
    for source in sources:
        rating = validator.get_rating(source)
        desc = validator.get_rating_desc(rating)
        print(f"  {source}: {rating}级 - {desc}")
    
    # 测试引用生成
    print("\n引用标注示例:")
    print(validator.cite('DeFiLlama', 'https://defillama.com', '2026-04-17'))
    print(validator.cite('Twitter @vitalik', 'https://twitter.com/vitalik', '2026-04-17'))
    
    # 测试批量评级
    print("\n批量评级:")
    ratings = validator.batch_rate(['DeFiLlama', 'CoinGecko', 'Etherscan'])
    print(f"  {ratings}")
    
    # 测试验证
    print("\n核心数据验证:")
    result = validator.validate_core_data('Twitter @user')
    print(f"  Twitter: {result}")
    result = validator.validate_core_data('DeFiLlama')
    print(f"  DeFiLlama: {result}")
