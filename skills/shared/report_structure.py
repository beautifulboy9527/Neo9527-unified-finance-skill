#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告结构优化器 v2.0
按照逻辑递进重新组织报告结构
"""

import sys
from typing import Dict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def generate_structured_report(report: Dict, enhancer) -> str:
    """
    生成结构化报告
    
    结构逻辑：
    1. 基本面 - 投资根基
    2. 估值 - 价格评估
    3. 财务健康 - 风险检查
    4. 技术分析 - 择时参考
    5. 市场情绪 - 短期风向
    6. 监管风险 - 政策环境
    7. 深度研报 - 综合研判
    8. 全局观点 - 最终建议
    """
    
    symbol = report['symbol']
    overall = report.get('overall', {})
    sections = report.get('sections', {})
    
    md = f"""# {symbol} 投资分析报告

**生成时间**: {report['timestamp']}
**投资风格**: {report['style']}

---

## 📊 综合评分

| 评分 | 建议 | 风险等级 |
|------|------|---------|
| **{overall.get('score', 0)}/100** | {overall.get('recommendation', 'N/A')} | {'🟢 低风险' if overall.get('score', 0) >= 70 else '🟡 中风险' if overall.get('score', 0) >= 50 else '🔴 高风险'} |

---

## 第一部分：基本面分析（投资根基）

> 基本面决定股票的长期价值，是投资决策的核心依据。

"""
    
    # ===== 1. 基本面分析 =====
    if 'fundamentals' in sections:
        fund = sections['fundamentals']
        pe = fund.get('pe')
        pb = fund.get('pb')
        roe = fund.get('roe')
        market_cap = fund.get('market_cap')
        
        # 格式化
        pe_str = f"{pe:.1f}" if pe else "N/A"
        pb_str = f"{pb:.2f}" if pb else "N/A"
        roe_str = f"{roe:.1f}%" if roe else "N/A"
        mc_str = enhancer.format_number(market_cap, 'market_cap') if market_cap else 'N/A'
        
        # 解读
        pe_interp = enhancer.interpret_pe(pe) if pe else None
        pb_status = '低估' if pb and pb < 3 else '合理' if pb and pb < 6 else '偏高' if pb and pb < 10 else '高估'
        roe_interp = enhancer.interpret_roe(roe) if roe else None
        
        md += f"""### 1.1 盈利能力

| 指标 | 值 | 评级 | 分析 |
|------|------|------|------|
| ROE | {roe_str} | {roe_interp['rating'] if roe_interp else 'N/A'} | {roe_interp['description'] if roe_interp else '数据缺失'} |

**解读**: {roe_interp['description'] if roe_interp else '无ROE数据，无法判断盈利能力'}

### 1.2 估值水平

| 指标 | 值 | 行业对比 | 分析 |
|------|------|---------|------|
| P/E | {pe_str} | {pe_interp['vs_industry'] if pe_interp else 'N/A'} | {pe_interp['status'] if pe_interp else '数据缺失'} |
| P/B | {pb_str} | {'低估(<3)' if pb and pb < 3 else '合理(3-6)' if pb and pb < 6 else '偏高(6-10)' if pb and pb < 10 else '高估(>10)'} | {pb_status} |
| 市值 | {mc_str} | 美元计价 | 大盘股 |

**PE分析**: {pe_interp['description'] if pe_interp else '无PE数据'}

### 1.3 基本面小结

"""
        # 基本面评分
        fund_score = 0
        if roe and roe > 15:
            fund_score += 40
            md += "- ✅ **盈利能力强**: ROE超过15%，具备优秀盈利能力\n"
        elif roe and roe > 10:
            fund_score += 25
            md += "- ⚠️ **盈利能力一般**: ROE在10-15%区间\n"
        else:
            md += "- ❌ **盈利能力弱**: ROE低于10%\n"
        
        if pe and pe < 20:
            fund_score += 30
            md += "- ✅ **估值合理**: PE低于20倍\n"
        elif pe and pe < 30:
            fund_score += 20
            md += "- ⚠️ **估值偏高**: PE在20-30倍区间\n"
        else:
            md += "- ❌ **估值过高**: PE超过30倍，风险较大\n"
        
        md += f"\n**基本面评分**: {fund_score}/70\n\n"
    
    # ===== 2. 估值分析 =====
    md += """---

