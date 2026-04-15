#!/usr/bin/env python3
"""
Cache Manager - 缓存管理
支持内存缓存 + 文件缓存
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Optional, Any, Dict

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'cache'
)

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, ttl: int = 300, use_file_cache: bool = True):
        """
        Args:
            ttl: 缓存有效期 (秒)，默认 5 分钟
            use_file_cache: 是否使用文件缓存
        """
        self.ttl = ttl
        self.use_file_cache = use_file_cache
        self.memory_cache: Dict[str, Dict] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'writes': 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_str = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_file_path(self, key: str) -> str:
        """获取文件缓存路径"""
        return os.path.join(CACHE_DIR, f"{key}.json")
    
    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            prefix: 缓存前缀 (用于分类)
            *args, **kwargs: 用于生成缓存键
        
        Returns:
            缓存数据，如果不存在或过期则返回 None
        """
        key = self._generate_key(prefix, *args, **kwargs)
        
        # 先尝试内存缓存
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry['time'] < self.ttl:
                self.stats['hits'] += 1
                return entry['data']
            else:
                # 过期，删除
                del self.memory_cache[key]
        
        # 尝试文件缓存
        if self.use_file_cache:
            file_path = self._get_file_path(key)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    
                    if time.time() - entry['time'] < self.ttl:
                        # 加载到内存缓存
                        self.memory_cache[key] = entry
                        self.stats['hits'] += 1
                        return entry['data']
                    else:
                        # 过期，删除文件
                        os.remove(file_path)
                except:
                    pass
        
        self.stats['misses'] += 1
        return None
    
    def set(self, prefix: str, data: Any, *args, **kwargs):
        """
        设置缓存数据
        
        Args:
            prefix: 缓存前缀
            data: 缓存数据
            *args, **kwargs: 用于生成缓存键
        """
        key = self._generate_key(prefix, *args, **kwargs)
        entry = {
            'data': data,
            'time': time.time(),
            'created_at': datetime.now().isoformat()
        }
        
        # 写入内存缓存
        self.memory_cache[key] = entry
        self.stats['writes'] += 1
        
        # 写入文件缓存
        if self.use_file_cache:
            try:
                file_path = self._get_file_path(key)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"文件缓存写入失败：{e}")
    
    def delete(self, prefix: str, *args, **kwargs):
        """删除缓存"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        # 删除内存缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 删除文件缓存
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def clear(self, prefix: Optional[str] = None):
        """
        清空缓存
        
        Args:
            prefix: 如果指定，只清空该前缀的缓存
        """
        if prefix:
            # 清空指定前缀
            keys_to_delete = [k for k in self.memory_cache.keys() 
                            if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.memory_cache[key]
            
            # 清空文件缓存
            if os.path.exists(CACHE_DIR):
                for filename in os.listdir(CACHE_DIR):
                    if filename.startswith(prefix):
                        os.remove(os.path.join(CACHE_DIR, filename))
        else:
            # 清空所有
            self.memory_cache.clear()
            if os.path.exists(CACHE_DIR):
                for filename in os.listdir(CACHE_DIR):
                    os.remove(os.path.join(CACHE_DIR, filename))
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total,
            'hit_rate': f"{hit_rate:.1f}%",
            'memory_cache_size': len(self.memory_cache),
            'file_cache_size': len(os.listdir(CACHE_DIR)) if os.path.exists(CACHE_DIR) else 0
        }
    
    def cleanup_expired(self):
        """清理过期缓存"""
        # 清理内存缓存
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if time.time() - v['time'] >= self.ttl
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # 清理文件缓存
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                file_path = os.path.join(CACHE_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                    if time.time() - entry['time'] >= self.ttl:
                        os.remove(file_path)
                except:
                    pass


# 全局缓存实例
quote_cache = CacheManager(ttl=300)  # 行情缓存 5 分钟
historical_cache = CacheManager(ttl=600)  # 历史数据缓存 10 分钟
chart_cache = CacheManager(ttl=1800)  # 图表缓存 30 分钟


if __name__ == '__main__':
    # 测试缓存
    cache = CacheManager(ttl=10)  # 10 秒过期用于测试
    
    print("测试缓存功能")
    print("=" * 60)
    
    # 设置缓存
    print("\n1. 设置缓存")
    cache.set('test', {'price': 100}, 'AAPL')
    print("已缓存 AAPL 价格")
    
    # 获取缓存
    print("\n2. 获取缓存")
    data = cache.get('test', 'AAPL')
    print(f"从缓存获取：{data}")
    
    # 获取统计
    print("\n3. 缓存统计")
    stats = cache.get_stats()
    print(json.dumps(stats, indent=2))
    
    # 等待过期
    print("\n4. 等待 10 秒让缓存过期...")
    import time
    time.sleep(11)
    
    # 再次获取 (应该过期)
    print("\n5. 再次获取 (应过期)")
    data = cache.get('test', 'AAPL')
    print(f"缓存数据：{data} (None 表示已过期)")
    
    # 最终统计
    print("\n6. 最终统计")
    stats = cache.get_stats()
    print(json.dumps(stats, indent=2))
