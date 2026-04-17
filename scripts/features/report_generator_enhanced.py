#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版报告生成器 (v4.5)
集成所有Skills + K线图 + 链上数据
"""

import sys
import os
from datetime import datetime
from typing import Dict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_enhanced_report(symbol: str, output_dir: str = r"D:\OpenClaw\outputs\reports") -> str:
    """
    生成增强版报告 - 集成所有Skills
    
    Args:
        symbol: 交易对 (ETH-USD)
        output_dir: 输出目录
        
    Returns:
        报告文件路径
    """
    
    # 导入所有模块
    from features.complete_crypto_analyzer import analyze_complete
    from features.kline_chart import get_kline_data
    from features.onchain_data import get_onchain_data
    
    # Skills导入
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills', 'onchain-skill'))
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'skills'))
        from base_skill import SkillInput
        from whale import OnchainWhaleSkill
        whale_skill_available = True
    except:
        whale_skill_available = False
    
    print(f"正在分析 {symbol}...")
    
    # 1. 完整市场分析
    result = analyze_complete(symbol)
    
    # 2. K线数据
    print("获取K线数据...")
    kline_data = get_kline_data(symbol, '3mo')
    
    # 3. 链上数据（增强版）
    print("获取链上数据...")
    base_symbol = symbol.split('-')[0]
    
    # 旧版链上数据
    onchain_data = get_onchain_data(base_symbol)
    
    # 新版鲸鱼分析
    if whale_skill_available:
        try:
            whale_skill = OnchainWhaleSkill()
            whale_result = whale_skill.execute(SkillInput(symbol=base_symbol, market='crypto'))
            whale_data = whale_result.data if whale_result.success else {}
        except:
            whale_data = {}
    else:
        whale_data = {}
    
    # 4. 生成HTML
    html = generate_html_report(symbol, result, kline_data, onchain_data, whale_data)
    
    # 5. 保存
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f'{symbol}_report_v4.5_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {report_file}")
    return report_file


def generate_html_report(symbol: str, result: Dict, kline_data: Dict, onchain_data: Dict, whale_data: Dict) -> str:
    """生成完整HTML报告"""
    
    # 提取基础符号
    base_symbol = symbol.split('-')[0]
    
    market = result.get('market', {})
    technical = result.get('technical', {})
    signals = result.get('signals', [])
    conclusion = result.get('conclusion', {})
    
    # K线数据
    candlestick_js = "[]"
    ma5_js = "[]"
    ma10_js = "[]"
    volume_js = "[]"
    
    if kline_data and 'candles' in kline_data:
        candles = kline_data['candles']
        candlestick_js = "[" + ",".join([
            f'{{"time": {c["time"]}, "open": {c["open"]}, "high": {c["high"]}, "low": {c["low"]}, "close": {c["close"]}}}'
            for c in candles
        ]) + "]"
        
        if 'ma5' in kline_data:
            ma5_js = "[" + ",".join([
                f'{{"time": {m["time"]}, "value": {m["value"]}}}'
                for m in kline_data['ma5']
            ]) + "]"
        
        if 'ma10' in kline_data:
            ma10_js = "[" + ",".join([
                f'{{"time": {m["time"]}, "value": {m["value"]}}}'
                for m in kline_data['ma10']
            ]) + "]"
        
        if 'volume' in kline_data:
            volume_js = "[" + ",".join([
                f'{{"time": {v["time"]}, "value": {v["value"]}, "color": "{v.get("color", "#26a69a")}"}}'
                for v in kline_data['volume']
            ]) + "]"
    
    # 信号HTML
    bullish_signals = [s for s in signals if s['strength'] > 0]
    bearish_signals = [s for s in signals if s['strength'] < 0]
    
    bullish_html = "\n".join([
        f'<div class="signal signal-bullish"><span>[{s["category"]}] {s["name"]}: {s["signal"]}</span><span class="strength">+{s["strength"]}</span></div>'
        for s in bullish_signals
    ])
    
    bearish_html = "\n".join([
        f'<div class="signal signal-bearish"><span>[{s["category"]}] {s["name"]}: {s["signal"]}</span><span class="strength">{s["strength"]}</span></div>'
        for s in bearish_signals
    ])
    
    # 链上数据HTML
    onchain_html = ""
    if whale_data:
        whale_summary = whale_data.get('whale_summary', {})
        onchain_html = f"""
        <div class="card">
            <h3 class="section-title">🐋 链上数据</h3>
            <div class="grid">
                <div class="metric">
                    <div class="metric-label">鲸鱼偏向</div>
                    <div class="metric-value">{whale_summary.get('whale_bias', 'neutral')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">生态TVL</div>
                    <div class="metric-value">${whale_summary.get('ecosystem_tvl', 0)/1e9:.2f}B</div>
                </div>
                <div class="metric">
                    <div class="metric-label">7日变化</div>
                    <div class="metric-value">{whale_summary.get('avg_protocol_change_7d', 0):+.2f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">匹配协议</div>
                    <div class="metric-value">{whale_summary.get('matched_protocols', 0)} 个</div>
                </div>
            </div>
            {f'<p style="margin-top: 16px; color: #6b7280;"><strong>专业解读:</strong> {whale_data.get("commentary", "")}</p>' if whale_data.get('commentary') else ''}
        </div>
        """
    elif onchain_data:
        whale = onchain_data.get('whale', {})
        defi = onchain_data.get('defi', {})
        onchain_html = f"""
        <div class="card">
            <h3 class="section-title">🐋 链上数据</h3>
            <div class="grid">
                <div class="metric">
                    <div class="metric-label">鲸鱼净流入</div>
                    <div class="metric-value">{whale.get('net_flow', 0):+,} {base_symbol}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">状态</div>
                    <div class="metric-value">{whale.get('status', 'unknown')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">总TVL</div>
                    <div class="metric-value">${defi.get('total_tvl', 0)/1e9:.2f}B</div>
                </div>
                <div class="metric">
                    <div class="metric-label">协议数</div>
                    <div class="metric-value">{defi.get('protocols', 0)} 个</div>
                </div>
            </div>
            <p style="margin-top: 16px; color: #6b7280;">{whale.get('signal', '')}</p>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 投资分析报告 v4.5</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 10px; font-weight: 700; }}
        .header .subtitle {{ font-size: 16px; opacity: 0.9; }}
        .header .meta {{ margin-top: 20px; font-size: 14px; opacity: 0.8; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            border-left: 5px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .card.highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .metric {{
            padding: 20px;
            background: white;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-label {{ color: #6b7280; font-size: 14px; margin-bottom: 8px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1f2937; }}
        .score-display {{ text-align: center; padding: 20px; }}
        .score-value {{ font-size: 72px; font-weight: bold; }}
        .score-label {{ font-size: 18px; opacity: 0.9; margin-top: 10px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #667eea;
            color: white;
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
        .strength {{ font-weight: bold; }}
        #kline-chart {{ width: 100%; height: 450px; margin-bottom: 10px; }}
        #volume-chart {{ width: 100%; height: 150px; }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 13px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{symbol} 投资分析报告</h1>
            <div class="subtitle">多维度分析 · 专业投资建议</div>
            <div class="meta">
                分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 报告版本: v4.5 (增强版)
            </div>
        </div>
        
        <div class="content">
            <!-- 综合评分 -->
            <div class="section">
                <h2 class="section-title">一、综合评分</h2>
                <div class="card highlight">
                    <div class="score-display">
                        <div class="score-value">{conclusion.get('score', 0)}/100</div>
                        <div class="score-label">{conclusion.get('decision', 'HOLD')} | 置信度 {conclusion.get('confidence', 0)}%</div>
                    </div>
                </div>
            </div>
            
            <!-- 市场数据 -->
            <div class="section">
                <h2 class="section-title">二、市场数据</h2>
                <table>
                    <tr><th>指标</th><th>数值</th><th>说明</th></tr>
                    <tr><td>当前价格</td><td><strong>${market.get('price', 0):,.2f}</strong></td><td>实时价格</td></tr>
                    <tr><td>24h涨跌</td><td style="color: {'#10b981' if market.get('change_24h', 0) > 0 else '#ef4444'}">{market.get('change_24h', 0):+.2f}%</td><td>{'📈 上涨' if market.get('change_24h', 0) > 0 else '📉 下跌'}</td></tr>
                    <tr><td>24h成交量</td><td>${market.get('volume_24h', 0)/1e9:.2f}B</td><td>市场活跃度</td></tr>
                    <tr><td>市值</td><td>${market.get('market_cap', 0)/1e9:.2f}B</td><td>市场规模</td></tr>
                </table>
            </div>
            
            <!-- K线图 -->
            <div class="section">
                <h2 class="section-title">三、价格走势 (交互式K线图)</h2>
                <div id="kline-chart"></div>
                <div id="volume-chart"></div>
                <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 13px; color: #666;">
                    <span>🔵 MA5</span>
                    <span>🟢 MA10</span>
                    <span style="margin-left: auto;">💡 可缩放/拖拽</span>
                </div>
            </div>
            
            <!-- 技术分析 -->
            <div class="section">
                <h2 class="section-title">四、技术分析</h2>
                <div class="card">
                    <div class="grid">
                        <div class="metric">
                            <div class="metric-label">趋势</div>
                            <div class="metric-value">{technical.get('patterns', {}).get('trend_desc', 'unknown')}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">RSI</div>
                            <div class="metric-value">{technical.get('indicators', {}).get('rsi', 0):.1f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">MACD</div>
                            <div class="metric-value">{technical.get('patterns', {}).get('macd_signal', 'unknown')}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 链上数据 -->
            {onchain_html}
            
            <!-- 信号汇总 -->
            <div class="section">
                <h2 class="section-title">五、信号汇总</h2>
                <div class="card">
                    <p><strong>看涨信号 ({len(bullish_signals)}项)</strong></p>
                    {bullish_html}
                    
                    <p style="margin-top: 16px;"><strong>看跌信号 ({len(bearish_signals)}项)</strong></p>
                    {bearish_html}
                    
                    <p style="margin-top: 20px; padding: 12px; background: #f3f4f6; border-radius: 6px;">
                        <strong>总强度:</strong> {sum([s['strength'] for s in signals]):+d} | 
                        <strong>倾向:</strong> {'看涨' if sum([s['strength'] for s in signals]) > 0 else '看跌'}
                    </p>
                </div>
            </div>
            
            <!-- 综合结论 -->
            <div class="section">
                <h2 class="section-title">六、综合结论</h2>
                <div class="card">
                    <p style="line-height: 1.8; color: #374151; font-size: 16px;">{conclusion.get('narrative', '')}</p>
                </div>
            </div>
            
            <!-- 数据来源 -->
            <div class="section">
                <h2 class="section-title">七、数据来源</h2>
                <div class="card">
                    <ul style="color: #6b7280; line-height: 2;">
                        <li>CoinGecko - 市场数据</li>
                        <li>yfinance - 技术指标</li>
                        <li>DeFiLlama - 链上数据</li>
                        <li>OnchainWhaleSkill - 鲸鱼分析</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Neo9527 Finance Skill v4.5 | GitHub: beautifulboy9527/Neo9527-unified-finance-skill</p>
        </div>
    </div>
    
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <script>
        const candlestickData = {candlestick_js};
        const ma5Data = {ma5_js};
        const ma10Data = {ma10_js};
        const volumeData = {volume_js};
        
        if (candlestickData.length > 0) {{
            const chart = LightweightCharts.createChart(document.getElementById('kline-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#ffffff' }}, textColor: '#333' }},
                grid: {{ vertLines: {{ color: '#f0f0f0' }}, horzLines: {{ color: '#f0f0f0' }} }},
                timeScale: {{ borderColor: '#cccccc', timeVisible: true }}
            }});
            
            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350'
            }});
            candlestickSeries.setData(candlestickData);
            
            if (ma5Data.length > 0) {{
                const ma5Line = chart.addLineSeries({{ color: '#2196f3', lineWidth: 2 }});
                ma5Line.setData(ma5Data);
            }}
            
            if (ma10Data.length > 0) {{
                const ma10Line = chart.addLineSeries({{ color: '#4caf50', lineWidth: 2 }});
                ma10Line.setData(ma10Data);
            }}
            
            const volumeChart = LightweightCharts.createChart(document.getElementById('volume-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#ffffff' }}, textColor: '#333' }},
                grid: {{ vertLines: {{ color: '#f0f0f0' }}, horzLines: {{ color: '#f0f0f0' }} }},
                timeScale: {{ visible: false }}
            }});
            
            const volumeSeries = volumeChart.addHistogramSeries({{
                priceFormat: {{ type: 'volume' }}
            }});
            volumeSeries.setData(volumeData);
        }}
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'ETH-USD'
    
    print("=" * 60)
    print(f"生成 {symbol} 增强版报告 (v4.5)")
    print("=" * 60)
    
    report_file = generate_enhanced_report(symbol)
    
    print(f"\n✅ 完成!")
    print(f"   文件: {report_file}")
