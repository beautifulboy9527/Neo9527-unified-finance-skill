#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WatchlistManager - 自选股管理 + 监控告警
整合 alert_manager.py，扩展分组、备注、优先级功能
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 配置文件路径 - 复用现有 alerts.json
WATCHLIST_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'watchlist.json'
)

# 兼容旧路径
ALERTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'alerts.json'
)


class WatchlistManager:
    """
    自选股管理器
    
    功能:
    - 增删改查自选股
    - 目标价/止损价监控
    - 分组管理
    - 备注、优先级
    
    参考: scripts/alert_manager.py
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化
        
        Args:
            config_path: 配置文件路径 (默认 watchlist.json)
        """
        self.config_path = config_path or WATCHLIST_FILE
        self._ensure_config_dir()
        self._load_watchlist()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
    
    def _load_watchlist(self):
        """加载自选股配置"""
        # 尝试新路径
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.watchlist = json.load(f)
        # 兼容旧路径 alerts.json
        elif os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                # 转换旧格式到新格式
                self.watchlist = self._convert_old_format(old_data)
            # 保存到新路径
            self._save_watchlist()
        else:
            self.watchlist = {
                'items': [],
                'groups': ['默认', '科技成长', '价值蓝筹', '周期资源', '消费医药'],
                'last_check': None,
                'version': '2.0'
            }
    
    def _convert_old_format(self, old_data: Dict) -> Dict:
        """转换旧格式 alerts.json 到新格式"""
        items = []
        for alert in old_data.get('alerts', []):
            items.append({
                'id': alert['id'],
                'symbol': alert['symbol'],
                'target': alert.get('target'),
                'stop': alert.get('stop'),
                'notes': '',
                'group': '默认',
                'priority': '中',
                'created_at': alert.get('created_at', datetime.now().isoformat()),
                'last_triggered': alert.get('last_triggered'),
                'enabled': alert.get('enabled', True)
            })
        return {
            'items': items,
            'groups': ['默认', '科技成长', '价值蓝筹', '周期资源', '消费医药'],
            'last_check': old_data.get('last_check'),
            'version': '2.0'
        }
    
    def _save_watchlist(self):
        """保存自选股配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.watchlist, f, ensure_ascii=False, indent=2)
    
    def _next_id(self) -> int:
        """获取下一个ID"""
        if not self.watchlist['items']:
            return 1
        return max(item['id'] for item in self.watchlist['items']) + 1
    
    # ========================================
    # 增删改查
    # ========================================
    
    def add(
        self,
        symbol: str,
        target: Optional[float] = None,
        stop: Optional[float] = None,
        notes: str = '',
        group: str = '默认',
        priority: str = '中'
    ) -> Dict:
        """
        添加自选股
        
        Args:
            symbol: 股票代码
            target: 目标价
            stop: 止损价
            notes: 备注
            group: 分组
            priority: 优先级 (高/中/低)
            
        Returns:
            新增的自选股记录
        """
        # 检查是否已存在
        existing = self.find_by_symbol(symbol)
        if existing:
            return {
                'success': False,
                'message': f'{symbol} 已在自选股中',
                'item': existing
            }
        
        item = {
            'id': self._next_id(),
            'symbol': symbol.upper(),
            'target': target,
            'stop': stop,
            'notes': notes,
            'group': group if group in self.watchlist['groups'] else '默认',
            'priority': priority if priority in ['高', '中', '低'] else '中',
            'created_at': datetime.now().isoformat(),
            'last_triggered': None,
            'enabled': True
        }
        
        self.watchlist['items'].append(item)
        self._save_watchlist()
        
        return {
            'success': True,
            'message': f'{symbol} 已添加到自选股',
            'item': item
        }
    
    def remove(self, item_id: int) -> Dict:
        """
        移除自选股
        
        Args:
            item_id: 自选股ID
            
        Returns:
            操作结果
        """
        original_count = len(self.watchlist['items'])
        self.watchlist['items'] = [
            item for item in self.watchlist['items'] if item['id'] != item_id
        ]
        
        if len(self.watchlist['items']) == original_count:
            return {
                'success': False,
                'message': f'未找到ID {item_id}'
            }
        
        self._save_watchlist()
        return {
            'success': True,
            'message': f'自选股 {item_id} 已移除'
        }
    
    def update(
        self,
        item_id: int,
        target: Optional[float] = None,
        stop: Optional[float] = None,
        notes: Optional[str] = None,
        group: Optional[str] = None,
        priority: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> Dict:
        """
        更新自选股
        
        Args:
            item_id: 自选股ID
            其他参数: 可选更新字段
            
        Returns:
            更新后的记录
        """
        for item in self.watchlist['items']:
            if item['id'] == item_id:
                if target is not None:
                    item['target'] = target
                if stop is not None:
                    item['stop'] = stop
                if notes is not None:
                    item['notes'] = notes
                if group is not None and group in self.watchlist['groups']:
                    item['group'] = group
                if priority is not None and priority in ['高', '中', '低']:
                    item['priority'] = priority
                if enabled is not None:
                    item['enabled'] = enabled
                
                self._save_watchlist()
                return {
                    'success': True,
                    'message': f'自选股 {item_id} 已更新',
                    'item': item
                }
        
        return {
            'success': False,
            'message': f'未找到ID {item_id}'
        }
    
    def list(
        self,
        group: Optional[str] = None,
        priority: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[Dict]:
        """
        列出自选股
        
        Args:
            group: 按分组筛选
            priority: 按优先级筛选
            enabled_only: 只返回启用的
            
        Returns:
            自选股列表
        """
        items = self.watchlist['items']
        
        if enabled_only:
            items = [item for item in items if item['enabled']]
        
        if group:
            items = [item for item in items if item['group'] == group]
        
        if priority:
            items = [item for item in items if item['priority'] == priority]
        
        # 按优先级排序
        priority_order = {'高': 0, '中': 1, '低': 2}
        items.sort(key=lambda x: priority_order.get(x['priority'], 1))
        
        return items
    
    def find_by_symbol(self, symbol: str) -> Optional[Dict]:
        """
        按股票代码查找
        
        Args:
            symbol: 股票代码
            
        Returns:
            自选股记录 (未找到返回 None)
        """
        symbol = symbol.upper()
        for item in self.watchlist['items']:
            if item['symbol'] == symbol:
                return item
        return None
    
    def get(self, item_id: int) -> Optional[Dict]:
        """
        按ID获取
        
        Args:
            item_id: 自选股ID
            
        Returns:
            自选股记录
        """
        for item in self.watchlist['items']:
            if item['id'] == item_id:
                return item
        return None
    
    # ========================================
    # 分组管理
    # ========================================
    
    def add_group(self, group_name: str) -> Dict:
        """
        添加分组
        
        Args:
            group_name: 分组名称
            
        Returns:
            操作结果
        """
        if group_name in self.watchlist['groups']:
            return {
                'success': False,
                'message': f'分组 {group_name} 已存在'
            }
        
        self.watchlist['groups'].append(group_name)
        self._save_watchlist()
        
        return {
            'success': True,
            'message': f'分组 {group_name} 已添加'
        }
    
    def list_groups(self) -> List[str]:
        """
        列出所有分组
        
        Returns:
            分组列表
        """
        return self.watchlist['groups']
    
    def group_stats(self) -> Dict[str, int]:
        """
        分组统计
        
        Returns:
            各分组股票数量
        """
        stats = {}
        for group in self.watchlist['groups']:
            stats[group] = len([
                item for item in self.watchlist['items']
                if item['group'] == group and item['enabled']
            ])
        return stats
    
    # ========================================
    # 监控告警
    # ========================================
    
    def check(self) -> Dict:
        """
        检查触发条件
        
        参考: scripts/alert_manager.py check()
        
        Returns:
            检查结果
        """
        import akshare as ak
        
        triggered = []
        checked_count = 0
        errors = []
        
        for item in self.watchlist['items']:
            if not item['enabled']:
                continue
            
            try:
                current_price = self._get_current_price(item['symbol'])
                
                if current_price is None:
                    errors.append({
                        'symbol': item['symbol'],
                        'error': '无法获取价格'
                    })
                    continue
                
                checked_count += 1
                
                # 检查目标价
                if item['target'] and current_price >= item['target']:
                    triggered.append({
                        'id': item['id'],
                        'symbol': item['symbol'],
                        'type': 'target',
                        'target': item['target'],
                        'current': current_price,
                        'gap_pct': (current_price / item['target'] - 1) * 100,
                        'priority': item['priority'],
                        'message': f"{item['symbol']} 达到目标价 {item['target']} (当前：{current_price:.2f})",
                        'notes': item['notes']
                    })
                    item['last_triggered'] = datetime.now().isoformat()
                
                # 检查止损价
                if item['stop'] and current_price <= item['stop']:
                    triggered.append({
                        'id': item['id'],
                        'symbol': item['symbol'],
                        'type': 'stop',
                        'stop': item['stop'],
                        'current': current_price,
                        'gap_pct': (current_price / item['stop'] - 1) * 100,
                        'priority': item['priority'],
                        'message': f"{item['symbol']} 触及止损价 {item['stop']} (当前：{current_price:.2f})",
                        'notes': item['notes']
                    })
                    item['last_triggered'] = datetime.now().isoformat()
                
            except Exception as e:
                errors.append({
                    'symbol': item['symbol'],
                    'error': str(e)
                })
        
        self.watchlist['last_check'] = datetime.now().isoformat()
        self._save_watchlist()
        
        # 按优先级排序触发结果
        priority_order = {'高': 0, '中': 1, '低': 2}
        triggered.sort(key=lambda x: priority_order.get(x['priority'], 1))
        
        return {
            'success': True,
            'checked_count': checked_count,
            'triggered_count': len(triggered),
            'triggered': triggered,
            'errors': errors,
            'last_check': self.watchlist['last_check']
        }
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """
        获取当前价格
        
        Args:
            symbol: 股票代码
            
        Returns:
            当前价格
        """
        import akshare as ak
        
        try:
            # A股
            if symbol.isdigit() and len(symbol) == 6:
                # 判断市场
                if symbol.startswith('6'):
                    code = f"{symbol}"
                else:
                    code = f"{symbol}"
                
                df = ak.stock_zh_a_spot_em()
                row = df[df['代码'] == code]
                if not row.empty:
                    return float(row['最新价'].values[0])
            
            # 美股/港股 (使用 yfinance)
            else:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get('regularMarketPrice') or info.get('currentPrice')
                if price:
                    return float(price)
            
        except Exception:
            pass
        
        return None
    
    # ========================================
    # 统计报告
    # ========================================
    
    def summary(self) -> Dict:
        """
        自选股统计
        
        Returns:
            统计报告
        """
        items = self.watchlist['items']
        enabled_items = [item for item in items if item['enabled']]
        
        # 优先级分布
        priority_dist = {'高': 0, '中': 0, '低': 0}
        for item in enabled_items:
            priority_dist[item['priority']] = priority_dist.get(item['priority'], 0) + 1
        
        # 分组分布
        group_dist = self.group_stats()
        
        # 监控设置率
        has_target = len([item for item in enabled_items if item['target']])
        has_stop = len([item for item in enabled_items if item['stop']])
        has_both = len([
            item for item in enabled_items 
            if item['target'] and item['stop']
        ])
        
        return {
            'total': len(items),
            'enabled': len(enabled_items),
            'disabled': len(items) - len(enabled_items),
            'priority_distribution': priority_dist,
            'group_distribution': group_dist,
            'monitoring': {
                'has_target': has_target,
                'has_stop': has_stop,
                'has_both': has_both,
                'no_monitoring': len(enabled_items) - max(has_target, has_stop)
            },
            'last_check': self.watchlist['last_check']
        }


# ========================================
# Skill 接口
# ========================================

class WatchlistSkill:
    """
    Watchlist Skill - 适配 Hermes Skill 规范
    """
    
    name = "watchlist"
    description = "自选股管理 + 监控告警"
    version = "1.0.0"
    
    def __init__(self):
        self.manager = WatchlistManager()
    
    def execute(self, action: str, **kwargs) -> Dict:
        """
        执行 Skill
        
        Args:
            action: 操作类型 (add/remove/update/list/check/summary)
            kwargs: 参数
            
        Returns:
            执行结果
        """
        actions = {
            'add': self._add,
            'remove': self._remove,
            'update': self._update,
            'list': self._list,
            'get': self._get,
            'check': self._check,
            'summary': self._summary,
            'add_group': self._add_group,
            'list_groups': self._list_groups
        }
        
        if action not in actions:
            return {
                'success': False,
                'message': f'未知操作: {action}',
                'available_actions': list(actions.keys())
            }
        
        return actions[action](**kwargs)
    
    def _add(self, **kwargs) -> Dict:
        return self.manager.add(
            symbol=kwargs.get('symbol'),
            target=kwargs.get('target'),
            stop=kwargs.get('stop'),
            notes=kwargs.get('notes', ''),
            group=kwargs.get('group', '默认'),
            priority=kwargs.get('priority', '中')
        )
    
    def _remove(self, **kwargs) -> Dict:
        return self.manager.remove(kwargs.get('id'))
    
    def _update(self, **kwargs) -> Dict:
        return self.manager.update(
            item_id=kwargs.get('id'),
            target=kwargs.get('target'),
            stop=kwargs.get('stop'),
            notes=kwargs.get('notes'),
            group=kwargs.get('group'),
            priority=kwargs.get('priority'),
            enabled=kwargs.get('enabled')
        )
    
    def _list(self, **kwargs) -> Dict:
        items = self.manager.list(
            group=kwargs.get('group'),
            priority=kwargs.get('priority'),
            enabled_only=kwargs.get('enabled_only', True)
        )
        return {
            'success': True,
            'count': len(items),
            'items': items
        }
    
    def _get(self, **kwargs) -> Dict:
        item = self.manager.get(kwargs.get('id'))
        if item:
            return {'success': True, 'item': item}
        return {'success': False, 'message': f'未找到ID {kwargs.get("id")}'}
    
    def _check(self, **kwargs) -> Dict:
        return self.manager.check()
    
    def _summary(self, **kwargs) -> Dict:
        return self.manager.summary()
    
    def _add_group(self, **kwargs) -> Dict:
        return self.manager.add_group(kwargs.get('name'))
    
    def _list_groups(self, **kwargs) -> Dict:
        return {
            'success': True,
            'groups': self.manager.list_groups(),
            'stats': self.manager.group_stats()
        }


# CLI 测试入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='自选股管理')
    parser.add_argument('action', choices=[
        'list', 'add', 'remove', 'update', 'check', 'summary', 'groups'
    ])
    parser.add_argument('--symbol', type=str)
    parser.add_argument('--id', type=int)
    parser.add_argument('--target', type=float)
    parser.add_argument('--stop', type=float)
    parser.add_argument('--notes', type=str, default='')
    parser.add_argument('--group', type=str, default='默认')
    parser.add_argument('--priority', type=str, default='中')
    parser.add_argument('--enabled', type=lambda x: x.lower() == 'true', default=True)
    
    args = parser.parse_args()
    
    skill = WatchlistSkill()
    
    if args.action == 'list':
        result = skill.execute('list')
        print(f"\n📊 自选股列表 ({result['count']} 个):")
        for item in result['items']:
            print(f"  [{item['id']}] {item['symbol']} | 目标:{item['target']} 止损:{item['stop']} | {item['group']} | {item['priority']}")
            if item['notes']:
                print(f"      备注: {item['notes']}")
    
    elif args.action == 'add':
        if not args.symbol:
            print("❌ 需要指定 --symbol")
            sys.exit(1)
        result = skill.execute('add', 
            symbol=args.symbol,
            target=args.target,
            stop=args.stop,
            notes=args.notes,
            group=args.group,
            priority=args.priority
        )
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"⚠️ {result['message']}")
    
    elif args.action == 'remove':
        if not args.id:
            print("❌ 需要指定 --id")
            sys.exit(1)
        result = skill.execute('remove', id=args.id)
        print(f"{'✅' if result['success'] else '❌'} {result['message']}")
    
    elif args.action == 'check':
        result = skill.execute('check')
        print(f"\n🔍 检查结果 ({result['checked_count']} 个已检查):")
        if result['triggered']:
            print(f"  ⚠️ 触发警报 ({result['triggered_count']} 个):")
            for t in result['triggered']:
                print(f"    [{t['priority']}] {t['symbol']}: {t['message']}")
        else:
            print("  ✓ 无触发警报")
        if result['errors']:
            print(f"  ❌ 检查失败 ({len(result['errors'])} 个):")
            for e in result['errors']:
                print(f"    {e['symbol']}: {e['error']}")
    
    elif args.action == 'summary':
        result = skill.execute('summary')
        print(f"\n📊 自选股统计:")
        print(f"  总数: {result['total']} | 启用: {result['enabled']} | 禁用: {result['disabled']}")
        print(f"  优先级: 高 {result['priority_distribution']['高']} | 中 {result['priority_distribution']['中']} | 低 {result['priority_distribution']['低']}")
        print(f"  监控设置: 目标价 {result['monitoring']['has_target']} | 止损价 {result['monitoring']['has_stop']} | 双向 {result['monitoring']['has_both']}")
    
    elif args.action == 'groups':
        result = skill.execute('list_groups')
        print(f"\n📁 分组列表:")
        for group in result['groups']:
            count = result['stats'].get(group, 0)
            print(f"  {group}: {count} 个")