## 第二部分：估值分析（价格评估）

> 估值决定买入时机，好公司也要好价格。

"""
    
    if 'valuation' in sections:
        val = sections['valuation']
        current = val.get('current_price', 0)
        fair = val.get('fair_value', 0)
        safe = val.get('safe_price', 0)
        upside = val.get('upside', 0)
        
        if upside > 0:
            val_status = f"低估 {abs(upside):.0f}%"
            val_signal = "✅ 买入机会"
        elif upside > -20:
            val_status = "合理区间"
            val_signal = "⏸️ 观望"
        elif upside > -50:
            val_status = f"高估 {abs(upside):.0f}%"
            val_signal = "⚠️ 风险较大"
        else:
            val_status = f"严重高估 {abs(upside):.0f}%"
            val_signal = "❌ 不建议买入"
        
        md += f"""### 2.1 估值模型

| 指标 | 值 | 说明 |
|------|------|------|
| 当前价格 | ${current:.2f} | 市场价格 |
| 公允价值 | ${fair:.2f} | DCF模型估值 |
| 安全价格 | ${safe:.2f} | 含安全边际 |
| 估值状态 | {val_status} | 相对公允价值 |

### 2.2 估值信号

**信号**: {val_signal}

**分析**: 当前价格${current:.2f}，公允价值${fair:.2f}，{f'存在{abs(upside):.0f}%上涨空间' if upside > 0 else f'高估{abs(upside):.0f}%，不建议追高'}

"""
    
    # ===== 3. 财务健康 =====
    md += """---

## 第三部分：财务健康（风险检查）

> 财务健康度影响企业生存能力，是风险控制的关键。

"""
    
    if 'financial_check' in sections:
        fc = sections['financial_check']
        risk_level = fc.get('risk_level', 'unknown')
        risk_desc = fc.get('risk_description', 'N/A')
        anomaly_count = fc.get('anomaly_count', 0)
        gross_margin = fc.get('gross_margin', 0)
        net_margin = fc.get('net_margin', 0)
        
        # 异常解读
        if anomaly_count == 0:
            anomaly_explain = "财务报表无异常信号"
        elif anomaly_count <= 2:
            anomaly_explain = "存在轻微财务异常，需关注"
        else:
            anomaly_explain = "存在多项财务异常，警惕风险"
        
        # 毛利率解读
        if gross_margin > 50:
            margin_status = "优秀 (>{50%)"
        elif gross_margin > 30:
            margin_status = "良好 (30-50%)"
        elif gross_margin > 15:
            margin_status = "一般 (15-30%)"
        else:
            margin_status = "较低 (<15%)"
        
        md += f"""### 3.1 异常检测

| 指标 | 值 | 分析 |
|------|------|------|
| 风险等级 | {risk_desc} | {'财务健康' if risk_level == 'low' else '需关注' if risk_level == 'medium' else '警惕风险'} |
| 异常数量 | {anomaly_count} | {anomaly_explain} |

**数据来源**: 财务报表（利润表/资产负债表）

### 3.2 盈利质量

| 指标 | 值 | 水平 |
|------|------|------|
| 毛利率 | {gross_margin:.1f}% | {margin_status} |
| 净利率 | {net_margin:.1f}% | {'优秀' if net_margin > 20 else '良好' if net_margin > 10 else '一般'} |

### 3.3 财务小结

"""
        if risk_level == 'low' and anomaly_count == 0:
            md += "- ✅ **财务健康**: 无异常信号，盈利质量良好\n"
        else:
            md += f"- ⚠️ **财务风险**: {anomaly_count}项异常需关注\n"
    
    # ===== 4. 技术分析 =====
    md += """---

## 第四部分：技术分析（择时参考）

> 技术分析辅助择时，不改变投资方向。

"""
    
    if 'technical' in sections:
        tech = sections['technical']
        trend = tech.get('trend', 'N/A')
        rsi = tech.get('rsi', 50)
        macd = tech.get('macd_status', 'N/A')
        
        rsi_interp = enhancer.interpret_rsi(rsi)
        trend_interp = enhancer.interpret_trend(trend, rsi)
        patterns = enhancer.get_technical_patterns(sections)
        
        md += f"""### 4.1 趋势判断

