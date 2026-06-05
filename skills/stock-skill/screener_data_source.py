#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选股器数据源集成模块 v1.0
整合 MultiSourceManager + UnifiedDataLayer，提供稳定的数据获取

Phase 4 - 数据源稳定性
"""

import sys
import os
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


class DataSourceHealth:
    """数据源健康状态 - 参考 data_source_manager.py"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_available = True
        self.last_check_time = None
        self.failure_count = 0
        self.success_count = 0
        self.avg_response_time = 0
        self.last_error = None
    
    def record_success(self, response_time: float):
        """记录成功请求"""
        self.success_count += 1
        self.failure_count = max(0, self.failure_count - 1)
        
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.8 + response_time * 0.2)
        
        self.is_available = True
        self.last_check_time = datetime.now()
    
    def record_failure(self, error: str):
        """记录失败请求"""
        self.failure_count += 1
        self.last_error = error
        self.last_check_time = datetime.now()
        
        if self.failure_count >= 3:
            self.is_available = False
            logger.warning(f"数据源 {self.name} 已标记为不可用: {error}")
    
    def get_health_score(self) -> float:
        """获取健康分数 (0-100)"""
        if self.success_count == 0 and self.failure_count == 0:
            return 100
        
        total = self.success_count + self.failure_count
        success_rate = self.success_count / total if total > 0 else 0
        return success_rate * 100


