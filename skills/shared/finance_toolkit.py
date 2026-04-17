#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinanceToolkit 整合模块
提供 150+ 财务比率计算能力
"""

import sys
import os
from typing import Dict, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from financetoolkit import Toolkit
    FINANCETOOLKIT_AVAILABLE = True
except ImportError:
    FINANCETOOLKIT_AVAILABLE = False


class FinanceToolkitSkill:
    """FinanceToolkit 财务分析 Skill"""
    
    def __init__(self):
        self.name = "FinanceToolkitSkill"
        self.version = "1.0.0"
    
    def analyze(self, symbol: str) -> Dict:
        """
        使用 FinanceToolkit 进行深度财务分析
        
        Args:
            symbol: 股票代码 (仅支持美股)
            
        Returns:
            财务分析结果
        """
        if not FINANCETOOLKIT_AVAILABLE:
            return {
                'success': False,
                'error': 'FinanceToolkit 未安装',
                'symbol': symbol
            }
        
        print(f"FinanceToolkit 分析 {symbol}...")
        
        try:
            # 初始化 Toolkit
            toolkit = Toolkit(
                tickers=[symbol],
                start_date='2020-01-01',
                end_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            # 获取财务比率
            ratios = toolkit.ratios
            
            # 获取关键指标
            result = {
                'success': True,
                'symbol': symbol,
                'data_source': ['FinanceToolkit'],
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat(),
                'data': {}
            }
            
            # 盈利能力
            try:
                result['data']['profitability'] = {
                    'gross_margin': self._get_latest(ratios['gross_margin']),
                    'operating_margin': self._get_latest(ratios['operating_margin']),
                    'net_margin': self._get_latest(ratios['net_profit_margin']),
                    'roe': self._get_latest(ratios['return_on_equity']),
                    'roa': self._get_latest(ratios['return_on_assets']),
                    'roic': self._get_latest(ratios['return_on_invested_capital']),
                }
            except Exception as e:
                print(f"  盈利能力获取失败: {e}")
            
            # 估值指标
            try:
                result['data']['valuation'] = {
                    'pe_ratio': self._get_latest(ratios['price_earnings_ratio']),
                    'pb_ratio': self._get_latest(ratios['price_book_ratio']),
                    'ps_ratio': self._get_latest(ratios['price_sales_ratio']),
                    'ev_ebitda': self._get_latest(ratios['enterprise_value_ebitda']),
                }
            except Exception as e:
                print(f"  估值指标获取失败: {e}")
            
            # 杜邦分析
            try:
                result['data']['dupont'] = {
                    'profit_margin': self._get_latest(ratios['net_profit_margin']),
                    'asset_turnover': self._get_latest(ratios['asset_turnover']),
                    'financial_leverage': self._get_latest(ratios['financial_leverage']),
                }
            except Exception as e:
                print(f"  杜邦分析获取失败: {e}")
            
            # 流动性
            try:
                result['data']['liquidity'] = {
                    'current_ratio': self._get_latest(ratios['current_ratio']),
                    'quick_ratio': self._get_latest(ratios['quick_ratio']),
                    'cash_ratio': self._get_latest(ratios['cash_ratio']),
                }
            except Exception as e:
                print(f"  流动性获取失败: {e}")
            
            # 偿债能力
            try:
                result['data']['solvency'] = {
                    'debt_to_equity': self._get_latest(ratios['debt_to_equity']),
                    'debt_to_assets': self._get_latest(ratios['debt_to_assets']),
                    'interest_coverage': self._get_latest(ratios['interest_coverage']),
                }
            except Exception as e:
                print(f"  偿债能力获取失败: {e}")
            
            # 效率指标
            try:
                result['data']['efficiency'] = {
                    'inventory_turnover': self._get_latest(ratios['inventory_turnover']),
                    'receivables_turnover': self._get_latest(ratios['receivables_turnover']),
                    'asset_turnover': self._get_latest(ratios['asset_turnover']),
                }
            except Exception as e:
                print(f"  效率指标获取失败: {e}")
            
            return result
            
        except Exception as e:
            print(f"FinanceToolkit 错误: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': symbol
            }
    
    def _get_latest(self, series) -> Optional[float]:
        """获取最新值"""
        try:
            if hasattr(series, 'iloc'):
                return float(series.iloc[-1])
            return float(series)
        except:
            return None
    
    def get_all_ratios(self, symbol: str) -> Dict:
        """获取所有财务比率"""
        if not FINANCETOOLKIT_AVAILABLE:
            return {'error': 'FinanceToolkit 未安装'}
        
        try:
            toolkit = Toolkit(
                tickers=[symbol],
                start_date='2020-01-01',
                end_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            ratios = toolkit.ratios
            
            # 返回所有可用的比率
            all_ratios = {}
            for col in ratios.columns:
                latest = self._get_latest(ratios[col])
                if latest is not None:
                    all_ratios[col] = latest
            
            return all_ratios
            
        except Exception as e:
            return {'error': str(e)}


# 快速使用函数
def analyze_with_finance_toolkit(symbol: str) -> Dict:
    """使用 FinanceToolkit 分析"""
    skill = FinanceToolkitSkill()
    return skill.analyze(symbol)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("FinanceToolkit 测试")
    print("=" * 60)
    
    if not FINANCETOOLKIT_AVAILABLE:
        print("❌ FinanceToolkit 未安装")
        sys.exit(1)
    
    result = analyze_with_finance_toolkit('AAPL')
    
    if result['success']:
        print(f"\n✅ AAPL 分析成功")
        print(f"数据源: {result['data_source']}")
        print(f"置信度: {result['confidence']}")
        
        for category, metrics in result['data'].items():
            print(f"\n{category}:")
            for name, value in metrics.items():
                if value is not None:
                    print(f"  {name}: {value:.2f}" if value else f"  {name}: N/A")
    else:
        print(f"\n❌ 分析失败: {result['error']}")