**趋势**: {trend}

> {trend_interp}

### 4.2 技术指标

| 指标 | 值 | 状态 | 信号 |
|------|------|------|------|
| RSI | {rsi:.1f} | {rsi_interp['color']} {rsi_interp['status']} | {rsi_interp['signal']} |
| MACD | {macd} | {'看涨' if '金叉' in macd else '看跌' if '死叉' in macd else '中性'} | {'买入' if '金叉' in macd else '卖出' if '死叉' in macd else '观望'} |

### 4.3 技术形态

"""
        if patterns:
            for p in patterns:
                md += f"- **{p['name']}**: {p['description']} ({p['signal']})\n"
        else:
            md += "- 无明显技术形态\n"
        
        md += f"""
### 4.4 技术小结

{rsi_interp['description']}。{'MACD金叉提供买入信号。' if '金叉' in macd else 'MACD死叉发出卖出信号。' if '死叉' in macd else ''}

**注意**: 技术分析仅作择时参考，投资决策应以基本面为主。

"""
    
    # ===== 5. 市场情绪 =====
    md += """---

## 第五部分：市场情绪（短期风向）

> 情绪影响短期波动，不改变长期价值。

"""
    
    if 'sentiment' in sections:
        sent = sections['sentiment']
        status = sent.get('status', 'neutral')
        description = sent.get('description', '中性')
        bullish_pct = sent.get('bullish_pct', 50)
        alignment = sent.get('alignment', 'local')
        
        # 数据来源说明
        source_map = {
            'local': '新闻标题关键词分析（本地模型）',
            'adanos': 'Adanos API（多数据源）',
            'news': '新闻情感分析'
        }
        source_desc = source_map.get(alignment, '未知来源')
        
        md += f"""### 5.1 情绪指标

| 指标 | 值 | 分析 |
|------|------|------|
| 情绪状态 | {status} | {description} |
| 看涨比例 | {bullish_pct:.0f}% | {'多头占优' if bullish_pct > 60 else '空头占优' if bullish_pct < 40 else '多空平衡'} |

**数据来源**: {source_desc}

### 5.2 情绪小结

当前市场情绪{description}，{'短期可能上涨' if status == 'positive' else '短期可能下跌' if status == 'negative' else '短期震荡为主'}。

"""
    
    # ===== 6. 监管风险 =====
    md += """---

## 第六部分：监管风险（政策环境）

> 政策风险影响行业前景，需持续关注。

"""
    
    if 'regulation' in sections:
        reg = sections['regulation']
        risk_score = reg.get('risk_score', 0)
        risk_level = reg.get('risk_level', 'unknown')
        risk_desc = reg.get('risk_description', 'N/A')
        alerts = reg.get('alerts_count', 0)
        
        # 监管来源说明
        reg_source = "CSRC(证监会)/PBOC(央行)/NFRA(金监总局)公开信息"
        
        md += f"""### 6.1 风险评估

| 指标 | 值 | 分析 |
|------|------|------|
| 风险评分 | {risk_score}/100 | {'低风险' if risk_score < 30 else '中风险' if risk_score < 60 else '高风险'} |
| 风险等级 | {risk_desc} | {'环境稳定' if risk_level == 'low' else '需关注政策变化'} |
| 监管警报 | {alerts}条 | {'无监管警报' if alerts == 0 else f'存在{alerts}条监管警报'} |

**数据来源**: {reg_source}

### 6.2 监管小结

{risk_desc}，{'可正常投资' if risk_level == 'low' else '建议关注政策动态'}。

"""
    
    # ===== 7. 深度研报 =====
    md += """---

## 第七部分：深度研报（综合研判）

> 多维度综合分析，提供深度见解。

