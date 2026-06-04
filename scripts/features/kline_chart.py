#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线图数据生成器
为 lightweight-charts 生成标准格式数据
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

if __name__ != '__main__':
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class KlineDataGenerator:
    """K线数据生成器"""
    
    def __init__(self):
        self.cache = {}
    
    def get_kline_data(self, symbol: str, period: str = '3mo') -> Dict:
        """
        获取K线数据 (lightweight-charts 格式)
        
        Args:
            symbol: 交易对 (BTC-USD)
            period: 时间范围
            
        Returns:
            {
                'candlestick': K线数据,
                'ma5': MA5数据,
                'ma10': MA10数据,
                'ma20': MA20数据,
                'volume': 成交量数据,
                'metadata': 元数据
            }
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {'error': 'No data available'}
            
            # K线数据
            candlestick = []
            for idx, row in hist.iterrows():
                candlestick.append({
                    'time': int(idx.timestamp()),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2)
                })
            
            # 均线数据
            def generate_ma_data(series: pd.Series) -> List[Dict]:
                data = []
                for idx, val in series.items():
                    if pd.notna(val):
                        data.append({
                            'time': int(idx.timestamp()),
                            'value': round(float(val), 2)
                        })
                return data
            
            ma5_data = generate_ma_data(hist['Close'].rolling(5).mean())
            ma10_data = generate_ma_data(hist['Close'].rolling(10).mean())
            ma20_data = generate_ma_data(hist['Close'].rolling(20).mean())
            
            # 成交量数据
            volume = []
            for idx, row in hist.iterrows():
                volume.append({
                    'time': int(idx.timestamp()),
                    'value': float(row['Volume']),
                    'color': '#26a69a' if row['Close'] >= row['Open'] else '#ef5350'
                })
            
            # 元数据
            metadata = {
                'symbol': symbol,
                'period': period,
                'start_time': hist.index[0].strftime('%Y-%m-%d'),
                'end_time': hist.index[-1].strftime('%Y-%m-%d'),
                'data_points': len(candlestick),
                'latest_price': candlestick[-1]['close'],
                'price_change': round(
                    (candlestick[-1]['close'] - candlestick[0]['close']) / candlestick[0]['close'] * 100, 2
                )
            }
            
            return {
                'candlestick': candlestick,
                'ma5': ma5_data,
                'ma10': ma10_data,
                'ma20': ma20_data,
                'volume': volume,
                'metadata': metadata,
                'data_source': 'yfinance'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def to_json(self, data: Dict) -> str:
        """转换为 JSON 字符串"""
        import json
        return json.dumps(data, indent=2)


def get_kline_data(symbol: str, period: str = '3mo') -> Dict:
    """便捷函数"""
    generator = KlineDataGenerator()
    return generator.get_kline_data(symbol, period)


if __name__ == '__main__':
    print("测试 K 线数据生成...")
    print("=" * 60)
    
    data = get_kline_data('BTC-USD', '3mo')
    
    if 'error' in data:
        print(f"❌ 错误: {data['error']}")
    else:
        print(f"✅ 数据点数: {data['metadata']['data_points']}")
        print(f"✅ 时间范围: {data['metadata']['start_time']} ~ {data['metadata']['end_time']}")
        print(f"✅ 最新价格: ${data['metadata']['latest_price']:,.2f}")
        print(f"✅ 价格变化: {data['metadata']['price_change']:+.2f}%")
        print()
        print(f"✅ K线数据: {len(data['candlestick'])} 条")
        print(f"✅ MA5数据: {len(data['ma5'])} 条")
        print(f"✅ MA10数据: {len(data['ma10'])} 条")
        print(f"✅ MA20数据: {len(data['ma20'])} 条")
        print(f"✅ 成交量数据: {len(data['volume'])} 条")
        
        print()
        print("最新K线:")
        print(f"  时间: {datetime.fromtimestamp(data['candlestick'][-1]['time'])}")
        print(f"  开: ${data['candlestick'][-1]['open']:,.2f}")
        print(f"  高: ${data['candlestick'][-1]['high']:,.2f}")
        print(f"  低: ${data['candlestick'][-1]['low']:,.2f}")
        print(f"  收: ${data['candlestick'][-1]['close']:,.2f}")
    
    print("=" * 60)
