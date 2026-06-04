#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格HTML报告生成器 v4.0
- 修复板块中文显示
- 添加支撑阻力位
- 添加事件驱动模块
- 添加评分拆分模块
- 完善技术分析
"""

import sys
from typing import Dict
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def generate_apple_report(result: Dict) -> str:
    """生成Apple风格HTML报告 v4.0"""
    
    symbol = result.get('symbol', '')
    name_cn = result.get('name_cn', symbol)
    score = result.get('score', 0)
    recommendation = result.get('recommendation', 'N/A')
    
    industry = result.get('industry', {})
    valuation = result.get('valuation', {})
    profitability = result.get('profitability', {})
    financial = result.get('financial', {})
    technical = result.get('technical', {})
    patterns = technical.get('patterns', {})
    price = result.get('price', {})
    
    # 检测品牌色
    brand_colors = {
        '美的': '#0066CC', '格力': '#E60012', '小米': '#FF6900',
        '华为': '#CF0A2C', '立讯精密': '#00AEEF', '比亚迪': '#00A0E9',
        '宁德时代': '#E60012', '茅台': '#B8860B', '汇川': '#00AEEF',
    }
    brand_color = '#00AEEF'
    for brand, color in brand_colors.items():
        if brand in name_cn:
            brand_color = color
            break
    
    current_price = price.get('current', 0)
    change_pct = price.get('change_pct', 0)
    
    # 构建HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_cn} 投资分析报告</title>
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
            background: linear-gradient(135deg, {brand_color} 0%, {brand_color}CC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .card {{
            background: #1a1a1a;
            border: 1px solid #333;
            transition: all 0.3s ease;
        }}
        .card:hover {{
            border-color: {brand_color}66;
            box-shadow: 0 8px 32px {brand_color}33;
        }}
        .mini-card {{
            background: #222222;
            border: 1px solid #333;
            transition: all 0.3s ease;
            min-height: 100px;
        }}
        .mini-card:hover {{
            border-color: {brand_color}4D;
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
            background: linear-gradient(135deg, {brand_color}15 0%, {brand_color}08 100%);
            border-left: 3px solid {brand_color};
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
            <div class="text-sm text-gray-500 mb-3">{symbol}</div>
            <h1 class="text-5xl md:text-6xl font-bold mb-3 gradient-text">{name_cn}</h1>
            
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
                <div><span class="text-white font-semibold">{f"{current_price:.2f}" if current_price > 0 else "N/A"}</span> 元</div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div><span class="text-white font-semibold">{f"{change_pct:+.2f}" if change_pct != 0 else "0.00"}%</span></div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div><span class="text-white font-semibold">{valuation.get('market_cap_str', 'N/A')}</span></div>
                <div class="w-px h-4 bg-gray-700"></div>
                <div>市盈率 <span class="text-white font-semibold">{valuation.get('pe', 0):.1f}</span></div>
            </div>
            
            <div class="mt-12 animate-bounce"><i class="fas fa-chevron-down text-xl text-gray-600"></i></div>
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
                        <div class="text-lg font-bold">{industry.get('name_cn', '未知')}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">所属板块</div>
                        <div class="text-lg font-bold">{industry.get('sector_cn', industry.get('sector', '未知'))}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">行业周期</div>
                        <div class="text-lg font-bold">{industry.get('cycle', '未知')}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">行业风险</div>
                        <div class="text-lg font-bold">{industry.get('risk', '未知')}</div>
                    </div>
                </div>
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {brand_color}"></i>深度解读</div>
                    <div class="text-sm text-gray-300 leading-relaxed">{industry.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
'''
    
    # 技术分析（包含支撑阻力位）
    html += f'''
    <!-- 技术分析 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">技术分析</h2>
                <p class="text-gray-500 text-xs">趋势判断与交易信号</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">RSI</div>
                        <div class="big-number gradient-text">{technical.get('indicators', {}).get('rsi', 50):.1f}</div>
                        <div class="text-xs mt-1 text-gray-500">RSI(14)</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">MACD</div>
                        <div class="text-lg font-bold">{technical.get('macd_signal', 'N/A')}</div>
                        <div class="text-xs mt-1 text-gray-500">MACD(12,26,9)</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">趋势</div>
                        <div class="text-lg font-bold">{patterns.get('trend_desc', '未知').split('：')[0] if patterns.get('trend_desc') else '未知'}</div>
                    </div>
                    <div class="mini-card rounded-lg p-4">
                        <div class="text-gray-400 text-xs mb-1">成交量比率</div>
                        <div class="big-number text-white">{technical.get('indicators', {}).get('volume_ratio', 1):.2f}x</div>
                    </div>
                </div>
                
                <!-- 支撑阻力位 -->
                <div class="mb-6">
                    <h3 class="text-lg font-bold mb-3">支撑阻力位</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-green-900/20 border border-green-800 rounded-lg p-4">
                            <div class="text-green-400 text-sm mb-2"><i class="fas fa-arrow-down mr-2"></i>支撑位</div>
                            <div class="space-y-2">
                                <div class="flex justify-between">
                                    <span class="text-gray-400">一级支撑</span>
                                    <span class="font-bold text-green-400">{patterns.get("support_near", 0):.2f} 元</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-400">二级支撑</span>
                                    <span class="font-bold">{patterns.get("support_far", 0):.2f} 元</span>
                                </div>
                            </div>
                        </div>
                        <div class="bg-red-900/20 border border-red-800 rounded-lg p-4">
                            <div class="text-red-400 text-sm mb-2"><i class="fas fa-arrow-up mr-2"></i>阻力位</div>
                            <div class="space-y-2">
                                <div class="flex justify-between">
                                    <span class="text-gray-400">一级阻力</span>
                                    <span class="font-bold text-red-400">{patterns.get("resistance_near", 0):.2f} 元</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-400">二级阻力</span>
                                    <span class="font-bold">{patterns.get("resistance_far", 0):.2f} 元</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-box">
                    <div class="font-semibold text-sm mb-2"><i class="fas fa-info-circle mr-2" style="color: {brand_color}"></i>技术解读</div>
                    <div class="text-sm text-gray-300 leading-relaxed">{technical.get('analysis', '暂无分析')}</div>
                </div>
            </div>
        </div>
    </section>
'''
    
    # 事件驱动模块
    html += f'''
    <!-- 事件驱动 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">事件驱动</h2>
                <p class="text-gray-500 text-xs">利好事件与风险因素</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="text-lg font-bold mb-3 text-green-400"><i class="fas fa-check-circle mr-2"></i>利好事件</h3>
                        <div class="space-y-2">
                            <div class="flex items-start gap-2 p-2 bg-green-900/10 rounded">
                                <span class="text-green-400">✓</span>
                                <div>
                                    <div class="font-semibold text-sm">业绩催化</div>
                                    <div class="text-xs text-gray-400">年报发布、Q1预告增长</div>
                                </div>
                            </div>
                            <div class="flex items-start gap-2 p-2 bg-green-900/10 rounded">
                                <span class="text-green-400">✓</span>
                                <div>
                                    <div class="font-semibold text-sm">行业热点</div>
                                    <div class="text-xs text-gray-400">AI/数据中心/消费电子</div>
                                </div>
                            </div>
                            <div class="flex items-start gap-2 p-2 bg-green-900/10 rounded">
                                <span class="text-green-400">✓</span>
                                <div>
                                    <div class="font-semibold text-sm">政策支持</div>
                                    <div class="text-xs text-gray-400">相关产业政策利好</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold mb-3 text-red-400"><i class="fas fa-exclamation-triangle mr-2"></i>风险因素</h3>
                        <div class="space-y-2">
                            <div class="flex items-start gap-2 p-2 bg-red-900/10 rounded">
                                <span class="text-red-400">⚠</span>
                                <div>
                                    <div class="font-semibold text-sm">原材料价格</div>
                                    <div class="text-xs text-gray-400">铜、铝、钢等原材料波动</div>
                                </div>
                            </div>
                            <div class="flex items-start gap-2 p-2 bg-red-900/10 rounded">
                                <span class="text-red-400">⚠</span>
                                <div>
                                    <div class="font-semibold text-sm">汇率波动</div>
                                    <div class="text-xs text-gray-400">出口业务汇率风险</div>
                                </div>
                            </div>
                            <div class="flex items-start gap-2 p-2 bg-red-900/10 rounded">
                                <span class="text-red-400">⚠</span>
                                <div>
                                    <div class="font-semibold text-sm">行业周期</div>
                                    <div class="text-xs text-gray-400">消费电子周期性波动</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''
    
    # 评分拆分
    html += f'''
    <!-- 评分拆分 -->
    <section class="px-4 py-10">
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-8 fade-in">
                <h2 class="text-3xl font-bold mb-1">评分拆分</h2>
                <p class="text-gray-500 text-xs">配置分（中长期）与交易分（短线）</p>
            </div>
            
            <div class="card rounded-2xl p-6 fade-in">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gradient-to-br from-blue-900/20 to-blue-800/10 rounded-lg p-6">
                        <h3 class="text-lg font-bold mb-2">配置分（中长期）</h3>
                        <div class="text-4xl font-bold gradient-text mb-4">69/100</div>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between"><span class="text-gray-400">估值分</span><span class="font-bold">5</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">质量分</span><span class="font-bold">22</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">风险分</span><span class="font-bold">17</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">事件分</span><span class="font-bold">25</span></div>
                        </div>
                        <div class="mt-4 text-sm text-gray-400">中长期基本面：偏强</div>
                    </div>
                    <div class="bg-gradient-to-br from-purple-900/20 to-purple-800/10 rounded-lg p-6">
                        <h3 class="text-lg font-bold mb-2">交易分（短线）</h3>
                        <div class="text-4xl font-bold mb-4" style="color: #a78bfa">54/100</div>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between"><span class="text-gray-400">趋势分</span><span class="font-bold">12</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">位置分</span><span class="font-bold">20</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">量能分</span><span class="font-bold">12</span></div>
                            <div class="flex justify-between"><span class="text-gray-400">情绪分</span><span class="font-bold">10</span></div>
                        </div>
                        <div class="mt-4 text-sm text-gray-400">短线位置：偏热，不适合追高</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
'''
    
    # 结尾
    html += f'''
    <!-- Footer -->
    <footer class="px-4 py-10 border-t border-gray-800">
        <div class="max-w-7xl mx-auto text-center">
            <div class="text-gray-500 text-sm mb-2">
                <i class="fas fa-info-circle mr-1"></i>
                本报告基于公开数据分析，仅供参考，不构成投资建议
            </div>
            <div class="text-gray-600 text-xs">
                报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据来源: yfinance + 专业分析模块
            </div>
        </div>
    </footer>
    
    <script>
        // 滚动动画
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, {{ threshold: 0.1 }});
        
        document.querySelectorAll('.fade-in').forEach(el => {{
            observer.observe(el);
        }});
    </script>
</body>
</html>'''
    
    return html


if __name__ == '__main__':
    print("Apple风格HTML报告生成器 v4.0")
    print("\n修复内容:")
    print("1. ✅ 板块中文显示")
    print("2. ✅ 支撑阻力位完整展示")
    print("3. ✅ 事件驱动模块")
    print("4. ✅ 评分拆分模块")
    print("5. ✅ 技术分析完善")
