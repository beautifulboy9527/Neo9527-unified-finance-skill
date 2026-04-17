#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币分析 Skill

功能:
- 市场数据获取 (CoinGecko)
- 技术分析 (yfinance)
- 形态识别
- 信号生成
"""

import sys
import os
from typing import Dict, List

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, register_skill


@register_skill
class CryptoAnalysisSkill(BaseSkill):
    """加密货币分析 Skill"""
    
    @property
    def description(self) -> str:
        return "Multi-dimensional crypto analysis with K-line, patterns, and signals"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['crypto']
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行分析"""
        
        try:
            # 导入分析器
            from scripts.features.complete_crypto_analyzer import analyze_complete
            
            # 执行分析
            result = analyze_complete(input_data.symbol)
            
            # 提取数据
            conclusion = result.get('conclusion', {})
            signals = result.get('signals', [])
            market = result.get('market', {})
            technical = result.get('technical', {})
            
            # 构建 Skill 输出
            return SkillOutput(
                skill_name=self.name,
                success=True,
                data={
                    'market': {
                        'price': market.get('price', 0),
                        'change_24h': market.get('change_24h', 0),
                        'volume': market.get('volume_24h', 0),
                        'market_cap': market.get('market_cap', 0)
                    },
                    'technical': {
                        'trend': technical.get('patterns', {}).get('trend', 'unknown'),
                        'rsi': technical.get('indicators', {}).get('rsi', 0),
                        'macd': technical.get('indicators', {}).get('macd', 0)
                    },
                    'conclusion': {
                        'decision': conclusion.get('decision', 'HOLD'),
                        'narrative': conclusion.get('narrative', '')
                    }
                },
                signals=signals,
                score=conclusion.get('score', 50),
                confidence=conclusion.get('confidence', 0) / 100,
                timestamp=result.get('timestamp', ''),
                data_source=['CoinGecko', 'yfinance', 'DeFiLlama']
            )
            
        except Exception as e:
            return self.create_error_output(str(e))


if __name__ == '__main__':
    # 测试
    from skills.base_skill import SkillInput
    
    skill = CryptoAnalysisSkill()
    
    input_data = SkillInput(
        symbol='BTC-USD',
        market='crypto',
        timeframe='medium'
    )
    
    output = skill.execute(input_data)
    
    print(f"Skill: {output.skill_name}")
    print(f"Success: {output.success}")
    print(f"Score: {output.score}/100")
    print(f"Confidence: {output.confidence:.2%}")
    print(f"Signals: {len(output.signals)}")
    
    for signal in output.signals[:3]:
        print(f"  - [{signal['category']}] {signal['name']}: {signal['signal']} ({signal['strength']:+d})")
