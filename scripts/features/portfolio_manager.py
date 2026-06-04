#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组合管理器 - 投资组合优化与分析
支持组合风险、Markowitz优化、风险平价、Kelly仓位
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class PortfolioManager:
    """
    组合管理器
    
    功能:
    - 组合风险度量 (VaR/CVaR)
    - 相关性矩阵
    - Markowitz 优化
    - 风险平价
    - Kelly 仓位
    """
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化
        
        Args:
            risk_free_rate: 无风险利率 (默认 3%)
        """
        self.risk_free_rate = risk_free_rate
    
    # ========================================
    # 数据获取
    # ========================================
    
    def get_portfolio_prices(
        self,
        symbols: List[str],
        days: int = 365
    ) -> pd.DataFrame:
        """
        获取组合内所有股票的历史价格
        
        Args:
            symbols: 股票代码列表
            days: 历史天数
            
        Returns:
            价格 DataFrame (列为股票代码)
        """
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        import yfinance as yf
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # A股代码转换
        converted_symbols = []
        for symbol in symbols:
            if symbol.isdigit():
                if symbol.startswith('6'):
                    converted_symbols.append(f"{symbol}.SS")
                elif symbol.startswith(('0', '3')):
                    converted_symbols.append(f"{symbol}.SZ")
                else:
                    converted_symbols.append(symbol)
            else:
                converted_symbols.append(symbol)
        
        # 下载数据
        try:
            data = yf.download(
                converted_symbols,
                start=start_date,
                end=end_date,
                progress=False
            )['Close']
            
            if isinstance(data, pd.Series):
                data = data.to_frame()
            
            return data
            
        except Exception as e:
            print(f"⚠️ 获取数据失败: {e}")
            return pd.DataFrame()
    
    # ========================================
    # 组合风险度量
    # ========================================
    
    def calculate_portfolio_risk(
        self,
        symbols: List[str],
        weights: Optional[List[float]] = None,
        days: int = 365
    ) -> Dict:
        """
        计算组合风险
        
        Args:
            symbols: 股票代码列表
            weights: 权重列表 (None = 等权)
            days: 历史天数
            
        Returns:
            风险指标
        """
        prices = self.get_portfolio_prices(symbols, days)
        
        if prices.empty:
            return {'error': '无法获取数据'}
        
        # 计算收益率
        returns = prices.pct_change().dropna()
        
        # 默认等权
        if weights is None:
            weights = [1.0 / len(symbols)] * len(symbols)
        
        weights = np.array(weights)
        
        # 组合收益率
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # 基本统计
        mean_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = (mean_return - self.risk_free_rate) / volatility if volatility > 0 else 0
        
        # VaR (95%, 99%)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        
        # CVaR (期望短缺)
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()
        
        # 最大回撤
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 相关性矩阵
        correlation_matrix = returns.corr()
        
        return {
            'symbols': symbols,
            'weights': weights.tolist(),
            'annual_return': mean_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'max_drawdown': max_drawdown,
            'correlation_matrix': correlation_matrix.to_dict(),
            'portfolio_returns': portfolio_returns.tolist()
        }
    
    # ========================================
    # Markowitz 优化
    # ========================================
    
    def optimize_portfolio(
        self,
        symbols: List[str],
        method: str = 'max_sharpe',
        days: int = 365
    ) -> Dict:
        """
        Markowitz 优化
        
        Args:
            symbols: 股票代码列表
            method: 优化方法 (max_sharpe / min_volatility / max_return)
            days: 历史天数
            
        Returns:
            最优权重
        """
        prices = self.get_portfolio_prices(symbols, days)
        
        if prices.empty:
            return {'error': '无法获取数据'}
        
        returns = prices.pct_change().dropna()
        
        # 简化优化：网格搜索
        n_assets = len(symbols)
        best_weights = None
        best_metric = -float('inf') if method != 'min_volatility' else float('inf')
        
        # 生成随机权重组合
        np.random.seed(42)
        n_simulations = 1000
        
        for _ in range(n_simulations):
            # 随机权重
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            
            # 计算指标
            portfolio_return = (returns.mean() * weights * 252).sum()
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            
            if method == 'max_sharpe':
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
                metric = sharpe
                if metric > best_metric:
                    best_metric = metric
                    best_weights = weights
            
            elif method == 'min_volatility':
                metric = portfolio_vol
                if metric < best_metric:
                    best_metric = metric
                    best_weights = weights
            
            elif method == 'max_return':
                metric = portfolio_return
                if metric > best_metric:
                    best_metric = metric
                    best_weights = weights
        
        if best_weights is None:
            return {'error': '优化失败'}
        
        # 计算最优组合指标
        optimal_return = (returns.mean() * best_weights * 252).sum()
        optimal_vol = np.sqrt(np.dot(best_weights.T, np.dot(returns.cov() * 252, best_weights)))
        optimal_sharpe = (optimal_return - self.risk_free_rate) / optimal_vol if optimal_vol > 0 else 0
        
        return {
            'method': method,
            'symbols': symbols,
            'optimal_weights': best_weights.tolist(),
            'expected_return': optimal_return,
            'volatility': optimal_vol,
            'sharpe_ratio': optimal_sharpe,
            'weight_allocation': {
                symbol: f"{weight*100:.1f}%"
                for symbol, weight in zip(symbols, best_weights)
            }
        }
    
    # ========================================
    # 风险平价
    # ========================================
    
    def risk_parity(
        self,
        symbols: List[str],
        days: int = 365
    ) -> Dict:
        """
        风险平价策略
        
        Args:
            symbols: 股票代码列表
            days: 历史天数
            
        Returns:
            风险平价权重
        """
        prices = self.get_portfolio_prices(symbols, days)
        
        if prices.empty:
            return {'error': '无法获取数据'}
        
        returns = prices.pct_change().dropna()
        
        # 计算每个资产的波动率
        volatilities = returns.std() * np.sqrt(252)
        
        # 风险平价权重 = 1 / 波动率
        risk_weights = 1 / volatilities
        risk_weights = risk_weights / risk_weights.sum()
        
        return {
            'method': 'risk_parity',
            'symbols': symbols,
            'weights': risk_weights.tolist(),
            'weight_allocation': {
                symbol: f"{weight*100:.1f}%"
                for symbol, weight in zip(symbols, risk_weights)
            },
            'volatilities': volatilities.to_dict()
        }
    
    # ========================================
    # Kelly 仓位
    # ========================================
    
    def kelly_criterion(
        self,
        symbol: str,
        days: int = 365
    ) -> Dict:
        """
        Kelly 仓位计算
        
        Kelly% = W - (1-W) / R
        
        Args:
            symbol: 股票代码
            days: 历史天数
            
        Returns:
            Kelly 仓位
        """
        prices = self.get_portfolio_prices([symbol], days)
        
        if prices.empty:
            return {'error': '无法获取数据'}
        
        returns = prices.iloc[:, 0].pct_change().dropna()
        
        # 计算胜率和平均盈亏比
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        win_rate = len(positive_returns) / len(returns)
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 1
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Kelly 公式
        kelly_pct = win_rate - (1 - win_rate) / win_loss_ratio if win_loss_ratio > 0 else 0
        
        # 保守 Kelly (减半)
        conservative_kelly = kelly_pct * 0.5
        
        return {
            'symbol': symbol,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'kelly_pct': kelly_pct,
            'kelly_fraction': min(max(kelly_pct, 0), 1),  # 限制在 0-1
            'conservative_kelly': min(max(conservative_kelly, 0), 0.5),
            'recommendation': {
                'kelly_pct > 0.5': '高置信度，可重仓',
                '0.2 < kelly_pct <= 0.5': '中等置信度，适度仓位',
                'kelly_pct <= 0.2': '低置信度，轻仓或观望',
                'kelly_pct < 0': '不建议持仓'
            }
        }
    
    # ========================================
    # 组合报告
    # ========================================
    
    def generate_portfolio_report(
        self,
        symbols: List[str],
        weights: Optional[List[float]] = None
    ) -> Dict:
        """
        生成组合报告
        
        Args:
            symbols: 股票代码列表
            weights: 权重列表
            
        Returns:
            完整报告
        """
        # 1. 组合风险
        risk = self.calculate_portfolio_risk(symbols, weights)
        
        if 'error' in risk:
            return risk
        
        # 2. Markowitz 优化
        optimal = self.optimize_portfolio(symbols, method='max_sharpe')
        
        # 3. 风险平价
        risk_parity_weights = self.risk_parity(symbols)
        
        # 4. 各股票 Kelly
        kelly_results = {}
        for symbol in symbols:
            kelly_results[symbol] = self.kelly_criterion(symbol)
        
        # 综合评分
        score = 0
        
        # 夏普比率 (40分)
        if risk['sharpe_ratio'] > 1.5:
            score += 40
        elif risk['sharpe_ratio'] > 1.0:
            score += 30
        elif risk['sharpe_ratio'] > 0.5:
            score += 20
        
        # 最大回撤 (30分)
        if risk['max_drawdown'] > -0.10:
            score += 30
        elif risk['max_drawdown'] > -0.15:
            score += 25
        elif risk['max_drawdown'] > -0.20:
            score += 20
        elif risk['max_drawdown'] > -0.30:
            score += 10
        
        # 分散度 (30分) - 相关性越低越好
        corr_matrix = risk['correlation_matrix']
        
        # 获取实际的股票代码键名
        actual_symbols = list(corr_matrix.keys())
        
        avg_correlation = np.mean([
            corr_matrix[s1][s2]
            for i, s1 in enumerate(actual_symbols)
            for j, s2 in enumerate(actual_symbols)
            if i < j
        ]) if len(actual_symbols) > 1 else 0
        
        if avg_correlation < 0.3:
            score += 30
        elif avg_correlation < 0.5:
            score += 20
        elif avg_correlation < 0.7:
            score += 10
        
        return {
            'portfolio': {
                'symbols': symbols,
                'weights': weights or [1/len(symbols)] * len(symbols),
                'score': score,
                'grade': 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D'
            },
            'risk_metrics': risk,
            'optimal_weights': optimal,
            'risk_parity_weights': risk_parity_weights,
            'kelly_analysis': kelly_results,
            'avg_correlation': avg_correlation,
            'recommendation': {
                'score >= 80': '优秀组合，可积极配置',
                'score >= 60': '良好组合，适度配置',
                'score >= 40': '一般组合，谨慎配置',
                'score < 40': '组合质量较差，建议调整'
            }
        }


# ============================================
# 便捷函数
# ============================================

def analyze_portfolio(
    symbols: List[str],
    weights: Optional[List[float]] = None
) -> Dict:
    """分析投资组合"""
    manager = PortfolioManager()
    return manager.generate_portfolio_report(symbols, weights)


def optimize_portfolio(
    symbols: List[str],
    method: str = 'max_sharpe'
) -> Dict:
    """优化投资组合"""
    manager = PortfolioManager()
    return manager.optimize_portfolio(symbols, method)


if __name__ == '__main__':
    # 测试
    symbols = ['002241', '600519', '000858']  # 歌尔、茅台、五粮液
    
    print("=" * 60)
    print("组合分析测试")
    print("=" * 60)
    
    report = analyze_portfolio(symbols)
    
    if 'error' not in report:
        print(f"\n组合评分: {report['portfolio']['score']}/100 (Grade {report['portfolio']['grade']})")
        
        risk = report['risk_metrics']
        print(f"\n风险指标:")
        print(f"  年化收益: {risk['annual_return']*100:.1f}%")
        print(f"  波动率: {risk['volatility']*100:.1f}%")
        print(f"  夏普比率: {risk['sharpe_ratio']:.2f}")
        print(f"  VaR(95%): {risk['var_95']*100:.2f}%")
        print(f"  最大回撤: {risk['max_drawdown']*100:.1f}%")
        
        optimal = report['optimal_weights']
        print(f"\n最优权重 (最大夏普):")
        for symbol, weight in optimal['weight_allocation'].items():
            print(f"  {symbol}: {weight}")
        
        print(f"\n平均相关性: {report['avg_correlation']:.2f}")
    else:
        print(f"错误: {report['error']}")
