#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析 Skill

功能:
- 自动市场检测 (A股/港股/美股)
- 技术分析 (MA/RSI/趋势)
- 基本面数据 (PE/PB/市值)
- 资金流向 (仅A股)
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import BaseSkill, SkillInput, SkillOutput, register_skill


@register_skill
class StockAnalysisSkill(BaseSkill):
    """股票分析 Skill"""
    
    @property
    def description(self) -> str:
        return "Multi-dimensional stock analysis with technicals and fundamentals"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_markets(self) -> List[str]:
        return ['stock']
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行分析"""
        
        try:
            symbol = input_data.symbol
            
            # 检测市场
            market = self._detect_market(symbol)
            
            # 获取数据
            if market == 'cn':
                data = self._analyze_cn_stock(symbol)
            elif market == 'us':
                data = self._analyze_us_stock(symbol)
            else:
                data = self._analyze_hk_stock(symbol)
            
            # 生成信号
            signals = self._generate_signals(data)
            
            # 计算评分
            score = self._calculate_score(data, signals)
            
            return SkillOutput(
                skill_name=self.name,
                success=True,
                data=data,
                signals=signals,
                score=score,
                confidence=0.7,
                timestamp=data.get('timestamp', ''),
                data_source=data.get('data_source', [])
            )
            
        except Exception as e:
            return self.create_error_output(str(e))
    
    def _detect_market(self, symbol: str) -> str:
        """检测市场类型"""
        if symbol.isdigit() and len(symbol) == 6:
            return 'cn'  # A股
        elif symbol.endswith('.HK'):
            return 'hk'  # 港股
        else:
            return 'us'  # 美股
    
    def _analyze_cn_stock(self, symbol: str) -> Dict:
        """分析A股"""
        try:
            # 尝试使用 agent-stock
            from core.quote import get_quote
            from core.technical import analyze_technical
            from core.financial import get_financial_summary, get_fundflow
            
            quote = get_quote(symbol)
            tech = analyze_technical(symbol)
            fin = get_financial_summary(symbol)
            flow = get_fundflow(symbol)
            
            return {
                'market': 'cn',
                'symbol': symbol,
                'name': quote.get('name', ''),
                'price': quote.get('price', 0),
                'change_pct': quote.get('change_pct', 0),
                'valuation': {
                    'pe': quote.get('pe', 0),
                    'pb': quote.get('pb', 0),
                    'market_cap': quote.get('market_cap', 0)
                },
                'technical': tech.get('basic_indicators', {}),
                'fundflow': flow,
                'data_source': ['agent-stock', 'akshare']
            }
            
        except Exception as e:
            # 降级到 yfinance
            return self._analyze_us_stock(symbol)
    
    def _analyze_us_stock(self, symbol: str) -> Dict:
        """分析美股"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取历史数据
            hist = ticker.history(period='30d')
            
            # 计算技术指标
            if len(hist) > 0:
                ma5 = hist['Close'].rolling(5).mean().iloc[-1]
                ma10 = hist['Close'].rolling(10).mean().iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                
                # RSI
                delta = hist['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1]))
                
                price = hist['Close'].iloc[-1]
                trend = 'uptrend' if price > ma20 else 'downtrend'
            else:
                ma5 = ma10 = ma20 = rsi = 0
                price = trend = 0
            
            return {
                'market': 'us',
                'symbol': symbol,
                'name': info.get('longName', ''),
                'price': price,
                'change_pct': info.get('regularMarketChangePercent', 0),
                'valuation': {
                    'pe': info.get('trailingPE', 0),
                    'pb': info.get('priceToBook', 0),
                    'market_cap': info.get('marketCap', 0) / 1e9  # 转换为B
                },
                'technical': {
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20,
                    'rsi': rsi,
                    'trend': trend
                },
                'data_source': ['yfinance']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_hk_stock(self, symbol: str) -> Dict:
        """分析港股"""
        return self._analyze_us_stock(symbol)
    
    def _generate_signals(self, data: Dict) -> List[Dict]:
        """生成信号"""
        signals = []
        
        technical = data.get('technical', {})
        
        # 趋势信号
        trend = technical.get('trend', '')
        if trend == 'uptrend':
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': 'bullish',
                'strength': 3,
                'desc': '上升趋势'
            })
        elif trend == 'downtrend':
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': 'bearish',
                'strength': -3,
                'desc': '下降趋势'
            })
        
        # RSI信号
        rsi = technical.get('rsi', 0)
        if rsi:
            if rsi > 70:
                signals.append({
                    'category': '动量指标',
                    'name': 'RSI',
                    'signal': 'bearish',
                    'strength': -2,
                    'desc': f'RSI超买 ({rsi:.1f})'
                })
            elif rsi < 30:
                signals.append({
                    'category': '动量指标',
                    'name': 'RSI',
                    'signal': 'bullish',
                    'strength': 2,
                    'desc': f'RSI超卖 ({rsi:.1f})'
                })
        
        return signals
    
    def _calculate_score(self, data: Dict, signals: List[Dict]) -> int:
        """计算评分"""
        base_score = 50
        
        # 信号强度
        total_strength = sum(s['strength'] for s in signals)
        
        # 估值调整
        valuation = data.get('valuation', {})
        pe = valuation.get('pe', 0)
        
        if pe and 0 < pe < 20:
            base_score += 10  # 低估值加分
        elif pe and pe > 50:
            base_score -= 10  # 高估值减分
        
        score = base_score + total_strength * 2
        
        return max(0, min(100, score))


if __name__ == '__main__':
    from skills.base_skill import SkillInput
    
    skill = StockAnalysisSkill()
    
    # 测试A股
    print("Testing A-Share (002050)...")
    output = skill.execute(SkillInput(symbol='002050', market='stock'))
    print(f"Success: {output.success}")
    print(f"Market: {output.data.get('market', 'unknown')}")
    print(f"Score: {output.score}/100")
    
    # 测试美股
    print("\nTesting US Stock (AAPL)...")
    output = skill.execute(SkillInput(symbol='AAPL', market='stock'))
    print(f"Success: {output.success}")
    print(f"Market: {output.data.get('market', 'unknown')}")
    print(f"Score: {output.score}/100")
