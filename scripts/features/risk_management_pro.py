#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业风险管理模块 - Professional Risk Management
对标机构级风险管理系统

包含:
- VaR计算 (历史模拟、参数法、蒙特卡洛)
- CVaR/ES (条件风险价值)
- 压力测试 (历史情景、假设情景)
- 相关性风险矩阵
- 风险预算分配
- 风险报告生成
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from scipy import stats
import warnings

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

warnings.filterwarnings('ignore')


class RiskManager:
    """专业风险管理"""
    
    def __init__(
        self,
        returns: pd.DataFrame = None,
        positions: Dict[str, float] = None,
        confidence_levels: List[float] = [0.90, 0.95, 0.99]
    ):
        """
        初始化
        
        Args:
            returns: 收益率DataFrame (columns为资产名)
            positions: 持仓 {'资产名': 市值}
            confidence_levels: 置信水平列表
        """
        self.returns = returns
        self.positions = positions or {}
        self.confidence_levels = confidence_levels
        
        # 计算组合权重
        if positions:
            total_value = sum(positions.values())
            self.weights = {k: v/total_value for k, v in positions.items()}
        else:
            self.weights = {}
    
    # ========================================
    # VaR计算方法
    # ========================================
    
    def var_historical(
        self,
        returns: pd.Series = None,
        confidence_level: float = 0.95
    ) -> float:
        """
        VaR - 历史模拟法
        
        直接使用历史收益率分布
        
        优点: 无分布假设，捕捉肥尾
        缺点: 依赖历史数据，极端事件可能不足
        """
        if returns is None:
            returns = self._portfolio_returns()
        
        return -np.percentile(returns, (1 - confidence_level) * 100)
    
    def var_parametric(
        self,
        returns: pd.Series = None,
        confidence_level: float = 0.95,
        distribution: str = 'normal'
    ) -> float:
        """
        VaR - 参数法
        
        假设收益率服从特定分布
        
        Args:
            distribution: 'normal' 或 't' (t分布)
        """
        if returns is None:
            returns = self._portfolio_returns()
        
        mu = returns.mean()
        sigma = returns.std()
        
        if distribution == 'normal':
            z_score = stats.norm.ppf(1 - confidence_level)
            var = -(mu + z_score * sigma)
        
        elif distribution == 't':
            # 拟合t分布
            df, loc, scale = stats.t.fit(returns)
            t_score = stats.t.ppf(1 - confidence_level, df)
            var = -(loc + t_score * scale)
        
        return var
    
    def var_monte_carlo(
        self,
        returns: pd.Series = None,
        confidence_level: float = 0.95,
        simulations: int = 10000,
        days: int = 1
    ) -> float:
        """
        VaR - 蒙特卡洛模拟
        
        基于历史统计参数模拟未来收益
        
        Args:
            simulations: 模拟次数
            days: 预测天数
        """
        if returns is None:
            returns = self._portfolio_returns()
        
        mu = returns.mean()
        sigma = returns.std()
        
        # 模拟未来收益
        simulated_returns = np.random.normal(
            mu * days,
            sigma * np.sqrt(days),
            simulations
        )
        
        return -np.percentile(simulated_returns, (1 - confidence_level) * 100)
    
    def var_cornish_fisher(
        self,
        returns: pd.Series = None,
        confidence_level: float = 0.95
    ) -> float:
        """
        VaR - Cornish-Fisher展开
        
        考虑偏度和峰度的修正VaR，更准确捕捉非正态分布
        """
        if returns is None:
            returns = self._portfolio_returns()
        
        mu = returns.mean()
        sigma = returns.std()
        skew = stats.skew(returns)
        kurt = stats.kurtosis(returns)
        
        z = stats.norm.ppf(1 - confidence_level)
        
        # Cornish-Fisher展开
        z_cf = (z + 
                (z**2 - 1) * skew / 6 +
                (z**3 - 3*z) * (kurt - 3) / 24 -
                (2*z**3 - 5*z) * skew**2 / 36)
        
        return -(mu + z_cf * sigma)
    
    # ========================================
    # CVaR/ES计算
    # ========================================
    
    def cvar(
        self,
        returns: pd.Series = None,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        CVaR (条件风险价值) / ES (预期短缺)
        
        超过VaR的平均损失，更保守的风险度量
        
        Args:
            method: 'historical' 或 'parametric'
        """
        if returns is None:
            returns = self._portfolio_returns()
        
        var = self.var_historical(returns, confidence_level) if method == 'historical' else self.var_parametric(returns, confidence_level)
        
        if method == 'historical':
            tail_returns = returns[returns < -var]
            if len(tail_returns) == 0:
                return var
            return -tail_returns.mean()
        
        elif method == 'parametric':
            mu = returns.mean()
            sigma = returns.std()
            z = stats.norm.ppf(1 - confidence_level)
            
            # CVaR公式 (正态分布)
            return -mu - sigma * stats.norm.pdf(z) / (1 - confidence_level)
    
    # ========================================
    # 压力测试
    # ========================================
    
    def stress_test(
        self,
        positions: Dict[str, float] = None,
        scenarios: Dict[str, Dict[str, float]] = None
    ) -> Dict:
        """
        压力测试
        
        Args:
            positions: {'资产名': 市值}
            scenarios: {'情景名': {'资产名': 收益率}}
        
        Returns:
            各情景下的损失
        """
        if positions is None:
            positions = self.positions
        
        if scenarios is None:
            scenarios = self._default_scenarios()
        
        results = {}
        total_value = sum(positions.values())
        
        for scenario_name, shocks in scenarios.items():
            loss = 0
            for asset, position_value in positions.items():
                shock = shocks.get(asset, 0)
                loss += position_value * shock
            
            results[scenario_name] = {
                'loss': loss,
                'loss_pct': loss / total_value if total_value > 0 else 0
            }
        
        return results
    
    def _default_scenarios(self) -> Dict:
        """默认压力情景"""
        return {
            '2008金融危机': {
                '股票': -0.50,
                '债券': -0.05,
                '商品': -0.30,
                '加密货币': -0.80
            },
            '2020疫情': {
                '股票': -0.35,
                '债券': 0.05,
                '商品': -0.20,
                '加密货币': -0.50
            },
            '加息冲击': {
                '股票': -0.20,
                '债券': -0.15,
                '商品': -0.10,
                '加密货币': -0.40
            },
            '流动性危机': {
                '股票': -0.25,
                '债券': -0.10,
                '商品': -0.35,
                '加密货币': -0.60
            },
            '极端下跌': {
                '股票': -0.30,
                '债券': -0.10,
                '商品': -0.30,
                '加密货币': -0.70
            }
        }
    
    # ========================================
    # 相关性风险
    # ========================================
    
    def correlation_matrix(
        self,
        returns: pd.DataFrame = None
    ) -> pd.DataFrame:
        """相关性矩阵"""
        if returns is None:
            returns = self.returns
        
        return returns.corr()
    
    def covariance_matrix(
        self,
        returns: pd.DataFrame = None,
        annualize: bool = True
    ) -> pd.DataFrame:
        """
        协方差矩阵
        
        Args:
            annualize: 是否年化
        """
        if returns is None:
            returns = self.returns
        
        cov = returns.cov()
        
        if annualize:
            cov = cov * 252
        
        return cov
    
    def portfolio_volatility(
        self,
        weights: Dict[str, float] = None,
        returns: pd.DataFrame = None
    ) -> float:
        """
        组合波动率
        
        σp = √(w'Σw)
        """
        if returns is None:
            returns = self.returns
        
        if weights is None:
            weights = self.weights
        
        # 构建权重向量
        assets = list(returns.columns)
        w = np.array([weights.get(a, 0) for a in assets])
        
        # 协方差矩阵
        cov = returns.cov().values
        
        # 组合波动率
        port_var = w @ cov @ w
        return np.sqrt(port_var) * np.sqrt(252)  # 年化
    
    def marginal_var(
        self,
        asset: str,
        confidence_level: float = 0.95
    ) -> float:
        """
        边际VaR (Marginal VaR)
        
        增加一单位资产i持仓对组合VaR的影响
        """
        if self.returns is None:
            return None
        
        # 组合收益
        port_returns = self._portfolio_returns()
        port_var = self.var_historical(port_returns, confidence_level)
        
        # 资产收益
        asset_returns = self.returns[asset]
        
        # 协方差
        cov = np.cov(port_returns, asset_returns)[0, 1]
        port_std = port_returns.std()
        
        # 边际VaR
        z = stats.norm.ppf(confidence_level)
        return (cov / port_std) * z
    
    def component_var(
        self,
        confidence_level: float = 0.95
    ) -> Dict[str, float]:
        """
        成分VaR (Component VaR)
        
        各资产对组合VaR的贡献
        """
        if not self.positions or self.returns is None:
            return {}
        
        port_var = self.var_historical(self._portfolio_returns(), confidence_level)
        
        component_vars = {}
        for asset in self.weights:
            mvar = self.marginal_var(asset, confidence_level)
            if mvar:
                component_vars[asset] = self.weights[asset] * mvar
        
        return component_vars
    
    # ========================================
    # 风险预算
    # ========================================
    
    def risk_budget(
        self,
        target_volatility: float = 0.15,
        method: str = 'equal_risk'
    ) -> Dict[str, float]:
        """
        风险预算分配
        
        Args:
            target_volatility: 目标波动率
            method: 
                - 'equal_risk': 风险平价 (各资产风险贡献相等)
                - 'equal_weight': 等权重
                - 'min_variance': 最小方差
        
        Returns:
            {'资产名': 权重}
        """
        if self.returns is None:
            return {}
        
        n_assets = len(self.returns.columns)
        
        if method == 'equal_weight':
            return {a: 1/n_assets for a in self.returns.columns}
        
        elif method == 'equal_risk':
            # 风险平价 (简化版: 逆波动率加权)
            vols = self.returns.std() * np.sqrt(252)
            inv_vols = 1 / vols
            weights = inv_vols / inv_vols.sum()
            
            # 缩放到目标波动率
            current_vol = self.portfolio_volatility(dict(zip(self.returns.columns, weights)))
            scale = target_volatility / current_vol
            weights = weights * scale
            
            return dict(zip(self.returns.columns, weights))
        
        elif method == 'min_variance':
            # 最小方差 (简化版)
            from scipy.optimize import minimize
            
            n = n_assets
            cov = self.returns.cov().values * 252
            
            def portfolio_variance(w):
                return w @ cov @ w
            
            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            bounds = tuple((0, 1) for _ in range(n))
            
            result = minimize(
                portfolio_variance,
                x0=np.ones(n) / n,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            return dict(zip(self.returns.columns, result.x))
        
        return {}
    
    # ========================================
    # 风险报告
    # ========================================
    
    def risk_report(
        self,
        portfolio_value: float = 1000000
    ) -> Dict:
        """
        生成完整风险报告
        """
        port_returns = self._portfolio_returns()
        
        report = {
            'portfolio_value': portfolio_value,
            'timestamp': datetime.now().isoformat()
        }
        
        # VaR (多种方法)
        report['var'] = {}
        for cl in self.confidence_levels:
            report['var'][f'{int(cl*100)}%'] = {
                'historical': self.var_historical(port_returns, cl),
                'parametric_normal': self.var_parametric(port_returns, cl, 'normal'),
                'parametric_t': self.var_parametric(port_returns, cl, 't'),
                'monte_carlo': self.var_monte_carlo(port_returns, cl),
                'cornish_fisher': self.var_cornish_fisher(port_returns, cl)
            }
        
        # CVaR
        report['cvar'] = {}
        for cl in self.confidence_levels:
            report['cvar'][f'{int(cl*100)}%'] = {
                'historical': self.cvar(port_returns, cl, 'historical'),
                'parametric': self.cvar(port_returns, cl, 'parametric')
            }
        
        # VaR金额
        report['var_amount'] = {}
        for cl in self.confidence_levels:
            var_pct = self.var_historical(port_returns, cl)
            report['var_amount'][f'{int(cl*100)}%'] = {
                'var': portfolio_value * var_pct,
                'cvar': portfolio_value * self.cvar(port_returns, cl)
            }
        
        # 波动率
        report['volatility'] = {
            'daily': port_returns.std(),
            'annual': port_returns.std() * np.sqrt(252)
        }
        
        # 最大回撤
        equity = (1 + port_returns).cumprod()
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        report['max_drawdown'] = drawdown.min()
        
        # 压力测试
        if self.positions:
            report['stress_test'] = self.stress_test()
        
        # 相关性风险
        if self.returns is not None:
            report['correlation'] = self.correlation_matrix().to_dict()
            report['portfolio_volatility'] = self.portfolio_volatility()
            
            # 成分VaR
            report['component_var'] = self.component_var()
        
        # 风险评级
        report['risk_rating'] = self._calculate_risk_rating(report)
        
        return report
    
    def _calculate_risk_rating(self, report: Dict) -> Dict:
        """计算风险评级"""
        score = 100
        
        # VaR惩罚 (最多扣40分)
        var_95 = report['var']['95%']['historical']
        if var_95 > 0.10:  # VaR > 10%
            score -= 40
        elif var_95 > 0.07:
            score -= 30
        elif var_95 > 0.05:
            score -= 20
        elif var_95 > 0.03:
            score -= 10
        
        # 波动率惩罚 (最多扣30分)
        ann_vol = report['volatility']['annual']
        if ann_vol > 0.40:  # 波动率 > 40%
            score -= 30
        elif ann_vol > 0.30:
            score -= 20
        elif ann_vol > 0.20:
            score -= 10
        elif ann_vol > 0.15:
            score -= 5
        
        # 回撤惩罚 (最多扣30分)
        max_dd = report['max_drawdown']
        if max_dd < -0.40:  # 回撤 > 40%
            score -= 30
        elif max_dd < -0.30:
            score -= 20
        elif max_dd < -0.20:
            score -= 10
        elif max_dd < -0.10:
            score -= 5
        
        # 评级
        if score >= 80:
            grade = '低风险'
            color = 'green'
        elif score >= 60:
            grade = '中等风险'
            color = 'yellow'
        elif score >= 40:
            grade = '较高风险'
            color = 'orange'
        else:
            grade = '高风险'
            color = 'red'
        
        return {
            'score': score,
            'grade': grade,
            'color': color
        }
    
    def _portfolio_returns(self) -> pd.Series:
        """计算组合收益率"""
        if self.returns is None or not self.weights:
            raise ValueError("需要returns和positions")
        
        port_returns = pd.Series(0, index=self.returns.index)
        for asset, weight in self.weights.items():
            if asset in self.returns.columns:
                port_returns += weight * self.returns[asset]
        
        return port_returns


# ============================================
# 便捷函数
# ============================================

def calculate_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
    method: str = 'historical'
) -> float:
    """
    计算VaR
    
    Args:
        returns: 收益率序列
        confidence_level: 置信水平
        method: 'historical', 'parametric', 'monte_carlo', 'cornish_fisher'
    """
    rm = RiskManager()
    
    if method == 'historical':
        return rm.var_historical(returns, confidence_level)
    elif method == 'parametric':
        return rm.var_parametric(returns, confidence_level)
    elif method == 'monte_carlo':
        return rm.var_monte_carlo(returns, confidence_level)
    elif method == 'cornish_fisher':
        return rm.var_cornish_fisher(returns, confidence_level)
    
    return 0.0


def run_stress_test(
    positions: Dict[str, float],
    scenarios: Dict[str, Dict[str, float]] = None
) -> Dict:
    """
    运行压力测试
    """
    rm = RiskManager(positions=positions)
    return rm.stress_test(positions, scenarios)


if __name__ == '__main__':
    # 测试
    np.random.seed(42)
    
    # 模拟多资产收益率
    dates = pd.date_range('2023-01-01', periods=252, freq='D')
    returns = pd.DataFrame({
        '股票': np.random.normal(0.001, 0.02, 252),
        '债券': np.random.normal(0.0003, 0.005, 252),
        '商品': np.random.normal(0.0005, 0.015, 252),
        '加密货币': np.random.normal(0.002, 0.05, 252)
    }, index=dates)
    
    # 持仓
    positions = {
        '股票': 500000,
        '债券': 300000,
        '商品': 100000,
        '加密货币': 100000
    }
    
    print("=" * 60)
    print("专业风险管理测试")
    print("=" * 60)
    
    rm = RiskManager(returns=returns, positions=positions)
    report = rm.risk_report(portfolio_value=1000000)
    
    print(f"\n📊 VaR分析 (组合价值: ¥1,000,000)")
    print("-" * 60)
    for cl, methods in report['var'].items():
        print(f"\n置信水平 {cl}:")
        for method, value in methods.items():
            print(f"  {method:20s}: {value*100:5.2f}% (¥{value*1000000:,.0f})")
    
    print(f"\n📈 CVaR分析")
    print("-" * 60)
    for cl, methods in report['cvar'].items():
        print(f"\n置信水平 {cl}:")
        for method, value in methods.items():
            print(f"  {method:20s}: {value*100:5.2f}%")
    
    print(f"\n⚠️ 风险指标")
    print("-" * 60)
    print(f"  日波动率: {report['volatility']['daily']*100:.2f}%")
    print(f"  年化波动率: {report['volatility']['annual']*100:.1f}%")
    print(f"  最大回撤: {report['max_drawdown']*100:.1f}%")
    
    print(f"\n🔥 压力测试")
    print("-" * 60)
    for scenario, result in report['stress_test'].items():
        print(f"  {scenario:15s}: {result['loss_pct']*100:6.1f}% (¥{result['loss']:,.0f})")
    
    print(f"\n🎯 风险评级")
    print("-" * 60)
    rating = report['risk_rating']
    print(f"  评分: {rating['score']}/100")
    print(f"  评级: {rating['grade']}")
    
    print(f"\n⚖️ 风险预算 (风险平价)")
    print("-" * 60)
    budget = rm.risk_budget(target_volatility=0.15, method='equal_risk')
    for asset, weight in budget.items():
        print(f"  {asset:10s}: {weight*100:5.1f}%")
