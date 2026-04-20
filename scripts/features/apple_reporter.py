#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格HTML报告生成器 v2.0
- 纯黑背景 + 卡片式布局
- 完整保留所有分析内容
- 迷你卡片网格 + 详细解读
- 滚动动画 + Chart.js图表
"""

import sys
from typing import Dict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class AppleStyleReporter:
    """Apple风格报告生成器 v2.0"""
    
    # 品牌颜色映射
    BRAND_COLORS = {
        '美的': '#0066CC',
        '格力': '#E60012',
        '小米': '#FF6900',
        '华为': '#CF0A2C',
        '立讯精密': '#00AEEF',
        '比亚迪': '#00A0E9',
        '宁德时代': '#E60012',
        '茅台': '#B8860B',
        '平安': '#FF8800',
        '招商银行': '#E60012',
    }
    
    def __init__(self):
        self.brand_color = '#00AEEF'
    
    def detect_brand_color(self, stock_name: str) -> str:
        """检测品牌颜色"""
        for brand, color in self.BRAND_COLORS.items():
            if brand in stock_name:
                return color
        return '#00AEEF'
    
    def generate(self, result: Dict) -> str:
        """生成Apple风格HTML报告"""
        
        stock_name = result.get('name_cn', result.get('symbol', ''))
        self.brand_color = self.detect_brand_color(stock_name)
        
        english_names = {
            '美的集团': 'Midea Group Co., Ltd.',
            '格力电器': 'Gree Electric Appliances',
            '立讯精密': 'Luxshare Precision Industry',
            '比亚迪': 'BYD Company Limited',
            '宁德时代': 'Contemporary Amperex Technology',
            '贵州茅台': 'Kweichow Moutai Co., Ltd.',
        }
        english_name = english_names.get(stock_name, stock_name)
        
        return self._build_html(result, stock_name, english_name)
    
    def _build_html(self, result: Dict, stock_name: str, english_name: str) -> str:
        """构建完整HTML"""
        
        score = result.get('score', 0)
        recommendation = result.get('recommendation', 'N/A')
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_name} 投资分析报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: #000000;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow-x: hidden;
        }}
        
        .gradient-bg {{
            background: linear-gradient(135deg, {self.brand_color}B3 0%, {self.brand_color}4D 100%);
        }}
        
        .gradient-text {{
            background: linear-gradient(135deg, {self.brand_color} 0%, {self.brand_color}CC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .card {{
            background: #1a1a1a;
            border: 1px solid #333;
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            border-color: {self.brand_color}66;
            box-shadow: 0 8px 32px {self.brand_color}33;
        }}
        
        .mini-card {{
            background: #222222;
            border: 1px solid #333;
            transition: all 0.3s ease;
            min-height: 120px;
        }}
        
        .mini-card:hover {{
            border-color: {self.brand_color}4D;
            transform: translateY(-4px);
        }}
        
        .fade-in {{
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }}
        
        .fade-in.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        .grid-item:nth-child(1) {{ transition-delay: 0.05s; }}
        .grid-item:nth-child(2) {{ transition-delay: 0.07s; }}
        .grid-item:nth-child(3) {{ transition-delay: 0.09s; }}
        .grid-item:nth-child(4) {{ transition-delay: 0.11s; }}
        .grid-item:nth-child(5) {{ transition-delay: 0.13s; }}
        .grid-item:nth-child(6) {{ transition-delay: 0.15s; }}
        
        .big-number {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.1;
        }}
        
        .analysis-box {{
            background: linear-gradient(135deg, {self.brand_color}15 0%, {self.brand_color}08 100%);
            border-left: 3px solid {self.brand_color};
            padding: 16px;
            margin-top: 16px;
            border-radius: 0 8px 8px 0;
        }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #1a1a1a; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 4px; }}
    </style>
</head>
<body class="antialiased">
    
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center px-4 py-16">
        <div class="text-center max-w-4xl fade-in">
            <div class="text-sm text-gray-500 mb-3 tracking-widest">{result.get('symbol', '')}</div>
            
            <h1 class="text-5xl md:text-6xl font-bold mb-3 gradient-text">{stock_name}</h1>
            <div class="text-lg md:text-xl text-gray-400 mb-8 font-medium">{english_name}</div>
            
            <div class="inline-block bg-gradient-to-br from-gray-900 to-black border border-gray-800 rounded-3xl p-6 mb-6">
                <div class="flex items-center justify-center gap-6">
                    <div class="text-center">
                        <div class="text-4xl font-bold gradient-text">{score}</div>
                        <div class="text-xs text-gray-500 mt-1">/ 100</div>
                    </div>
                    <div class="w-px h-16 bg-gray-700"></div>
                    <div class="text-left">
                        <div class="text-xl font-bold mb-1">{recommendation}</div>
                        <div class="text-xs text-gray-400">综合投资建议</div>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-center gap-6 text-sm text-gray-400">
                <div><span class="text-white font-semibold">{result.get('price', {}).get('current', 0):.2f}</span> 元</div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div><span class="text-white font-semibold">{result.get('valuation', {}).get('market_cap_str', 'N/A')}</span></div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div>PE <span class="text-white font-semibold">{result.get('valuation', {}).get('pe', 0):.1f}</span></div>
            </div>
            
            <div class="mt-12 animate-bounce">
                <i class="fas fa-chevron-down text-xl text-gray-600"></i>
            </div>
        </div>
    </section>
    
    <!-- 1. 行业分析 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">行业分析</h2>
                <p class="text-gray-400 text-sm">Industry Analysis</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">所属行业</div>
                        <div class="text-xl font-bold">{result.get('industry', {}).get('name_cn', 'N/A')}</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">所属板块</div>
                        <div class="text-xl font-bold">{result.get('industry', {}).get('sector', 'N/A')}</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">行业周期</div>
                        <div class="text-xl font-bold">{result.get('industry', {}).get('cycle', '未知')}</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">行业风险</div>
                        <div class="text-xl font-bold">{result.get('industry', {}).get('risk', '未知')}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('industry', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 2. 估值分析 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">估值分析</h2>
                <p class="text-gray-400 text-sm">Valuation Analysis</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">市盈率 PE</div>
                        <div class="big-number gradient-text">{result.get('valuation', {}).get('pe', 0):.1f}</div>
                        <div class="text-xs mt-2 text-gray-500">Price to Earnings</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">市净率 PB</div>
                        <div class="big-number text-white">{result.get('valuation', {}).get('pb', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Price to Book</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">市销率 PS</div>
                        <div class="big-number text-white">{result.get('valuation', {}).get('ps', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Price to Sales</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">总市值</div>
                        <div class="text-xl font-bold text-white">{result.get('valuation', {}).get('market_cap_str', 'N/A')}</div>
                        <div class="text-xs mt-2 text-gray-500">Market Cap</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('valuation', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 3. 盈利能力 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">盈利能力</h2>
                <p class="text-gray-400 text-sm">Profitability</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">ROE 净资产收益率</div>
                        <div class="big-number gradient-text">{result.get('profitability', {}).get('roe', 0)*100:.1f}%</div>
                        <div class="text-xs mt-2 text-gray-500">Return on Equity</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">毛利率</div>
                        <div class="big-number text-white">{result.get('profitability', {}).get('gross_margin', 0)*100:.1f}%</div>
                        <div class="text-xs mt-2 text-gray-500">Gross Margin</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">净利率</div>
                        <div class="big-number text-white">{result.get('profitability', {}).get('net_margin', 0)*100:.1f}%</div>
                        <div class="text-xs mt-2 text-gray-500">Net Margin</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">盈利状态</div>
                        <div class="text-2xl font-bold" style="color: {'#22c55e' if result.get('profitability', {}).get('is_profitable') else '#ef4444'}">
                            {'盈利' if result.get('profitability', {}).get('is_profitable') else '亏损'}
                        </div>
                        <div class="text-xs mt-2 text-gray-500">Profit Status</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('profitability', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 4. 财务健康 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">财务健康</h2>
                <p class="text-gray-400 text-sm">Financial Health</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">资产负债率</div>
                        <div class="big-number text-white">{result.get('financial', {}).get('debt_ratio', 0):.1f}%</div>
                        <div class="text-xs mt-2 text-gray-500">Debt to Assets</div>
                        <div class="mt-2 px-2 py-1 rounded text-xs inline-block" style="background: {self.brand_color}20; color: {self.brand_color}">
                            {result.get('financial', {}).get('data_source', 'N/A')} ({result.get('financial', {}).get('confidence', 0)*100:.0f}%)
                        </div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">流动比率</div>
                        <div class="big-number text-white">{result.get('financial', {}).get('current_ratio', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Current Ratio</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">财务状态</div>
                        <div class="text-2xl font-bold gradient-text">{result.get('financial', {}).get('status', 'N/A')}</div>
                        <div class="text-xs mt-2 text-gray-500">Financial Status</div>
                    </div>
                </div>
                {self._generate_risk_cards_html(result.get('financial', {}).get('risks', []))}
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('financial', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 5. 技术分析 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">技术分析</h2>
                <p class="text-gray-400 text-sm">Technical Analysis</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in mb-6">
                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-chart-line" style="color: {self.brand_color}"></i>核心指标
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">RSI 相对强弱</div>
                        <div class="big-number text-white">{result.get('technical', {}).get('indicators', {}).get('rsi', 50):.1f}</div>
                        <div class="text-xs mt-2 text-gray-500">Relative Strength Index</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">MACD 状态</div>
                        <div class="text-xl font-bold" style="color: {'#22c55e' if '金叉' in str(result.get('technical', {}).get('patterns', {}).get('macd_desc', '')) else '#ef4444'}">
                            {str(result.get('technical', {}).get('patterns', {}).get('macd_desc', 'N/A')).split('(')[0].strip()}
                        </div>
                        <div class="text-xs mt-2 text-gray-500">Moving Average Convergence</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">趋势判断</div>
                        <div class="text-xl font-bold gradient-text">
                            {str(result.get('technical', {}).get('patterns', {}).get('trend_desc', 'N/A')).split('(')[0].strip()}
                        </div>
                        <div class="text-xs mt-2 text-gray-500">Trend Analysis</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">成交量比</div>
                        <div class="big-number text-white">{result.get('volume_validation', {}).get('volume_ratio', 1):.2f}x</div>
                        <div class="text-xs mt-2 text-gray-500">Volume Ratio</div>
                    </div>
                </div>
            </div>
            
            <!-- 支撑阻力位 -->
            <div class="card rounded-2xl p-6 fade-in mb-6">
                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-layer-group" style="color: {self.brand_color}"></i>支撑阻力位
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">近期支撑</div>
                        <div class="text-2xl font-bold text-green-400">{result.get('technical', {}).get('support_near', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Near Support</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">远期支撑</div>
                        <div class="text-2xl font-bold text-green-600">{result.get('technical', {}).get('support_far', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Far Support</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">近期阻力</div>
                        <div class="text-2xl font-bold text-red-400">{result.get('technical', {}).get('resistance_near', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Near Resistance</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">远期阻力</div>
                        <div class="text-2xl font-bold text-red-600">{result.get('technical', {}).get('resistance_far', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Far Resistance</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('technical', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
            
            <!-- 成交量验证 -->
            <div class="card rounded-2xl p-6 fade-in mb-6">
                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-chart-bar" style="color: {self.brand_color}"></i>成交量验证
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">成交量状态</div>
                        <div class="text-xl font-bold gradient-text">{result.get('volume_validation', {}).get('status', 'N/A')}</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">信号强度</div>
                        <div class="text-xl font-bold text-white">{result.get('technical', {}).get('signal_strength', 0)}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('volume_validation', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
            
        </div>
    </section>
    
    <!-- 6. 风险管理 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">风险管理</h2>
                <p class="text-gray-400 text-sm">Risk Management</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in mb-6">
                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-shield-alt" style="color: {self.brand_color}"></i>ATR止损建议
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">当前价格</div>
                        <div class="text-xl font-bold text-white">{result.get('risk_management', {}).get('current_price', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Current Price</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">止损价位</div>
                        <div class="text-xl font-bold text-red-400">{result.get('risk_management', {}).get('stop_loss_price', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">Stop Loss</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">风险比例</div>
                        <div class="text-xl font-bold text-white">{result.get('risk_management', {}).get('risk_pct', 0):.1f}%</div>
                        <div class="text-xs mt-2 text-gray-500">Risk %</div>
                    </div>
                    <div class="mini-card rounded-xl p-4 grid-item fade-in">
                        <div class="text-gray-400 text-xs mb-2">ATR值</div>
                        <div class="text-xl font-bold text-white">{result.get('risk_management', {}).get('atr', 0):.2f}</div>
                        <div class="text-xs mt-2 text-gray-500">ATR Value</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-1"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>分析解读</div>
                    <div class="text-sm text-gray-300">{result.get('risk_management', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
            
        </div>
    </section>
    
    <!-- 7. Buff叠加分析 -->
    {self._generate_buff_section_html(result)}
    
    <!-- 8. 汇总分析 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-10 fade-in">
                <h2 class="text-3xl md:text-4xl font-bold mb-2">汇总分析</h2>
                <p class="text-gray-400 text-sm">Summary Analysis</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="space-y-4">
                    <div class="analysis-box">
                        <div class="font-semibold text-sm mb-1"><i class="fas fa-industry mr-2" style="color: {self.brand_color}"></i>行业周期分析</div>
                        <div class="text-sm text-gray-300">{result.get('summary', {}).get('industry_analysis', '暂无分析')}</div>
                    </div>
                    <div class="analysis-box">
                        <div class="font-semibold text-sm mb-1"><i class="fas fa-chart-line mr-2" style="color: {self.brand_color}"></i>盈利能力推演</div>
                        <div class="text-sm text-gray-300">{result.get('summary', {}).get('profit_analysis', '暂无分析')}</div>
                    </div>
                    <div class="analysis-box">
                        <div class="font-semibold text-sm mb-1"><i class="fas fa-coins mr-2" style="color: {self.brand_color}"></i>估值水平分析</div>
                        <div class="text-sm text-gray-300">{result.get('summary', {}).get('valuation_analysis', '暂无分析')}</div>
                    </div>
                    <div class="analysis-box">
                        <div class="font-semibold text-sm mb-1"><i class="fas fa-heartbeat mr-2" style="color: {self.brand_color}"></i>财务健康评估</div>
                        <div class="text-sm text-gray-300">{result.get('summary', {}).get('financial_analysis', '暂无分析')}</div>
                    </div>
                    <div class="analysis-box">
                        <div class="font-semibold text-sm mb-1"><i class="fas fa-globe mr-2" style="color: {self.brand_color}"></i>综合投资建议</div>
                        <div class="text-sm text-gray-300">{result.get('summary', {}).get('recommendation', '暂无分析')}</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 9. Chart.js雷达图 -->
    <section class="px-4 py-12">
        <div class="max-w-7xl mx-auto">
            <div class="card rounded-2xl p-6 fade-in">
                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                    <i class="fas fa-chart-pie" style="color: {self.brand_color}"></i>综合评分雷达图
                </h3>
                <div style="height: 350px;">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="px-4 py-8 border-t border-gray-800">
        <div class="max-w-7xl mx-auto text-center text-gray-500 text-xs">
            <div class="mb-1">{stock_name} 投资分析报告</div>
            <div>生成时间: {result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</div>
            <div class="mt-1">数据来源: yfinance + 专业分析模块 | 报告仅供参考，不构成投资建议</div>
        </div>
    </footer>
    
    <script>
        // Intersection Observer
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, {{ threshold: 0.1, rootMargin: '0px 0px -30px 0px' }});
        
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
        
        // Radar Chart
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['盈利能力', '估值水平', '财务健康', '技术面', '成长性'],
                datasets: [{{
                    label: '综合评分',
                    data: [
                        {min(result.get('profitability', {}).get('roe', 0) * 500, 100)},
                        {max(100 - result.get('valuation', {}).get('pe', 50), 0)},
                        {100 - result.get('financial', {}).get('debt_ratio', 50)},
                        {result.get('technical', {}).get('signal_strength', 0) * 10 + 50},
                        60
                    ],
                    backgroundColor: '{self.brand_color}33',
                    borderColor: '{self.brand_color}',
                    borderWidth: 2,
                    pointBackgroundColor: '{self.brand_color}'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{ stepSize: 20, color: '#666', backdropColor: 'transparent' }},
                        grid: {{ color: '#333' }},
                        angleLines: {{ color: '#333' }},
                        pointLabels: {{ color: '#fff', font: {{ size: 13, weight: 'bold' }} }}
                    }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    </script>
    
</body>
</html>'''
    
    def _generate_risk_cards_html(self, risks: list) -> str:
        """生成风险卡片HTML"""
        if not risks:
            return ''
        
        cards = ''
        for risk in risks:
            cards += f'''
                <div class="mt-4 p-3 bg-yellow-900/20 border border-yellow-700/30 rounded-lg fade-in">
                    <div class="flex items-center gap-2">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-sm"></i>
                        <span class="text-sm text-gray-300">{risk}</span>
                    </div>
                </div>'''
        
        return cards
    
    def _generate_buff_section_html(self, result: Dict) -> str:
        """生成Buff叠加分析区域HTML"""
        
        buffs = []
        
        # 基本面buff
        roe = result.get('profitability', {}).get('roe', 0)
        if roe > 0.15:
            buffs.append(('基本面', '+3', f'ROE强劲 ({roe*100:.1f}%)', '#22c55e'))
        elif roe > 0.10:
            buffs.append(('基本面', '+2', f'ROE良好 ({roe*100:.1f}%)', '#22c55e'))
        
        # 估值buff
        pe = result.get('valuation', {}).get('pe', 0)
        if pe and pe < 15:
            buffs.append(('估值', '+2', f'PE低估 ({pe:.1f})', '#22c55e'))
        elif pe and pe < 25:
            buffs.append(('估值', '+1', f'PE合理 ({pe:.1f})', '#f59e0b'))
        elif pe and pe > 40:
            buffs.append(('估值', '-2', f'PE高估 ({pe:.1f})', '#ef4444'))
        
        # 财务健康buff
        status = result.get('financial', {}).get('status', '')
        if status == '健康':
            buffs.append(('财务健康', '+1', '财务状态良好', '#22c55e'))
        elif status == '需关注':
            buffs.append(('财务健康', '-1', '财务需关注', '#f59e0b'))
        elif status == '高风险':
            buffs.append(('财务健康', '-2', '财务风险高', '#ef4444'))
        
        # 计算总buff
        total = sum([int(b[1]) for b in buffs])
        
        cards = ''
        for buff_type, score, desc, color in buffs:
            cards += f'''
                <div class="mini-card rounded-xl p-4 grid-item fade-in">
                    <div class="text-xl font-bold mb-1" style="color: {color}">{score}</div>
                    <div class="text-sm text-gray-400">{buff_type}</div>
                    <div class="text-xs text-gray-500 mt-1">{desc}</div>
                </div>'''
        
        total_color = '#22c55e' if total > 0 else ('#ef4444' if total < 0 else '#f59e0b')
        total_text = '偏多' if total > 0 else ('偏空' if total < 0 else '中性')
        
        return f'''
            <section class="px-4 py-12">
                <div class="max-w-7xl mx-auto">
                    <div class="text-center mb-10 fade-in">
                        <h2 class="text-3xl md:text-4xl font-bold mb-2">Buff叠加分析</h2>
                        <p class="text-gray-400 text-sm">Multi-Dimensional Analysis</p>
                    </div>
                    
                    <div class="card rounded-2xl p-6 fade-in">
                        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                            {cards}
                            
                            <!-- Total Buff -->
                            <div class="mini-card rounded-xl p-4 grid-item fade-in" style="background: linear-gradient(135deg, {self.brand_color}20 0%, {self.brand_color}10 100%);">
                                <div class="text-2xl font-bold mb-1" style="color: {total_color}">{total:+d}</div>
                                <div class="text-sm text-gray-400">总Buff</div>
                                <div class="text-xs text-gray-500 mt-1">{total_text} (评分 {result.get('score', 0)}/100)</div>
                            </div>
                            
                        </div>
                    </div>
                </div>
            </section>'''


def generate_apple_report(result: Dict) -> str:
    """生成Apple风格报告"""
    reporter = AppleStyleReporter()
    return reporter.generate(result)


if __name__ == '__main__':
    print("Apple风格报告生成器 v2.0 已加载")
