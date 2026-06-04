#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级技术图表模块 - 完整集成自 stock-market-pro skill
生成高清 PNG 图表，支持 RSI/MACD/布林带/VWAP/ATR 指标
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 输出目录
OUTPUT_DIR = Path(r'D:\OpenClaw\outputs\charts')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TechnicalChartGenerator:
    """
    技术图表生成器 - 完整集成自 stock-market-pro
    
    能力:
    - K线图 / 折线图
    - RSI 指标
    - MACD 指标
    - 布林带
    - VWAP
    - ATR
    - 高清 PNG 输出
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
    def _normalize_for_yfinance(self, symbol: str) -> str:
        """
        标准化股票代码为 yfinance 格式
        A股需要添加 .SS 或 .SZ 后缀
        """
        import re
        
        # 如果已经有后缀，直接返回
        if '.' in symbol:
            return symbol
        
        # A股: 6位数字
        if re.match(r'^[0-9]{6}$', symbol):
            if symbol.startswith('6'):
                return f"{symbol}.SS"  # 上海
            elif symbol.startswith(('0', '3')):
                return f"{symbol}.SZ"  # 深圳
            else:
                return f"{symbol}.SS"  # 默认上海
        
        # 港股: 5位数字
        if re.match(r'^[0-9]{5}$', symbol):
            return f"{symbol}.HK"
        
        # 美股: 纯字母，无需转换
        return symbol
    
    def _has_data(self, s) -> bool:
        """检查数据是否有效"""
        try:
            import pandas as pd
            return s is not None and hasattr(s, "dropna") and not s.dropna().empty
        except:
            return False
    
    def _calc_rsi(self, close, window: int = 14):
        """计算 RSI"""
        import pandas as pd
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
        avg_loss = loss.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calc_macd(self, close, fast: int = 12, slow: int = 26, signal: int = 9):
        """计算 MACD"""
        ema_fast = close.ewm(span=fast, adjust=False, min_periods=fast).mean()
        ema_slow = close.ewm(span=slow, adjust=False, min_periods=slow).mean()
        macd = ema_fast - ema_slow
        sig = macd.ewm(span=signal, adjust=False, min_periods=signal).mean()
        hist = macd - sig
        return macd, sig, hist
    
    def _calc_bbands(self, close, window: int = 20, n_std: float = 2.0):
        """计算布林带"""
        import pandas as pd
        ma = close.rolling(window=window, min_periods=window).mean()
        std = close.rolling(window=window, min_periods=window).std(ddof=0)
        upper = ma + n_std * std
        lower = ma - n_std * std
        return upper, ma, lower
    
    def _calc_vwap(self, df):
        """计算 VWAP"""
        import pandas as pd
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vol = df['Volume'].fillna(0)
        tpv = (typical_price * vol).cumsum()
        vwap = tpv / vol.cumsum().replace(0, pd.NA)
        return vwap
    
    def _calc_atr(self, df, window: int = 14):
        """计算 ATR"""
        import pandas as pd
        high = df['High']
        low = df['Low']
        close = df['Close']
        prev_close = close.shift(1)
        tr = pd.concat([
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/window, adjust=False, min_periods=window).mean()
        return atr
    
    def generate_chart(
        self,
        period: str = '3mo',
        chart_type: str = 'candle',
        rsi: bool = False,
        macd: bool = False,
        bb: bool = False,
        vwap: bool = False,
        atr: bool = False
    ) -> Dict:
        """
        生成技术图表
        
        Args:
            period: 周期 (1mo, 3mo, 6mo, 1y)
            chart_type: 图表类型 (candle, line)
            rsi: 是否显示 RSI
            macd: 是否显示 MACD
            bb: 是否显示布林带
            vwap: 是否显示 VWAP
            atr: 是否显示 ATR
            
        Returns:
            {
                'symbol': 股票代码,
                'chart_path': 图表路径,
                'data_source': 数据源,
                'error': 错误信息
            }
        """
        result = {
            'symbol': self.symbol,
            'chart_path': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            import pandas as pd
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # 标准化股票代码 (A股需要加后缀)
            yf_symbol = self._normalize_for_yfinance(self.symbol)
            
            # 获取数据
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                result['error'] = '无历史数据'
                return result
            
            # 确保索引是 DatetimeIndex
            if not isinstance(hist.index, pd.DatetimeIndex):
                hist.index = pd.to_datetime(hist.index)
            
            # 尝试使用 mplfinance 生成专业图表
            try:
                import mplfinance as mpf
                
                return self._generate_mpf_chart(
                    hist, chart_type, rsi, macd, bb, vwap, atr
                )
                
            except ImportError:
                # 降级使用 matplotlib
                return self._generate_mpl_chart(
                    hist, chart_type, rsi, macd, bb, vwap, atr
                )
            
        except ImportError as e:
            result['error'] = f'缺少依赖: {str(e)}'
            return result
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _generate_mpf_chart(
        self,
        hist,
        chart_type: str,
        rsi: bool,
        macd: bool,
        bb: bool,
        vwap: bool,
        atr: bool
    ) -> Dict:
        """使用 mplfinance 生成专业图表"""
        import pandas as pd
        import mplfinance as mpf
        
        result = {
            'symbol': self.symbol,
            'chart_path': None,
            'data_source': 'yfinance_mplfinance',
            'error': None
        }
        
        # 输出路径
        chart_path = OUTPUT_DIR / f"{self.symbol}_technical.png"
        
        # 市场颜色设置
        mc = mpf.make_marketcolors(up='red', down='green', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', y_on_right=False)
        
        addplots = []
        panel_ratios = [6, 2]  # 主图 + 成交量
        next_panel = 2
        close = hist['Close']
        
        # 布林带 (主图叠加)
        if bb:
            upper, mid, lower = self._calc_bbands(close)
            if self._has_data(upper):
                addplots.append(mpf.make_addplot(upper, color='gray', width=0.8, panel=0))
                addplots.append(mpf.make_addplot(mid, color='dimgray', width=0.8, panel=0))
                addplots.append(mpf.make_addplot(lower, color='gray', width=0.8, panel=0))
        
        # VWAP (主图叠加)
        if vwap:
            vwap_series = self._calc_vwap(hist)
            if self._has_data(vwap_series):
                addplots.append(mpf.make_addplot(vwap_series, color='purple', width=1.0, panel=0))
        
        # RSI 面板
        if rsi:
            rsi_series = self._calc_rsi(close)
            if self._has_data(rsi_series):
                rsi_panel = next_panel
                next_panel += 1
                panel_ratios.append(2)
                addplots.append(mpf.make_addplot(rsi_series, panel=rsi_panel, color='orange', width=1.0, ylabel='RSI'))
                addplots.append(mpf.make_addplot(pd.Series(70, index=hist.index), panel=rsi_panel, color='gray', linestyle='--', width=0.7))
                addplots.append(mpf.make_addplot(pd.Series(30, index=hist.index), panel=rsi_panel, color='gray', linestyle='--', width=0.7))
        
        # MACD 面板
        if macd:
            macd_line, signal_line, histogram = self._calc_macd(close)
            if self._has_data(macd_line):
                macd_panel = next_panel
                next_panel += 1
                panel_ratios.append(2)
                addplots.append(mpf.make_addplot(macd_line, panel=macd_panel, color='blue', width=1.0, ylabel='MACD'))
                addplots.append(mpf.make_addplot(signal_line, panel=macd_panel, color='red', width=1.0))
                bar_colors = histogram.apply(lambda x: 'red' if x >= 0 else 'green').tolist()
                addplots.append(mpf.make_addplot(histogram, panel=macd_panel, type='bar', color=bar_colors, alpha=0.35))
        
        # ATR 面板
        if atr:
            atr_series = self._calc_atr(hist)
            if self._has_data(atr_series):
                atr_panel = next_panel
                next_panel += 1
                panel_ratios.append(2)
                addplots.append(mpf.make_addplot(atr_series, panel=atr_panel, color='teal', width=1.0, ylabel='ATR'))
        
        # 生成图表
        chart_type_mpf = 'candle' if chart_type == 'candle' else 'line'
        
        mpf.plot(
            hist,
            type=chart_type_mpf,
            style=s,
            title=f'{self.symbol} Technical Chart',
            ylabel='Price',
            volume=True,
            addplot=addplots if addplots else None,
            panel_ratios=panel_ratios,
            figsize=(14, 10),
            savefig=str(chart_path)
        )
        
        result['chart_path'] = str(chart_path)
        result['indicators'] = {
            'rsi': rsi,
            'macd': macd,
            'bb': bb,
            'vwap': vwap,
            'atr': atr
        }
        
        return result
    
    def _generate_mpl_chart(
        self,
        hist,
        chart_type: str,
        rsi: bool,
        macd: bool,
        bb: bool,
        vwap: bool,
        atr: bool
    ) -> Dict:
        """使用 matplotlib 生成图表 (降级方案)"""
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        result = {
            'symbol': self.symbol,
            'chart_path': None,
            'data_source': 'yfinance_matplotlib',
            'error': None
        }
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 计算需要的面板数
        panels = 1  # 主图
        if rsi:
            panels += 1
        if macd:
            panels += 1
        if atr:
            panels += 1
        
        # 创建子图
        fig, axes = plt.subplots(panels, 1, figsize=(14, 4 * panels), sharex=True)
        if panels == 1:
            axes = [axes]
        
        close = hist['Close']
        panel_idx = 0
        
        # 主图
        ax_main = axes[panel_idx]
        
        # 绘制价格
        if chart_type == 'line':
            ax_main.plot(hist.index, close, 'b-', linewidth=1.5, label='价格')
        else:
            # 简化的 K 线图
            for idx, row in hist.iterrows():
                color = 'red' if row['Close'] >= row['Open'] else 'green'
                ax_main.bar(idx, row['Close'] - row['Open'], bottom=row['Open'], color=color, width=0.8, alpha=0.8)
        
        # 布林带
        if bb:
            upper, mid, lower = self._calc_bbands(close)
            ax_main.plot(hist.index, upper, 'gray', linewidth=0.8, linestyle='--', label='BB上轨')
            ax_main.plot(hist.index, mid, 'gray', linewidth=0.8, label='BB中轨')
            ax_main.plot(hist.index, lower, 'gray', linewidth=0.8, linestyle='--', label='BB下轨')
            ax_main.fill_between(hist.index, upper, lower, alpha=0.1, color='gray')
        
        # VWAP
        if vwap:
            vwap_series = self._calc_vwap(hist)
            ax_main.plot(hist.index, vwap_series, 'purple', linewidth=1.0, label='VWAP')
        
        ax_main.set_ylabel('价格')
        ax_main.set_title(f'{self.symbol} 技术图表')
        ax_main.legend(loc='best', fontsize=8)
        ax_main.grid(True, alpha=0.3)
        
        # RSI 面板
        if rsi:
            panel_idx += 1
            ax_rsi = axes[panel_idx]
            rsi_series = self._calc_rsi(close)
            ax_rsi.plot(hist.index, rsi_series, 'orange', linewidth=1.0, label='RSI')
            ax_rsi.axhline(y=70, color='gray', linestyle='--', linewidth=0.8)
            ax_rsi.axhline(y=30, color='gray', linestyle='--', linewidth=0.8)
            ax_rsi.fill_between(hist.index, 30, 70, alpha=0.1, color='yellow')
            ax_rsi.set_ylabel('RSI')
            ax_rsi.legend(loc='best', fontsize=8)
            ax_rsi.grid(True, alpha=0.3)
        
        # MACD 面板
        if macd:
            panel_idx += 1
            ax_macd = axes[panel_idx]
            macd_line, signal_line, histogram = self._calc_macd(close)
            ax_macd.plot(hist.index, macd_line, 'blue', linewidth=1.0, label='MACD')
            ax_macd.plot(hist.index, signal_line, 'red', linewidth=1.0, label='Signal')
            
            # 柱状图
            colors = ['red' if v >= 0 else 'green' for v in histogram]
            ax_macd.bar(hist.index, histogram, color=colors, alpha=0.5, width=0.8)
            ax_macd.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
            ax_macd.set_ylabel('MACD')
            ax_macd.legend(loc='best', fontsize=8)
            ax_macd.grid(True, alpha=0.3)
        
        # ATR 面板
        if atr:
            panel_idx += 1
            ax_atr = axes[panel_idx]
            atr_series = self._calc_atr(hist)
            ax_atr.plot(hist.index, atr_series, 'teal', linewidth=1.0, label='ATR')
            ax_atr.set_ylabel('ATR')
            ax_atr.legend(loc='best', fontsize=8)
            ax_atr.grid(True, alpha=0.3)
        
        # 设置 X 轴格式
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        axes[-1].xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 保存
        chart_path = OUTPUT_DIR / f"{self.symbol}_technical.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        result['chart_path'] = str(chart_path)
        result['indicators'] = {
            'rsi': rsi,
            'macd': macd,
            'bb': bb,
            'vwap': vwap,
            'atr': atr
        }
        
        return result
    
    def generate_quick_chart(self, period: str = '3mo') -> Dict:
        """快速生成基础图表 (无指标)"""
        return self.generate_chart(period=period)
    
    def generate_full_chart(self, period: str = '3mo') -> Dict:
        """生成完整图表 (包含所有指标)"""
        return self.generate_chart(
            period=period,
            rsi=True,
            macd=True,
            bb=True,
            vwap=True,
            atr=True
        )


def generate_chart(
    symbol: str,
    period: str = '3mo',
    rsi: bool = False,
    macd: bool = False,
    bb: bool = False,
    vwap: bool = False,
    atr: bool = False
) -> Dict:
    """生成技术图表入口"""
    generator = TechnicalChartGenerator(symbol)
    return generator.generate_chart(period, 'candle', rsi, macd, bb, vwap, atr)


def generate_full_chart(symbol: str, period: str = '3mo') -> Dict:
    """生成完整图表 (所有指标)"""
    generator = TechnicalChartGenerator(symbol)
    return generator.generate_full_chart(period)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='高级技术图表 - 完整集成自 stock-market-pro')
    parser.add_argument('--symbol', required=True, help='股票代码')
    parser.add_argument('--period', default='3mo', help='周期')
    parser.add_argument('--rsi', action='store_true', help='显示 RSI')
    parser.add_argument('--macd', action='store_true', help='显示 MACD')
    parser.add_argument('--bb', action='store_true', help='显示布林带')
    parser.add_argument('--vwap', action='store_true', help='显示 VWAP')
    parser.add_argument('--atr', action='store_true', help='显示 ATR')
    parser.add_argument('--full', action='store_true', help='显示所有指标')
    
    args = parser.parse_args()
    
    generator = TechnicalChartGenerator(args.symbol)
    
    if args.full:
        result = generator.generate_full_chart(args.period)
    else:
        result = generator.generate_chart(
            period=args.period,
            rsi=args.rsi,
            macd=args.macd,
            bb=args.bb,
            vwap=args.vwap,
            atr=args.atr
        )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
