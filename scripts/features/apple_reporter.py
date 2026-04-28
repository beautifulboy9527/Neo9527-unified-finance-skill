#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格HTML报告生成器 v4.0
- 复用A股分析器的深度分析模块
- 修复数据加载问题
- 优化中文显示
- 完善操作建议
- 深度数据分析
"""

import sys
from typing import Dict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 导入A股分析器的深度模块
try:
    from a_share_analyzer import AShareAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False

# 导入胜率模型和深度分析
try:
    from win_rate_model import WinRateModel, DepthAnalyzer
    WIN_RATE_AVAILABLE = True
except ImportError:
    WIN_RATE_AVAILABLE = False


class AppleStyleReporter:
    """Apple风格报告生成器 v4.0"""
    
    BRAND_COLORS = {
        '中科曙光': '#1E90FF',
        '艾力斯': '#FF6B6B',
        '美的': '#0066CC',
        '格力': '#E60012',
        '小米': '#FF6900',
        '华为': '#CF0A2C',
        '立讯精密': '#00AEEF',
        '比亚迪': '#00A0E9',
        '宁德时代': '#E60012',
        '茅台': '#B8860B',
    }
    
    def __init__(self):
        self.brand_color = '#00AEEF'
    
    def detect_brand_color(self, stock_name: str) -> str:
        for brand, color in self.BRAND_COLORS.items():
            if brand in stock_name:
                return color
        return '#00AEEF'
    
    def generate(self, result: Dict) -> str:
        stock_name = result.get('name_cn', result.get('symbol', ''))
        self.brand_color = self.detect_brand_color(stock_name)
        
        english_names = {
            '中科曙光': 'Sugon',
            '美的集团': 'Midea Group',
            '格力电器': 'Gree Electric',
            '立讯精密': 'Luxshare Precision',
            '比亚迪': 'BYD',
            '宁德时代': 'CATL',
            '贵州茅台': 'Kweichow Moutai',
        }
        # 如果name_cn是代码，尝试获取symbol
        if not stock_name or stock_name.isdigit():
            stock_name = result.get('symbol', '')
        english_name = english_names.get(stock_name, stock_name)
        
        return self._build_html(result, stock_name, english_name)
    
    def _build_html(self, result: Dict, stock_name: str, english_name: str) -> str:
        score = result.get('score', 0)
        recommendation = result.get('recommendation', 'N/A')
        
        # 安全获取数据
        tech = result.get('technical', {})
        financial = result.get('financial', {})
        valuation = result.get('valuation', {})
        profitability = result.get('profitability', {})
        risk_mgmt = result.get('risk_management', {})
        volume_val = result.get('volume_validation', {})
        
        # 转换numpy类型为Python原生类型，避免格式化错误
        import numpy as np
        def to_float(val, default=0):
            if val is None or (hasattr(val, 'item') and np.isnan(val)):
                return default
            try:
                return float(val)
            except:
                return default
        
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
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            overflow-x: hidden;
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
            min-height: 100px;
        }}
        .mini-card:hover {{
            border-color: {self.brand_color}4D;
            transform: translateY(-2px);
        }}
        .fade-in {{
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }}
        .fade-in.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .big-number {{
            font-size: 2rem;
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
        .action-box {{
            background: linear-gradient(135deg, #fbbf2420 0%, #fbbf2410 100%);
            border-left: 3px solid #fbbf24;
            padding: 16px;
            margin-top: 16px;
            border-radius: 0 8px 8px 0;
        }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #1a1a1a; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 4px; }}
    </style>
</head>
<body>
    
    <!-- Hero -->
    <section class="min-h-screen flex items-center justify-center px-4 py-16">
        <div class="text-center max-w-4xl fade-in">
            <div class="text-sm text-gray-500 mb-3">股票代码: {result.get('symbol', '')} · 科创板</div>
            <h1 class="text-5xl md:text-6xl font-bold mb-3 gradient-text">{result.get('name', stock_name)}</h1>
            <div class="text-xs text-gray-600 mb-8">📅 分析时间: {result.get('timestamp', '')} · 📊 数据周期: 日线(60交易日)</div>
            
            <div class="inline-block bg-gradient-to-br from-gray-900 to-black border border-gray-800 rounded-3xl p-6 mb-6">
                <div class="flex items-center justify-center gap-6">
                    <div class="text-center">
                        <div class="text-4xl font-bold gradient-text">{score}</div>
                        <div class="text-xs text-gray-500 mt-1">综合评分</div>
                    </div>
                    <div class="w-px h-16 bg-gray-700"></div>
                    <div class="text-left">
                        <div class="text-xl font-bold mb-1">{recommendation}</div>
                        <div class="text-xs text-gray-400">投资建议</div>
                    </div>
                </div>
            </div>
            
            <div class="flex justify-center gap-6 text-sm text-gray-400">
                <div><span class="text-white font-semibold">{result.get('price', {}).get('current', 0):.2f}</span> 元</div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div><span class="text-white font-semibold">{valuation.get('market_cap_str', 'N/A')}</span></div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div>市盈率 <span class="text-white font-semibold">{valuation.get('pe', 0):.2f}</span></div>
            </div>
            
            <div class="mt-12 animate-bounce"><i class="fas fa-chevron-down text-xl text-gray-600"></i></div>
        </div>
    </section>
    

    <!-- 实时行情板块 -->
    <section class="px-4 py-2 -mt-16">
        <div class="max-w-7xl mx-auto">
            <div class="card rounded-2xl p-4 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="text-center">
                        <div class="text-gray-400 text-xs mb-1">涨跌幅</div>
                        <div class="text-2xl font-bold" style="color:#ef4444">{'+' if result.get('price',{}).get('change_pct',0)>0 else ''}{result.get('price',{}).get('change_pct',0):.2f}%</div>
                    </div>
                    <div class="text-center">
                        <div class="text-gray-400 text-xs mb-1">52周区间</div>
                        <div class="text-lg font-bold text-white">{result.get('price',{}).get('low_52w',0):.1f}-{result.get('price',{}).get('high_52w',0):.1f}</div>
                    </div>
                    <div class="text-center">
                        <div class="text-gray-400 text-xs mb-1">今年涨跌</div>
                        <div class="text-lg font-bold" style="color:#22c55e">{'+' if result.get('price',{}).get('ytd_change',0)>0 else ''}{result.get('price',{}).get('ytd_change',0):.1f}%</div>
                    </div>
                    <div class="text-center">
                        <div class="text-gray-400 text-xs mb-1">成交量</div>
                        <div class="text-lg font-bold text-white">{result.get('volume_validation',{}).get('volume_level_cn','N/A')}</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 行业分析 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">行业分析</h2>
                <p class="text-gray-500 text-xs">行业定位与周期分析</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">所属行业</div>
                        <div class="text-lg font-bold">{self._translate_industry(self._translate_industry(result.get('industry', {}).get('name_cn', '未知')))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">所属板块</div>
                        <div class="text-lg font-bold">{result.get('industry', {}).get('sector_cn', result.get('industry', {}).get('sector', '未知'))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">行业周期</div>
                        <div class="text-lg font-bold">{result.get('industry', {}).get('cycle') or '成熟期'}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">行业风险</div>
                        <div class="text-lg font-bold">{result.get('industry', {}).get('risk') or '中等'}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>深度解读 <span class="ml-2 px-1.5 py-0.5 rounded text-xs" style="background:#22c55e20;color:#22c55e">实时数据</span></div>
                    <div class="text-sm text-gray-300 leading-relaxed">{result.get('industry', {}).get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 估值分析 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">估值分析</h2>
                <p class="text-gray-500 text-xs">估值水平与投资价值</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">市盈率 PE</div>
                        <div class="big-number gradient-text">{valuation.get('pe', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_pe_evaluation(valuation.get('pe', 0))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">市净率 PB</div>
                        <div class="big-number text-white">{valuation.get('pb', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_pb_evaluation(valuation.get('pb', 0))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">市销率 PS</div>
                        <div class="big-number text-white">{valuation.get('ps', 0):.2f}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">总市值</div>
                        <div class="text-lg font-bold">{valuation.get('market_cap_str', 'N/A')}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>深度解读 <span class="ml-2 px-1.5 py-0.5 rounded text-xs" style="background:#22c55e20;color:#22c55e">实时数据</span></div>
                    <div class="text-sm text-gray-300 leading-relaxed">{valuation.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 盈利能力 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">盈利能力</h2>
                <p class="text-gray-500 text-xs">企业竞争力与盈利质量</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="text-xs text-gray-500 mb-3">📅 {profitability.get('fiscal_period', '最新财报数据 (TTM)')}</div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">净资产收益率</div>
                        <div class="big-number gradient-text">{to_float(profitability.get('roe'))*100:.1f}%</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_roe_evaluation(profitability.get('roe') or 0)}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">毛利率</div>
                        <div class="big-number text-white">{profitability.get('gross_margin', 0)*100:.1f}%</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">净利率</div>
                        <div class="big-number text-white">{profitability.get('net_margin', 0)*100:.1f}%</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">盈利状态</div>
                        <div class="text-2xl font-bold" style="color: {'#22c55e' if profitability.get('is_profitable') else '#ef4444'}">
                            {'盈利' if profitability.get('is_profitable') else '亏损'}
                        </div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>深度解读 <span class="ml-2 px-1.5 py-0.5 rounded text-xs" style="background:#22c55e20;color:#22c55e">实时数据</span></div>
                    <div class="text-sm text-gray-300 leading-relaxed">{profitability.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 财务健康 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">财务健康</h2>
                <p class="text-gray-500 text-xs">财务风险与偿债能力</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">资产负债率</div>
                        <div class="big-number text-white">{financial.get('debt_ratio', 0):.1f}%</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_debt_evaluation(financial.get('debt_ratio', 0))}</div>
                        <div class="mt-2 px-2 py-1 rounded text-xs inline-block" style="background: {self.brand_color}20; color: {self.brand_color}">
                            {financial.get('data_source', '财报')} ({financial.get('confidence', 0)*100:.0f}%置信度)
                        </div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">流动比率</div>
                        <div class="big-number text-white">{to_float(financial.get('current_ratio')):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_liquidity_evaluation(financial.get('current_ratio', 0))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">财务状态</div>
                        <div class="text-2xl font-bold gradient-text">{financial.get('status', '未知')}</div>
                    </div>
                </div>
                {self._generate_risk_alerts(financial.get('risks', []))}
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>深度解读 <span class="ml-2 px-1.5 py-0.5 rounded text-xs" style="background:#22c55e20;color:#22c55e">实时数据</span></div>
                    <div class="text-sm text-gray-300 leading-relaxed">{financial.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 技术面分析 -->
    <section class="px-4 py-6">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-6 fade-in">
                <h2 class="text-2xl font-bold mb-1">📈 技术面分析 <span class="text-sm font-normal text-gray-500">(含形态预警)</span></h2>
                <p class="text-gray-500 text-xs"></p>
            </div>
        </div>
    </section>
    
    <!-- 技术分析 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">技术分析</h2>
                <p class="text-gray-500 text-xs">趋势形态与交易信号</p>
            </div>
            
            <!-- 核心指标 -->
            <div class="card rounded-2xl p-6 fade-in mb-4">
                <h3 class="text-base font-bold mb-3" style="display:none"><i class="fas fa-chart-line mr-2" style="color: {self.brand_color}"></i>核心指标</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">RSI 相对强弱</div>
                        <div class="big-number text-white">{tech.get('indicators', {}).get('rsi', 50):.1f}</div>
                        <div class="text-xs mt-1 text-gray-500">{tech.get('patterns', {}).get('rsi_desc', 'N/A')}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">MACD 状态</div>
                        <div class="text-xl font-bold" style="color: {'#22c55e' if tech.get('indicators', {}).get('macd_cross', 'bullish') in ['golden', 'bullish'] else '#ef4444'}">
                            {'金叉' if tech.get('indicators', {}).get('macd_cross', '') == 'golden' else '死叉' if tech.get('indicators', {}).get('macd_cross', '') == 'dead' else '多头' if tech.get('indicators', {}).get('macd_cross', '') == 'bullish' else '空头'}
                        </div>
                        <div class="text-xs text-gray-500">DIF:{tech.get('indicators', {}).get('macd', 0):.2f} DEA:{tech.get('indicators', {}).get('macd_signal', 0):.2f}</div>
                    </div>
                </div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">趋势判断</div>
                        <div class="text-xl font-bold gradient-text">
                            {str(tech.get('patterns', {}).get('trend_desc', 'N/A')).split('(')[0].strip()}
                        </div>
                        <div class="text-xs mt-1 text-gray-500">均线系统</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">技术面评分</div>
                        <div class="big-number text-white">{tech.get('signal_strength', 50)}</div>
                        <div class="text-xs mt-1 text-gray-500">0=极弱 50=中性 100=极强</div>
                    </div>
                </div>
            </div>
            
            <!-- 支撑阻力位 -->
            <div class="card rounded-2xl p-6 fade-in mb-4">
                <h3 class="text-base font-bold mb-3" style="display:none"><i class="fas fa-layer-group mr-2" style="color: {self.brand_color}"></i>支撑阻力位分析</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">近期支撑</div>
                        <div class="text-2xl font-bold text-green-400">{tech.get('patterns', {}).get('support_near', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{tech.get('patterns', {}).get('support_near_pct', 0):.1f}% 距离</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">远期支撑</div>
                        <div class="text-2xl font-bold text-green-600">{tech.get('patterns', {}).get('support_far', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{tech.get('patterns', {}).get('support_far_pct', 0):.1f}% 距离</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">近期阻力</div>
                        <div class="text-2xl font-bold text-red-400">{tech.get('patterns', {}).get('resistance_near', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{tech.get('patterns', {}).get('resistance_near_pct', 0):.1f}% 距离</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">远期阻力</div>
                        <div class="text-2xl font-bold text-red-600">{tech.get('patterns', {}).get('resistance_far', 0):.2f}</div>
                        <div class="text-xs mt-1 text-gray-500">{tech.get('patterns', {}).get('resistance_far_pct', 0):.1f}% 距离</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>支撑阻力解读</div>
                    <div class="text-sm text-gray-300 leading-relaxed">
                        【支撑分析】{tech.get('patterns', {}).get('support_desc', '暂无数据')}
                        <br><br>
                        【阻力分析】{tech.get('patterns', {}).get('resistance_desc', '暂无数据')}
                    </div>
                </div>
            </div>
            
            <!-- 成交量验证 -->
            <div class="card rounded-2xl p-6 fade-in mb-4">
                <h3 class="text-base font-bold mb-3"><i class="fas fa-chart-bar mr-2" style="color: {self.brand_color}"></i>成交量验证</h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">成交量比率</div>
                        <div class="big-number text-white">{volume_val.get('volume_ratio', 1):.2f}x</div>
                        <div class="text-xs mt-1 text-gray-500">{self._get_volume_level(volume_val.get('volume_ratio', 1))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">成交量状态</div>
                        <div class="text-xl font-bold gradient-text">{volume_val.get('vp_signal', volume_val.get('status', 'N/A'))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">量价关系</div>
                        <div class="text-xl font-bold text-white">{volume_val.get('vp_pattern', 'N/A')}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>成交量解读</div>
                    <div class="text-sm text-gray-300 leading-relaxed">{volume_val.get('analysis', '暂无分析')}</div>
                </div>
            </div>
            
            <!-- 信号列表 (带详细解释) -->
            <div class="card rounded-2xl p-6 fade-in mb-4">
                <h3 class="text-base font-bold mb-3" style="display:none"><i class="fas fa-broadcast-tower mr-2" style="color: {self.brand_color}"></i>交易信号</h3>
                <div class="space-y-2">
                    {''.join([f"""
                    <div class="p-3 bg-gray-800 rounded-lg">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-gray-300 text-sm font-medium">{s.get('name', '')}</span>
                            <span class="px-2 py-1 rounded text-xs" style="background: {'#22c55e20' if s.get('strength', 0) > 0 else '#ef444420' if s.get('strength', 0) < 0 else '#f59e0b20'}; color: {'#22c55e' if s.get('strength', 0) > 0 else '#ef4444' if s.get('strength', 0) < 0 else '#f59e0b'}">{s.get('signal', '')}</span>
                        </div>
                        <div class="text-xs text-gray-500">{s.get('desc', '') + ' (日线)'}</div>
                    </div>
                    """ for s in tech.get('signals', [])[:3]]) or '<div class="text-gray-500 text-sm">暂无明显交易信号</div>'}
                </div>
                <div class="mt-3 p-3 bg-gray-800 rounded-lg">
                    <div class="text-center mb-2">
                        <span class="text-gray-400 text-sm">技术面判断: </span>
                        <span class="font-bold" style="color: {'#22c55e' if tech.get('total_strength', 0) > 0 else '#ef4444' if tech.get('total_strength', 0) < 0 else '#f59e0b'}">{'偏多' if tech.get('total_strength', 0) > 0 else '偏空' if tech.get('total_strength', 0) < 0 else '中性'} ({tech.get('total_strength', 0):+d})</span>
                    </div>
                    <div class="text-xs text-gray-500 text-center">
                        {'上涨趋势中，均线多头排列，MACD金叉，短期有望继续上行' if tech.get('total_strength', 0) > 3 else '下跌趋势中，均线空头排列，MACD死叉，短期可能继续调整' if tech.get('total_strength', 0) < -3 else '震荡整理中，多空平衡，建议观望或高抛低吸'}
                    </div>
                </div>
                
                <div class="mt-3 p-2 bg-gray-800 rounded-lg text-center">
                    <span class="text-gray-400 text-sm">信号强度: </span>

            <!-- 风险提醒 -->
            <div class="card rounded-2xl p-6 fade-in mb-4" style="border-left: 3px solid #ef4444">
                <h3 class="text-base font-bold mb-3" style="color: #ef4444"><i class="fas fa-exclamation-triangle mr-2"></i>风险提醒</h3>
                <div class="space-y-2">
                    {''.join([f'<div class="p-2 bg-red-900/20 rounded text-sm text-red-300">• {w}</div>' for w in volume_val.get('warnings', [])]) if volume_val.get('warnings') else ''}
                    {''.join([f'<div class="p-2 bg-red-900/20 rounded text-sm text-red-300">• 失败形态: {p.get("name", "")}</div>' for p in result.get("failed_patterns", {}).get("patterns", [])[:2]]) if result.get("failed_patterns", {}).get("count", 0) > 0 else ''}
                    {'<div class="p-2 bg-yellow-900/20 rounded text-sm text-yellow-300">• 估值偏高 (PE>' + str(int(valuation.get("pe", 0))) + ')</div>' if valuation.get("pe", 0) > 40 else ''}
                    {'<div class="p-2 bg-yellow-900/20 rounded text-sm text-yellow-300">• 主力净流出</div>' if volume_val.get("vp_signal") in ["量价背离", "放量下跌"] else ''}
                </div>
            </div>
                    <span class="font-bold" style="color: {'#22c55e' if tech.get('total_strength', 0) > 0 else '#ef4444' if tech.get('total_strength', 0) < 0 else '#f59e0b'}">{tech.get('total_strength', 0):+d}</span>
                </div>
            </div>
            
        </div>
    </section>
    
    <!-- 风险管理 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">风险管理</h2>
                <p class="text-gray-500 text-xs">止损策略与仓位建议</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <!-- 支撑阻力与ATR关系说明 -->
                <div class="p-3 bg-blue-900 rounded-lg text-sm text-gray-300 mb-4">
                    <span class="font-bold text-blue-400">📊 支撑阻力 vs ATR止损的关系：</span><br>
                    • <span class="font-semibold">支撑/阻力位</span>是价格可能反转的技术点位<br>
                    • <span class="font-semibold">ATR止损</span>是基于市场波动的风险控制位，2倍ATR是趋势交易标准止损<br>
                    • 两者结合：支撑位作为目标参考，ATR止损作为风险底线
                </div>
                
                <h3 class="text-base font-bold mb-3"><i class="fas fa-shield-alt mr-2" style="color: {self.brand_color}"></i>ATR止损建议</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">当前价格</div>
                        <div class="big-number text-white">{risk_mgmt.get('current_price', 0):.2f}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">标准止损</div>
                        <div class="big-number text-red-400">{risk_mgmt.get('stop_loss_standard', risk_mgmt.get('stop_loss_price', 0)):.2f}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">保守止损</div>
                        <div class="big-number text-orange-400">{risk_mgmt.get('stop_loss_conservative', 0):.2f}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">ATR值</div>
                        <div class="big-number text-white">{risk_mgmt.get('atr', 0):.2f}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>止损策略解读</div>
                    <div class="text-sm text-gray-300 leading-relaxed">{risk_mgmt.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- 失败形态预警 (如果有信号则显示) -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">形态预警</h2>
                <p class="text-gray-500 text-xs">识别常见失败形态，避免高位接盘</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                {self._generate_failed_patterns_html(result)}
            </div>
        </div>
    </section>
    
    <!-- 综合评估 (包含分析逻辑 + 操作建议 + 风险管理) -->
    {self._generate_summary_section(result)}
    
    <!-- Footer -->
    <footer class="px-4 py-6 border-t border-gray-800">
        <div class="max-w-7xl mx-auto text-center text-gray-500 text-xs">
            <div class="mb-2">{stock_name} 投资分析报告 · {result.get('timestamp', '')}</div>
            <div class="mb-2">数据来源: yfinance · 分析周期: 日线(60交易日)</div>
            <div class="text-gray-600">⚠️ 免责声明：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</div>
        </div>
    </footer>
    
    <script>
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) entry.target.classList.add('visible');
            }});
        }}, {{ threshold: 0.1 }});
        
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
        
        const ctx = document.getElementById('radarChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['盈利能力', '估值水平', '财务健康', '技术面', '成长性'],
                datasets: [{{
                    data: [
                        {min((profitability.get('roe') or 0) * 500, 100)},
                        {max(100 - valuation.get('pe', 50), 0)},
                        {100 - financial.get('debt_ratio', 50)},
                        {tech.get('signal_strength', 0) * 10 + 50},
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
                        pointLabels: {{ color: '#fff', font: {{ size: 12 }} }}
                    }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
    </script>
    
</body>
</html>'''
    
    def _get_pe_evaluation(self, pe: float) -> str:
        if pe < 15: return '低估'
        elif pe < 25: return '合理'
        elif pe < 40: return '偏高'
        return '高估'
    
    def _get_pb_evaluation(self, pb: float) -> str:
        if pb < 2: return '低估'
        elif pb < 4: return '合理'
        elif pb < 6: return '偏高'
        return '高估'
    
    def _get_roe_evaluation(self, roe: float) -> str:
        if roe > 0.20: return '优秀'
        elif roe > 0.15: return '良好'
        elif roe > 0.10: return '一般'
        return '较差'
    
    def _get_debt_evaluation(self, debt: float) -> str:
        if debt < 40: return '低风险'
        elif debt < 60: return '适中'
        elif debt < 70: return '需关注'
        return '高风险'
    
    def _get_volume_level(self, ratio: float) -> str:
        """成交量水平评估"""
        if ratio > 2: return '放量'
        elif ratio > 1: return '正常'
        elif ratio > 0.5: return '偏低'
        return '缩量'
    
    def _get_liquidity_evaluation(self, ratio: float) -> str:
        if ratio is None: return '数据不足'
        if ratio > 2: return '流动性好'
        elif ratio > 1: return '流动性正常'
        elif ratio > 0.5: return '流动性不足'
        return '流动性风险'
    
    def _translate_industry(self, name: str) -> str:
        """行业名称翻译兜底"""
        translations = {
            'Specialty Industrial Machinery': '专用设备',
            'Consumer Electronics': '消费电子',
            'Semiconductors': '半导体',
            'Software': '软件',
            'Pharmaceuticals': '制药',
            'Biotechnology': '生物技术',
            'Automobile': '汽车',
            'Real Estate': '房地产',
            'Banking': '银行',
            'Insurance': '保险',
        }
        return translations.get(name, name)

        if ratio > 2: return '放量'
        elif ratio > 1.5: return '温和放量'
        elif ratio > 0.8: return '正常'
        return '缩量'
    
    def _generate_risk_alerts(self, risks: list) -> str:
        if not risks:
            return ''
        
        alerts = ''
        for risk in risks:
            alerts += f'''
                <div class="mt-3 p-3 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
                    <div class="flex items-center gap-2">
                        <i class="fas fa-exclamation-triangle text-yellow-500 text-sm"></i>
                        <span class="text-sm text-gray-300">{risk}</span>
                    </div>
                </div>'''
        return alerts
    
    def _generate_action_advice(self, result: Dict) -> str:
        """生成基于实际数据的操作建议 - 包含不同投资风格"""
        tech = result.get('technical', {})
        volume = result.get('volume_validation', {})
        price = result.get('price', {})
        risk_mgmt = result.get('risk_management', {})
        score = result.get('score', 50)
        
        current = price.get('current', 0)
        support_near = tech.get('patterns', {}).get('support_near', 0)
        resistance_near = tech.get('patterns', {}).get('resistance_near', 0)
        rsi = tech.get('indicators', {}).get('rsi', 50)
        volume_ratio = volume.get('volume_ratio', 1)
        trend = str(tech.get('patterns', {}).get('trend_desc', '')).split('(')[0].strip()
        total_strength = tech.get('total_strength', 0)
        atr = risk_mgmt.get('atr', 0)
        stop_loss = risk_mgmt.get('stop_loss_standard', 0)
        
        # 基于实际数据生成建议
        advice = []
        
        # 趋势建议
        if '多头' in trend:
            advice.append(f"当前处于{trend}，趋势向上，可考虑持股或逢低加仓")
        elif '空头' in trend:
            advice.append(f"当前处于{trend}，趋势向下，建议观望或减仓")
        else:
            advice.append(f"当前趋势{trend}，建议观望等待方向明确")
        
        # RSI建议
        if rsi > 80:
            advice.append(f"RSI={rsi:.1f}极度超买，短期回调风险大，不建议追高")
        elif rsi > 70:
            advice.append(f"RSI={rsi:.1f}超买，注意回调风险，可考虑逢高减仓")
        elif rsi < 30:
            advice.append(f"RSI={rsi:.1f}超卖，可能存在反弹机会，可关注")
        
        # 支撑阻力建议
        if current and support_near:
            support_pct = (current - support_near) / current * 100
            advice.append(f"近期支撑位{support_near:.2f}元(距离{support_pct:.1f}%)，跌破支撑需警惕")
        
        if current and resistance_near:
            resistance_pct = (resistance_near - current) / current * 100
            advice.append(f"近期阻力位{resistance_near:.2f}元(距离{resistance_pct:.1f}%)，突破阻力可加仓")
        
        # 成交量建议
        if volume_ratio > 1.5:
            advice.append(f"成交量放大{volume_ratio:.2f}倍，市场活跃度高，趋势可信")
        elif volume_ratio < 0.8:
            advice.append(f"成交量萎缩至{volume_ratio:.2f}倍，市场观望情绪浓，注意风险")
        
        advice_text = '<br><br>'.join(advice)
        
        # 针对不同投资风格的操作建议
        short_term = ""  # 短线 (1-5天)
        mid_term = ""    # 中线 (1-4周)
        long_term = ""   # 长线 (1-3月)
        
        if rsi < 30 and volume_ratio > 1.2:
            short_term = "超卖+放量，短线可能有反弹机会，激进型可轻仓试多"
        elif rsi > 70:
            short_term = "超买信号，短线风险较大，建议观望或减仓"
        else:
            short_term = "无明显短线信号，保持观望"
        
        if total_strength > 3 and score > 60:
            mid_term = "技术面偏多+基本面良好，可考虑分批建仓，止损设在支撑位下方"
        elif total_strength < -3 or score < 40:
            mid_term = "技术面偏弱+基本面一般，建议继续观望，等待信号好转"
        else:
            mid_term = "中性震荡格局，建议高抛低吸，跌破支撑减仓"
        
        if score >= 70 and '多头' in trend:
            long_term = "基本面+技术面均向好，适合长线持有，逢低布局"
        elif score < 50:
            long_term = "基本面存在隐忧，建议等待基本面改善后再考虑长线"
        else:
            long_term = "基本面尚可，长线可持有但需关注止损位"
        
        return f'''
            <div class="card rounded-2xl p-6 fade-in">
                <h3 class="text-base font-bold mb-3"><i class="fas fa-lightbulb mr-2" style="color: #fbbf24"></i>操作建议</h3>
                
                <!-- 当前市场解读 -->
                <div class="action-box mb-4">
                    <div class="text-sm text-gray-300 leading-relaxed">{advice_text}</div>
                </div>
                
                <!-- 针对不同投资风格 -->
                <div class="mt-4">
                    <h4 class="font-bold text-white mb-3"><i class="fas fa-users mr-2"></i>不同投资风格建议</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div class="p-3 bg-orange-900 rounded-lg">
                            <div class="font-bold text-orange-400 mb-2">🔥 短线 (1-5天)</div>
                            <div class="text-sm text-gray-300">{short_term}</div>
                            <div class="text-xs text-gray-500 mt-2">止损: {stop_loss:.2f}元 ({abs((stop_loss-current)/current*100):.1f}%)</div>
                        </div>
                        <div class="p-3 bg-blue-900 rounded-lg">
                            <div class="font-bold text-blue-400 mb-2">⚡ 中线 (1-4周)</div>
                            <div class="text-sm text-gray-300">{mid_term}</div>
                            <div class="text-xs text-gray-500 mt-2">目标: {resistance_near:.2f}元</div>
                        </div>
                        <div class="p-3 bg-green-900 rounded-lg">
                            <div class="font-bold text-green-400 mb-2">📈 长线 (1-3月)</div>
                            <div class="text-sm text-gray-300">{long_term}</div>
                            <div class="text-xs text-gray-500 mt-2">关注ROE变化</div>
                        </div>
                    </div>
                </div>
            </div>'''
    
    def _generate_failed_patterns_html(self, result: Dict) -> str:
        """生成失败形态预警HTML - 跳过风险提醒中已显示的形态"""
        failed = result.get('failed_patterns', {})
        patterns = failed.get('patterns', [])
        
        if not patterns:
            return '<div class="text-gray-500 text-center p-4">未检测到失败形态</div>'
        
        # 风险提醒区块显示了前2个形态，这里跳过前2个避免重复
        remaining_patterns = patterns[2:] if len(patterns) > 2 else []
        
        if not remaining_patterns:
            return '<div class="text-gray-500 text-center p-4">其他形态详见风险提醒</div>'
        
        html = '<div class="space-y-3">'
        for p in remaining_patterns:
            confidence = p.get('confidence', 0) * 100
            html += f'''
            <div class="p-3 bg-red-900 rounded-lg">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-bold text-red-400">{p.get('name', '未知形态')}</span>
                    <span class="text-xs px-2 py-1 rounded bg-red-800 text-red-300">置信度 {confidence:.0f}%</span>
                </div>
                <div class="text-sm text-gray-300">{p.get('pattern', '')}</div>
                <div class="mt-2 text-xs text-gray-400">反向操作: {p.get('reverse_action', '观望')}</div>
            </div>'''
        html += '</div>'
        
        html += f'''
        <div class="mt-4 p-3 bg-gray-800 rounded-lg text-sm text-gray-400">
            <i class="fas fa-exclamation-triangle mr-2 text-yellow-500"></i>{failed.get('analysis', '形态检测完成')}
        </div>'''
        return html
    
    def _generate_buff_from_win_rate(self, result: Dict) -> str:
        """基于胜率模型生成Buff"""
        buff_data = result.get('buff_enhanced', {})
        buffs = buff_data.get('buffs', [])
        total_score = buff_data.get('total_score', 0)
        direction = buff_data.get('direction', '中性')
        icon = buff_data.get('icon', '⚖️')
        win_rate = buff_data.get('win_rate', 0.5)
        
        # 生成HTML卡片
        cards = ''
        for buff in buffs:
            score = buff['score']
            color = '#22c55e' if score > 0 else ('#ef4444' if score < 0 else '#f59e0b')
            cards += f'''
            <div class="mini-card rounded-lg p-4">
                <div class="text-gray-400 text-xs mb-1">{buff['type']}</div>
                <div class="text-2xl font-bold" style="color: {color}">{score:+.1f}</div>
                <div class="text-xs mt-1 text-gray-500">{buff['description']}</div>
            </div>
            '''
        
        total_color = '#22c55e' if total_score > 0 else ('#ef4444' if total_score < 0 else '#f59e0b')
        
        return f'''
        <div class="card rounded-2xl p-6 fade-in mb-4">
            <h3 class="text-base font-bold mb-3" style="display:none"><i class="fas fa-layer-group mr-2" style="color: {self.brand_color}"></i>Buff叠加分析</h3>
            <div class="mb-4 text-sm text-gray-400">
                <i class="fas fa-percentage mr-1"></i>技术面胜率：<span class="font-bold" style="color: {total_color}">{win_rate*100:.1f}%</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                {cards}
            </div>
            <div class="analysis-box">
                <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {self.brand_color}"></i>综合Buff</div>
                <div class="text-2xl font-bold mb-2" style="color: {total_color}">{icon} {direction} ({total_score:+.1f})</div>
                <div class="text-sm text-gray-400">基于胜率模型的综合评估</div>
            </div>
        </div>
        '''

    def _generate_summary_section(self, result: Dict) -> str:
        """生成综合评估部分 - 增强版，包含全局详尽分析"""
        summary = result.get('summary', {})
        industry = result.get('industry', {})
        profitability = result.get('profitability', {})
        valuation = result.get('valuation', {})
        financial = result.get('financial', {})
        tech = result.get('technical', {})
        score = result.get('score', 0)
        recommendation = result.get('recommendation', '观望')
        
        # 构建全局详尽分析
        analysis_parts = []
        
        # 1. 行业层面分析
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-industry mr-2" style="color: {self.brand_color}"></i>一、行业与定位分析</h4>
            <div class="p-4 bg-gray-800 rounded-lg text-gray-300 leading-relaxed">
                {summary.get('industry_analysis', '暂无分析')}
                <br><br>
                <span class="text-gray-400">行业周期判断：</span>{industry.get('cycle', '未知')}，
                行业风险等级：{industry.get('risk', '中')}
            </div>
        </div>
        """)
        
        # 2. 基本面分析
        roe = profitability.get('roe') or 0
        gm = profitability.get('gross_margin', 0)
        nm = profitability.get('net_margin', 0)
        pe = valuation.get('pe', 0)
        pb = valuation.get('pb', 0)
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-chart-line mr-2" style="color: {self.brand_color}"></i>二、基本面深度分析</h4>
            <div class="p-4 bg-gray-800 rounded-lg text-gray-300 leading-relaxed">
                <span class="text-gray-400">盈利能力：</span>{summary.get('profit_analysis', '暂无分析')}<br>
                关键指标：ROE={roe*100:.1f}%，毛利率={gm*100:.1f}%，净利率={nm*100:.1f}%<br><br>
                <span class="text-gray-400">估值水平：</span>{summary.get('valuation_analysis', '暂无分析')}<br>
                关键指标：PE={pe:.1f}倍，PB={pb:.1f}倍<br><br>
                <span class="text-gray-400">财务健康：</span>{summary.get('financial_analysis', '暂无分析')}
            </div>
        </div>
        """)
        
        # 3. 技术面分析
        trend = tech.get('trend', '')
        rsi = tech.get('rsi', 50)
        total_strength = tech.get('total_strength', 0)
        signals = tech.get('signals', [])
        signal_names = [s.get('name', '') for s in signals if s.get('strength', 0) != 0]
        
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-chart-pie mr-2" style="color: {self.brand_color}"></i>三、技术面综合分析</h4>
            <div class="p-4 bg-gray-800 rounded-lg text-gray-300 leading-relaxed">
                {summary.get('tech_analysis', '暂无分析')}<br><br>
                <span class="text-gray-400">趋势状态：</span>{trend}<br>
                <span class="text-gray-400">RSI指标：</span>{rsi:.1f} ({'超买' if rsi > 70 else '超卖' if rsi < 30 else '中性'})<br>
                <span class="text-gray-400">信号强度：</span>{total_strength:+d} ({'偏多' if total_strength > 0 else '偏空' if total_strength < 0 else '中性'})<br>
                <span class="text-gray-400">活跃信号：</span>{', '.join(signal_names) if signal_names else '无'}
            </div>
        </div>
        """)
        
        # 4. 综合判断
        final = summary.get('final', '')
        risk_mgmt = result.get('risk_management', {})
        atr = risk_mgmt.get('atr', 0)
        stop_loss = risk_mgmt.get('stop_loss_standard', 0)
        
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-balance-scale mr-2" style="color: {self.brand_color}"></i>四、综合判断与投资建议</h4>
            <div class="p-4 bg-gray-800 rounded-lg text-gray-300">
                <div class="mb-4 p-3 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-lg">
                    <span class="text-gray-400">综合评分（基本面+技术面）：</span><span class="text-2xl font-bold text-white">{score}</span>/100
                    <span class="ml-3 px-3 py-1 rounded-full text-sm font-bold" style="background:#22c55e30;color:#22c55e">{recommendation}</span>
                </div>
                <div class="mb-4">{final}</div>
                <div class="grid grid-cols-2 gap-4">
                    <div class="p-3 bg-red-900/20 rounded-lg">
                        <div class="text-red-400 font-bold mb-2">风险控制</div>
                        <div class="text-sm">ATR: {atr:.2f} · 止损: <span class="text-red-400 font-bold">{stop_loss:.2f}元</span></div>
                    </div>
                    <div class="p-3 bg-green-900/20 rounded-lg">
                        <div class="text-green-400 font-bold mb-2">机构观点</div>
                        <div class="text-sm">{result.get('research', {}).get('recommendation', recommendation)}</div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # 5. 研报分析 (如果可用)
        research = result.get('research', {})
        if research.get('available'):
            # 使用综合报告的核心观点
            phase8 = research.get('phase8', {})
            executive_summary = phase8.get('executive_summary', {})
            investment_thesis = phase8.get('investment_thesis', {})
            key_signals = phase8.get('key_signals', [])
            
            # 机构评级
            phase6 = research.get('phase6', {})
            analyst_ratings = phase6.get('analyst_ratings', {})
            rating = analyst_ratings.get('recommendation', '暂无')
            target_price = analyst_ratings.get('target_price', '暂无')
            analyst_count = analyst_ratings.get('number_of_analysts', '暂无')
            
            # 估值数据
            phase7 = research.get('phase7', {})
            relative_val = phase7.get('relative_valuation', {})
            moat = phase7.get('moat_assessment', {})
            
            analysis_parts.append(f"""
            <div class="mb-6">
                <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-file-alt mr-2" style="color: {self.brand_color}"></i>五、机构研报与估值分析</h4>
                <div class="p-4 bg-gray-800 rounded-lg text-gray-300 leading-relaxed">
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div><span class="text-gray-400">机构评级：</span><span class="font-bold text-green-400">{rating.upper() if rating and rating != 'none' else '暂无'}</span></div>
                        <div><span class="text-gray-400">目标价：</span>{f"{target_price:.2f}" if target_price else '暂无'}</div>
                        <div><span class="text-gray-400">PE：</span>{relative_val.get('pe_ratio', 'N/A')}</div>
                        <div><span class="text-gray-400">护城河：</span><span class="font-bold text-blue-400">{moat.get('level', '暂无')} ({moat.get('score', 0)}/6分)</span></div>
                        <div><span class="text-gray-400">分析师：</span>{analyst_count}人</div>
                    </div>
                    <div class="mb-3"><span class="text-gray-400">关键信号：</span></div>
                    <div class="flex flex-wrap gap-2">
                        {''.join([f'<span class="px-2 py-1 bg-gray-700 rounded text-xs">{sig}</span>' for sig in key_signals[:5]]) if key_signals else '<span class="px-2 py-1 bg-gray-700 rounded text-xs">暂无</span>'}
                    </div>
                </div>
            </div>
            """)
        
        # 6. 投资逻辑分析
        bull_points = []
        bear_points = []
        
        # 看多逻辑
        if profitability.get('roe', 0) > 0.15:
            bull_points.append(f"盈利能力较强(ROE={profitability.get('roe', 0)*100:.1f}%)")
        if valuation.get('pe', 0) < 40:
            bull_points.append(f"估值相对合理(PE={valuation.get('pe', 0):.2f})")
        if total_strength > 0:
            bull_points.append(f"技术面偏多(信号强度:{total_strength:+d})")
        if financial.get('status') == '健康':
            bull_points.append("财务健康")
        
        # 看空逻辑
        if valuation.get('pe', 0) > 40:
            bear_points.append("估值偏高，回调风险")
        if total_strength < 0:
            bear_points.append("技术面偏弱")
        if financial.get('status') in ['高风险', '需关注']:
            bear_points.append(f"财务{financial.get('status', '风险')}")
        
        bull_html = ''.join([f'<li>{p}</li>' for p in bull_points]) or '<li>暂无明确看多逻辑</li>'
        bear_html = ''.join([f'<li>{p}</li>' for p in bear_points]) or '<li>暂无明确看空逻辑</li>'
        
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-brain mr-2" style="color: {self.brand_color}"></i>六、投资逻辑分析</h4>
            <div class="p-4 bg-gray-800 rounded-lg">
                <div class="mb-4">
                    <div class="text-green-400 font-bold mb-2">看多逻辑</div>
                    <ul class="text-sm text-gray-300 space-y-1">{bull_html}</ul>
                </div>
                <div>
                    <div class="text-red-400 font-bold mb-2">看空逻辑</div>
                    <ul class="text-sm text-gray-300 space-y-1">{bear_html}</ul>
                </div>
            </div>
        </div>
        """)
        
        
        # 8. 交易建议
        ta = result.get('trading_advice', {})
        rm = ta.get('risk_management', {})
        kl = ta.get('key_levels', {})
        
        analysis_parts.append(f"""
        <div class="mb-6">
            <h4 class="text-lg font-bold text-white mb-3"><i class="fas fa-chess mr-2" style="color: {self.brand_color}"></i>八、交易建议</h4>
            <div class="p-4 bg-gray-800 rounded-lg">
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="p-3 bg-blue-900/30 rounded-lg">
                        <div class="text-blue-400 font-bold mb-1">短期策略</div>
                        <div class="text-white font-semibold">{ta.get('short_term', {}).get('strategy', 'N/A')}</div>
                        <div class="text-xs text-gray-400 mt-1">买入区间: {ta.get('short_term', {}).get('entry_zone', 'N/A')}</div>
                    </div>
                    <div class="p-3 bg-purple-900/30 rounded-lg">
                        <div class="text-purple-400 font-bold mb-1">中期策略</div>
                        <div class="text-white font-semibold">{ta.get('mid_term', {}).get('strategy', 'N/A')}</div>
                        <div class="text-xs text-gray-400 mt-1">持有: {ta.get('mid_term', {}).get('holding_weeks', 'N/A')}</div>
                    </div>
                </div>
                <div class="p-3 bg-red-900/20 rounded-lg mb-3">
                    <div class="text-red-400 font-bold mb-1">止损位</div>
                    <div class="text-white font-semibold">{rm.get('stop_loss', 0):.2f}元 ({rm.get('stop_loss_pct', 0):.1f}%)</div>
                </div>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-400">当前价</span>
                        <span class="text-white font-bold">{kl.get('current', 0):.2f} 元</span>
                    </div>
                    <div class="flex justify-between items-center p-1 bg-red-900/20 rounded">
                        <span class="text-red-400">近支撑</span>
                        <span class="text-red-400 font-bold">{kl.get('support_near', 0):.2f} 元</span>
                    </div>
                    <div class="flex justify-between items-center p-1 bg-red-900/10 rounded">
                        <span class="text-gray-500">远支撑</span>
                        <span class="text-gray-400">{kl.get('support_far', 0):.2f} 元</span>
                    </div>
                    <div class="flex justify-between items-center p-1 bg-green-900/20 rounded">
                        <span class="text-green-400">近压力</span>
                        <span class="text-green-400 font-bold">{kl.get('resistance_near', 0):.2f} 元</span>
                    </div>
                    <div class="flex justify-between items-center p-1 bg-green-900/10 rounded">
                        <span class="text-gray-500">远压力</span>
                        <span class="text-gray-400">{kl.get('resistance_far', 0):.2f} 元</span>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        analysis_html = '\n'.join(analysis_parts)
        
        return f'''
        <section class="px-4 py-10">
            <div class="max-w-7xl mx-auto">
                <div class="text-center mb-8 fade-in">
                    <h2 class="text-3xl font-bold mb-1">综合分析报告</h2>
                    <p class="text-gray-500 text-xs">基于全维度的系统性投资分析</p>
                </div>
                
                <div class="card rounded-2xl p-6 fade-in">
                    {analysis_html}
                </div>
            </div>
        </section>
        '''

    def _generate_buff_section(self, result: Dict) -> str:
        """生成详细的Buff分析"""
        
        # 如果有增强的buff数据，使用它
        if result.get('buff_enhanced', {}).get('win_rate_based'):
            return self._generate_buff_from_win_rate(result)
        
        # 否则使用原有逻辑
        buffs = []
        
        # 基本面buff
        roe = result.get('profitability', {}).get('roe', 0)
        if roe > 0.20:
            buffs.append(('基本面', '+3', f'ROE优秀({roe*100:.1f}%)，盈利能力强', '#22c55e'))
        elif roe > 0.15:
            buffs.append(('基本面', '+2', f'ROE良好({roe*100:.1f}%)，盈利稳健', '#22c55e'))
        elif roe > 0.10:
            buffs.append(('基本面', '+1', f'ROE一般({roe*100:.1f}%)', '#f59e0b'))
        else:
            buffs.append(('基本面', '-1', f'ROE较差({roe*100:.1f}%)', '#ef4444'))
        
        # 估值buff
        pe = result.get('valuation', {}).get('pe', 0)
        if pe and pe < 15:
            buffs.append(('估值', '+2', f'PE低估({pe:.1f})，安全边际高', '#22c55e'))
        elif pe and pe < 25:
            buffs.append(('估值', '+1', f'PE合理({pe:.1f})', '#f59e0b'))
        elif pe and pe > 40:
            buffs.append(('估值', '-2', f'PE高估({pe:.1f})，估值偏高', '#ef4444'))
        
        # 财务健康buff
        status = result.get('financial', {}).get('status', '')
        debt_ratio = result.get('financial', {}).get('debt_ratio', 0)
        if status == '健康':
            buffs.append(('财务', '+1', f'财务健康，资产负债率{debt_ratio:.1f}%', '#22c55e'))
        elif status == '需关注':
            buffs.append(('财务', '-1', f'财务需关注，资产负债率{debt_ratio:.1f}%', '#f59e0b'))
        elif status == '高风险':
            buffs.append(('财务', '-2', f'财务风险高，资产负债率{debt_ratio:.1f}%', '#ef4444'))
        
        # 技术面buff
        signal = result.get('technical', {}).get('signal_strength', 0)
        if signal > 3:
            buffs.append(('技术面', '+2', f'技术面强势，信号强度{signal}', '#22c55e'))
        elif signal > 0:
            buffs.append(('技术面', '+1', f'技术面偏多，信号强度{signal}', '#22c55e'))
        elif signal < -3:
            buffs.append(('技术面', '-2', f'技术面弱势，信号强度{signal}', '#ef4444'))
        elif signal < 0:
            buffs.append(('技术面', '-1', f'技术面偏空，信号强度{signal}', '#ef4444'))
        
        total = sum([int(b[1]) for b in buffs])
        total_color = '#22c55e' if total > 0 else ('#ef4444' if total < 0 else '#f59e0b')
        total_text = '偏多' if total > 0 else ('偏空' if total < 0 else '中性')
        
        cards = ''
        for buff_type, score, desc, color in buffs:
            cards += f'''
                <div class="mini-card rounded-lg p-3">
                    <div class="flex items-center justify-between mb-1">
                        <span class="text-sm font-bold">{buff_type}</span>
                        <span class="text-lg font-bold" style="color: {color}">{score}</span>
                    </div>
                    <div class="text-xs text-gray-400">{desc}</div>
                </div>'''
        
        return f'''
            <section class="px-4 py-10">
                <div class="max-w-7xl mx-auto">
                    <div class="text-center mb-8 fade-in">
                        <h2 class="text-3xl font-bold mb-1">Buff叠加分析</h2>
                        <p class="text-gray-500 text-xs">多维度综合评估</p>
                    </div>
                    
                    <div class="card rounded-2xl p-6 fade-in">
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                            {cards}
                        </div>
                        
                        <div class="p-4 rounded-lg" style="background: linear-gradient(135deg, {self.brand_color}20 0%, {self.brand_color}10 100%);">
                            <div class="flex items-center justify-between">
                                <div>
                                    <div class="text-sm text-gray-400">总Buff评分</div>
                                    <div class="text-2xl font-bold" style="color: {total_color}">{total:+d}</div>
                                </div>
                                <div class="text-right">
                                    <div class="text-sm text-gray-400">综合判断</div>
                                    <div class="text-xl font-bold">{total_text}</div>
                                    <div class="text-xs text-gray-500">综合评分 {result.get('score', 0)}/100</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>'''


def generate_apple_report(result: Dict) -> str:
    return AppleStyleReporter().generate(result)


if __name__ == '__main__':
    print("Apple风格报告生成器 v3.0")
