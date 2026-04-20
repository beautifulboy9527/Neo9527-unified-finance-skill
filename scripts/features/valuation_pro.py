#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业估值模型 - Professional Valuation Models
对标机构级估值分析

包含:
- DCF多阶段模型 (两阶段、三阶段、H模型)
- 相对估值 (PE、PB、PS、EV/EBITDA、PEG)
- 行业估值矩阵
- 敏感性分析
- 估值报告
"""

import sys
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yfinance as yf

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class ValuationModels:
    """专业估值模型"""
    
    def __init__(
        self,
        ticker: str,
        risk_free_rate: float = 0.03,
        market_return: float = 0.10
    ):
        """
        初始化
        
        Args:
            ticker: 股票代码
            risk_free_rate: 无风险利率
            market_return: 市场预期收益率
        """
        self.ticker = ticker
        self.rf = risk_free_rate
        self.rm = market_return
        
        # 获取数据
        self.stock = yf.Ticker(ticker)
        self.info = self.stock.info
    
    # ========================================
    # DCF模型
    # ========================================
    
    def dcf_two_stage(
        self,
        current_fcf: float,
        growth_rate_high: float = 0.15,
        growth_rate_stable: float = 0.03,
        high_growth_years: int = 5,
        wacc: float = 0.10,
        terminal_multiple: float = None
    ) -> Dict:
        """
        两阶段DCF模型
        
        Args:
            current_fcf: 当前自由现金流
            growth_rate_high: 高增长期增长率
            growth_rate_stable: 稳定期增长率
            high_growth_years: 高增长期年数
            wacc: 加权平均资本成本
            terminal_multiple: 终值倍数 (可选)
        
        Returns:
            估值结果
        """
        # 高增长期现金流现值
        high_growth_value = 0
        fcf_forecast = []
        
        for year in range(1, high_growth_years + 1):
            fcf = current_fcf * (1 + growth_rate_high) ** year
            pv = fcf / (1 + wacc) ** year
            high_growth_value += pv
            fcf_forecast.append({
                'year': year,
                'fcf': fcf,
                'pv': pv
            })
        
        # 终值
        final_fcf = current_fcf * (1 + growth_rate_high) ** high_growth_years
        
        if terminal_multiple:
            # 使用倍数法
            terminal_value = final_fcf * terminal_multiple
        else:
            # Gordon增长模型
            terminal_value = final_fcf * (1 + growth_rate_stable) / (wacc - growth_rate_stable)
        
        # 终值现值
        terminal_pv = terminal_value / (1 + wacc) ** high_growth_years
        
        # 企业价值
        enterprise_value = high_growth_value + terminal_pv
        
        return {
            'model': '两阶段DCF',
            'current_fcf': current_fcf,
            'high_growth_value': high_growth_value,
            'terminal_value': terminal_value,
            'terminal_pv': terminal_pv,
            'enterprise_value': enterprise_value,
            'fcf_forecast': fcf_forecast,
            'parameters': {
                'growth_rate_high': growth_rate_high,
                'growth_rate_stable': growth_rate_stable,
                'high_growth_years': high_growth_years,
                'wacc': wacc
            }
        }
    
    def dcf_three_stage(
        self,
        current_fcf: float,
        growth_rate_high: float = 0.20,
        growth_rate_transition: float = 0.10,
        growth_rate_stable: float = 0.03,
        high_growth_years: int = 5,
        transition_years: int = 5,
        wacc: float = 0.10
    ) -> Dict:
        """
        三阶段DCF模型
        
        高增长期 → 过渡期 → 稳定期
        """
        total_value = 0
        fcf_forecast = []
        
        # 阶段1: 高增长期
        for year in range(1, high_growth_years + 1):
            fcf = current_fcf * (1 + growth_rate_high) ** year
            pv = fcf / (1 + wacc) ** year
            total_value += pv
            fcf_forecast.append({
                'year': year,
                'stage': '高增长',
                'fcf': fcf,
                'growth': growth_rate_high,
                'pv': pv
            })
        
        # 阶段2: 过渡期 (增长率线性递减)
        last_fcf = fcf_forecast[-1]['fcf']
        growth_decline = (growth_rate_transition - growth_rate_stable) / transition_years
        
        for year in range(1, transition_years + 1):
            growth = growth_rate_transition - growth_decline * (year - 1)
            fcf = last_fcf * (1 + growth)
            pv = fcf / (1 + wacc) ** (high_growth_years + year)
            total_value += pv
            fcf_forecast.append({
                'year': high_growth_years + year,
                'stage': '过渡',
                'fcf': fcf,
                'growth': growth,
                'pv': pv
            })
            last_fcf = fcf
        
        # 阶段3: 稳定期 (终值)
        terminal_value = last_fcf * (1 + growth_rate_stable) / (wacc - growth_rate_stable)
        terminal_pv = terminal_value / (1 + wacc) ** (high_growth_years + transition_years)
        total_value += terminal_pv
        
        return {
            'model': '三阶段DCF',
            'current_fcf': current_fcf,
            'enterprise_value': total_value,
            'terminal_value': terminal_value,
            'terminal_pv': terminal_pv,
            'fcf_forecast': fcf_forecast,
            'parameters': {
                'growth_rate_high': growth_rate_high,
                'growth_rate_transition': growth_rate_transition,
                'growth_rate_stable': growth_rate_stable,
                'high_growth_years': high_growth_years,
                'transition_years': transition_years,
                'wacc': wacc
            }
        }
    
    def dcf_h_model(
        self,
        current_fcf: float,
        growth_rate_initial: float = 0.20,
        growth_rate_stable: float = 0.03,
        half_life: float = 5,
        wacc: float = 0.10
    ) -> Dict:
        """
        H模型 (H-Model)
        
        增长率从初始值线性衰减到稳定值
        
        公式: V = FCF0 * [(1+gL) + H*(gS-gL)] / (r-gL) + FCF0*(gS-gL)*H/(r-gL)
        
        Args:
            half_life: 增长率衰减半衰期
        """
        gL = growth_rate_stable
        gS = growth_rate_initial
        H = half_life
        r = wacc
        
        # H模型公式
        value = current_fcf * ((1 + gL) + H * (gS - gL)) / (r - gL)
        value += current_fcf * (gS - gL) * H / (r - gL)
        
        return {
            'model': 'H模型',
            'current_fcf': current_fcf,
            'enterprise_value': value,
            'parameters': {
                'growth_rate_initial': gS,
                'growth_rate_stable': gL,
                'half_life': H,
                'wacc': wacc
            }
        }
    
    # ========================================
    # 相对估值
    # ========================================
    
    def relative_valuation(
        self,
        current_price: float = None,
        eps: float = None,
        book_value_per_share: float = None,
        revenue_per_share: float = None,
        ebitda: float = None,
        enterprise_value: float = None,
        industry_pe: float = 20,
        industry_pb: float = 2,
        industry_ps: float = 3,
        industry_ev_ebitda: float = 12
    ) -> Dict:
        """
        相对估值法
        
        使用行业倍数进行估值
        """
        if current_price is None:
            current_price = self.info.get('currentPrice', 0)
        
        if eps is None:
            eps = self.info.get('trailingEps', 0)
        
        if book_value_per_share is None:
            book_value_per_share = self.info.get('bookValue', 0)
        
        results = {}
        
        # PE估值
        if eps and eps > 0:
            current_pe = current_price / eps
            pe_valuation = eps * industry_pe
            results['pe'] = {
                'current_pe': current_pe,
                'industry_pe': industry_pe,
                'fair_value': pe_valuation,
                'upside': (pe_valuation - current_price) / current_price,
                'valuation': '低估' if current_pe < industry_pe * 0.8 else ('高估' if current_pe > industry_pe * 1.2 else '合理')
            }
        
        # PB估值
        if book_value_per_share and book_value_per_share > 0:
            current_pb = current_price / book_value_per_share
            pb_valuation = book_value_per_share * industry_pb
            results['pb'] = {
                'current_pb': current_pb,
                'industry_pb': industry_pb,
                'fair_value': pb_valuation,
                'upside': (pb_valuation - current_price) / current_price,
                'valuation': '低估' if current_pb < industry_pb * 0.8 else ('高估' if current_pb > industry_pb * 1.2 else '合理')
            }
        
        # PS估值
        if revenue_per_share and revenue_per_share > 0:
            current_ps = current_price / revenue_per_share
            ps_valuation = revenue_per_share * industry_ps
            results['ps'] = {
                'current_ps': current_ps,
                'industry_ps': industry_ps,
                'fair_value': ps_valuation,
                'upside': (ps_valuation - current_price) / current_price,
                'valuation': '低估' if current_ps < industry_ps * 0.8 else ('高估' if current_ps > industry_ps * 1.2 else '合理')
            }
        
        # EV/EBITDA估值
        if ebitda and ebitda > 0 and enterprise_value:
            current_ev_ebitda = enterprise_value / ebitda
            ev_ebitda_valuation = ebitda * industry_ev_ebitda
            results['ev_ebitda'] = {
                'current_ev_ebitda': current_ev_ebitda,
                'industry_ev_ebitda': industry_ev_ebitda,
                'fair_enterprise_value': ev_ebitda_valuation,
                'valuation': '低估' if current_ev_ebitda < industry_ev_ebitda * 0.8 else ('高估' if current_ev_ebitda > industry_ev_ebitda * 1.2 else '合理')
            }
        
        # PEG估值
        if eps and eps > 0:
            growth_rate = self.info.get('earningsGrowth', 0)
            if growth_rate and growth_rate > 0:
                peg = (current_price / eps) / (growth_rate * 100)
                results['peg'] = {
                    'peg': peg,
                    'valuation': '低估' if peg < 1 else ('合理' if peg < 2 else '高估')
                }
        
        return results
    
    # ========================================
    # 敏感性分析
    # ========================================
    
    def sensitivity_analysis(
        self,
        current_fcf: float,
        base_wacc: float = 0.10,
        base_growth: float = 0.03,
        wacc_range: Tuple[float, float] = (0.08, 0.12),
        growth_range: Tuple[float, float] = (0.01, 0.05),
        steps: int = 5
    ) -> pd.DataFrame:
        """
        敏感性分析
        
        分析WACC和增长率变化对估值的影响
        """
        wacc_values = np.linspace(wacc_range[0], wacc_range[1], steps)
        growth_values = np.linspace(growth_range[0], growth_range[1], steps)
        
        results = []
        
        for wacc in wacc_values:
            for growth in growth_values:
                if growth < wacc:  # 确保增长率 < WACC
                    # 简化DCF
                    value = current_fcf * (1 + growth) / (wacc - growth)
                    results.append({
                        'WACC': wacc,
                        '增长率': growth,
                        '估值': value
                    })
        
        df = pd.DataFrame(results)
        return df.pivot(index='WACC', columns='增长率', values='估值')
    
    # ========================================
    # 行业估值矩阵
    # ========================================
    
    def industry_valuation_matrix(
        self,
        industry_data: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        行业估值矩阵
        
        Args:
            industry_data: {'公司名': {'pe': 20, 'pb': 3, 'ps': 2, ...}}
        
        Returns:
            行业对比表
        """
        df = pd.DataFrame(industry_data).T
        
        # 计算行业平均
        df.loc['行业平均'] = df.mean()
        df.loc['行业中位数'] = df.median()
        
        return df
    
    # ========================================
    # WACC计算
    # ========================================
    
    def calculate_wacc(
        self,
        beta: float = None,
        cost_of_debt: float = 0.05,
        tax_rate: float = 0.25,
        debt_ratio: float = 0.3
    ) -> float:
        """
        计算加权平均资本成本 (WACC)
        
        WACC = E/V * Re + D/V * Rd * (1-T)
        """
        if beta is None:
            beta = self.info.get('beta', 1.0)
        
        # CAPM计算权益成本
        cost_of_equity = self.rf + beta * (self.rm - self.rf)
        
        # WACC
        equity_ratio = 1 - debt_ratio
        wacc = equity_ratio * cost_of_equity + debt_ratio * cost_of_debt * (1 - tax_rate)
        
        return wacc
    
    # ========================================
    # 综合估值报告
    # ========================================
    
    def valuation_report(
        self,
        current_fcf: float = None,
        shares_outstanding: float = None,
        net_debt: float = 0
    ) -> Dict:
        """
        生成综合估值报告
        """
        # 获取数据
        if current_fcf is None:
            # 尝试从财务数据获取
            cashflow = self.stock.cashflow
            if not cashflow.empty:
                current_fcf = cashflow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cashflow.index else 0
            if not current_fcf:
                current_fcf = 1000000000  # 默认10亿
        
        if shares_outstanding is None:
            shares_outstanding = self.info.get('sharesOutstanding', 1000000000)
        
        current_price = self.info.get('currentPrice', 0)
        eps = self.info.get('trailingEps', 0)
        book_value = self.info.get('bookValue', 0)
        beta = self.info.get('beta', 1.0)
        
        # 计算WACC
        wacc = self.calculate_wacc(beta)
        
        report = {
            'ticker': self.ticker,
            'current_price': current_price,
            'timestamp': datetime.now().isoformat()
        }
        
        # DCF估值
        report['dcf_two_stage'] = self.dcf_two_stage(
            current_fcf,
            growth_rate_high=0.15,
            growth_rate_stable=0.03,
            high_growth_years=5,
            wacc=wacc
        )
        
        report['dcf_three_stage'] = self.dcf_three_stage(
            current_fcf,
            growth_rate_high=0.20,
            growth_rate_transition=0.10,
            growth_rate_stable=0.03,
            high_growth_years=5,
            transition_years=5,
            wacc=wacc
        )
        
        report['dcf_h_model'] = self.dcf_h_model(
            current_fcf,
            growth_rate_initial=0.20,
            growth_rate_stable=0.03,
            half_life=5,
            wacc=wacc
        )
        
        # 计算每股价值
        for model in ['dcf_two_stage', 'dcf_three_stage', 'dcf_h_model']:
            ev = report[model]['enterprise_value']
            equity_value = ev - net_debt
            price_per_share = equity_value / shares_outstanding
            report[model]['equity_value'] = equity_value
            report[model]['price_per_share'] = price_per_share
            report[model]['upside'] = (price_per_share - current_price) / current_price if current_price > 0 else 0
        
        # 相对估值
        report['relative'] = self.relative_valuation(
            current_price=current_price,
            eps=eps,
            book_value_per_share=book_value
        )
        
        # 敏感性分析
        report['sensitivity'] = self.sensitivity_analysis(
            current_fcf,
            base_wacc=wacc,
            base_growth=0.03
        )
        
        # 综合估值
        dcf_values = [
            report['dcf_two_stage']['price_per_share'],
            report['dcf_three_stage']['price_per_share'],
            report['dcf_h_model']['price_per_share']
        ]
        
        report['summary'] = {
            'dcf_average': np.mean(dcf_values),
            'dcf_range': [min(dcf_values), max(dcf_values)],
            'dcf_upside': (np.mean(dcf_values) - current_price) / current_price if current_price > 0 else 0,
            'wacc': wacc,
            'beta': beta
        }
        
        # 估值评级
        report['rating'] = self._calculate_valuation_rating(report)
        
        return report
    
    def _calculate_valuation_rating(self, report: Dict) -> Dict:
        """计算估值评级"""
        current_price = report['current_price']
        dcf_avg = report['summary']['dcf_average']
        
        # DCF隐含涨幅
        dcf_upside = (dcf_avg - current_price) / current_price
        
        # 相对估值信号
        relative_signals = []
        for method, data in report['relative'].items():
            if 'valuation' in data:
                relative_signals.append(data['valuation'])
        
        # 综合判断
        undervalued_count = relative_signals.count('低估')
        overvalued_count = relative_signals.count('高估')
        
        if dcf_upside > 0.3 and undervalued_count >= 2:
            grade = '显著低估'
            recommendation = '强烈买入'
        elif dcf_upside > 0.15 and undervalued_count >= 1:
            grade = '低估'
            recommendation = '买入'
        elif dcf_upside > 0 or (undervalued_count > overvalued_count):
            grade = '合理偏低'
            recommendation = '持有/轻仓买入'
        elif dcf_upside > -0.15:
            grade = '合理'
            recommendation = '持有'
        elif dcf_upside > -0.30:
            grade = '高估'
            recommendation = '减仓'
        else:
            grade = '显著高估'
            recommendation = '卖出'
        
        return {
            'grade': grade,
            'recommendation': recommendation,
            'dcf_upside': dcf_upside,
            'relative_signals': relative_signals
        }


