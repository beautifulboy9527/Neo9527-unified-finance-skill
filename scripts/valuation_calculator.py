#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valuation Calculator - DCF/DDM/相对估值
整合自 china-stock-analysis 的估值能力
"""

import sys
import os
import json
import argparse
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ValuationResult:
    """估值结果"""
    method: str
    fair_value: float
    current_price: float
    upside: float  # 潜在涨幅 %
    confidence: str  # 高/中/低
    details: Dict


class ValuationCalculator:
    """估值计算器"""
    
    def __init__(self, code: str, name: str = ""):
        self.code = code
        self.name = name
        
    def calculate_dcf(self,
                       fcf_list: list,
                       discount_rate: float = 0.10,
                       terminal_growth: float = 0.03,
                       forecast_years: int = 5,
                       shares_outstanding: float = 1.0,
                       net_debt: float = 0.0) -> ValuationResult:
        """
        DCF 估值
        
        Args:
            fcf_list: 未来5年自由现金流预测 [FCF1, FCF2, ..., FCF5]
            discount_rate: WACC 折现率 (默认 10%)
            terminal_growth: 永续增长率 (默认 3%)
            forecast_years: 预测年数 (默认 5)
            shares_outstanding: 流通股数 (亿股)
            net_debt: 净债务 (亿元)
        """
        # Step 1: 计算预测期现金流现值
        pv_fcf = 0
        for i, fcf in enumerate(fcf_list[:forecast_years]):
            year = i + 1
            pv = fcf / ((1 + discount_rate) ** year)
            pv_fcf += pv
            
        # Step 2: 计算永续价值
        terminal_fcf = fcf_list[forecast_years - 1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_years)
        
        # Step 3: 计算企业价值
        enterprise_value = pv_fcf + pv_terminal
        
        # Step 4: 计算股权价值
        equity_value = enterprise_value - net_debt
        fair_value_per_share = equity_value / shares_outstanding
        
        return ValuationResult(
            method="DCF",
            fair_value=fair_value_per_share,
            current_price=0,  # 需要外部传入
            upside=0,  # 需要外部计算
            confidence="中",
            details={
                "pv_fcf": pv_fcf,
                "pv_terminal": pv_terminal,
                "enterprise_value": enterprise_value,
                "equity_value": equity_value,
                "wacc": discount_rate,
                "terminal_growth": terminal_growth,
                "forecast_years": forecast_years,
                "fcf_forecast": fcf_list[:forecast_years]
            }
        )
    
    def calculate_ddm(self,
                      dividend_list: list,
                      required_return: float = 0.10,
                      growth_rate: float = 0.05,
                      shares_outstanding: float = 1.0) -> ValuationResult:
        """
        DDM (Dividend Discount Model) 估值
        
        Args:
            dividend_list: 未来5年股息预测 [DIV1, DIV2, ..., DIV5]
            required_return: 要求回报率 (默认 10%)
            growth_rate: 股息增长率 (默认 5%)
            shares_outstanding: 流通股数 (亿股)
        """
        # Gordon Growth Model
        next_dividend = dividend_list[0]
        fair_value = next_dividend / (required_return - growth_rate)
        
        return ValuationResult(
            method="DDM",
            fair_value=fair_value,
            current_price=0,
            upside=0,
            confidence="中",
            details={
                "next_dividend": next_dividend,
                "required_return": required_return,
                "growth_rate": growth_rate,
                "dividend_forecast": dividend_list[:5]
            }
        )
    
    def relative_valuation(self,
                           peers: list,
                           metrics: Dict[str, float]) -> ValuationResult:
        """
        相对估值 (行业对比)
        
        Args:
            peers: 同行列表 [{name, pe, pb, ps}]
            metrics: 当前公司指标 {pe, pb, ps, ev_ebitda}
        """
        # 计算行业中位数
        pe_median = sorted([p['pe'] for p in peers if p.get('pe')])[-1] if peers else None
        pb_median = sorted([p['pb'] for p in peers if p.get('pb')])[-1] if peers else None
        
        # 基于 PE 的相对估值
        if metrics.get('pe') and pe_median:
            fair_value_pe = metrics['pe'] / pe_median * metrics.get('price', 0)
        else:
            fair_value_pe = 0
            
        return ValuationResult(
            method="Relative",
            fair_value=fair_value_pe,
            current_price=metrics.get('price', 0),
            upside=(fair_value_pe / metrics.get('price', 1) - 1) * 100 if metrics.get('price') else 0,
            confidence="中",
            details={
                "pe_median": pe_median,
                "pb_median": pb_median,
                "current_pe": metrics.get('pe'),
                "current_pb": metrics.get('pb')
            }
        )


def main():
    parser = argparse.ArgumentParser(description='估值计算器 - DCF/DDM/相对估值')
    parser.add_argument('--code', required=True, help='股票代码')
    parser.add_argument('--methods', default='all', choices=['all', 'dcf', 'ddm', 'relative'], help='估值方法')
    parser.add_argument('--discount-rate', type=float, default=0.10, help='WACC 折现率')
    parser.add_argument('--terminal-growth', type=float, default=0.03, help='永续增长率')
    parser.add_argument('--forecast-years', type=int, default=5, help='预测年数')
    parser.add_argument('--margin-of-safety', type=float, default=30, help='安全边际 %')
    parser.add_argument('--output', default='valuation_result.json', help='输出文件')
    
    args = parser.parse_args()
    
    # 示例数据 (实际使用时从 data_fetcher 获取)
    calc = ValuationCalculator(args.code)
    
    print(f"📊 {args.code} 估值计算")
    print(f"折现率: {args.discount_rate*100}%")
    print(f"永续增长率: {args.terminal_growth*100}%")
    print(f"安全边际: {args.margin_of_safety}%")
    print()
    
    # 这里需要接入真实数据
    # 示例: 贵州茅台 DCF 估值
    result = calc.calculate_dcf(
        fcf_list=[200, 230, 260, 290, 320],  # 示例 FCF (亿元)
        discount_rate=args.discount_rate,
        terminal_growth=args.terminal_growth,
        forecast_years=args.forecast_years,
        shares_outstanding=12.6,  # 茅台约12.6亿股
        net_debt=-500  # 茅台净现金
    )
    
    print(f"DCF 估值结果:")
    print(f"  每股价值: ¥{result.fair_value:.2f}")
    print(f"  详细信息: {json.dumps(result.details, indent=2, ensure_ascii=False)}")
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({
            'code': args.code,
            'method': result.method,
            'fair_value': result.fair_value,
            'details': result.details
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
