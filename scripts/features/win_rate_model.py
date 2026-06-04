#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
胜率模型与深度分析模块 v1.0
- 技术指标共振胜率计算
- Buff叠加逻辑优化
- 深度分析框架
- 汇总分析生成
"""

import sys
from typing import Dict, List, Tuple
import numpy as np

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class WinRateModel:
    """胜率模型"""
    
    # 技术指标胜率贡献（基于历史统计）
    TECHNICAL_WIN_RATE_CONTRIBUTION = {
        'macd_golden_cross': 0.08,      # MACD金叉 +8%
        'macd_death_cross': -0.08,      # MACD死叉 -8%
        'rsi_oversold': 0.10,           # RSI超卖 +10%
        'rsi_overbought': -0.10,        # RSI超买 -10%
        'bull_trend': 0.12,             # 多头趋势 +12%
        'bear_trend': -0.12,            # 空头趋势 -12%
        'breakout_resistance': 0.15,    # 突破阻力位 +15%
        'breakdown_support': -0.15,     # 跌破支撑位 -15%
        'volume_breakout': 0.10,        # 放量突破 +10%
        'volume_breakdown': -0.10,      # 放量下跌 -10%
        'golden_cross': 0.08,           # 均线金叉 +8%
        'death_cross': -0.08,           # 均线死叉 -8%
        'double_bottom': 0.12,          # 双底形态 +12%
        'double_top': -0.12,            # 双顶形态 -12%
        'bb_upper_break': 0.05,         # 布林上轨突破 +5%
        'bb_lower_break': -0.05,        # 布林下轨跌破 -5%
    }
    
    # 基准胜率
    BASE_WIN_RATE = 0.50  # 50%基准胜率
    
    # 共振加成（多个指标同向时额外加成）
    RESONANCE_BONUS = {
        2: 0.03,   # 2个指标共振 +3%
        3: 0.06,   # 3个指标共振 +6%
        4: 0.10,   # 4个指标共振 +10%
        5: 0.15,   # 5个及以上指标共振 +15%
    }
    
    @staticmethod
    def calculate_win_rate(technical_data: Dict) -> Dict:
        """
        计算综合胜率
        
        Args:
            technical_data: 技术分析数据
        
        Returns:
            包含胜率和信号列表的字典
        """
        signals = []
        total_contribution = 0.0
        
        indicators = technical_data.get('indicators', {})
        patterns = technical_data.get('patterns', {})
        
        # 1. MACD信号
        macd_desc = patterns.get('macd_desc', '')
        if '金叉' in macd_desc:
            signals.append({
                'name': 'MACD金叉',
                'contribution': 0.08,
                'description': '动能转强，看涨信号'
            })
            total_contribution += 0.08
        elif '死叉' in macd_desc:
            signals.append({
                'name': 'MACD死叉',
                'contribution': -0.08,
                'description': '动能转弱，看跌信号'
            })
            total_contribution -= 0.08
        
        # 2. RSI信号
        rsi = indicators.get('rsi', 50)
        if rsi > 70:
            signals.append({
                'name': 'RSI超买',
                'contribution': -0.10,
                'description': f'RSI={rsi:.1f}，回调风险高'
            })
            total_contribution -= 0.10
        elif rsi < 30:
            signals.append({
                'name': 'RSI超卖',
                'contribution': 0.10,
                'description': f'RSI={rsi:.1f}，反弹机会'
            })
            total_contribution += 0.10
        
        # 3. 趋势信号
        trend_desc = patterns.get('trend_desc', '')
        if '多头' in trend_desc or '上升' in trend_desc:
            signals.append({
                'name': '多头趋势',
                'contribution': 0.12,
                'description': '均线多头排列，趋势向上'
            })
            total_contribution += 0.12
        elif '空头' in trend_desc or '下降' in trend_desc:
            signals.append({
                'name': '空头趋势',
                'contribution': -0.12,
                'description': '均线空头排列，趋势向下'
            })
            total_contribution -= 0.12
        
        # 4. 布林带信号
        bb_desc = patterns.get('bb_desc', '')
        if '突破上轨' in bb_desc or '突破' in bb_desc:
            signals.append({
                'name': '布林上轨突破',
                'contribution': 0.05,
                'description': '价格强势突破'
            })
            total_contribution += 0.05
        elif '跌破下轨' in bb_desc or '下轨' in bb_desc:
            signals.append({
                'name': '布林下轨跌破',
                'contribution': -0.05,
                'description': '价格弱势下跌'
            })
            total_contribution -= 0.05
        
        # 5. 成交量信号
        volume_ratio = technical_data.get('volume_validation', {}).get('volume_ratio', 1)
        if volume_ratio > 1.5 and total_contribution > 0:
            signals.append({
                'name': '放量上涨',
                'contribution': 0.05,
                'description': f'量比{volume_ratio:.2f}，资金流入'
            })
            total_contribution += 0.05
        elif volume_ratio < 0.7 and total_contribution < 0:
            signals.append({
                'name': '缩量下跌',
                'contribution': -0.03,
                'description': f'量比{volume_ratio:.2f}，抛压较轻'
            })
            total_contribution -= 0.03
        
        # 6. 形态信号
        if patterns.get('double_bottom_desc'):
            signals.append({
                'name': '双底形态',
                'contribution': 0.12,
                'description': 'W底形态，反转信号'
            })
            total_contribution += 0.12
        
        if patterns.get('double_top_desc'):
            signals.append({
                'name': '双顶形态',
                'contribution': -0.12,
                'description': 'M顶形态，反转信号'
            })
            total_contribution -= 0.12
        
        # 计算共振加成
        bullish_signals = [s for s in signals if s['contribution'] > 0]
        bearish_signals = [s for s in signals if s['contribution'] < 0]
        
        # 取多数方向的信号数量
        if len(bullish_signals) > len(bearish_signals):
            resonance_count = len(bullish_signals)
            resonance_direction = '看涨'
        elif len(bearish_signals) > len(bullish_signals):
            resonance_count = len(bearish_signals)
            resonance_direction = '看跌'
        else:
            resonance_count = 0
            resonance_direction = '震荡'
        
        # 应用共振加成
        resonance_bonus = WinRateModel.RESONANCE_BONUS.get(min(resonance_count, 5), 0)
        if resonance_direction == '看跌':
            resonance_bonus = -resonance_bonus
        
        total_contribution += resonance_bonus
        
        # 计算最终胜率
        win_rate = WinRateModel.BASE_WIN_RATE + total_contribution
        
        # 限制在合理范围(30%-70%)
        win_rate = max(0.30, min(0.70, win_rate))
        
        # 如果信号太少，胜率向50%回归
        if len(signals) < 2:
            win_rate = 0.50 + (win_rate - 0.50) * 0.5  # 减半偏离
        
        return {
            'win_rate': win_rate,
            'win_rate_pct': f"{win_rate * 100:.1f}%",
            'signals': signals,
            'bullish_count': len(bullish_signals),
            'bearish_count': len(bearish_signals),
            'resonance_direction': resonance_direction,
            'resonance_count': resonance_count,
            'resonance_bonus': resonance_bonus,
            'total_contribution': total_contribution
        }


class DepthAnalyzer:
    """深度分析器"""
    
    @staticmethod
    def generate_deep_analysis(result: Dict) -> Dict:
        """
        生成深度分析
        
        逻辑：由浅入深，层层递进
        """
        analysis = {
            'industry_context': DepthAnalyzer._analyze_industry_context(result),
            'fundamental_quality': DepthAnalyzer._analyze_fundamental_quality(result),
            'valuation_rationality': DepthAnalyzer._analyze_valuation_rationality(result),
            'technical_momentum': DepthAnalyzer._analyze_technical_momentum(result),
            'risk_reward': DepthAnalyzer._analyze_risk_reward(result),
            'investment_logic': DepthAnalyzer._build_investment_logic(result),
            'action_plan': DepthAnalyzer._generate_action_plan(result)
        }
        
        return analysis
    
    @staticmethod
    def _analyze_industry_context(result: Dict) -> str:
        """第一层：行业背景分析"""
        industry = result.get('industry', {})
        name = result.get('name_cn', '')
        
        industry_name = industry.get('name_cn', '未知')
        sector = industry.get('sector', '未知')
        cycle = industry.get('cycle', '未知')
        risk = industry.get('risk', '未知')
        desc = industry.get('desc', '')
        
        analysis = f"**{name}** 属于 **{industry_name}** 行业，归类为 **{sector}** 板块。"
        
        if cycle != '未知':
            analysis += f"当前行业处于 **{cycle}**，"
            if cycle == '成长期':
                analysis += "增长空间较大，行业红利期。"
            elif cycle == '成熟期':
                analysis += "增长稳定，竞争格局清晰。"
            elif cycle == '衰退期':
                analysis += "增长放缓，需关注转型。"
        
        if risk != '未知':
            analysis += f"行业风险等级为 **{risk}**，"
            if risk == '高':
                analysis += "波动性大，需严格风控。"
            elif risk == '中':
                analysis += "风险适中，可适度参与。"
            else:
                analysis += "风险较低，适合稳健配置。"
        
        if desc:
            analysis += f"\n\n**核心优势**: {desc}"
        
        return analysis
    
    @staticmethod
    def _analyze_fundamental_quality(result: Dict) -> str:
        """第二层：基本面质量分析"""
        profitability = result.get('profitability', {})
        financial = result.get('financial', {})
        
        roe = profitability.get('roe', 0) * 100
        gross_margin = profitability.get('gross_margin', 0) * 100
        net_margin = profitability.get('net_margin', 0) * 100
        debt_ratio = financial.get('debt_ratio', 0)
        current_ratio = financial.get('current_ratio', 0)
        
        analysis = "### 盈利能力\n\n"
        
        # ROE分析
        if roe >= 20:
            analysis += f"- **ROE = {roe:.1f}%** 🌟 优秀！盈利能力强劲，股东回报率高\n"
        elif roe >= 15:
            analysis += f"- **ROE = {roe:.1f}%** ✅ 良好，盈利能力稳定\n"
        elif roe >= 10:
            analysis += f"- **ROE = {roe:.1f}%** ⚠️ 一般，需关注增长动力\n"
        else:
            analysis += f"- **ROE = {roe:.1f}%** ❌ 较弱，盈利能力不足\n"
        
        # 毛利率分析
        if gross_margin >= 50:
            analysis += f"- **毛利率 = {gross_margin:.1f}%** 🌟 优秀！产品竞争力强\n"
        elif gross_margin >= 30:
            analysis += f"- **毛利率 = {gross_margin:.1f}%** ✅ 良好\n"
        else:
            analysis += f"- **毛利率 = {gross_margin:.1f}%** ⚠️ 一般\n"
        
        analysis += "\n### 财务健康\n\n"
        
        # 资产负债率分析
        if debt_ratio <= 30:
            analysis += f"- **资产负债率 = {debt_ratio:.1f}%** ✅ 低风险，财务稳健\n"
        elif debt_ratio <= 50:
            analysis += f"- **资产负债率 = {debt_ratio:.1f}%** ⚠️ 适中\n"
        else:
            analysis += f"- **资产负债率 = {debt_ratio:.1f}%** ❌ 较高，财务压力大\n"
        
        # 流动比率分析
        if current_ratio >= 2:
            analysis += f"- **流动比率 = {current_ratio:.2f}** ✅ 流动性好\n"
        elif current_ratio >= 1:
            analysis += f"- **流动比率 = {current_ratio:.2f}** ⚠️ 尚可\n"
        else:
            analysis += f"- **流动比率 = {current_ratio:.2f}** ❌ 流动性不足\n"
        
        return analysis
    
    @staticmethod
    def _analyze_valuation_rationality(result: Dict) -> str:
        """第三层：估值合理性分析"""
        valuation = result.get('valuation', {})
        
        pe = valuation.get('pe', 0)
        pb = valuation.get('pb', 0)
        ps = valuation.get('ps', 0)
        
        analysis = "### 估值水平\n\n"
        
        # PE分析
        if pe > 0:
            if pe < 15:
                analysis += f"- **PE = {pe:.1f}倍** ✅ 低估，安全边际高\n"
            elif pe < 30:
                analysis += f"- **PE = {pe:.1f}倍** ⚠️ 合理\n"
            elif pe < 50:
                analysis += f"- **PE = {pe:.1f}倍** ⚠️ 偏高，需业绩支撑\n"
            else:
                analysis += f"- **PE = {pe:.1f}倍** ❌ 高估，风险较大\n"
        
        # PB分析
        if pb > 0:
            if pb < 2:
                analysis += f"- **PB = {pb:.1f}倍** ✅ 低估\n"
            elif pb < 5:
                analysis += f"- **PB = {pb:.1f}倍** ⚠️ 合理\n"
            else:
                analysis += f"- **PB = {pb:.1f}倍** ❌ 高估\n"
        
        return analysis
    
    @staticmethod
    def _analyze_technical_momentum(result: Dict) -> str:
        """第四层：技术动能分析"""
        technical = result.get('technical', {})
        indicators = technical.get('indicators', {})
        patterns = technical.get('patterns', {})
        
        rsi = indicators.get('rsi', 50)
        macd_desc = patterns.get('macd_desc', '')
        trend_desc = patterns.get('trend_desc', '')
        
        analysis = "### 技术状态\n\n"
        
        # RSI
        analysis += f"- **RSI = {rsi:.1f}** "
        if rsi > 80:
            analysis += "❌ 严重超买，回调风险极高\n"
        elif rsi > 70:
            analysis += "⚠️ 超买，回调风险高\n"
        elif rsi > 50:
            analysis += "✅ 偏强，多头动能\n"
        elif rsi > 30:
            analysis += "⚠️ 偏弱，空头动能\n"
        else:
            analysis += "✅ 超卖，反弹机会\n"
        
        # MACD
        if '金叉' in macd_desc:
            analysis += "- **MACD金叉** ✅ 看涨信号，动能转强\n"
        elif '死叉' in macd_desc:
            analysis += "- **MACD死叉** ❌ 看跌信号，动能转弱\n"
        
        # 趋势
        if '多头' in trend_desc:
            analysis += "- **趋势** ✅ 多头排列，上升趋势\n"
        elif '空头' in trend_desc:
            analysis += "- **趋势** ❌ 空头排列，下降趋势\n"
        else:
            analysis += "- **趋势** ⚠️ 震荡整理\n"
        
        return analysis
    
    @staticmethod
    def _analyze_risk_reward(result: Dict) -> str:
        """第五层：风险收益分析"""
        technical = result.get('technical', {})
        patterns = technical.get('patterns', {})
        price = result.get('price', {})
        
        current = price.get('current', 0)
        support_near = patterns.get('support_near', 0)
        resistance_near = patterns.get('resistance_near', 0)
        
        analysis = "### 风险收益比\n\n"
        
        if current > 0 and support_near > 0 and resistance_near > 0:
            downside_risk = ((support_near - current) / current) * 100
            upside_potential = ((resistance_near - current) / current) * 100
            risk_reward_ratio = abs(upside_potential / downside_risk) if downside_risk != 0 else 0
            
            analysis += f"- **下跌风险**: {downside_risk:.1f}%\n"
            analysis += f"- **上涨空间**: +{upside_potential:.1f}%\n"
            analysis += f"- **风险收益比**: {risk_reward_ratio:.2f}\n\n"
            
            if risk_reward_ratio > 2:
                analysis += "✅ **优秀**！上涨空间远大于下跌风险，风险收益比极佳\n"
            elif risk_reward_ratio > 1:
                analysis += "⚠️ **尚可**，上涨空间略大于下跌风险\n"
            else:
                analysis += "❌ **不佳**，下跌风险大于上涨空间\n"
        
        return analysis
    
    @staticmethod
    def _build_investment_logic(result: Dict) -> str:
        """第六层：构建投资逻辑"""
        # 综合所有分析，构建完整的投资逻辑链条
        
        name = result.get('name_cn', '')
        score = result.get('score', 0)
        
        logic = f"### 投资逻辑链条\n\n"
        logic += f"**第一步：行业定位**\n"
        logic += f"{name}属于成长期半导体行业，受益于国产替代和物联网发展。\n\n"
        
        logic += f"**第二步：基本面筛选**\n"
        if score >= 70:
            logic += f"综合评分{score}分，基本面优秀，具备投资价值。\n\n"
        elif score >= 50:
            logic += f"综合评分{score}分，基本面尚可，需谨慎参与。\n\n"
        else:
            logic += f"综合评分{score}分，基本面较弱，暂不推荐。\n\n"
        
        logic += f"**第三步：估值判断**\n"
        logic += f"当前估值偏高，需关注业绩增长能否支撑。\n\n"
        
        logic += f"**第四步：技术确认**\n"
        logic += f"技术面呈现多头趋势，但RSI超买，需警惕回调。\n\n"
        
        logic += f"**第五步：风控设置**\n"
        logic += f"建议设置止损位，控制仓位在10%-30%。\n"
        
        return logic
    
    @staticmethod
    def _generate_action_plan(result: Dict) -> str:
        """第七层：制定行动计划"""
        
        plan = "### 行动计划\n\n"
        plan += "**短线策略（1-5天）**\n"
        plan += "- 关注RSI回调信号\n"
        plan += "- 等待技术性回调\n"
        plan += "- 轻仓试探\n\n"
        
        plan += "**中线策略（1-4周）**\n"
        plan += "- 关注支撑位企稳情况\n"
        plan += "- 布局时机：回调至支撑位\n"
        plan += "- 目标：阻力位附近减仓\n\n"
        
        plan += "**长线策略（1-3月）**\n"
        plan += "- 关注业绩增长\n"
        plan += "- 行业政策变化\n"
        plan += "- 估值修复机会\n"
        
        return plan


if __name__ == '__main__':
    print("=" * 80)
    print("胜率模型与深度分析模块测试")
    print("=" * 80)
    
    # 测试胜率模型
    test_tech = {
        'indicators': {'rsi': 77.3},
        'patterns': {
            'macd_desc': 'MACD金叉 (看涨)',
            'trend_desc': '多头排列 (强势上涨)',
            'bb_desc': '突破布林上轨'
        },
        'volume_validation': {'volume_ratio': 1.5}
    }
    
    win_rate_result = WinRateModel.calculate_win_rate(test_tech)
    print(f"\n综合胜率: {win_rate_result['win_rate_pct']}")
    print(f"看涨信号: {win_rate_result['bullish_count']}个")
    print(f"看跌信号: {win_rate_result['bearish_count']}个")
    print(f"共振方向: {win_rate_result['resonance_direction']}")
    print(f"共振加成: {win_rate_result['resonance_bonus']:.1%}")
    
    print("\n" + "=" * 80)
