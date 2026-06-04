#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险监控清单 - Python实现
用于投资后续跟踪和风险预警
"""

from typing import Dict, List, Optional
from datetime import datetime


class RiskMonitor:
    """风险监控器"""
    
    # 加密货币监控条件
    CRYPTO_CONDITIONS = {
        'strengthen': [
            {
                'id': 'tvl_new_high',
                'name': 'TVL突破历史新高',
                'condition': 'tvl_change_24h > 0 and tvl_is_all_time_high',
                'action': '考虑加仓',
                'severity': 'info'
            },
            {
                'id': 'whale_accumulation',
                'name': '鲸鱼连续7日持仓增加>2%',
                'condition': 'whale_holding_change_7d > 2',
                'action': '强化持有',
                'severity': 'info'
            },
            {
                'id': 'protocol_revenue_high',
                'name': '协议收入创月度新高',
                'condition': 'protocol_revenue_is_monthly_high',
                'action': '看好生态',
                'severity': 'info'
            },
            {
                'id': 'dev_activity_increase',
                'name': '开发活跃度提升',
                'condition': 'dev_commits_change_7d > 50',
                'action': '项目持续迭代',
                'severity': 'info'
            },
        ],
        'warning': [
            {
                'id': 'tvl_drop',
                'name': 'TVL单日下降>10%',
                'condition': 'tvl_change_24h < -10',
                'action': '密切关注',
                'severity': 'warning'
            },
            {
                'id': 'whale_distribution',
                'name': '鲸鱼连续3日持仓减少',
                'condition': 'whale_holding_change_3d < -1',
                'action': '准备减仓',
                'severity': 'warning'
            },
            {
                'id': 'token_unlock',
                'name': '代币大规模解锁(>5%流通量)',
                'condition': 'token_unlock_pct > 5',
                'action': '注意抛压',
                'severity': 'warning'
            },
            {
                'id': 'dev_stagnation',
                'name': '开发停滞(2周无提交)',
                'condition': 'dev_commits_14d == 0',
                'action': '关注项目状态',
                'severity': 'warning'
            },
        ],
        'exit': [
            {
                'id': 'support_break',
                'name': '跌破关键支撑位>15%',
                'condition': 'price_drop_from_support < -15',
                'action': '立即止损',
                'severity': 'critical'
            },
            {
                'id': 'hack_event',
                'name': '协议被黑客攻击',
                'condition': 'security_incident == True',
                'action': '立即退出',
                'severity': 'critical'
            },
            {
                'id': 'team_issue',
                'name': '核心团队离职/争议',
                'condition': 'team_issue == True',
                'action': '立即退出',
                'severity': 'critical'
            },
            {
                'id': 'regulatory_action',
                'name': '监管重大利空',
                'condition': 'regulatory_action == True',
                'action': '立即退出',
                'severity': 'critical'
            },
        ]
    }
    
    # 股票监控条件
    STOCK_CONDITIONS = {
        'strengthen': [
            {
                'id': 'earnings_beat',
                'name': '业绩超预期>10%',
                'condition': 'earnings_surprise > 10',
                'action': '考虑加仓',
                'severity': 'info'
            },
            {
                'id': 'institution_buy',
                'name': '机构持仓增加>5%',
                'condition': 'institution_holding_change > 5',
                'action': '强化持有',
                'severity': 'info'
            },
        ],
        'warning': [
            {
                'id': 'earnings_miss',
                'name': '业绩不及预期>10%',
                'condition': 'earnings_surprise < -10',
                'action': '密切关注',
                'severity': 'warning'
            },
            {
                'id': 'cashflow_worsen',
                'name': '经营现金流/净利润<0.5',
                'condition': 'ocf_to_ni < 0.5',
                'action': '关注盈利质量',
                'severity': 'warning'
            },
        ],
        'exit': [
            {
                'id': 'fraud_risk',
                'name': '财务造假风险',
                'condition': 'audit_opinion == "adverse"',
                'action': '立即退出',
                'severity': 'critical'
            },
            {
                'id': 'continuous_loss',
                'name': '连续2年亏损',
                'condition': 'consecutive_loss_years >= 2',
                'action': '立即退出',
                'severity': 'critical'
            },
        ]
    }
    
    def __init__(self, asset_type: str = 'crypto'):
        """
        初始化监控器
        
        Args:
            asset_type: 资产类型 ('crypto' 或 'stock')
        """
        self.asset_type = asset_type
        self.conditions = (
            self.CRYPTO_CONDITIONS if asset_type == 'crypto' 
            else self.STOCK_CONDITIONS
        )
    
    def check(self, data: Dict) -> Dict:
        """
        检查监控条件
        
        Args:
            data: 监控数据字典
            
        Returns:
            {
                'strengthens': [...],  # 触发的强化条件
                'alerts': [...],       # 触发的预警条件
                'exits': [...],        # 触发的退出条件
                'recommendation': str  # 建议行动
            }
        """
        results = {
            'strengthens': [],
            'alerts': [],
            'exits': [],
            'recommendation': 'hold'
        }
        
        # 检查强化条件
        for cond in self.conditions['strengthen']:
            if self._evaluate_condition(cond['condition'], data):
                results['strengthens'].append({
                    'id': cond['id'],
                    'name': cond['name'],
                    'action': cond['action'],
                    'severity': cond['severity']
                })
        
        # 检查预警条件
        for cond in self.conditions['warning']:
            if self._evaluate_condition(cond['condition'], data):
                results['alerts'].append({
                    'id': cond['id'],
                    'name': cond['name'],
                    'action': cond['action'],
                    'severity': cond['severity']
                })
        
        # 检查退出条件
        for cond in self.conditions['exit']:
            if self._evaluate_condition(cond['condition'], data):
                results['exits'].append({
                    'id': cond['id'],
                    'name': cond['name'],
                    'action': cond['action'],
                    'severity': cond['severity']
                })
        
        # 确定建议
        if results['exits']:
            results['recommendation'] = 'exit'
        elif results['alerts']:
            results['recommendation'] = 'monitor'
        elif results['strengthens']:
            results['recommendation'] = 'strengthen'
        
        return results
    
    def _evaluate_condition(self, condition: str, data: Dict) -> bool:
        """
        评估条件
        
        Args:
            condition: 条件表达式字符串
            data: 数据字典
            
        Returns:
            条件是否满足
        """
        try:
            # 简单的条件解析
            # 支持: var > value, var < value, var == value
            condition = condition.strip()
            
            # 处理布尔值
            if ' == True' in condition:
                var = condition.split(' == True')[0].strip()
                return data.get(var, False) == True
            
            if ' == False' in condition:
                var = condition.split(' == False')[0].strip()
                return data.get(var, True) == False
            
            if ' == "' in condition:
                var, val = condition.split(' == "')
                val = val.strip('"')
                return str(data.get(var, '')) == val
            
            # 处理数值比较
            for op in [' > ', ' < ', ' >= ', ' <= ', ' == ']:
                if op in condition:
                    parts = condition.split(op)
                    var = parts[0].strip()
                    val = float(parts[1].strip())
                    actual = float(data.get(var, 0))
                    
                    if op == ' > ':
                        return actual > val
                    elif op == ' < ':
                        return actual < val
                    elif op == ' >= ':
                        return actual >= val
                    elif op == ' <= ':
                        return actual <= val
                    elif op == ' == ':
                        return actual == val
            
            return False
            
        except Exception:
            return False
    
    def generate_checklist(self, symbol: str = '') -> str:
        """
        生成监控清单 (Markdown格式)
        
        Args:
            symbol: 资产符号
            
        Returns:
            Markdown格式的监控清单
        """
        checklist = f"""## 📊 监控清单

