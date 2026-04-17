#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外汇分析 Skill

功能:
- 汇率数据获取
- 技术分析
- 趋势判断
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, register_skill


@register_skill
class ForexAnalysisSkill(BaseSkill):
    """外汇分析 Skill"""
    
    @property
    def description(self) -> str:
        return "Forex analysis with exchange rate and technicals"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['forex']
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行分析"""
        
        try:
            import yfinance as yf
            
            symbol = input_data.symbol
            
            # 确保格式正确
            if not symbol.endswith('=X'):
                symbol += '=X'
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='30d')
            
            if len(hist) == 0:
                return self.create_error_output('No data available')
            
            # 计算技术指标
            close = hist['Close']
            ma5 = close.rolling(5).mean().iloc[-1]
            ma10 = close.rolling(10).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # 趋势判断
            current = close.iloc[-1]
            trend = 'uptrend' if current > ma20 else 'downtrend'
            
            # 变化率
            change_pct = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100)
            
            # 生成信号
            signals = self._generate_signals(trend, rsi, current, ma20)
            
            # 计算评分
            score = self._calculate_score(signals)
            
            return SkillOutput(
                skill_name=self.name,
                success=True,
                data={
                    'symbol': symbol,
                    'rate': current,
                    'change_pct': change_pct,
                    'technical': {
                        'ma5': ma5,
                        'ma10': ma10,
                        'ma20': ma20,
                        'rsi': rsi,
                        'trend': trend
                    },
                    'data_source': ['yfinance']
                },
                signals=signals,
                score=score,
                confidence=0.7,
                timestamp=hist.index[-1].isoformat(),
                data_source=['yfinance']
            )
            
        except Exception as e:
            return self.create_error_output(str(e))
    
    def _generate_signals(
        self,
        trend: str,
        rsi: float,
        current: float,
        ma20: float
    ) -> List[Dict]:
        """生成信号"""
        signals = []
        
        # 趋势信号
        if trend == 'uptrend':
            signals.append({
                'category': '趋势',
                'name': 'MA趋势',
                'signal': 'bullish',
                'strength': 3,
                'desc': '价格在MA20上方'
            })
        else:
            signals.append({
                'category': '趋势',
                'name': 'MA趋势',
                'signal': 'bearish',
                'strength': -3,
                'desc': '价格在MA20下方'
            })
        
        # RSI信号
        if rsi > 70:
            signals.append({
                'category': '动量',
                'name': 'RSI',
                'signal': 'bearish',
                'strength': -2,
                'desc': f'RSI超买 ({rsi:.1f})'
            })
        elif rsi < 30:
            signals.append({
                'category': '动量',
                'name': 'RSI',
                'signal': 'bullish',
                'strength': 2,
                'desc': f'RSI超卖 ({rsi:.1f})'
            })
        
        return signals
    
    def _calculate_score(self, signals: List[Dict]) -> int:
        """计算评分"""
        base = 50
        total_strength = sum(s['strength'] for s in signals)
        score = base + total_strength * 2
        return max(0, min(100, score))


if __name__ == '__main__':
    from skills.base_skill import SkillInput
    
    skill = ForexAnalysisSkill()
    
    print("Testing EUR/USD...")
    output = skill.execute(SkillInput(symbol='EURUSD', market='forex'))
    
    print(f"Success: {output.success}")
    print(f"Rate: {output.data.get('rate', 0):.4f}")
    print(f"Trend: {output.data.get('technical', {}).get('trend', 'unknown')}")
    print(f"Score: {output.score}/100")
