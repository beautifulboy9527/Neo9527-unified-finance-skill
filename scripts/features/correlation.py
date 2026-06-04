#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相关性分析模块 - 完整集成自 stock-correlation skill
发现相关股票、分析相关性、板块聚类、滚动相关性
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quote import detect_market


class CorrelationAnalyzer:
    """
    相关性分析器 - 完整集成自 stock-correlation skill
    
    能力:
    - 发现相关股票 (Co-movement Discovery)
    - 两只股票相关性分析
    - 板块聚类分析
    - 滚动相关性分析
    - 条件相关性分析
    """
    
    def __init__(self, symbol: str = None):
        self.symbol = symbol
    
    def _normalize_for_yfinance(self, symbol: str) -> str:
        """
        标准化股票代码为 yfinance 格式
        A股需要添加 .SS 或 .SZ 后缀
        """
        import re
        
        # 如果已经有后缀，直接返回
        if '.' in symbol:
            return symbol
        
        # A股: 6位数字
        if re.match(r'^[0-9]{6}$', symbol):
            if symbol.startswith('6'):
                return f"{symbol}.SS"  # 上海
            elif symbol.startswith(('0', '3')):
                return f"{symbol}.SZ"  # 深圳
            else:
                return f"{symbol}.SS"  # 默认上海
        
        # 港股: 5位数字
        if re.match(r'^[0-9]{5}$', symbol):
            return f"{symbol}.HK"
        
        # 美股: 纯字母，无需转换
        return symbol
    
    def discover_correlated(
        self,
        target_ticker: str,
        peer_tickers: List[str],
        period: str = '1y',
        top_n: int = 10
    ) -> Dict:
        """
        发现相关股票 - Sub-Skill A: Co-movement Discovery
        
        Args:
            target_ticker: 目标股票代码
            peer_tickers: 候选股票列表
            period: 回溯周期
            top_n: 返回数量
            
        Returns:
            相关性排名结果
        """
        result = {
            'target': target_ticker,
            'peers': [],
            'period': period,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            # 标准化股票代码
            yf_target = self._normalize_for_yfinance(target_ticker)
            yf_peers = [self._normalize_for_yfinance(t) for t in peer_tickers]
            
            # 合并并去重
            all_tickers = [yf_target] + [t for t in yf_peers if t != yf_target]
            
            # 下载数据
            data = yf.download(all_tickers, period=period, auto_adjust=True, progress=False)
            
            if data.empty:
                result['error'] = '无历史数据'
                return result
            
            # 提取收盘价
            if isinstance(data.columns, pd.MultiIndex):
                closes = data['Close'].dropna(axis=1, thresh=max(60, len(data) // 2))
            else:
                closes = data[['Close']].dropna()
            
            # 使用标准化后的代码进行检查
            if yf_target not in closes.columns:
                result['error'] = f'目标股票 {target_ticker} 无数据'
                return result
            
            # 计算对数收益率
            returns = np.log(closes / closes.shift(1)).dropna()
            
            if returns.empty or len(returns.columns) < 2:
                result['error'] = '数据不足'
                return result
            
            # 计算相关性
            corr_series = returns.corr()[yf_target].drop(yf_target, errors='ignore')
            
            # 按绝对值排序
            ranked = corr_series.abs().sort_values(ascending=False)
            
            # 构建结果
            peers = []
            for ticker in ranked.index[:top_n]:
                corr_value = corr_series[ticker]
                peers.append({
                    'ticker': ticker,
                    'correlation': round(corr_value, 4),
                    'abs_correlation': round(abs(corr_value), 4),
                    'relationship': 'positive' if corr_value > 0 else 'negative'
                })
            
            result['peers'] = peers
            result['observations'] = len(returns)
            result['data_source'] = 'yfinance'
            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_pair(
        self,
        ticker_a: str,
        ticker_b: str,
        period: str = '1y',
        rolling_window: int = 60
    ) -> Dict:
        """
        两只股票相关性分析 - Sub-Skill B: Return Correlation
        
        Args:
            ticker_a: 股票A
            ticker_b: 股票B
            period: 回溯周期
            rolling_window: 滚动窗口
            
        Returns:
            相关性分析结果
        """
        result = {
            'ticker_a': ticker_a,
            'ticker_b': ticker_b,
            'period': period,
            'metrics': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            # 下载数据
            data = yf.download([ticker_a, ticker_b], period=period, auto_adjust=True, progress=False)
            
            if data.empty:
                result['error'] = '无历史数据'
                return result
            
            # 提取收盘价
            if isinstance(data.columns, pd.MultiIndex):
                closes = data['Close'][[ticker_a, ticker_b]].dropna()
            else:
                closes = data[['Close']].dropna()
            
            if len(closes.columns) < 2:
                result['error'] = '数据不足'
                return result
            
            # 计算对数收益率
            returns = np.log(closes / closes.shift(1)).dropna()
            
            if returns.empty:
                result['error'] = '收益率数据为空'
                return result
            
            # 计算相关性
            corr = returns[ticker_a].corr(returns[ticker_b])
            
            # 计算 Beta
            cov_matrix = returns.cov()
            beta = cov_matrix.loc[ticker_b, ticker_a] / cov_matrix.loc[ticker_a, ticker_a]
            
            # R-squared
            r_squared = corr ** 2
            
            # 滚动相关性
            rolling_corr = returns[ticker_a].rolling(rolling_window).corr(returns[ticker_b])
            
            # 价差 (用于均值回归分析)
            spread = np.log(closes[ticker_a] / closes[ticker_b])
            spread_z = (spread - spread.mean()) / spread.std()
            
            result['metrics'] = {
                'correlation': round(corr, 4),
                'beta': round(beta, 4),
                'r_squared': round(r_squared, 4),
                'rolling_corr_mean': round(rolling_corr.mean(), 4) if not rolling_corr.empty else None,
                'rolling_corr_std': round(rolling_corr.std(), 4) if not rolling_corr.empty else None,
                'rolling_corr_min': round(rolling_corr.min(), 4) if not rolling_corr.empty else None,
                'rolling_corr_max': round(rolling_corr.max(), 4) if not rolling_corr.empty else None,
                'spread_z_current': round(spread_z.iloc[-1], 4) if not spread_z.empty else None,
                'observations': len(returns)
            }
            
            # 相关性强度判断
            if abs(corr) > 0.80:
                strength = 'strong'
                desc = '强相关 - 高度联动'
            elif abs(corr) > 0.50:
                strength = 'moderate'
                desc = '中等相关 - 部分联动'
            else:
                strength = 'weak'
                desc = '弱相关 - 有限联动'
            
            result['strength'] = strength
            result['description'] = desc
            result['data_source'] = 'yfinance'
            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_cluster(
        self,
        tickers: List[str],
        period: str = '1y'
    ) -> Dict:
        """
        板块聚类分析 - Sub-Skill C: Sector Clustering
        
        Args:
            tickers: 股票列表
            period: 回溯周期
            
        Returns:
            聚类分析结果
        """
        result = {
            'tickers': tickers,
            'period': period,
            'correlation_matrix': {},
            'clusters': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            # 下载数据
            data = yf.download(tickers, period=period, auto_adjust=True, progress=False)
            
            if data.empty:
                result['error'] = '无历史数据'
                return result
            
            # 提取收盘价
            if isinstance(data.columns, pd.MultiIndex):
                closes = data['Close'].dropna(axis=1, thresh=max(60, len(data) // 2))
            else:
                closes = data[['Close']].dropna()
            
            # 计算对数收益率
            returns = np.log(closes / closes.shift(1)).dropna()
            
            if returns.empty:
                result['error'] = '收益率数据为空'
                return result
            
            # 计算相关性矩阵
            corr_matrix = returns.corr()
            
            # 转换为字典格式
            matrix_dict = {}
            for i, ticker_a in enumerate(corr_matrix.columns):
                matrix_dict[ticker_a] = {}
                for ticker_b in corr_matrix.columns:
                    matrix_dict[ticker_a][ticker_b] = round(corr_matrix.loc[ticker_a, ticker_b], 4)
            
            result['correlation_matrix'] = matrix_dict
            
            # 找出最强和最弱相关对
            pairs = []
            for i, ticker_a in enumerate(corr_matrix.columns):
                for ticker_b in corr_matrix.columns[i+1:]:
                    corr_value = corr_matrix.loc[ticker_a, ticker_b]
                    pairs.append({
                        'pair': f'{ticker_a}/{ticker_b}',
                        'correlation': round(corr_value, 4)
                    })
            
            # 排序
            pairs_sorted = sorted(pairs, key=lambda x: abs(x['correlation']), reverse=True)
            
            result['strongest_pairs'] = pairs_sorted[:5]
            result['weakest_pairs'] = pairs_sorted[-5:] if len(pairs_sorted) >= 5 else pairs_sorted
            
            # 尝试层次聚类
            try:
                from scipy.cluster.hierarchy import linkage, leaves_list
                from scipy.spatial.distance import squareform
                
                # 距离矩阵
                dist_matrix = 1 - corr_matrix.abs()
                np.fill_diagonal(dist_matrix.values, 0)
                condensed = squareform(dist_matrix.values)
                linkage_matrix = linkage(condensed, method='ward')
                order = leaves_list(linkage_matrix)
                ordered_tickers = [corr_matrix.columns[i] for i in order]
                
                result['clustered_order'] = ordered_tickers
                result['clustering_method'] = 'hierarchical'
                
            except ImportError:
                # 无 scipy，按平均相关性排序
                avg_corr = corr_matrix.abs().mean().sort_values(ascending=False)
                result['clustered_order'] = avg_corr.index.tolist()
                result['clustering_method'] = 'average_correlation'
            
            result['observations'] = len(returns)
            result['data_source'] = 'yfinance'
            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze_rolling(
        self,
        ticker_a: str,
        ticker_b: str,
        period: str = '2y',
        windows: List[int] = [20, 60, 120]
    ) -> Dict:
        """
        滚动相关性分析 - Sub-Skill D: Realized Correlation
        
        Args:
            ticker_a: 股票A
            ticker_b: 股票B
            period: 回溯周期
            windows: 滚动窗口列表
            
        Returns:
            滚动相关性结果
        """
        result = {
            'ticker_a': ticker_a,
            'ticker_b': ticker_b,
            'period': period,
            'rolling_stats': {},
            'regime_correlation': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            # 下载数据
            data = yf.download([ticker_a, ticker_b], period=period, auto_adjust=True, progress=False)
            
            if data.empty:
                result['error'] = '无历史数据'
                return result
            
            # 提取收盘价
            if isinstance(data.columns, pd.MultiIndex):
                closes = data['Close'][[ticker_a, ticker_b]].dropna()
            else:
                closes = data[['Close']].dropna()
            
            # 计算对数收益率
            returns = np.log(closes / closes.shift(1)).dropna()
            
            # 计算不同窗口的滚动相关性
            rolling_stats = {}
            for w in windows:
                rolling = returns[ticker_a].rolling(w).corr(returns[ticker_b])
                rolling_stats[f'{w}d'] = {
                    'current': round(rolling.iloc[-1], 4) if not rolling.empty else None,
                    'mean': round(rolling.mean(), 4) if not rolling.empty else None,
                    'min': round(rolling.min(), 4) if not rolling.empty else None,
                    'max': round(rolling.max(), 4) if not rolling.empty else None,
                    'std': round(rolling.std(), 4) if not rolling.empty else None
                }
            
            result['rolling_stats'] = rolling_stats
            
            # 条件相关性 (基于 ticker_a 的表现)
            ret_a = returns[ticker_a]
            
            regimes = {
                'all_days': pd.Series(True, index=returns.index),
                'up_days': ret_a > 0,
                'down_days': ret_a < 0,
                'high_vol': ret_a.abs() > ret_a.abs().quantile(0.75),
                'low_vol': ret_a.abs() < ret_a.abs().quantile(0.25),
                'large_drop': ret_a < -0.02
            }
            
            regime_corr = {}
            for name, mask in regimes.items():
                subset = returns[mask]
                if len(subset) >= 20:
                    regime_corr[name] = {
                        'correlation': round(subset[ticker_a].corr(subset[ticker_b]), 4),
                        'days': int(mask.sum())
                    }
            
            result['regime_correlation'] = regime_corr
            result['observations'] = len(returns)
            result['data_source'] = 'yfinance'
            result['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result


def discover_correlated(target: str, peers: List[str], period: str = '1y') -> Dict:
    """发现相关股票"""
    analyzer = CorrelationAnalyzer()
    return analyzer.discover_correlated(target, peers, period)


def analyze_pair_correlation(ticker_a: str, ticker_b: str, period: str = '1y') -> Dict:
    """分析两只股票相关性"""
    analyzer = CorrelationAnalyzer()
    return analyzer.analyze_pair(ticker_a, ticker_b, period)


def analyze_cluster(tickers: List[str], period: str = '1y') -> Dict:
    """板块聚类分析"""
    analyzer = CorrelationAnalyzer()
    return analyzer.analyze_cluster(tickers, period)


def analyze_rolling_correlation(ticker_a: str, ticker_b: str, period: str = '2y') -> Dict:
    """滚动相关性分析"""
    analyzer = CorrelationAnalyzer()
    return analyzer.analyze_rolling(ticker_a, ticker_b, period)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='相关性分析 - 完整集成自 stock-correlation skill')
    parser.add_argument('--type', choices=['discover', 'pair', 'cluster', 'rolling'], required=True)
    parser.add_argument('--target', help='目标股票')
    parser.add_argument('--peers', nargs='+', help='候选股票列表')
    parser.add_argument('--ticker-a', help='股票A')
    parser.add_argument('--ticker-b', help='股票B')
    parser.add_argument('--tickers', nargs='+', help='股票列表')
    parser.add_argument('--period', default='1y', help='回溯周期')
    
    args = parser.parse_args()
    
    analyzer = CorrelationAnalyzer()
    
    if args.type == 'discover':
        if not args.target or not args.peers:
            print('错误: discover 需要 --target 和 --peers')
            sys.exit(1)
        result = analyzer.discover_correlated(args.target, args.peers, args.period)
    
    elif args.type == 'pair':
        if not args.ticker_a or not args.ticker_b:
            print('错误: pair 需要 --ticker-a 和 --ticker-b')
            sys.exit(1)
        result = analyzer.analyze_pair(args.ticker_a, args.ticker_b, args.period)
    
    elif args.type == 'cluster':
        if not args.tickers:
            print('错误: cluster 需要 --tickers')
            sys.exit(1)
        result = analyzer.analyze_cluster(args.tickers, args.period)
    
    elif args.type == 'rolling':
        if not args.ticker_a or not args.ticker_b:
            print('错误: rolling 需要 --ticker-a 和 --ticker-b')
            sys.exit(1)
        result = analyzer.analyze_rolling(args.ticker_a, args.ticker_b, args.period)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
