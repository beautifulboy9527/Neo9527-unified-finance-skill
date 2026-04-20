#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业绩效评估模块 - Professional Performance Metrics
对标Bloomberg/机构级绩效分析

包含:
- 风险调整收益指标 (Sharpe, Sortino, Calmar, Information Ratio)
- Alpha/Beta 分析
- 风险指标 (VaR, CVaR, 最大回撤, 下行风险)
- 交易统计 (连续盈亏, 平均持仓, 盈亏分布)
- 基准对比 (相对沪深300/标普500表现)
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from scipy import stats

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class PerformanceMetrics:
    """专业绩效评估"""
    
    def __init__(
        self,
        returns: pd.Series,
        equity_curve: pd.Series = None,
        benchmark_returns: pd.Series = None,
        risk_free_rate: float = 0.03,  # 无风险利率 (年化3%)
        trading_days: int = 252
    ):
        """
        初始化
        
        Args:
            returns: 收益率序列 (日频)
            equity_curve: 权益曲线 (可选)
            benchmark_returns: 基准收益率序列 (可选)
            risk_free_rate: 无风险利率 (年化)
            trading_days: 年交易日数
        """
        self.returns = returns.dropna()
        self.equity_curve = equity_curve
        self.benchmark_returns = benchmark_returns.dropna() if benchmark_returns is not None else None
        self.rf = risk_free_rate
        self.trading_days = trading_days
        
        # 日无风险利率
        self.rf_daily = (1 + risk_free_rate) ** (1/trading_days) - 1
    
    # ========================================
    # 风险调整收益指标
    # ========================================
    
    def sharpe_ratio(self) -> float:
        """
        夏普比率 (Sharpe Ratio)
        
        SR = (Rp - Rf) / σp
        
        解释:
        - < 1: 差
        - 1-2: 好
        - > 2: 优秀
        """
        excess_returns = self.returns - self.rf_daily
        if self.returns.std() == 0:
            return 0.0
        return (excess_returns.mean() / self.returns.std()) * np.sqrt(self.trading_days)
    
    def sortino_ratio(self) -> float:
        """
        索提诺比率 (Sortino Ratio)
        
        只考虑下行风险，更关注亏损波动
        
        SR = (Rp - Rf) / σd
        
        解释:
        - 夏普比率的改进版，不惩罚正向波动
        """
        excess_returns = self.returns - self.rf_daily
        
        # 下行标准差 (只考虑负收益)
        negative_returns = self.returns[self.returns < 0]
        if len(negative_returns) == 0:
            return float('inf')
        
        downside_std = negative_returns.std()
        if downside_std == 0:
            return 0.0
        
        return (excess_returns.mean() / downside_std) * np.sqrt(self.trading_days)
    
    def calmar_ratio(self, max_drawdown: float = None) -> float:
        """
        卡尔玛比率 (Calmar Ratio)
        
        CR = 年化收益 / 最大回撤
        
        解释:
        - 衡量收益与回撤的平衡
        - > 3: 优秀
        - 1-3: 良好
        - < 1: 较差
        """
        if max_drawdown is None:
            max_drawdown = self.max_drawdown()
        
        if max_drawdown == 0:
            return float('inf')
        
        annual_return = self.annual_return()
        return annual_return / abs(max_drawdown)
    
    def information_ratio(self) -> float:
        """
        信息比率 (Information Ratio)
        
        IR = (Rp - Rb) / σ(Rp - Rb)
        
        衡量相对基准的超额收益稳定性
        """
        if self.benchmark_returns is None:
            return None
        
        # 对齐长度
        min_len = min(len(self.returns), len(self.benchmark_returns))
        active_returns = self.returns.iloc[:min_len] - self.benchmark_returns.iloc[:min_len]
        
        if active_returns.std() == 0:
            return 0.0
        
        return (active_returns.mean() / active_returns.std()) * np.sqrt(self.trading_days)
    
    def treynor_ratio(self, beta: float = None) -> float:
        """
        特雷诺比率 (Treynor Ratio)
        
        TR = (Rp - Rf) / β
        
        衡量每单位系统性风险的收益
        """
        if beta is None:
            beta = self.beta()
        
        if beta == 0:
            return None
        
        annual_return = self.annual_return()
        return (annual_return - self.rf) / beta
    
    # ========================================
    # Alpha/Beta 分析
    # ========================================
    
    def beta(self) -> float:
        """
        Beta系数
        
        β = Cov(Rp, Rb) / Var(Rb)
        
        解释:
        - β > 1: 激进 (涨跌幅大于市场)
        - β = 1: 跟随市场
        - β < 1: 防守 (涨跌幅小于市场)
        - β < 0: 反向
        """
        if self.benchmark_returns is None:
            return None
        
        min_len = min(len(self.returns), len(self.benchmark_returns))
        p_returns = self.returns.iloc[:min_len]
        b_returns = self.benchmark_returns.iloc[:min_len]
        
        covariance = np.cov(p_returns, b_returns)[0, 1]
        variance = np.var(b_returns)
        
        if variance == 0:
            return 0.0
        
        return covariance / variance
    
    def alpha(self) -> float:
        """
        Alpha系数 (Jensen's Alpha)
        
        α = Rp - [Rf + β(Rb - Rf)]
        
        解释:
        - α > 0: 跑赢市场 (超额收益)
        - α = 0: 跟随市场
        - α < 0: 跑输市场
        """
        if self.benchmark_returns is None:
            return None
        
        beta = self.beta()
        annual_return = self.annual_return()
        benchmark_return = self.benchmark_returns.mean() * self.trading_days
        
        return annual_return - (self.rf + beta * (benchmark_return - self.rf))
    
    # ========================================
    # 风险指标
    # ========================================
    
    def max_drawdown(self) -> float:
        """
        最大回撤 (Maximum Drawdown)
        
        MDD = max(Peak - Trough) / Peak
        """
        if self.equity_curve is not None:
            equity = self.equity_curve
        else:
            # 从收益率构建权益曲线
            equity = (1 + self.returns).cumprod()
        
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        
        return drawdown.min()
    
    def average_drawdown(self) -> float:
        """平均回撤"""
        if self.equity_curve is not None:
            equity = self.equity_curve
        else:
            equity = (1 + self.returns).cumprod()
        
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        
        return drawdown.mean()
    
    def var(
        self,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        风险价值 (Value at Risk)
        
        在置信水平下，最大可能损失
        
        Args:
            confidence_level: 置信水平 (默认95%)
            method: 计算方法
                - 'historical': 历史模拟法
                - 'parametric': 参数法 (假设正态分布)
        
        解释:
            VaR(95%) = -5% 表示有95%概率损失不超过5%
        """
        if method == 'historical':
            # 历史模拟法
            return -np.percentile(self.returns, (1 - confidence_level) * 100)
        
        elif method == 'parametric':
            # 参数法 (假设正态分布)
            mu = self.returns.mean()
            sigma = self.returns.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            return -(mu + z_score * sigma)
        
        return 0.0
    
    def cvar(
        self,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        条件风险价值 (Conditional VaR / Expected Shortfall)
        
        超过VaR的平均损失，更保守的风险度量
        
        解释:
            CVaR(95%) = -7% 表示在最坏5%情况下平均损失7%
        """
        var = self.var(confidence_level, method)
        
        if method == 'historical':
            # 超过VaR的收益率的平均值
            tail_returns = self.returns[self.returns < -var]
            if len(tail_returns) == 0:
                return var
            return -tail_returns.mean()
        
        elif method == 'parametric':
            mu = self.returns.mean()
            sigma = self.returns.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            
            # CVaR公式 (正态分布)
            cvar = -mu - sigma * stats.norm.pdf(z_score) / (1 - confidence_level)
            return cvar
        
        return var
    
    def downside_deviation(self, target_return: float = 0.0) -> float:
        """
        下行标准差 (Downside Deviation)
        
        只考虑低于目标收益的波动
        """
        downside_returns = self.returns[self.returns < target_return]
        
        if len(downside_returns) == 0:
            return 0.0
        
        return np.sqrt(((downside_returns - target_return) ** 2).mean())
    
    def ulcer_index(self) -> float:
        """
        Ulcer Index
        
        衡量回撤深度和持续时间的综合指标
        """
        if self.equity_curve is not None:
            equity = self.equity_curve
        else:
            equity = (1 + self.returns).cumprod()
        
        running_max = equity.cummax()
        drawdown_pct = (equity - running_max) / running_max * 100
        
        return np.sqrt((drawdown_pct ** 2).mean())
    
    # ========================================
    # 收益指标
    # ========================================
    
    def annual_return(self) -> float:
        """年化收益率"""
        total_return = (1 + self.returns).prod() - 1
        n_years = len(self.returns) / self.trading_days
        return (1 + total_return) ** (1/n_years) - 1
    
    def annual_volatility(self) -> float:
        """年化波动率"""
        return self.returns.std() * np.sqrt(self.trading_days)
    
    def total_return(self) -> float:
        """总收益率"""
        return (1 + self.returns).prod() - 1
    
    def cumulative_return(self) -> float:
        """累计收益率"""
        return self.total_return()
    
    # ========================================
    # 交易统计
    # ========================================
    
    def trade_statistics(
        self,
        trades: List[Dict] = None
    ) -> Dict:
        """
        交易统计
        
        Args:
            trades: 交易列表 [{'profit_pct': 0.05, 'holding_days': 10}, ...]
        """
        if trades is None or len(trades) == 0:
            return {}
        
        profits = [t['profit_pct'] for t in trades]
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p <= 0]
        
        # 连续盈亏
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for p in profits:
            if p > 0:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        # 持仓时间
        holding_days = [t.get('holding_days', 0) for t in trades]
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades) if trades else 0,
            'avg_profit': np.mean(profits),
            'avg_win': np.mean(winning_trades) if winning_trades else 0,
            'avg_loss': np.mean(losing_trades) if losing_trades else 0,
            'profit_factor': abs(np.sum(winning_trades) / np.sum(losing_trades)) if losing_trades and np.sum(losing_trades) != 0 else float('inf'),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_holding_days': np.mean(holding_days),
            'max_holding_days': max(holding_days),
            'min_holding_days': min(holding_days),
            'expectancy': (len(winning_trades)/len(trades) * np.mean(winning_trades) - 
                          len(losing_trades)/len(trades) * abs(np.mean(losing_trades))) if winning_trades and losing_trades else 0
        }
    
    # ========================================
    # 综合评估
    # ========================================
    
    def full_report(
        self,
        trades: List[Dict] = None
    ) -> Dict:
        """
        生成完整绩效报告
        """
        report = {
            # 收益指标
            'total_return': self.total_return(),
            'annual_return': self.annual_return(),
            'annual_volatility': self.annual_volatility(),
            
            # 风险调整收益
            'sharpe_ratio': self.sharpe_ratio(),
            'sortino_ratio': self.sortino_ratio(),
            'calmar_ratio': self.calmar_ratio(),
            'information_ratio': self.information_ratio(),
            'treynor_ratio': self.treynor_ratio(),
            
            # Alpha/Beta
            'alpha': self.alpha(),
            'beta': self.beta(),
            
            # 风险指标
            'max_drawdown': self.max_drawdown(),
            'average_drawdown': self.average_drawdown(),
            'var_95': self.var(0.95),
            'cvar_95': self.cvar(0.95),
            'var_99': self.var(0.99),
            'cvar_99': self.cvar(0.99),
            'downside_deviation': self.downside_deviation(),
            'ulcer_index': self.ulcer_index(),
            
            # 交易统计
            'trade_stats': self.trade_statistics(trades)
        }
        
        # 评级
        report['rating'] = self._calculate_rating(report)
        
        return report
    
    def _calculate_rating(self, report: Dict) -> Dict:
        """
        计算综合评级
        
        评分维度:
        - 收益能力 (30分)
        - 风险控制 (30分)
        - 稳定性 (20分)
        - 效率 (20分)
        """
        score = 0
        
        # 收益能力 (30分)
        annual_return = report.get('annual_return', 0)
        if annual_return > 0.30:  # 年化收益 > 30%
            score += 30
        elif annual_return > 0.20:
            score += 25
        elif annual_return > 0.15:
            score += 20
        elif annual_return > 0.10:
            score += 15
        elif annual_return > 0.05:
            score += 10
        elif annual_return > 0:
            score += 5
        
        # 风险控制 (30分)
        max_dd = report.get('max_drawdown', 0)
        sharpe = report.get('sharpe_ratio', 0)
        
        # 回撤评分 (15分)
        if max_dd > -0.05:  # 回撤 < 5%
            score += 15
        elif max_dd > -0.10:
            score += 12
        elif max_dd > -0.15:
            score += 9
        elif max_dd > -0.20:
            score += 6
        elif max_dd > -0.30:
            score += 3
        
        # 夏普评分 (15分)
        if sharpe > 2.0:
            score += 15
        elif sharpe > 1.5:
            score += 12
        elif sharpe > 1.0:
            score += 9
        elif sharpe > 0.5:
            score += 6
        elif sharpe > 0:
            score += 3
        
        # 稳定性 (20分) - Sortino比率
        sortino = report.get('sortino_ratio', 0)
        if sortino > 2.5:
            score += 20
        elif sortino > 2.0:
            score += 16
        elif sortino > 1.5:
            score += 12
        elif sortino > 1.0:
            score += 8
        elif sortino > 0.5:
            score += 4
        
        # 效率 (20分) - Calmar比率
        calmar = report.get('calmar_ratio', 0)
        if calmar > 3.0:
            score += 20
        elif calmar > 2.0:
            score += 16
        elif calmar > 1.5:
            score += 12
        elif calmar > 1.0:
            score += 8
        elif calmar > 0.5:
            score += 4
        
        # 评级
        if score >= 85:
            grade = 'A+'
            desc = '卓越表现，机构级水平'
        elif score >= 75:
            grade = 'A'
            desc = '优秀表现，推荐使用'
        elif score >= 65:
            grade = 'B+'
            desc = '良好表现，可考虑使用'
        elif score >= 55:
            grade = 'B'
            desc = '中等表现，谨慎使用'
        elif score >= 45:
            grade = 'C'
            desc = '表现一般，需改进'
        else:
            grade = 'D'
            desc = '表现较差，不建议使用'
        
        return {
            'score': score,
            'grade': grade,
            'description': desc
        }


