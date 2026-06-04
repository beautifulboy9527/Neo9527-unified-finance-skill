#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理模块 - 整合自 sm-analyze 和 sm-stock-daily
ATR止损、仓位计算、目标价计算
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional
import pandas as pd

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class ATRStopLoss:
    """ATR 动态止损计算器"""
    
    # ATR 倍数级别
    LEVELS = {
        'conservative': 1.0,   # 保守止损
        'standard': 2.0,       # 标准止损 (推荐)
        'aggressive': 3.0      # 激进止损
    }
    
    def calculate(self, symbol: str, level: str = 'standard') -> Dict:
        """
        计算 ATR 止损位
        
        Args:
            symbol: 股票代码
            level: 止损级别 (conservative/standard/aggressive)
            
        Returns:
            {
                'atr': 0.0382,
                'current_price': 266.43,
                'stop_loss': 1.4966,
                'stop_loss_pct': -4.86,
                'risk_amount': 12.92,
                'level': 'standard',
                'atr_multiplier': 2.0
            }
        """
        result = {
            'symbol': symbol,
            'atr': None,
            'current_price': None,
            'stop_loss': None,
            'stop_loss_pct': None,
            'risk_amount': None,
            'level': level,
            'atr_multiplier': self.LEVELS.get(level, 2.0),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 获取行情数据
            ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is not None and not ohlcv.empty:
                # 计算 ATR
                atr = self._calculate_atr(ohlcv)
                result['atr'] = round(atr, 4)
                
                # 当前价格
                close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
                current_price = close.iloc[-1]
                result['current_price'] = round(float(current_price), 2)
                
                # 计算止损位
                atr_multiplier = self.LEVELS.get(level, 2.0)
                stop_loss = current_price - atr * atr_multiplier
                result['stop_loss'] = round(float(stop_loss), 2)
                
                # 止损百分比
                stop_loss_pct = (stop_loss - current_price) / current_price * 100
                result['stop_loss_pct'] = round(stop_loss_pct, 2)
                
                # 风险金额 (假设1手)
                result['risk_amount'] = round(float(current_price - stop_loss), 2)
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_ohlcv(self, symbol: str):
        """获取K线数据"""
        import traceback
        
        # 判断市场类型
        is_us_stock = symbol.isalpha() and len(symbol) <= 5  # 美股: AAPL, MSFT
        is_cn_stock = symbol.isdigit() or (symbol[:3].isdigit())  # A股: 002475, 600519
        
        # 尝试方法1: 主要数据源
        try:
            if is_us_stock:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="3mo")
                if df is not None and not df.empty:
                    return df
            elif is_cn_stock:
                import akshare as ak
                # 标准化代码格式
                code = symbol.zfill(6) if len(symbol) < 6 else symbol
                df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
                if df is not None and not df.empty:
                    return df
        except Exception as e:
            pass  # 继续尝试备用方法
        
        # 尝试方法2: 使用 yfinance 作为 A股的备用
        if is_cn_stock:
            try:
                import yfinance as yf
                # yfinance A股格式: 002475.SZ
                code = symbol.zfill(6)
                suffix = '.SZ' if code.startswith(('0', '3')) else '.SS'
                ticker = yf.Ticker(code + suffix)
                df = ticker.history(period="3mo")
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                pass
        
        return None
    
    def _calculate_atr(self, ohlcv, period: int = 14) -> float:
        """计算 ATR"""
        high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
        low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
        close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR
        atr = tr.rolling(period).mean().iloc[-1]
        return float(atr)


class PositionSizer:
    """仓位计算器"""
    
    def calculate(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: float = 0.02
    ) -> Dict:
        """
        计算仓位大小
        
        Args:
            capital: 总资金
            entry_price: 入场价
            stop_loss: 止损价
            risk_per_trade: 单笔风险比例 (默认 2%)
            
        Returns:
            {
                'position_value': 10000.0,
                'shares': 37,
                'risk_amount': 200.0,
                'risk_pct': 2.0,
                'stop_loss_distance': 5.38
            }
        """
        # 参数验证
        if entry_price is None or stop_loss is None:
            return {
                'error': '缺少必要参数: entry_price 或 stop_loss 为 None',
                'suggestion': '请确保能获取到当前价格并计算止损价',
                'capital': capital,
                'shares': 0,
                'position_value': 0
            }
        
        # 风险金额
        risk_amount = capital * risk_per_trade
        
        # 止损距离
        stop_loss_distance = abs(entry_price - stop_loss)
        
        # 可买股数
        if stop_loss_distance > 0:
            shares = int(risk_amount / stop_loss_distance)
        else:
            shares = 0
        
        # 仓位金额
        position_value = shares * entry_price
        
        return {
            'capital': capital,
            'position_value': round(position_value, 2),
            'shares': shares,
            'risk_amount': round(risk_amount, 2),
            'risk_pct': round(risk_per_trade * 100, 2),
            'stop_loss_distance': round(stop_loss_distance, 2),
            'entry_price': entry_price,
            'stop_loss': stop_loss
        }
    
    def calculate_by_risk_level(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        risk_level: str = 'medium'
    ) -> Dict:
        """
        根据风险等级计算仓位
        
        Args:
            risk_level: low(1%) / medium(2%) / high(3%) / very_high(5%)
        """
        risk_map = {
            'low': 0.01,
            'medium': 0.02,
            'high': 0.03,
            'very_high': 0.05
        }
        
        risk_per_trade = risk_map.get(risk_level, 0.02)
        return self.calculate(capital, entry_price, stop_loss, risk_per_trade)


