#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存层 - 提升数据获取和分析速度
支持 diskcache 和 joblib，自动缓存结果
"""

import sys
import os
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable
from functools import wraps

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CacheLayer:
    """
    缓存层
    
    功能:
    - 数据缓存 (行情、财务、回测结果)
    - TTL 支持 (自动过期)
    - 缓存统计 (命中率、大小)
    - 自动清理 (防止无限膨胀)
    """
    
    def __init__(
        self,
        cache_dir: str = "D:\\OpenClaw\\cache",
        default_ttl: int = 3600,  # 默认1小时过期
        max_size: int = 1000,  # 最大缓存条目数
        auto_cleanup: bool = True  # 自动清理过期缓存
    ):
        """
        初始化
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间(秒)
            max_size: 最大缓存条目数
            auto_cleanup: 是否自动清理过期缓存
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.auto_cleanup = auto_cleanup
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0  # 清理次数
        }
        
        os.makedirs(cache_dir, exist_ok=True)
        
        # 尝试使用 diskcache
        self._use_diskcache = False
        try:
            from diskcache import Cache
            self.cache = Cache(cache_dir)
            self._use_diskcache = True
            print("✅ 使用 diskcache 加速")
            
            # 设置 diskcache 大小限制 (默认 1GB)
            self.cache.size_limit = 1024 * 1024 * 1024  # 1GB
            
        except ImportError:
            # 回退到内存缓存
            self.cache = {}
            print("⚠️ diskcache 未安装，使用内存缓存 (pip install diskcache)")
        
        # 启动时清理过期缓存
        if auto_cleanup:
            self._cleanup_expired()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            if self._use_diskcache:
                value = self.cache.get(key)
                if value is not None:
                    data, expire_time = value
                    if datetime.now() < expire_time:
                        self.stats['hits'] += 1
                        return data
                    else:
                        # 过期，删除
                        self.cache.delete(key)
            else:
                if key in self.cache:
                    data, expire_time = self.cache[key]
                    if datetime.now() < expire_time:
                        self.stats['hits'] += 1
                        return data
                    else:
                        del self.cache[key]
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.stats['misses'] += 1
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """设置缓存"""
        ttl = ttl or self.default_ttl
        expire_time = datetime.now() + timedelta(seconds=ttl)
        
        try:
            if self._use_diskcache:
                self.cache.set(key, (value, expire_time))
            else:
                self.cache[key] = (value, expire_time)
            
            self.stats['sets'] += 1
            
            # 自动清理过期缓存
            if self.auto_cleanup and self.stats['sets'] % 100 == 0:
                self._cleanup_expired()
            
            # 强制执行大小限制
            self._enforce_size_limit()
            
        except Exception as e:
            print(f"⚠️ 缓存设置失败: {e}")
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        try:
            if self._use_diskcache:
                self.cache.delete(key)
            else:
                if key in self.cache:
                    del self.cache[key]
        except:
            pass
    
    def clear(self) -> None:
        """清空缓存"""
        try:
            if self._use_diskcache:
                self.cache.clear()
            else:
                self.cache.clear()
            
            self.stats = {'hits': 0, 'misses': 0, 'sets': 0, 'evictions': 0}
            
        except Exception as e:
            print(f"⚠️ 清空缓存失败: {e}")
    
    def _cleanup_expired(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的条目数
        """
        cleaned = 0
        now = datetime.now()
        
        try:
            if self._use_diskcache:
                # diskcache 自动过期，但我们也手动检查
                for key in list(self.cache):
                    try:
                        value = self.cache.get(key)
                        if value and isinstance(value, tuple) and len(value) == 2:
                            _, expire_time = value
                            if now > expire_time:
                                self.cache.delete(key)
                                cleaned += 1
                    except:
                        pass
            else:
                # 内存缓存
                keys_to_delete = []
                for key, (value, expire_time) in self.cache.items():
                    if now > expire_time:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.cache[key]
                    cleaned += 1
            
            self.stats['evictions'] += cleaned
            if cleaned > 0:
                print(f"🧹 清理过期缓存: {cleaned} 条")
            
        except Exception as e:
            print(f"⚠️ 清理缓存失败: {e}")
        
        return cleaned
    
    def _enforce_size_limit(self) -> None:
        """
        强制执行缓存大小限制
        超过 max_size 时，删除最旧的缓存
        """
        try:
            if self._use_diskcache:
                # diskcache 自动管理大小
                pass
            else:
                # 内存缓存
                if len(self.cache) > self.max_size:
                    # 按过期时间排序，删除最旧的
                    items = [(k, v[1]) for k, v in self.cache.items()]
                    items.sort(key=lambda x: x[1])
                    
                    # 删除最旧的 10%
                    to_delete = int(self.max_size * 0.1)
                    for key, _ in items[:to_delete]:
                        del self.cache[key]
                        self.stats['evictions'] += 1
                    
                    print(f"🧹 缓存超限，清理: {to_delete} 条")
        
        except Exception as e:
            print(f"⚠️ 强制清理失败: {e}")
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0
        
        # 获取缓存大小
        cache_size = 0
        try:
            if self._use_diskcache:
                cache_size = len(self.cache)
            else:
                cache_size = len(self.cache)
        except:
            pass
        
        return {
            **self.stats,
            'total_requests': total,
            'hit_rate': hit_rate,
            'cache_type': 'diskcache' if self._use_diskcache else 'memory',
            'cache_size': cache_size,
            'max_size': self.max_size,
            'usage_pct': (cache_size / self.max_size * 100) if self.max_size > 0 else 0
        }


# 全局缓存实例
_cache_layer = None


def get_cache() -> CacheLayer:
    """获取全局缓存实例"""
    global _cache_layer
    if _cache_layer is None:
        _cache_layer = CacheLayer()
    return _cache_layer


def cached(
    ttl: int = 3600,
    key_prefix: str = ""
):
    """
    缓存装饰器
    
    Args:
        ttl: 过期时间(秒)
        key_prefix: 键前缀
        
    Returns:
        装饰器
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}_{func.__name__}_{get_cache()._generate_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_value = get_cache().get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 计算并缓存
            result = func(*args, **kwargs)
            get_cache().set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# ============================================
# 预定义缓存装饰器
# ============================================

# 行情数据缓存 (5分钟)
def cache_quote(func: Callable) -> Callable:
    """行情数据缓存装饰器"""
    return cached(ttl=300, key_prefix="quote")(func)


# 财务数据缓存 (1天)
def cache_financial(func: Callable) -> Callable:
    """财务数据缓存装饰器"""
    return cached(ttl=86400, key_prefix="financial")(func)


# 回测结果缓存 (1小时)
def cache_backtest(func: Callable) -> Callable:
    """回测结果缓存装饰器"""
    return cached(ttl=3600, key_prefix="backtest")(func)


# 组合分析缓存 (1小时)
def cache_portfolio(func: Callable) -> Callable:
    """组合分析缓存装饰器"""
    return cached(ttl=3600, key_prefix="portfolio")(func)


# ============================================
# 便捷函数
# ============================================

def clear_cache():
    """清空所有缓存"""
    get_cache().clear()


def get_cache_stats():
    """获取缓存统计"""
    return get_cache().get_stats()


if __name__ == '__main__':
    # 测试缓存
    print("=" * 60)
    print("缓存层测试")
    print("=" * 60)
    
    # 测试装饰器
    @cached(ttl=60, key_prefix="test")
    def expensive_function(n):
        print(f"  计算 {n}...")
        import time
        time.sleep(1)
        return n * n
    
    print("\n第一次调用 (应该计算):")
    result1 = expensive_function(5)
    print(f"结果: {result1}")
    
    print("\n第二次调用 (应该缓存):")
    result2 = expensive_function(5)
    print(f"结果: {result2}")
    
    # 缓存统计
    stats = get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  命中: {stats['hits']}")
    print(f"  未命中: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']*100:.1f}%")
    print(f"  缓存类型: {stats['cache_type']}")
