#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化回测状态标记。

当前模块不执行真实历史回测，只标记技术规则是否触发。
"""

def simple_backtest_validation(tech_data, symbol):
    """
    简化的回测状态标记。
    
    返回的结果仅代表规则触发，不包含真实胜率或收益统计。
    """
    results = []
    
    # MACD信号历史统计
    if '金叉' in tech_data.get('macd_status', ''):
        results.append({
            'signal': 'MACD金叉',
            'win_rate': None,
            'avg_return': None,
            'sample_size': 0,
            'holding_days': 10,
            'risk_level': '未验证',
            'verified': False,
            'description': 'MACD金叉规则触发；未接入当前标的真实历史回测'
        })
    
    # RSI信号统计
    rsi = tech_data.get('rsi', 50)
    if rsi > 70:
        results.append({
            'signal': 'RSI超买',
            'win_rate': None,
            'avg_return': None,
            'sample_size': 0,
            'holding_days': 5,
            'risk_level': '未验证',
            'verified': False,
            'description': f'RSI={rsi:.1f}超买；未接入当前标的真实历史回测'
        })
    elif rsi < 30:
        results.append({
            'signal': 'RSI超卖',
            'win_rate': None,
            'avg_return': None,
            'sample_size': 0,
            'holding_days': 10,
            'risk_level': '未验证',
            'verified': False,
            'description': f'RSI={rsi:.1f}超卖；未接入当前标的真实历史回测'
        })
    
    # 趋势信号
    trend = tech_data.get('trend', '')
    if '多头' in trend:
        results.append({
            'signal': '强势多头',
            'win_rate': None,
            'avg_return': None,
            'sample_size': 0,
            'holding_days': 20,
            'risk_level': '未验证',
            'verified': False,
            'description': '强势多头规则触发；未接入当前标的真实历史回测'
        })
    
    return results


if __name__ == '__main__':
    # 测试
    test_data = {
        'macd_status': '金叉',
        'rsi': 73.4,
        'trend': '强势多头'
    }
    
    results = simple_backtest_validation(test_data, 'AAPL')
    for r in results:
        print(f"{r['signal']}: {r['description']}")