class TargetCalculator:
    """目标价计算器"""
    
    def calculate(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        risk_reward_ratio: float = 2.0
    ) -> Dict:
        """
        计算目标价
        
        Args:
            symbol: 股票代码
            entry_price: 入场价
            stop_loss: 止损价
            risk_reward_ratio: 风险收益比 (默认 1:2)
            
        Returns:
            {
                'entry_price': 266.43,
                'stop_loss': 253.51,
                'target_price': 292.27,
                'risk': 12.92,
                'reward': 25.84,
                'risk_reward_ratio': 2.0,
                'target_return_pct': 9.70,
                'support': 255.0,
                'resistance': 280.0
            }
        """
        result = {
            'symbol': symbol,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': None,
            'risk': None,
            'reward': None,
            'risk_reward_ratio': risk_reward_ratio,
            'target_return_pct': None,
            'support': None,
            'resistance': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 计算风险
            risk = abs(entry_price - stop_loss)
            result['risk'] = round(risk, 2)
            
            # 计算目标价
            target_price = entry_price + risk * risk_reward_ratio
            result['target_price'] = round(target_price, 2)
            
            # 收益
            reward = target_price - entry_price
            result['reward'] = round(reward, 2)
            
            # 目标收益率
            target_return_pct = (target_price - entry_price) / entry_price * 100
            result['target_return_pct'] = round(target_return_pct, 2)
            
            # 获取支撑阻力位
            support_resistance = self._get_support_resistance(symbol)
            if support_resistance:
                result['support'] = support_resistance.get('support')
                result['resistance'] = support_resistance.get('resistance')
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_support_resistance(self, symbol: str) -> Optional[Dict]:
        """获取支撑阻力位"""
        try:
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo")
            else:
                import akshare as ak
                hist = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            
            if hist.empty:
                return None
            
            close = hist['Close'] if 'Close' in hist else hist['收盘']
            high = hist['High'] if 'High' in hist else hist['最高']
            low = hist['Low'] if 'Low' in hist else hist['最低']
            
            # 简化：用20日高低点作为支撑阻力
            support = low.rolling(20).min().iloc[-1]
            resistance = high.rolling(20).max().iloc[-1]
            
            return {
                'support': round(float(support), 2),
                'resistance': round(float(resistance), 2)
            }
        except:
            return None


class RiskManager:
    """风险管理器"""
    
    def __init__(self):
        self.atr_stop = ATRStopLoss()
        self.position_sizer = PositionSizer()
        self.target_calc = TargetCalculator()
    
    def analyze(
        self,
        symbol: str,
        capital: float = 100000,
        risk_level: str = 'medium'
    ) -> Dict:
        """
        完整风险管理分析
        
        Args:
            symbol: 股票代码
            capital: 总资金
            risk_level: 风险等级
            
        Returns:
            {
                'stop_loss': {...},
                'position': {...},
                'target': {...},
                'summary': {...}
            }
        """
        # ATR 止损
        stop_loss_result = self.atr_stop.calculate(symbol)
        
        if stop_loss_result['error']:
            return {
                'symbol': symbol,
                'error': stop_loss_result['error'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        entry_price = stop_loss_result['current_price']
        stop_loss = stop_loss_result['stop_loss']
        
        # 检查价格是否有效
        if entry_price is None or stop_loss is None:
            return {
                'symbol': symbol,
                'error': '无法获取有效价格数据',
                'stop_loss_result': stop_loss_result,
                'suggestion': '请检查股票代码是否正确，或稍后重试',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # 仓位计算
        position_result = self.position_sizer.calculate_by_risk_level(
            capital, entry_price, stop_loss, risk_level
        )
        
        # 目标价计算
        target_result = self.target_calc.calculate(symbol, entry_price, stop_loss)
        
        # 汇总
        summary = {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'stop_loss_pct': stop_loss_result['stop_loss_pct'],
            'target_price': target_result['target_price'],
            'target_return_pct': target_result['target_return_pct'],
            'shares': position_result['shares'],
            'position_value': position_result['position_value'],
            'risk_amount': position_result['risk_amount'],
            'risk_reward_ratio': target_result['risk_reward_ratio'],
            'risk_level': risk_level
        }
        
        return {
            'symbol': symbol,
            'capital': capital,
            'stop_loss': stop_loss_result,
            'position': position_result,
            'target': target_result,
            'summary': summary,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def analyze_risk(symbol: str, capital: float = 100000, risk_level: str = 'medium') -> Dict:
    """风险管理分析入口"""
    manager = RiskManager()
    return manager.analyze(symbol, capital, risk_level)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='风险管理分析')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--capital', type=float, default=100000, help='总资金')
    parser.add_argument('--risk-level', default='medium', help='风险等级')
    
    args = parser.parse_args()
    
    result = analyze_risk(args.symbol, args.capital, args.risk_level)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
