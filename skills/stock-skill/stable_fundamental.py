#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
稳定财务数据 Skill v1.0

数据源优先级:
1. Baostock (最稳定，官方数据源)
2. Tushare (备用，需token)
3. AkShare (最后的备用)

支持:
- A股财务报表数据
- 关键财务指标计算
- 批量查询优化
- 自动缓存
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 数据源可用性检查
BAOSTOCK_AVAILABLE = False
TUSHARE_AVAILABLE = False
AKSHARE_AVAILABLE = False

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    pass

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    pass

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    pass


class StableFundamentalSkill:
    """稳定财务数据 Skill"""
    
    def __init__(self, tushare_token: str = None):
        """
        初始化
        
        Args:
            tushare_token: Tushare API token (可选)
        """
        self.name = "StableFundamentalSkill"
        self.version = "1.0.0"
        self.tushare_token = tushare_token
        
        # 初始化 Tushare
        if TUSHARE_AVAILABLE and tushare_token:
            ts.set_token(tushare_token)
            self.ts_pro = ts.pro_api()
        else:
            self.ts_pro = None
    
    def get_fundamentals(self, symbol: str) -> Dict:
        """
        获取财务数据
        
        Args:
            symbol: 股票代码 (如 "600519")
            
        Returns:
            财务数据字典
        """
        print(f"获取 {symbol} 财务数据...")
        
        # 标准化股票代码
        code = self._normalize_code(symbol)
        
        # 尝试 Baostock
        if BAOSTOCK_AVAILABLE:
            data = self._fetch_baostock(code)
            if data:
                return self._format_result(data, 'Baostock', 0.95)
        
        # 尝试 Tushare
        if TUSHARE_AVAILABLE and self.ts_pro:
            data = self._fetch_tushare(symbol)
            if data:
                return self._format_result(data, 'Tushare', 0.90)
        
        # 尝试 AkShare
        if AKSHARE_AVAILABLE:
            data = self._fetch_akshare(symbol)
            if data:
                return self._format_result(data, 'AkShare', 0.70)
        
        return {
            'success': False,
            'error': '所有数据源均不可用',
            'symbol': symbol
        }
    
    def batch_get_fundamentals(self, symbols: List[str]) -> pd.DataFrame:
        """
        批量获取财务数据
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            DataFrame
        """
        results = []
        
        for i, symbol in enumerate(symbols):
            if i % 20 == 0:
                print(f"  进度: {i}/{len(symbols)}")
            
            data = self.get_fundamentals(symbol)
            if data.get('success'):
                results.append(data)
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def _normalize_code(self, symbol: str) -> str:
        """标准化股票代码"""
        # 移除前缀
        code = symbol.replace('SH', '').replace('SZ', '').replace('.SS', '').replace('.SZ', '')
        
        # 添加市场前缀
        if code.startswith('6'):
            return f"sh.{code}"
        else:
            return f"sz.{code}"
    
    def _fetch_baostock(self, code: str) -> Optional[Dict]:
        """从 Baostock 获取数据"""
        try:
            # 登录
            lg = bs.login()
            if lg.error_code != '0':
                print(f"  Baostock 登录失败: {lg.error_msg}")
                return None
            
            # 获取最近一年的数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            # 查询盈利能力 (参数名: code, year, quarter)
            current_year = datetime.now().year
            current_quarter = (datetime.now().month - 1) // 3 + 1
            
            # 查询最近4个季度
            rs = bs.query_profit_data(code=code, year=str(current_year), quarter=str(current_quarter))
            
            if rs.error_code != '0':
                print(f"  Baostock 查询失败: {rs.error_msg}")
                bs.logout()
                return None
            
            # 获取数据
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            bs.logout()
            
            if not data_list:
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            if df.empty:
                return None
            
            # 提取最新数据
            latest = df.iloc[0]
            
            return {
                'roe': self._safe_float(latest.get('roe')),
                'roa': self._safe_float(latest.get('roa')),
                'gross_margin': self._safe_float(latest.get('grossProfitMargin')),
                'net_margin': self._safe_float(latest.get('netProfitMargin')),
                'debt_ratio': self._safe_float(latest.get('debtToAssets')),
                'current_ratio': self._safe_float(latest.get('currentRatio')),
            }
            
        except Exception as e:
            print(f"  Baostock 错误: {e}")
            try:
                bs.logout()
            except:
                pass
            return None
    
    def _fetch_tushare(self, symbol: str) -> Optional[Dict]:
        """从 Tushare 获取数据"""
        try:
            if not self.ts_pro:
                return None
            
            # 获取财务指标
            df = self.ts_pro.daily_basic(ts_code=symbol, 
                                         fields='pe,pb,roe,debt_ratio,current_ratio')
            
            if df.empty:
                return None
            
            latest = df.iloc[0]
            
            return {
                'pe': self._safe_float(latest.get('pe')),
                'pb': self._safe_float(latest.get('pb')),
                'roe': self._safe_float(latest.get('roe')),
                'debt_ratio': self._safe_float(latest.get('debt_ratio')),
                'current_ratio': self._safe_float(latest.get('current_ratio')),
            }
            
        except Exception as e:
            print(f"  Tushare 错误: {e}")
            return None
    
    def _fetch_akshare(self, symbol: str) -> Optional[Dict]:
        """从 AkShare 获取数据 (备用)"""
        try:
            # 尝试利润表
            df = ak.stock_financial_report_sina(stock=symbol, symbol="利润表")
            
            if df.empty:
                return None
            
            latest = df.iloc[0]
            
            # 计算指标
            revenue = self._safe_float(latest.get('营业收入'))
            profit = self._safe_float(latest.get('净利润'))
            cost = self._safe_float(latest.get('营业成本', 0))
            
            net_margin = (profit / revenue * 100) if revenue > 0 else 0
            gross_margin = ((revenue - cost) / revenue * 100) if revenue > 0 else 0
            
            return {
                'total_revenue': revenue,
                'net_profit': profit,
                'net_margin': net_margin,
                'gross_margin': gross_margin,
            }
            
        except Exception as e:
            print(f"  AkShare 错误: {e}")
            return None
    
    def _safe_float(self, value) -> float:
        """安全转换为浮点数"""
        if value is None:
            return 0.0
        try:
            return float(value)
        except:
            return 0.0
    
    def _format_result(self, data: Dict, source: str, confidence: float) -> Dict:
        """格式化结果"""
        return {
            'success': True,
            'symbol': data.get('symbol', ''),
            'data': data,
            'data_source': [source],
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'provenance': f'查询日期: {datetime.now().strftime("%Y-%m-%d")}',
        }


