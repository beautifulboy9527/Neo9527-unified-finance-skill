#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号检测 Skill

功能:
- 多因子信号检测
- 信号分级 (S/A/B/C)
- 时间维度分析
"""

import sys
import os
from typing import Dict, List
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, register_skill


class SignalGrade(Enum):
    """信号等级"""
    S = "S"  # 强买/强卖
    A = "A"  # 偏多/偏空
    B = "B"  # 观望
    C = "C"  # 风险


class SignalBias(Enum):
    """信号倾向"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@register_skill
class SignalDetectionSkill(BaseSkill):
    """信号检测 Skill"""
    
    @property
    def description(self) -> str:
        return "Multi-factor signal detection with grading system"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['crypto', 'stock', 'forex']
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行信号检测"""
        
        try:
            # 导入分析器
            from scripts.features.complete_crypto_analyzer import analyze_complete
            
            # 执行分析
            result = analyze_complete(input_data.symbol)
            
            signals = result.get('signals', [])
            conclusion = result.get('conclusion', {})
            
            # 计算总强度
            total_strength = sum(s['strength'] for s in signals)
            bullish_count = len([s for s in signals if s['strength'] > 0])
            bearish_count = len([s for s in signals if s['strength'] < 0])
            
            # 信号分级
            grade, bias = self._calculate_grade(
                total_strength,
                bullish_count,
                bearish_count,
                conclusion.get('confidence', 50)
            )
            
            # 时间维度分析
            timeframe_analysis = self._analyze_timeframe(
                result.get('technical', {}),
                result.get('patterns', {})
            )
            
            return SkillOutput(
                skill_name=self.name,
                success=True,
                data={
                    'grade': grade.value,
                    'bias': bias.value,
                    'total_strength': total_strength,
                    'bullish_count': bullish_count,
                    'bearish_count': bearish_count,
                    'timeframe': timeframe_analysis
                },
                signals=signals,
                score=conclusion.get('score', 50),
                confidence=conclusion.get('confidence', 0) / 100,
                timestamp=result.get('timestamp', ''),
                data_source=['Multi-factor Analysis']
            )
            
        except Exception as e:
            return self.create_error_output(str(e))
    
    def _calculate_grade(
        self,
        total_strength: int,
        bullish: int,
        bearish: int,
        confidence: float
    ) -> tuple:
        """
        计算信号等级
        
        S级: 总强度 >= 10 且置信度 >= 75%
        A级: 总强度 >= 5 且置信度 >= 60%
        B级: 总强度 -5 ~ 5
        C级: 总强度 <= -5 或置信度 < 40%
        """
        
        # 判断倾向
        if total_strength > 5:
            bias = SignalBias.BULLISH
        elif total_strength < -5:
            bias = SignalBias.BEARISH
        else:
            bias = SignalBias.NEUTRAL
        
        # 判断等级
        if abs(total_strength) >= 10 and confidence >= 75:
            grade = SignalGrade.S
        elif abs(total_strength) >= 5 and confidence >= 60:
            grade = SignalGrade.A
        elif abs(total_strength) <= 5:
            grade = SignalGrade.B
        else:
            grade = SignalGrade.C
        
        return grade, bias
    
    def _analyze_timeframe(
        self,
        technical: Dict,
        patterns: Dict
    ) -> Dict:
        """分析不同时间维度的信号"""
        
        timeframe_signals = {
            'short': {
                'trend': 'neutral',
                'strength': 0,
                'signals': []
            },
            'medium': {
                'trend': 'neutral',
                'strength': 0,
                'signals': []
            },
            'long': {
                'trend': 'neutral',
                'strength': 0,
                'signals': []
            }
        }
        
        # 短线 (1-7天)
        rsi = technical.get('indicators', {}).get('rsi', 50)
        if rsi:
            timeframe_signals['short']['signals'].append({
                'indicator': 'RSI',
                'value': rsi,
                'signal': 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'
            })
            timeframe_signals['short']['strength'] = (70 - rsi) / 40 if 30 <= rsi <= 70 else 0
        
        # 中线 (1-3个月)
        trend = patterns.get('trend', 'unknown')
        if trend == 'uptrend':
            timeframe_signals['medium']['trend'] = 'bullish'
            timeframe_signals['medium']['strength'] = 2
        elif trend == 'downtrend':
            timeframe_signals['medium']['trend'] = 'bearish'
            timeframe_signals['medium']['strength'] = -2
        
        # 长线 (3个月+)
        # 基于 MA20 判断
        ma20 = technical.get('indicators', {}).get('ma20', 0)
        price = technical.get('indicators', {}).get('price', 0)
        
        if ma20 and price:
            if price > ma20 * 1.1:
                timeframe_signals['long']['trend'] = 'bullish'
                timeframe_signals['long']['strength'] = 3
            elif price < ma20 * 0.9:
                timeframe_signals['long']['trend'] = 'bearish'
                timeframe_signals['long']['strength'] = -3
        
        return timeframe_signals


if __name__ == '__main__':
    from skills.base_skill import SkillInput
    
    skill = SignalDetectionSkill()
    
    input_data = SkillInput(
        symbol='BTC-USD',
        market='crypto'
    )
    
    output = skill.execute(input_data)
    
    print(f"Grade: {output.data['grade']}")
    print(f"Bias: {output.data['bias']}")
    print(f"Total Strength: {output.data['total_strength']:+d}")
    print(f"Bullish: {output.data['bullish_count']} | Bearish: {output.data['bearish_count']}")
    
    print("\nTimeframe Analysis:")
    for tf, data in output.data['timeframe'].items():
        print(f"  {tf}: {data['trend']} ({data['strength']:+d})")
