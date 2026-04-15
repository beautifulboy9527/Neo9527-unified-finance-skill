#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Screener - 多条件选股器
基于 yfinance + AkShare 实现基本面和技术面筛选
"""

import sys
import os
import pandas as pd
from typing import Dict, List, Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.results = []
    
    def screen_us_stocks(self, 
                         pe_max: Optional[float] = None,
                         pb_max: Optional[float] = None,
                         roe_min: Optional[float] = None,
                         market_cap_min: Optional[float] = None,
                         volume_min: Optional[int] = None,
                         rsi_max: Optional[float] = None,
                         limit: int = 20) -> pd.DataFrame:
        """
        筛选美股
        
        Args:
            pe_max: 最大市盈率
            pb_max: 最大市净率
            roe_min: 最小 ROE
            market_cap_min: 最小市值 (美元)
            volume_min: 最小成交量
            rsi_max: 最大 RSI (超卖筛选)
            limit: 返回数量限制
        """
        import yfinance as yf
        
        # 标普 500 成分股 (简化版)
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
            'UNH', 'JNJ', 'XOM', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK',
            'ABBV', 'PFE', 'KO', 'PEP', 'COST', 'AVGO', 'TMO', 'WMT', 'DIS',
            'ABT', 'MCD', 'CSCO', 'ACN', 'VZ', 'ADBE', 'CRM', 'NKE', 'INTC',
            'TXN', 'QCOM', 'NEE', 'BMY', 'UPS', 'RTX', 'HON', 'AMGN', 'PM',
            'LOW', 'IBM', 'ORCL', 'SPGI', 'GS', 'CAT', 'DE', 'BA', 'BLK'
        ]
        
        print(f"正在筛选 {len(symbols)} 只美股...")
        
        results = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 获取基本面数据
                pe = info.get('forwardPE')
                pb = info.get('priceToBook')
                roe = info.get('returnOnEquity')
                market_cap = info.get('marketCap')
                volume = info.get('volume')
                price = info.get('regularMarketPrice') or info.get('currentPrice')
                
                # 获取 RSI
                hist = ticker.history(period='1mo')
                if not hist.empty:
                    close = hist['Close']
                    delta = close.diff()
                    gain = delta.clip(lower=0)
                    loss = -delta.clip(upper=0)
                    avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
                    avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
                    rs = avg_gain / avg_loss.replace(0, pd.NA)
                    rsi = 100 - (100 / (1 + rs))
                    current_rsi = rsi.iloc[-1] if not rsi.empty else None
                else:
                    current_rsi = None
                
                # 应用筛选条件
                if pe_max and (not pe or pe > pe_max):
                    continue
                if pb_max and (not pb or pb > pb_max):
                    continue
                if roe_min and (not roe or roe < roe_min):
                    continue
                if market_cap_min and (not market_cap or market_cap < market_cap_min):
                    continue
                if volume_min and (not volume or volume < volume_min):
                    continue
                if rsi_max and (not current_rsi or current_rsi > rsi_max):
                    continue
                
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': price,
                    'pe': pe,
                    'pb': pb,
                    'roe': roe * 100 if roe else None,  # 转为百分比
                    'market_cap': market_cap,
                    'volume': volume,
                    'rsi': round(current_rsi, 1) if current_rsi else None
                })
                
            except Exception as e:
                continue
        
        # 转换为 DataFrame 并排序
        df = pd.DataFrame(results)
        
        if not df.empty:
            df = df.sort_values('market_cap', ascending=False)
            df = df.head(limit)
        
        return df
    
    def screen_cn_stocks(self,
                         pe_max: Optional[float] = None,
                         pb_max: Optional[float] = None,
                         roe_min: Optional[float] = None,
                         limit: int = 20) -> pd.DataFrame:
        """
        筛选 A 股
        
        Args:
            pe_max: 最大市盈率
            pb_max: 最大市净率
            roe_min: 最小 ROE
            limit: 返回数量限制
        """
        try:
            import akshare as ak
            
            print("正在获取 A 股数据...")
            
            # 获取全部 A 股实时行情
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                return pd.DataFrame()
            
            # 重命名列
            rename_map = {
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'price',
                '市盈率 - 动': 'pe',
                '市净率': 'pb',
                '成交量': 'volume'
            }
            
            df = df.rename(columns=rename_map)
            
            # 应用筛选条件
            if pe_max:
                df = df[df['pe'] <= pe_max]
            if pb_max:
                df = df[df['pb'] <= pb_max]
            if roe_min:
                # A 股数据 ROE 需要另外获取，这里简化处理
                pass
            
            # 添加 ROE 数据 (需要额外 API 调用，这里简化)
            df['roe'] = None
            df['market_cap'] = df.get('总市值', None)
            df['rsi'] = None
            
            # 选择需要的列
            df = df[['symbol', 'name', 'price', 'pe', 'pb', 'roe', 'market_cap', 'volume', 'rsi']]
            
            # 排序并限制数量
            df = df.sort_values('market_cap', ascending=False)
            df = df.head(limit)
            
            return df
            
        except Exception as e:
            print(f"A 股筛选失败：{e}")
            return pd.DataFrame()
    
    def screen_by_technical(self,
                            market: str = 'us',
                            rsi_oversold: bool = False,
                            rsi_overbought: bool = False,
                            macd_bullish: bool = False,
                            limit: int = 20) -> pd.DataFrame:
        """
        技术面筛选
        
        Args:
            market: 市场 (us/cn/hk)
            rsi_oversold: RSI 超卖 (<30)
            rsi_overbought: RSI 超买 (>70)
            macd_bullish: MACD 金叉
            limit: 返回数量限制
        """
        if market == 'us':
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
                      'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS']
        elif market == 'cn':
            # 沪深 300 成分股 (简化)
            symbols = ['600519', '000858', '000333', '601318', '600030', '601166']
        else:
            symbols = []
        
        print(f"正在筛选技术信号 ({market})...")
        
        results = []
        
        for symbol in symbols:
            try:
                import yfinance as yf
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='3mo')
                
                if hist.empty:
                    continue
                
                close = hist['Close']
                
                # 计算 RSI
                delta = close.diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)
                avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
                avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
                rs = avg_gain / avg_loss.replace(0, pd.NA)
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                # 计算 MACD
                ema_fast = close.ewm(span=12, adjust=False, min_periods=12).mean()
                ema_slow = close.ewm(span=26, adjust=False, min_periods=26).mean()
                macd = ema_fast - ema_slow
                signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
                macd_bull = macd.iloc[-1] > signal.iloc[-1]
                
                # 应用筛选条件
                if rsi_oversold and current_rsi >= 30:
                    continue
                if rsi_overbought and current_rsi <= 70:
                    continue
                if macd_bullish and not macd_bull:
                    continue
                
                info = ticker.info
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': info.get('regularMarketPrice'),
                    'rsi': round(current_rsi, 1),
                    'macd_bullish': macd_bull,
                    'signal': 'oversold' if rsi_oversold else ('overbought' if rsi_overbought else 'macd_bullish')
                })
                
            except Exception:
                continue
        
        return pd.DataFrame(results).head(limit)


def format_table(df: pd.DataFrame) -> str:
    """格式化 DataFrame 为表格"""
    if df.empty:
        return "无符合条件的股票"
    
    # 格式化数值列
    for col in ['pe', 'pb', 'roe', 'rsi']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else 'N/A')
    
    # 格式化市值
    if 'market_cap' in df.columns:
        df['market_cap'] = df['market_cap'].apply(
            lambda x: f"{x/1e9:.1f}B" if pd.notna(x) and x > 1e9 else f"{x/1e6:.1f}M" if pd.notna(x) else 'N/A'
        )
    
    return df.to_string(index=False)


if __name__ == '__main__':
    screener = StockScreener()
    
    if len(sys.argv) < 2:
        print("用法：python stock_screener.py <筛选类型> [参数]")
        print("\n筛选类型:")
        print("  fundamental --pe-max 20 --roe-min 15  # 基本面筛选")
        print("  technical --rsi-oversold              # 技术面筛选")
        print("  cn --pe-max 30                         # A 股筛选")
        sys.exit(1)
    
    screen_type = sys.argv[1]
    
    if screen_type == 'fundamental':
        # 解析参数
        pe_max = float(sys.argv[sys.argv.index('--pe-max') + 1]) if '--pe-max' in sys.argv else None
        pb_max = float(sys.argv[sys.argv.index('--pb-max') + 1]) if '--pb-max' in sys.argv else None
        roe_min = float(sys.argv[sys.argv.index('--roe-min') + 1]) if '--roe-min' in sys.argv else None
        limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 20
        
        print("\n=== 美股基本面筛选 ===")
        df = screener.screen_us_stocks(pe_max=pe_max, pb_max=pb_max, roe_min=roe_min, limit=limit)
        print(format_table(df))
    
    elif screen_type == 'technical':
        rsi_oversold = '--rsi-oversold' in sys.argv
        rsi_overbought = '--rsi-overbought' in sys.argv
        macd_bullish = '--macd-bullish' in sys.argv
        limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 20
        
        print("\n=== 技术面筛选 ===")
        df = screener.screen_by_technical(
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            macd_bullish=macd_bullish,
            limit=limit
        )
        print(format_table(df))
    
    elif screen_type == 'cn':
        pe_max = float(sys.argv[sys.argv.index('--pe-max') + 1]) if '--pe-max' in sys.argv else None
        limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 20
        
        print("\n=== A 股筛选 ===")
        df = screener.screen_cn_stocks(pe_max=pe_max, limit=limit)
        print(format_table(df))
    
    else:
        print(f"未知筛选类型：{screen_type}")
