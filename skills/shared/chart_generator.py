#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight Charts 模块
生成交互式 K 线图表
"""

import sys
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
import base64

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ChartGenerator:
    """使用 lightweight-charts 生成 K 线图"""
    
    def __init__(self):
        self.name = "ChartGenerator"
        self.version = "1.0.0"
    
    def generate_candlestick_html(
        self,
        ohlcv_data: List[Dict],
        title: str = "K线图",
        volume: bool = True,
        width: int = 800,
        height: int = 400
    ) -> str:
        """
        生成交互式 K 线图 HTML
        
        Args:
            ohlcv_data: OHLCV 数据列表
            title: 图表标题
            volume: 是否显示成交量
            width: 图表宽度
            height: 图表高度
            
        Returns:
            HTML 字符串
        """
        if not PANDAS_AVAILABLE:
            return "<p>需要安装 pandas</p>"
        
        # 准备数据
        candles = []
        volumes = []
        
        for row in ohlcv_data:
            candle = {
                'time': row.get('date', row.get('time', '')),
                'open': float(row.get('open', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
                'close': float(row.get('close', 0)),
            }
            candles.append(candle)
            
            if volume:
                vol = {
                    'time': row.get('date', row.get('time', '')),
                    'value': float(row.get('volume', 0)),
                    'color': 'rgba(0, 150, 136, 0.5)' if row.get('close', 0) >= row.get('open', 0) else 'rgba(255, 82, 82, 0.5)'
                }
                volumes.append(vol)
        
        # 生成 HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .chart-container {{ width: {width}px; height: {height}px; }}
        .title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="title">{title}</div>
    <div id="chart" class="chart-container"></div>
    
    <script>
        const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
            layout: {{
                background: {{ type: 'solid', color: 'white' }},
                textColor: '#333',
            }},
            grid: {{
                vertLines: {{ color: '#f0f0f0' }},
                horzLines: {{ color: '#f0f0f0' }},
            }},
            width: {width},
            height: {height},
        }});
        
        const candlestickSeries = chart.addCandlestickSeries({{
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        }});
        
        candlestickSeries.setData({json.dumps(candles)});
        
        {' '.join(self._generate_volume_series(volumes) if volume else '')}
        
        chart.timeScale().fitContent();
    </script>
</body>
</html>'''
        
        return html
    
    def _generate_volume_series(self, volumes: List[Dict]) -> str:
        """生成成交量系列代码"""
        if not volumes:
            return ''
        
        return f'''
        const volumeSeries = chart.addHistogramSeries({{
            color: '#26a69a',
            priceFormat: {{
                type: 'volume',
            }},
            priceScaleId: '',
            scaleMargins: {{
                top: 0.8,
                bottom: 0,
            }},
        }});
        
        volumeSeries.setData({json.dumps(volumes)});
        '''
    
    def generate_line_chart(
        self,
        data: List[Dict],
        title: str = "折线图",
        width: int = 800,
        height: int = 300
    ) -> str:
        """
        生成折线图
        
        Args:
            data: 数据列表 [{'time': '2024-01-01', 'value': 100}]
            title: 图表标题
            width: 图表宽度
            height: 图表高度
            
        Returns:
            HTML 字符串
        """
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .chart-container {{ width: {width}px; height: {height}px; }}
        .title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="title">{title}</div>
    <div id="chart" class="chart-container"></div>
    
    <script>
        const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
            layout: {{
                background: {{ type: 'solid', color: 'white' }},
                textColor: '#333',
            }},
            width: {width},
            height: {height},
        }});
        
        const lineSeries = chart.addLineSeries({{
            color: '#2962FF',
            lineWidth: 2,
        }});
        
        lineSeries.setData({json.dumps(data)});
        
        chart.timeScale().fitContent();
    </script>
</body>
</html>'''
        
        return html
    
    def save_chart(self, html: str, filename: str) -> str:
        """保存图表到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        return filename


# 快速使用函数
def generate_candlestick(ohlcv_data: List[Dict], title: str = "K线图") -> str:
    """生成 K 线图 HTML"""
    generator = ChartGenerator()
    return generator.generate_candlestick_html(ohlcv_data, title)


def generate_line(data: List[Dict], title: str = "折线图") -> str:
    """生成折线图 HTML"""
    generator = ChartGenerator()
    return generator.generate_line_chart(data, title)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("Lightweight Charts 测试")
    print("=" * 60)
    
    # 测试数据
    test_data = [
        {'date': '2024-01-01', 'open': 100, 'high': 105, 'low': 98, 'close': 103, 'volume': 1000},
        {'date': '2024-01-02', 'open': 103, 'high': 108, 'low': 102, 'close': 107, 'volume': 1200},
        {'date': '2024-01-03', 'open': 107, 'high': 110, 'low': 105, 'close': 106, 'volume': 1100},
        {'date': '2024-01-04', 'open': 106, 'high': 109, 'low': 104, 'close': 108, 'volume': 900},
        {'date': '2024-01-05', 'open': 108, 'high': 112, 'low': 107, 'close': 111, 'volume': 1300},
    ]
    
    generator = ChartGenerator()
    
    # 生成 K 线图
    html = generator.generate_candlestick_html(test_data, title="AAPL K线图")
    output_file = r'D:\OpenClaw\outputs\charts\test_candlestick.html'
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    generator.save_chart(html, output_file)
    
    print(f"\n✅ K线图已生成: {output_file}")
    print(f"文件大小: {len(html)} 字符")
