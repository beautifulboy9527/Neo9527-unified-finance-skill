#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格专业报告生成器 v5.0
- 多周期分析框架
- 买入/卖出完整策略
- 动态支撑阻力位
- 趋势一致性判断
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yfinance as yf
import pandas as pd
import numpy as np

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MultiTimeframeAnalyzer:
    """多周期分析器"""
    
    @staticmethod
    def get_multi_timeframe_data(symbol: str) -> Dict:
        """获取多周期K线数据"""
        print("获取多周期数据...")
        
        data = {}
        
        try:
            # 周线（6个月）
            data['weekly'] = yf.download(symbol, period='6mo', interval='1wk', progress=False)
            
            # 日线（3个月）
            data['daily'] = yf.download(symbol, period='3mo', interval='1d', progress=False)
            
            # 4小时（1个月）- yfinance不支持4h，用日线替代
            data['4h'] = data['daily'].tail(30)  # 最近30天模拟4小时
            
            # 1小时（1周）- 用日线替代
            data['1h'] = data['daily'].tail(7)  # 最近7天模拟1小时
            
            return data
            
        except Exception as e:
            print(f"⚠️ 数据获取失败: {e}")
            return {}
    
    @staticmethod
    def analyze_timeframe_trend(df: pd.DataFrame) -> Dict:
        """分析单个时间周期的趋势"""
        
        if df is None or len(df) < 20:
            return {'trend': 'unknown', 'strength': 0}
        
        try:
            # 复制DataFrame避免警告
            df = df.copy()
            
            # 计算均线
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA10'] = df['Close'].rolling(window=10).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            
            current_price = float(df['Close'].iloc[-1].iloc[0] if hasattr(df['Close'].iloc[-1], 'iloc') else df['Close'].iloc[-1])
            ma5 = float(df['MA5'].iloc[-1].iloc[0] if hasattr(df['MA5'].iloc[-1], 'iloc') else df['MA5'].iloc[-1])
            ma10 = float(df['MA10'].iloc[-1].iloc[0] if hasattr(df['MA10'].iloc[-1], 'iloc') else df['MA10'].iloc[-1])
            ma20 = float(df['MA20'].iloc[-1].iloc[0] if hasattr(df['MA20'].iloc[-1], 'iloc') else df['MA20'].iloc[-1])
            
            # 趋势判断
            if current_price > ma5 and ma5 > ma10 and ma10 > ma20:
                trend = 'up'
                strength = 0.8
            elif current_price > ma20 and ma5 > ma10:
                trend = 'up'
                strength = 0.6
            elif current_price < ma5 and ma5 < ma10 and ma10 < ma20:
                trend = 'down'
                strength = 0.8
            elif current_price < ma20 and ma5 < ma10:
                trend = 'down'
                strength = 0.6
            else:
                trend = 'sideways'
                strength = 0.4
            
            # 蜡烛形态
            last_open = float(df['Open'].iloc[-1])
            last_close = float(df['Close'].iloc[-1])
            
            if last_close > last_open:
                candle_color = 'green'
            else:
                candle_color = 'red'
            
            # 计算RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # 计算ADX
            high = df['High']
            low = df['Low']
            close = df['Close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            
            tr = pd.concat([
                high - low,
                abs(high - close.shift()),
                abs(low - close.shift())
            ], axis=1).max(axis=1)
            
            atr = tr.rolling(window=14).mean()
            plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=14).mean()
            adx_value = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 25
            
            return {
                'trend': trend,
                'strength': strength,
                'candle': candle_color,
                'price': float(current_price),
                'ma5': float(ma5),
                'ma10': float(ma10),
                'ma20': float(ma20),
                'rsi': float(rsi_value),
                'adx': float(adx_value),
                'plus_di': float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 20,
                'minus_di': float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 20
            }
            
        except Exception as e:
            print(f"⚠️ 趋势分析失败: {e}")
            return {'trend': 'unknown', 'strength': 0}
    
    @staticmethod
    def check_trend_consistency(weekly: Dict, daily: Dict, hourly4: Dict) -> Dict:
        """判断趋势一致性"""
        
        trends = [weekly['trend'], daily['trend'], hourly4['trend']]
        
        # 统计各趋势数量
        up_count = trends.count('up')
        down_count = trends.count('down')
        
        if up_count == 3:
            return {
                'status': 'aligned',
                'direction': 'strong_up',
                'confidence': 0.9,
                'desc': '多周期趋势一致向上，强烈看涨'
            }
        elif down_count == 3:
            return {
                'status': 'aligned',
                'direction': 'strong_down',
                'confidence': 0.9,
                'desc': '多周期趋势一致向下，强烈看跌'
            }
        elif up_count == 2 and down_count == 0:
            return {
                'status': 'mostly_up',
                'direction': 'up',
                'confidence': 0.7,
                'desc': '多数周期看涨，谨慎乐观'
            }
        elif down_count == 2 and up_count == 0:
            return {
                'status': 'mostly_down',
                'direction': 'down',
                'confidence': 0.7,
                'desc': '多数周期看跌，谨慎悲观'
            }
        else:
            return {
                'status': 'divergent',
                'direction': 'neutral',
                'confidence': 0.3,
                'desc': '多周期趋势背离，建议观望'
            }


