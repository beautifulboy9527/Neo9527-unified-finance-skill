#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值计算器 v1.0

功能:
- DCF (现金流折现) 估值
- DDM (股息折现) 估值
- 相对估值 (PE/PB)
- 安全边际计算
"""

import sys
import os
from typing import Dict, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import akshare as ak
    import numpy as np
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

import yfinance as yf


class ValuationCalculator:
    """估值计算器"""
    
    def __init__(self):
        self.name = "ValuationCalculator"
        self.version = "1.0.0"
    
    def calculate(self, symbol: str, methods: str = 'all', **params) -> Dict:
        """
        执行估值计算
        
        Args:
            symbol: 股票代码
            methods: 计算方法 (all/dcf/ddm/relative)
            **params: 自定义参数
            
        Returns:
            估值结果
        """
        print(f"开始估值计算: {symbol}...")
        
        # 默认参数
        default_params = {
            'discount_rate': 0.10,      # 折现率 (WACC)
            'terminal_growth': 0.03,    # 永续增长率
            'forecast_years': 5,        # 预测年数
            'margin_of_safety': 0.30,   # 安全边际
            'required_return': 0.10,    # 要求回报率
            'dividend_growth': 0.05,    # 股息增长率
        }
        
        # 合并参数
        calc_params = {**default_params, **params}
        
        # 检测市场
        market = self._detect_market(symbol)
        
        # 获取财务数据
        financial_data = self._get_financial_data(symbol, market)
        
        if not financial_data:
            return {
                'success': False,
                'error': '无法获取财务数据',
                'symbol': symbol
            }
        
        # 执行估值
        valuations = {}
        
        if methods in ['all', 'relative']:
            valuations['relative'] = self._relative_valuation(financial_data)
        
        if methods in ['all', 'dcf'] and market == 'cn':
            valuations['dcf'] = self._dcf_valuation(financial_data, calc_params)
        
        if methods in ['all', 'ddm'] and market == 'cn':
            valuations['ddm'] = self._ddm_valuation(financial_data, calc_params)
        
        # 计算综合估值
        fair_value = self._calculate_fair_value(valuations, financial_data)
        
        print(f"  估值计算完成")
        
        return {
            'success': True,
            'symbol': symbol,
            'market': market,
            'current_price': financial_data.get('price', 0),
            'valuations': valuations,
            'fair_value': fair_value,
            'margin_of_safety': calc_params['margin_of_safety'],
            'safe_price': fair_value * (1 - calc_params['margin_of_safety']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_market(self, symbol: str) -> str:
        """检测市场类型"""
        if symbol.isdigit() and len(symbol) == 6:
            return 'cn'
        elif symbol.endswith('.HK'):
            return 'hk'
        else:
            return 'us'
    
    def _get_financial_data(self, symbol: str, market: str) -> Optional[Dict]:
        """获取财务数据"""
        data = {}
        
        try:
            if market == 'cn' and AKSHARE_AVAILABLE:
                # A股数据
                # 实时行情
                df_quote = ak.stock_zh_a_spot_em()
                stock_quote = df_quote[df_quote['代码'] == symbol]
                
                if not stock_quote.empty:
                    quote = stock_quote.iloc[0]
                    data['price'] = float(quote.get('最新价', 0))
                    data['name'] = quote.get('名称', '')
                
                # 财务数据
                try:
                    df_fin = ak.stock_financial_analysis_indicator(symbol=symbol)
                    if not df_fin.empty:
                        latest = df_fin.iloc[0]
                        
                        # 使用关键词匹配获取数据
                        def get_value(df, keywords, default=0):
                            for col in df.columns:
                                if any(kw in str(col) for kw in keywords):
                                    val = df[col].iloc[0] if isinstance(df, pd.DataFrame) else df[col]
                                    return float(val) if val else default
                            return default
                        
                        import pandas as pd
                        
                        data['eps'] = get_value(latest.to_frame().T, ['每股收益', 'EPS'])
                        data['bps'] = get_value(latest.to_frame().T, ['每股净资产', 'BPS'])
                        data['pe'] = get_value(latest.to_frame().T, ['市盈率', 'PE'])
                        data['pb'] = get_value(latest.to_frame().T, ['市净率', 'PB'])
                        data['dividend'] = get_value(latest.to_frame().T, ['每股股利', '分红']) * 10  # 年度
                        data['dividend_yield'] = get_value(latest.to_frame().T, ['股息率']) / 100
                        
                        # 现金流 (简化，实际需要从现金流量表获取)
                        data['free_cash_flow'] = get_value(latest.to_frame().T, ['自由现金流', 'FCF'])
                        
                except Exception as e:
                    print(f"    财务数据获取失败: {e}")
            
            else:
                # 美股/港股数据
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                data['price'] = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
                data['name'] = info.get('longName', symbol)
                data['eps'] = info.get('trailingEps', 0) or 0
                data['bps'] = info.get('bookValue', 0) or 0
                data['pe'] = info.get('trailingPE', 0) or 0
                data['pb'] = info.get('priceToBook', 0) or 0
                data['dividend'] = info.get('dividendRate', 0) or 0
                data['dividend_yield'] = info.get('dividendYield', 0) or 0
                
                # 自由现金流
                try:
                    cashflow = ticker.cashflow
                    if not cashflow.empty:
                        ocf = float(cashflow.loc['Operating Cash Flow'].iloc[0]) if 'Operating Cash Flow' in cashflow.index else 0
                        capex = float(cashflow.loc['Capital Expenditure'].iloc[0]) if 'Capital Expenditure' in cashflow.index else 0
                        data['free_cash_flow'] = ocf + capex  # capex为负数
                except:
                    data['free_cash_flow'] = 0
        
        except Exception as e:
            print(f"  数据获取失败: {e}")
            return None
        
        return data
    
    def _relative_valuation(self, data: Dict) -> Dict:
        """相对估值"""
        pe = data.get('pe', 0)
        pb = data.get('pb', 0)
        eps = data.get('eps', 0)
        bps = data.get('bps', 0)
        
        valuations = {}
        
        # PE估值
        if pe and pe > 0 and eps:
            # 假设合理PE为15
            reasonable_pe = 15
            valuations['pe_based'] = {
                'current_pe': pe,
                'reasonable_pe': reasonable_pe,
                'fair_value': eps * reasonable_pe,
                'overvalued': pe > reasonable_pe * 1.5
            }
        
        # PB估值
        if pb and pb > 0 and bps:
            # 假设合理PB为2
            reasonable_pb = 2
            valuations['pb_based'] = {
                'current_pb': pb,
                'reasonable_pb': reasonable_pb,
                'fair_value': bps * reasonable_pb,
                'overvalued': pb > reasonable_pb * 1.5
            }
        
        return valuations
    
    def _dcf_valuation(self, data: Dict, params: Dict) -> Dict:
        """DCF估值"""
        fcf = data.get('free_cash_flow', 0)
        
        if not fcf or fcf <= 0:
            return {
                'error': '自由现金流数据不可用',
                'fair_value': 0
            }
        
        discount_rate = params['discount_rate']
        terminal_growth = params['terminal_growth']
        forecast_years = params['forecast_years']
        
        # 简化DCF：假设FCF增长率为5%
        fcf_growth = 0.05
        
        # 计算未来现金流现值
        pv_fcf = 0
        for year in range(1, forecast_years + 1):
            future_fcf = fcf * ((1 + fcf_growth) ** year)
            pv = future_fcf / ((1 + discount_rate) ** year)
            pv_fcf += pv
        
        # 终值
        terminal_value = (fcf * ((1 + fcf_growth) ** forecast_years) * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_years)
        
        # 企业价值
        enterprise_value = pv_fcf + pv_terminal
        
        # 假设总股本 (简化，实际应获取)
        shares = 1e9  # 10亿股
        
        fair_value = enterprise_value / shares
        
        return {
            'method': 'DCF',
            'free_cash_flow': fcf,
            'growth_rate': fcf_growth,
            'discount_rate': discount_rate,
            'terminal_growth': terminal_growth,
            'forecast_years': forecast_years,
            'pv_fcf': pv_fcf,
            'pv_terminal': pv_terminal,
            'enterprise_value': enterprise_value,
            'fair_value': fair_value,
            'note': '简化DCF模型，实际估值需更详细财务数据'
        }
    
    def _ddm_valuation(self, data: Dict, params: Dict) -> Dict:
        """DDM估值"""
        dividend = data.get('dividend', 0)
        
        if not dividend or dividend <= 0:
            return {
                'error': '无股息数据，不适用DDM',
                'fair_value': 0
            }
        
        required_return = params['required_return']
        dividend_growth = params['dividend_growth']
        
        # Gordon Growth Model
        # P = D1 / (r - g)
        # D1 = D0 * (1 + g)
        
        d1 = dividend * (1 + dividend_growth)
        fair_value = d1 / (required_return - dividend_growth)
        
        return {
            'method': 'DDM (Gordon Growth)',
            'current_dividend': dividend,
            'dividend_growth': dividend_growth,
            'required_return': required_return,
            'd1': d1,
            'fair_value': fair_value,
            'note': '适用于稳定分红公司'
        }
    
    def _calculate_fair_value(self, valuations: Dict, data: Dict) -> float:
        """计算综合公允价值"""
        values = []
        weights = []
        
        # 相对估值
        if 'relative' in valuations:
            rel = valuations['relative']
            
            if 'pe_based' in rel and rel['pe_based'].get('fair_value', 0) > 0:
                values.append(rel['pe_based']['fair_value'])
                weights.append(0.3)
            
            if 'pb_based' in rel and rel['pb_based'].get('fair_value', 0) > 0:
                values.append(rel['pb_based']['fair_value'])
                weights.append(0.2)
        
        # DCF
        if 'dcf' in valuations and valuations['dcf'].get('fair_value', 0) > 0:
            values.append(valuations['dcf']['fair_value'])
            weights.append(0.3)
        
        # DDM
        if 'ddm' in valuations and valuations['ddm'].get('fair_value', 0) > 0:
            values.append(valuations['ddm']['fair_value'])
            weights.append(0.2)
        
        if not values:
            # 使用当前价格
            return data.get('price', 0)
        
        # 加权平均
        total_weight = sum(weights)
        fair_value = sum(v * w for v, w in zip(values, weights)) / total_weight if total_weight > 0 else sum(values) / len(values)
        
        return fair_value


# 快速使用函数
def calculate_valuation(symbol: str, **params) -> Dict:
    """快速计算估值"""
    calculator = ValuationCalculator()
    return calculator.calculate(symbol, **params)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("估值计算器 v1.0 测试")
    print("=" * 60)
    
    # 测试美股
    result = calculate_valuation('AAPL')
    
    if result['success']:
        print(f"\n=== {result['symbol']} ({result['market']}) ===")
        print(f"当前价格: ${result['current_price']:.2f}")
        print(f"公允价值: ${result['fair_value']:.2f}")
        print(f"安全价格: ${result['safe_price']:.2f} (安全边际{result['margin_of_safety']*100:.0f}%)")
        
        if 'relative' in result['valuations']:
            print("\n相对估值:")
            rel = result['valuations']['relative']
            if 'pe_based' in rel:
                print(f"  PE估值: ${rel['pe_based']['fair_value']:.2f} (当前PE: {rel['pe_based']['current_pe']:.1f})")
    else:
        print(f"\n估值失败: {result['error']}")
