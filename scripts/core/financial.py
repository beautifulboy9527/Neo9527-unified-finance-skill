#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一财务数据模块 - 整合 akshare + yfinance
A股用 akshare，美股/港股用 yfinance
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quote import detect_market


class FinancialDataFetcher:
    """财务数据获取器"""
    
    def __init__(self, symbol: str):
        self.symbol = str(symbol).replace('.SS', '').replace('.SZ', '')
        self.market = detect_market(symbol)
        
    def get_summary(self) -> Dict:
        """
        获取财务摘要
        """
        if self.market == 'cn':
            return self._get_summary_cn()
        else:
            return self._get_summary_global()
    
    def _get_summary_cn(self) -> Dict:
        """A股财务摘要 (akshare)"""
        result = {
            'symbol': self.symbol,
            'market': 'cn',
            'revenue_3y': [],
            'net_profit_3y': [],
            'gross_margin': None,
            'net_margin': None,
            'roe': None,
            'debt_ratio': None,
            'data_source': 'none',
            'update_time': None,
            'error': None
        }
        
        try:
            import akshare as ak
            import pandas as pd
            
            df = ak.stock_financial_abstract(symbol=self.symbol)
            
            if df is not None and len(df) > 0:
                # 查找关键数据行
                revenue_row = None
                profit_row = None
                roe_row = None
                gross_margin_row = None
                net_margin_row = None
                debt_ratio_row = None
                
                # 遍历找到指标行 - 使用精确匹配
                for idx, row in df.iterrows():
                    indicator = str(row.get('指标', '')) if '指标' in df.columns else str(row.iloc[1]) if len(row) > 1 else ''
                    
                    # 精确匹配，避免子串误匹配
                    if indicator == '营业总收入' or indicator == '营业收入':
                        revenue_row = row
                    elif indicator == '归母净利润' or indicator == '净利润':
                        profit_row = row
                    elif indicator == 'ROE' or indicator == '净资产收益率':
                        roe_row = row
                    elif indicator == '毛利率':
                        gross_margin_row = row
                    elif indicator == '净利率':
                        net_margin_row = row
                    elif indicator == '资产负债率':
                        debt_ratio_row = row
                
                # 提取近3年数据
                if revenue_row is not None:
                    for col in df.columns[2:5]:  # 最近3年
                        try:
                            val = revenue_row[col]
                            if pd.notna(val):
                                revenue_yi = float(val) / 1e8
                                result['revenue_3y'].append(round(revenue_yi, 2))
                        except:
                            pass
                
                if profit_row is not None:
                    for col in df.columns[2:5]:  # 最近3年
                        try:
                            val = profit_row[col]
                            if pd.notna(val):
                                # 数据已经是实际值，转换为亿
                                profit_yi = float(val) / 1e8
                                result['net_profit_3y'].append(round(profit_yi, 2))
                        except Exception as e:
                            pass
                
                # 提取最新指标值
                latest_col = df.columns[2] if len(df.columns) > 2 else None
                if latest_col:
                    if roe_row is not None:
                        try:
                            val = roe_row[latest_col]
                            result['roe'] = round(float(val), 2) if pd.notna(val) else None
                        except:
                            pass
                    
                    if gross_margin_row is not None:
                        try:
                            val = gross_margin_row[latest_col]
                            result['gross_margin'] = round(float(val), 2) if pd.notna(val) else None
                        except:
                            pass
                    
                    if net_margin_row is not None:
                        try:
                            val = net_margin_row[latest_col]
                            result['net_margin'] = round(float(val), 2) if pd.notna(val) else None
                        except:
                            pass
                    
                    if debt_ratio_row is not None:
                        try:
                            val = debt_ratio_row[latest_col]
                            result['debt_ratio'] = round(float(val), 2) if pd.notna(val) else None
                        except:
                            pass
                
                result['data_source'] = 'akshare'
                result['update_time'] = datetime.now().strftime('%Y-%m-%d')
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_summary_global(self) -> Dict:
        """美股/港股财务摘要"""
        result = {
            'symbol': self.symbol,
            'market': self.market,
            'revenue_3y': [],
            'net_profit_3y': [],
            'gross_margin': None,
            'net_margin': None,
            'roe': None,
            'debt_ratio': None,
            'data_source': 'none',
            'update_time': None,
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 基本信息
            result.update({
                'gross_margin': info.get('grossMargins'),
                'net_margin': info.get('profitMargins'),
                'roe': info.get('returnOnEquity'),
                'debt_ratio': info.get('debtToEquity'),
                'data_source': 'yfinance',
                'update_time': datetime.now().strftime('%Y-%m-%d')
            })
            
            # 历史营收/利润
            income_stmt = ticker.income_stmt
            if income_stmt is not None and len(income_stmt) > 0:
                for col in income_stmt.columns[:3]:  # 最近3年
                    try:
                        revenue = income_stmt.loc['Total Revenue', col] / 1e8
                        net_income = income_stmt.loc['Net Income', col] / 1e8
                        result['revenue_3y'].append(round(revenue, 2))
                        result['net_profit_3y'].append(round(net_income, 2))
                    except:
                        continue
                        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_fundflow(self, days: int = 10) -> Dict:
        """
        获取资金流向 (仅A股)
        """
        from datetime import datetime, timedelta
        
        result = {
            'symbol': self.symbol,
            'history': [],
            'summary': {},
            'data_source': 'none',
            'update_time': None,
            'data_freshness': None,
            'warning': None,
            'error': None
        }
        
        if self.market != 'cn':
            result['error'] = '资金流向仅支持A股'
            return result
        
        try:
            import akshare as ak
            
            market = 'sh' if self.symbol.startswith('6') else 'sz'
            df = ak.stock_individual_fund_flow(stock=self.symbol, market=market)
            
            if df is not None and len(df) > 0:
                history = []
                
                for _, row in df.head(days).iterrows():
                    values = row.values.tolist()
                    
                    entry = {
                        'date': str(values[0]) if len(values) > 0 else '',
                        'close': float(values[1]) if len(values) > 1 and values[1] else None,
                        'change_pct': float(values[2]) if len(values) > 2 and values[2] else None,
                        'main_net_inflow': round(float(values[5]) / 1e8 + float(values[7]) / 1e8, 4) if len(values) > 7 else None,
                        'retail_net_inflow': round(float(values[9]) / 1e8 + float(values[11]) / 1e8, 4) if len(values) > 11 else None,
                    }
                    history.append(entry)
                
                # 检查数据时效性
                if history:
                    latest_date_str = history[0].get('date', '')
                    try:
                        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
                        days_old = (datetime.now() - latest_date).days
                        
                        if days_old > 7:
                            result['warning'] = f'⚠️ 数据已过时 {days_old} 天 (最新: {latest_date_str})'
                            result['data_freshness'] = 'stale'
                        elif days_old > 3:
                            result['warning'] = f'数据延迟 {days_old} 天'
                            result['data_freshness'] = 'delayed'
                        else:
                            result['data_freshness'] = 'fresh'
                    except:
                        result['data_freshness'] = 'unknown'
                
                # 计算汇总
                total_main = sum(h['main_net_inflow'] or 0 for h in history)
                
                result['history'] = history
                result['summary'] = {
                    'total_main_inflow': round(total_main, 2),
                    'trend': 'inflow' if total_main > 0 else 'outflow'
                }
                result['data_source'] = 'akshare_fundflow'
                result['update_time'] = datetime.now().strftime('%Y-%m-%d')
                
        except Exception as e:
            result['error'] = str(e)
        
        return result


def get_financial_summary(symbol: str) -> Dict:
    """获取财务摘要"""
    fetcher = FinancialDataFetcher(symbol)
    return fetcher.get_summary()


def get_fundflow(symbol: str, days: int = 10) -> Dict:
    """获取资金流向"""
    fetcher = FinancialDataFetcher(symbol)
    return fetcher.get_fundflow(days)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='统一财务数据')
    parser.add_argument('--symbol', required=True, help='股票代码')
    parser.add_argument('--type', choices=['summary', 'fundflow'], default='summary')
    
    args = parser.parse_args()
    
    fetcher = FinancialDataFetcher(args.symbol)
    
    if args.type == 'summary':
        result = fetcher.get_summary()
    else:
        result = fetcher.get_fundflow()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