class SupportResistanceAnalyzer:
    """支撑阻力位分析器（改进版）"""
    
    @staticmethod
    def calculate_dynamic_levels(prices: List[float], current_price: float, volumes: List[float] = None) -> Dict:
        """
        动态计算支撑阻力位
        
        Args:
            prices: 价格序列
            current_price: 当前价格
            volumes: 成交量序列（可选）
        
        Returns:
            支撑阻力位字典
        """
        
        if not prices:
            return {'supports': [], 'resistances': []}
        
        high = max(prices)
        low = min(prices)
        diff = high - low
        
        supports = []
        resistances = []
        
        # 方法1: 斐波那契回调（从高点往下算）
        fib_levels = [
            (0.0, '历史高点'),
            (0.236, '23.6%回调'),
            (0.382, '38.2%回调'),
            (0.5, '50%回调'),
            (0.618, '61.8%回调'),
            (0.786, '78.6%回调'),
            (1.0, '历史低点')
        ]
        
        for fib, desc in fib_levels:
            price = high - diff * fib
            
            if price < current_price - current_price * 0.001:  # 低于当前价格0.1%才算是支撑
                supports.append({
                    'price': price,
                    'type': f'fib_{fib*100:.1f}%',
                    'desc': desc,
                    'distance_pct': (current_price - price) / current_price * 100,
                    'strength': 'strong' if fib in [0.5, 0.618] else 'moderate'
                })
            elif price > current_price + current_price * 0.001:  # 高于当前价格0.1%才算是阻力
                resistances.append({
                    'price': price,
                    'type': f'fib_{fib*100:.1f}%',
                    'desc': desc,
                    'distance_pct': (price - current_price) / current_price * 100,
                    'strength': 'strong' if fib in [0.236, 0.382] else 'moderate'
                })
        
        # 方法2: 成交量密集区（如果有成交量数据）
        if volumes and len(volumes) == len(prices):
            # 找成交量最大的价格区间
            df = pd.DataFrame({'price': prices, 'volume': volumes})
            df['price_bucket'] = pd.cut(df['price'], bins=20)
            volume_profile = df.groupby('price_bucket')['volume'].sum()
            
            # 成交量最大的3个区间
            top_zones = volume_profile.nlargest(3)
            
            for zone, vol in top_zones.items():
                zone_price = (zone.left + zone.right) / 2
                
                if zone_price < current_price:
                    supports.append({
                        'price': zone_price,
                        'type': 'volume_cluster',
                        'desc': f'成交量密集区 ${zone_price:,.0f}',
                        'distance_pct': (current_price - zone_price) / current_price * 100,
                        'strength': 'strong'
                    })
                else:
                    resistances.append({
                        'price': zone_price,
                        'type': 'volume_cluster',
                        'desc': f'成交量密集区 ${zone_price:,.0f}',
                        'distance_pct': (zone_price - current_price) / current_price * 100,
                        'strength': 'strong'
                    })
        
        # 排序
        supports = sorted(supports, key=lambda x: x['price'], reverse=True)[:5]  # 最多5个支撑位
        resistances = sorted(resistances, key=lambda x: x['price'])[:5]  # 最多5个阻力位
        
        return {
            'supports': supports,
            'resistances': resistances,
            'current': current_price
        }
    
    @staticmethod
    def find_multi_timeframe_levels(weekly_data: Dict, daily_data: Dict, hourly4_data: Dict) -> Dict:
        """找出多周期共振的支撑阻力位"""
        
        weekly_prices = weekly_data.get('prices', [])
        daily_prices = daily_data.get('prices', [])
        hourly4_prices = hourly4_data.get('prices', [])
        
        current_price = daily_data.get('current_price', 0)
        
        # 各周期支撑阻力位
        weekly_sr = SupportResistanceAnalyzer.calculate_dynamic_levels(weekly_prices, current_price)
        daily_sr = SupportResistanceAnalyzer.calculate_dynamic_levels(daily_prices, current_price)
        hourly4_sr = SupportResistanceAnalyzer.calculate_dynamic_levels(hourly4_prices, current_price)
        
        # 找共振位置（多个周期都有的位置）
        confluence_supports = []
        confluence_resistances = []
        
        # 支撑位共振
        for s in daily_sr['supports']:
            # 检查是否在其他周期也存在
            weekly_match = any(abs(s['price'] - ws['price']) / s['price'] < 0.02 for ws in weekly_sr['supports'])
            hourly4_match = any(abs(s['price'] - hs['price']) / s['price'] < 0.02 for hs in hourly4_sr['supports'])
            
            if weekly_match and hourly4_match:
                confluence_supports.append({
                    **s,
                    'confluence': 'multi_timeframe',
                    'strength': 'critical'
                })
        
        # 阻力位共振
        for r in daily_sr['resistances']:
            weekly_match = any(abs(r['price'] - wr['price']) / r['price'] < 0.02 for wr in weekly_sr['resistances'])
            hourly4_match = any(abs(r['price'] - hr['price']) / r['price'] < 0.02 for hr in hourly4_sr['resistances'])
            
            if weekly_match and hourly4_match:
                confluence_resistances.append({
                    **r,
                    'confluence': 'multi_timeframe',
                    'strength': 'critical'
                })
        
        return {
            'weekly': weekly_sr,
            'daily': daily_sr,
            '4h': hourly4_sr,
            'confluence': {
                'supports': confluence_supports[:2],  # 最多2个共振支撑
                'resistances': confluence_resistances[:2]  # 最多2个共振阻力
            }
        }


