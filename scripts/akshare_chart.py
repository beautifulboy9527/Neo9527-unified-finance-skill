#!/usr/bin/env python3
"""
AkShare Chart Generator - A 股/港股图表生成
支持 K 线图 + 技术指标 (RSI/MACD/BB/MA)
"""

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def get_akshare_data(symbol, period='6mo'):
    """获取 AkShare A 股/港股数据"""
    clean_symbol = str(symbol).replace('.HK', '').replace('.SS', '').replace('.SZ', '')
    
    try:
        if str(symbol).endswith('.HK'):
            # 港股数据列名是英文小写
            df = ak.stock_hk_daily(symbol=clean_symbol, adjust='qfq')
            rename_map = {
                'date': 'Date', 'open': 'Open', 'close': 'Close',
                'high': 'High', 'low': 'Low', 'volume': 'Volume'
            }
        else:
            # A 股数据列名是中文
            df = ak.stock_zh_a_hist(symbol=clean_symbol, period='daily', adjust='qfq')
            rename_map = {
                '日期': 'Date', '开盘': 'Open', '收盘': 'Close',
                '最高': 'High', '最低': 'Low', '成交量': 'Volume'
            }
        
        if df is None or df.empty:
            raise Exception("数据为空")
        
        df = df.rename(columns=rename_map)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        if period == '1mo': df = df.tail(21)
        elif period == '3mo': df = df.tail(63)
        elif period == '6mo': df = df.tail(126)
        elif period == '1y': df = df.tail(252)
        
        return df
    except Exception as e:
        raise Exception(f"获取数据失败：{e}")

def calc_rsi(close, window=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))

def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
    ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
    macd = ema_fast - ema_slow
    sig = macd.ewm(span=signal, adjust=False, min_periods=signal).mean()
    hist = macd - sig
    return macd, sig, hist

def calc_bbands(close, window=20, n_std=2.0):
    ma = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std()
    return ma + n_std * std, ma, ma - n_std * std

def generate_akshare_chart(symbol, period='6mo', indicators=None, save_path=None):
    """生成 A 股/港股图表"""
    indicators = indicators or {'rsi': True, 'macd': True, 'bb': False}
    
    print(f"正在获取 {symbol} 的数据...")
    df = get_akshare_data(symbol, period)
    
    if df.empty:
        raise Exception("数据为空")
    
    # 创建 3 个子图：K 线 + MACD + RSI
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), 
                                         gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # === 主图：K 线 + 均线 + 布林带 ===
    up = df['Close'] >= df['Open']
    down = ~up
    
    # 绘制 K 线
    for i, (idx, row) in enumerate(df.iterrows()):
        color = 'red' if row['Close'] >= row['Open'] else 'green'
        # 影线
        ax1.vlines(idx, row['Low'], row['High'], color=color, linewidth=0.8)
        # 实体
        ax1.plot([idx, idx], [row['Open'], row['Close']], color=color, linewidth=3)
    
    # 均线
    ma5 = df['Close'].rolling(5).mean()
    ma20 = df['Close'].rolling(20).mean()
    ax1.plot(df.index, ma5, label='MA5', color='orange', linewidth=1.5)
    ax1.plot(df.index, ma20, label='MA20', color='blue', linewidth=1.5)
    
    # 布林带
    if indicators.get('bb'):
        upper, mid, lower = calc_bbands(df['Close'])
        ax1.plot(df.index, upper, '--', color='gray', alpha=0.5, label='BB Upper')
        ax1.plot(df.index, mid, '-', color='gray', alpha=0.5, label='BB Mid')
        ax1.plot(df.index, lower, '--', color='gray', alpha=0.5, label='BB Lower')
        ax1.fill_between(df.index, upper, lower, alpha=0.1, color='gray')
    
    ax1.set_title(f'{symbol} K 线图 + 技术指标 ({period})', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel('价格')
    
    # === MACD 副图 ===
    macd, sig, hist = calc_macd(df['Close'])
    ax2.plot(df.index, macd, label='MACD', color='blue', linewidth=1.2)
    ax2.plot(df.index, sig, label='Signal', color='red', linewidth=1.2)
    ax2.bar(df.index, hist, color='gray', alpha=0.5, width=1, label='Hist')
    ax2.axhline(0, color='black', linewidth=0.5)
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylabel('MACD')
    
    # === RSI 副图 ===
    rsi = calc_rsi(df['Close'])
    ax3.plot(df.index, rsi, label='RSI(14)', color='purple', linewidth=1.2)
    ax3.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax3.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax3.fill_between(df.index, 70, 100, alpha=0.1, color='red')
    ax3.fill_between(df.index, 0, 30, alpha=0.1, color='green')
    ax3.legend(loc='upper left', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylabel('RSI')
    ax3.set_ylim(0, 100)
    ax3.set_xlabel('日期')
    
    # 保存图表 - 统一输出目录
    if save_path is None:
        save_dir = r'D:\OpenClaw\outputs\charts'
        os.makedirs(save_dir, exist_ok=True)
        clean_sym = str(symbol).replace('.', '_')
        save_path = os.path.join(save_dir, f'{clean_sym}_akshare.png')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存：{save_path}")
    return save_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python akshare_chart.py <股票代码> [周期]")
        print("示例：python akshare_chart.py 600519 6mo")
        sys.exit(1)
    
    symbol = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else '6mo'
    
    indicators = {'rsi': True, 'macd': True, 'bb': True}
    path = generate_akshare_chart(symbol, period, indicators)
    print(f"\n完成！图表路径：{path}")
