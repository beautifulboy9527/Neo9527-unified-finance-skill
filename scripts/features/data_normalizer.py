#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据字段映射检查器
检查分析器返回的字段名与markdown生成器期望的字段名是否一致
"""

# 风险管理字段映射
RISK_MANAGEMENT_MAPPING = {
    # 分析器返回 -> markdown期望
    'stop_loss_standard': 'stop_loss_std',
    'stop_loss_pct_standard': 'stop_loss_pct_std',
    # 'stop_loss_conservative': 'stop_loss_conservative',  # 一致
    # 'stop_loss_pct_conservative': 'stop_loss_pct_conservative',  # 一致
    # 'atr': 'atr',  # 一致
    # 'current_price': 'current_price',  # 一致
}

# 成交量验证字段映射
VOLUME_VALIDATION_MAPPING = {
    # 已一致
    # 'volume_ratio': 'volume_ratio',
    # 'status': 'status',
    # 'analysis': 'analysis',
}

# 技术分析字段映射
TECHNICAL_MAPPING = {
    # 已一致，patterns在technical下
    # 'patterns.support_near': 'patterns.support_near',
    # 'patterns.resistance_near': 'patterns.resistance_near',
}

# 财务健康字段映射
FINANCIAL_MAPPING = {
    # 已一致
    # 'debt_ratio': 'debt_ratio',
    # 'current_ratio': 'current_ratio',
    # 'status': 'status',
}


def normalize_risk_management(data: dict) -> dict:
    """规范化风险管理数据字段名"""
    normalized = data.copy()
    
    # 字段名映射
    if 'stop_loss_standard' in normalized:
        normalized['stop_loss_std'] = normalized['stop_loss_standard']
    if 'stop_loss_pct_standard' in normalized:
        normalized['stop_loss_pct_std'] = normalized['stop_loss_pct_standard']
    
    return normalized


def normalize_result(result: dict) -> dict:
    """规范化所有数据字段名"""
    # 规范化风险管理
    if 'risk_management' in result:
        result['risk_management'] = normalize_risk_management(result['risk_management'])
    
    return result


if __name__ == '__main__':
    print("数据字段映射检查器")
    print("\n风险管理字段映射:")
    for k, v in RISK_MANAGEMENT_MAPPING.items():
        print(f"  {k} -> {v}")
