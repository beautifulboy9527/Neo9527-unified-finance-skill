#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版报告生成器
解决用户反馈的所有问题
"""

import sys
from typing import Dict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def format_number(value, unit='', decimals=2):
    """智能数字格式化"""
    if value is None:
        return 'N/A'
    
    try:
        value = float(value)
    except:
        return str(value)
    
    # 市值格式化
    if unit == 'market_cap':
        if value >= 1e12:
            return f"${value/1e12:.2f}万亿"
        elif value >= 1e9:
            return f"${value/1e9:.2f}亿"
        elif value >= 1e6:
            return f"${value/1e6:.2f}百万"
        else:
            return f"${value:.0f}"
    
    # 百分比格式化
    if unit == '%':
        return f"{value:.1f}%"
    
    # 价格格式化
    if unit == '$':
        return f"${value:.2f}"
    
    # 普通数字
    if abs(value) >= 1e6:
        return f"{value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


def interpret_rsi(rsi: float) -> Dict:
    """RSI 解读"""
    if rsi >= 80:
        return {
            'status': '严重超买',
            'signal': '卖出',
            'description': 'RSI超过80，市场极度乐观，短期可能回调',
            'color': '🔴'
        }
    elif rsi >= 70:
        return {
            'status': '超买',
            'signal': '谨慎',
            'description': 'RSI超过70，市场较为乐观，注意回调风险',
            'color': '🟠'
        }
    elif rsi >= 60:
        return {
            'status': '偏强',
            'signal': '持有',
            'description': 'RSI在60-70区间，多头占优',
            'color': '🟡'
        }
    elif rsi >= 40:
        return {
            'status': '中性',
            'signal': '观望',
            'description': 'RSI在40-60区间，多空平衡',
            'color': '⚪'
        }
    elif rsi >= 30:
        return {
            'status': '偏弱',
            'signal': '关注',
            'description': 'RSI在30-40区间，空头占优',
            'color': '🟡'
        }
    elif rsi >= 20:
        return {
            'status': '超卖',
            'signal': '买入',
            'description': 'RSI低于30，市场悲观，可能反弹',
            'color': '🟢'
        }
    else:
        return {
            'status': '严重超卖',
            'signal': '强烈买入',
            'description': 'RSI低于20，市场极度悲观，反弹概率大',
            'color': '🟢'
        }


def interpret_pe(pe: float, industry_pe: float = 20) -> Dict:
    """PE 解读"""
    if pe <= 0:
        return {
            'status': '亏损',
            'description': '公司处于亏损状态',
            'vs_industry': 'N/A'
        }
    
    ratio = pe / industry_pe
    
    if ratio < 0.5:
        return {
            'status': '严重低估',
            'description': f'PE仅{pe:.1f}倍，远低于行业平均{industry_pe:.1f}倍，可能被低估',
            'vs_industry': f'低于行业{(1-ratio)*100:.0f}%'
        }
    elif ratio < 0.8:
        return {
            'status': '低估',
            'description': f'PE为{pe:.1f}倍，低于行业平均，具有一定价值',
            'vs_industry': f'低于行业{(1-ratio)*100:.0f}%'
        }
    elif ratio < 1.2:
        return {
            'status': '合理',
            'description': f'PE为{pe:.1f}倍，接近行业平均，估值合理',
            'vs_industry': '接近行业平均'
        }
    elif ratio < 1.5:
        return {
            'status': '偏高',
            'description': f'PE为{pe:.1f}倍，高于行业平均，估值偏高',
            'vs_industry': f'高于行业{(ratio-1)*100:.0f}%'
        }
    else:
        return {
            'status': '高估',
            'description': f'PE为{pe:.1f}倍，远高于行业平均，估值过高',
            'vs_industry': f'高于行业{(ratio-1)*100:.0f}%'
        }


def interpret_roe(roe: float) -> Dict:
    """ROE 解读"""
    if roe >= 20:
        return {
            'status': '优秀',
            'description': f'ROE {roe:.1f}%，盈利能力极强',
            'rating': '⭐⭐⭐⭐⭐'
        }
    elif roe >= 15:
        return {
            'status': '良好',
            'description': f'ROE {roe:.1f}%，盈利能力良好',
            'rating': '⭐⭐⭐⭐'
        }
    elif roe >= 10:
        return {
            'status': '一般',
            'description': f'ROE {roe:.1f}%，盈利能力一般',
            'rating': '⭐⭐⭐'
        }
    elif roe >= 5:
        return {
            'status': '较弱',
            'description': f'ROE {roe:.1f}%，盈利能力较弱',
            'rating': '⭐⭐'
        }
    else:
        return {
            'status': '差',
            'description': f'ROE {roe:.1f}%，盈利能力差',
            'rating': '⭐'
        }


def interpret_trend(trend: str, rsi: float) -> str:
    """趋势综合解读"""
    interpretations = {
        '强势多头': '价格位于所有均线上方，上升趋势强劲',
        '多头': '价格位于主要均线上方，上升趋势确立',
        '震荡': '价格在均线间波动，方向不明',
        '空头': '价格位于主要均线下方，下降趋势确立',
        '强势空头': '价格位于所有均线下方，下降趋势强劲'
    }
    
    base = interpretations.get(trend, '趋势分析中')
    
    # 结合 RSI
    if rsi > 70:
        warning = '⚠️ 但RSI超买，短期可能回调'
    elif rsi < 30:
        warning = '⚠️ RSI超卖，可能迎来反弹'
    else:
        warning = ''
    
    return f"{base}{warning}"


def get_technical_patterns(data: Dict) -> list:
    """识别技术形态"""
    patterns = []
    
    tech = data.get('technical', {})
    rsi = tech.get('rsi', 50)
    macd_status = tech.get('macd_status', '')
    trend = tech.get('trend', '')
    
    # 金叉/死叉
    if '金叉' in macd_status:
        patterns.append({
            'name': 'MACD金叉',
            'signal': '买入',
            'description': 'MACD快线上穿慢线，短期看涨信号'
        })
    elif '死叉' in macd_status:
        patterns.append({
            'name': 'MACD死叉',
            'signal': '卖出',
            'description': 'MACD快线下穿慢线，短期看跌信号'
        })
    
    # 超买超卖
    if rsi >= 70:
        patterns.append({
            'name': 'RSI超买',
            'signal': '卖出',
            'description': f'RSI={rsi:.1f}，短期可能回调'
        })
    elif rsi <= 30:
        patterns.append({
            'name': 'RSI超卖',
            'signal': '买入',
            'description': f'RSI={rsi:.1f}，短期可能反弹'
        })
    
    # 趋势形态
    if '强势' in trend:
        patterns.append({
            'name': '强势趋势',
            'signal': '顺势',
            'description': f'{trend}，建议顺势操作'
        })
    
    return patterns


def get_investment_advice(score: float, horizon: str, data: Dict) -> Dict:
    """根据投资周期给出建议"""
    
    # 基础建议
    if score >= 70:
        base = '看好'
    elif score >= 50:
        base = '中性'
    else:
        base = '谨慎'
    
    # 根据投资周期调整
    if horizon == 'short':  # 短线
        tech = data.get('technical', {})
        rsi = tech.get('rsi', 50)
        trend = tech.get('trend', '')
        
        if rsi > 70:
            return {
                'advice': '观望',
                'reason': 'RSI超买，短线不宜追高',
                'action': '等待回调'
            }
        elif '多头' in trend:
            return {
                'advice': '轻仓试多',
                'reason': '趋势向上，可小仓位跟随',
                'action': '设置止损'
            }
        else:
            return {
                'advice': '观望',
                'reason': '趋势不明朗',
                'action': '等待机会'
            }
    
    elif horizon == 'medium':  # 波段
        val = data.get('valuation', {})
        upside = val.get('upside', 0)
        
        if upside > 20:
            return {
                'advice': '逢低布局',
                'reason': f'估值低估{upside:.0f}%，中期有空间',
                'action': '分批建仓'
            }
        elif upside < -30:
            return {
                'advice': '减仓',
                'reason': f'估值高估{abs(upside):.0f}%，中期风险大',
                'action': '逐步减仓'
            }
        else:
            return {
                'advice': '持有',
                'reason': '估值合理，波段持有',
                'action': '高抛低吸'
            }
    
    else:  # 长线
        fund = data.get('fundamentals', {})
        roe = fund.get('roe', 0)
        
        if roe > 15:
            return {
                'advice': '长期持有',
                'reason': f'ROE {roe:.1f}%，优质企业',
                'action': '定期定额'
            }
        else:
            return {
                'advice': '谨慎',
                'reason': '基本面一般，长期风险',
                'action': '分散投资'
            }


# 测试
if __name__ == '__main__':
    print("增强版报告工具测试")
    print("=" * 60)
    
    # 测试 RSI 解读
    print("\nRSI 解读:")
    for rsi in [75, 65, 50, 35, 25]:
        result = interpret_rsi(rsi)
        print(f"  RSI {rsi}: {result['color']} {result['status']} - {result['description']}")
    
    # 测试 PE 解读
    print("\nPE 解读:")
    for pe in [10, 20, 30, 50]:
        result = interpret_pe(pe, industry_pe=25)
        print(f"  PE {pe}: {result['status']} - {result['vs_industry']}")
    
    # 测试市值格式化
    print("\n市值格式化:")
    print(f"  {format_number(3971820552192, 'market_cap')}")
    print(f"  {format_number(1500000000000, 'market_cap')}")
