#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标解读优化模块
用于生成更专业、更有价值的技术分析
"""

from typing import Dict, List


class TechnicalAnalyzer:
    """技术指标分析器"""
    
    @staticmethod
    def analyze_comprehensive(technical: Dict, total_strength: int) -> Dict:
        """
        综合技术分析
        
        Returns:
            {
                'trend_analysis': {...},
                'momentum_analysis': {...},
                'scenario': {...},
                'timeframe': {...},
                'suggestion': str
            }
        """
        
        if not technical:
            return {}
        
        # 提取指标
        rsi = technical.get('rsi', 50)
        macd_hist = technical.get('macd_histogram', 0)
        adx = technical.get('adx', 25)
        plus_di = technical.get('plus_di', 20)
        minus_di = technical.get('minus_di', 20)
        
        # 1. 趋势分析
        trend_analysis = TechnicalAnalyzer._analyze_trend(adx, plus_di, minus_di)
        
        # 2. 动量分析
        momentum_analysis = TechnicalAnalyzer._analyze_momentum(rsi, macd_hist)
        
        # 3. 场景识别
        scenario = TechnicalAnalyzer._identify_scenario(rsi, macd_hist, adx, plus_di, minus_di)
        
        # 4. 时间维度分析
        timeframe = TechnicalAnalyzer._analyze_timeframe(rsi, adx, plus_di, minus_di)
        
        # 5. 综合建议
        suggestion = TechnicalAnalyzer._generate_suggestion(
            trend_analysis, momentum_analysis, scenario, total_strength
        )
        
        return {
            'trend_analysis': trend_analysis,
            'momentum_analysis': momentum_analysis,
            'scenario': scenario,
            'timeframe': timeframe,
            'suggestion': suggestion
        }
    
    @staticmethod
    def _analyze_trend(adx: float, plus_di: float, minus_di: float) -> Dict:
        """趋势分析"""
        
        # 趋势方向
        if plus_di > minus_di:
            direction = 'up'
            direction_text = '上涨'
            di_desc = f'+DI({plus_di:.1f}) > -DI({minus_di:.1f})，多头力量占优'
        elif minus_di > plus_di:
            direction = 'down'
            direction_text = '下跌'
            di_desc = f'-DI({minus_di:.1f}) > +DI({plus_di:.1f})，空头力量占优'
        else:
            direction = 'sideways'
            direction_text = '震荡'
            di_desc = '+DI ≈ -DI，多空平衡'
        
        # 趋势强度
        if adx > 40:
            strength = 'very_strong'
            strength_text = '极强'
            strength_desc = f'ADX={adx:.1f}，趋势极强，单边行情'
        elif adx > 25:
            strength = 'strong'
            strength_text = '强劲'
            strength_desc = f'ADX={adx:.1f}，趋势强劲，顺势交易'
        elif adx > 15:
            strength = 'moderate'
            strength_text = '中等'
            strength_desc = f'ADX={adx:.1f}，趋势中等，谨慎操作'
        else:
            strength = 'weak'
            strength_text = '弱势'
            strength_desc = f'ADX={adx:.1f}，趋势不明，震荡整理'
        
        return {
            'direction': direction,
            'direction_text': direction_text,
            'strength': strength,
            'strength_text': strength_text,
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di,
            'summary': f'{strength_text}{direction_text}趋势；{di_desc}；{strength_desc}'
        }
    
    @staticmethod
    def _analyze_momentum(rsi: float, macd_hist: float) -> Dict:
        """动量分析"""
        
        # RSI分析
        if rsi > 80:
            rsi_status = 'extreme_overbought'
            rsi_text = '极度超买'
            rsi_signal = '强烈卖出信号'
        elif rsi > 70:
            rsi_status = 'overbought'
            rsi_text = '超买'
            rsi_signal = '卖出信号，回调风险高'
        elif rsi > 60:
            rsi_status = 'strong'
            rsi_text = '强势'
            rsi_signal = '偏多，动能向上'
        elif rsi >= 40:
            rsi_status = 'neutral'
            rsi_text = '中性'
            rsi_signal = '平衡状态'
        elif rsi >= 30:
            rsi_status = 'weak'
            rsi_text = '弱势'
            rsi_signal = '偏空，动能向下'
        else:
            rsi_status = 'oversold'
            rsi_text = '超卖'
            rsi_signal = '买入信号，反弹机会'
        
        # MACD分析
        if macd_hist > 0:
            macd_signal = 'golden_cross'
            macd_text = '金叉'
            macd_desc = '动能向上，看涨信号'
        else:
            macd_signal = 'death_cross'
            macd_text = '死叉'
            macd_desc = '动能减弱，看跌信号'
        
        # 综合动量
        if rsi > 70 and macd_hist < 0:
            momentum = 'weak_bearish'
            momentum_text = '动能转弱'
        elif rsi < 30 and macd_hist > 0:
            momentum = 'strong_bullish'
            momentum_text = '动能转强'
        elif rsi > 60 and macd_hist > 0:
            momentum = 'bullish'
            momentum_text = '动能向上'
        elif rsi < 40 and macd_hist < 0:
            momentum = 'bearish'
            momentum_text = '动能向下'
        else:
            momentum = 'neutral'
            momentum_text = '动能中性'
        
        return {
            'rsi': rsi,
            'rsi_status': rsi_status,
            'rsi_text': rsi_text,
            'rsi_signal': rsi_signal,
            'macd_hist': macd_hist,
            'macd_signal': macd_signal,
            'macd_text': macd_text,
            'macd_desc': macd_desc,
            'momentum': momentum,
            'momentum_text': momentum_text,
            'summary': f'RSI {rsi:.1f} ({rsi_text})，{rsi_signal}；MACD {macd_text}，{macd_desc}'
        }
    
    @staticmethod
    def _identify_scenario(rsi: float, macd_hist: float, adx: float, 
                          plus_di: float, minus_di: float) -> Dict:
        """场景识别"""
        
        # 强势上涨场景
        if adx > 25 and plus_di > minus_di and rsi < 70 and macd_hist > 0:
            return {
                'name': '强势上涨',
                'type': 'strong_bullish',
                'confidence': 0.8,
                'suggestion': '趋势强劲，动能向上，可顺势追涨',
                'risk': 'RSI接近超买，注意回调风险',
                'position': '可加仓至50-60%',
                'stop_loss': '跌破趋势线或支撑位-3%'
            }
        
        # 弱势下跌场景
        elif adx > 25 and minus_di > plus_di and rsi > 30 and macd_hist < 0:
            return {
                'name': '弱势下跌',
                'type': 'strong_bearish',
                'confidence': 0.8,
                'suggestion': '趋势向下，动能减弱，建议观望',
                'opportunity': '等待RSI超卖(<30)或MACD金叉',
                'position': '减仓至20-30%',
                'stop_loss': '不适用'
            }
        
        # 超买回调场景
        elif rsi > 70 and macd_hist > 0:
            return {
                'name': '超买回调',
                'type': 'overbought_pullback',
                'confidence': 0.6,
                'suggestion': 'RSI超买，短期面临回调压力',
                'strategy': '但MACD金叉，建议谨慎追高，等待回调',
                'position': '轻仓或观望',
                'stop_loss': '跌破支撑位-3%'
            }
        
        # 超卖反弹场景
        elif rsi < 30 and macd_hist > 0:
            return {
                'name': '超卖反弹',
                'type': 'oversold_bounce',
                'confidence': 0.7,
                'suggestion': 'RSI超卖，存在反弹机会',
                'strategy': '配合MACD金叉，可考虑分批建仓',
                'position': '分批买入至40%',
                'stop_loss': '跌破历史低点-3%'
            }
        
        # 震荡整理场景
        elif adx < 25 and 40 <= rsi <= 60:
            return {
                'name': '震荡整理',
                'type': 'consolidation',
                'confidence': 0.5,
                'suggestion': '趋势不明，市场震荡',
                'strategy': '区间操作，高抛低吸，不追涨杀跌',
                'position': '保持30-40%',
                'stop_loss': '不适用'
            }
        
        # 默认场景
        else:
            return {
                'name': '中性观望',
                'type': 'neutral',
                'confidence': 0.4,
                'suggestion': '信号不明确，建议观望',
                'strategy': '等待更明确的趋势信号',
                'position': '轻仓或空仓',
                'stop_loss': '不适用'
            }
    
    @staticmethod
    def _analyze_timeframe(rsi: float, adx: float, 
                          plus_di: float, minus_di: float) -> Dict:
        """时间维度分析"""
        
        # 短期 (1-7日)
        if rsi > 70:
            short_term = '超买回调'
            short_desc = 'RSI超买，短期面临回调压力'
        elif rsi < 30:
            short_term = '超卖反弹'
            short_desc = 'RSI超卖，短期存在反弹机会'
        elif rsi > 60:
            short_term = '偏强'
            short_desc = 'RSI偏高，短期偏多'
        elif rsi < 40:
            short_term = '偏弱'
            short_desc = 'RSI偏低，短期偏空'
        else:
            short_term = '震荡'
            short_desc = 'RSI中性，短期震荡'
        
        # 中期 (1-4周)
        if adx > 25:
            mid_term = '趋势延续'
            mid_desc = f'ADX={adx:.1f}，中期趋势明确'
        else:
            mid_term = '震荡整理'
            mid_desc = f'ADX={adx:.1f}，中期震荡'
        
        # 长期 (1-3月)
        if plus_di > minus_di:
            long_term = '上涨趋势'
            long_desc = '+DI>-DI，长期看涨'
        elif minus_di > plus_di:
            long_term = '下跌趋势'
            long_desc = '-DI>+DI，长期看跌'
        else:
            long_term = '横盘整理'
            long_desc = '+DI≈-DI，长期横盘'
        
        return {
            'short_term': short_term,
            'short_desc': short_desc,
            'mid_term': mid_term,
            'mid_desc': mid_desc,
            'long_term': long_term,
            'long_desc': long_desc
        }
    
    @staticmethod
    def _generate_suggestion(trend: Dict, momentum: Dict, 
                           scenario: Dict, total_strength: int) -> str:
        """生成综合建议"""
        
        suggestions = []
        
        # 基于场景
        suggestions.append(f"当前处于{scenario['name']}状态，{scenario['suggestion']}")
        
        # 基于趋势和动量
        if trend['strength'] == 'strong' and momentum['momentum'] == 'bullish':
            suggestions.append("趋势强劲且动能向上，可考虑顺势操作")
        elif trend['strength'] == 'weak':
            suggestions.append("趋势不明，建议谨慎操作，等待明确信号")
        
        # 基于总强度
        if total_strength >= 10:
            suggestions.append("综合信号强烈看多，可积极布局")
        elif total_strength >= 5:
            suggestions.append("综合信号偏多，可谨慎参与")
        elif total_strength <= -10:
            suggestions.append("综合信号强烈看空，建议观望或减仓")
        elif total_strength <= -5:
            suggestions.append("综合信号偏空，建议谨慎")
        else:
            suggestions.append("综合信号不明确，建议观望")
        
        return '；'.join(suggestions)


# 测试
if __name__ == '__main__':
    # 模拟技术指标数据
    test_technical = {
        'rsi': 69.7,
        'macd_histogram': 5.2,
        'adx': 36.9,
        'plus_di': 25.3,
        'minus_di': 15.2
    }
    
    result = TechnicalAnalyzer.analyze_comprehensive(test_technical, total_strength=11)
    
    print("=" * 60)
    print("技术指标综合分析")
    print("=" * 60)
    
    print(f"\n趋势分析: {result['trend_analysis']['summary']}")
    print(f"动量分析: {result['momentum_analysis']['summary']}")
    print(f"\n场景识别: {result['scenario']['name']}")
    print(f"建议: {result['scenario']['suggestion']}")
    print(f"风险: {result['scenario'].get('risk', '无')}")
    
    print(f"\n时间维度:")
    print(f"  短期: {result['timeframe']['short_term']} - {result['timeframe']['short_desc']}")
    print(f"  中期: {result['timeframe']['mid_term']} - {result['timeframe']['mid_desc']}")
    print(f"  长期: {result['timeframe']['long_term']} - {result['timeframe']['long_desc']}")
    
    print(f"\n综合建议: {result['suggestion']}")
