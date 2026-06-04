#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
失败模式检测器 - 整合自 technical-analysis
"Failed Patterns Are Signals - A failed pattern often produces moves in the opposite direction"
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class FailedPatternDetector:
    """
    失败模式检测器
    
    来自 technical-analysis 的核心原则:
    - "Failed Patterns Are Signals"
    - "Failed breakout = breakdown setup"
    - "Failed breakdown = breakout setup"
    
    实战案例:
    - "Got chopped to pieces trading breakouts - now wait for retest and volume confirmation"
    """
    
    # 失败模式定义
    FAILED_PATTERNS = {
        'failed_breakout': {
            'name': '假突破',
            'description': '突破后快速回落',
            'reverse_action': 'sell',
            'success_rate': 0.70,
            'lookback': 5  # 检测过去5天
        },
        'failed_breakdown': {
            'name': '假跌破',
            'description': '跌破后快速反弹',
            'reverse_action': 'buy',
            'success_rate': 0.70,
            'lookback': 5
        },
        'failed_flag': {
            'name': '失败旗形',
            'description': '旗形整理后反向突破',
            'reverse_action': 'auto',  # 根据旗形方向
            'success_rate': 0.65,
            'lookback': 10
        },
        'failed_head_shoulders': {
            'name': '失败头肩顶/底',
            'description': '头肩形态未完成颈线突破',
            'reverse_action': 'auto',
            'success_rate': 0.60,
            'lookback': 20
        }
    }
    
    def detect(self, symbol: str, ohlcv: pd.DataFrame = None) -> List[Dict]:
        """
        检测失败模式
        
        Args:
            symbol: 股票代码
            ohlcv: K线数据
            
        Returns:
            [
                {
                    'pattern': 'failed_breakout',
                    'name': '假突破',
                    'detected': True,
                    'confidence': 0.7,
                    'reverse_action': 'sell',
                    'description': '...',
                    'entry_point': 265.0,
                    'stop_loss': 270.0,
                    'target': 255.0
                }
            ]
        """
        signals = []
        
        try:
            # 获取K线数据
            if ohlcv is None:
                ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is None or len(ohlcv) < 30:
                return signals
            
            # 检测各种失败模式
            signals.extend(self._detect_failed_breakout(symbol, ohlcv))
            signals.extend(self._detect_failed_breakdown(symbol, ohlcv))
            signals.extend(self._detect_failed_flag(symbol, ohlcv))
            
        except Exception as e:
            pass
        
        return signals
    
    def _get_ohlcv(self, symbol: str):
        """获取K线数据"""
        try:
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="3mo")
            else:
                import akshare as ak
                return ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        except:
            return None
    
    def _detect_failed_breakout(self, symbol: str, ohlcv: pd.DataFrame) -> List[Dict]:
        """
        检测假突破
        
        定义: 价格突破前高，但在1-3天内回落到前高以下
        
        失败模式信号: 做空
        """
        signals = []
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
            low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
            
            # 最近10日的最高点
            lookback = 10
            if len(close) < lookback + 5:
                return signals
            
            recent_high = high.iloc[-lookback-5:-5].max()
            current_price = close.iloc[-1]
            recent_high_time = high.iloc[-lookback-5:-5].idxmax()
            
            # 检查是否曾经突破
            breakout_occurred = False
            breakout_day = None
            
            for i in range(-5, 0):
                if high.iloc[i] > recent_high:
                    breakout_occurred = True
                    breakout_day = i
                    break
            
            # 如果突破了但现在已经回落
            if breakout_occurred and current_price < recent_high:
                # 计算突破失败程度
                pullback_pct = (recent_high - current_price) / recent_high * 100
                
                # 突破失败超过2%才算显著
                if pullback_pct > 2:
                    signals.append({
                        'pattern': 'failed_breakout',
                        'name': '假突破',
                        'detected': True,
                        'confidence': self.FAILED_PATTERNS['failed_breakout']['success_rate'],
                        'reverse_action': 'sell',
                        'description': f'突破{recent_high:.2f}后回落{pullback_pct:.1f}%',
                        'entry_point': round(current_price, 2),
                        'stop_loss': round(recent_high * 1.02, 2),  # 止损在突破位上方2%
                        'target': round(current_price - (recent_high - current_price) * 2, 2),
                        'risk_reward': 2.0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        except:
            pass
        
        return signals
    
    def _detect_failed_breakdown(self, symbol: str, ohlcv: pd.DataFrame) -> List[Dict]:
        """
        检测假跌破
        
        定义: 价格跌破前低，但在1-3天内反弹到前低以上
        
        失败模式信号: 做多
        """
        signals = []
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
            low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
            
            # 最近10日的最低点
            lookback = 10
            if len(close) < lookback + 5:
                return signals
            
            recent_low = low.iloc[-lookback-5:-5].min()
            current_price = close.iloc[-1]
            
            # 检查是否曾经跌破
            breakdown_occurred = False
            
            for i in range(-5, 0):
                if low.iloc[i] < recent_low:
                    breakdown_occurred = True
                    break
            
            # 如果跌破了但现在已经反弹
            if breakdown_occurred and current_price > recent_low:
                # 计算反弹程度
                bounce_pct = (current_price - recent_low) / recent_low * 100
                
                # 反弹超过2%才算显著
                if bounce_pct > 2:
                    signals.append({
                        'pattern': 'failed_breakdown',
                        'name': '假跌破',
                        'detected': True,
                        'confidence': self.FAILED_PATTERNS['failed_breakdown']['success_rate'],
                        'reverse_action': 'buy',
                        'description': f'跌破{recent_low:.2f}后反弹{bounce_pct:.1f}%',
                        'entry_point': round(current_price, 2),
                        'stop_loss': round(recent_low * 0.98, 2),  # 止损在跌破位下方2%
                        'target': round(current_price + (current_price - recent_low) * 2, 2),
                        'risk_reward': 2.0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        except:
            pass
        
        return signals
    
    def _detect_failed_flag(self, symbol: str, ohlcv: pd.DataFrame) -> List[Dict]:
        """
        检测失败旗形
        
        定义: 旗形整理后未朝预期方向突破，而是反向突破
        
        失败模式信号: 反向交易
        """
        signals = []
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
            low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
            
            if len(close) < 20:
                return signals
            
            # 简化的旗形检测
            # 检查最近10天是否在区间震荡
            recent_close = close.iloc[-10:]
            recent_high = high.iloc[-10:].max()
            recent_low = low.iloc[-10:].min()
            
            range_size = (recent_high - recent_low) / recent_low * 100
            
            # 如果区间小于5%，可能是旗形
            if range_size < 5:
                # 检查之前的趋势
                prior_trend = 'up' if close.iloc[-20] < close.iloc[-11] else 'down'
                
                # 检查突破方向
                current_price = close.iloc[-1]
                
                # 向上突破但之前是下跌趋势 = 失败旗形
                if prior_trend == 'down' and current_price > recent_high:
                    signals.append({
                        'pattern': 'failed_flag',
                        'name': '失败旗形',
                        'detected': True,
                        'confidence': self.FAILED_PATTERNS['failed_flag']['success_rate'],
                        'reverse_action': 'buy',
                        'description': '下跌旗形后向上突破',
                        'entry_point': round(current_price, 2),
                        'stop_loss': round(recent_low, 2),
                        'target': round(current_price + (recent_high - recent_low) * 2, 2),
                        'risk_reward': 2.0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # 向下突破但之前是上涨趋势 = 失败旗形
                elif prior_trend == 'up' and current_price < recent_low:
                    signals.append({
                        'pattern': 'failed_flag',
                        'name': '失败旗形',
                        'detected': True,
                        'confidence': self.FAILED_PATTERNS['failed_flag']['success_rate'],
                        'reverse_action': 'sell',
                        'description': '上涨旗形后向下突破',
                        'entry_point': round(current_price, 2),
                        'stop_loss': round(recent_high, 2),
                        'target': round(current_price - (recent_high - recent_low) * 2, 2),
                        'risk_reward': 2.0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        except:
            pass
        
        return signals
    
    def get_trading_setup(self, failed_pattern: Dict, capital: float = 100000) -> Dict:
        """
        根据失败模式生成交易设置
        
        Args:
            failed_pattern: 失败模式检测结果
            capital: 总资金
            
        Returns:
            {
                'action': 'sell',
                'entry': 265.0,
                'stop_loss': 270.0,
                'target': 255.0,
                'shares': 100,
                'risk_amount': 500.0,
                'position_value': 26500.0
            }
        """
        if not failed_pattern.get('detected'):
            return {}
        
        entry = failed_pattern.get('entry_point')
        stop_loss = failed_pattern.get('stop_loss')
        target = failed_pattern.get('target')
        action = failed_pattern.get('reverse_action')
        
        if not all([entry, stop_loss, target]):
            return {}
        
        # 计算仓位
        risk_pct = 0.02  # 2%风险
        risk_amount = capital * risk_pct
        stop_distance = abs(entry - stop_loss)
        shares = int(risk_amount / stop_distance) if stop_distance > 0 else 0
        position_value = shares * entry
        
        return {
            'action': action,
            'entry': entry,
            'stop_loss': stop_loss,
            'target': target,
            'shares': shares,
            'risk_amount': round(risk_amount, 2),
            'position_value': round(position_value, 2),
            'risk_reward_ratio': failed_pattern.get('risk_reward', 2.0),
            'confidence': failed_pattern.get('confidence', 0.7),
            'description': failed_pattern.get('description', '')
        }


def detect_failed_patterns(symbol: str, ohlcv: pd.DataFrame = None) -> List[Dict]:
    """失败模式检测入口"""
    detector = FailedPatternDetector()
    return detector.detect(symbol, ohlcv)


if __name__ == '__main__':
    # 测试示例
    signals = detect_failed_patterns('AAPL')
    
    if signals:
        print("=" * 60)
        print("失败模式检测结果")
        print("=" * 60)
        
        for signal in signals:
            print(f"\n模式: {signal['name']}")
            print(f"置信度: {signal['confidence']}")
            print(f"反向操作: {signal['reverse_action']}")
            print(f"描述: {signal['description']}")
            print(f"入场点: {signal['entry_point']}")
            print(f"止损: {signal['stop_loss']}")
            print(f"目标: {signal['target']}")
    else:
        print("未检测到失败模式")
