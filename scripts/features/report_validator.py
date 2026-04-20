#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告数据验证器 v1.0
- 一致性校验
- 数据完整性检查
- 字段合理性验证
"""

from typing import Dict, List, Tuple


def validate_report(result: Dict) -> Tuple[bool, List[str]]:
    """报告生成前一致性校验"""
    errors = []
    warnings = []
    
    # 1. 评分范围
    score = result.get('score', 0)
    if not (0 <= score <= 100):
        errors.append(f"评分异常：{score}（应在0-100之间）")
    
    # 2. Buff总分一致性
    buffs = result.get('buffs', [])
    if buffs:
        calculated_total = sum([int(b[1]) for b in buffs])
        displayed_total = result.get('buff_total', calculated_total)
        if calculated_total != displayed_total:
            errors.append(f"Buff总分不一致：计算{calculated_total:+d} vs 显示{displayed_total:+d}")
    
    # 3. 止损价位合理性
    current_price = result.get('price', {}).get('current', 0)
    risk_mgmt = result.get('risk_management', {})
    
    stop_loss_std = risk_mgmt.get('stop_loss_std', risk_mgmt.get('stop_loss_price', 0))
    stop_loss_conservative = risk_mgmt.get('stop_loss_conservative', 0)
    
    if stop_loss_std <= 0 and current_price > 0:
        errors.append("标准止损价位无效（<=0）")
    elif stop_loss_std >= current_price and current_price > 0:
        errors.append(f"止损价位{stop_loss_std:.2f}高于当前价{current_price:.2f}")
    
    if stop_loss_conservative > 0 and stop_loss_conservative >= current_price:
        errors.append(f"保守止损价位{stop_loss_conservative:.2f}高于当前价{current_price:.2f}")
    
    # 4. N/A字段不应有确定性文案
    volume_val = result.get('volume_validation', {})
    if volume_val.get('status') in ['N/A', None, '']:
        volume_analysis = volume_val.get('analysis', '')
        if volume_analysis and any(keyword in volume_analysis for keyword in ['确认', '判断', '明确', '肯定']):
            warnings.append("成交量N/A字段存在确定性文案")
    
    # 5. 阻力位去重
    tech = result.get('technical', {})
    patterns = tech.get('patterns', {})
    
    res_near = patterns.get('resistance_near', 0)
    res_far = patterns.get('resistance_far', 0)
    
    if res_near > 0 and res_far > 0:
        diff_pct = abs(res_near - res_far) / current_price if current_price > 0 else 0
        if diff_pct < 0.002:  # 0.2%以内视为重复
            warnings.append(f"阻力位重复：{res_near:.2f}和{res_far:.2f}相差仅{diff_pct*100:.1f}%，建议合并")
    
    # 6. 评分与Buff逻辑一致性
    total_buff = result.get('buff_total', 0)
    if total_buff > 2 and score < 50:
        warnings.append(f"Buff总分{total_buff:+d}偏多，但评分{score}偏低，逻辑可能不自洽")
    elif total_buff < -2 and score > 50:
        warnings.append(f"Buff总分{total_buff:+d}偏空，但评分{score}偏高，逻辑可能不自洽")
    
    # 7. 支撑阻力合理性
    support_near = patterns.get('support_near', 0)
    support_far = patterns.get('support_far', 0)
    
    if support_near > 0 and support_near >= current_price:
        errors.append(f"支撑位{support_near:.2f}高于当前价{current_price:.2f}")
    
    if support_far > support_near and support_near > 0:
        warnings.append(f"远期支撑{support_far:.2f}低于近期支撑{support_near:.2f}，逻辑可能有误")
    
    # 8. 技术指标合理性
    rsi = tech.get('indicators', {}).get('rsi', 50)
    if rsi > 100 or rsi < 0:
        errors.append(f"RSI值{rsi:.1f}超出合理范围(0-100)")
    
    # 9. 财务数据合理性
    financial = result.get('financial', {})
    debt_ratio = financial.get('debt_ratio', 0)
    
    if debt_ratio > 100:
        errors.append(f"资产负债率{debt_ratio:.1f}%超过100%，数据异常")
    elif debt_ratio > 90:
        warnings.append(f"资产负债率{debt_ratio:.1f}%极高，建议核实")
    
    # 10. 必填字段检查
    required_fields = ['symbol', 'name_cn', 'score', 'recommendation', 'timestamp']
    for field in required_fields:
        if not result.get(field):
            errors.append(f"必填字段{field}缺失")
    
    # 输出结果
    if errors:
        print("❌ 报告校验失败：")
        for error in errors:
            print(f"  ⚠️ {error}")
    
    if warnings:
        print("⚠️ 报告警告：")
        for warning in warnings:
            print(f"  📝 {warning}")
    
    if not errors and not warnings:
        print("✅ 报告校验通过")
    
    return len(errors) == 0, errors + warnings


def calculate_stop_loss_levels(current_price: float, atr: float) -> Dict:
    """计算止损位"""
    if current_price <= 0 or atr <= 0:
        return {
            'stop_loss_std': 0,
            'stop_loss_conservative': 0,
            'stop_loss_pct_std': 0,
            'stop_loss_pct_conservative': 0
        }
    
    stop_loss_std = current_price - 2 * atr
    stop_loss_conservative = current_price - 1 * atr
    
    stop_loss_pct_std = (current_price - stop_loss_std) / current_price * 100
    stop_loss_pct_conservative = (current_price - stop_loss_conservative) / current_price * 100
    
    return {
        'stop_loss_std': round(stop_loss_std, 2),
        'stop_loss_conservative': round(stop_loss_conservative, 2),
        'stop_loss_pct_std': round(stop_loss_pct_std, 1),
        'stop_loss_pct_conservative': round(stop_loss_pct_conservative, 1)
    }


if __name__ == '__main__':
    print("报告数据验证器 v1.0")
