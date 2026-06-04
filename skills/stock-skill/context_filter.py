#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文过滤器 - 整合自 technical-analysis
"Context Over Pattern - A pattern's meaning depends entirely on where it appears"
"""

import sys
import os
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class ContextFilter:
    """
    上下文过滤器
    
    来自 technical-analysis 的核心原则:
    - "Context Over Pattern - A pattern's meaning depends entirely on where it appears"
    - "A hammer at 200-day MA after 30% decline ≠ hammer in middle of range"
    """
    
    # 趋势强度阈值
    TREND_THRESHOLDS = {
        'strong_bull': 0.15,    # 60日涨幅 > 15%
        'bull': 0.05,           # 60日涨幅 > 5%
        'neutral': -0.05,       # -5% ~ 5%
        'bear': -0.15,          # 60日跌幅 > 5%
        'strong_bear': -0.15    # 60日跌幅 > 15%
    }
    
    # 关键位置
    KEY_LEVELS = {
        'ma20': 20,
        'ma50': 50,
        'ma200': 200,
        'high_52w': 252,
        'low_52w': 252
    }
    
    def filter_signal(
        self,
        symbol: str,
        signal: Dict,
        ohlcv: pd.DataFrame = None
    ) -> Dict:
        """
        根据市场上下文过滤/调整信号
        
        Args:
            symbol: 股票代码
            signal: 信号字典
            ohlcv: K线数据
            
        Returns:
            {
                'original_confidence': 0.85,
                'adjusted_confidence': 0.70,
                'context': {...},
                'adjustments': [...],
                'warnings': [...],
                'final_action': 'buy'
            }
        """
        result = {
            'symbol': symbol,
            'original_confidence': signal.get('confidence', 0.5),
            'adjusted_confidence': signal.get('confidence', 0.5),
            'context': {},
            'adjustments': [],
            'warnings': [],
            'final_action': signal.get('action', 'hold'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 获取K线数据
            if ohlcv is None:
                ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is None or ohlcv.empty:
                result['warnings'].append('无法获取市场上下文数据')
                return result
            
            # 分析上下文
            context = self._analyze_context(ohlcv)
            result['context'] = context
            
            # 根据信号类型调整
            signal_name = signal.get('name', '').lower()
            
            # 1. RSI背离在趋势中
            if '背离' in signal_name or 'divergence' in signal_name:
                result.update(self._adjust_divergence(signal, context))
            
            # 2. 突破在关键位置
            elif '突破' in signal_name or 'breakout' in signal_name:
                result.update(self._adjust_breakout(signal, context))
            
            # 3. 反转信号
            elif '反转' in signal_name or 'reversal' in signal_name:
                result.update(self._adjust_reversal(signal, context))
            
            # 4. 趋势信号
            elif '趋势' in signal_name or 'trend' in signal_name:
                result.update(self._adjust_trend(signal, context))
            
            # 5. 一般信号
            else:
                result.update(self._adjust_general(signal, context))
        
        except Exception as e:
            result['warnings'].append(f'上下文过滤异常: {str(e)}')
        
        # 确保置信度在合理范围
        result['adjusted_confidence'] = max(0.1, min(1.0, result['adjusted_confidence']))
        
        # 根据调整后的置信度确定最终操作
        if result['adjusted_confidence'] >= 0.7:
            result['final_action'] = 'buy'
        elif result['adjusted_confidence'] >= 0.5:
            result['final_action'] = 'watch'
        elif result['adjusted_confidence'] >= 0.3:
            result['final_action'] = 'hold'
        else:
            result['final_action'] = 'avoid'
        
        return result
    
    def _get_ohlcv(self, symbol: str):
        """获取K线数据"""
        try:
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="1y")
            else:
                import akshare as ak
                return ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        except:
            return None
    
    def _analyze_context(self, ohlcv: pd.DataFrame) -> Dict:
        """分析市场上下文"""
        close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
        high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
        low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
        
        context = {
            'trend': 'neutral',
            'trend_strength': 'medium',
            'at_key_level': False,
            'key_levels': {},
            'position_in_range': 'middle'
        }
        
        # 1. 趋势判断 (60日)
        if len(close) >= 60:
            change_60d = (close.iloc[-1] - close.iloc[-60]) / close.iloc[-60]
            
            if change_60d >= self.TREND_THRESHOLDS['strong_bull']:
                context['trend'] = 'strong_bull'
                context['trend_strength'] = 'strong'
            elif change_60d >= self.TREND_THRESHOLDS['bull']:
                context['trend'] = 'bull'
                context['trend_strength'] = 'medium'
            elif change_60d <= self.TREND_THRESHOLDS['strong_bear']:
                context['trend'] = 'strong_bear'
                context['trend_strength'] = 'strong'
            elif change_60d <= self.TREND_THRESHOLDS['bear']:
                context['trend'] = 'bear'
                context['trend_strength'] = 'medium'
            else:
                context['trend'] = 'neutral'
                context['trend_strength'] = 'weak'
            
            context['change_60d'] = round(change_60d * 100, 2)
        
        # 2. 关键位置
        # MA20
        if len(close) >= 20:
            ma20 = close.rolling(20).mean().iloc[-1]
            context['key_levels']['ma20'] = round(ma20, 2)
            if abs(close.iloc[-1] - ma20) / ma20 < 0.02:  # 2%以内
                context['at_key_level'] = True
                context['key_level'] = 'ma20'
        
        # MA50
        if len(close) >= 50:
            ma50 = close.rolling(50).mean().iloc[-1]
            context['key_levels']['ma50'] = round(ma50, 2)
            if abs(close.iloc[-1] - ma50) / ma50 < 0.02:
                context['at_key_level'] = True
                context['key_level'] = 'ma50'
        
        # MA200
        if len(close) >= 200:
            ma200 = close.rolling(200).mean().iloc[-1]
            context['key_levels']['ma200'] = round(ma200, 2)
            if abs(close.iloc[-1] - ma200) / ma200 < 0.02:
                context['at_key_level'] = True
                context['key_level'] = 'ma200'
        
        # 52周高低点
        if len(high) >= 252:
            high_52w = high.iloc[-252:].max()
            low_52w = low.iloc[-252:].min()
            
            context['key_levels']['high_52w'] = round(high_52w, 2)
            context['key_levels']['low_52w'] = round(low_52w, 2)
            
            if abs(close.iloc[-1] - high_52w) / high_52w < 0.03:
                context['at_key_level'] = True
                context['key_level'] = 'high_52w'
            elif abs(close.iloc[-1] - low_52w) / low_52w < 0.03:
                context['at_key_level'] = True
                context['key_level'] = 'low_52w'
        
        # 3. 在区间中的位置
        if len(high) >= 20 and len(low) >= 20:
            range_high = high.iloc[-20:].max()
            range_low = low.iloc[-20:].min()
            
            if range_high > range_low:
                position = (close.iloc[-1] - range_low) / (range_high - range_low)
                
                if position > 0.8:
                    context['position_in_range'] = 'high'
                elif position > 0.5:
                    context['position_in_range'] = 'upper_middle'
                elif position > 0.2:
                    context['position_in_range'] = 'lower_middle'
                else:
                    context['position_in_range'] = 'low'
        
        return context
    
    def _adjust_divergence(self, signal: Dict, context: Dict) -> Dict:
        """
        调整背离信号
        
        原则: "背离在强趋势中可能持续更久"
        来自案例: "Blew an account using RSI divergence in a trending market"
        """
        result = {
            'adjusted_confidence': signal.get('confidence', 0.5),
            'adjustments': [],
            'warnings': []
        }
        
        trend = context.get('trend', 'neutral')
        trend_strength = context.get('trend_strength', 'medium')
        
        # 强趋势中的背离要大幅降权
        if trend_strength == 'strong':
            adjustment = 0.4  # 降低60%
            result['adjustments'].append(f'强趋势中的背离，置信度降低至{adjustment*100:.0f}%')
            result['warnings'].append('⚠️ 强趋势中背离可能持续更久，建议等待趋势减弱')
        elif trend_strength == 'medium':
            adjustment = 0.7  # 降低30%
            result['adjustments'].append(f'中等趋势中的背离，置信度降低至{adjustment*100:.0f}%')
            result['warnings'].append('趋势中背离风险较高')
        else:
            adjustment = 1.0  # 不调整
            result['adjustments'].append('震荡市中的背离，保持原有置信度')
        
        result['adjusted_confidence'] = signal.get('confidence', 0.5) * adjustment
        
        return result
    
    def _adjust_breakout(self, signal: Dict, context: Dict) -> Dict:
        """
        调整突破信号
        
        原则: 关键位置的突破更可靠
        """
        result = {
            'adjusted_confidence': signal.get('confidence', 0.5),
            'adjustments': [],
            'warnings': []
        }
        
        at_key_level = context.get('at_key_level', False)
        trend = context.get('trend', 'neutral')
        position = context.get('position_in_range', 'middle')
        
        # 关键位置突破加权
        if at_key_level:
            result['adjusted_confidence'] *= 1.3
            result['adjustments'].append(f'关键位置({context.get("key_level")})突破，置信度+30%')
        
        # 顺势突破加权
        if trend in ['bull', 'strong_bull'] and signal.get('action') == 'buy':
            result['adjusted_confidence'] *= 1.2
            result['adjustments'].append('顺势突破，置信度+20%')
        elif trend in ['bear', 'strong_bear'] and signal.get('action') == 'buy':
            result['adjusted_confidence'] *= 0.7
            result['warnings'].append('⚠️ 逆势突破风险高')
        
        # 区间高位突破谨慎
        if position == 'high':
            result['warnings'].append('已在区间高位，突破空间有限')
        
        return result
    
    def _adjust_reversal(self, signal: Dict, context: Dict) -> Dict:
        """
        调整反转信号
        
        原则: 关键位置的反转更可靠
        """
        result = {
            'adjusted_confidence': signal.get('confidence', 0.5),
            'adjustments': [],
            'warnings': []
        }
        
        at_key_level = context.get('at_key_level', False)
        trend = context.get('trend', 'neutral')
        position = context.get('position_in_range', 'middle')
        
        # 关键位置反转加权
        if at_key_level:
            result['adjusted_confidence'] *= 1.4
            result['adjustments'].append(f'关键位置反转，置信度+40%')
        
        # 极端位置反转更可靠
        if position in ['high', 'low']:
            result['adjusted_confidence'] *= 1.2
            result['adjustments'].append(f'区间极端位置({position})反转，置信度+20%')
        
        # 强趋势中的反转要谨慎
        if trend in ['strong_bull', 'strong_bear']:
            result['adjusted_confidence'] *= 0.6
            result['warnings'].append('⚠️ 强趋势中反转风险高')
        
        return result
    
    def _adjust_trend(self, signal: Dict, context: Dict) -> Dict:
        """调整趋势信号"""
        result = {
            'adjusted_confidence': signal.get('confidence', 0.5),
            'adjustments': [],
            'warnings': []
        }
        
        trend = context.get('trend', 'neutral')
        signal_trend = signal.get('trend', 'neutral')
        
        # 趋势一致加权
        if trend == signal_trend:
            result['adjusted_confidence'] *= 1.3
            result['adjustments'].append('趋势方向一致，置信度+30%')
        elif trend != 'neutral' and signal_trend != 'neutral':
            result['adjusted_confidence'] *= 0.5
            result['warnings'].append('⚠️ 趋势方向不一致')
        
        return result
    
    def _adjust_general(self, signal: Dict, context: Dict) -> Dict:
        """一般性调整"""
        result = {
            'adjusted_confidence': signal.get('confidence', 0.5),
            'adjustments': [],
            'warnings': []
        }
        
        # 关键位置加权
        if context.get('at_key_level'):
            result['adjusted_confidence'] *= 1.15
            result['adjustments'].append('在关键位置附近')
        
        # 趋势一致加权
        trend = context.get('trend', 'neutral')
        if trend != 'neutral':
            signal_action = signal.get('action', 'hold')
            if (trend in ['bull', 'strong_bull'] and signal_action == 'buy') or \
               (trend in ['bear', 'strong_bear'] and signal_action == 'sell'):
                result['adjusted_confidence'] *= 1.1
                result['adjustments'].append('顺势操作')
        
        return result


def filter_signal_context(symbol: str, signal: Dict, ohlcv: pd.DataFrame = None) -> Dict:
    """上下文过滤入口"""
    filter_obj = ContextFilter()
    return filter_obj.filter_signal(symbol, signal, ohlcv)


if __name__ == '__main__':
    # 测试示例
    test_signal = {
        'signal': 'rsi_divergence',
        'name': 'RSI背离',
        'action': 'watch',
        'confidence': 0.6
    }
    
    result = filter_signal_context('AAPL', test_signal)
    
    print("=" * 60)
    print("上下文过滤结果")
    print("=" * 60)
    print(f"股票: {result['symbol']}")
    print(f"趋势: {result['context'].get('trend', 'N/A')}")
    print(f"趋势强度: {result['context'].get('trend_strength', 'N/A')}")
    print(f"在关键位置: {result['context'].get('at_key_level', False)}")
    print(f"原始置信度: {result['original_confidence']}")
    print(f"调整后置信度: {result['adjusted_confidence']}")
    print(f"最终操作: {result['final_action']}")
    print(f"调整: {result['adjustments']}")
    print(f"警告: {result['warnings']}")