class BuySellAnalyzer:
    """买入卖出分析器"""
    
    @staticmethod
    def analyze_buy_opportunity(current_price: float, supports: List[Dict], trend: Dict) -> Dict:
        """分析买入机会"""
        
        # 确定最佳买入区间
        optimal_range = BuySellAnalyzer._find_optimal_buy_range(current_price, supports, trend)
        
        # 分批建仓策略
        position_sizing = BuySellAnalyzer._calculate_position_sizing(current_price, optimal_range)
        
        # 确认信号
        confirmation_signals = BuySellAnalyzer._check_confirmation_signals(trend)
        
        # 止损设置
        stop_loss = BuySellAnalyzer._calculate_stop_loss(current_price, supports)
        
        return {
            'price_range': optimal_range,
            'timing': confirmation_signals,
            'position_sizing': position_sizing,
            'stop_loss': stop_loss
        }
    
    @staticmethod
    def _find_optimal_buy_range(current_price: float, supports: List[Dict], trend: Dict) -> Dict:
        """找出最佳买入区间"""
        
        if not supports:
            return {
                'optimal': f"${current_price * 0.95:,.0f} - ${current_price * 0.98:,.0f}",
                'acceptable': f"${current_price * 0.93:,.0f} - ${current_price:,.0f}",
                'reason': '无明确支撑位，建议谨慎'
            }
        
        # 找最近的支撑位
        nearest_support = supports[0]
        second_support = supports[1] if len(supports) > 1 else None
        
        optimal_low = nearest_support['price']
        optimal_high = current_price
        
        # 如果趋势向上，可以稍微激进
        if trend['trend'] == 'up':
            acceptable_low = optimal_low * 0.97
            acceptable_high = current_price * 1.01
        else:
            acceptable_low = optimal_low * 0.95
            acceptable_high = optimal_low * 1.02
        
        return {
            'optimal': f"${optimal_low:,.0f} - ${optimal_high:,.0f}",
            'acceptable': f"${acceptable_low:,.0f} - ${acceptable_high:,.0f}",
            'reason': f"接近支撑位${nearest_support['price']:,.0f} ({nearest_support['desc']})"
        }
    
    @staticmethod
    def _calculate_position_sizing(current_price: float, optimal_range: Dict) -> Dict:
        """计算分批建仓策略"""
        
        # 提取价格范围
        prices = optimal_range['optimal'].replace('$', '').replace(',', '').split(' - ')
        low_price = float(prices[0])
        high_price = float(prices[1])
        
        return {
            'recommended': '30-40%仓位',
            'strategy': '分3批买入',
            'batch_1': {
                'price': f"${high_price:,.0f}",
                'size': '15%',
                'reason': '当前价位轻仓试探'
            },
            'batch_2': {
                'price': f"${(low_price + high_price) / 2:,.0f}",
                'size': '15%',
                'reason': '回调加仓'
            },
            'batch_3': {
                'price': f"${low_price:,.0f}",
                'size': '10%',
                'reason': '支撑位补仓'
            }
        }
    
    @staticmethod
    def _check_confirmation_signals(trend: Dict) -> Dict:
        """检查确认信号"""
        
        signals = []
        
        # RSI信号
        rsi = trend.get('rsi', 50)
        if rsi < 30:
            signals.append('RSI超卖(<30)，反弹机会')
        elif rsi < 40:
            signals.append('RSI偏低，可考虑建仓')
        
        # MACD信号
        if trend.get('macd_histogram', 0) > 0:
            signals.append('MACD金叉，动能向上')
        
        # 趋势强度
        adx = trend.get('adx', 25)
        if adx > 25:
            signals.append(f'ADX={adx:.1f}，趋势明确')
        
        # 方向指标
        plus_di = trend.get('plus_di', 20)
        minus_di = trend.get('minus_di', 20)
        if plus_di > minus_di:
            signals.append('+DI>-DI，多头占优')
        
        return {
            'immediate': len(signals) >= 2,
            'wait_for': '回调至支撑位附近' if len(signals) < 2 else '可考虑立即买入',
            'signals': signals
        }
    
    @staticmethod
    def _calculate_stop_loss(current_price: float, supports: List[Dict]) -> Dict:
        """计算止损位"""
        
        if not supports:
            initial_stop = current_price * 0.97
        else:
            # 止损设在支撑位下方2-3%
            nearest_support = supports[0]['price']
            initial_stop = nearest_support * 0.97
        
        return {
            'initial': f"${initial_stop:,.0f} (-{(current_price - initial_stop) / current_price * 100:.1f}%)",
            'trailing': True,
            'trailing_percent': 3,
            'reason': '跌破支撑位止损'
        }
    
    @staticmethod
    def analyze_sell_opportunity(current_price: float, resistances: List[Dict], trend: Dict) -> Dict:
        """分析卖出机会"""
        
        # 止盈目标
        take_profit = BuySellAnalyzer._calculate_take_profit(current_price, resistances)
        
        # 卖出时机
        sell_timing = BuySellAnalyzer._identify_sell_timing(trend)
        
        return {
            'take_profit': take_profit,
            'timing': sell_timing
        }
    
    @staticmethod
    def _calculate_take_profit(current_price: float, resistances: List[Dict]) -> List[Dict]:
        """计算止盈目标"""
        
        targets = []
        
        if not resistances:
            # 默认目标
            targets = [
                {'price': current_price * 1.05, 'percent': 5, 'position': 30, 'reason': '短期目标'},
                {'price': current_price * 1.10, 'percent': 10, 'position': 40, 'reason': '中期目标'},
                {'price': current_price * 1.15, 'percent': 15, 'position': 30, 'reason': '长期目标'}
            ]
        else:
            # 根据阻力位设定目标
            for i, r in enumerate(resistances[:3]):
                if i == 0:
                    targets.append({
                        'price': r['price'],
                        'percent': (r['price'] - current_price) / current_price * 100,
                        'position': 30,
                        'reason': f'第一阻力位 ({r["desc"]})'
                    })
                elif i == 1:
                    targets.append({
                        'price': r['price'],
                        'percent': (r['price'] - current_price) / current_price * 100,
                        'position': 40,
                        'reason': f'第二阻力位 ({r["desc"]})'
                    })
                else:
                    targets.append({
                        'price': r['price'],
                        'percent': (r['price'] - current_price) / current_price * 100,
                        'position': 30,
                        'reason': f'第三阻力位 ({r["desc"]})'
                    })
        
        return targets
    
    @staticmethod
    def _identify_sell_timing(trend: Dict) -> Dict:
        """识别卖出时机"""
        
        signals = []
        
        # RSI超买
        rsi = trend.get('rsi', 50)
        if rsi > 70:
            signals.append('RSI超买(>70)，回调风险高')
        elif rsi > 60:
            signals.append('RSI偏高，注意回调')
        
        # MACD死叉
        if trend.get('macd_histogram', 0) < 0:
            signals.append('MACD死叉，动能减弱')
        
        # 趋势反转
        adx = trend.get('adx', 25)
        if adx < 20:
            signals.append('ADX下降，趋势可能反转')
        
        return {
            'signals': signals,
            'urgent': len(signals) >= 2,
            'desc': '多个卖出信号出现，建议减仓' if len(signals) >= 2 else '暂无明确卖出信号'
        }


# 测试代码
if __name__ == '__main__':
    print("多周期分析框架 v5.0")
    print("=" * 60)
    
    # 测试
    symbol = 'ETH-USD'
    
    # 获取数据
    data = MultiTimeframeAnalyzer.get_multi_timeframe_data(symbol)
    
    if data:
        # 分析趋势
        weekly_trend = MultiTimeframeAnalyzer.analyze_timeframe_trend(data['weekly'])
        daily_trend = MultiTimeframeAnalyzer.analyze_timeframe_trend(data['daily'])
        hourly4_trend = MultiTimeframeAnalyzer.analyze_timeframe_trend(data['4h'])
        
        print(f"\n周线趋势: {weekly_trend['trend']} (强度: {weekly_trend['strength']:.0%})")
        print(f"日线趋势: {daily_trend['trend']} (强度: {daily_trend['strength']:.0%})")
        print(f"4小时趋势: {hourly4_trend['trend']} (强度: {hourly4_trend['strength']:.0%})")
        
        # 趋势一致性
        consistency = MultiTimeframeAnalyzer.check_trend_consistency(weekly_trend, daily_trend, hourly4_trend)
        print(f"\n趋势一致性: {consistency['status']}")
        print(f"判断: {consistency['desc']}")
