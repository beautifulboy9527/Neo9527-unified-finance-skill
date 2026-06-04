#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PortfolioSkill - 组合分析 Skill
整合 portfolio_manager.py，扩展健康度评分、风险预警
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 导入现有的 PortfolioManager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from skills.stock_skill.portfolio_manager_legacy import PortfolioManager
except ImportError:
    # 如果导入失败，定义简化版本
    PortfolioManager = None


class PortfolioAnalyzer:
    """
    组合分析器
    
    功能:
    - 组合风险度量 (VaR/CVaR)
    - Markowitz 优化
    - 风险平价
    - Kelly 仓位
    - 健康度评分
    
    参考: scripts/features/portfolio_manager.py
    """
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化
        
        Args:
            risk_free_rate: 无风险利率 (默认 3%)
        """
        self.risk_free_rate = risk_free_rate
        self._portfolio_manager = None
    
    def _get_portfolio_manager(self):
        """获取 PortfolioManager 实例"""
        if PortfolioManager is not None:
            self._portfolio_manager = PortfolioManager(self.risk_free_rate)
        return self._portfolio_manager
    
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
        
        参考: portfolio_manager.py get_portfolio_prices()
        
        Args:
            symbols: 股票代码列表
            days: 历史天数
            
        Returns:
            价格 DataFrame
        """
        import akshare as ak
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        prices_data = {}
        
        for symbol in symbols:
            try:
                # A股
                if symbol.isdigit() and len(symbol) == 6:
                    df = ak.stock_zh_a_hist(
                        symbol=symbol,
                        period="daily",
                        start_date=start_date.strftime('%Y%m%d'),
                        end_date=end_date.strftime('%Y%m%d'),
                        adjust="qfq"
                    )
                    if not df.empty:
                        prices_data[symbol] = df['收盘'].values
                # 美股
                else:
                    import yfinance as yf
                    # A股代码转换
                    converted = symbol
                    if symbol.isdigit():
                        if symbol.startswith('6'):
                            converted = f"{symbol}.SS"
                        elif symbol.startswith(('0', '3')):
                            converted = f"{symbol}.SZ"
                    
                    ticker = yf.Ticker(converted)
                    hist = ticker.history(start=start_date, end=end_date)
                    if not hist.empty:
                        prices_data[symbol] = hist['Close'].values
                        
            except Exception as e:
                print(f"⚠️ 获取 {symbol} 数据失败: {e}")
        
        if not prices_data:
            return pd.DataFrame()
        
        # 构建 DataFrame
        min_len = min(len(v) for v in prices_data.values())
        for symbol in prices_data:
            prices_data[symbol] = prices_data[symbol][-min_len:]
        
        return pd.DataFrame(prices_data)
    
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
        
        参考: portfolio_manager.py calculate_portfolio_risk()
        
        Args:
            symbols: 股票代码列表
            weights: 权重列表 (None = 等权)
            days: 历史天数
            
        Returns:
            风险指标
        """
        prices = self.get_portfolio_prices(symbols, days)
        
        if prices.empty:
            return {'success': False, 'error': '无法获取数据'}
        
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
            'success': True,
            'symbols': symbols,
            'weights': weights.tolist(),
            'annual_return': round(mean_return * 100, 2),
            'volatility': round(volatility * 100, 2),
            'sharpe_ratio': round(sharpe, 2),
            'var_95_pct': round(abs(var_95) * 100, 2),
            'var_99_pct': round(abs(var_99) * 100, 2),
            'cvar_95_pct': round(abs(cvar_95) * 100, 2),
            'max_drawdown_pct': round(abs(max_drawdown) * 100, 2),
            'correlation_matrix': correlation_matrix.to_dict(),
            'health_score': self._calculate_health_score(
                sharpe, volatility, max_drawdown, correlation_matrix, weights
            )
        }
    
    def _calculate_health_score(
        self,
        sharpe: float,
        volatility: float,
        max_drawdown: float,
        correlation_matrix: pd.DataFrame,
        weights: np.ndarray
    ) -> Dict:
        """
        计算组合健康度评分
        
        Args:
            各项风险指标
            
        Returns:
            健康度评分 (0-100)
        """
        # Sharpe 评分 (越高越好)
        sharpe_score = min(100, max(0, sharpe * 25 + 50))
        
        # 波动率评分 (越低越好)
        vol_score = min(100, max(0, 100 - volatility * 2))
        
        # 最大回撤评分 (越小越好)
        dd_score = min(100, max(0, 100 + max_drawdown * 100))
        
        # 集中度评分 (权重分散度)
        max_weight = max(weights)
        concentration_score = min(100, max(0, 100 - max_weight * 100 + 20))
        
        # 相关性评分 (低相关性更好)
        avg_corr = correlation_matrix.mean().mean()
        corr_score = min(100, max(0, 100 - avg_corr * 50))
        
        # 综合评分
        total_score = (
            sharpe_score * 0.3 +
            vol_score * 0.2 +
            dd_score * 0.2 +
            concentration_score * 0.15 +
            corr_score * 0.15
        )
        
        return {
            'total': round(total_score, 1),
            'sharpe': round(sharpe_score, 1),
            'volatility': round(vol_score, 1),
            'drawdown': round(dd_score, 1),
            'concentration': round(concentration_score, 1),
            'correlation': round(corr_score, 1),
            'rating': self._get_rating(total_score)
        }
    
    def _get_rating(self, score: float) -> str:
        """获取评级"""
        if score >= 80:
            return '优秀'
        elif score >= 60:
            return '良好'
        elif score >= 40:
            return '一般'
        else:
            return '较差'
    
    # ========================================
    # 风险预警
    # ========================================
    
    def check_risk_warnings(
        self,
        symbols: List[str],
        weights: List[float],
        days: int = 365
    ) -> List[Dict]:
        """
        检查风险预警
        
        Args:
            symbols: 股票代码列表
            weights: 权重列表
            days: 历史天数
            
        Returns:
            风险预警列表
        """
        warnings = []
        
        # 单股占比过高
        max_weight = max(weights)
        max_weight_symbol = symbols[weights.index(max_weight)]
        if max_weight > 0.4:
            warnings.append({
                'type': 'concentration',
                'severity': '高' if max_weight > 0.5 else '中',
                'symbol': max_weight_symbol,
                'message': f"单股 {max_weight_symbol} 占比 {max_weight*100:.1f}% 过高，建议分散风险"
            })
        
        # 计算相关性
        prices = self.get_portfolio_prices(symbols, days)
        if not prices.empty:
            returns = prices.pct_change().dropna()
            correlation_matrix = returns.corr()
            
            # 高相关性预警
            for i, s1 in enumerate(symbols):
                for j, s2 in enumerate(symbols):
                    if i < j:
                        corr = correlation_matrix.loc[s1, s2]
                        if corr > 0.8:
                            warnings.append({
                                'type': 'correlation',
                                'severity': '中',
                                'symbols': [s1, s2],
                                'message': f"{s1} 与 {s2} 相关性 {corr:.2f} 过高，分散效果有限"
                            })
        
        return warnings
    
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
        
        参考: portfolio_manager.py optimize_portfolio()
        
        Args:
            symbols: 股票代码列表
            method: 优化方法 (max_sharpe / min_volatility / risk_parity)
            days: 历史天数
            
        Returns:
            最优权重
        """
        prices = self.get_portfolio_prices(symbols, days)
        
        if prices.empty:
            return {'success': False, 'error': '无法获取数据'}
        
        returns = prices.pct_change().dropna()
        
        if method == 'risk_parity':
            return self._risk_parity(symbols, returns)
        
        # 网格搜索
        n_assets = len(symbols)
        best_weights = None
        best_metric = -float('inf') if method != 'min_volatility' else float('inf')
        
        np.random.seed(42)
        n_simulations = 1000
        
        for _ in range(n_simulations):
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            
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
        
        if best_weights is None:
            return {'success': False, 'error': '优化失败'}
        
        optimal_return = (returns.mean() * best_weights * 252).sum()
        optimal_vol = np.sqrt(np.dot(best_weights.T, np.dot(returns.cov() * 252, best_weights)))
        optimal_sharpe = (optimal_return - self.risk_free_rate) / optimal_vol if optimal_vol > 0 else 0
        
        return {
            'success': True,
            'method': method,
            'symbols': symbols,
            'optimal_weights': [round(w, 4) for w in best_weights.tolist()],
            'expected_return_pct': round(optimal_return * 100, 2),
            'volatility_pct': round(optimal_vol * 100, 2),
            'sharpe_ratio': round(optimal_sharpe, 2),
            'weight_allocation': {
                symbol: f"{weight*100:.1f}%"
                for symbol, weight in zip(symbols, best_weights)
            }
        }
    
    def _risk_parity(self, symbols: List[str], returns: pd.DataFrame) -> Dict:
        """风险平价策略"""
        volatilities = returns.std() * np.sqrt(252)
        risk_weights = 1 / volatilities
        risk_weights = risk_weights / risk_weights.sum()
        
        return {
            'success': True,
            'method': 'risk_parity',
            'symbols': symbols,
            'optimal_weights': [round(w, 4) for w in risk_weights.tolist()],
            'weight_allocation': {
                symbol: f"{weight*100:.1f}%"
                for symbol, weight in zip(symbols, risk_weights)
            },
            'volatilities': {
                symbol: round(vol * 100, 2)
                for symbol, vol in volatilities.to_dict().items()
            }
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
        
        参考: portfolio_manager.py kelly_criterion()
        
        Args:
            symbol: 股票代码
            days: 历史天数
            
        Returns:
            Kelly 仓位
        """
        prices = self.get_portfolio_prices([symbol], days)
        
        if prices.empty:
            return {'success': False, 'error': '无法获取数据'}
        
        returns = prices.iloc[:, 0].pct_change().dropna()
        
        # 计算胜率和平均盈亏比
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0
        avg_win = positive_returns.mean() if len(positive_returns) > 0 else 0
        avg_loss = abs(negative_returns.mean()) if len(negative_returns) > 0 else 1
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Kelly 公式: K% = W - (1-W) / R
        kelly_pct = win_rate - (1 - win_rate) / win_loss_ratio if win_loss_ratio > 0 else 0
        
        # 保守 Kelly (减半)
        conservative_kelly = kelly_pct * 0.5
        
        return {
            'success': True,
            'symbol': symbol,
            'win_rate': round(win_rate * 100, 2),
            'avg_win_pct': round(avg_win * 100, 4) if avg_win else 0,
            'avg_loss_pct': round(avg_loss * 100, 4) if avg_loss else 0,
            'win_loss_ratio': round(win_loss_ratio, 2),
            'kelly_pct': round(kelly_pct * 100, 2),
            'conservative_kelly_pct': round(conservative_kelly * 100, 2),
            'recommendation': self._kelly_recommendation(kelly_pct)
        }
    
    def _kelly_recommendation(self, kelly_pct: float) -> str:
        """Kelly 仓位建议"""
        if kelly_pct <= 0:
            return "不建议买入 (期望收益为负)"
        elif kelly_pct < 0.1:
            return "保守仓位 (建议 < 10%)"
        elif kelly_pct < 0.25:
            return "中等仓位 (建议 10-25%)"
        else:
            return "较高仓位 (建议 25%+，但需谨慎)"


# ========================================
# Skill 接口
# ========================================

class PortfolioSkill:
    """
    Portfolio Skill - 适配 Hermes Skill 规范
    """
    
    name = "portfolio"
    description = "组合分析 + 风险管理 + 优化"
    version = "1.0.0"
    
    def __init__(self):
        self.analyzer = PortfolioAnalyzer()
    
    def execute(self, action: str, **kwargs) -> Dict:
        """
        执行 Skill
        
        Args:
            action: 操作类型
            kwargs: 参数
            
        Returns:
            执行结果
        """
        actions = {
            'analyze': self._analyze,
            'optimize': self._optimize,
            'kelly': self._kelly,
            'warnings': self._warnings
        }
        
        if action not in actions:
            return {
                'success': False,
                'message': f'未知操作: {action}',
                'available_actions': list(actions.keys())
            }
        
        return actions[action](**kwargs)
    
    def _analyze(self, **kwargs) -> Dict:
        symbols = kwargs.get('symbols', [])
        weights = kwargs.get('weights')
        days = kwargs.get('days', 365)
        
        if not symbols:
            return {'success': False, 'message': '需要提供 symbols 参数'}
        
        return self.analyzer.calculate_portfolio_risk(symbols, weights, days)
    
    def _optimize(self, **kwargs) -> Dict:
        symbols = kwargs.get('symbols', [])
        method = kwargs.get('method', 'max_sharpe')
        days = kwargs.get('days', 365)
        
        if not symbols:
            return {'success': False, 'message': '需要提供 symbols 参数'}
        
        return self.analyzer.optimize_portfolio(symbols, method, days)
    
    def _kelly(self, **kwargs) -> Dict:
        symbol = kwargs.get('symbol')
        days = kwargs.get('days', 365)
        
        if not symbol:
            return {'success': False, 'message': '需要提供 symbol 参数'}
        
        return self.analyzer.kelly_criterion(symbol, days)
    
    def _warnings(self, **kwargs) -> Dict:
        symbols = kwargs.get('symbols', [])
        weights = kwargs.get('weights')
        days = kwargs.get('days', 365)
        
        if not symbols:
            return {'success': False, 'message': '需要提供 symbols 参数'}
        
        if weights is None:
            weights = [1.0 / len(symbols)] * len(symbols)
        
        warnings = self.analyzer.check_risk_warnings(symbols, weights, days)
        return {
            'success': True,
            'warning_count': len(warnings),
            'warnings': warnings
        }


# CLI 测试入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='组合分析')
    parser.add_argument('action', choices=['analyze', 'optimize', 'kelly', 'warnings'])
    parser.add_argument('--symbols', type=str, help='股票代码列表 (逗号分隔)')
    parser.add_argument('--symbol', type=str, help='单个股票代码 (用于 Kelly)')
    parser.add_argument('--weights', type=str, help='权重列表 (逗号分隔)')
    parser.add_argument('--method', type=str, default='max_sharpe', 
                        choices=['max_sharpe', 'min_volatility', 'risk_parity'])
    parser.add_argument('--days', type=int, default=365)
    
    args = parser.parse_args()
    
    skill = PortfolioSkill()
    
    if args.action == 'analyze':
        symbols = args.symbols.split(',') if args.symbols else []
        weights = [float(w) for w in args.weights.split(',')] if args.weights else None
        
        result = skill.execute('analyze', symbols=symbols, weights=weights, days=args.days)
        
        if result['success']:
            print(f"\n📊 组合分析结果:")
            print(f"  预期年化收益: {result['annual_return']}%")
            print(f"  波动率: {result['volatility']}%")
            print(f"  Sharpe: {result['sharpe_ratio']}")
            print(f"  VaR(95%): {result['var_95_pct']}%")
            print(f"  最大回撤: {result['max_drawdown_pct']}%")
            print(f"\n  健康度评分: {result['health_score']['total']} ({result['health_score']['rating']})")
        else:
            print(f"❌ {result['error']}")
    
    elif args.action == 'optimize':
        symbols = args.symbols.split(',') if args.symbols else []
        
        result = skill.execute('optimize', symbols=symbols, method=args.method, days=args.days)
        
        if result['success']:
            print(f"\n📊 优化结果 ({result['method']}):")
            print(f"  预期收益: {result['expected_return_pct']}%")
            print(f"  波动率: {result['volatility_pct']}%")
            print(f"  Sharpe: {result['sharpe_ratio']}")
            print(f"\n  权重分配:")
            for symbol, weight in result['weight_allocation'].items():
                print(f"    {symbol}: {weight}")
        else:
            print(f"❌ {result['error']}")
    
    elif args.action == 'kelly':
        if not args.symbol:
            print("❌ 需要指定 --symbol")
            sys.exit(1)
        
        result = skill.execute('kelly', symbol=args.symbol, days=args.days)
        
        if result['success']:
            print(f"\n📊 Kelly 仓位 ({result['symbol']}):")
            print(f"  胜率: {result['win_rate']}%")
            print(f"  盈亏比: {result['win_loss_ratio']}")
            print(f"  Kelly%: {result['kelly_pct']}%")
            print(f"  保守Kelly: {result['conservative_kelly_pct']}%")
            print(f"\n  建议: {result['recommendation']}")
        else:
            print(f"❌ {result['error']}")
    
    elif args.action == 'warnings':
        symbols = args.symbols.split(',') if args.symbols else []
        weights = [float(w) for w in args.weights.split(',')] if args.weights else None
        
        result = skill.execute('warnings', symbols=symbols, weights=weights, days=args.days)
        
        print(f"\n⚠️ 风险预警 ({result['warning_count']} 个):")
        for warning in result['warnings']:
            print(f"  [{warning['severity']}] {warning['message']}")