#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinanceToolkit 集成模块
提供 150+ 财务比率、DCF估值、财务异常检测等高级分析
"""

import sys
import os
from typing import Dict, Optional, List
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class FinanceToolkitWrapper:
    """
    FinanceToolkit 包装器
    
    集成 JerBouma/FinanceToolkit 的核心功能:
    - 150+ 财务比率
    - DCF 估值模型
    - Altman Z-Score
    - DuPont 分析
    - 财务异常检测
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            api_key: Financial Modeling Prep API Key (可选，有免费额度)
        """
        self.api_key = api_key
        self.toolkit = None
        self._initialized = False
    
    def _init_toolkit(self, symbol: str):
        """延迟初始化 Toolkit"""
        if self._initialized:
            return
        
        try:
            from financetoolkit import Toolkit
            
            # A股代码转换
            yf_symbol = self._convert_symbol(symbol)
            
            self.toolkit = Toolkit(
                tickers=yf_symbol,
                api_key=self.api_key,
                start_date="2020-01-01",
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            self._initialized = True
            
        except ImportError:
            print("⚠️ FinanceToolkit 未安装，使用 pip install financetoolkit")
            self._initialized = False
        except Exception as e:
            print(f"⚠️ Toolkit 初始化失败: {e}")
            self._initialized = False
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换 A股代码为 yfinance 格式"""
        if not symbol.isdigit():
            return symbol
        
        if symbol.startswith('6'):
            return f"{symbol}.SS"
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"
        elif len(symbol) == 5:
            return f"{symbol}.HK"
        else:
            return symbol
    
    # ========================================
    # 财务比率
    # ========================================
    
    def get_valuation_ratios(self, symbol: str) -> Dict:
        """
        获取估值比率
        
        Returns:
            PE, PB, PS, EV/EBITDA, PEG, 股息率等
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return self._fallback_valuation(symbol)
        
        try:
            ratios = self.toolkit.ratios.collect_valuation_ratios()
            
            # 转换为字典
            result = {}
            if not ratios.empty:
                latest = ratios.iloc[-1]
                result = {
                    'pe_ratio': self._safe_float(latest.get('Price to Earnings Ratio')),
                    'pb_ratio': self._safe_float(latest.get('Price to Book Ratio')),
                    'ps_ratio': self._safe_float(latest.get('Price to Sales Ratio')),
                    'ev_ebitda': self._safe_float(latest.get('Enterprise Value to EBITDA')),
                    'peg_ratio': self._safe_float(latest.get('Price Earnings to Growth Ratio')),
                    'dividend_yield': self._safe_float(latest.get('Dividend Yield')),
                    'data_source': 'FinanceToolkit'
                }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'data_source': 'FinanceToolkit'}
    
    def get_profitability_ratios(self, symbol: str) -> Dict:
        """
        获取盈利能力比率
        
        Returns:
            ROE, ROA, Gross Margin, Net Margin, Operating Margin等
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return self._fallback_profitability(symbol)
        
        try:
            ratios = self.toolkit.ratios.collect_profitability_ratios()
            
            result = {}
            if not ratios.empty:
                latest = ratios.iloc[-1]
                result = {
                    'roe': self._safe_float(latest.get('Return on Equity')),
                    'roa': self._safe_float(latest.get('Return on Assets')),
                    'gross_margin': self._safe_float(latest.get('Gross Margin')),
                    'net_margin': self._safe_float(latest.get('Net Profit Margin')),
                    'operating_margin': self._safe_float(latest.get('Operating Margin')),
                    'data_source': 'FinanceToolkit'
                }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'data_source': 'FinanceToolkit'}
    
    def get_leverage_ratios(self, symbol: str) -> Dict:
        """
        获取杠杆比率
        
        Returns:
            Debt to Equity, Debt to Assets, Interest Coverage等
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return {}
        
        try:
            ratios = self.toolkit.ratios.collect_solvency_ratios()
            
            result = {}
            if not ratios.empty:
                latest = ratios.iloc[-1]
                result = {
                    'debt_to_equity': self._safe_float(latest.get('Debt to Equity Ratio')),
                    'debt_to_assets': self._safe_float(latest.get('Debt to Assets Ratio')),
                    'interest_coverage': self._safe_float(latest.get('Interest Coverage Ratio')),
                    'equity_multiplier': self._safe_float(latest.get('Equity Multiplier')),
                    'data_source': 'FinanceToolkit'
                }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'data_source': 'FinanceToolkit'}
    
    # ========================================
    # 高级分析
    # ========================================
    
    def get_dupont_analysis(self, symbol: str) -> Dict:
        """
        DuPont 分析 - ROE 拆解
        
        ROE = 净利率 × 资产周转率 × 权益乘数
        
        Returns:
            三因子拆解结果
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return {}
        
        try:
            # 获取基础数据
            profitability = self.get_profitability_ratios(symbol)
            leverage = self.get_leverage_ratios(symbol)
            
            # DuPont 分解
            roe = profitability.get('roe', 0)
            net_margin = profitability.get('net_margin', 0)
            equity_multiplier = leverage.get('equity_multiplier', 1)
            
            # 估算资产周转率
            asset_turnover = roe / (net_margin * equity_multiplier) if net_margin > 0 else 0
            
            return {
                'roe': roe,
                'net_margin': net_margin,
                'asset_turnover': asset_turnover,
                'equity_multiplier': equity_multiplier,
                'interpretation': {
                    'profitability': '强' if net_margin > 15 else '中' if net_margin > 8 else '弱',
                    'efficiency': '高' if asset_turnover > 1 else '中' if asset_turnover > 0.5 else '低',
                    'leverage': '高' if equity_multiplier > 3 else '中' if equity_multiplier > 2 else '低'
                },
                'data_source': 'FinanceToolkit'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_altman_zscore(self, symbol: str) -> Dict:
        """
        Altman Z-Score - 破产预警
        
        Z > 2.99: 安全
        1.81 < Z < 2.99: 灰色区域
        Z < 1.81: 高风险
        
        Returns:
            Z-Score 和风险评估
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return {}
        
        try:
            models = self.toolkit.models.get_altman_z_score()
            
            result = {}
            if not models.empty:
                latest = models.iloc[-1]
                z_score = self._safe_float(latest.iloc[0]) if len(latest) > 0 else 0
                
                # 风险评估
                if z_score > 2.99:
                    risk_level = '安全'
                elif z_score > 1.81:
                    risk_level = '中等风险'
                else:
                    risk_level = '高风险'
                
                result = {
                    'z_score': z_score,
                    'risk_level': risk_level,
                    'warning': None if z_score > 2.99 else '⚠️ 建议关注财务健康',
                    'data_source': 'FinanceToolkit'
                }
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_dcf_valuation(self, symbol: str, growth_rate: float = 0.10) -> Dict:
        """
        DCF 估值模型
        
        Args:
            symbol: 股票代码
            growth_rate: 预期增长率 (默认 10%)
            
        Returns:
            内在价值、安全边际等
        """
        self._init_toolkit(symbol)
        
        if not self.toolkit:
            return {}
        
        try:
            # 获取 DCF 模型
            models = self.toolkit.models.discounted_cash_flow(
                growth_rate=growth_rate
            )
            
            result = {}
            if not models.empty:
                latest = models.iloc[-1]
                
                intrinsic_value = self._safe_float(latest.get('Intrinsic Value'))
                current_price = self._safe_float(latest.get('Stock Price'))
                
                # 安全边际
                margin_of_safety = 0
                if current_price and intrinsic_value:
                    margin_of_safety = (intrinsic_value - current_price) / current_price
                
                result = {
                    'intrinsic_value': intrinsic_value,
                    'current_price': current_price,
                    'margin_of_safety': margin_of_safety,
                    'undervalued': margin_of_safety > 0.2,
                    'interpretation': '低估' if margin_of_safety > 0.2 else '合理' if margin_of_safety > 0 else '高估',
                    'data_source': 'FinanceToolkit'
                }
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    # ========================================
    # 综合分析
    # ========================================
    
    def analyze_fundamentals(self, symbol: str) -> Dict:
        """
        综合基本面分析
        
        Returns:
            多维度基本面评分
        """
        self._init_toolkit(symbol)
        
        # 获取各类比率
        valuation = self.get_valuation_ratios(symbol)
        profitability = self.get_profitability_ratios(symbol)
        leverage = self.get_leverage_ratios(symbol)
        dupont = self.get_dupont_analysis(symbol)
        zscore = self.get_altman_zscore(symbol)
        
        # 计算综合评分
        score = 0
        reasons = []
        risks = []
        
        # 盈利能力 (40分)
        roe = profitability.get('roe') or 0
        if roe > 20:
            score += 40
            reasons.append(f"ROE {roe:.1f}% > 20%，盈利能力优秀")
        elif roe > 15:
            score += 30
            reasons.append(f"ROE {roe:.1f}% > 15%，盈利能力良好")
        elif roe > 10:
            score += 20
            reasons.append(f"ROE {roe:.1f}% > 10%，盈利能力中等")
        else:
            risks.append(f"ROE {roe:.1f}% < 10%，盈利能力较弱")
        
        # 估值水平 (30分)
        pe = valuation.get('pe_ratio') or 0
        if pe > 0 and pe < 15:
            score += 30
            reasons.append(f"PE {pe:.1f} < 15，估值有吸引力")
        elif pe > 0 and pe < 25:
            score += 20
            reasons.append(f"PE {pe:.1f}，估值合理")
        elif pe > 0:
            risks.append(f"PE {pe:.1f} > 25，估值偏高")
        
        # 财务健康 (20分)
        z = zscore.get('z_score') or 0
        if z > 2.99:
            score += 20
            reasons.append(f"Z-Score {z:.2f} > 2.99，财务健康")
        elif z > 1.81:
            score += 10
            reasons.append(f"Z-Score {z:.2f}，财务中等")
        else:
            risks.append(f"Z-Score {z:.2f} < 1.81，财务风险")
        
        # 杠杆水平 (10分)
        debt_ratio = leverage.get('debt_to_assets') or 0
        if debt_ratio < 0.4:
            score += 10
            reasons.append(f"资产负债率 {debt_ratio*100:.1f}% < 40%，财务稳健")
        elif debt_ratio < 0.6:
            score += 5
            reasons.append(f"资产负债率 {debt_ratio*100:.1f}%，财务适中")
        else:
            risks.append(f"资产负债率 {debt_ratio*100:.1f}% > 60%，杠杆偏高")
        
        return {
            'score': score,
            'grade': '优秀' if score >= 80 else '良好' if score >= 60 else '中等' if score >= 40 else '较差',
            'reasons': reasons,
            'risks': risks,
            'valuation': valuation,
            'profitability': profitability,
            'leverage': leverage,
            'dupont': dupont,
            'zscore': zscore,
            'data_source': 'FinanceToolkit'
        }
    
    # ========================================
    # 辅助函数
    # ========================================
    
    def _safe_float(self, value) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None:
            return None
        try:
            return float(value)
        except:
            return None
    
    def _fallback_valuation(self, symbol: str) -> Dict:
        """估值数据回退方案"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.valuation import get_valuation_summary
            result = get_valuation_summary(symbol)
            
            return {
                'pe_ratio': result.get('pe_analysis', {}).get('current'),
                'pb_ratio': result.get('pb_analysis', {}).get('current'),
                'data_source': 'yfinance'
            }
        except:
            return {'error': '无法获取估值数据'}
    
    def _fallback_profitability(self, symbol: str) -> Dict:
        """盈利数据回退方案"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from core.financial import get_financial_summary
            result = get_financial_summary(symbol)
            
            return {
                'roe': result.get('roe'),
                'debt_ratio': result.get('debt_ratio'),
                'data_source': 'yfinance'
            }
        except:
            return {'error': '无法获取盈利数据'}


# ============================================
# 便捷函数
# ============================================

_toolkit_wrapper = None

def get_toolkit_wrapper(api_key: Optional[str] = None) -> FinanceToolkitWrapper:
    """获取全局 Toolkit 实例"""
    global _toolkit_wrapper
    if _toolkit_wrapper is None:
        _toolkit_wrapper = FinanceToolkitWrapper(api_key)
    return _toolkit_wrapper


def analyze_fundamentals_deep(symbol: str) -> Dict:
    """深度基本面分析"""
    wrapper = get_toolkit_wrapper()
    return wrapper.analyze_fundamentals(symbol)


def get_valuation_ratios(symbol: str) -> Dict:
    """获取估值比率"""
    wrapper = get_toolkit_wrapper()
    return wrapper.get_valuation_ratios(symbol)


def get_profitability_ratios(symbol: str) -> Dict:
    """获取盈利能力比率"""
    wrapper = get_toolkit_wrapper()
    return wrapper.get_profitability_ratios(symbol)


def get_dupont_analysis(symbol: str) -> Dict:
    """DuPont 分析"""
    wrapper = get_toolkit_wrapper()
    return wrapper.get_dupont_analysis(symbol)


def get_altman_zscore(symbol: str) -> Dict:
    """Altman Z-Score"""
    wrapper = get_toolkit_wrapper()
    return wrapper.get_altman_zscore(symbol)


def get_dcf_valuation(symbol: str, growth_rate: float = 0.10) -> Dict:
    """DCF 估值"""
    wrapper = get_toolkit_wrapper()
    return wrapper.get_dcf_valuation(symbol, growth_rate)


if __name__ == '__main__':
    import json
    
    symbol = '002241'
    
    print("=" * 60)
    print(f"FinanceToolkit 深度分析: {symbol}")
    print("=" * 60)
    
    # 综合分析
    result = analyze_fundamentals_deep(symbol)
    
    print(f"\n综合评分: {result.get('score', 0)}/100")
    print(f"评级: {result.get('grade', '未知')}")
    
    print("\n✅ 优势:")
    for reason in result.get('reasons', []):
        print(f"  - {reason}")
    
    print("\n⚠️ 风险:")
    for risk in result.get('risks', []):
        print(f"  - {risk}")
    
    # DuPont 分析
    print("\n" + "=" * 60)
    print("DuPont 分析")
    print("=" * 60)
    dupont = result.get('dupont', {})
    print(f"ROE = 净利率 × 资产周转率 × 权益乘数")
    print(f"{dupont.get('roe', 0):.1f}% = {dupont.get('net_margin', 0):.1f}% × {dupont.get('asset_turnover', 0):.2f} × {dupont.get('equity_multiplier', 0):.2f}")
    
    interpretation = dupont.get('interpretation', {})
    print(f"\n盈利能力: {interpretation.get('profitability', '未知')}")
    print(f"运营效率: {interpretation.get('efficiency', '未知')}")
    print(f"财务杠杆: {interpretation.get('leverage', '未知')}")
