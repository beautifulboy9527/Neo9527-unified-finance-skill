#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报分析模块 - 饕餮整合自 earnings-preview + earnings-recap
财报预览、财报回顾、历史 beat/miss 追踪
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


class EarningsAnalyzer:
    """
    财报分析器 - 饕餮整合自 earnings-preview + earnings-recap
    
    能力:
    - 财报预览 (预盈预亏分析)
    - 财报回顾 (业绩总结)
    - 历史 beat/miss 追踪
    - 分析师预期汇总
    - 股价反应分析
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.reports_dir = OUTPUT_DIR / 'reports' / 'earnings'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_ticker(self):
        """获取 yfinance ticker 对象"""
        try:
            import yfinance as yf
            return yf.Ticker(self.symbol)
        except ImportError:
            return None
    
    def generate_preview(self) -> Dict:
        """
        生成财报预览报告
        
        Returns:
            财报预览数据
        """
        result = {
            'symbol': self.symbol,
            'report_type': 'earnings_preview',
            'earnings_date': None,
            'company_info': {},
            'estimates': {},
            'historical_beats': [],
            'analyst_sentiment': {},
            'key_metrics_to_watch': [],
            'summary': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            
            ticker = yf.Ticker(self.symbol)
            
            # 获取基础信息
            info = ticker.info
            calendar = ticker.calendar
            
            # 公司信息
            result['company_info'] = {
                'name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE')
            }
            
            # 财报日期
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.index[0] if hasattr(calendar, 'index') else None
                if earnings_date:
                    result['earnings_date'] = str(earnings_date)
            
            # 分析师预期
            try:
                earnings_est = ticker.earnings_estimate
                revenue_est = ticker.revenue_estimate
                
                if earnings_est is not None and not earnings_est.empty:
                    # 当前季度预期
                    current_q = earnings_est.iloc[0] if len(earnings_est) > 0 else None
                    if current_q is not None:
                        result['estimates']['eps'] = {
                            'consensus': current_q.get('avg') if 'avg' in current_q else None,
                            'low': current_q.get('low') if 'low' in current_q else None,
                            'high': current_q.get('high') if 'high' in current_q else None,
                            'analyst_count': current_q.get('numberOfAnalysts') if 'numberOfAnalysts' in current_q else None,
                            'year_ago': current_q.get('yearAgoEps') if 'yearAgoEps' in current_q else None,
                            'growth': current_q.get('growth') if 'growth' in current_q else None
                        }
                
                if revenue_est is not None and not revenue_est.empty:
                    current_q_rev = revenue_est.iloc[0] if len(revenue_est) > 0 else None
                    if current_q_rev is not None:
                        result['estimates']['revenue'] = {
                            'consensus': current_q_rev.get('avg') if 'avg' in current_q_rev else None,
                            'low': current_q_rev.get('low') if 'low' in current_q_rev else None,
                            'high': current_q_rev.get('high') if 'high' in current_q_rev else None,
                            'analyst_count': current_q_rev.get('numberOfAnalysts') if 'numberOfAnalysts' in current_q_rev else None,
                            'year_ago': current_q_rev.get('yearAgoRevenue') if 'yearAgoRevenue' in current_q_rev else None,
                            'growth': current_q_rev.get('growth') if 'growth' in current_q_rev else None
                        }
            except Exception as e:
                result['estimates']['error'] = str(e)
            
            # 历史 beat/miss 记录
            try:
                earnings_hist = ticker.earnings_history
                
                if earnings_hist is not None and not earnings_hist.empty:
                    beats = []
                    for idx, row in earnings_hist.head(4).iterrows():
                        surprise = row.get('surprisePercent', 0) if 'surprisePercent' in row else 0
                        beats.append({
                            'quarter': str(idx),
                            'eps_estimate': row.get('epsEstimate') if 'epsEstimate' in row else None,
                            'eps_actual': row.get('epsActual') if 'epsActual' in row else None,
                            'surprise_pct': round(surprise, 2) if surprise else None,
                            'result': 'Beat' if surprise > 0 else ('Miss' if surprise < 0 else 'In-line')
                        })
                    result['historical_beats'] = beats
                    
                    # 计算平均 surprise
                    if beats:
                        avg_surprise = sum(b['surprise_pct'] for b in beats if b['surprise_pct']) / len([b for b in beats if b['surprise_pct']])
                        beat_count = sum(1 for b in beats if b['result'] == 'Beat')
                        result['beat_summary'] = {
                            'total_quarters': len(beats),
                            'beats': beat_count,
                            'misses': len(beats) - beat_count,
                            'avg_surprise_pct': round(avg_surprise, 2)
                        }
            except Exception as e:
                result['historical_beats'] = [{'error': str(e)}]
            
            # 分析师情绪
            try:
                price_targets = ticker.analyst_price_targets
                recommendations = ticker.recommendations
                
                if price_targets:
                    result['analyst_sentiment']['price_targets'] = {
                        'current': price_targets.get('current'),
                        'low': price_targets.get('low'),
                        'high': price_targets.get('high'),
                        'mean': price_targets.get('mean'),
                        'median': price_targets.get('median')
                    }
                
                if recommendations is not None and not recommendations.empty:
                    latest = recommendations.iloc[-1] if len(recommendations) > 0 else None
                    if latest is not None:
                        result['analyst_sentiment']['recommendations'] = {
                            'strong_buy': latest.get('strongBuy', 0),
                            'buy': latest.get('buy', 0),
                            'hold': latest.get('hold', 0),
                            'sell': latest.get('sell', 0),
                            'strong_sell': latest.get('strongSell', 0)
                        }
            except Exception as e:
                result['analyst_sentiment']['error'] = str(e)
            
            # 关键指标监控
            try:
                quarterly = ticker.quarterly_income_stmt
                if quarterly is not None and not quarterly.empty:
                    metrics = []
                    
                    # 收入趋势
                    revenue = quarterly.loc['Total Revenue'] if 'Total Revenue' in quarterly.index else None
                    if revenue is not None and len(revenue) >= 2:
                        growth = (revenue.iloc[0] - revenue.iloc[1]) / revenue.iloc[1] * 100 if revenue.iloc[1] else None
                        metrics.append({
                            'metric': 'Revenue Growth (QoQ)',
                            'value': f"{growth:.1f}%" if growth else None,
                            'trend': '加速' if growth and growth > 5 else ('放缓' if growth and growth < -5 else '稳定')
                        })
                    
                    # 净利润趋势
                    net_income = quarterly.loc['Net Income'] if 'Net Income' in quarterly.index else None
                    if net_income is not None and len(net_income) >= 2:
                        growth = (net_income.iloc[0] - net_income.iloc[1]) / abs(net_income.iloc[1]) * 100 if net_income.iloc[1] else None
                        metrics.append({
                            'metric': 'Net Income Growth (QoQ)',
                            'value': f"{growth:.1f}%" if growth else None
                        })
                    
                    result['key_metrics_to_watch'] = metrics
            except Exception as e:
                result['key_metrics_to_watch'] = [{'error': str(e)}]
            
            # 总结
            summary_parts = []
            if result.get('earnings_date'):
                summary_parts.append(f"{self.symbol} 将在 {result['earnings_date']} 公布财报")
            else:
                summary_parts.append(f"{self.symbol} 财报预览")
            
            if result.get('estimates', {}).get('eps', {}).get('consensus'):
                eps_est = result['estimates']['eps']['consensus']
                summary_parts.append(f"预期 EPS ${eps_est:.2f}")
            
            if result.get('beat_summary'):
                bs = result['beat_summary']
                summary_parts.append(f"过去 {bs['total_quarters']} 季度 {bs['beats']} 次超预期")
            
            result['summary'] = ' | '.join(summary_parts)
            result['data_source'] = 'yfinance'
            result['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def generate_recap(self) -> Dict:
        """
        生成财报回顾报告
        
        Returns:
            财报回顾数据
        """
        result = {
            'symbol': self.symbol,
            'report_type': 'earnings_recap',
            'earnings_date': None,
            'headline': {},
            'actuals_vs_estimates': {},
            'quarterly_trends': [],
            'price_reaction': {},
            'what_changed': [],
            'summary': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            ticker = yf.Ticker(self.symbol)
            
            # 获取财报历史
            earnings_hist = ticker.earnings_history
            
            if earnings_hist is None or earnings_hist.empty:
                result['error'] = '无财报历史数据'
                return result
            
            # 最新财报
            latest = earnings_hist.iloc[0]
            earnings_date = earnings_hist.index[0]
            
            result['earnings_date'] = str(earnings_date)
            
            # 核心数据
            eps_est = latest.get('epsEstimate') if 'epsEstimate' in latest else None
            eps_act = latest.get('epsActual') if 'epsActual' in latest else None
            surprise = latest.get('surprisePercent') if 'surprisePercent' in latest else None
            
            result['headline'] = {
                'eps_estimate': eps_est,
                'eps_actual': eps_act,
                'surprise_pct': round(surprise, 2) if surprise else None,
                'result': 'Beat' if surprise and surprise > 0 else ('Miss' if surprise and surprise < 0 else 'In-line'),
                'eps_difference': round(eps_act - eps_est, 2) if eps_act and eps_est else None
            }
            
            # 实际 vs 预期
            result['actuals_vs_estimates'] = {
                'eps': {
                    'estimate': eps_est,
                    'actual': eps_act,
                    'surprise': result['headline']['eps_difference']
                }
            }
            
            # 季度趋势
            try:
                quarterly = ticker.quarterly_income_stmt
                if quarterly is not None and not quarterly.empty:
                    trends = []
                    for i, col in enumerate(quarterly.columns[:4]):
                        revenue = quarterly.loc['Total Revenue', col] if 'Total Revenue' in quarterly.index else None
                        net_income = quarterly.loc['Net Income', col] if 'Net Income' in quarterly.index else None
                        
                        # YoY 增长 (如果有数据)
                        yoy_growth = None
                        if i < len(quarterly.columns) - 4:
                            prev_year_col = quarterly.columns[i + 4]
                            prev_revenue = quarterly.loc['Total Revenue', prev_year_col] if 'Total Revenue' in quarterly.index else None
                            if revenue and prev_revenue:
                                yoy_growth = (revenue - prev_revenue) / prev_revenue * 100
                        
                        trends.append({
                            'quarter': str(col.date()) if hasattr(col, 'date') else str(col),
                            'revenue': revenue,
                            'net_income': net_income,
                            'yoy_growth': f"{yoy_growth:.1f}%" if yoy_growth else None
                        })
                    
                    result['quarterly_trends'] = trends
            except Exception as e:
                result['quarterly_trends'] = [{'error': str(e)}]
            
            # 股价反应
            try:
                hist = ticker.history(period="1mo")
                
                if hist is not None and not hist.empty:
                    # 找到财报日前后的价格变化
                    earnings_datetime = pd.to_datetime(earnings_date)
                    
                    # 前后 5 天的数据
                    pre_prices = hist[hist.index < earnings_datetime]['Close']
                    post_prices = hist[hist.index > earnings_datetime]['Close']
                    
                    if not pre_prices.empty and not post_prices.empty:
                        pre_price = pre_prices.iloc[-1]
                        post_price = post_prices.iloc[0]
                        reaction_pct = (post_price - pre_price) / pre_price * 100
                        
                        result['price_reaction'] = {
                            'pre_earnings_price': round(pre_price, 2),
                            'post_earnings_price': round(post_price, 2),
                            'reaction_pct': round(reaction_pct, 2),
                            'direction': '上涨' if reaction_pct > 0 else '下跌'
                        }
            except Exception as e:
                result['price_reaction'] = {'error': str(e)}
            
            # 变化分析
            changes = []
            if result.get('headline', {}).get('result'):
                changes.append(f"EPS {result['headline']['result']} 预期 {abs(result['headline']['surprise_pct']):.1f}%")
            
            if result.get('price_reaction', {}).get('reaction_pct'):
                changes.append(f"财报后股价 {result['price_reaction']['direction']} {abs(result['price_reaction']['reaction_pct']):.1f}%")
            
            result['what_changed'] = changes
            
            # 总结
            summary_parts = [f"{self.symbol} {str(earnings_date)[:10]} 财报:"]
            
            if result.get('headline'):
                h = result['headline']
                if h.get('result'):
                    summary_parts.append(f"EPS {h['result']} {abs(h['surprise_pct']):.1f}%")
            
            if result.get('price_reaction', {}).get('reaction_pct'):
                pr = result['price_reaction']
                summary_parts.append(f"股价 {pr['direction']} {abs(pr['reaction_pct']):.1f}%")
            
            result['summary'] = ' | '.join(summary_parts)
            result['data_source'] = 'yfinance'
            result['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_beat_miss_history(self, quarters: int = 8) -> Dict:
        """
        获取历史 beat/miss 记录
        
        Args:
            quarters: 季度数
            
        Returns:
            历史 beat/miss 数据
        """
        result = {
            'symbol': self.symbol,
            'quarters': [],
            'summary': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            earnings_hist = ticker.earnings_history
            
            if earnings_hist is None or earnings_hist.empty:
                result['error'] = '无财报历史数据'
                return result
            
            quarters_data = []
            beats = 0
            misses = 0
            total_surprise = 0
            
            for idx, row in earnings_hist.head(quarters).iterrows():
                eps_est = row.get('epsEstimate') if 'epsEstimate' in row else None
                eps_act = row.get('epsActual') if 'epsActual' in row else None
                surprise = row.get('surprisePercent') if 'surprisePercent' in row else None
                
                is_beat = surprise > 0 if surprise else False
                is_miss = surprise < 0 if surprise else False
                
                if is_beat:
                    beats += 1
                elif is_miss:
                    misses += 1
                
                if surprise:
                    total_surprise += surprise
                
                quarters_data.append({
                    'quarter': str(idx),
                    'eps_estimate': eps_est,
                    'eps_actual': eps_act,
                    'surprise_pct': round(surprise, 2) if surprise else None,
                    'result': 'Beat' if is_beat else ('Miss' if is_miss else 'In-line')
                })
            
            result['quarters'] = quarters_data
            result['summary'] = {
                'total_quarters': len(quarters_data),
                'beats': beats,
                'misses': misses,
                'beat_rate': round(beats / len(quarters_data) * 100, 1) if quarters_data else 0,
                'avg_surprise_pct': round(total_surprise / len(quarters_data), 2) if quarters_data else 0
            }
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def generate_earnings_preview(symbol: str) -> Dict:
    """生成财报预览"""
    analyzer = EarningsAnalyzer(symbol)
    return analyzer.generate_preview()


def generate_earnings_recap(symbol: str) -> Dict:
    """生成财报回顾"""
    analyzer = EarningsAnalyzer(symbol)
    return analyzer.generate_recap()


def get_beat_miss_history(symbol: str, quarters: int = 8) -> Dict:
    """获取历史 beat/miss"""
    analyzer = EarningsAnalyzer(symbol)
    return analyzer.get_beat_miss_history(quarters)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='财报分析 - 饕餮整合自 earnings-preview + earnings-recap')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--type', choices=['preview', 'recap', 'history'], default='preview', help='报告类型')
    parser.add_argument('--quarters', type=int, default=8, help='历史季度数')
    
    args = parser.parse_args()
    
    analyzer = EarningsAnalyzer(args.symbol)
    
    if args.type == 'preview':
        result = analyzer.generate_preview()
    elif args.type == 'recap':
        result = analyzer.generate_recap()
    elif args.type == 'history':
        result = analyzer.get_beat_miss_history(args.quarters)
    else:
        result = analyzer.generate_preview()
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
