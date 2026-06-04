#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业技术指标库 - Professional Technical Indicators
集成TA-Lib + 自定义指标

包含:
- 趋势指标 (MA/EMA/SMA/DEMA/TEMA/SAR/ADX/DMI)
- 动量指标 (RSI/MACD/Stochastic/CCI/Williams%R/MFI)
- 波动率指标 (ATR/Bollinger/Keltner/Donchian)
- 成交量指标 (OBV/AD/CMF/VWAP/MFI)
- 自定义指标 (多空力道/资金流向/趋势强度)
"""

import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 尝试导入TA-Lib
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("⚠️ TA-Lib未安装，使用内置计算")


class TechnicalIndicators:
    """专业技术指标库"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: OHLCV DataFrame (必须有 Open, High, Low, Close, Volume 列)
        """
        self.df = df.copy()
        self.open = df['Open'].values if 'Open' in df.columns else df['open'].values
        self.high = df['High'].values if 'High' in df.columns else df['high'].values
        self.low = df['Low'].values if 'Low' in df.columns else df['low'].values
        self.close = df['Close'].values if 'Close' in df.columns else df['close'].values
        self.volume = df['Volume'].values if 'Volume' in df.columns else df['volume'].values
        
        self.indicators = {}
    
    # ========================================
    # 趋势指标
    # ========================================
    
    def moving_averages(
        self,
        periods: List[int] = [5, 10, 20, 60, 120, 250]
    ) -> Dict[str, np.ndarray]:
        """
        移动平均线
        
        包括: SMA, EMA, WMA, DEMA, TEMA
        """
        results = {}
        
        for period in periods:
            if TALIB_AVAILABLE:
                # SMA
                results[f'SMA_{period}'] = talib.SMA(self.close, timeperiod=period)
                # EMA
                results[f'EMA_{period}'] = talib.EMA(self.close, timeperiod=period)
                # WMA
                results[f'WMA_{period}'] = talib.WMA(self.close, timeperiod=period)
                # DEMA
                if period >= 2:
                    results[f'DEMA_{period}'] = talib.DEMA(self.close, timeperiod=period)
                # TEMA
                if period >= 3:
                    results[f'TEMA_{period}'] = talib.TEMA(self.close, timeperiod=period)
            else:
                # 内置计算
                close_series = pd.Series(self.close)
                results[f'SMA_{period}'] = close_series.rolling(period).mean().values
                results[f'EMA_{period}'] = close_series.ewm(span=period, adjust=False).mean().values
        
        return results
    
    def macd(
        self,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9
    ) -> Dict[str, np.ndarray]:
        """
        MACD指标
        
        Returns:
            macd: MACD线 (DIF)
            signal: 信号线 (DEA)
            histogram: 柱状图 (MACD柱)
        """
        if TALIB_AVAILABLE:
            macd, signal, hist = talib.MACD(
                self.close,
                fastperiod=fastperiod,
                slowperiod=slowperiod,
                signalperiod=signalperiod
            )
        else:
            # 内置计算
            close_series = pd.Series(self.close)
            ema_fast = close_series.ewm(span=fastperiod, adjust=False).mean()
            ema_slow = close_series.ewm(span=slowperiod, adjust=False).mean()
            macd = (ema_fast - ema_slow).values
            signal = pd.Series(macd).ewm(span=signalperiod, adjust=False).mean().values
            hist = (macd - signal)
        
        return {
            'MACD': macd,
            'MACD_Signal': signal,
            'MACD_Hist': hist
        }
    
    def adx(
        self,
        period: int = 14
    ) -> Dict[str, np.ndarray]:
        """
        平均趋向指标 (ADX)
        
        ADX > 25: 趋势明显
        ADX < 20: 无明确趋势
        """
        if TALIB_AVAILABLE:
            adx = talib.ADX(self.high, self.low, self.close, timeperiod=period)
            plus_di = talib.PLUS_DI(self.high, self.low, self.close, timeperiod=period)
            minus_di = talib.MINUS_DI(self.high, self.low, self.close, timeperiod=period)
        else:
            # 内置计算
            high_series = pd.Series(self.high)
            low_series = pd.Series(self.low)
            close_series = pd.Series(self.close)
            
            plus_dm = high_series.diff()
            minus_dm = -low_series.diff()
            
            plus_dm = plus_dm.where(plus_dm > 0, 0)
            minus_dm = minus_dm.where(minus_dm > 0, 0)
            
            tr1 = high_series - low_series
            tr2 = (high_series - close_series.shift()).abs()
            tr3 = (low_series - close_series.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            plus_di = 100 * (plus_dm.rolling(period).mean() / (atr + 0.0001))
            minus_di = 100 * (minus_dm.rolling(period).mean() / (atr + 0.0001))
            
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 0.0001)
            adx = dx.rolling(period).mean()
        
        return {
            'ADX': adx,
            'Plus_DI': plus_di,
            'Minus_DI': minus_di
        }
    
    def sar(
        self,
        acceleration: float = 0.02,
        maximum: float = 0.2
    ) -> np.ndarray:
        """
        抛物线转向指标 (Parabolic SAR)
        
        价格在SAR上方: 多头
        价格在SAR下方: 空头
        """
        if TALIB_AVAILABLE:
            return talib.SAR(self.high, self.low, acceleration=acceleration, maximum=maximum)
        else:
            # 简化版SAR计算
            sar = pd.Series(self.close).rolling(4).mean().values
            return sar
    
    # ========================================
    # 动量指标
    # ========================================
    
    def rsi(
        self,
        periods: List[int] = [6, 14, 24]
    ) -> Dict[str, np.ndarray]:
        """
        相对强弱指标 (RSI)
        
        RSI > 70: 超买
        RSI < 30: 超卖
        """
        results = {}
        
        for period in periods:
            if TALIB_AVAILABLE:
                results[f'RSI_{period}'] = talib.RSI(self.close, timeperiod=period)
            else:
                close_series = pd.Series(self.close)
                delta = close_series.diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)
                
                avg_gain = gain.rolling(period).mean()
                avg_loss = loss.rolling(period).mean()
                
                rs = avg_gain / (avg_loss + 0.0001)
                rsi = 100 - (100 / (1 + rs))
                
                results[f'RSI_{period}'] = rsi.values
        
        return results
    
    def stochastic(
        self,
        fastk_period: int = 14,
        slowk_period: int = 3,
        slowd_period: int = 3
    ) -> Dict[str, np.ndarray]:
        """
        随机指标 (KDJ)
        
        K > D: 多头
        K < D: 空头
        """
        if TALIB_AVAILABLE:
            slowk, slowd = talib.STOCH(
                self.high, self.low, self.close,
                fastk_period=fastk_period,
                slowk_period=slowk_period,
                slowk_matype=0,
                slowd_period=slowd_period,
                slowd_matype=0
            )
        else:
            # 内置计算
            close_series = pd.Series(self.close)
            high_series = pd.Series(self.high)
            low_series = pd.Series(self.low)
            
            lowest_low = low_series.rolling(fastk_period).min()
            highest_high = high_series.rolling(fastk_period).max()
            
            slowk = 100 * (close_series - lowest_low) / (highest_high - lowest_low + 0.0001)
            slowd = slowk.rolling(slowd_period).mean()
        
        return {
            'Stoch_K': slowk,
            'Stoch_D': slowd,
            'Stoch_J': 3 * slowk - 2 * slowd if not TALIB_AVAILABLE else slowk
        }
    
    def williams_r(
        self,
        period: int = 14
    ) -> np.ndarray:
        """
        威廉指标 (Williams %R)
        
        %R > -20: 超买
        %R < -80: 超卖
        """
        if TALIB_AVAILABLE:
            return talib.WILLR(self.high, self.low, self.close, timeperiod=period)
        else:
            close_series = pd.Series(self.close)
            high_series = pd.Series(self.high)
            low_series = pd.Series(self.low)
            
            highest_high = high_series.rolling(period).max()
            lowest_low = low_series.rolling(period).min()
            
            wr = -100 * (highest_high - close_series) / (highest_high - lowest_low + 0.0001)
            return wr.values
    
    def cci(
        self,
        period: int = 20
    ) -> np.ndarray:
        """
        顺势指标 (CCI)
        
        CCI > 100: 超买
        CCI < -100: 超卖
        """
        if TALIB_AVAILABLE:
            return talib.CCI(self.high, self.low, self.close, timeperiod=period)
        else:
            tp = (pd.Series(self.high) + pd.Series(self.low) + pd.Series(self.close)) / 3
            ma = tp.rolling(period).mean()
            md = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean())
            
            cci = (tp - ma) / (0.015 * md + 0.0001)
            return cci.values
    
    def mfi(
        self,
        period: int = 14
    ) -> np.ndarray:
        """
        资金流量指标 (MFI)
        
        MFI > 80: 超买
        MFI < 20: 超卖
        """
        if TALIB_AVAILABLE:
            return talib.MFI(self.high, self.low, self.close, self.volume, timeperiod=period)
        else:
            # 内置计算
            tp = (pd.Series(self.high) + pd.Series(self.low) + pd.Series(self.close)) / 3
            mf = tp * pd.Series(self.volume)
            
            positive_mf = mf.where(tp > tp.shift(), 0)
            negative_mf = mf.where(tp < tp.shift(), 0)
            
            positive_sum = positive_mf.rolling(period).sum()
            negative_sum = negative_mf.rolling(period).sum()
            
            mfi = 100 - (100 / (1 + positive_sum / (negative_sum + 0.0001)))
            return mfi.values
    
    # ========================================
    # 波动率指标
    # ========================================
    
    def atr(
        self,
        period: int = 14
    ) -> np.ndarray:
        """
        平均真实波幅 (ATR)
        
        衡量波动性，用于止损位设定
        """
        if TALIB_AVAILABLE:
            return talib.ATR(self.high, self.low, self.close, timeperiod=period)
        else:
            high_series = pd.Series(self.high)
            low_series = pd.Series(self.low)
            close_series = pd.Series(self.close)
            
            tr1 = high_series - low_series
            tr2 = (high_series - close_series.shift()).abs()
            tr3 = (low_series - close_series.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            atr = tr.rolling(period).mean()
            return atr.values
    
    def bollinger_bands(
        self,
        period: int = 20,
        nbdevup: int = 2,
        nbdevdn: int = 2
    ) -> Dict[str, np.ndarray]:
        """
        布林带 (Bollinger Bands)
        
        价格突破上轨: 超买
        价格突破下轨: 超卖
        """
        if TALIB_AVAILABLE:
            upper, middle, lower = talib.BBANDS(
                self.close,
                timeperiod=period,
                nbdevup=nbdevup,
                nbdevdn=nbdevdn
            )
        else:
            close_series = pd.Series(self.close)
            middle = close_series.rolling(period).mean()
            std = close_series.rolling(period).std()
            
            upper = middle + nbdevup * std
            lower = middle - nbdevdn * std
        
        # 带宽
        bandwidth = (upper - lower) / middle * 100
        
        # %B指标
        close_series = pd.Series(self.close)
        pct_b = (close_series - lower) / (upper - lower + 0.0001)
        
        return {
            'BB_Upper': upper,
            'BB_Middle': middle,
            'BB_Lower': lower,
            'BB_Width': bandwidth,
            'BB_PctB': pct_b.values
        }
    
    def keltner_channel(
        self,
        period: int = 20,
        atr_period: int = 10,
        multiplier: float = 2.0
    ) -> Dict[str, np.ndarray]:
        """
        肯特纳通道 (Keltner Channel)
        
        基于ATR的波动通道
        """
        close_series = pd.Series(self.close)
        middle = close_series.rolling(period).mean()
        atr = self.atr(atr_period)
        
        upper = middle + multiplier * atr
        lower = middle - multiplier * atr
        
        return {
            'KC_Upper': upper,
            'KC_Middle': middle,
            'KC_Lower': lower
        }
    
    def donchian_channel(
        self,
        period: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        唐奇安通道 (Donchian Channel)
        
        突破策略经典指标
        """
        high_series = pd.Series(self.high)
        low_series = pd.Series(self.low)
        
        upper = high_series.rolling(period).max()
        lower = low_series.rolling(period).min()
        middle = (upper + lower) / 2
        
        return {
            'DC_Upper': upper,
            'DC_Middle': middle,
            'DC_Lower': lower
        }
    
    # ========================================
    # 成交量指标
    # ========================================
    
    def obv(self) -> np.ndarray:
        """
        能量潮指标 (OBV)
        
        OBV上升 + 价格下跌: 底背离，看涨
        OBV下降 + 价格上涨: 顶背离，看跌
        """
        if TALIB_AVAILABLE:
            return talib.OBV(self.close, self.volume)
        else:
            close_series = pd.Series(self.close)
            volume_series = pd.Series(self.volume)
            
            direction = np.sign(close_series.diff())
            obv = (direction * volume_series).cumsum()
            return obv.values
    
    def ad_line(self) -> np.ndarray:
        """
        累积/派发线 (A/D Line)
        """
        if TALIB_AVAILABLE:
            return talib.AD(self.high, self.low, self.close, self.volume)
        else:
            clv = ((pd.Series(self.close) - pd.Series(self.low)) - 
                   (pd.Series(self.high) - pd.Series(self.close))) / \
                  (pd.Series(self.high) - pd.Series(self.low) + 0.0001)
            
            ad = clv * pd.Series(self.volume)
            return ad.cumsum().values
    
    def cmf(
        self,
        period: int = 20
    ) -> np.ndarray:
        """
        蔡金资金流量 (CMF)
        
        CMF > 0: 买盘主导
        CMF < 0: 卖盘主导
        """
        high_series = pd.Series(self.high)
        low_series = pd.Series(self.low)
        close_series = pd.Series(self.close)
        volume_series = pd.Series(self.volume)
        
        mfv = ((close_series - low_series) - (high_series - close_series)) / \
              (high_series - low_series + 0.0001) * volume_series
        
        cmf = mfv.rolling(period).sum() / volume_series.rolling(period).sum()
        return cmf.values
    
    def vwap(self) -> np.ndarray:
        """
        成交量加权平均价 (VWAP)
        
        价格高于VWAP: 多头优势
        价格低于VWAP: 空头优势
        """
        high_series = pd.Series(self.high)
        low_series = pd.Series(self.low)
        close_series = pd.Series(self.close)
        volume_series = pd.Series(self.volume)
        
        typical_price = (high_series + low_series + close_series) / 3
        vwap = (typical_price * volume_series).cumsum() / volume_series.cumsum()
        return vwap.values
    
    # ========================================
    # 自定义指标
    # ========================================
    
    def trend_strength(
        self,
        period: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        趋势强度指标
        
        综合ADX + MA斜率 + 价格位置
        """
        # ADX
        adx_data = self.adx(period)
        adx = adx_data['ADX']
        
        # MA斜率
        close_series = pd.Series(self.close)
        ma = close_series.rolling(period).mean()
        ma_slope = ma.pct_change(period) * 100
        
        # 价格相对MA位置
        price_position = (close_series - ma) / ma * 100
        
        # 综合强度
        trend_strength = (adx / 100 * 40 + 
                         np.abs(ma_slope).clip(0, 20) + 
                         np.abs(price_position).clip(0, 40))
        
        return {
            'Trend_Strength': trend_strength.values,
            'ADX': adx,
            'MA_Slope': ma_slope.values,
            'Price_Position': price_position.values
        }
    
    def money_flow(
        self,
        period: int = 20
    ) -> Dict[str, np.ndarray]:
        """
        资金流向指标
        
        综合MFI + CMF + OBV趋势
        """
        mfi = self.mfi(period)
        cmf = self.cmf(period)
        obv = self.obv()
        
        # OBV趋势
        obv_series = pd.Series(obv)
        obv_slope = obv_series.diff(period) / obv_series.shift(period).abs().replace(0, 1)
        
        # 综合资金流向
        money_flow_score = (
            (mfi - 50) / 50 * 40 +  # MFI贡献40分
            cmf * 30 +               # CMF贡献30分
            obv_slope.clip(-1, 1) * 30  # OBV趋势贡献30分
        )
        
        return {
            'Money_Flow_Score': money_flow_score.values,
            'MFI': mfi,
            'CMF': cmf,
            'OBV_Slope': obv_slope.values
        }
    
    def support_resistance_strength(
        self,
        lookback: int = 60
    ) -> Dict[str, np.ndarray]:
        """
        支撑阻力强度
        
        统计历史触及次数和反弹幅度
        """
        high_series = pd.Series(self.high)
        low_series = pd.Series(self.low)
        close_series = pd.Series(self.close)
        
        # 找局部高点和低点
        from scipy.signal import argrelextrema
        
        local_max_idx = argrelextrema(high_series.values, np.greater, order=5)[0]
        local_min_idx = argrelextrema(low_series.values, np.less, order=5)[0]
        
        # 阻力位
        resistance_levels = high_series.iloc[local_max_idx].tail(5) if len(local_max_idx) > 0 else []
        
        # 支撑位
        support_levels = low_series.iloc[local_min_idx].tail(5) if len(local_min_idx) > 0 else []
        
        # 计算强度 (触及次数)
        current_price = close_series.iloc[-1]
        
        return {
            'resistance_levels': resistance_levels.tolist() if hasattr(resistance_levels, 'tolist') else [],
            'support_levels': support_levels.tolist() if hasattr(support_levels, 'tolist') else [],
            'current_price': current_price
        }
    
    # ========================================
    # 综合指标
    # ========================================
    
    def all_indicators(self) -> Dict:
        """
        计算所有指标
        """
        results = {
            'timestamp': self.df.index[-1] if hasattr(self.df, 'index') else None
        }
        
        # 趋势指标
        results.update(self.moving_averages())
        results.update(self.macd())
        results.update(self.adx())
        results['SAR'] = self.sar()
        
        # 动量指标
        results.update(self.rsi())
        results.update(self.stochastic())
        results['Williams_R'] = self.williams_r()
        results['CCI'] = self.cci()
        results['MFI'] = self.mfi()
        
        # 波动率指标
        results['ATR'] = self.atr()
        results.update(self.bollinger_bands())
        results.update(self.keltner_channel())
        results.update(self.donchian_channel())
        
        # 成交量指标
        results['OBV'] = self.obv()
        results['AD_Line'] = self.ad_line()
        results['CMF'] = self.cmf()
        results['VWAP'] = self.vwap()
        
        # 自定义指标
        results.update(self.trend_strength())
        results.update(self.money_flow())
        results.update(self.support_resistance_strength())
        
        return results
    
    def summary(self) -> Dict:
        """
        生成指标摘要
        """
        all_ind = self.all_indicators()
        
        latest = {}
        for key, value in all_ind.items():
            if isinstance(value, np.ndarray) and len(value) > 0:
                latest[key] = float(value[-1])
            elif isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, np.ndarray) and len(v) > 0:
                        latest[f"{key}_{k}"] = float(v[-1])
        
        return latest


# ============================================
# 便捷函数
# ============================================

def calculate_indicators(
    df: pd.DataFrame,
    include_all: bool = True
) -> Dict:
    """
    计算技术指标
    
    Args:
        df: OHLCV DataFrame
        include_all: 是否包含所有指标
        
    Returns:
        指标字典
    """
    ti = TechnicalIndicators(df)
    
    if include_all:
        return ti.all_indicators()
    else:
        return ti.summary()


if __name__ == '__main__':
    # 测试
    import yfinance as yf
    
    print("=" * 60)
    print("专业技术指标库测试")
    print("=" * 60)
    
    # 获取测试数据
    try:
        ticker = yf.Ticker('AAPL')
        df = ticker.history(period='1y')
        
        ti = TechnicalIndicators(df)
        summary = ti.summary()
        
        print(f"\n📊 趋势指标")
        print("-" * 60)
        print(f"  SMA_20: ${summary.get('SMA_20', 0):.2f}")
        print(f"  EMA_20: ${summary.get('EMA_20', 0):.2f}")
        print(f"  ADX: {summary.get('ADX', 0):.1f}")
        
        print(f"\n📈 动量指标")
        print("-" * 60)
        print(f"  RSI_14: {summary.get('RSI_14', 0):.1f}")
        print(f"  MACD: {summary.get('MACD', 0):.2f}")
        print(f"  Stoch_K: {summary.get('Stoch_K', 0):.1f}")
        print(f"  Williams_%R: {summary.get('Williams_R', 0):.1f}")
        
        print(f"\n📉 波动率指标")
        print("-" * 60)
        print(f"  ATR: ${summary.get('ATR', 0):.2f}")
        print(f"  BB_Upper: ${summary.get('BB_Upper', 0):.2f}")
        print(f"  BB_Lower: ${summary.get('BB_Lower', 0):.2f}")
        print(f"  BB_Width: {summary.get('BB_Width', 0):.1f}%")
        
        print(f"\n📊 成交量指标")
        print("-" * 60)
        print(f"  MFI: {summary.get('MFI', 0):.1f}")
        print(f"  CMF: {summary.get('CMF', 0):.3f}")
        print(f"  OBV: {summary.get('OBV', 0):,.0f}")
        
        print(f"\n🎯 自定义指标")
        print("-" * 60)
        print(f"  趋势强度: {summary.get('Trend_Strength', 0):.1f}")
        print(f"  资金流向: {summary.get('Money_Flow_Score', 0):.1f}")
        
        print(f"\nTA-Lib状态: {'✅ 已安装' if TALIB_AVAILABLE else '⚠️ 未安装 (使用内置计算)'}")
        
    except Exception as e:
        print(f"⚠️ 测试失败: {e}")
