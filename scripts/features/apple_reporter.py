#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格HTML报告生成器
- 纯黑背景 + 卡片式布局
- 迷你卡片网格
- 高亮色渐变
- 滚动动画
- Chart.js图表
"""

import sys
from typing import Dict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class AppleStyleReporter:
    """Apple风格报告生成器"""
    
    # 品牌颜色映射
    BRAND_COLORS = {
        '美的': '#0066CC',  # 美的蓝
        '格力': '#E60012',  # 格力红
        '小米': '#FF6900',  # 小米橙
        '华为': '#CF0A2C',  # 华为红
        '立讯精密': '#00AEEF',  # 立讯蓝
        '比亚迪': '#00A0E9',  # 比亚迪蓝
        '宁德时代': '#E60012',  # 宁德红
        '茅台': '#B8860B',  # 金色
        '平安': '#FF8800',  # 橙色
        '招商银行': '#E60012',  # 红色
    }
    
    def __init__(self):
        self.brand_color = '#00AEEF'  # 默认科技蓝
    
    def detect_brand_color(self, stock_name: str) -> str:
        """检测品牌颜色"""
        for brand, color in self.BRAND_COLORS.items():
            if brand in stock_name:
                return color
        return '#00AEEF'  # 默认科技蓝
    
    def generate(self, result: Dict) -> str:
        """生成Apple风格HTML报告"""
        
        # 检测品牌颜色
        stock_name = result.get('name_cn', result.get('symbol', ''))
        self.brand_color = self.detect_brand_color(stock_name)
        
        # 英文名称
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
        /* 基础样式 */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: #000000;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            overflow-x: hidden;
        }}
        
        /* 高亮色渐变 */
        .gradient-bg {{
            background: linear-gradient(135deg, {self.brand_color}B3 0%, {self.brand_color}4D 100%);
        }}
        
        .gradient-text {{
            background: linear-gradient(135deg, {self.brand_color} 0%, {self.brand_color}CC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        /* 卡片样式 */
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
        }}
        
        .mini-card:hover {{
            border-color: {self.brand_color}4D;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
        }}
        
        /* 动画 */
        .fade-in {{
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }}
        
        .fade-in.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        /* 网格延迟 */
        .grid-item:nth-child(1) {{ transition-delay: 0.1s; }}
        .grid-item:nth-child(2) {{ transition-delay: 0.15s; }}
        .grid-item:nth-child(3) {{ transition-delay: 0.2s; }}
        .grid-item:nth-child(4) {{ transition-delay: 0.25s; }}
        .grid-item:nth-child(5) {{ transition-delay: 0.3s; }}
        .grid-item:nth-child(6) {{ transition-delay: 0.35s; }}
        .grid-item:nth-child(7) {{ transition-delay: 0.4s; }}
        .grid-item:nth-child(8) {{ transition-delay: 0.45s; }}
        
        /* 数字强调 */
        .big-number {{
            font-size: 3.5rem;
            font-weight: 700;
            line-height: 1;
        }}
        
        /* 滚动条 */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #1a1a1a;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #333;
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {self.brand_color}66;
        }}
    </style>
</head>
<body class="antialiased">
    
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center px-4 py-20">
        <div class="text-center max-w-4xl fade-in">
            <!-- 股票代码 -->
            <div class="text-sm text-gray-500 mb-4 tracking-widest">{result.get('symbol', '')}</div>
            
            <!-- 主标题 -->
            <h1 class="text-6xl md:text-7xl font-bold mb-4 gradient-text">
                {stock_name}
            </h1>
            
            <!-- 英文副标题 -->
            <div class="text-xl md:text-2xl text-gray-400 mb-12 font-semibold">
                {english_name} Investment Analysis Report
            </div>
            
            <!-- 评分卡片 -->
            <div class="inline-block bg-gradient-to-br from-gray-900 to-black border border-gray-800 rounded-3xl p-8 mb-8">
                <div class="flex items-center justify-center gap-8">
                    <div>
                        <div class="big-number gradient-text">{score}</div>
                        <div class="text-sm text-gray-500 mt-2">/ 100</div>
                    </div>
                    <div class="w-px h-20 bg-gray-700"></div>
                    <div class="text-left">
                        <div class="text-2xl font-bold mb-1">{recommendation}</div>
                        <div class="text-sm text-gray-400">综合投资建议</div>
                    </div>
                </div>
            </div>
            
            <!-- 核心数据 -->
            <div class="flex justify-center gap-8 text-sm text-gray-400">
                <div>
                    <span class="text-white font-semibold">{result.get('price', {}).get('current', 0):.2f}</span> 元
                </div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div>
                    <span class="text-white font-semibold">{result.get('valuation', {}).get('market_cap_str', 'N/A')}</span>
                </div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div>
                    PE <span class="text-white font-semibold">{result.get('valuation', {}).get('pe', 0):.1f}</span>
                </div>
            </div>
            
            <!-- 向下滚动提示 -->
            <div class="mt-16 animate-bounce">
                <i class="fas fa-chevron-down text-2xl text-gray-600"></i>
            </div>
        </div>
    </section>
    
    <!-- Key Metrics Section -->
    <section class="px-4 py-20">
        <div class="max-w-7xl mx-auto">
            
            <!-- Section Title -->
            <div class="text-center mb-16 fade-in">
                <h2 class="text-4xl md:text-5xl font-bold mb-4">关键指标</h2>
                <p class="text-gray-400 text-lg">Key Performance Metrics</p>
            </div>
            
            <!-- Mini Cards Grid -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                
                <!-- ROE -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number gradient-text mb-2">
                        {result.get('profitability', {}).get('roe', 0)*100:.1f}%
                    </div>
                    <div class="text-sm text-gray-400">ROE 净资产收益率</div>
                    <div class="text-xs text-gray-600 mt-1">Return on Equity</div>
                </div>
                
                <!-- PE -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('valuation', {}).get('pe', 0):.1f}
                    </div>
                    <div class="text-sm text-gray-400">PE 市盈率</div>
                    <div class="text-xs text-gray-600 mt-1">Price to Earnings</div>
                </div>
                
                <!-- PB -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('valuation', {}).get('pb', 0):.1f}
                    </div>
                    <div class="text-sm text-gray-400">PB 市净率</div>
                    <div class="text-xs text-gray-600 mt-1">Price to Book</div>
                </div>
                
                <!-- 毛利率 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('profitability', {}).get('gross_margin', 0)*100:.1f}%
                    </div>
                    <div class="text-sm text-gray-400">毛利率</div>
                    <div class="text-xs text-gray-600 mt-1">Gross Margin</div>
                </div>
                
                <!-- 净利率 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('profitability', {}).get('net_margin', 0)*100:.1f}%
                    </div>
                    <div class="text-sm text-gray-400">净利率</div>
                    <div class="text-xs text-gray-600 mt-1">Net Profit Margin</div>
                </div>
                
            </div>
        </div>
    </section>
    
    <!-- Financial Health Section -->
    <section class="px-4 py-20">
        <div class="max-w-7xl mx-auto">
            
            <!-- Section Title -->
            <div class="text-center mb-16 fade-in">
                <h2 class="text-4xl md:text-5xl font-bold mb-4">财务健康</h2>
                <p class="text-gray-400 text-lg">Financial Health Assessment</p>
            </div>
            
            <!-- Mini Cards Grid -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
                
                <!-- 资产负债率 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('financial', {}).get('debt_ratio', 0):.1f}%
                    </div>
                    <div class="text-sm text-gray-400">资产负债率</div>
                    <div class="text-xs text-gray-600 mt-1">Debt to Assets</div>
                    <div class="text-xs mt-2 px-2 py-1 rounded inline-block" style="background: {self.brand_color}20; color: {self.brand_color}">
                        {result.get('financial', {}).get('data_source', 'N/A')}
                    </div>
                </div>
                
                <!-- 流动比率 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('financial', {}).get('current_ratio', 0):.2f}
                    </div>
                    <div class="text-sm text-gray-400">流动比率</div>
                    <div class="text-xs text-gray-600 mt-1">Current Ratio</div>
                </div>
                
                <!-- 财务状态 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="text-3xl font-bold mb-2 gradient-text">
                        {result.get('financial', {}).get('status', 'N/A')}
                    </div>
                    <div class="text-sm text-gray-400">财务状态</div>
                    <div class="text-xs text-gray-600 mt-1">Financial Status</div>
                </div>
                
            </div>
            
            <!-- 风险提示 -->
            {self._generate_risk_cards(result.get('financial', {}).get('risks', []))}
            
        </div>
    </section>
    
    <!-- Technical Analysis Section -->
    <section class="px-4 py-20">
        <div class="max-w-7xl mx-auto">
            
            <!-- Section Title -->
            <div class="text-center mb-16 fade-in">
                <h2 class="text-4xl md:text-5xl font-bold mb-4">技术分析</h2>
                <p class="text-gray-400 text-lg">Technical Analysis</p>
            </div>
            
            <!-- Signal Cards -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
                
                <!-- RSI -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('technical', {}).get('indicators', {}).get('rsi', 50):.1f}
                    </div>
                    <div class="text-sm text-gray-400">RSI 相对强弱</div>
                    <div class="text-xs text-gray-600 mt-1">Relative Strength Index</div>
                </div>
                
                <!-- MACD -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="text-2xl font-bold mb-2" style="color: {'#22c55e' if '金叉' in result.get('technical', {}).get('patterns', {}).get('macd_desc', '') else '#ef4444'}">
                        {result.get('technical', {}).get('patterns', {}).get('macd_desc', 'N/A').split('(')[0].strip()}
                    </div>
                    <div class="text-sm text-gray-400">MACD 状态</div>
                    <div class="text-xs text-gray-600 mt-1">Moving Average Convergence</div>
                </div>
                
                <!-- 趋势 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="text-2xl font-bold mb-2 gradient-text">
                        {result.get('technical', {}).get('patterns', {}).get('trend_desc', 'N/A').split('(')[0].strip()}
                    </div>
                    <div class="text-sm text-gray-400">趋势判断</div>
                    <div class="text-xs text-gray-600 mt-1">Trend Analysis</div>
                </div>
                
                <!-- 成交量比 -->
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">
                        {result.get('volume_validation', {}).get('volume_ratio', 1):.2f}x
                    </div>
                    <div class="text-sm text-gray-400">成交量比</div>
                    <div class="text-xs text-gray-600 mt-1">Volume Ratio</div>
                </div>
                
            </div>
            
            <!-- 支撑阻力位 -->
            <div class="card rounded-2xl p-8 fade-in">
                <h3 class="text-2xl font-bold mb-6 flex items-center gap-3">
                    <i class="fas fa-layer-group" style="color: {self.brand_color}"></i>
                    支撑阻力位
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-400 mb-2">
                            {result.get('technical', {}).get('support_near', 0):.2f}
                        </div>
                        <div class="text-sm text-gray-400">近期支撑</div>
                        <div class="text-xs text-gray-600 mt-1">Near Support</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-600 mb-2">
                            {result.get('technical', {}).get('support_far', 0):.2f}
                        </div>
                        <div class="text-sm text-gray-400">远期支撑</div>
                        <div class="text-xs text-gray-600 mt-1">Far Support</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-red-400 mb-2">
                            {result.get('technical', {}).get('resistance_near', 0):.2f}
                        </div>
                        <div class="text-sm text-gray-400">近期阻力</div>
                        <div class="text-xs text-gray-600 mt-1">Near Resistance</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-red-600 mb-2">
                            {result.get('technical', {}).get('resistance_far', 0):.2f}
                        </div>
                        <div class="text-sm text-gray-400">远期阻力</div>
                        <div class="text-xs text-gray-600 mt-1">Far Resistance</div>
                    </div>
                </div>
            </div>
            
        </div>
    </section>
    
    <!-- Buff Analysis Section -->
    {self._generate_buff_section(result)}
    
    <!-- Risk Management Section -->
    <section class="px-4 py-20">
        <div class="max-w-7xl mx-auto">
            
            <!-- Section Title -->
            <div class="text-center mb-16 fade-in">
                <h2 class="text-4xl md:text-5xl font-bold mb-4">风险管理</h2>
                <p class="text-gray-400 text-lg">Risk Management</p>
            </div>
            
            <!-- VaR Cards -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">90%</div>
                    <div class="text-sm text-gray-400">VaR 置信水平</div>
                    <div class="text-xs text-gray-600 mt-1">Confidence Level</div>
                </div>
                
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">95%</div>
                    <div class="text-sm text-gray-400">VaR 置信水平</div>
                    <div class="text-xs text-gray-600 mt-1">Confidence Level</div>
                </div>
                
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="big-number text-white mb-2">99%</div>
                    <div class="text-sm text-gray-400">VaR 置信水平</div>
                    <div class="text-xs text-gray-600 mt-1">Confidence Level</div>
                </div>
                
            </div>
            
        </div>
    </section>
    
    <!-- Chart Section -->
    <section class="px-4 py-20">
        <div class="max-w-7xl mx-auto">
            <div class="card rounded-2xl p-8 fade-in">
                <h3 class="text-2xl font-bold mb-6 flex items-center gap-3">
                    <i class="fas fa-chart-line" style="color: {self.brand_color}"></i>
                    综合评分雷达图
                </h3>
                <div style="height: 400px;">
                    <canvas id="radarChart"></canvas>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="px-4 py-12 border-t border-gray-800">
        <div class="max-w-7xl mx-auto text-center text-gray-500 text-sm">
            <div class="mb-2">{stock_name} 投资分析报告</div>
            <div class="text-xs">生成时间: {result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</div>
            <div class="text-xs mt-1">数据来源: yfinance + 专业分析模块 | 报告仅供参考，不构成投资建议</div>
        </div>
    </footer>
    
    <!-- JavaScript -->
    <script>
        // Intersection Observer for animations
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }});
        
        document.querySelectorAll('.fade-in').forEach(el => {{
            observer.observe(el);
        }});
        
        // Radar Chart
        const ctx = document.getElementById('radarChart').getContext('2d');
        const radarChart = new Chart(ctx, {{
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
                    pointBackgroundColor: '{self.brand_color}',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '{self.brand_color}'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 20,
                            color: '#666',
                            backdropColor: 'transparent'
                        }},
                        grid: {{
                            color: '#333'
                        }},
                        angleLines: {{
                            color: '#333'
                        }},
                        pointLabels: {{
                            color: '#fff',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
    
</body>
</html>'''
    
    def _generate_risk_cards(self, risks: list) -> str:
        """生成风险卡片"""
        if not risks:
            return ''
        
        cards = ''
        for risk in risks:
            cards += f'''
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="flex items-start gap-3">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-xl mt-1"></i>
                        <div>
                            <div class="text-base font-semibold text-white mb-1">{risk}</div>
                            <div class="text-xs text-gray-500">需要关注的风险因素</div>
                        </div>
                    </div>
                </div>'''
        
        return f'''
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
                {cards}
            </div>'''
    
    def _generate_buff_section(self, result: Dict) -> str:
        """生成Buff叠加分析区域"""
        
        # 计算各个buff
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
                <div class="mini-card rounded-xl p-6 fade-in grid-item">
                    <div class="text-2xl font-bold mb-2" style="color: {color}">{score}</div>
                    <div class="text-sm text-gray-400">{buff_type}</div>
                    <div class="text-xs text-gray-600 mt-1">{desc}</div>
                </div>'''
        
        total_color = '#22c55e' if total > 0 else ('#ef4444' if total < 0 else '#f59e0b')
        total_text = '偏多' if total > 0 else ('偏空' if total < 0 else '中性')
        
        return f'''
            <section class="px-4 py-20">
                <div class="max-w-7xl mx-auto">
                    
                    <!-- Section Title -->
                    <div class="text-center mb-16 fade-in">
                        <h2 class="text-4xl md:text-5xl font-bold mb-4">Buff叠加分析</h2>
                        <p class="text-gray-400 text-lg">Multi-Dimensional Analysis</p>
                    </div>
                    
                    <!-- Buff Cards -->
                    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
                        {cards}
                        
                        <!-- Total Buff -->
                        <div class="mini-card rounded-xl p-6 fade-in grid-item" style="background: linear-gradient(135deg, {self.brand_color}20 0%, {self.brand_color}10 100%);">
                            <div class="text-4xl font-bold mb-2" style="color: {total_color}">
                                {total:+d}
                            </div>
                            <div class="text-sm text-gray-400">总Buff</div>
                            <div class="text-xs text-gray-600 mt-1">{total_text} (评分 {result.get('score', 0)}/100)</div>
                        </div>
                        
                    </div>
                    
                </div>
            </section>'''


# 便捷函数
def generate_apple_report(result: Dict) -> str:
    """生成Apple风格报告"""
    reporter = AppleStyleReporter()
    return reporter.generate(result)


if __name__ == '__main__':
    print("Apple风格报告生成器已加载")
    print("使用方法: from apple_reporter import generate_apple_report")