# ============================================
# 便捷函数
# ============================================

def value_stock(
    ticker: str,
    current_fcf: float = None
) -> Dict:
    """
    股票估值
    
    Args:
        ticker: 股票代码
        current_fcf: 当前自由现金流
    
    Returns:
        估值报告
    """
    vm = ValuationModels(ticker)
    return vm.valuation_report(current_fcf)


if __name__ == '__main__':
    print("=" * 60)
    print("专业估值模型测试")
    print("=" * 60)
    
    # 测试AAPL
    ticker = 'AAPL'
    
    try:
        vm = ValuationModels(ticker)
        
        # 使用假设数据进行测试
        current_fcf = 100000000000  # 1000亿
        
        print(f"\n📊 {ticker} DCF估值")
        print("-" * 60)
        
        # 两阶段DCF
        result = vm.dcf_two_stage(
            current_fcf,
            growth_rate_high=0.15,
            growth_rate_stable=0.03,
            high_growth_years=5,
            wacc=0.10
        )
        
        print(f"\n两阶段DCF模型:")
        print(f"  当前FCF: ${current_fcf/1e9:.1f}B")
        print(f"  企业价值: ${result['enterprise_value']/1e9:.1f}B")
        print(f"  高增长期现值: ${result['high_growth_value']/1e9:.1f}B")
        print(f"  终值现值: ${result['terminal_pv']/1e9:.1f}B")
        
        # 三阶段DCF
        result3 = vm.dcf_three_stage(
            current_fcf,
            growth_rate_high=0.20,
            growth_rate_transition=0.10,
            growth_rate_stable=0.03
        )
        
        print(f"\n三阶段DCF模型:")
        print(f"  企业价值: ${result3['enterprise_value']/1e9:.1f}B")
        
        # H模型
        result_h = vm.dcf_h_model(
            current_fcf,
            growth_rate_initial=0.20,
            growth_rate_stable=0.03
        )
        
        print(f"\nH模型:")
        print(f"  企业价值: ${result_h['enterprise_value']/1e9:.1f}B")
        
        # 敏感性分析
        print(f"\n📈 敏感性分析 (WACC vs 增长率)")
        print("-" * 60)
        sensitivity = vm.sensitivity_analysis(current_fcf)
        print(sensitivity.to_string())
        
        # 相对估值
        print(f"\n📊 相对估值")
        print("-" * 60)
        relative = vm.relative_valuation(
            current_price=180,
            eps=6.0,
            book_value_per_share=4.0,
            industry_pe=25,
            industry_pb=8
        )
        
        for method, data in relative.items():
            if 'fair_value' in data:
                print(f"\n{method.upper()}估值:")
                print(f"  当前倍数: {data.get(f'current_{method}', 'N/A'):.2f}")
                print(f"  行业倍数: {data.get(f'industry_{method}', 'N/A'):.2f}")
                print(f"  公允价值: ${data['fair_value']:.2f}")
                print(f"  涨幅空间: {data['upside']*100:.1f}%")
                print(f"  估值判断: {data['valuation']}")
        
        # WACC计算
        wacc = vm.calculate_wacc(beta=1.2)
        print(f"\n💰 WACC计算")
        print("-" * 60)
        print(f"  Beta: 1.2")
        print(f"  无风险利率: {vm.rf*100:.1f}%")
        print(f"  市场收益率: {vm.rm*100:.1f}%")
        print(f"  WACC: {wacc*100:.1f}%")
        
    except Exception as e:
        print(f"⚠️ 测试失败: {e}")
        print("使用离线数据测试...")
        
        # 离线测试
        vm = ValuationModels('AAPL')
        result = vm.dcf_two_stage(100e9)
        print(f"\n两阶段DCF: ${result['enterprise_value']/1e9:.1f}B")
