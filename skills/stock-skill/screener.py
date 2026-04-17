#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股选股器 v1.0

功能:
- 多条件筛选 (估值/盈利/成长/股息/财务安全)
- 自定义条件组合
- 输出JSON结果
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import akshare as ak
    import pandas as pd
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: AkShare 未安装，A股选股功能不可用")


class StockScreener:
    """A股选股器"""
    
    # 默认选股条件
    DEFAULT_CRITERIA = {
        # 估值指标
        'pe_max': 30,           # PE上限
        'pb_max': 5,            # PB上限
        'ps_max': 10,           # PS上限
        
        # 盈利指标
        'roe_min': 10,          # ROE下限 (%)
        'roa_min': 5,           # ROA下限 (%)
        'gross_margin_min': 20, # 毛利率下限 (%)
        'net_margin_min': 5,    # 净利率下限 (%)
        
        # 成长指标
        'revenue_growth_min': 0,     # 营收增长率下限 (%)
        'profit_growth_min': 0,      # 净利润增长率下限 (%)
        
        # 股息指标
        'dividend_yield_min': 0,     # 股息率下限 (%)
        
        # 财务安全
        'debt_ratio_max': 60,        # 资产负债率上限 (%)
        'current_ratio_min': 1,      # 流动比率下限
    }
    
    def __init__(self):
        self.name = "StockScreener"
        self.version = "1.0.0"
    
    def screen(self, scope: str = 'hs300', criteria: Optional[Dict] = None) -> Dict:
        """
        执行选股
        
        Args:
            scope: 选股范围 (hs300/zz500/all/a50)
            criteria: 选股条件 (可选，使用默认条件)
            
        Returns:
            选股结果
        """
        if not AKSHARE_AVAILABLE:
            return {
                'success': False,
                'error': 'AkShare 未安装',
                'stocks': []
            }
        
        print(f"开始选股 (范围: {scope})...")
        
        # 合并条件
        crit = {**self.DEFAULT_CRITERIA, **(criteria or {})}
        
        # 获取股票池
        stock_pool = self._get_stock_pool(scope)
        print(f"  股票池: {len(stock_pool)} 只")
        
        # 获取财务数据
        financial_data = self._get_financial_data(stock_pool)
        
        # 筛选
        result_stocks = self._apply_criteria(financial_data, crit)
        
        print(f"  符合条件: {len(result_stocks)} 只")
        
        return {
            'success': True,
            'scope': scope,
            'criteria': crit,
            'total_stocks': len(stock_pool),
            'matched_stocks': len(result_stocks),
            'stocks': result_stocks,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_stock_pool(self, scope: str) -> List[str]:
        """获取股票池"""
        stocks = []
        
        try:
            if scope == 'hs300':
                # 沪深300
                df = ak.index_stock_cons_weight_csindex(symbol='000300')
                stocks = df['成分券代码'].tolist()
            elif scope == 'zz500':
                # 中证500
                df = ak.index_stock_cons_weight_csindex(symbol='000905')
                stocks = df['成分券代码'].tolist()
            elif scope == 'a50':
                # 上证50
                df = ak.index_stock_cons_weight_csindex(symbol='000016')
                stocks = df['成分券代码'].tolist()
            elif scope == 'all':
                # 全A股
                df = ak.stock_zh_a_spot_em()
                stocks = df['代码'].tolist()
            else:
                # 默认沪深300
                df = ak.index_stock_cons_weight_csindex(symbol='000300')
                stocks = df['成分券代码'].tolist()
        except Exception as e:
            print(f"  获取股票池失败: {e}")
        
        return stocks
    
    def _get_financial_data(self, stocks: List[str]) -> pd.DataFrame:
        """获取财务数据"""
        all_data = []
        
        print("  获取财务数据...")
        
        # 批量获取 (限制数量避免超时)
        max_stocks = min(len(stocks), 100)
        
        for i, code in enumerate(stocks[:max_stocks]):
            if i % 20 == 0:
                print(f"    进度: {i}/{max_stocks}")
            
            try:
                # 财务指标
                df = ak.stock_financial_analysis_indicator(symbol=code)
                
                if df is not None and not df.empty:
                    latest = df.iloc[0]
                    
                    stock_data = {
                        'code': code,
                        'pe': float(latest.get('市盈率', 0) or 0),
                        'pb': float(latest.get('市净率', 0) or 0),
                        'roe': float(latest.get('净资产收益率', 0) or 0),
                        'roa': float(latest.get('总资产净利润(ROA)', 0) or 0),
                        'gross_margin': float(latest.get('销售毛利率', 0) or 0),
                        'net_margin': float(latest.get('销售净利率', 0) or 0),
                        'debt_ratio': float(latest.get('资产负债率', 0) or 0),
                        'current_ratio': float(latest.get('流动比率', 0) or 0),
                    }
                    
                    all_data.append(stock_data)
            
            except Exception as e:
                continue
        
        return pd.DataFrame(all_data)
    
    def _apply_criteria(self, df: pd.DataFrame, criteria: Dict) -> List[Dict]:
        """应用筛选条件"""
        if df.empty:
            return []
        
        # 创建筛选掩码
        mask = pd.Series([True] * len(df))
        
        # 估值筛选
        if criteria.get('pe_max'):
            mask &= (df['pe'] > 0) & (df['pe'] <= criteria['pe_max'])
        if criteria.get('pb_max'):
            mask &= (df['pb'] > 0) & (df['pb'] <= criteria['pb_max'])
        
        # 盈利筛选
        if criteria.get('roe_min'):
            mask &= df['roe'] >= criteria['roe_min']
        if criteria.get('roa_min'):
            mask &= df['roa'] >= criteria['roa_min']
        if criteria.get('gross_margin_min'):
            mask &= df['gross_margin'] >= criteria['gross_margin_min']
        if criteria.get('net_margin_min'):
            mask &= df['net_margin'] >= criteria['net_margin_min']
        
        # 财务安全筛选
        if criteria.get('debt_ratio_max'):
            mask &= df['debt_ratio'] <= criteria['debt_ratio_max']
        if criteria.get('current_ratio_min'):
            mask &= df['current_ratio'] >= criteria['current_ratio_min']
        
        # 筛选结果
        result_df = df[mask]
        
        # 按ROE排序
        result_df = result_df.sort_values('roe', ascending=False)
        
        # 转换为列表
        return result_df.to_dict('records')


# 快速使用函数
def screen_stocks(scope: str = 'hs300', **criteria) -> Dict:
    """快速选股"""
    screener = StockScreener()
    return screener.screen(scope, criteria if criteria else None)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("A股选股器 v1.0 测试")
    print("=" * 60)
    
    # 测试选股
    result = screen_stocks(
        scope='hs300',
        pe_max=20,
        roe_min=15,
        debt_ratio_max=50
    )
    
    if result['success']:
        print(f"\n选股结果: {result['matched_stocks']}/{result['total_stocks']} 只")
        
        if result['stocks']:
            print("\nTOP 10:")
            for i, stock in enumerate(result['stocks'][:10], 1):
                print(f"  {i}. {stock['code']} - ROE: {stock['roe']:.1f}%, PE: {stock['pe']:.1f}")
    else:
        print(f"\n选股失败: {result['error']}")