# 快速使用函数
def get_stable_fundamentals(symbol: str, tushare_token: str = None) -> Dict:
    """快速获取稳定财务数据"""
    skill = StableFundamentalSkill(tushare_token)
    return skill.get_fundamentals(symbol)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("稳定财务数据 Skill v1.0 测试")
    print("=" * 60)
    
    print(f"\n数据源可用性:")
    print(f"  Baostock: {'✅' if BAOSTOCK_AVAILABLE else '❌'}")
    print(f"  Tushare:  {'✅' if TUSHARE_AVAILABLE else '❌'}")
    print(f"  AkShare:  {'✅' if AKSHARE_AVAILABLE else '❌'}")
    
    # 测试获取数据
    result = get_stable_fundamentals('600519')
    
    if result['success']:
        print(f"\n=== 600519 财务数据 ===")
        print(f"数据源: {result['data_source']}")
        print(f"置信度: {result['confidence']}")
        
        data = result['data']
        if data.get('roe'):
            print(f"ROE: {data['roe']:.2f}%")
        if data.get('gross_margin'):
            print(f"毛利率: {data['gross_margin']:.2f}%")
        if data.get('net_margin'):
            print(f"净利率: {data['net_margin']:.2f}%")
    else:
        print(f"\n获取失败: {result['error']}")
