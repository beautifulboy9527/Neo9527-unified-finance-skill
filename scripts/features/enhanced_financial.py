#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强财务分析模块 - 完整集成自 akshare-data skill
支持 A股/港股/美股 财务数据、宏观数据、指数数据
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class EnhancedFinancialAnalyzer:
    """
    增强财务分析器 - 完整集成自 akshare-data skill
    
    能力:
    - A股财务数据 (实时/历史)
    - 港股数据
    - 美股数据
    - 宏观经济数据 (GDP/CPI/PMI)
    - 指数数据
    - 数据缓存
    """
    
    def __init__(self):
        self.cache_dir = OUTPUT_DIR.parent / 'cache' / 'akshare'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, func_name: str, **kwargs) -> str:
        """生成缓存键"""
        import hashlib
        params_str = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
        key_str = f"{func_name}:{params_str}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[Any]:
        """从缓存获取数据"""
        import pandas as pd
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        if not cache_file.exists():
            return None
        
        # 检查过期
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_time > timedelta(hours=max_age_hours):
            return None
        
        try:
            return pd.read_parquet(cache_file)
        except:
            return None
    
    def _save_to_cache(self, data, cache_key: str) -> bool:
        """保存数据到缓存"""
        import pandas as pd
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        try:
            if isinstance(data, pd.DataFrame):
                data.to_parquet(cache_file, index=False)
                return True
        except:
            pass
        return False
    
    def get_stock_list(self, market: str = 'a') -> Dict:
        """
        获取股票列表
        
        Args:
            market: 市场类型 (a/hk/us)
            
        Returns:
            股票列表
        """
        result = {
            'market': market,
            'stocks': [],
            'count': 0,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            import pandas as pd
            
            cache_key = self._get_cache_key('stock_list', market=market)
            cached = self._get_from_cache(cache_key, max_age_hours=24)
            
            if cached is not None:
                stocks = cached.to_dict('records')
            else:
                if market == 'a':
                    df = ak.stock_zh_a_spot_em()
                    stocks = df[['代码', '名称']].rename(columns={'代码': 'code', '名称': 'name'}).to_dict('records')
                elif market == 'hk':
                    df = ak.stock_hk_spot_em()
                    stocks = df[['代码', '名称']].rename(columns={'代码': 'code', '名称': 'name'}).to_dict('records')
                elif market == 'us':
                    df = ak.stock_us_spot_em()
                    stocks = df[['代码', '名称']].rename(columns={'代码': 'code', '名称': 'name'}).to_dict('records')
                else:
                    result['error'] = f'不支持的市场: {market}'
                    return result
                
                # 缓存
                cache_df = pd.DataFrame(stocks)
                self._save_to_cache(cache_df, cache_key)
            
            result['stocks'] = stocks[:100]  # 限制返回数量
            result['count'] = len(stocks)
            result['data_source'] = 'akshare'
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_realtime_quotes(self, symbols: List[str]) -> Dict:
        """
        获取实时行情
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            行情数据
        """
        result = {
            'quotes': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            # 获取全市场数据
            df = ak.stock_zh_a_spot_em()
            
            for symbol in symbols:
                # 去除后缀
                code = symbol.replace('.SH', '').replace('.SZ', '')
                
                match = df[df['代码'] == code]
                if not match.empty:
                    row = match.iloc[0]
                    result['quotes'][symbol] = {
                        'code': code,
                        'name': row.get('名称', ''),
                        'price': float(row.get('最新价', 0)),
                        'change': float(row.get('涨跌幅', 0)),
                        'volume': float(row.get('成交量', 0)),
                        'amount': float(row.get('成交额', 0)),
                        'high': float(row.get('最高', 0)),
                        'low': float(row.get('最低', 0)),
                        'open': float(row.get('今开', 0)),
                        'prev_close': float(row.get('昨收', 0))
                    }
            
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = 'daily',
        start_date: str = None,
        end_date: str = None,
        adjust: str = 'qfq'
    ) -> Dict:
        """
        获取历史数据
        
        Args:
            symbol: 股票代码
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权方式 (qfq/hfq/空)
            
        Returns:
            历史数据
        """
        result = {
            'symbol': symbol,
            'period': period,
            'data': [],
            'count': 0,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            # 去除后缀
            code = symbol.replace('.SH', '').replace('.SZ', '')
            
            # 默认日期
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df.empty:
                result['error'] = '无历史数据'
                return result
            
            # 转换为列表
            data = df.to_dict('records')
            
            result['data'] = data[:500]  # 限制返回数量
            result['count'] = len(data)
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_financial_statements(self, symbol: str) -> Dict:
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
            
        Returns:
            财务报表数据
        """
        result = {
            'symbol': symbol,
            'income': {},
            'balance': {},
            'cashflow': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            code = symbol.replace('.SH', '').replace('.SZ', '')
            
            # 利润表
            try:
                income_df = ak.stock_financial_analysis_sheet(symbol=code, indicator='利润表')
                if not income_df.empty:
                    result['income'] = income_df.head(4).to_dict('records')
            except:
                pass
            
            # 资产负债表
            try:
                balance_df = ak.stock_financial_analysis_sheet(symbol=code, indicator='资产负债表')
                if not balance_df.empty:
                    result['balance'] = balance_df.head(4).to_dict('records')
            except:
                pass
            
            # 现金流量表
            try:
                cashflow_df = ak.stock_financial_analysis_sheet(symbol=code, indicator='现金流量表')
                if not cashflow_df.empty:
                    result['cashflow'] = cashflow_df.head(4).to_dict('records')
            except:
                pass
            
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_macro_data(self, indicator: str = 'gdp') -> Dict:
        """
        获取宏观经济数据
        
        Args:
            indicator: 指标类型 (gdp/cpi/pmi)
            
        Returns:
            宏观数据
        """
        result = {
            'indicator': indicator,
            'data': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            cache_key = self._get_cache_key('macro', indicator=indicator)
            cached = self._get_from_cache(cache_key, max_age_hours=48)
            
            if cached is not None:
                result['data'] = cached.to_dict('records')
            else:
                if indicator == 'gdp':
                    df = ak.macro_china_gdp()
                elif indicator == 'cpi':
                    df = ak.macro_china_cpi()
                elif indicator == 'pmi':
                    df = ak.macro_china_pmi()
                else:
                    result['error'] = f'不支持的指标: {indicator}'
                    return result
                
                result['data'] = df.to_dict('records')
                self._save_to_cache(df, cache_key)
            
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_index_data(self, index: str = 'sh000001') -> Dict:
        """
        获取指数数据
        
        Args:
            index: 指数代码
            
        Returns:
            指数数据
        """
        result = {
            'index': index,
            'data': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            # 上证指数
            if index in ['sh000001', '000001']:
                df = ak.stock_zh_index_daily(symbol='sh000001')
            # 深证成指
            elif index in ['sz399001', '399001']:
                df = ak.stock_zh_index_daily(symbol='sz399001')
            # 创业板指
            elif index in ['sz399006', '399006']:
                df = ak.stock_zh_index_daily(symbol='sz399006')
            else:
                df = ak.stock_zh_index_daily(symbol=index)
            
            if df.empty:
                result['error'] = '无指数数据'
                return result
            
            result['data'] = df.tail(100).to_dict('records')
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_industry_data(self) -> Dict:
        """
        获取行业板块数据
        
        Returns:
            行业板块数据
        """
        result = {
            'industries': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            cache_key = self._get_cache_key('industry')
            cached = self._get_from_cache(cache_key, max_age_hours=6)
            
            if cached is not None:
                result['industries'] = cached.to_dict('records')
            else:
                df = ak.stock_board_industry_name_em()
                result['industries'] = df.to_dict('records')
                self._save_to_cache(df, cache_key)
            
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_fund_flow(self, symbol: str) -> Dict:
        """
        获取资金流向
        
        Args:
            symbol: 股票代码
            
        Returns:
            资金流向数据
        """
        result = {
            'symbol': symbol,
            'flow': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import akshare as ak
            
            code = symbol.replace('.SH', '').replace('.SZ', '')
            
            # 个股资金流
            df = ak.stock_individual_fund_flow(stock=code, market='sh' if code.startswith('6') else 'sz')
            
            if df.empty:
                result['error'] = '无资金流向数据'
                return result
            
            result['flow'] = df.head(10).to_dict('records')
            result['data_source'] = 'akshare'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def get_stock_list(market: str = 'a') -> Dict:
    """获取股票列表"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_stock_list(market)


def get_realtime_quotes(symbols: List[str]) -> Dict:
    """获取实时行情"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_realtime_quotes(symbols)


def get_historical_data(symbol: str, period: str = 'daily', start_date: str = None, end_date: str = None) -> Dict:
    """获取历史数据"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_historical_data(symbol, period, start_date, end_date)


def get_financial_statements(symbol: str) -> Dict:
    """获取财务报表"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_financial_statements(symbol)


def get_macro_data(indicator: str = 'gdp') -> Dict:
    """获取宏观数据"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_macro_data(indicator)


def get_index_data(index: str = 'sh000001') -> Dict:
    """获取指数数据"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_index_data(index)


def get_industry_data() -> Dict:
    """获取行业板块数据"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_industry_data()


def get_fund_flow(symbol: str) -> Dict:
    """获取资金流向"""
    analyzer = EnhancedFinancialAnalyzer()
    return analyzer.get_fund_flow(symbol)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='增强财务分析 - 完整集成自 akshare-data skill')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # stock-list
    list_parser = subparsers.add_parser('list', help='股票列表')
    list_parser.add_argument('--market', default='a', help='市场 (a/hk/us)')
    
    # quotes
    quotes_parser = subparsers.add_parser('quotes', help='实时行情')
    quotes_parser.add_argument('symbols', nargs='+', help='股票代码')
    
    # history
    hist_parser = subparsers.add_parser('history', help='历史数据')
    hist_parser.add_argument('symbol', help='股票代码')
    hist_parser.add_argument('--period', default='daily', help='周期')
    hist_parser.add_argument('--start', help='开始日期')
    hist_parser.add_argument('--end', help='结束日期')
    
    # financial
    fin_parser = subparsers.add_parser('financial', help='财务报表')
    fin_parser.add_argument('symbol', help='股票代码')
    
    # macro
    macro_parser = subparsers.add_parser('macro', help='宏观数据')
    macro_parser.add_argument('--indicator', default='gdp', help='指标 (gdp/cpi/pmi)')
    
    # index
    index_parser = subparsers.add_parser('index', help='指数数据')
    index_parser.add_argument('--code', default='sh000001', help='指数代码')
    
    # industry
    subparsers.add_parser('industry', help='行业板块')
    
    # fund-flow
    flow_parser = subparsers.add_parser('flow', help='资金流向')
    flow_parser.add_argument('symbol', help='股票代码')
    
    args = parser.parse_args()
    
    analyzer = EnhancedFinancialAnalyzer()
    
    if args.command == 'list':
        result = analyzer.get_stock_list(args.market)
    elif args.command == 'quotes':
        result = analyzer.get_realtime_quotes(args.symbols)
    elif args.command == 'history':
        result = analyzer.get_historical_data(args.symbol, args.period, args.start, args.end)
    elif args.command == 'financial':
        result = analyzer.get_financial_statements(args.symbol)
    elif args.command == 'macro':
        result = analyzer.get_macro_data(args.indicator)
    elif args.command == 'index':
        result = analyzer.get_index_data(args.code)
    elif args.command == 'industry':
        result = analyzer.get_industry_data()
    elif args.command == 'flow':
        result = analyzer.get_fund_flow(args.symbol)
    else:
        parser.print_help()
        sys.exit(0)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