class DataCache:
    """数据缓存 - 参考 data_source_manager.py"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        if datetime.now() - entry['timestamp'] > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            return None
        
        return entry['data']
    
    def set(self, key: str, data: Dict):
        """设置缓存数据"""
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()


class ScreenerDataSourceManager:
    """选股器数据源管理器 - 整合健康检查 + 缓存 + 降级"""
    
    def __init__(self):
        self.health_checker = {}
        self.cache = DataCache(max_size=200, ttl_seconds=300)  # 5分钟缓存
        
        # 数据源优先级
        self.sources = ['akshare', 'eastmoney', 'sina']
        for source in self.sources:
            self.health_checker[source] = DataSourceHealth(source)
    
    def get_best_source(self) -> str:
        """获取最佳数据源"""
        sorted_sources = sorted(
            self.sources,
            key=lambda s: self.health_checker[s].get_health_score(),
            reverse=True
        )
        
        for source in sorted_sources:
            if self.health_checker[source].is_available:
                return source
        
        return self.sources[0]
    
    def fetch_with_retry(self, fetch_func, max_retries: int = 2, *args, **kwargs) -> Any:
        """带重试的数据获取"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = fetch_func(*args, **kwargs)
                response_time = time.time() - start_time
                
                current_source = self.get_best_source()
                self.health_checker[current_source].record_success(response_time)
                
                return result
                
            except Exception as e:
                last_error = e
                current_source = self.get_best_source()
                self.health_checker[current_source].record_failure(str(e))
                
                if attempt < max_retries - 1:
                    delay = 1.0 * (2 ** attempt)  # 指数退避
                    logger.warning(f"第{attempt + 1}次重试失败，{delay}秒后重试: {e}")
                    time.sleep(delay)
        
        logger.error(f"重试{max_retries}次后仍失败: {last_error}")
        return None
    
    def get_stock_pool_with_fallback(self, scope: str) -> List[str]:
        """获取股票池（带降级）"""
        cache_key = f"pool_{scope}"
        
        # 尝试缓存
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"从缓存获取股票池: {scope}")
            return cached
        
        stocks = []
        
        # 主源: akshare
        try:
            stocks = self._fetch_pool_akshare(scope)
            if stocks:
                self.health_checker['akshare'].record_success(1.0)
                self.cache.set(cache_key, stocks)
                return stocks
        except Exception as e:
            self.health_checker['akshare'].record_failure(str(e))
            logger.warning(f"akshare获取股票池失败: {e}")
        
        # 备用源: 本地缓存或简化列表
        logger.warning("使用备用股票池")
        stocks = self._fetch_pool_fallback(scope)
        
        if stocks:
            self.cache.set(cache_key, stocks)
        
        return stocks
    
    def _fetch_pool_akshare(self, scope: str) -> List[str]:
        """使用akshare获取股票池"""
        if not AKSHARE_AVAILABLE:
            return []
        
        if scope == 'hs300':
            df = ak.index_stock_cons_weight_csindex(symbol='000300')
            return df['成分券代码'].tolist()
        elif scope == 'zz500':
            df = ak.index_stock_cons_weight_csindex(symbol='000905')
            return df['成分券代码'].tolist()
        elif scope == 'a50':
            df = ak.index_stock_cons_weight_csindex(symbol='000016')
            return df['成分券代码'].tolist()
        elif scope == 'all':
            df = ak.stock_zh_a_spot_em()
            return df['代码'].tolist()
        else:
            df = ak.index_stock_cons_weight_csindex(symbol='000300')
            return df['成分券代码'].tolist()
    
    def _fetch_pool_fallback(self, scope: str) -> List[str]:
        """备用股票池（简化版）"""
        # 增量缓存或常见成分股
        fallback_pools = {
            'hs300': ['600519', '601318', '600036', '601166', '600276', 
                      '600030', '601888', '600887', '601012', '600000'],
            'a50': ['600519', '601318', '600036', '601166', '600276'],
        }
        return fallback_pools.get(scope, fallback_pools['hs300'])
    
    def get_financial_data_with_fallback(self, code: str) -> Dict:
        """获取财务数据（带降级）"""
        cache_key = f"financial_{code}"
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data = {}
        
        # 主源
        try:
            data = self._fetch_financial_akshare(code)
            if data and data.get('roe'):
                self.health_checker['akshare'].record_success(0.5)
                self.cache.set(cache_key, data)
                return data
        except Exception as e:
            self.health_checker['akshare'].record_failure(str(e))
        
        # 不使用默认财务值。缺数据时返回明确的不可用状态，供选股器剔除或降权。
        return self._get_financial_unavailable(code)
    
    def _fetch_financial_akshare(self, code: str) -> Dict:
        """使用akshare获取财务数据"""
        if not AKSHARE_AVAILABLE:
            return {}
        
        df = ak.stock_financial_analysis_indicator(symbol=code)
        
        if df is None or df.empty:
            return {}
        
        latest = df.iloc[0]
        
        def _num(value):
            if value is None:
                return None
            try:
                text = str(value).replace(",", "").replace("%", "").strip()
                if text in {"", "--", "None", "nan", "NaN", "暂无数据", "-"}:
                    return None
                return float(text)
            except:
                return None
        
        data = {
            'code': code,
            'pe': _num(latest.get('市盈率')),
            'pb': _num(latest.get('市净率')),
            'roe': _num(latest.get('净资产收益率')),
            'roa': _num(latest.get('总资产净利润(ROA)')),
            'gross_margin': _num(latest.get('销售毛利率')),
            'net_margin': _num(latest.get('销售净利率')),
            'debt_ratio': _num(latest.get('资产负债率')),
            'current_ratio': _num(latest.get('流动比率')),
            'data_quality': 'primary',
        }
        
        # 成长指标
        if len(df) >= 2:
            prev = df.iloc[1]
            prev_roe = _num(prev.get('净资产收益率'))
            if data['roe'] and prev_roe:
                data['roe_growth'] = data['roe'] - prev_roe
        
        return data
    
    def _get_financial_unavailable(self, code: str) -> Dict:
        """财务数据不可用占位。字段保持 None，避免默认值污染选股结果。"""
        return {
            'code': code,
            'pe': None,
            'pb': None,
            'roe': None,
            'roa': None,
            'gross_margin': None,
            'net_margin': None,
            'debt_ratio': None,
            'current_ratio': None,
            'roe_growth': None,
            'data_quality': 'unavailable',
            'missing_reason': '未取得可验证财务数据，未使用默认值补齐',
        }
    
    def get_kline_with_fallback(self, code: str, days: int = 60) -> Optional[Dict]:
        """获取K线数据（带降级）"""
        cache_key = f"kline_{code}_{days}"
        
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            if AKSHARE_AVAILABLE:
                df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
                
                if df and len(df) >= days:
                    prices = df['收盘'].tolist()[-days:]
                    volumes = df['成交量'].tolist()[-days:]
                    
                    data = {
                        'prices': prices,
                        'volumes': volumes,
                        'data_quality': 'primary',
                    }
                    
                    self.health_checker['akshare'].record_success(0.5)
                    self.cache.set(cache_key, data)
                    return data
        except Exception as e:
            self.health_checker['akshare'].record_failure(str(e))
        
        return None
    
    def get_health_report(self) -> Dict:
        """获取健康报告"""
        report = {}
        
        for source, health in self.health_checker.items():
            report[source] = {
                'available': health.is_available,
                'health_score': health.get_health_score(),
                'success_count': health.success_count,
                'failure_count': health.failure_count,
                'avg_response_time': f"{health.avg_response_time:.2f}s",
                'last_error': health.last_error,
            }
        
        return report
    
    def print_health_report(self):
        """打印健康报告"""
        report = self.get_health_report()
        
        print("\n" + "=" * 60)
        print("数据源健康报告")
        print("=" * 60)
        
        for source, info in report.items():
            status = "✅ 可用" if info['available'] else "❌ 不可用"
            print(f"\n{source}:")
            print(f"  状态: {status}")
            print(f"  健康分数: {info['health_score']:.1f}/100")
            print(f"  成功/失败: {info['success_count']}/{info['failure_count']}")
            if info['last_error']:
                print(f"  最后错误: {info['last_error']}")


