#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整Markdown报告生成器 v2.0
- 修复数据获取问题
- 完整的支撑阻力位、成交量、风险管理数据
- 详细解读
"""

import sys
from typing import Dict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


from report_validator import calculate_stop_loss_levels

def generate_markdown_report(result: Dict) -> str:
    """生成完整的Markdown报告"""
    
    symbol = result.get('symbol', '')
    name_cn = result.get('name_cn', symbol)
    score = result.get('score', 0)
    recommendation = result.get('recommendation', 'N/A')
    
    # 安全获取数据
    tech = result.get('technical', {})
    patterns = tech.get('patterns', {})
    financial = result.get('financial', {})
    valuation = result.get('valuation', {})
    profitability = result.get('profitability', {})
    risk_mgmt = result.get('risk_management', {})
    volume_val = result.get('volume_validation', {})
    
    md = f'''# 📊 {name_cn} ({symbol}) 投资分析报告

**报告时间**: {result.get('timestamp', '')}  
**数据来源**: yfinance + 专业分析模块  
**综合评分**: **{score}/100**  
**投资建议**: **{recommendation}**

---

## 一、基础信息

| 项目 | 数值 |
|------|------|
| 股票名称 | {name_cn} |
| 股票代码 | {symbol} |
| 所属市场 | {result.get('market', 'N/A')} |
| 所属行业 | {result.get('industry', {}).get('name_cn', 'N/A')} |
| 所属板块 | {result.get('industry', {}).get('sector', 'N/A')} |
| 当前价格 | **{result.get('price', {}).get('current', 0):.2f}元** |
| 今日涨跌 | **{result.get('price', {}).get('change_pct', 0):+.2f}%** |
| 总市值 | {valuation.get('market_cap_str', 'N/A')} |

---

## 二、行业分析

### 2.1 行业定位

| 指标 | 数值 |
|------|------|
| 所属行业 | {result.get('industry', {}).get('name_cn', 'N/A')} |
| 所属板块 | {result.get('industry', {}).get('sector', 'N/A')} |
| 行业周期 | {result.get('industry', {}).get('cycle', '未知')} |
| 行业风险 | {result.get('industry', {}).get('risk', '未知')} |

### 2.2 行业分析解读

{result.get('industry', {}).get('analysis', '暂无分析')}

---

## 三、估值分析

### 3.1 估值指标

| 指标 | 数值 | 评价 |
|------|------|------|
| 市盈率 PE | **{valuation.get('pe', 0):.2f}** | {_get_pe_eval(valuation.get('pe', 0))} |
| 市净率 PB | **{valuation.get('pb', 0):.2f}** | {_get_pb_eval(valuation.get('pb', 0))} |
| 市销率 PS | **{valuation.get('ps', 0):.2f}** | - |
| 总市值 | **{valuation.get('market_cap_str', 'N/A')}** | - |

### 3.2 估值分析解读

{valuation.get('analysis', '暂无分析')}

---

## 四、盈利能力

### 4.1 盈利指标

| 指标 | 数值 | 评价 |
|------|------|------|
| 净资产收益率 ROE | **{profitability.get('roe', 0)*100:.2f}%** | {_get_roe_eval(profitability.get('roe', 0))} |
| 毛利率 | **{profitability.get('gross_margin', 0)*100:.2f}%** | - |
| 净利率 | **{profitability.get('net_margin', 0)*100:.2f}%** | - |
| 盈利状态 | **{'盈利' if profitability.get('is_profitable') else '亏损'}** | {'✅' if profitability.get('is_profitable') else '❌'} |

### 4.2 盈利能力解读

{profitability.get('analysis', '暂无分析')}

---

## 五、财务健康

### 5.1 财务指标

| 指标 | 数值 | 评价 |
|------|------|------|
| 资产负债率 | **{financial.get('debt_ratio', 0):.2f}%** | {_get_debt_eval(financial.get('debt_ratio', 0))} |
| 流动比率 | **{financial.get('current_ratio', 0):.2f}** | {_get_liquidity_eval(financial.get('current_ratio', 0))} |
| 财务状态 | **{financial.get('status', 'N/A')}** | - |

**数据来源**: {financial.get('data_source', '财报')} (置信度: {financial.get('confidence', 0)*100:.0f}%)

### 5.2 风险提示

'''

    risks = financial.get('risks', [])
    if risks:
        for risk in risks:
            md += f"- ⚠️ {risk}\n"
    else:
        md += "- ✅ 暂无明显风险\n"
    
    md += f'''
### 5.3 财务健康解读

{financial.get('analysis', '暂无分析')}

---

## 六、技术分析

### 6.1 核心技术指标

| 指标 | 数值 | 状态 |
|------|------|------|
| RSI 相对强弱 | **{tech.get('indicators', {}).get('rsi', 50):.1f}** | {patterns.get('rsi_desc', 'N/A')} |
| MACD 状态 | **{str(patterns.get('macd_desc', 'N/A')).split('(')[0].strip()}** | {'看涨' if '金叉' in str(patterns.get('macd_desc', '')) else '看跌'} |
| 趋势判断 | **{str(patterns.get('trend_desc', 'N/A')).split('(')[0].strip()}** | - |
| 信号强度 | **{tech.get('signal_strength', 0)}** | - |

### 6.2 技术形态分析

'''

    # 技术形态
    if patterns.get('trend_desc'):
        md += f"- **趋势**: {patterns['trend_desc']}\n"
    if patterns.get('rsi_desc'):
        md += f"- **RSI**: {patterns['rsi_desc']}\n"
    if patterns.get('macd_desc'):
        md += f"- **MACD**: {patterns['macd_desc']}\n"
    if patterns.get('bb_desc'):
        md += f"- **布林带**: {patterns['bb_desc']}\n"
    if patterns.get('double_top_desc'):
        md += f"- **形态**: {patterns['double_top_desc']}\n"
    if patterns.get('double_bottom_desc'):
        md += f"- **形态**: {patterns['double_bottom_desc']}\n"
    
    # 支撑阻力位 - 从patterns获取
    support_near = patterns.get('support_near', 0)
    support_far = patterns.get('support_far', 0)
    resistance_near = patterns.get('resistance_near', 0)
    resistance_far = patterns.get('resistance_far', 0)
    support_near_pct = patterns.get('support_near_pct', 0)
    support_far_pct = patterns.get('support_far_pct', 0)
    resistance_near_pct = patterns.get('resistance_near_pct', 0)
    resistance_far_pct = patterns.get('resistance_far_pct', 0)
    
    md += f'''

### 6.3 支撑阻力位

| 类型 | 价位 | 距离 |
|------|------|------|
| 近期支撑 | **{support_near:.2f}元** | {support_near_pct:.1f}% |
| 远期支撑 | **{support_far:.2f}元** | {support_far_pct:.1f}% |
| 近期阻力 | **{resistance_near:.2f}元** | +{resistance_near_pct:.1f}% |
| 远期阻力 | **{resistance_far:.2f}元** | +{resistance_far_pct:.1f}% |

**支撑解读**: {patterns.get('support_desc', '暂无数据')}

**阻力解读**: {patterns.get('resistance_desc', '暂无数据')}

### 6.4 成交量验证

| 指标 | 数值 | 状态 |
|------|------|------|
| 成交量比率 | **{volume_val.get('volume_ratio', 1):.2f}x** | {_get_volume_eval(volume_val.get('volume_ratio', 1))} |
| 成交量状态 | **{volume_val.get('status', '正常')}** | - |
| 趋势确认 | **{volume_val.get('trend_confirmation', '中性')}** | - |

**成交量解读**: {volume_val.get('analysis', '暂无分析')}

### 6.5 技术分析综合解读

{tech.get('analysis', '暂无分析')}

---

## 七、风险管理

### 7.1 ATR止损建议

| 指标 | 数值 |
|------|------|
| 当前价格 | **{risk_mgmt.get('current_price', result.get('price', {}).get('current', 0)):.2f}元** |
| ATR值 | **{risk_mgmt.get('atr', 0):.2f}** |
| 标准止损 | **{risk_mgmt.get('stop_loss_price', 0):.2f}元** |
| 止损幅度 | **{risk_mgmt.get('risk_pct', 0):.1f}%** |

### 7.2 止损策略解读

{risk_mgmt.get('analysis', '暂无分析')}

---

## 八、Buff叠加分析

'''

    # Buff分析
    buffs = _calculate_buffs(result)
    
    md += "| Buff类型 | 分值 | 描述 |\n"
    md += "|----------|------|------|\n"
    
    for buff_type, buff_score, desc, color in buffs:
        md += f"| **{buff_type}** | **{buff_score}** | {desc} |\n"
    
    total = sum([int(b[1]) for b in buffs])
    total_text = '偏多' if total > 0 else ('偏空' if total < 0 else '中性')
    
    md += f"| **总Buff** | **{total:+d}** | **{total_text}** (综合评分 {score}/100) |\n"
    
    md += f'''

---

## 九、汇总分析

### 9.1 行业周期分析

{result.get('summary', {}).get('industry_analysis', '暂无分析')}

### 9.2 盈利能力推演

{result.get('summary', {}).get('profit_analysis', '暂无分析')}

### 9.3 估值水平分析

{result.get('summary', {}).get('valuation_analysis', '暂无分析')}

### 9.4 财务健康评估

{result.get('summary', {}).get('financial_analysis', '暂无分析')}

### 9.5 技术面判断

{result.get('summary', {}).get('tech_analysis', '暂无分析')}

### 9.6 综合投资建议

{result.get('summary', {}).get('final', '暂无分析')}

---

## 十、操作建议

{_generate_action_advice_md(result)}

---

## 十一、风险提示

⚠️ **重要提示**:
- 本报告基于公开数据分析，仅供参考，不构成投资建议
- 投资有风险，入市需谨慎
- 数据来源: yfinance
- 分析时间: {result.get('timestamp', '')}

---

**报告生成**: A股分析器 v3.0  
**数据来源**: yfinance + 专业分析模块
'''
    
    return md


def _get_pe_eval(pe: float) -> str:
    if pe < 15: return '低估 ✅'
    elif pe < 25: return '合理 ✅'
    elif pe < 40: return '偏高 ⚠️'
    return '高估 ❌'

def _get_pb_eval(pb: float) -> str:
    if pb < 2: return '低估 ✅'
    elif pb < 4: return '合理 ✅'
    elif pb < 6: return '偏高 ⚠️'
    return '高估 ❌'

def _get_roe_eval(roe: float) -> str:
    if roe > 0.20: return '优秀 ✅'
    elif roe > 0.15: return '良好 ✅'
    elif roe > 0.10: return '一般 ⚠️'
    return '较差 ❌'

def _get_debt_eval(debt: float) -> str:
    if debt < 40: return '低风险 ✅'
    elif debt < 60: return '适中 ✅'
    elif debt < 70: return '需关注 ⚠️'
    return '高风险 ❌'

def _get_liquidity_eval(ratio: float) -> str:
    if ratio > 2: return '流动性好 ✅'
    elif ratio > 1: return '流动性正常 ✅'
    elif ratio > 0.5: return '流动性不足 ⚠️'
    return '流动性风险 ❌'

def _get_volume_eval(ratio: float) -> str:
    if ratio > 2: return '放量 ✅'
    elif ratio > 1.5: return '温和放量 ✅'
    elif ratio > 0.8: return '正常 ✅'
    return '缩量 ⚠️'

def _calculate_buffs(result: Dict) -> list:
    buffs = []
    
    profitability = result.get('profitability', {})
    valuation = result.get('valuation', {})
    financial = result.get('financial', {})
    tech = result.get('technical', {})
    
    # 基本面buff
    roe = profitability.get('roe', 0)
    if roe > 0.20:
        buffs.append(('基本面', '+3', f'ROE优秀({roe*100:.1f}%)，盈利能力强', '#22c55e'))
    elif roe > 0.15:
        buffs.append(('基本面', '+2', f'ROE良好({roe*100:.1f}%)，盈利稳健', '#22c55e'))
    elif roe > 0.10:
        buffs.append(('基本面', '+1', f'ROE一般({roe*100:.1f}%)', '#f59e0b'))
    else:
        buffs.append(('基本面', '-1', f'ROE较差({roe*100:.1f}%)', '#ef4444'))
    
    # 估值buff
    pe = valuation.get('pe', 0)
    if pe and pe < 15:
        buffs.append(('估值', '+2', f'PE低估({pe:.1f})，安全边际高', '#22c55e'))
    elif pe and pe < 25:
        buffs.append(('估值', '+1', f'PE合理({pe:.1f})', '#f59e0b'))
    elif pe and pe > 40:
        buffs.append(('估值', '-2', f'PE高估({pe:.1f})，估值偏高', '#ef4444'))
    
    # 财务健康buff
    status = financial.get('status', '')
    debt_ratio = financial.get('debt_ratio', 0)
    if status == '健康':
        buffs.append(('财务', '+1', f'财务健康，资产负债率{debt_ratio:.1f}%', '#22c55e'))
    elif status == '需关注':
        buffs.append(('财务', '-1', f'财务需关注，资产负债率{debt_ratio:.1f}%', '#f59e0b'))
    elif status == '高风险':
        buffs.append(('财务', '-2', f'财务风险高，资产负债率{debt_ratio:.1f}%', '#ef4444'))
    
    # 技术面buff
    signal = tech.get('signal_strength', 0)
    if signal > 3:
        buffs.append(('技术面', '+2', f'技术面强势，信号强度{signal}', '#22c55e'))
    elif signal > 0:
        buffs.append(('技术面', '+1', f'技术面偏多，信号强度{signal}', '#22c55e'))
    elif signal < -3:
        buffs.append(('技术面', '-2', f'技术面弱势，信号强度{signal}', '#ef4444'))
    elif signal < 0:
        buffs.append(('技术面', '-1', f'技术面偏空，信号强度{signal}', '#ef4444'))
    
    return buffs

def _generate_action_advice_md(result: Dict) -> str:
    tech = result.get('technical', {})
    patterns = tech.get('patterns', {})
    volume = result.get('volume_validation', {})
    price = result.get('price', {})
    
    current = price.get('current', 0)
    support_near = patterns.get('support_near', 0)
    resistance_near = patterns.get('resistance_near', 0)
    rsi = tech.get('indicators', {}).get('rsi', 50)
    volume_ratio = volume.get('volume_ratio', 1)
    trend = str(patterns.get('trend_desc', '')).split('(')[0].strip()
    
    advice = []
    
    # 趋势建议
    if '多头' in trend:
        advice.append(f"✅ 当前处于{trend}，趋势向上，可考虑持股或逢低加仓")
    elif '空头' in trend:
        advice.append(f"⚠️ 当前处于{trend}，趋势向下，建议观望或减仓")
    else:
        advice.append(f"➡️ 当前趋势{trend}，建议观望等待方向明确")
    
    # RSI建议
    if rsi > 80:
        advice.append(f"⚠️ RSI={rsi:.1f}极度超买，短期回调风险大，不建议追高")
    elif rsi > 70:
        advice.append(f"⚠️ RSI={rsi:.1f}超买，注意回调风险，可考虑逢高减仓")
    elif rsi < 30:
        advice.append(f"✅ RSI={rsi:.1f}超卖，可能存在反弹机会，可关注")
    
    # 支撑阻力建议
    if current and support_near and support_near > 0:
        support_pct = (current - support_near) / current * 100
        advice.append(f"📍 近期支撑位{support_near:.2f}元(距离{support_pct:.1f}%)，跌破支撑需警惕")
    
    if current and resistance_near and resistance_near > 0:
        resistance_pct = (resistance_near - current) / current * 100
        advice.append(f"📍 近期阻力位{resistance_near:.2f}元(距离{resistance_pct:.1f}%)，突破阻力可加仓")
    
    # 成交量建议
    if volume_ratio > 1.5:
        advice.append(f"✅ 成交量放大{volume_ratio:.2f}倍，市场活跃度高，趋势可信")
    elif volume_ratio < 0.8:
        advice.append(f"⚠️ 成交量萎缩至{volume_ratio:.2f}倍，市场观望情绪浓，注意风险")
    
    return '\n\n'.join(advice)


if __name__ == '__main__':
    print("Markdown报告生成器 v2.0")