# ============================================
# 便捷函数
# ============================================

def calculate_metrics(
    returns: pd.Series,
    benchmark_returns: pd.Series = None,
    trades: List[Dict] = None
) -> Dict:
    """
    计算绩效指标
    
    Args:
        returns: 收益率序列
        benchmark_returns: 基准收益率
        trades: 交易列表
        
    Returns:
        绩效报告
    """
    pm = PerformanceMetrics(returns, benchmark_returns=benchmark_returns)
    return pm.full_report(trades)


def compare_strategies(
    strategies: Dict[str, pd.Series],
    benchmark_returns: pd.Series = None
) -> pd.DataFrame:
    """
    多策略对比
    
    Args:
        strategies: {'策略名': 收益率序列}
        benchmark_returns: 基准收益率
        
    Returns:
        对比表格
    """
    results = []
    
    for name, returns in strategies.items():
        pm = PerformanceMetrics(returns, benchmark_returns=benchmark_returns)
        report = pm.full_report()
        
        results.append({
            '策略': name,
            '年化收益': f"{report['annual_return']*100:.1f}%",
            '年化波动': f"{report['annual_volatility']*100:.1f}%",
            '夏普比率': f"{report['sharpe_ratio']:.2f}",
            '索提诺': f"{report['sortino_ratio']:.2f}",
            '卡尔玛': f"{report['calmar_ratio']:.2f}",
            '最大回撤': f"{report['max_drawdown']*100:.1f}%",
            'VaR(95%)': f"{report['var_95']*100:.1f}%",
            '评级': report['rating']['grade']
        })
    
    return pd.DataFrame(results)


