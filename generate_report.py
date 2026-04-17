#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成ETH完整报告
"""

import sys
import os
from datetime import datetime

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\scripts')

from features.complete_crypto_analyzer import analyze_complete

# 执行分析
print("正在分析 ETH-USD...")
result = analyze_complete('ETH-USD')

# 生成HTML报告
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETH-USD 分析报告 v4.4</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .score-card {{
            text-align: center;
            padding: 40px;
        }}
        .score {{
            font-size: 72px;
            font-weight: bold;
            color: #10b981;
        }}
        .decision {{
            font-size: 24px;
            color: #10b981;
            margin-top: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .metric {{
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .metric-label {{
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
        }}
        .signal {{
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .signal-bullish {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
        }}
        .signal-bearish {{
            background: #fee2e2;
            border-left: 4px solid #ef4444;
        }}
        .strength {{
            font-weight: bold;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 16px;
            color: #1f2937;
        }}
        .timestamp {{
            text-align: center;
            color: #6b7280;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ETH-USD 分析报告</h1>
        <p>Neo9527 Finance Skill v4.4 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="card score-card">
        <div class="score">{result['conclusion']['score']}/100</div>
        <div class="decision">{result['conclusion']['decision']}</div>
        <p style="color: #6b7280; margin-top: 10px;">置信度 {result['conclusion']['confidence']}%</p>
    </div>

    <div class="card">
        <div class="section-title">📊 市场数据</div>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">当前价格</div>
                <div class="metric-value">${result['market']['price']:,.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">24h涨跌</div>
                <div class="metric-value" style="color: {'#10b981' if result['market']['change_24h'] > 0 else '#ef4444'}">{result['market']['change_24h']:+.2f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">成交量</div>
                <div class="metric-value">${result['market']['volume_24h']/1e9:.2f}B</div>
            </div>
            <div class="metric">
                <div class="metric-label">市值</div>
                <div class="metric-value">${result['market']['market_cap']/1e9:.2f}B</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="section-title">📈 技术分析</div>
        <div class="grid">
            <div class="metric">
                <div class="metric-label">趋势</div>
                <div class="metric-value">{result['technical']['patterns']['trend_desc']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">RSI</div>
                <div class="metric-value">{result['technical']['indicators']['rsi']:.1f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">MACD信号</div>
                <div class="metric-value">{result['technical']['patterns']['macd_signal']}</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="section-title">🎯 信号汇总</div>
        <p><strong>看涨信号 ({len([s for s in result['signals'] if s['strength'] > 0])}项)</strong></p>
        {chr(10).join([f'<div class="signal signal-bullish"><span>[{s["category"]}] {s["name"]}: {s["signal"]}</span><span class="strength">{s["strength"]:+d}</span></div>' for s in result['signals'] if s['strength'] > 0])}
        
        <p style="margin-top: 16px;"><strong>看跌信号 ({len([s for s in result['signals'] if s['strength'] < 0])}项)</strong></p>
        {chr(10).join([f'<div class="signal signal-bearish"><span>[{s["category"]}] {s["name"]}: {s["signal"]}</span><span class="strength">{s["strength"]:+d}</span></div>' for s in result['signals'] if s['strength'] < 0])}
        
        <p style="margin-top: 20px; padding: 12px; background: #f3f4f6; border-radius: 6px;">
            <strong>总强度:</strong> {sum([s['strength'] for s in result['signals']]):+d} | 
            <strong>倾向:</strong> {'看涨' if sum([s['strength'] for s in result['signals']]) > 0 else '看跌'}
        </p>
    </div>

    <div class="card">
        <div class="section-title">💡 综合结论</div>
        <p style="line-height: 1.8; color: #374151;">{result['conclusion']['narrative']}</p>
    </div>

    <div class="card">
        <div class="section-title">📡 数据来源</div>
        <ul style="color: #6b7280; line-height: 1.8;">
            <li>CoinGecko - 市场数据</li>
            <li>yfinance - 技术指标</li>
            <li>DeFiLlama - 链上数据</li>
        </ul>
    </div>

    <div class="timestamp">
        <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Neo9527 Finance Skill v4.4 | GitHub: beautifulboy9527/Neo9527-unified-finance-skill</p>
    </div>
</body>
</html>
"""

# 保存报告
output_dir = r'D:\OpenClaw\outputs\reports'
os.makedirs(output_dir, exist_ok=True)

report_file = os.path.join(output_dir, f'ETH-USD_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ 报告已生成: {report_file}")
print(f"   大小: {os.path.getsize(report_file):,} 字节")
