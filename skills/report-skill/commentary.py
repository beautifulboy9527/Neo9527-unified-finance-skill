#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Commentary Skill

功能:
- 专业分析师语言生成
- 多因子总结
- 风险提示语言
- 让报告"活起来"
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, SkillRegistry, register_skill


@register_skill
class AICommentarySkill(BaseSkill):
    """AI 解读 Skill"""
    
    @property
    def description(self) -> str:
        return "Professional analyst commentary generation"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['crypto', 'stock', 'forex']
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """生成专业解读"""
        
        try:
            if input_data.market != 'crypto':
                return self._execute_generic_commentary(input_data)
            
            # 导入分析器
            from scripts.features.complete_crypto_analyzer import analyze_complete
            
            # 执行分析
            result = analyze_complete(input_data.symbol)
            
            technical = result.get('technical', {})
            patterns = technical.get('patterns', {})
            indicators = technical.get('indicators', {})
            conclusion = result.get('conclusion', {})
            
            # 生成解读
            commentary = {
                'title': self._generate_title(result),
                'technical_summary': self._generate_technical_summary(patterns, indicators),
                'risk_warning': self._generate_risk_warning(patterns, indicators),
                'action_advice': self._generate_action_advice(conclusion),
                'one_sentence': self._generate_one_sentence(result)
            }
            
            return SkillOutput(
                skill_name=self.name,
                success=True,
                data=commentary,
                signals=[],
                score=conclusion.get('score', 50),
                confidence=conclusion.get('confidence', 0) / 100,
                timestamp=result.get('timestamp', ''),
                data_source=['CoinGecko', 'yfinance', 'Blockchain.com', 'Rule-based commentary']
            )
            
        except Exception as e:
            return self.create_error_output(str(e))
    
    def _execute_generic_commentary(self, input_data: SkillInput) -> SkillOutput:
        """股票/外汇使用对应市场分析结果生成解读，避免套用加密分析器。"""
        skill_map = {
            'stock': 'StockAnalysisSkill',
            'forex': 'ForexAnalysisSkill',
        }
        skill_name = skill_map.get(input_data.market)
        if not skill_name:
            raise ValueError(f'Unsupported market for commentary: {input_data.market}')
        
        output = SkillRegistry.execute(skill_name, input_data)
        if not output.success:
            raise ValueError(output.error or f'{skill_name} failed')
        
        technical = output.data.get('technical', {})
        valuation = output.data.get('valuation', output.data.get('fundamentals', {}))
        score = output.score
        
        commentary = {
            'title': f"{input_data.symbol} 分析摘要 - 综合评分 {score}/100",
            'technical_summary': self._generate_generic_technical_summary(technical, output.signals),
            'risk_warning': self._generate_generic_risk_warning(output.data, output.signals),
            'action_advice': self._generate_score_based_view(score, output.confidence),
            'one_sentence': self._generate_generic_one_sentence(input_data.symbol, score, valuation)
        }
        
        return SkillOutput(
            skill_name=self.name,
            success=True,
            data=commentary,
            signals=output.signals,
            score=score,
            confidence=output.confidence,
            timestamp=output.timestamp,
            data_source=output.data_source + ['Rule-based commentary']
        )
    
    def _generate_generic_technical_summary(self, technical: Dict, signals: List[Dict]) -> str:
        trend = technical.get('trend', '未知')
        rsi = technical.get('rsi')
        parts = [f"当前趋势判断为{trend}"]
        
        if isinstance(rsi, (int, float)):
            if rsi > 70:
                parts.append(f"RSI={rsi:.1f}，短期处于偏热区间")
            elif rsi < 30:
                parts.append(f"RSI={rsi:.1f}，短期处于偏冷区间")
            else:
                parts.append(f"RSI={rsi:.1f}，动量处于中性区间")
        
        if signals:
            bullish = len([s for s in signals if self._signal_strength(s) > 0])
            bearish = len([s for s in signals if self._signal_strength(s) < 0])
            parts.append(f"已识别{bullish}项偏多信号和{bearish}项偏空信号")
        
        return "。".join(parts) + "。"
    
    def _generate_generic_risk_warning(self, data: Dict, signals: List[Dict]) -> str:
        warnings = []
        technical = data.get('technical', {})
        valuation = data.get('valuation', data.get('fundamentals', {}))
        
        rsi = technical.get('rsi')
        if isinstance(rsi, (int, float)) and rsi > 70:
            warnings.append("技术动量偏热，需防范短线回撤。")
        
        pe = valuation.get('pe')
        if isinstance(pe, (int, float)) and pe > 50:
            warnings.append("估值倍数偏高，结论对盈利增长假设较敏感。")
        
        if not warnings:
            warnings.append("未发现单一强风险信号，但仍需核对数据来源、财报口径和市场流动性。")
        
        return "".join(warnings)
    
    def _generate_score_based_view(self, score: float, confidence: float) -> str:
        confidence_pct = confidence * 100
        if score >= 65:
            return f"当前观点偏多，评分{score}/100，置信度{confidence_pct:.0f}%。适合作为进一步研究候选，需结合估值、安全边际和失效条件确认。"
        if score <= 40:
            return f"当前观点偏谨慎，评分{score}/100，置信度{confidence_pct:.0f}%。优先关注风险暴露、趋势修复和关键数据复核。"
        return f"当前观点中性，评分{score}/100，置信度{confidence_pct:.0f}%。建议等待更清晰的基本面或价格信号。"
    
    def _generate_generic_one_sentence(self, symbol: str, score: float, valuation: Dict) -> str:
        pe = valuation.get('pe')
        pe_text = f"，PE约{pe:.1f}" if isinstance(pe, (int, float)) and pe > 0 else ""
        return f"{symbol} 当前综合评分{score}/100{pe_text}，结论应结合数据质量和投资周期使用。"
    
    def _signal_strength(self, signal: Dict) -> int:
        strength = signal.get('strength', 0)
        label = str(signal.get('signal', '')).lower()
        if any(item in label for item in ['sell', 'bearish', '看跌', '强烈看跌']) and strength > 0:
            return -strength
        return strength
    
    def _generate_title(self, result: Dict) -> str:
        """生成标题"""
        symbol = result.get('symbol', 'Unknown')
        score = result.get('conclusion', {}).get('score', 50)
        decision = result.get('conclusion', {}).get('decision', 'HOLD')
        
        if score >= 70:
            return f"{symbol} 强势看多信号 - 综合评分 {score}/100"
        elif score >= 55:
            return f"{symbol} 偏多格局 - 综合评分 {score}/100"
        elif score >= 45:
            return f"{symbol} 震荡整理 - 综合评分 {score}/100"
        else:
            return f"{symbol} 偏空风险 - 综合评分 {score}/100"
    
    def _generate_technical_summary(
        self,
        patterns: Dict,
        indicators: Dict
    ) -> str:
        """生成技术面总结"""
        
        parts = []
        
        # 趋势
        trend = patterns.get('trend', 'unknown')
        trend_desc = patterns.get('trend_desc', '')
        
        if trend == 'uptrend':
            parts.append(f"趋势向上，{trend_desc}")
        elif trend == 'downtrend':
            parts.append(f"趋势向下，{trend_desc}")
        else:
            parts.append(f"震荡整理，方向不明确")
        
        # RSI
        rsi = indicators.get('rsi', 0)
        if rsi:
            if rsi > 70:
                parts.append(f"RSI达{rsi:.1f}进入超买区，短期存在回调压力")
            elif rsi > 60:
                parts.append(f"RSI为{rsi:.1f}偏强，多头动能仍在")
            elif rsi < 30:
                parts.append(f"RSI仅{rsi:.1f}超卖，可能存在反弹机会")
            else:
                parts.append(f"RSI为{rsi:.1f}中性")
        
        # MACD
        macd_trend = patterns.get('macd_signal', '')
        if macd_trend == 'bullish':
            parts.append("MACD金叉确认，动能向上")
        elif macd_trend == 'bearish':
            parts.append("MACD死叉，动能减弱")
        
        return "。".join(parts) + "。"
    
    def _generate_risk_warning(
        self,
        patterns: Dict,
        indicators: Dict
    ) -> str:
        """生成风险提示"""
        
        risks = []
        
        rsi = indicators.get('rsi', 0)
        if rsi and rsi > 70:
            risks.append(f"RSI超买风险({rsi:.1f})，若出现顶背离需警惕高位回落")
        
        bb_position = patterns.get('bb_signal', '')
        if bb_position == 'above_upper':
            risks.append("价格突破布林上轨，短期波动率放大，注意假突破风险")
        
        trend = patterns.get('trend', '')
        if trend == 'downtrend':
            risks.append("当前下跌趋势未改变，建议等待企稳信号")
        
        if not risks:
            risks.append("当前无明显风险信号，但仍需关注市场变化")
        
        return " ".join(risks)
    
    def _generate_action_advice(self, conclusion: Dict) -> str:
        """生成操作建议"""
        
        decision = conclusion.get('decision', 'HOLD')
        score = conclusion.get('score', 50)
        confidence = conclusion.get('confidence', 0)
        
        if decision == 'BUY':
            if confidence >= 75:
                return (
                    f"综合评分{score}/100，置信度{confidence}%，观点偏多。"
                    f"适合作为进一步研究候选，需设置失效条件并控制仓位风险。"
                )
            else:
                return (
                    f"综合评分{score}/100，置信度{confidence}%，偏多信号尚需确认。"
                    f"更适合观察回调承接、成交量和关键支撑是否有效。"
                )
        elif decision == 'SELL':
            return (
                f"综合评分{score}/100，风险信号占优。"
                f"优先控制风险暴露，等待趋势或基本面信号修复。"
            )
        else:
            return (
                f"综合评分{score}/100，信号不明确。"
                f"等待更清晰的趋势、成交量或基本面确认更稳妥。"
            )
    
    def _generate_one_sentence(self, result: Dict) -> str:
        """一句话总结"""
        
        symbol = result.get('symbol', '')
        score = result.get('conclusion', {}).get('score', 50)
        decision = result.get('conclusion', {}).get('decision', 'HOLD')
        bullish = result.get('conclusion', {}).get('signals_count', {}).get('bullish', 0)
        bearish = result.get('conclusion', {}).get('signals_count', {}).get('bearish', 0)
        
        if decision == 'BUY':
            return (
                f"{symbol} 当前呈现{bullish}项看多信号 vs {bearish}项看空信号，"
                f"综合评分{score}/100，观点偏多。"
            )
        elif decision == 'SELL':
            return (
                f"{symbol} 风险信号偏多，综合评分{score}/100，建议规避。"
            )
        else:
            return (
                f"{symbol} 多空信号均衡({bullish} vs {bearish})，"
                f"综合评分{score}/100，建议观望。"
            )


if __name__ == '__main__':
    from skills.base_skill import SkillInput
    
    skill = AICommentarySkill()
    
    input_data = SkillInput(
        symbol='BTC-USD',
        market='crypto'
    )
    
    output = skill.execute(input_data)
    
    print(f"Title: {output.data['title']}")
    print(f"\nTechnical Summary:\n{output.data['technical_summary']}")
    print(f"\nRisk Warning:\n{output.data['risk_warning']}")
    print(f"\nAction Advice:\n{output.data['action_advice']}")
    print(f"\nOne Sentence:\n{output.data['one_sentence']}")
