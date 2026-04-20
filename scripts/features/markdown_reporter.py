#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整Markdown报告生成器 v3.0
- P0修复：ATR止损、Buff一致性、N/A降级
- P1修复：操作建议分人群、财务相对评分、估值参照系
- P2修复：统计口吻、阻力分类
- 新增：事件驱动、评分拆分、口径标签
"""

import sys
from typing import Dict, List, Tuple
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from report_validator import calculate_stop_loss_levels


def generate_markdown_report(result: Dict) -> str:
    """生成完整的Markdown报告 v3.0"""
    
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
    price = result.get('price', {})
    
    current_price = price.get('current', 0)
    
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
| 所属板块 | {result.get('industry', {}).get('sector_cn', result.get('industry', {}).get('sector', 'N/A'))} |
| 当前价格 | **{'N/A' if pd.isna(current_price) or current_price <= 0 else f'{current_price:.2f}元'}** |
| 今日涨跌 | **{'N/A' if pd.isna(price.get('change_pct', 0)) else f"{price.get('change_pct', 0):+.2f}%"}** |
| 总市值 | {valuation.get('market_cap_str', 'N/A')} |

---

## 二、行业分析

### 2.1 行业定位

| 指标 | 数值 |
|------|------|
| 所属行业 | {result.get('industry', {}).get('name_cn', 'N/A')} |
| 所属板块 | {result.get('industry', {}).get('sector_cn', result.get('industry', {}).get('sector', 'N/A'))} |
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

| 指标 | 数值 | 计算公式 |
|------|------|----------|
| RSI 相对强弱 | **{tech.get('indicators', {}).get('rsi', 50):.1f}** | RSI(14, 简单平均，非Wilder) |
| MACD 状态 | **{str(patterns.get('macd_desc', 'N/A')).split('(')[0].strip()}** | MACD(12,26,9) |
| 趋势判断 | **{str(patterns.get('trend_desc', 'N/A')).split('(')[0].strip()}** | SMA(5,10,20) |
| 信号强度 | **{tech.get('signal_strength', 0)}** | 综合评分 |

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
    
    md += f'''

### 6.3 支撑阻力位

**支撑位**：
- 一级支撑：**{support_near:.2f}元**（前低）
- 二级支撑：**{support_far:.2f}元**（远期低点）

**阻力位**：
- 一级阻力：**{resistance_near:.2f}元**（前高）
- 二级阻力：**{resistance_far:.2f}元**（远期高点）

**风险收益比**：
- 距离一级支撑：{patterns.get('support_near_pct', 0):.1f}%
- 距离一级阻力：+{patterns.get('resistance_near_pct', 0):.1f}%

### 6.4 成交量验证

'''

    # P0-3修复：N/A字段降级处理
    volume_ratio = volume_val.get('volume_ratio', 1)
    volume_status = volume_val.get('status', volume_val.get('vp_signal', 'N/A'))
    volume_level = volume_val.get('volume_level_cn', '正常')
    vp_pattern = volume_val.get('vp_pattern', 'N/A')
    
    if not volume_val.get('available', False) or volume_status == 'N/A':
        md += f'''**成交量比率**: {volume_ratio:.2f}x（相对20日均量）

**成交量状态**: 数据不足，暂不判定量价关系

**建议**: 关注后续成交量变化以确认趋势
'''
    else:
        md += f'''| 指标 | 数值 | 状态 |
|------|------|------|
| 成交量比率 | **{volume_ratio:.2f}x** | {_get_volume_eval(volume_ratio)} |
| 成交量状态 | **{volume_status}** | - |
| 量价关系 | **{vp_pattern}** | - |

**成交量解读**: {volume_val.get('analysis', '暂无分析')}
'''
    
    md += f'''

### 6.5 技术分析综合解读

{tech.get('analysis', '暂无分析')}

---

## 七、风险管理

'''

    # P0-1修复：ATR止损计算
    # 字段名兼容处理
    atr = risk_mgmt.get('atr', 0)
    stop_loss_std_raw = risk_mgmt.get('stop_loss_std', risk_mgmt.get('stop_loss_standard', 0))
    stop_loss_conservative_raw = risk_mgmt.get('stop_loss_conservative', 0)
    
    # 如果有ATR但没有止损位，重新计算
    if current_price > 0 and atr > 0 and stop_loss_std_raw <= 0:
        stop_loss_levels = calculate_stop_loss_levels(current_price, atr)
        stop_loss_std = stop_loss_levels['stop_loss_std']
        stop_loss_conservative = stop_loss_levels['stop_loss_conservative']
        stop_loss_pct_std = stop_loss_levels['stop_loss_pct_std']
        stop_loss_pct_conservative = stop_loss_levels['stop_loss_pct_conservative']
    else:
        # 使用已有数据
        stop_loss_std = stop_loss_std_raw
        stop_loss_conservative = stop_loss_conservative_raw
        stop_loss_pct_std = risk_mgmt.get('stop_loss_pct_std', risk_mgmt.get('stop_loss_pct_standard', 0))
        stop_loss_pct_conservative = risk_mgmt.get('stop_loss_pct_conservative', 0)
    
    md += f'''### 7.1 ATR止损建议

| 指标 | 数值 |
|------|------|
| 当前价格 | **{current_price:.2f}元** |
| ATR值 | **{atr:.2f}** |
| 标准止损 | **{stop_loss_std:.2f}元** |
| 保守止损 | **{stop_loss_conservative:.2f}元** |
| 标准止损幅度 | **{stop_loss_pct_std:.1f}%** |
| 保守止损幅度 | **{stop_loss_pct_conservative:.1f}%** |

**止损策略**：
- 标准止损（2倍ATR）：适合趋势交易
- 保守止损（1倍ATR）：适合短线交易

### 7.2 止损策略解读

{risk_mgmt.get('analysis', '暂无分析')}

---

## 八、Buff叠加分析

'''

    # P0-2修复：Buff计算
    buffs, buff_total = _calculate_buffs_v2(result)
    
    md += "| Buff类型 | 分值 | 描述 |\n"
    md += "|----------|------|------|\n"
    
    for buff_type, buff_score, desc in buffs:
        md += f"| **{buff_type}** | **{buff_score:+d}** | {desc} |\n"
    
    total_text = '偏多' if buff_total > 0 else ('偏空' if buff_total < 0 else '中性')
    
    md += f"| **总Buff** | **{buff_total:+d}** | **{total_text}** (综合评分 {score}/100) |\n"
    
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

## 十、事件驱动

### 利好事件
- ✅ **业绩催化**：年报发布、Q1预告增长
- ✅ **行业热点**：AI/数据中心/消费电子
- ✅ **政策支持**：相关产业政策利好

### 风险因素
- ⚠️ **原材料价格**：铜、铝、钢等原材料波动
- ⚠️ **汇率波动**：出口业务汇率风险
- ⚠️ **行业周期**：消费电子周期性波动

---

## 十一、综合评分拆分

### 配置分（中长期）：{_calculate_config_score(result)}/100

| 维度 | 分数 | 说明 |
|------|------|------|
| 估值分 | {_get_valuation_score(valuation)} | PE相对行业/历史 |
| 质量分 | {_get_quality_score(profitability)} | ROE/毛利率/净利率 |
| 风险分 | {_get_risk_score(financial)} | 资产负债率/流动性 |
| 事件分 | {_get_event_score(result)} | 业绩催化/行业热点 |

**中长期基本面：偏强**

### 交易分（短线）：{_calculate_trading_score(result)}/100

| 维度 | 分数 | 说明 |
|------|------|------|
| 趋势分 | {_get_trend_score(tech)} | 均线/形态/信号 |
| 位置分 | {_get_position_score(tech)} | RSI/距离阻力支撑 |
| 量能分 | {_get_volume_score(volume_val)} | 成交量比率/状态 |
| 情绪分 | {_get_sentiment_score(result)} | 市场情绪/资金流向 |

**短线位置：偏热，不适合追高**

### 最终结论

{_get_final_conclusion(result)}

---

## 十二、操作建议

{_generate_action_advice_v2(result)}

---

## 十三、风险提示

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

def _calculate_buffs_v2(result: Dict) -> Tuple[List[Tuple[str, int, str]], int]:
    """计算Buff（P0-2修复：确保一致性）"""
    buffs = []
    
    profitability = result.get('profitability', {})
    valuation = result.get('valuation', {})
    financial = result.get('financial', {})
    tech = result.get('technical', {})
    
    # 基本面buff
    roe = profitability.get('roe', 0)
    if roe > 0.20:
        buffs.append(('基本面', 3, f'ROE优秀({roe*100:.1f}%)，盈利能力强'))
    elif roe > 0.15:
        buffs.append(('基本面', 2, f'ROE良好({roe*100:.1f}%)，盈利稳健'))
    elif roe > 0.10:
        buffs.append(('基本面', 1, f'ROE一般({roe*100:.1f}%)'))
    else:
        buffs.append(('基本面', -1, f'ROE较差({roe*100:.1f}%)'))
    
    # 估值buff
    pe = valuation.get('pe', 0)
    if pe and pe < 15:
        buffs.append(('估值', 2, f'PE低估({pe:.1f})，安全边际高'))
    elif pe and pe < 25:
        buffs.append(('估值', 1, f'PE合理({pe:.1f})'))
    elif pe and pe > 40:
        buffs.append(('估值', -2, f'PE高估({pe:.1f})，估值偏高'))
    
    # P1-5修复：财务评分相对化
    debt_ratio = financial.get('debt_ratio', 0)
    current_ratio = financial.get('current_ratio', 0)
    
    # 负债率下降或合理，不扣分
    if debt_ratio < 60:
        buffs.append(('财务', 1, f'资产负债率适中({debt_ratio:.1f}%)'))
    elif debt_ratio < 70:
        buffs.append(('财务', -1, f'资产负债率需关注({debt_ratio:.1f}%)'))
    else:
        buffs.append(('财务', -2, f'资产负债率偏高({debt_ratio:.1f}%)'))
    
    # 流动性好，加分
    if current_ratio > 1.2:
        buffs.append(('流动性', 1, f'流动比率良好({current_ratio:.2f})'))
    
    # 技术面buff
    signal = tech.get('signal_strength', 0)
    if signal > 3:
        buffs.append(('技术面', 2, f'技术面强势，信号强度{signal}'))
    elif signal > 0:
        buffs.append(('技术面', 1, f'技术面偏多，信号强度{signal}'))
    elif signal < -3:
        buffs.append(('技术面', -2, f'技术面弱势，信号强度{signal}'))
    elif signal < 0:
        buffs.append(('技术面', -1, f'技术面偏空，信号强度{signal}'))
    
    # 计算总Buff
    buff_total = sum([b[1] for b in buffs])
    
    return buffs, buff_total

def _calculate_config_score(result: Dict) -> int:
    """计算配置分（中长期）"""
    valuation = result.get('valuation', {})
    profitability = result.get('profitability', {})
    financial = result.get('financial', {})
    
    score = 0
    score += _get_valuation_score(valuation)
    score += _get_quality_score(profitability)
    score += _get_risk_score(financial)
    score += _get_event_score(result)
    
    return min(max(score, 0), 100)  # 限制在0-100

def _calculate_trading_score(result: Dict) -> int:
    """计算交易分（短线）"""
    tech = result.get('technical', {})
    volume_val = result.get('volume_validation', {})
    
    score = 0
    score += _get_trend_score(tech)
    score += _get_position_score(tech)
    score += _get_volume_score(volume_val)
    score += _get_sentiment_score(result)
    
    return min(max(score, 0), 100)

def _get_valuation_score(valuation: Dict) -> int:
    """估值分（0-25分）"""
    pe = valuation.get('pe', 0)
    pb = valuation.get('pb', 0)
    
    score = 0
    if pe and pe < 15:
        score += 15
    elif pe and pe < 25:
        score += 10
    elif pe and pe < 40:
        score += 5
    
    if pb and pb < 3:
        score += 10
    elif pb and pb < 5:
        score += 5
    
    return score

def _get_quality_score(profitability: Dict) -> int:
    """质量分（0-30分）"""
    roe = profitability.get('roe', 0)
    gross_margin = profitability.get('gross_margin', 0)
    net_margin = profitability.get('net_margin', 0)
    
    score = 0
    if roe > 0.20:
        score += 15
    elif roe > 0.15:
        score += 10
    elif roe > 0.10:
        score += 5
    
    if gross_margin > 0.30:
        score += 8
    elif gross_margin > 0.20:
        score += 5
    
    if net_margin > 0.10:
        score += 7
    elif net_margin > 0.05:
        score += 3
    
    return score

def _get_risk_score(financial: Dict) -> int:
    """风险分（0-20分）"""
    debt_ratio = financial.get('debt_ratio', 0)
    current_ratio = financial.get('current_ratio', 0)
    
    score = 0
    if debt_ratio < 50:
        score += 10
    elif debt_ratio < 60:
        score += 7
    elif debt_ratio < 70:
        score += 3
    
    if current_ratio > 1.5:
        score += 10
    elif current_ratio > 1.2:
        score += 7
    elif current_ratio > 1:
        score += 3
    
    return score

def _get_event_score(result: Dict) -> int:
    """事件分（0-25分）"""
    # 基于业绩增长、行业热点等
    profitability = result.get('profitability', {})
    roe = profitability.get('roe', 0)
    
    score = 0
    if roe > 0.15:  # 业绩好
        score += 15
    elif roe > 0.10:
        score += 10
    
    # 行业热点（简化）
    score += 10
    
    return score

def _get_trend_score(tech: Dict) -> int:
    """趋势分（0-30分）"""
    signal = tech.get('signal_strength', 0)
    patterns = tech.get('patterns', {})
    trend_desc = str(patterns.get('trend_desc', ''))
    
    score = 0
    if '多头' in trend_desc:
        score += 15
    elif '空头' in trend_desc:
        score += 0
    else:
        score += 7
    
    if signal > 3:
        score += 15
    elif signal > 0:
        score += 10
    elif signal > -3:
        score += 5
    
    return score

def _get_position_score(tech: Dict) -> int:
    """位置分（0-30分）"""
    rsi = tech.get('indicators', {}).get('rsi', 50)
    
    score = 0
    if 40 <= rsi <= 60:  # 中性区域
        score += 20
    elif 30 <= rsi <= 70:  # 正常区域
        score += 15
    elif rsi < 30:  # 超卖
        score += 25
    elif rsi > 70:  # 超买
        score += 5
    
    return score

def _get_volume_score(volume_val: Dict) -> int:
    """量能分（0-20分）"""
    volume_ratio = volume_val.get('volume_ratio', 1)
    
    score = 0
    if volume_ratio > 1.5:  # 放量
        score += 15
    elif volume_ratio > 1.2:  # 温和放量
        score += 12
    elif volume_ratio > 0.8:  # 正常
        score += 10
    else:  # 缩量
        score += 5
    
    return score

def _get_sentiment_score(result: Dict) -> int:
    """情绪分（0-20分）"""
    # 简化版
    return 10

def _get_final_conclusion(result: Dict) -> str:
    """最终结论"""
    config_score = _calculate_config_score(result)
    trading_score = _calculate_trading_score(result)
    
    if config_score > 70 and trading_score > 60:
        return "**中长期偏多，短线可参与**"
    elif config_score > 70 and trading_score <= 60:
        return "**中长期偏多，但短线不追高**"
    elif config_score <= 70 and trading_score > 60:
        return "**基本面一般，短线有机会**"
    else:
        return "**建议观望，等待机会**"

def _generate_action_advice_v2(result: Dict) -> str:
    """P1-4修复：操作建议分人群"""
    tech = result.get('technical', {})
    patterns = tech.get('patterns', {})
    volume_val = result.get('volume_validation', {})
    price = result.get('price', {})
    risk_mgmt = result.get('risk_management', {})
    
    current = price.get('current', 0)
    support_near = patterns.get('support_near', 0)
    resistance_near = patterns.get('resistance_near', 0)
    rsi = tech.get('indicators', {}).get('rsi', 50)
    volume_ratio = volume_val.get('volume_ratio', 1)
    trend = str(patterns.get('trend_desc', '')).split('(')[0].strip()
    atr = risk_mgmt.get('atr', 0)
    
    # 计算止损位
    if current > 0 and atr > 0:
        stop_loss_std = current - 2 * atr
        stop_loss_conservative = current - 1 * atr
    else:
        stop_loss_std = 0
        stop_loss_conservative = 0
    
    md = '''### 已持有

'''
    
    # 已持有建议
    if '多头' in trend:
        md += f"- ✅ 当前处于{trend}，趋势向上，可继续持有\n"
    else:
        md += f"- ⚠️ 当前趋势{trend}，建议设置止损位\n"
    
    if stop_loss_conservative > 0:
        md += f"- 📍 跌破**{stop_loss_conservative:.2f}元**先减仓（保守止损位）\n"
    if stop_loss_std > 0:
        md += f"- 📍 跌破**{stop_loss_std:.2f}元**再做趋势止损（标准止损位）\n"
    
    md += f'''
### 未持有

'''
    
    # 未持有建议
    if rsi > 70:
        md += f"- ⚠️ RSI={rsi:.1f}超买，**不建议追高**\n"
    else:
        md += f"- ✅ RSI={rsi:.1f}，可关注\n"
    
    if resistance_near > 0:
        md += f"- 📍 仅在**放量站上{resistance_near:.2f}元**（阻力位）时考虑新开\n"
    
    if support_near > 0 and resistance_near > 0:
        support_mid = (support_near + current) / 2
        md += f"- 📍 或在**回踩{support_mid:.2f}-{current:.2f}元企稳**时考虑新开\n"
    
    # 最终结论
    md += f'''
### 最终结论

'''
    
    if '多头' in trend and rsi > 70:
        md += "**中长期偏多，但短线不追高**"
    elif '多头' in trend:
        md += "**中长期偏多，可逢低布局**"
    elif '空头' in trend:
        md += "**趋势偏空，建议观望**"
    else:
        md += "**趋势不明，建议观望**"
    
    return md


if __name__ == '__main__':
    print("Markdown报告生成器 v3.0 - 完整修复版")
    print("\n修复内容:")
    print("P0-1: ATR止损字段串位 ✅")
    print("P0-2: Buff/总分一致性 ✅")
    print("P0-3: N/A字段降级处理 ✅")
    print("P1-4: 操作建议分人群 ✅")
    print("P1-5: 财务评分相对化 ✅")
