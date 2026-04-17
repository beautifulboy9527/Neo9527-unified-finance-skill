#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资尽调 HTML 报告生成器
- 参考 crypto-skill Apple 风格
- 差异化配色 (深蓝/金色主题)
- 数据可视化
"""

import sys
import os
from datetime import datetime
from typing import Dict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def generate_stock_html(results: Dict) -> str:
    """
    生成股票投资尽调 HTML 报告
    
    Args:
        results: 分析结果字典
        
    Returns:
        HTML字符串
    """
    symbol = results['symbol']
    timestamp = results['timestamp']
    rating = results['rating']
    phases = results['phases']
    
    # 颜色主题 (深蓝/金色，区别于crypto的橙色)
    colors = {
        'primary': '#1e3a5f',      # 深蓝
        'secondary': '#c9a227',    # 金色
        'success': '#22c55e',
        'warning': '#eab308',
        'danger': '#ef4444',
        'bg_dark': '#0a1628',
        'bg_card': '#162236',
    }
    
    # Phase 1: 公司事实底座
    p1 = phases.get(1, {}).get('data', {})
    company_info = p1.get('公司基本信息', {})
    
    # Phase 4: 财务质量
    p4 = phases.get(4, {}).get('data', {})
    key_metrics = p4.get('关键指标', {})
    cashflow = p4.get('现金流验证', {})
    
    # Phase 7: 估值与护城河
    p7 = phases.get(7, {}).get('data', {})
    valuation = p7.get('估值指标', {})
    moat = p7.get('护城河评分', {})
    
    # Phase 6: 市场分歧
    p6 = phases.get(6, {}).get('data', {})
    analyst = p6.get('分析师观点', {})
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 投资尽调报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #0a1628 0%, #162236 50%, #1e3a5f 100%);
            min-height: 100vh;
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, #c9a227 0%, #f0d060 50%, #c9a227 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .card {{
            background: rgba(22, 34, 54, 0.9);
            border: 1px solid rgba(201, 162, 39, 0.2);
            backdrop-filter: blur(10px);
        }}
        .metric-card {{
            background: linear-gradient(135deg, #1e3a5f 0%, #162236 100%);
            border: 1px solid rgba(201, 162, 39, 0.3);
        }}
        .progress-bar {{
            background: linear-gradient(90deg, #c9a227 0%, #f0d060 100%);
        }}
    </style>
</head>
<body class="text-white p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        
        <!-- Header -->
        <div class="text-center mb-8">
            <div class="inline-flex items-center gap-3 mb-4">
                <iconify-icon icon="mdi:chart-line" class="text-4xl text-yellow-500"></iconify-icon>
                <h1 class="text-4xl md:text-5xl font-bold gold-gradient">{symbol}</h1>
            </div>
            <p class="text-gray-400">{company_info.get('公司名称', '')} | {company_info.get('所属行业', '')}</p>
            <p class="text-gray-500 text-sm mt-2">报告时间: {timestamp}</p>
        </div>
        
        <!-- 综合评级卡片 -->
        <div class="card rounded-2xl p-6 mb-8 text-center">
            <div class="text-5xl mb-4">{rating['rating']}</div>
            <div class="text-xl text-gray-300 mb-2">综合评分: {rating['score']:.1f}/{rating['max_score']}</div>
            <div class="text-lg text-yellow-400">{rating['recommendation']}</div>
            <div class="text-sm text-gray-500 mt-2">投资风格: {results.get('style', 'value')} | 分析深度: standard</div>
            
            <!-- 评分进度条 -->
            <div class="mt-4 max-w-md mx-auto">
                <div class="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div class="h-full progress-bar rounded-full" style="width: {rating['score']/rating['max_score']*100}%"></div>
                </div>
            </div>
        </div>
        
        <!-- 关键指标网格 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="metric-card rounded-xl p-4 text-center">
                <div class="text-gray-400 text-sm mb-1">ROE</div>
                <div class="text-2xl font-bold text-yellow-400">{key_metrics.get('ROE', 'N/A')}</div>
            </div>
            <div class="metric-card rounded-xl p-4 text-center">
                <div class="text-gray-400 text-sm mb-1">毛利率</div>
                <div class="text-2xl font-bold text-yellow-400">{key_metrics.get('毛利率', 'N/A')}</div>
            </div>
            <div class="metric-card rounded-xl p-4 text-center">
                <div class="text-gray-400 text-sm mb-1">净利率</div>
                <div class="text-2xl font-bold text-yellow-400">{key_metrics.get('净利率', 'N/A')}</div>
            </div>
            <div class="metric-card rounded-xl p-4 text-center">
                <div class="text-gray-400 text-sm mb-1">负债率</div>
                <div class="text-2xl font-bold text-yellow-400">{key_metrics.get('负债率', 'N/A')}</div>
            </div>
        </div>
        
        <!-- Phase 4: 财务质量 -->
        <div class="card rounded-2xl p-6 mb-6">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
                <iconify-icon icon="mdi:finance" class="text-yellow-500"></iconify-icon>
                Phase 4: 财务质量分析
            </h2>
            
            <div class="grid md:grid-cols-2 gap-6">
                <!-- 现金流验证 -->
                <div class="bg-gray-800/50 rounded-xl p-4">
                    <h3 class="font-semibold mb-3 text-yellow-400">现金流验证</h3>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-gray-400">经营现金流</span>
                            <span class="font-medium">{cashflow.get('经营现金流', 'N/A')}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">自由现金流</span>
                            <span class="font-medium">{cashflow.get('自由现金流', 'N/A')}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">OCF/净利润</span>
                            <span class="font-medium">{cashflow.get('OCF/净利润', 'N/A')}</span>
                        </div>
                        <div class="mt-3 p-2 bg-gray-700/50 rounded text-center">
                            <span class="text-lg">{cashflow.get('判断', 'N/A')}</span>
                            <p class="text-sm text-gray-400 mt-1">{cashflow.get('说明', '')}</p>
                        </div>
                    </div>
                </div>
                
                <!-- 异常排查 -->
                <div class="bg-gray-800/50 rounded-xl p-4">
                    <h3 class="font-semibold mb-3 text-yellow-400">异常排查</h3>
                    <ul class="space-y-2">
                        {''.join(f'<li class="flex items-start gap-2"><span>{w}</span></li>' for w in p4.get('异常排查', []))}
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Phase 7: 估值与护城河 -->
        <div class="card rounded-2xl p-6 mb-6">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
                <iconify-icon icon="mdi:shield-check" class="text-yellow-500"></iconify-icon>
                Phase 7: 估值与护城河
            </h2>
            
            <div class="grid md:grid-cols-3 gap-4 mb-4">
                <div class="bg-gray-800/50 rounded-xl p-4 text-center">
                    <div class="text-gray-400 text-sm">P/E</div>
                    <div class="text-2xl font-bold">{valuation.get('P/E (TTM)', 'N/A')}</div>
                </div>
                <div class="bg-gray-800/50 rounded-xl p-4 text-center">
                    <div class="text-gray-400 text-sm">P/B</div>
                    <div class="text-2xl font-bold">{valuation.get('P/B', 'N/A')}</div>
                </div>
                <div class="bg-gray-800/50 rounded-xl p-4 text-center">
                    <div class="text-gray-400 text-sm">EV/EBITDA</div>
                    <div class="text-2xl font-bold">{valuation.get('EV/EBITDA', 'N/A')}</div>
                </div>
            </div>
            
            <!-- 护城河评分 -->
            <div class="bg-gray-800/50 rounded-xl p-4">
                <h3 class="font-semibold mb-3">护城河评分: {moat.get('总分', 'N/A')}</h3>
                <div class="flex gap-1 mb-2">
                    {''.join([f'<div class="flex-1 h-2 rounded {"bg-yellow-500" if i < int(moat.get("总分", "0/5").split("/")[0]) else "bg-gray-600"}"></div>' for i in range(5)])}
                </div>
                <p class="text-sm text-gray-400">{moat.get('评级', '')}</p>
            </div>
        </div>
        
        <!-- Phase 6: 市场分歧 -->
        <div class="card rounded-2xl p-6 mb-6">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
                <iconify-icon icon="mdi:scale-balance" class="text-yellow-500"></iconify-icon>
                Phase 6: 市场分歧分析
            </h2>
            
            <div class="grid md:grid-cols-2 gap-6">
                <!-- 多方逻辑 -->
                <div class="bg-green-900/20 border border-green-500/30 rounded-xl p-4">
                    <h3 class="font-semibold mb-2 text-green-400">多方逻辑</h3>
                    <ul class="space-y-1">
                        {''.join(f'<li class="text-sm">✅ {p}</li>' for p in p6.get('多方逻辑', []))}
                    </ul>
                </div>
                
                <!-- 空方逻辑 -->
                <div class="bg-red-900/20 border border-red-500/30 rounded-xl p-4">
                    <h3 class="font-semibold mb-2 text-red-400">空方逻辑</h3>
                    <ul class="space-y-1">
                        {''.join(f'<li class="text-sm">⚠️ {p}</li>' for p in p6.get('空方逻辑', []))}
                    </ul>
                </div>
            </div>
            
            <!-- 分析师观点 -->
            <div class="mt-4 bg-gray-800/50 rounded-xl p-4">
                <h3 class="font-semibold mb-3 text-yellow-400">分析师观点</h3>
                {generate_analyst_section(analyst)}
            </div>
        </div>
        
        <!-- Phase 1: 公司事实底座 -->
        {generate_phase1_html(phases.get(1, {}))}
        
        <!-- Phase 2: 行业周期 -->
        {generate_phase2_html(phases.get(2, {}))}
        
        <!-- Phase 3: 业务拆解 -->
        {generate_phase3_html(phases.get(3, {}))}
        
        <!-- Phase 5: 股权治理 -->
        {generate_phase5_html(phases.get(5, {}))}
        
        <!-- 监控清单 -->
        {generate_monitoring_html(results.get('monitoring_checklist', ''))}
        
        <!-- 数据来源 -->
        <div class="card rounded-2xl p-4 mb-6">
            <h3 class="font-semibold mb-2 text-yellow-400 text-sm">数据来源</h3>
            <p class="text-xs text-gray-500">
                本报告数据来源于 yfinance 财务报表。分析框架基于8阶段投资尽调体系。
                所有数据仅供参考，请以官方财报为准。
            </p>
        </div>
        
        <!-- 免责声明 -->
        <div class="text-center text-gray-500 text-xs py-4">
            <p>⚠️ 本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
            <p class="mt-1">by Neo9527 Finance Skill v5.0 | {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        
    </div>
</body>
</html>'''
    
    return html


def generate_analyst_section(analyst: Dict) -> str:
    """生成分析师观点部分，处理空数据"""
    # 检查是否有有效数据
    has_data = any(
        v and v != 'N/A' 
        for k, v in analyst.items() 
        if k in ['评级', '目标价', '当前价']
    )
    
    if not has_data:
        return '''
        <div class="text-center text-gray-400 py-4">
            <p class="text-sm">暂无分析师数据</p>
            <p class="text-xs mt-1">分析师评级和目标价数据需订阅专业数据源</p>
        </div>
        '''
    
    return f'''
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <div>
            <div class="text-gray-400 text-sm">评级</div>
            <div class="font-bold text-lg">{analyst.get('评级', 'N/A')}</div>
        </div>
        <div>
            <div class="text-gray-400 text-sm">目标价</div>
            <div class="font-bold text-lg">{analyst.get('目标价', 'N/A')}</div>
        </div>
        <div>
            <div class="text-gray-400 text-sm">当前价</div>
            <div class="font-bold text-lg">{analyst.get('当前价', 'N/A')}</div>
        </div>
        <div>
            <div class="text-gray-400 text-sm">潜在空间</div>
            <div class="font-bold text-lg text-yellow-400">{analyst.get('潜在空间', 'N/A')}</div>
        </div>
    </div>
    '''


def generate_phase1_html(phase1: Dict) -> str:
    """生成 Phase 1 HTML - 公司事实底座"""
    if not phase1 or 'data' not in phase1:
        return ''
    
    data = phase1['data']
    company_info = data.get('公司基本信息', {})
    main_business = data.get('主营业务', {})
    revenue = data.get('收入构成', {})
    
    return f'''
<div class="card rounded-2xl p-6 mb-6">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
        <iconify-icon icon="mdi:office-building" class="text-yellow-500"></iconify-icon>
        第一阶段：公司事实底座
    </h2>
    
    <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-gray-800/50 rounded-xl p-4">
            <h3 class="font-semibold mb-3 text-yellow-400">基本信息</h3>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                    <span class="text-gray-400">公司名称</span>
                    <span>{company_info.get('公司名称', 'N/A')}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">所属行业</span>
                    <span>{company_info.get('所属行业', 'N/A')}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">所属板块</span>
                    <span>{company_info.get('所属板块', 'N/A')}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">员工数量</span>
                    <span>{company_info.get('员工数量', 'N/A')}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-400">总部地址</span>
                    <span>{company_info.get('总部地址', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <div class="bg-gray-800/50 rounded-xl p-4">
            <h3 class="font-semibold mb-3 text-yellow-400">主营业务</h3>
            <p class="text-sm text-gray-300 leading-relaxed">
                {main_business.get('业务描述', '主营业务描述暂无')[:300]}{'...' if len(main_business.get('业务描述', '')) > 300 else ''}
            </p>
        </div>
    </div>
    
    <div class="mt-4 bg-gray-800/50 rounded-xl p-4">
        <h3 class="font-semibold mb-3 text-yellow-400">收入构成</h3>
        <div class="grid md:grid-cols-3 gap-4 text-center">
            <div>
                <div class="text-gray-400 text-sm">主营业务</div>
                <div class="text-lg">{revenue.get('主营业务', 'N/A')}</div>
            </div>
            <div>
                <div class="text-gray-400 text-sm">其他业务</div>
                <div class="text-lg">{revenue.get('其他业务', 'N/A')}</div>
            </div>
            <div>
                <div class="text-gray-400 text-sm">说明</div>
                <div class="text-sm">{revenue.get('说明', 'N/A')}</div>
            </div>
        </div>
    </div>
</div>'''


def generate_phase2_html(phase2: Dict) -> str:
    """生成 Phase 2 HTML"""
    if not phase2 or 'data' not in phase2:
        return ''
    
    data = phase2['data']
    industry = data.get('行业概况', {})
    
    return f'''
<div class="card rounded-2xl p-6 mb-6">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
        <iconify-icon icon="mdi:trending-up" class="text-yellow-500"></iconify-icon>
        Phase 2: 行业周期分析
    </h2>
    <div class="grid md:grid-cols-3 gap-4">
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">周期阶段</div>
            <div class="text-xl font-bold text-yellow-400">{industry.get('周期阶段', 'N/A')}</div>
        </div>
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">行业增速</div>
            <div class="text-xl font-bold">{industry.get('行业增速', 'N/A')}</div>
        </div>
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">市场地位</div>
            <div class="text-xl font-bold">{data.get('竞争态势', {}).get('市场地位', 'N/A')}</div>
        </div>
    </div>
</div>'''


def generate_phase3_html(phase3: Dict) -> str:
    """生成 Phase 3 HTML"""
    if not phase3 or 'data' not in phase3:
        return ''
    
    data = phase3['data']
    profit_model = data.get('赚钱机制', {})
    
    return f'''
<div class="card rounded-2xl p-6 mb-6">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
        <iconify-icon icon="mdi:bank" class="text-yellow-500"></iconify-icon>
        Phase 3: 业务拆解
    </h2>
    <div class="grid md:grid-cols-2 gap-4">
        <div class="bg-gray-800/50 rounded-xl p-4">
            <h3 class="font-semibold mb-2 text-yellow-400">盈利模式</h3>
            <p class="text-sm">{profit_model.get('盈利模式', 'N/A')}</p>
            <div class="mt-2 text-sm">
                <span class="text-gray-400">毛利率: </span>{profit_model.get('毛利率水平', 'N/A')}
            </div>
        </div>
        <div class="bg-gray-800/50 rounded-xl p-4">
            <h3 class="font-semibold mb-2 text-yellow-400">定价权</h3>
            <p class="text-sm">{data.get('定价权分析', {}).get('定价权', 'N/A')}</p>
            <p class="text-xs text-gray-400 mt-1">{data.get('定价权分析', {}).get('依据', '')}</p>
        </div>
    </div>
</div>'''


def generate_phase5_html(phase5: Dict) -> str:
    """生成 Phase 5 HTML"""
    if not phase5 or 'data' not in phase5:
        return ''
    
    data = phase5['data']
    equity = data.get('股权结构', {})
    
    return f'''
<div class="card rounded-2xl p-6 mb-6">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
        <iconify-icon icon="mdi:account-group" class="text-yellow-500"></iconify-icon>
        Phase 5: 股权治理分析
    </h2>
    <div class="grid md:grid-cols-3 gap-4">
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">机构持股</div>
            <div class="text-xl font-bold">{equity.get('机构持股', 'N/A')}</div>
        </div>
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">内部人持股</div>
            <div class="text-xl font-bold">{equity.get('内部人持股', 'N/A')}</div>
        </div>
        <div class="bg-gray-800/50 rounded-xl p-4 text-center">
            <div class="text-gray-400 text-sm">CEO</div>
            <div class="text-lg font-bold">{data.get('管理层', {}).get('CEO', 'N/A')}</div>
        </div>
    </div>
</div>'''


def generate_monitoring_html(checklist: str) -> str:
    """生成监控清单 HTML"""
    if not checklist:
        return ''
    
    return f'''
<div class="card rounded-2xl p-6 mb-6">
    <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
        <iconify-icon icon="mdi:clipboard-check" class="text-yellow-500"></iconify-icon>
        风险监控清单
    </h2>
    <div class="bg-gray-800/50 rounded-xl p-4">
        <pre class="text-sm whitespace-pre-wrap">{checklist}</pre>
    </div>
</div>'''


# 测试
if __name__ == '__main__':
    # 模拟测试数据
    test_results = {
        'symbol': 'AAPL',
        'timestamp': '2026-04-17T18:30:00',
        'rating': {'rating': '🟢🟢🟢', 'score': 4.2, 'max_score': 5, 'recommendation': '基本面强劲'},
        'phases': {
            1: {'data': {'公司基本信息': {'公司名称': 'Apple Inc.', '所属行业': 'Consumer Electronics', '所属板块': 'Technology'}}},
            4: {'data': {'关键指标': {'ROE': '152.1%', '毛利率': '47.3%', '净利率': '27.0%', '负债率': '1.34'}}},
            7: {'data': {'估值指标': {'P/E (TTM)': '28.5', 'P/B': '45.2', 'EV/EBITDA': '22.1'}, '护城河评分': {'总分': '4/5', '评级': '强护城河'}}},
        }
    }
    
    html = generate_stock_html(test_results)
    print(html[:500])