if __name__ == '__main__':
    # 测试
    np.random.seed(42)
    
    # 模拟收益率序列
    returns = pd.Series(np.random.normal(0.001, 0.02, 252))  # 日收益约0.1%，波动2%
    
    # 模拟基准
    benchmark = pd.Series(np.random.normal(0.0005, 0.015, 252))  # 基准收益较低
    
    # 模拟交易
    trades = [
        {'profit_pct': 0.08, 'holding_days': 10},
        {'profit_pct': -0.03, 'holding_days': 5},
        {'profit_pct': 0.12, 'holding_days': 15},
        {'profit_pct': 0.05, 'holding_days': 8},
        {'profit_pct': -0.02, 'holding_days': 3},
    ]
    
    print("=" * 60)
    print("专业绩效评估测试")
    print("=" * 60)
    
    pm = PerformanceMetrics(returns, benchmark_returns=benchmark)
    report = pm.full_report(trades)
    
    print(f"\n📊 收益指标")
    print(f"  总收益: {report['total_return']*100:.1f}%")
    print(f"  年化收益: {report['annual_return']*100:.1f}%")
    print(f"  年化波动: {report['annual_volatility']*100:.1f}%")
    
    print(f"\n📈 风险调整收益")
    print(f"  夏普比率: {report['sharpe_ratio']:.2f}")
    print(f"  索提诺比率: {report['sortino_ratio']:.2f}")
    print(f"  卡尔玛比率: {report['calmar_ratio']:.2f}")
    print(f"  信息比率: {report['information_ratio']:.2f}" if report['information_ratio'] else "  信息比率: N/A")
    
    print(f"\n🎯 Alpha/Beta")
    print(f"  Alpha: {report['alpha']*100:.1f}%" if report['alpha'] else "  Alpha: N/A")
    print(f"  Beta: {report['beta']:.2f}" if report['beta'] else "  Beta: N/A")
    
    print(f"\n⚠️ 风险指标")
    print(f"  最大回撤: {report['max_drawdown']*100:.1f}%")
    print(f"  VaR(95%): {report['var_95']*100:.1f}%")
    print(f"  CVaR(95%): {report['cvar_95']*100:.1f}%")
    print(f"  下行标准差: {report['downside_deviation']*100:.2f}%")
    print(f"  Ulcer Index: {report['ulcer_index']:.2f}")
    
    print(f"\n📊 交易统计")
    ts = report['trade_stats']
    if ts:
        print(f"  总交易数: {ts['total_trades']}")
        print(f"  胜率: {ts['win_rate']*100:.1f}%")
        print(f"  盈亏比: {ts['profit_factor']:.2f}")
        print(f"  最大连续盈利: {ts['max_consecutive_wins']}")
        print(f"  最大连续亏损: {ts['max_consecutive_losses']}")
        print(f"  平均持仓: {ts['avg_holding_days']:.1f}天")
    
    print(f"\n⭐ 综合评级")
    rating = report['rating']
    print(f"  评分: {rating['score']}/100")
    print(f"  评级: {rating['grade']}")
    print(f"  描述: {rating['description']}")