class DataQualityScorer:
    """数据质量评分器 - 参考 unified_data_layer.py"""
    
    @staticmethod
    def get_quality_label(score: float) -> tuple:
        """获取数据质量标签"""
        if score >= 90:
            return '高置信度', '✅', '数据完整可靠'
        elif score >= 70:
            return '中等置信度', '⚠️', '部分数据为估算值'
        elif score >= 50:
            return '低置信度', '❌', '大量数据缺失，建议谨慎使用'
        else:
            return '不可用', '🚫', '数据严重缺失，不可依赖'
    
    @staticmethod
    def score_financial_data(data: Dict) -> float:
        """评分财务数据"""
        if not data:
            return 0
        
        critical_fields = ['pe', 'pb', 'roe']
        important_fields = ['gross_margin', 'net_margin', 'debt_ratio']
        
        def is_valid(value):
            if value is None:
                return False
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                return False
            return True
        
        critical_score = sum(1 for f in critical_fields if is_valid(data.get(f))) / len(critical_fields) * 60
        important_score = sum(1 for f in important_fields if is_valid(data.get(f))) / len(important_fields) * 40
        
        return critical_score + important_score
    
    @staticmethod
    def add_quality_to_result(result: Dict) -> Dict:
        """为选股结果添加质量标签"""
        if 'stocks' in result:
            for stock in result['stocks']:
                score = DataQualityScorer.score_financial_data(stock)
                label, icon, desc = DataQualityScorer.get_quality_label(score)
                stock['quality_score'] = score
                stock['quality_label'] = label
                stock['quality_icon'] = icon
        
        # 总体质量
        if result.get('stocks'):
            total_scores = [s.get('quality_score', 50) for s in result['stocks']]
            avg_score = sum(total_scores) / len(total_scores)
            label, icon, desc = DataQualityScorer.get_quality_label(avg_score)
            result['data_quality'] = {
                'avg_score': avg_score,
                'label': label,
                'icon': icon,
                'desc': desc,
            }
        
        return result


# 全局实例
_screener_data_manager = None


def get_screener_data_manager() -> ScreenerDataSourceManager:
    """获取全局数据源管理器"""
    global _screener_data_manager
    if _screener_data_manager is None:
        _screener_data_manager = ScreenerDataSourceManager()
    return _screener_data_manager


if __name__ == '__main__':
    print("=" * 60)
    print("选股器数据源集成模块测试")
    print("=" * 60)
    
    manager = get_screener_data_manager()
    
    # 测试股票池
    pool = manager.get_stock_pool_with_fallback('hs300')
    print(f"\n股票池 (hs300): {len(pool)} 只")
    
    # 测试财务数据
    data = manager.get_financial_data_with_fallback('600519')
    print(f"\n财务数据 (600519):")
    print(f"  PE: {data.get('pe')}")
    print(f"  ROE: {data.get('roe')}")
    print(f"  数据质量: {data.get('data_quality')}")
    
    # 打印健康报告
    manager.print_health_report()
