#!/usr/bin/env python3
"""
Valuation Monitor - 估值监控
计算 PE/PB 历史分位数，判断估值高低
"""

import sys
import os
import pandas as pd
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ValuationMonitor:
    """估值监控器"""
    
    def __init__(self):
        self.cache = {}
    
    def get_pe_percentile(self, symbol: str, period: str = '5y') -> Dict:
        """
        计算 PE 历史分位数
        
        Args:
            symbol: 股票代码
            period: 历史周期 (1y, 3y, 5y, 10y)
        
        Returns:
            包含当前 PE、历史分位数、估值评级
        """
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_pe = info.get('forwardPE') or info.get('trailingPE')
        
        if not current_pe:
            return {'error': '无法获取当前 PE'}
        
        # 获取历史 PE 数据 (简化：使用历史价格估算)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {'error': '无法获取历史数据'}
        
        # 简化计算：使用历史价格/盈利估算
        # 实际应该使用历史 PE 数据
        hist['estimated_pe'] = hist['Close'] / (info.get('trailingEps') or 1)
        
        # 计算分位数
        current_est_pe = hist['estimated_pe'].iloc[-1]
        percentile = (hist['estimated_pe'] < current_est_pe).mean() * 100
        
        # 估值评级
        if percentile < 20:
            rating = '低估'
        elif percentile < 50:
            rating = '合理'
        elif percentile < 80:
            rating = '偏高'
        else:
            rating = '高估'
        
        return {
            'symbol': symbol,
            'current_pe': current_pe,
            'percentile': round(percentile, 1),
            'rating': rating,
            'period': period,
            'pe_range': {
                'min': round(hist['estimated_pe'].min(), 2),
                'max': round(hist['estimated_pe'].max(), 2),
                'median': round(hist['estimated_pe'].median(), 2)
            }
        }
    
    def get_pb_percentile(self, symbol: str, period: str = '5y') -> Dict:
        """
        计算 PB 历史分位数
        
        Args:
            symbol: 股票代码
            period: 历史周期
        
        Returns:
            包含当前 PB、历史分位数、估值评级
        """
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_pb = info.get('priceToBook')
        
        if not current_pb:
            return {'error': '无法获取当前 PB'}
        
        # 获取历史数据
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {'error': '无法获取历史数据'}
        
        # 简化计算
        book_value = info.get('bookValue') or 1
        hist['estimated_pb'] = hist['Close'] / book_value
        
        # 计算分位数
        percentile = (hist['estimated_pb'] < current_pb).mean() * 100
        
        # 估值评级
        if percentile < 20:
            rating = '低估'
        elif percentile < 50:
            rating = '合理'
        elif percentile < 80:
            rating = '偏高'
        else:
            rating = '高估'
        
        return {
            'symbol': symbol,
            'current_pb': current_pb,
            'percentile': round(percentile, 1),
            'rating': rating,
            'period': period,
            'pb_range': {
                'min': round(hist['estimated_pb'].min(), 2),
                'max': round(hist['estimated_pb'].max(), 2),
                'median': round(hist['estimated_pb'].median(), 2)
            }
        }
    
    def get_comprehensive_valuation(self, symbol: str) -> Dict:
        """
        综合估值分析
        
        Args:
            symbol: 股票代码
        
        Returns:
            综合估值报告
        """
        pe_data = self.get_pe_percentile(symbol)
        pb_data = self.get_pb_percentile(symbol)
        
        # 综合评分 (0-100, 越低越低估)
        avg_percentile = (pe_data.get('percentile', 50) + pb_data.get('percentile', 50)) / 2
        
        if avg_percentile < 20:
            overall_rating = '严重低估'
            score = 10
        elif avg_percentile < 40:
            overall_rating = '低估'
            score = 30
        elif avg_percentile < 60:
            overall_rating = '合理'
            score = 50
        elif avg_percentile < 80:
            overall_rating = '偏高'
            score = 70
        else:
            overall_rating = '高估'
            score = 90
        
        return {
            'symbol': symbol,
            'pe_analysis': pe_data,
            'pb_analysis': pb_data,
            'overall': {
                'rating': overall_rating,
                'score': round(score, 1),
                'avg_percentile': round(avg_percentile, 1)
            }
        }


def format_valuation_report(data: Dict) -> str:
    """格式化估值报告"""
    if 'error' in data:
        return f"错误：{data['error']}"
    
    lines = [
        "=" * 60,
        f"  {data['symbol']} 估值分析",
        "=" * 60,
        "",
        "市盈率 (PE) 分析:",
        f"  当前 PE: {data['pe_analysis'].get('current_pe', 'N/A')}",
        f"  历史分位：{data['pe_analysis'].get('percentile', 'N/A')}%",
        f"  估值评级：{data['pe_analysis'].get('rating', 'N/A')}",
        f"  历史范围：{data['pe_analysis'].get('pe_range', {}).get('min', 'N/A')} - {data['pe_analysis'].get('pe_range', {}).get('max', 'N/A')}",
        "",
        "市净率 (PB) 分析:",
        f"  当前 PB: {data['pb_analysis'].get('current_pb', 'N/A')}",
        f"  历史分位：{data['pb_analysis'].get('percentile', 'N/A')}%",
        f"  估值评级：{data['pb_analysis'].get('rating', 'N/A')}",
        f"  历史范围：{data['pb_analysis'].get('pb_range', {}).get('min', 'N/A')} - {data['pb_analysis'].get('pb_range', {}).get('max', 'N/A')}",
        "",
        "-" * 60,
        f"综合估值：{data['overall']['rating']} (评分：{data['overall']['score']})",
        f"平均百分位：{data['overall']['avg_percentile']}%",
        "=" * 60
    ]
    
    return "\n".join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python valuation_monitor.py <股票代码> [综合|pe|pb]")
        print("示例：python valuation_monitor.py AAPL")
        sys.exit(1)
    
    symbol = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else '综合'
    
    monitor = ValuationMonitor()
    
    if mode == 'pe':
        result = monitor.get_pe_percentile(symbol)
        print(f"\n{symbol} PE 分析:")
        print(f"  当前 PE: {result.get('current_pe', 'N/A')}")
        print(f"  历史分位：{result.get('percentile', 'N/A')}%")
        print(f"  估值评级：{result.get('rating', 'N/A')}")
    
    elif mode == 'pb':
        result = monitor.get_pb_percentile(symbol)
        print(f"\n{symbol} PB 分析:")
        print(f"  当前 PB: {result.get('current_pb', 'N/A')}")
        print(f"  历史分位：{result.get('percentile', 'N/A')}%")
        print(f"  估值评级：{result.get('rating', 'N/A')}")
    
    else:
        result = monitor.get_comprehensive_valuation(symbol)
        print(format_valuation_report(result))
