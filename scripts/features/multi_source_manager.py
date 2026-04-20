#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源管理器 v1.0
自动切换数据源，确保数据完整性

优先级：
1. yfinance (主源)
2. 东方财富 (备用)
3. 新浪财经 (备用)
"""

import sys
import time
from typing import Dict, Optional
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class MultiSourceManager:
    """多数据源管理器"""
    
    def __init__(self):
        self.sources = {
            'yfinance': self._fetch_yfinance,
            'eastmoney': self._fetch_eastmoney,
            'sina': self._fetch_sina,
        }
        self.timeout = 5  # 减少超时时间
        self.retry_count = 1  # 减少重试次数
        self.cache = {}  # 简单缓存
        self.cache_time = {}  # 缓存时间
    
    def fetch_stock_data(self, symbol: str) -> Dict:
        """
        从多个数据源获取股票数据
        自动降级：yfinance → 东方财富 → 新浪
        """
        # 检查缓存（5分钟有效期）
        import time
        cache_key = f"stock_{symbol}"
        if cache_key in self.cache:
            cache_age = time.time() - self.cache_time.get(cache_key, 0)
            if cache_age < 300:  # 5分钟缓存
                print(f"✅ 使用缓存数据（{int(cache_age)}秒前）")
                return self.cache[cache_key]
        
        result = {
            'success': False,
            'source': None,
            'price': {},
            'hist': None,
            'info': {},
            'errors': []
        }
        
        # 尝试各个数据源
        for source_name, fetch_func in self.sources.items():
            try:
                print(f"尝试数据源: {source_name}")
                
                # 设置超时
                import signal
                
                data = fetch_func(symbol)
                
                if data and self._validate_data(data):
                    result['success'] = True
                    result['source'] = source_name
                    result['price'] = data.get('price', {})
                    result['hist'] = data.get('hist')
                    result['info'] = data.get('info', {})
                    print(f"✅ 数据源 {source_name} 成功")
                    
                    # 缓存结果
                    self.cache[cache_key] = result
                    self.cache_time[cache_key] = time.time()
                    break
                else:
                    result['errors'].append(f"{source_name}: 数据验证失败")
                    print(f"⚠️ 数据源 {source_name} 数据不完整")
                    
            except Exception as e:
                error_msg = f"{source_name}: {str(e)[:50]}"
                result['errors'].append(error_msg)
                print(f"❌ 数据源 {source_name} 失败: {str(e)[:50]}")
                continue
        
        return result
    
    def _fetch_yfinance(self, symbol: str) -> Optional[Dict]:
        """从yfinance获取数据"""
        import yfinance as yf
        
        # 尝试不同的市场代码
        suffixes = ['.SS', '.SZ', '']
        
        for suffix in suffixes:
            try:
                yf_symbol = f"{symbol}{suffix}"
                ticker = yf.Ticker(yf_symbol)
                
                # 获取历史数据
                hist = ticker.history(period='6mo')
                
                if hist.empty:
                    continue
                
                # 获取基本信息
                info = ticker.info
                
                # 提取价格数据
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                
                # 验证数据有效性
                if pd.isna(current_price) or current_price <= 0:
                    continue
                
                return {
                    'price': {
                        'current': float(current_price),
                        'change_pct': float(change_pct),
                        'high': float(hist['High'].iloc[-1]),
                        'low': float(hist['Low'].iloc[-1]),
                        'volume': float(hist['Volume'].iloc[-1]),
                    },
                    'hist': hist,
                    'info': info
                }
                
            except Exception as e:
                continue
        
        return None
    
    def _fetch_eastmoney(self, symbol: str) -> Optional[Dict]:
        """从东方财富获取数据（简化版）"""
        try:
            import akshare as ak
            
            # 使用akshare获取数据
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            
            if df.empty:
                return None
            
            # 获取最近数据
            recent = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else recent
            
            current_price = float(recent['收盘'])
            prev_price = float(prev['收盘'])
            change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
            
            # 转换为yfinance格式
            hist = pd.DataFrame({
                'Close': df['收盘'],
                'High': df['最高'],
                'Low': df['最低'],
                'Volume': df['成交量'],
            })
            
            return {
                'price': {
                    'current': current_price,
                    'change_pct': change_pct,
                    'high': float(recent['最高']),
                    'low': float(recent['最低']),
                    'volume': float(recent['成交量']),
                },
                'hist': hist,
                'info': {}
            }
            
        except ImportError:
            print("⚠️ akshare未安装，跳过东方财富数据源")
            return None
        except Exception as e:
            print(f"东方财富获取失败: {str(e)[:50]}")
            return None
    
    def _fetch_sina(self, symbol: str) -> Optional[Dict]:
        """从新浪财经获取数据（简化版）"""
        try:
            import akshare as ak
            
            # 使用akshare的新浪接口
            df = ak.stock_zh_a_spot_em()
            
            # 筛选目标股票
            stock = df[df['代码'] == symbol]
            
            if stock.empty:
                return None
            
            row = stock.iloc[0]
            
            current_price = float(row['最新价'])
            change_pct = float(row['涨跌幅'])
            
            return {
                'price': {
                    'current': current_price,
                    'change_pct': change_pct,
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'volume': float(row['成交量']),
                },
                'hist': None,  # 新浪接口只有当前数据
                'info': {
                    'name': row['名称'],
                }
            }
            
        except ImportError:
            print("⚠️ akshare未安装，跳过新浪数据源")
            return None
        except Exception as e:
            print(f"新浪获取失败: {str(e)[:50]}")
            return None
    
    def _validate_data(self, data: Dict) -> bool:
        """验证数据完整性"""
        if not data:
            return False
        
        price = data.get('price', {})
        
        # 必须有当前价格
        current = price.get('current')
        if not current or pd.isna(current) or current <= 0:
            return False
        
        return True
    
    def fill_missing_data(self, result: Dict, symbol: str) -> Dict:
        """
        填充缺失数据
        如果主数据源缺少某些数据，尝试从备用源补充
        """
        price = result.get('price', {})
        
        # 检查是否需要补充价格数据
        if pd.isna(price.get('current')) or price.get('current', 0) <= 0:
            print("⚠️ 检测到价格数据缺失，尝试备用数据源...")
            
            backup_data = self.fetch_stock_data(symbol)
            
            if backup_data['success']:
                # 补充缺失数据
                result['price'] = backup_data['price']
                result['backup_source'] = backup_data['source']
                print(f"✅ 已从 {backup_data['source']} 补充价格数据")
        
        return result


def get_stock_data_with_fallback(symbol: str) -> Dict:
    """便捷函数：带降级的数据获取"""
    manager = MultiSourceManager()
    return manager.fetch_stock_data(symbol)


if __name__ == '__main__':
    print("多数据源管理器 v1.0")
    print("\n支持的降级策略:")
    print("1. yfinance (主源)")
    print("2. 东方财富 (备用)")  
    print("3. 新浪财经 (备用)")
    print("\n特性:")
    print("- 自动降级：主源失败自动切换备用源")
    print("- 数据验证：确保数据完整有效")
    print("- 缺失补充：自动补充缺失数据")
