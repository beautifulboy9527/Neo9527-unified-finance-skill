#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期权分析模块 - Black-Scholes 定价与 Greeks 计算
Delta, Gamma, Vega, Theta, Rho 敏感性分析
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import math

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class OptionsAnalyzer:
    """
    期权分析器 - Black-Scholes 模型与 Greeks
    
    能力:
    - 期权定价 (Call/Put)
    - Greeks 计算 (Delta, Gamma, Vega, Theta, Rho)
    - 隐含波动率计算
    - 期权链分析
    """
    
    def __init__(self):
        self.data_dir = OUTPUT_DIR / 'data' / 'options'
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def normal_cdf(x: float) -> float:
        """标准正态分布累积函数"""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
    @staticmethod
    def normal_pdf(x: float) -> float:
        """标准正态分布概率密度函数"""
        return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)
    
    def d1(
        self,
        S: float,  # 标的价格
        K: float,  # 行权价
        T: float,  # 到期时间 (年)
        r: float,  # 无风险利率
        sigma: float  # 波动率
    ) -> float:
        """计算 d1"""
        if T <= 0:
            return 0
        return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    def d2(self, d1: float, sigma: float, T: float) -> float:
        """计算 d2"""
        if T <= 0:
            return 0
        return d1 - sigma * math.sqrt(T)
    
    def black_scholes_price(
        self,
        S: float,  # 标的价格
        K: float,  # 行权价
        T: float,  # 到期时间 (年)
        r: float,  # 无风险利率
        sigma: float,  # 波动率
        option_type: str = 'call'  # call/put
    ) -> float:
        """
        Black-Scholes 期权定价
        
        Args:
            S: 标的资产价格
            K: 行权价
            T: 到期时间 (年)
            r: 无风险利率 (小数, 如 0.05)
            sigma: 波动率 (小数, 如 0.2)
            option_type: 'call' 或 'put'
            
        Returns:
            期权价格
        """
        if T <= 0:
            # 到期时期权价值
            if option_type == 'call':
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        d1_val = self.d1(S, K, T, r, sigma)
        d2_val = self.d2(d1_val, sigma, T)
        
        if option_type == 'call':
            price = S * self.normal_cdf(d1_val) - K * math.exp(-r * T) * self.normal_cdf(d2_val)
        else:  # put
            price = K * math.exp(-r * T) * self.normal_cdf(-d2_val) - S * self.normal_cdf(-d1_val)
        
        return price
    
    def calculate_delta(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        计算 Delta
        
        Delta = ∂V/∂S
        Call: N(d1)
        Put: N(d1) - 1
        """
        if T <= 0:
            if option_type == 'call':
                return 1.0 if S > K else 0.0
            else:
                return -1.0 if S < K else 0.0
        
        d1_val = self.d1(S, K, T, r, sigma)
        
        if option_type == 'call':
            return self.normal_cdf(d1_val)
        else:
            return self.normal_cdf(d1_val) - 1
    
    def calculate_gamma(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        计算 Gamma
        
        Gamma = ∂²V/∂S² = N'(d1) / (S * σ * √T)
        """
        if T <= 0:
            return 0.0
        
        d1_val = self.d1(S, K, T, r, sigma)
        
        return self.normal_pdf(d1_val) / (S * sigma * math.sqrt(T))
    
    def calculate_vega(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float
    ) -> float:
        """
        计算 Vega
        
        Vega = ∂V/∂σ = S * N'(d1) * √T
        """
        if T <= 0:
            return 0.0
        
        d1_val = self.d1(S, K, T, r, sigma)
        
        return S * self.normal_pdf(d1_val) * math.sqrt(T)
    
    def calculate_theta(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        计算 Theta (每日衰减)
        
        Theta = -∂V/∂T
        """
        if T <= 0:
            return 0.0
        
        d1_val = self.d1(S, K, T, r, sigma)
        d2_val = self.d2(d1_val, sigma, T)
        
        # 第一项
        term1 = -S * self.normal_pdf(d1_val) * sigma / (2 * math.sqrt(T))
        
        if option_type == 'call':
            term2 = -r * K * math.exp(-r * T) * self.normal_cdf(d2_val)
        else:
            term2 = r * K * math.exp(-r * T) * self.normal_cdf(-d2_val)
        
        # 转换为每日
        return (term1 + term2) / 365
    
    def calculate_rho(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> float:
        """
        计算 Rho
        
        Rho = ∂V/∂r
        """
        if T <= 0:
            return 0.0
        
        d1_val = self.d1(S, K, T, r, sigma)
        d2_val = self.d2(d1_val, sigma, T)
        
        if option_type == 'call':
            return K * T * math.exp(-r * T) * self.normal_cdf(d2_val) / 100
        else:
            return -K * T * math.exp(-r * T) * self.normal_cdf(-d2_val) / 100
    
    def calculate_all_greeks(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = 'call'
    ) -> Dict:
        """
        计算所有 Greeks
        
        Returns:
            {
                'price': float,
                'delta': float,
                'gamma': float,
                'vega': float,
                'theta': float,
                'rho': float
            }
        """
        return {
            'price': round(self.black_scholes_price(S, K, T, r, sigma, option_type), 4),
            'delta': round(self.calculate_delta(S, K, T, r, sigma, option_type), 4),
            'gamma': round(self.calculate_gamma(S, K, T, r, sigma), 4),
            'vega': round(self.calculate_vega(S, K, T, r, sigma), 4),
            'theta': round(self.calculate_theta(S, K, T, r, sigma, option_type), 4),
            'rho': round(self.calculate_rho(S, K, T, r, sigma, option_type), 4),
            'params': {
                'S': S,
                'K': K,
                'T': T,
                'r': r,
                'sigma': sigma,
                'type': option_type
            }
        }
    
    def implied_volatility(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        market_price: float,
        option_type: str = 'call',
        max_iterations: int = 100,
        precision: float = 1e-5
    ) -> Optional[float]:
        """
        计算隐含波动率 (Newton-Raphson 方法)
        
        Args:
            S: 标的价格
            K: 行权价
            T: 到期时间
            r: 无风险利率
            market_price: 市场价格
            option_type: call/put
            
        Returns:
            隐含波动率
        """
        # 初始猜测
        sigma = 0.3
        
        for i in range(max_iterations):
            price = self.black_scholes_price(S, K, T, r, sigma, option_type)
            vega = self.calculate_vega(S, K, T, r, sigma)
            
            if abs(vega) < 1e-10:
                return None
            
            diff = market_price - price
            
            if abs(diff) < precision:
                return sigma
            
            sigma = sigma + diff / vega
            
            # 防止发散
            if sigma < 0.001:
                sigma = 0.001
            elif sigma > 5.0:
                sigma = 5.0
        
        return None
    
    def analyze_option_chain(
        self,
        S: float,
        strikes: List[float],
        T: float,
        r: float,
        sigma: float
    ) -> Dict:
        """
        分析期权链
        
        Args:
            S: 标的价格
            strikes: 行权价列表
            T: 到期时间
            r: 无风险利率
            sigma: 波动率
            
        Returns:
            期权链分析
        """
        calls = []
        puts = []
        
        for K in strikes:
            # Call
            call_greeks = self.calculate_all_greeks(S, K, T, r, sigma, 'call')
            call_greeks['strike'] = K
            call_greeks['moneyness'] = round(S / K, 4)
            calls.append(call_greeks)
            
            # Put
            put_greeks = self.calculate_all_greeks(S, K, T, r, sigma, 'put')
            put_greeks['strike'] = K
            put_greeks['moneyness'] = round(S / K, 4)
            puts.append(put_greeks)
        
        return {
            'spot': S,
            'time_to_expiry': T,
            'risk_free_rate': r,
            'volatility': sigma,
            'calls': calls,
            'puts': puts,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> float:
    """期权定价"""
    analyzer = OptionsAnalyzer()
    return analyzer.black_scholes_price(S, K, T, r, sigma, option_type)


def calculate_all_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> Dict:
    """计算所有 Greeks"""
    analyzer = OptionsAnalyzer()
    return analyzer.calculate_all_greeks(S, K, T, r, sigma, option_type)


def implied_volatility(S: float, K: float, T: float, r: float, market_price: float, option_type: str = 'call') -> Optional[float]:
    """计算隐含波动率"""
    analyzer = OptionsAnalyzer()
    return analyzer.implied_volatility(S, K, T, r, market_price, option_type)


def analyze_option_chain(S: float, strikes: List[float], T: float, r: float, sigma: float) -> Dict:
    """分析期权链"""
    analyzer = OptionsAnalyzer()
    return analyzer.analyze_option_chain(S, strikes, T, r, sigma)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='期权分析 - Black-Scholes 定价与 Greeks')
    parser.add_argument('--price', action='store_true', help='计算期权价格')
    parser.add_argument('--greeks', action='store_true', help='计算 Greeks')
    parser.add_argument('--iv', action='store_true', help='计算隐含波动率')
    parser.add_argument('--chain', action='store_true', help='分析期权链')
    
    parser.add_argument('--S', type=float, default=100, help='标的价格')
    parser.add_argument('--K', type=float, default=100, help='行权价')
    parser.add_argument('--T', type=float, default=0.25, help='到期时间 (年)')
    parser.add_argument('--r', type=float, default=0.05, help='无风险利率')
    parser.add_argument('--sigma', type=float, default=0.2, help='波动率')
    parser.add_argument('--type', choices=['call', 'put'], default='call', help='期权类型')
    parser.add_argument('--market-price', type=float, help='市场价格 (用于 IV 计算)')
    
    args = parser.parse_args()
    
    analyzer = OptionsAnalyzer()
    
    if args.iv and args.market_price:
        iv = analyzer.implied_volatility(args.S, args.K, args.T, args.r, args.market_price, args.type)
        result = {'implied_volatility': iv}
    elif args.chain:
        strikes = [args.S * 0.8, args.S * 0.9, args.S, args.S * 1.1, args.S * 1.2]
        result = analyzer.analyze_option_chain(args.S, strikes, args.T, args.r, args.sigma)
    elif args.greeks:
        result = analyzer.calculate_all_greeks(args.S, args.K, args.T, args.r, args.sigma, args.type)
    else:
        result = analyzer.calculate_all_greeks(args.S, args.K, args.T, args.r, args.sigma, args.type)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
