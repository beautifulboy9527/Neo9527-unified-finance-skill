#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源管理器 v1.0
- 数据源健康检查
- 自动重试机制
- 数据缓存
- 智能切换
"""

import sys
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceHealth:
    """数据源健康状态"""
    
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
        self.failure_count = max(0, self.failure_count - 1)  # 减少失败计数
        
        # 更新平均响应时间
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
        
        # 连续失败3次则标记为不可用
        if self.failure_count >= 3:
            self.is_available = False
            logger.warning(f"数据源 {self.name} 已标记为不可用: {error}")
    
    def get_health_score(self) -> float:
        """获取健康分数 (0-100)"""
        if self.success_count == 0 and self.failure_count == 0:
            return 100  # 新数据源默认满分
        
        total = self.success_count + self.failure_count
        success_rate = self.success_count / total if total > 0 else 0
        
        # 健康分数 = 成功率 * 100
        return success_rate * 100


class DataCache:
    """数据缓存"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # 检查是否过期
        if datetime.now() - entry['timestamp'] > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            return None
        
        return entry['data']
    
    def set(self, key: str, data: Dict):
        """设置缓存数据"""
        # 如果缓存已满，删除最旧的条目
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


class RetryManager:
    """重试管理器"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute_with_retry(self, func, *args, **kwargs):
        """
        带重试的执行函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数执行结果
        
        Raises:
            Exception: 所有重试都失败后抛出最后一个异常
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries - 1:
                    # 指数退避
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"第{attempt + 1}次重试失败，{delay}秒后重试: {e}")
                    time.sleep(delay)
        
        # 所有重试都失败
        logger.error(f"重试{self.max_retries}次后仍失败: {last_error}")
        raise last_error


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.health_checker = {}  # 数据源健康状态
        self.cache = DataCache()
        self.retry_manager = RetryManager()
        
        # 初始化数据源
        self.sources = ['yfinance', 'eastmoney', 'sina']
        for source in self.sources:
            self.health_checker[source] = DataSourceHealth(source)
    
    def get_best_source(self) -> str:
        """获取最佳数据源"""
        # 按健康分数排序
        sorted_sources = sorted(
            self.sources,
            key=lambda s: self.health_checker[s].get_health_score(),
            reverse=True
        )
        
        # 返回最健康的数据源
        for source in sorted_sources:
            if self.health_checker[source].is_available:
                return source
        
        # 如果都不可用，返回第一个（强制尝试）
        return self.sources[0]
    
    def fetch_with_cache(self, key: str, fetch_func, use_cache: bool = True):
        """
        带缓存的数据获取
        
        Args:
            key: 缓存键
            fetch_func: 数据获取函数
            use_cache: 是否使用缓存
        
        Returns:
            数据
        """
        # 尝试从缓存获取
        if use_cache:
            cached_data = self.cache.get(key)
            if cached_data is not None:
                logger.info(f"从缓存获取数据: {key}")
                return cached_data
        
        # 获取数据
        try:
            start_time = time.time()
            data = self.retry_manager.execute_with_retry(fetch_func)
            response_time = time.time() - start_time
            
            # 记录成功
            current_source = self.get_best_source()
            self.health_checker[current_source].record_success(response_time)
            
            # 缓存数据
            if use_cache and data:
                self.cache.set(key, data)
            
            return data
            
        except Exception as e:
            # 记录失败
            current_source = self.get_best_source()
            self.health_checker[current_source].record_failure(str(e))
            
            # 尝试切换数据源
            if self.health_checker[current_source].failure_count >= 2:
                logger.warning(f"数据源 {current_source} 频繁失败，尝试切换")
            
            raise
    
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
                'last_error': health.last_error
            }
        
        return report
    
    def print_health_report(self):
        """打印健康报告"""
        report = self.get_health_report()
        
        print("\n" + "=" * 80)
        print("数据源健康报告")
        print("=" * 80)
        
        for source, info in report.items():
            status = "✅ 可用" if info['available'] else "❌ 不可用"
            print(f"\n{source}:")
            print(f"  状态: {status}")
            print(f"  健康分数: {info['health_score']:.1f}/100")
            print(f"  成功/失败: {info['success_count']}/{info['failure_count']}")
            print(f"  平均响应时间: {info['avg_response_time']}")
            if info['last_error']:
                print(f"  最后错误: {info['last_error']}")
        
        print("\n" + "=" * 80)


# 全局数据源管理器实例
_data_source_manager = None


def get_data_source_manager() -> DataSourceManager:
    """获取全局数据源管理器实例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


if __name__ == '__main__':
    # 测试
    print("=" * 80)
    print("数据源管理器测试")
    print("=" * 80)
    
    manager = get_data_source_manager()
    
    # 模拟健康状态
    manager.health_checker['yfinance'].record_success(0.5)
    manager.health_checker['yfinance'].record_success(0.6)
    manager.health_checker['eastmoney'].record_failure("连接超时")
    manager.health_checker['eastmoney'].record_failure("连接超时")
    
    # 打印健康报告
    manager.print_health_report()
    
    # 测试最佳数据源选择
    best_source = manager.get_best_source()
    print(f"\n最佳数据源: {best_source}")