**资产**: {symbol if symbol else '待填写'}  
**日期**: {datetime.now().strftime('%Y-%m-%d')}

### ✅ 强化条件

"""
        for cond in self.conditions['strengthen']:
            checklist += f"- [ ] {cond['name']} → {cond['action']}\n"
        
        checklist += "\n### ⚠️ 预警条件\n\n"
        for cond in self.conditions['warning']:
            checklist += f"- [ ] {cond['name']} → {cond['action']}\n"
        
        checklist += "\n### 🛑 退出触发\n\n"
        for cond in self.conditions['exit']:
            checklist += f"- [ ] {cond['name']} → {cond['action']}\n"
        
        checklist += """
---

**使用说明**:
- 定期检查以上条件
- 出现预警条件时提高警惕
- 出现退出触发时立即行动
"""
        
        return checklist
    
    def generate_checklist_html(self, symbol: str = '') -> str:
        """
        生成监控清单 (HTML格式)
        
        Args:
            symbol: 资产符号
            
        Returns:
            HTML格式的监控清单
        """
        html = f'''
<div class="monitoring-checklist" style="background: #1a1a1a; border-radius: 12px; padding: 20px; margin: 16px 0;">
    <h3 style="color: #fff; margin-bottom: 16px;">📊 监控清单</h3>
    
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #333;">
        <span style="color: #9ca3af;">资产: <span style="color: #fff;">{symbol if symbol else '待填写'}</span></span>
        <span style="color: #9ca3af;">日期: {datetime.now().strftime('%Y-%m-%d')}</span>
    </div>
    
    <div class="strengthen-section" style="margin-bottom: 20px;">
        <h4 style="color: #10b981; margin-bottom: 12px;">✅ 强化条件</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
'''
        for cond in self.conditions['strengthen']:
            html += f'''
            <li style="padding: 8px 12px; margin: 4px 0; background: rgba(16, 185, 129, 0.1); border-radius: 6px; border-left: 3px solid #10b981;">
                <span style="color: #fff;">{cond['name']}</span>
                <span style="color: #6b7280; margin-left: 8px;">→ {cond['action']}</span>
            </li>
'''
        
        html += '''
        </ul>
    </div>
    
    <div class="warning-section" style="margin-bottom: 20px;">
        <h4 style="color: #f59e0b; margin-bottom: 12px;">⚠️ 预警条件</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
'''
        for cond in self.conditions['warning']:
            html += f'''
            <li style="padding: 8px 12px; margin: 4px 0; background: rgba(245, 158, 11, 0.1); border-radius: 6px; border-left: 3px solid #f59e0b;">
                <span style="color: #fff;">{cond['name']}</span>
                <span style="color: #6b7280; margin-left: 8px;">→ {cond['action']}</span>
            </li>
'''
        
        html += '''
        </ul>
    </div>
    
    <div class="exit-section">
        <h4 style="color: #ef4444; margin-bottom: 12px;">🛑 退出触发</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
'''
        for cond in self.conditions['exit']:
            html += f'''
            <li style="padding: 8px 12px; margin: 4px 0; background: rgba(239, 68, 68, 0.1); border-radius: 6px; border-left: 3px solid #ef4444;">
                <span style="color: #fff;">{cond['name']}</span>
                <span style="color: #6b7280; margin-left: 8px;">→ {cond['action']}</span>
            </li>
'''
        
        html += '''
        </ul>
    </div>
</div>
'''
        
        return html


# 便捷函数
def check_crypto(data: Dict) -> Dict:
    """快速检查加密货币监控条件"""
    monitor = RiskMonitor(asset_type='crypto')
    return monitor.check(data)


def check_stock(data: Dict) -> Dict:
    """快速检查股票监控条件"""
    monitor = RiskMonitor(asset_type='stock')
    return monitor.check(data)


# 测试
if __name__ == '__main__':
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    monitor = RiskMonitor(asset_type='crypto')
    
    print("=" * 60)
    print("风险监控清单测试")
    print("=" * 60)
    
    # 测试检查
    test_data = {
        'tvl_change_24h': -12,
        'whale_holding_change_7d': 3.5,
        'price_drop_from_support': -5,
        'security_incident': False
    }
    
    print("\n测试数据:")
    print(f"  TVL 24h变化: {test_data['tvl_change_24h']}%")
    print(f"  鲸鱼7日持仓变化: {test_data['whale_holding_change_7d']}%")
    print(f"  距离支撑位: {test_data['price_drop_from_support']}%")
    
    results = monitor.check(test_data)
    
    print("\n检查结果:")
    if results['strengthens']:
        print("  ✅ 强化条件:")
        for s in results['strengthens']:
            print(f"     - {s['name']} → {s['action']}")
    
    if results['alerts']:
        print("  ⚠️ 预警条件:")
        for a in results['alerts']:
            print(f"     - {a['name']} → {a['action']}")
    
    if results['exits']:
        print("  🛑 退出触发:")
        for e in results['exits']:
            print(f"     - {e['name']} → {e['action']}")
    
    print(f"\n建议: {results['recommendation']}")
    
    # 测试清单生成
    print("\n" + "=" * 60)
    print("监控清单 (Markdown)")
    print("=" * 60)
    print(monitor.generate_checklist('ETH'))
