#!/usr/bin/env python3
"""ETH完整技术分析脚本"""

import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange

eth = yf.Ticker('ETH-USD')
hist = eth.history(period='3mo')
info = eth.info

close = hist['Close']
high = hist['High']
low = hist['Low']

ma7 = SMAIndicator(close=close, window=7).sma_indicator()
ma14 = SMAIndicator(close=close, window=14).sma_indicator()
ma30 = SMAIndicator(close=close, window=30).sma_indicator()

rsi14 = RSIIndicator(close=close, window=14).rsi()

macd = MACD(close=close)
macd_hist = macd.macd_diff()

bb = BollingerBands(close=close, window=20)
bb_upper = bb.bollinger_hband()
bb_lower = bb.bollinger_lband()

atr = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()

latest_price = close.iloc[-1]

print('=== ETH完整技术分析 ===')
print(f'当前价格: ${latest_price:.2f}')
print(f'市值: ${info.get("marketCap", 0):,.0f}')
print(f'52周高点: ${info.get("fiftyTwoWeekHigh", 0):.2f}')
print(f'52周低点: ${info.get("fiftyTwoWeekLow", 0):.2f}')

pct_from_high = (latest_price / info.get('fiftyTwoWeekHigh', 1) - 1) * 100
pct_from_low = (latest_price / info.get('fiftyTwoWeekLow', 1) - 1) * 100
print(f'距52周高点: {pct_from_high:.1f}%')
print(f'距52周低点: {pct_from_low:.1f}%')

print()
print('[移动均线]')
print(f'MA7: ${ma7.iloc[-1]:.2f} | MA14: ${ma14.iloc[-1]:.2f} | MA30: ${ma30.iloc[-1]:.2f}')

if latest_price > ma7.iloc[-1] and latest_price > ma14.iloc[-1] and latest_price > ma30.iloc[-1]:
    ma_trend = '多头排列'
elif latest_price < ma7.iloc[-1] and latest_price < ma14.iloc[-1] and latest_price < ma30.iloc[-1]:
    ma_trend = '空头排列'
else:
    ma_trend = '震荡整理'
print(f'均线形态: {ma_trend}')

print()
print('[动量指标]')
print(f'RSI(14): {rsi14.iloc[-1]:.2f}')
if rsi14.iloc[-1] > 70:
    print('RSI状态: 超买')
elif rsi14.iloc[-1] < 30:
    print('RSI状态: 超卖')
else:
    print('RSI状态: 正常区间')

print()
print('[MACD]')
print(f'MACD柱: {macd_hist.iloc[-1]:.4f}')
if macd_hist.iloc[-1] > 0:
    print('MACD状态: 金叉')
else:
    print('MACD状态: 死叉')

print()
print('[布林带]')
bb_position = (latest_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1]) * 100
print(f'布林带位置: {bb_position:.1f}%')

print()
print('[波动率]')
print(f'ATR(14): ${atr.iloc[-1]:.2f} ({(atr.iloc[-1]/latest_price)*100:.2f}%)')

print()
print('[30日统计]')
print(f'30日最高: ${close[-30:].max():.2f}')
print(f'30日最低: ${close[-30:].min():.2f}')
print(f'30日涨跌: {(close.iloc[-1]/close.iloc[-30]-1)*100:.2f}%')
print(f'30日振幅: {(close[-30:].max()/close[-30:].min()-1)*100:.2f}%')

print()
print('[支撑阻力]')
support = close[-30:].min()
resistance = close[-30:].max()
print(f'支撑位: ${support:.2f}')
print(f'阻力位: ${resistance:.2f}')
print(f'止损位: ${support*0.97:.2f}')
print(f'目标位: ${resistance*1.05:.2f}')