"""
    
    if 'deep_research' in sections:
        dr = sections['deep_research']
        rating = dr.get('rating', 'N/A')
        score = dr.get('score', 0)
        recommendation = dr.get('recommendation', 'N/A')
        
        # 评级解读
        rating_desc = {
            '🟢🟢🟢🟢🟢': '强烈推荐',
            '🟢🟢🟢🟢': '推荐',
            '🟡🟡🟡': '中性',
            '🔴🔴': '谨慎',
            '🔴🔴🔴': '不推荐'
        }.get(rating, '待评估')
        
        md += f"""### 7.1 研报评级

| 指标 | 值 | 分析 |
|------|------|------|
| 评级 | {rating} | {rating_desc} |
| 评分 | {score}/5 | {'优秀' if score >= 4 else '良好' if score >= 3 else '一般' if score >= 2 else '较差'} |
| 建议 | {recommendation} | - |

### 7.2 研报小结

{recommendation}

"""
    
    # ===== 8. 全局观点 =====
    md += """---

## 第八部分：全局观点（最终建议）

> 综合各维度分析，给出投资决策建议。

"""
    
    score = overall.get('score', 0)
    
    # 综合评价
    if score >= 70:
        overall_view = "基本面优秀，估值合理，财务健康，技术面支持，适合投资"
    elif score >= 50:
        overall_view = "基本面尚可，但存在估值或风险问题，需谨慎投资"
    else:
        overall_view = "基本面较弱或估值过高，风险较大，建议观望"
    
    md += f"""### 8.1 综合评价

{overall_view}

**综合评分**: {score}/100

### 8.2 各维度评分

"""
    
    # 计算各维度评分
    weights = {
        'fundamentals': 25,
        'valuation': 25,
        'financial_check': 20,
        'technical': 15,
        'sentiment': 10,
        'regulation': 5
    }
    
    if 'fundamentals' in sections:
        fund = sections['fundamentals']
        roe = fund.get('roe', 0)
        pe = fund.get('pe', 0)
        fund_score = min(100, max(0, (roe / 2 if roe else 0) + (100 - pe if pe else 50)))
        md += f"- 基本面: {fund_score:.0f}/100 (权重25%)\n"
    
    if 'valuation' in sections:
        val = sections['valuation']
        upside = val.get('upside', 0)
        val_score = max(0, 50 + upside)
        md += f"- 估值: {val_score:.0f}/100 (权重25%)\n"
    
    if 'financial_check' in sections:
        fc = sections['financial_check']
        risk_level = fc.get('risk_level', 'medium')
        risk_score_map = {'low': 100, 'medium': 60, 'high': 30}
        fin_score = risk_score_map.get(risk_level, 50)
        md += f"- 财务健康: {fin_score}/100 (权重20%)\n"
    
    if 'technical' in sections:
        tech = sections['technical']
        rsi = tech.get('rsi', 50)
        tech_score = 100 - abs(rsi - 50)
        md += f"- 技术面: {tech_score:.0f}/100 (权重15%)\n"
    
    if 'sentiment' in sections:
        sent = sections['sentiment']
        bullish = sent.get('bullish_pct', 50)
        sent_score = bullish
        md += f"- 市场情绪: {sent_score:.0f}/100 (权重10%)\n"
    
    if 'regulation' in sections:
        reg = sections['regulation']
        reg_score = 100 - reg.get('risk_score', 50)
        md += f"- 监管环境: {reg_score}/100 (权重5%)\n"
    
    # 不同周期建议
    md += """
### 8.3 投资建议

"""
    
    short_advice = enhancer.get_investment_advice(score, 'short', sections)
    medium_advice = enhancer.get_investment_advice(score, 'medium', sections)
    long_advice = enhancer.get_investment_advice(score, 'long', sections)
    
    md += f"""**短线投资者** (日内/隔夜): {short_advice['advice']}
- 理由: {short_advice['reason']}
- 操作: {short_advice['action']}

**波段投资者** (数天-数周): {medium_advice['advice']}
- 理由: {medium_advice['reason']}
- 操作: {medium_advice['action']}

**长线投资者** (数月-数年): {long_advice['advice']}
- 理由: {long_advice['reason']}
- 操作: {long_advice['action']}

---

## ⚠️ 风险提示

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

*报告由 Neo9527 Finance Agent v6.1 生成*
"""
    
    return md


# 测试
if __name__ == '__main__':
    print("报告结构优化器测试")
    print("=" * 60)
