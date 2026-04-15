#!/usr/bin/env python3
"""
Data Quality Monitor - 数据质量监控
检测异常数据并告警
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class DataQualityMonitor:
    """数据质量监控器"""
    
    def __init__(self):
        self.alerts: List[Dict] = []
        self.history: Dict[str, List[Dict]] = {}
        self.max_history = 100  # 每个股票最多保留 100 条历史记录
    
    def _add_alert(self, symbol: str, alert_type: str, message: str, severity: str = 'warning'):
        """添加告警"""
        alert = {
            'symbol': symbol,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.alerts.append(alert)
        print(f"[{severity.upper()}] {symbol}: {message}")
    
    def validate_price(self, symbol: str, price: float, prev_price: Optional[float] = None) -> bool:
        """
        验证价格数据
        
        检查项:
        - 价格是否为正数
        - 价格是否异常波动 (> 20%)
        - 价格是否超出合理范围
        """
        valid = True
        
        # 检查价格是否为正
        if price <= 0:
            self._add_alert(symbol, 'invalid_price', f'价格无效：{price}', 'error')
            valid = False
        
        # 检查价格波动
        if prev_price and prev_price > 0:
            change_pct = abs(price - prev_price) / prev_price * 100
            if change_pct > 20:
                self._add_alert(symbol, 'price_spike', 
                               f'价格异常波动：{change_pct:.1f}%', 'warning')
        
        return valid
    
    def validate_volume(self, symbol: str, volume: int, avg_volume: Optional[int] = None) -> bool:
        """
        验证成交量数据
        
        检查项:
        - 成交量是否为非负数
        - 成交量是否异常 (> 10 倍平均)
        """
        valid = True
        
        # 检查成交量是否为非负
        if volume < 0:
            self._add_alert(symbol, 'invalid_volume', f'成交量无效：{volume}', 'error')
            valid = False
        
        # 检查成交量异常
        if avg_volume and avg_volume > 0:
            ratio = volume / avg_volume
            if ratio > 10:
                self._add_alert(symbol, 'volume_spike', 
                               f'成交量异常：{ratio:.1f}x 平均', 'warning')
            elif ratio < 0.1 and avg_volume > 1000000:
                self._add_alert(symbol, 'volume_low', 
                               f'成交量过低：{ratio:.2f}x 平均', 'info')
        
        return valid
    
    def validate_timestamp(self, symbol: str, timestamp: str, max_age_hours: int = 24) -> bool:
        """
        验证时间戳
        
        检查项:
        - 时间戳格式是否正确
        - 数据是否过期
        """
        try:
            ts = datetime.fromisoformat(timestamp)
            age = datetime.now() - ts
            age_hours = age.total_seconds() / 3600
            
            if age_hours > max_age_hours:
                self._add_alert(symbol, 'stale_data', 
                               f'数据过期：{age_hours:.1f}小时前', 'warning')
                return False
            
            return True
        except Exception as e:
            self._add_alert(symbol, 'invalid_timestamp', f'时间戳格式错误：{e}', 'error')
            return False
    
    def validate_completeness(self, symbol: str, data: Dict, required_fields: List[str]) -> bool:
        """
        验证数据完整性
        
        检查项:
        - 必填字段是否存在
        - 字段值是否为 None
        """
        missing = []
        null_fields = []
        
        for field in required_fields:
            if field not in data:
                missing.append(field)
            elif data[field] is None:
                null_fields.append(field)
        
        if missing:
            self._add_alert(symbol, 'missing_fields', 
                           f'缺少字段：{", ".join(missing)}', 'error')
            return False
        
        if null_fields:
            self._add_alert(symbol, 'null_fields', 
                           f'空值字段：{", ".join(null_fields)}', 'info')
        
        return True
    
    def cross_validate(self, symbol: str, source1_data: Dict, source2_data: Dict) -> Dict:
        """
        跨数据源验证
        
        比较两个数据源的数据差异
        
        Returns:
            差异分析报告
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'valid': True,
            'issues': []
        }
        
        # 价格对比
        price1 = source1_data.get('price')
        price2 = source2_data.get('price')
        
        if price1 and price2:
            diff = abs(price1 - price2)
            diff_pct = (diff / price1 * 100) if price1 else 0
            
            if diff_pct > 1:  # 差异超过 1%
                result['valid'] = False
                result['issues'].append({
                    'type': 'price_mismatch',
                    'message': f'价格差异：{diff_pct:.2f}%',
                    'source1': price1,
                    'source2': price2
                })
                self._add_alert(symbol, 'price_mismatch', 
                               f'数据源价格差异：{diff_pct:.2f}%', 'warning')
        
        # 涨跌幅对比
        change1 = source1_data.get('change_percent')
        change2 = source2_data.get('change_percent')
        
        if change1 is not None and change2 is not None:
            diff = abs(change1 - change2)
            if diff > 1:  # 差异超过 1%
                result['issues'].append({
                    'type': 'change_mismatch',
                    'message': f'涨跌幅差异：{diff:.2f}%',
                    'source1': change1,
                    'source2': change2
                })
        
        return result
    
    def record_history(self, symbol: str, data: Dict):
        """记录数据历史"""
        if symbol not in self.history:
            self.history[symbol] = []
        
        self.history[symbol].append({
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        # 限制历史记录数量
        if len(self.history[symbol]) > self.max_history:
            self.history[symbol] = self.history[symbol][-self.max_history:]
    
    def get_alerts(self, symbol: Optional[str] = None, 
                   severity: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """
        获取告警列表
        
        Args:
            symbol: 过滤特定股票
            severity: 过滤严重级别 (error/warning/info)
            limit: 返回数量限制
        """
        filtered = self.alerts
        
        if symbol:
            filtered = [a for a in filtered if a['symbol'] == symbol]
        if severity:
            filtered = [a for a in filtered if a['severity'] == severity]
        
        return filtered[-limit:]
    
    def clear_alerts(self, symbol: Optional[str] = None):
        """清空告警"""
        if symbol:
            self.alerts = [a for a in self.alerts if a['symbol'] != symbol]
        else:
            self.alerts = []
    
    def get_report(self, symbol: Optional[str] = None) -> Dict:
        """
        生成数据质量报告
        
        Returns:
            质量报告字典
        """
        alerts = self.get_alerts(symbol) if symbol else self.alerts
        
        error_count = len([a for a in alerts if a['severity'] == 'error'])
        warning_count = len([a for a in alerts if a['severity'] == 'warning'])
        info_count = len([a for a in alerts if a['severity'] == 'info'])
        
        # 计算质量分数 (100 分制)
        score = 100
        score -= error_count * 20
        score -= warning_count * 5
        score -= info_count * 1
        score = max(0, score)
        
        return {
            'symbol': symbol or 'all',
            'timestamp': datetime.now().isoformat(),
            'quality_score': score,
            'rating': 'excellent' if score >= 90 else 'good' if score >= 70 else 'fair' if score >= 50 else 'poor',
            'alerts': {
                'total': len(alerts),
                'error': error_count,
                'warning': warning_count,
                'info': info_count
            },
            'recent_alerts': alerts[-10:]
        }


# 全局监控实例
quality_monitor = DataQualityMonitor()


if __name__ == '__main__':
    # 测试数据质量监控
    monitor = DataQualityMonitor()
    
    print("测试数据质量监控")
    print("=" * 60)
    
    # 测试价格验证
    print("\n1. 价格验证测试")
    monitor.validate_price('AAPL', 150.0)  # 正常
    monitor.validate_price('AAPL', -10.0)  # 异常
    monitor.validate_price('AAPL', 200.0, 150.0)  # 波动过大
    
    # 测试成交量验证
    print("\n2. 成交量验证测试")
    monitor.validate_volume('AAPL', 1000000, 50000000)  # 过低
    monitor.validate_volume('AAPL', 600000000, 50000000)  # 过高
    
    # 测试时间戳验证
    print("\n3. 时间戳验证测试")
    monitor.validate_timestamp('AAPL', datetime.now().isoformat())  # 正常
    monitor.validate_timestamp('AAPL', 
                              (datetime.now() - timedelta(hours=48)).isoformat())  # 过期
    
    # 测试完整性验证
    print("\n4. 完整性验证测试")
    monitor.validate_completeness('AAPL', 
                                  {'price': 150, 'volume': 1000},
                                  ['price', 'volume', 'market_cap'])  # 缺少字段
    
    # 跨数据源验证
    print("\n5. 跨数据源验证测试")
    source1 = {'price': 150.0, 'change_percent': 2.5}
    source2 = {'price': 152.0, 'change_percent': 3.0}
    result = monitor.cross_validate('AAPL', source1, source2)
    print(json.dumps(result, indent=2))
    
    # 获取告警
    print("\n6. 告警列表")
    alerts = monitor.get_alerts(limit=5)
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['symbol']}: {alert['message']}")
    
    # 质量报告
    print("\n7. 质量报告")
    report = monitor.get_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
