#!/usr/bin/env python3
"""
Alert Manager - 集成 stock-monitor 的警报功能
支持目标价、止损价、阈值预警
"""

import json
import os
from datetime import datetime

# 警报配置文件路径
ALERTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'alerts.json'
)

class AlertManager:
    def __init__(self):
        self.alerts_file = ALERTS_FILE
        self._ensure_config_dir()
        self._load_alerts()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.alerts_file)
        os.makedirs(config_dir, exist_ok=True)
    
    def _load_alerts(self):
        """加载警报配置"""
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                self.alerts = json.load(f)
        else:
            self.alerts = {'alerts': [], 'last_check': None}
    
    def _save_alerts(self):
        """保存警报配置"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)
    
    def add(self, symbol, target=None, stop=None):
        """添加警报"""
        alert = {
            'id': len(self.alerts['alerts']) + 1,
            'symbol': symbol.upper(),
            'target': target,
            'stop': stop,
            'created_at': datetime.now().isoformat(),
            'last_triggered': None,
            'enabled': True
        }
        self.alerts['alerts'].append(alert)
        self._save_alerts()
    
    def remove(self, alert_id):
        """移除警报"""
        self.alerts['alerts'] = [a for a in self.alerts['alerts'] if a['id'] != alert_id]
        self._save_alerts()
    
    def list(self):
        """列出所有警报"""
        return self.alerts['alerts']
    
    def check(self):
        """检查是否有触发的警报"""
        import yfinance as yf
        
        triggered = []
        
        for alert in self.alerts['alerts']:
            if not alert['enabled']:
                continue
            
            try:
                ticker = yf.Ticker(alert['symbol'])
                info = ticker.info
                current_price = info.get('regularMarketPrice') or info.get('currentPrice')
                
                if current_price is None:
                    continue
                
                # 检查目标价
                if alert['target'] and current_price >= alert['target']:
                    triggered.append({
                        'symbol': alert['symbol'],
                        'type': 'target',
                        'target': alert['target'],
                        'current': current_price,
                        'message': f"{alert['symbol']} 达到目标价 {alert['target']} (当前：{current_price:.2f})"
                    })
                    alert['last_triggered'] = datetime.now().isoformat()
                
                # 检查止损价
                if alert['stop'] and current_price <= alert['stop']:
                    triggered.append({
                        'symbol': alert['symbol'],
                        'type': 'stop',
                        'stop': alert['stop'],
                        'current': current_price,
                        'message': f"{alert['symbol']} 触及止损价 {alert['stop']} (当前：{current_price:.2f})"
                    })
                    alert['last_triggered'] = datetime.now().isoformat()
                
            except Exception as e:
                print(f"检查 {alert['symbol']} 失败：{e}")
        
        self._save_alerts()
        return triggered

if __name__ == '__main__':
    # 测试
    manager = AlertManager()
    
    print("添加测试警报:")
    manager.add('AAPL', target=200, stop=150)
    manager.add('MSFT', target=500)
    
    print("\n列出警报:")
    for alert in manager.list():
        print(f"  {alert['id']}: {alert['symbol']} - 目标：{alert['target']}, 止损：{alert['stop']}")
    
    print("\n检查警报:")
    triggered = manager.check()
    if triggered:
        for t in triggered:
            print(f"  ⚠ {t['message']}")
    else:
        print("  ✓ 无触发警报")
