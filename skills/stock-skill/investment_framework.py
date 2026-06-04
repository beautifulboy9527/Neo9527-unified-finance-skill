#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资框架 - 基于长中短线逻辑的分析系统
不再被动堆砌数据，而是根据投资逻辑输出决策建议
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class InvestmentFramework:
    """
    投资框架 - 长中短线分层分析
    
    设计理念:
    1. 不同投资周期，分析逻辑不同
    2. 决策优先级不同
    3. 风险控制方式不同
    """
    
    # 投资周期定义
    PERIODS = {
        'long': {
            'name': '长线投资',
            'horizon': '1-3年+',
            'focus': ['基本面', '行业地位', '成长性', '护城河'],
            'signals': ['低估值', '业绩拐点', '行业龙头'],
            'stop_loss': '基本面恶化',
            'target_return': '50-200%'
        },
        'medium': {
            'name': '中线投资',
            'horizon': '1-6个月',
            'focus': ['趋势', '基本面', '资金流向'],
            'signals': ['趋势转折', '资金介入', '业绩改善'],
            'stop_loss': '趋势破坏',
            'target_return': '20-50%'
        },
        'short': {
            'name': '短线交易',
            'horizon': '数天-数周',
            'focus': ['技术面', '情绪', '资金'],
            'signals': ['技术信号', '热点概念', '资金异动'],
            'stop_loss': '技术止损',
            'target_return': '5-20%'
        }
    }
    
    def analyze(self, symbol: str, period: str = 'medium') -> Dict:
        """
        根据投资周期进行分层分析
        
        Args:
            symbol: 股票代码
            period: 投资周期 (long/medium/short)
            
        Returns:
            分析结果
        """
        result = {
            'symbol': symbol,
            'period': period,
            'period_info': self.PERIODS.get(period, self.PERIODS['medium']),
            'analysis': {},
            'decision': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 根据周期选择分析重点
        if period == 'long':
            result['analysis'] = self._analyze_long(symbol)
        elif period == 'short':
            result['analysis'] = self._analyze_short(symbol)
        else:
            result['analysis'] = self._analyze_medium(symbol)
        
        # 生成决策
        result['decision'] = self._make_decision(result['analysis'], period)
        
        return result
    
    def _analyze_long(self, symbol: str) -> Dict:
        """
        长线分析 - 基本面为主
        
        核心问题:
        1. 这家公司是否是好公司？(行业地位、护城河)
        2. 当前价格是否便宜？(估值)
        3. 未来能否持续增长？(成长性)
        """
        analysis = {
            'type': 'long',
            'focus': '基本面深度分析',
            'dimensions': {}
        }
        
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. 基本面分析 (权重 40%)
        try:
            from core.financial import get_financial_summary
            from features.enhanced_financial import get_financial_statements
            
            financial = get_financial_summary(symbol)
            analysis['dimensions']['fundamentals'] = {
                'weight': 0.40,
                'data': financial,
                'questions': [
                    '营收是否持续增长？',
                    '净利润是否稳定？',
                    'ROE是否达标？(>15%)',
                    '负债率是否健康？(<60%)'
                ],
                'key_metrics': {
                    'roe': financial.get('roe'),
                    'debt_ratio': financial.get('debt_ratio'),
                    'revenue_growth': financial.get('revenue_3y', [])
                }
            }
        except:
            pass
        
        # 2. 估值分析 (权重 30%)
        try:
            from features.valuation import get_valuation_summary
            
            valuation = get_valuation_summary(symbol)
            analysis['dimensions']['valuation'] = {
                'weight': 0.30,
                'data': valuation,
                'questions': [
                    '当前PE是否低于历史中位数？',
                    '当前PB是否合理？',
                    '股息率是否有吸引力？'
                ]
            }
        except:
            pass
        
        # 3. 行业地位 (权重 20%)
        try:
            from features.research import run_research
            
            research = run_research(symbol)
            analysis['dimensions']['industry_position'] = {
                'weight': 0.20,
                'data': research,
                'questions': [
                    '是否为行业龙头？',
                    '市场份额是否领先？',
                    '是否有护城河？'
                ]
            }
        except:
            pass
        
        # 4. 成长性 (权重 10%)
        analysis['dimensions']['growth'] = {
            'weight': 0.10,
            'questions': [
                '行业是否处于成长期？',
                '公司是否有新增长点？',
                '研发投入是否充足？'
            ]
        }
        
        return analysis
    
    def _analyze_medium(self, symbol: str) -> Dict:
        """
        中线分析 - 趋势+基本面
        
        核心问题:
        1. 当前趋势如何？(多空方向)
        2. 基本面是否支撑？(业绩支撑)
        3. 资金是否认可？(资金流向)
        """
        analysis = {
            'type': 'medium',
            'focus': '趋势+基本面分析',
            'dimensions': {}
        }
        
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. 趋势分析 (权重 50%)
        try:
            from core.technical import analyze_technical
            
            tech = analyze_technical(symbol)
            basic = tech.get('basic_indicators', {})
            ai_decision = tech.get('ai_decision', {})
            
            analysis['dimensions']['trend'] = {
                'weight': 0.50,
                'data': tech,
                'questions': [
                    f"当前趋势: {basic.get('trend', 'unknown')}",
                    f"RSI: {basic.get('rsi', 0):.1f} (是否超买超卖？)",
                    f"均线状态: {'多头排列' if basic.get('ma5', 0) > basic.get('ma20', 0) else '空头排列'}",
                    f"AI建议: {ai_decision.get('recommendation', 'hold')}"
                ],
                'key_signal': ai_decision.get('recommendation', 'hold')
            }
        except:
            pass
        
        # 2. 入场信号 (权重 30%)
        try:
            from features.entry_signals import analyze_entry_signals
            
            signals = analyze_entry_signals(symbol)
            score = signals.get('score', {})
            
            analysis['dimensions']['signals'] = {
                'weight': 0.30,
                'data': signals,
                'questions': [
                    f"信号评分: {score.get('overall_score', 0)}/100",
                    f"建议操作: {score.get('action', 'hold')}",
                    f"风险等级: {score.get('risk_level', 'unknown')}"
                ],
                'key_signal': score.get('action', 'hold')
            }
        except:
            pass
        
        # 3. 资金流向 (权重 20%)
        try:
            from core.financial import get_fundflow
            
            fundflow = get_fundflow(symbol)
            summary = fundflow.get('summary', {})
            
            analysis['dimensions']['fundflow'] = {
                'weight': 0.20,
                'data': fundflow,
                'questions': [
                    f"主力资金: {'流入' if summary.get('trend') == 'inflow' else '流出'}",
                    f"净流入: {summary.get('total_main_inflow', 0):.2f} 亿",
                    f"数据时效: {fundflow.get('warning', '正常')}"
                ],
                'warning': fundflow.get('warning')
            }
        except:
            pass
        
        return analysis
    
    def _analyze_short(self, symbol: str) -> Dict:
        """
        短线分析 - 技术面为主
        
        核心问题:
        1. 技术信号是否触发？(入场时机)
        2. 市场情绪如何？(热点概念)
        3. 资金是否异动？(主力动向)
        """
        analysis = {
            'type': 'short',
            'focus': '技术面快速分析',
            'dimensions': {}
        }
        
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. 技术信号 (权重 60%)
        try:
            from features.entry_signals import analyze_entry_signals
            from core.technical import analyze_technical
            
            signals = analyze_entry_signals(symbol)
            tech = analyze_technical(symbol)
            
            score = signals.get('score', {})
            basic = tech.get('basic_indicators', {})
            
            analysis['dimensions']['technical'] = {
                'weight': 0.60,
                'data': {'signals': signals, 'tech': tech},
                'questions': [
                    f"信号评分: {score.get('overall_score', 0)}/100",
                    f"RSI: {basic.get('rsi', 0):.1f}",
                    f"趋势: {basic.get('trend', 'unknown')}",
                    f"建议: {score.get('action', 'hold')}"
                ],
                'key_signal': score.get('action', 'hold'),
                'signal_list': [s.get('name') for s in signals.get('signals', [])]
            }
        except:
            pass
        
        # 2. 情绪分析 (权重 25%)
        try:
            from features.sentiment import analyze_sentiment
            
            sentiment = analyze_sentiment(symbol)
            
            analysis['dimensions']['sentiment'] = {
                'weight': 0.25,
                'data': sentiment,
                'questions': [
                    f"情绪: {sentiment.get('sentiment_description', '未知')}",
                    f"看涨比例: {sentiment.get('avg_bullish_pct', 0):.0f}%"
                ]
            }
        except:
            pass
        
        # 3. 风险控制 (权重 15%)
        try:
            from features.risk_management import analyze_risk
            
            risk = analyze_risk(symbol)
            summary = risk.get('summary', {})
            
            analysis['dimensions']['risk'] = {
                'weight': 0.15,
                'data': risk,
                'questions': [
                    f"入场价: {summary.get('entry_price', 'N/A')}",
                    f"止损价: {summary.get('stop_loss', 'N/A')} ({summary.get('stop_loss_pct', 0):.1f}%)",
                    f"目标价: {summary.get('target_price', 'N/A')} ({summary.get('target_return_pct', 0):.1f}%)"
                ],
                'stop_loss': summary.get('stop_loss'),
                'target': summary.get('target_price')
            }
        except:
            pass
        
        return analysis
    
    def _make_decision(self, analysis: Dict, period: str) -> Dict:
        """
        生成投资决策
        
        关键: 不是简单汇总，而是根据投资逻辑判断
        """
        decision = {
            'action': 'hold',
            'confidence': 0,
            'reasons': [],
            'risks': [],
            'plan': {}
        }
        
        dimensions = analysis.get('dimensions', {})
        
        if period == 'long':
            # 长线: 基本面优先
            fundamentals = dimensions.get('fundamentals', {})
            valuation = dimensions.get('valuation', {})
            
            # 判断逻辑
            score = 0
            reasons = []
            risks = []
            
            # ROE > 15%
            roe = fundamentals.get('key_metrics', {}).get('roe')
            if roe and roe > 15:
                score += 25
                reasons.append(f"ROE {roe}% > 15%，盈利能力强")
            elif roe:
                risks.append(f"ROE {roe}% < 15%，盈利能力待提升")
            
            # 负债率 < 60%
            debt = fundamentals.get('key_metrics', {}).get('debt_ratio')
            if debt and debt < 60:
                score += 20
                reasons.append(f"负债率 {debt}% < 60%，财务健康")
            elif debt:
                risks.append(f"负债率 {debt}% > 60%，财务风险")
            
            # 估值
            pe_level = valuation.get('data', {}).get('pe_analysis', {}).get('level')
            if pe_level in ['低估', '偏低']:
                score += 30
                reasons.append(f"PE {pe_level}，估值有吸引力")
            
            decision['confidence'] = score
            decision['reasons'] = reasons
            decision['risks'] = risks
            
            if score >= 60:
                decision['action'] = 'buy'
            elif score >= 40:
                decision['action'] = 'hold'
            else:
                decision['action'] = 'avoid'
        
        elif period == 'medium':
            # 中线: 趋势优先
            trend = dimensions.get('trend', {})
            signals = dimensions.get('signals', {})
            fundflow = dimensions.get('fundflow', {})
            
            score = 0
            reasons = []
            risks = []
            
            # 趋势判断
            key_signal = trend.get('key_signal', 'hold')
            if key_signal == 'buy':
                score += 35
                reasons.append("技术面趋势向上")
            elif key_signal == 'sell':
                risks.append("技术面趋势向下")
            
            # 信号评分
            signal_score = signals.get('key_signal', {}).get('overall_score', 0) if isinstance(signals.get('key_signal'), dict) else 0
            if signal_score >= 70:
                score += 30
                reasons.append(f"入场信号评分 {signal_score}/100")
            
            # 资金流向
            fundflow_trend = fundflow.get('data', {}).get('summary', {}).get('trend')
            if fundflow_trend == 'inflow':
                score += 20
                reasons.append("主力资金流入")
            
            decision['confidence'] = score
            decision['reasons'] = reasons
            decision['risks'] = risks
            
            if score >= 50:
                decision['action'] = 'buy'
            elif score >= 30:
                decision['action'] = 'hold'
            else:
                decision['action'] = 'avoid'
        
        else:  # short
            # 短线: 技术信号优先
            technical = dimensions.get('technical', {})
            risk = dimensions.get('risk', {})
            
            score = 0
            reasons = []
            risks = []
            
            # 信号触发
            key_signal = technical.get('key_signal', 'hold')
            signal_list = technical.get('signal_list', [])
            
            if key_signal == 'buy' and len(signal_list) > 0:
                score += 50
                reasons.append(f"已触发信号: {', '.join(signal_list)}")
            
            # 风险控制
            stop_loss = risk.get('stop_loss')
            target = risk.get('target')
            if stop_loss and target:
                score += 20
                reasons.append(f"止损/目标明确: {stop_loss} / {target}")
            
            decision['confidence'] = score
            decision['reasons'] = reasons
            decision['risks'] = risks
            
            if score >= 50:
                decision['action'] = 'buy'
            else:
                decision['action'] = 'wait'
        
        return decision


def analyze_investment(symbol: str, period: str = 'medium') -> Dict:
    """投资分析入口"""
    framework = InvestmentFramework()
    return framework.analyze(symbol, period)


if __name__ == '__main__':
    import json
    
    # 测试三种周期
    symbol = '002241'
    
    print("=" * 60)
    print("长线分析")
    print("=" * 60)
    result = analyze_investment(symbol, 'long')
    print(json.dumps(result['decision'], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("中线分析")
    print("=" * 60)
    result = analyze_investment(symbol, 'medium')
    print(json.dumps(result['decision'], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("短线分析")
    print("=" * 60)
    result = analyze_investment(symbol, 'short')
    print(json.dumps(result['decision'], indent=2, ensure_ascii=False))
