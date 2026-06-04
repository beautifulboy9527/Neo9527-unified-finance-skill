#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告增强模块 v1.0
- 胜率驱动的Buff叠加
- 7层深度分析
- 完整汇总分析
- 投资逻辑链条
"""

import sys
from typing import Dict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from win_rate_model import WinRateModel, DepthAnalyzer


def enhance_report(result: Dict) -> Dict:
    """
    增强报告内容
    
    Args:
        result: 原始分析结果
    
    Returns:
        增强后的结果
    """
    # 1. 计算胜率
    if 'technical' in result:
        win_rate_data = WinRateModel.calculate_win_rate(result['technical'])
        result['win_rate'] = win_rate_data
    
    # 2. 生成深度分析
    depth_analysis = DepthAnalyzer.generate_deep_analysis(result)
    result['depth_analysis'] = depth_analysis
    
    # 3. 重新计算Buff（基于胜率）
    buff_data = _calculate_buff_from_win_rate(result)
    result['buff_enhanced'] = buff_data
    
    # 4. 生成汇总分析文本
    summary_text = _generate_summary_text(result)
    result['summary_text'] = summary_text
    
    return result


def _calculate_buff_from_win_rate(result: Dict) -> Dict:
    """
    基于胜率计算Buff
    
    逻辑：
    - 胜率 > 65% → 强烈看多 (+5以上)
    - 胜率 55-65% → 偏多 (+2到+5)
    - 胜率 45-55% → 中性 (-2到+2)
    - 胜率 < 45% → 偏空 (-5到-2)
    """
    win_rate_data = result.get('win_rate', {})
    win_rate = win_rate_data.get('win_rate', 0.5)
    
    # 计算buff分数（胜率基准50%）
    # 胜率50% → buff 0
    # 胜率60% → buff +3
    # 胜率70% → buff +6
    buff_score = (win_rate - 0.50) * 20  # -10 到 +10
    
    # 分类buff
    buffs = []
    
    # 1. 技术面Buff（基于胜率信号）
    signals = win_rate_data.get('signals', [])
    for signal in signals:
        if signal['contribution'] > 0:
            buffs.append({
                'type': '技术共振',
                'score': signal['contribution'] * 10,
                'description': f"{signal['name']}: {signal['description']}"
            })
    
    # 2. 基本面Buff
    profitability = result.get('profitability', {})
    roe = profitability.get('roe', 0) * 100
    
    if roe >= 20:
        buffs.append({
            'type': '基本面',
            'score': 3,
            'description': f'ROE优秀({roe:.1f}%)，盈利能力强'
        })
    elif roe >= 15:
        buffs.append({
            'type': '基本面',
            'score': 2,
            'description': f'ROE良好({roe:.1f}%)'
        })
    elif roe >= 10:
        buffs.append({
            'type': '基本面',
            'score': 1,
            'description': f'ROE一般({roe:.1f}%)'
        })
    else:
        buffs.append({
            'type': '基本面',
            'score': -1,
            'description': f'ROE较弱({roe:.1f}%)'
        })
    
    # 3. 估值Buff
    valuation = result.get('valuation', {})
    pe = valuation.get('pe', 0)
    
    if pe > 0 and pe < 15:
        buffs.append({
            'type': '估值',
            'score': 2,
            'description': f'PE低估({pe:.1f}倍)'
        })
    elif pe >= 15 and pe < 30:
        buffs.append({
            'type': '估值',
            'score': 1,
            'description': f'PE合理({pe:.1f}倍)'
        })
    elif pe >= 30 and pe < 50:
        buffs.append({
            'type': '估值',
            'score': 0,
            'description': f'PE偏高({pe:.1f}倍)'
        })
    elif pe >= 50:
        buffs.append({
            'type': '估值',
            'score': -1,
            'description': f'PE高估({pe:.1f}倍)'
        })
    
    # 4. 财务Buff
    financial = result.get('financial', {})
    debt_ratio = financial.get('debt_ratio', 0)
    
    if debt_ratio <= 30:
        buffs.append({
            'type': '财务',
            'score': 1,
            'description': f'资产负债率低({debt_ratio:.1f}%)'
        })
    elif debt_ratio <= 50:
        buffs.append({
            'type': '财务',
            'score': 0,
            'description': f'资产负债率适中({debt_ratio:.1f}%)'
        })
    else:
        buffs.append({
            'type': '财务',
            'score': -1,
            'description': f'资产负债率较高({debt_ratio:.1f}%)'
        })
    
    # 计算总分
    total_score = sum(b['score'] for b in buffs)
    
    # 判断方向
    if total_score >= 5:
        direction = '强烈看多'
        icon = '🚀'
    elif total_score >= 2:
        direction = '偏多'
        icon = '📈'
    elif total_score >= -2:
        direction = '中性'
        icon = '⚖️'
    elif total_score >= -5:
        direction = '偏空'
        icon = '📉'
    else:
        direction = '强烈看空'
        icon = '⚠️'
    
    return {
        'buffs': buffs,
        'total_score': total_score,
        'direction': direction,
        'icon': icon,
        'win_rate_based': True,
        'win_rate': win_rate
    }


def _generate_summary_text(result: Dict) -> str:
    """生成汇总分析文本"""
    
    name = result.get('name_cn', result.get('symbol', ''))
    score = result.get('score', 0)
    
    # 胜率数据
    win_rate_data = result.get('win_rate', {})
    win_rate = win_rate_data.get('win_rate', 0.5)
    bullish_count = win_rate_data.get('bullish_count', 0)
    bearish_count = win_rate_data.get('bearish_count', 0)
    
    # 深度分析
    depth = result.get('depth_analysis', {})
    
    # 估值
    valuation = result.get('valuation', {})
    pe = valuation.get('pe', 0)
    
    # 风险收益
    technical = result.get('technical', {})
    patterns = technical.get('patterns', {})
    price = result.get('price', {})
    current = price.get('current', 0)
    support_near = patterns.get('support_near', 0)
    resistance_near = patterns.get('resistance_near', 0)
    
    # 构建汇总文本
    summary = f"## 综合评估\n\n"
    
    # 评级
    if score >= 70:
        rating = "⭐⭐⭐⭐⭐"
        rating_text = "优秀"
    elif score >= 60:
        rating = "⭐⭐⭐⭐☆"
        rating_text = "良好"
    elif score >= 50:
        rating = "⭐⭐⭐☆☆"
        rating_text = "尚可"
    else:
        rating = "⭐⭐☆☆☆"
        rating_text = "较弱"
    
    summary += f"**投资价值**: {rating} ({rating_text})\n\n"
    
    # 核心逻辑
    summary += f"### 核心逻辑\n\n"
    summary += f"{name}综合评分{score}分，"
    
    if win_rate >= 0.65:
        summary += f"技术面胜率{win_rate*100:.1f}%（强烈看多），"
    elif win_rate >= 0.55:
        summary += f"技术面胜率{win_rate*100:.1f}%（偏多），"
    elif win_rate >= 0.45:
        summary += f"技术面胜率{win_rate*100:.1f}%（中性），"
    else:
        summary += f"技术面胜率{win_rate*100:.1f}%（偏空），"
    
    summary += f"共{bullish_count}个看涨信号，{bearish_count}个看跌信号。\n\n"
    
    # 估值判断
    if pe > 0:
        if pe < 20:
            summary += f"估值方面，PE={pe:.1f}倍，处于低估区域，安全边际高。"
        elif pe < 30:
            summary += f"估值方面，PE={pe:.1f}倍，估值合理。"
        elif pe < 50:
            summary += f"估值方面，PE={pe:.1f}倍，估值偏高，需业绩支撑。"
        else:
            summary += f"估值方面，PE={pe:.1f}倍，估值较高，风险较大。"
    
    summary += "\n\n"
    
    # 风险收益
    if current > 0 and support_near > 0 and resistance_near > 0:
        downside = ((support_near - current) / current) * 100
        upside = ((resistance_near - current) / current) * 100
        summary += f"风险收益方面，距离支撑{abs(downside):.1f}%，距离阻力+{abs(upside):.1f}%。"
        
        if abs(upside) > abs(downside) * 1.5:
            summary += "上涨空间大于下跌风险，风险收益比佳。"
        else:
            summary += "需谨慎控制仓位。"
    
    summary += "\n\n"
    
    # 操作建议
    summary += f"### 操作建议\n\n"
    
    buff_data = result.get('buff_enhanced', {})
    total_buff = buff_data.get('total_score', 0)
    
    # 综合胜率 = 技术面胜率 * 0.4 + 基本面评估 * 0.6
    # 基本面评估基于buff总分
    fundamental_score = (total_buff + 10) / 20 * 100  # -10~+10 → 0~100
    fundamental_rate = fundamental_score / 100
    
    # 综合胜率
    combined_win_rate = win_rate * 0.4 + fundamental_rate * 0.6
    
    # 操作建议基于综合胜率
    if combined_win_rate >= 0.65:
        summary += "✅ **强烈看多**，可积极布局。建议仓位30-50%，设置止损位。\n"
    elif combined_win_rate >= 0.55:
        summary += "⚠️ **偏多**，可适度参与。建议仓位20-30%，关注支撑位。\n"
    elif total_buff >= -2:
        summary += "⚖️ **中性**，建议观望。等待更明确信号再行动。\n"
    else:
        summary += "❌ **偏空**，暂不推荐。等待趋势反转信号。\n"
    
    summary += "\n"
    
    # 风险提示
    summary += f"### 风险提示\n\n"
    
    rsi = technical.get('indicators', {}).get('rsi', 50)
    if rsi > 70:
        summary += f"- ⚠️ RSI={rsi:.1f}超买，短线回调风险高\n"
    
    if pe > 50:
        summary += f"- ⚠️ 估值较高(PE={pe:.1f})，需业绩增长支撑\n"
    
    if abs(downside) > abs(upside):
        summary += f"- ⚠️ 下跌风险({abs(downside):.1f}%)大于上涨空间({abs(upside):.1f}%)\n"
    
    summary += "\n**免责声明**: 本报告基于公开数据分析，仅供参考，不构成投资建议。投资有风险，入市需谨慎。\n"
    
    return summary


if __name__ == '__main__':
    # 测试
    test_result = {
        'symbol': '600563',
        'name_cn': '睿能科技',
        'score': 65,
        'technical': {
            'indicators': {'rsi': 55.5},
            'patterns': {
                'macd_desc': 'MACD金叉 (看涨)',
                'trend_desc': '震荡整理'
            }
        },
        'profitability': {'roe': 0.21},
        'valuation': {'pe': 23.26},
        'financial': {'debt_ratio': 30.9},
        'price': {'current': 123.02}
    }
    
    enhanced = enhance_report(test_result)
    
    print("=" * 80)
    print("报告增强测试")
    print("=" * 80)
    print(f"\n胜率: {enhanced['win_rate']['win_rate_pct']}")
    print(f"Buff总分: {enhanced['buff_enhanced']['total_score']}")
    print(f"方向: {enhanced['buff_enhanced']['icon']} {enhanced['buff_enhanced']['direction']}")
    print("\n" + "=" * 80)
    print(enhanced['summary_text'])
