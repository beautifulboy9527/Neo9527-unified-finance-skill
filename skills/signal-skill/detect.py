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

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, SkillRegistry, register_skill


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
            result = self._run_analysis(input_data)
            signals = result.get('signals', [])
            score = result.get('score', 50)
            confidence_pct = result.get('confidence_pct', 50)
            technical = result.get('technical', {})
            patterns = result.get('patterns', {})
            
            # 计算总强度
            normalized_strengths = [self._normalize_strength(s) for s in signals]
            total_strength = sum(normalized_strengths)
            bullish_count = len([s for s in normalized_strengths if s > 0])
            bearish_count = len([s for s in normalized_strengths if s < 0])
            
            # 信号分级
            grade, bias = self._calculate_grade(
                total_strength,
                bullish_count,
                bearish_count,
                confidence_pct
            )
            
            # 时间维度分析
            timeframe_analysis = self._analyze_timeframe(
                technical,
                patterns
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
                score=score,
                confidence=confidence_pct / 100,
                timestamp=result.get('timestamp', ''),
                data_source=result.get('data_source', ['Multi-factor Analysis'])
            )
            
        except Exception as e:
            return self.create_error_output(str(e))
    
    def _run_analysis(self, input_data: SkillInput) -> Dict:
        """按市场调用对应分析器，避免股票/外汇误走加密逻辑。"""
        market = input_data.market
        
        if market == 'crypto':
            from scripts.features.complete_crypto_analyzer import analyze_complete
            
            result = analyze_complete(input_data.symbol)
            conclusion = result.get('conclusion', {})
            return {
                'signals': result.get('signals', []),
                'score': conclusion.get('score', 50),
                'confidence_pct': conclusion.get('confidence', 50),
                'technical': result.get('technical', {}),
                'patterns': result.get('patterns', {}),
                'timestamp': result.get('timestamp', ''),
                'data_source': ['CoinGecko', 'yfinance', 'Blockchain.com']
            }
        
        skill_map = {
            'stock': 'StockAnalysisSkill',
            'forex': 'ForexAnalysisSkill',
        }
        skill_name = skill_map.get(market)
        if not skill_name:
            raise ValueError(f'Unsupported market for signal detection: {market}')
        
        output = SkillRegistry.execute(skill_name, input_data)
        if not output.success:
            raise ValueError(output.error or f'{skill_name} failed')
        
        return {
            'signals': output.signals,
            'score': output.score,
            'confidence_pct': output.confidence * 100,
            'technical': output.data.get('technical', {}),
            'patterns': output.data.get('patterns', {}),
            'timestamp': output.timestamp,
            'data_source': output.data_source
        }
    
    def _normalize_strength(self, signal: Dict) -> int:
        """统一不同模块的多空强度符号。"""
        strength = signal.get('strength', 0)
        label = str(signal.get('signal', '')).lower()
        bearish_labels = ['sell', 'bearish', '看跌', '强烈看跌', '死叉', '规避']
        
        if any(item in label for item in bearish_labels) and strength > 0:
            return -strength
        
        return strength
    
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
        indicators = technical.get('indicators', technical)
        pattern_data = patterns or technical.get('patterns', {})
        
        rsi = indicators.get('rsi', 50)
        if rsi:
            timeframe_signals['short']['signals'].append({
                'indicator': 'RSI',
                'value': rsi,
                'signal': 'overbought' if rsi > 70 else 'oversold' if rsi < 30 else 'neutral'
            })
            timeframe_signals['short']['strength'] = (70 - rsi) / 40 if 30 <= rsi <= 70 else 0
        
        # 中线 (1-3个月)
        trend = pattern_data.get('trend', indicators.get('trend', 'unknown'))
        if trend == 'uptrend':
            timeframe_signals['medium']['trend'] = 'bullish'
            timeframe_signals['medium']['strength'] = 2
        elif trend == 'downtrend':
            timeframe_signals['medium']['trend'] = 'bearish'
            timeframe_signals['medium']['strength'] = -2
        
        # 长线 (3个月+)
        # 基于 MA20 判断
        ma20 = indicators.get('ma20', 0)
        price = indicators.get('price', indicators.get('current', 0))
        
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
