#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融分析专业版演示 - Professional Finance Analysis Demo
集成所有专业模块的完整演示

包含:
- 专业技术指标分析
- 专业绩效评估
- 专业风险管理
- 专业估值模型
- 综合分析报告
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from technical_indicators_pro import TechnicalIndicators
from performance_metrics import PerformanceMetrics
from risk_management_pro import RiskManager
from valuation_pro import ValuationModels


def run_comprehensive_analysis(
    symbol: str,
    days: int = 365
) -> Dict:
    """
    运行综合分析
    
    Args:
        symbol: 股票代码
        days: 历史天数
        
    Returns:
        综合分析报告
    """
    print("=" * 80)
    print(f"📊 {symbol} 专业金融分析报告")
    print("=" * 80)
    
    # 1. 获取数据
    print(f"\n📥 获取数据...")
    
    # A股代码转换
    if symbol.isdigit():
        if symbol.startswith('6'):
            yf_symbol = f"{symbol}.SS"
        elif symbol.startswith(('0', '3')):
            yf_symbol = f"{symbol}.SZ"
        else:
            yf_symbol = symbol
    else:
        yf_symbol = symbol
    
    ticker = yf.Ticker(yf_symbol)
    df = ticker.history(period=f"{days}d")
    
    if df.empty:
        print(f"❌ 无法获取 {symbol} 数据")
        return {}
    
    print(f"✅ 获取 {len(df)} 天数据")
    
    # 2. 专业技术指标分析
    print(f"\n📊 1. 专业技术指标分析")
    print("-" * 80)
    
    ti = TechnicalIndicators(df)
    indicators = ti.all_indicators()
    
    # 趋势判断
    close = df['Close'].iloc[-1]
    sma_20 = indicators.get('SMA_20', np.array([0]))[-1] if isinstance(indicators.get('SMA_20'), np.ndarray) else 0
    sma_60 = indicators.get('SMA_60', np.array([0]))[-1] if isinstance(indicators.get('SMA_60'), np.ndarray) else 0
    
    if sma_20 > 0 and sma_60 > 0:
        if close > sma_20 > sma_60:
            trend = "强势多头 ↑"
        elif close > sma_20:
            trend = "偏多 →"
        elif close < sma_20 < sma_60:
            trend = "强势空头 ↓"
        elif close < sma_20:
            trend = "偏空 ←"
        else:
            trend = "震荡 ↔"
    else:
        trend = "数据不足"
    
    print(f"  当前价格: ${close:.2f}")
    print(f"  SMA(20): ${sma_20:.2f}")
    print(f"  SMA(60): ${sma_60:.2f}")
    print(f"  趋势判断: {trend}")
    
    # RSI
    rsi = indicators.get('RSI_14', np.array([50]))[-1] if isinstance(indicators.get('RSI_14'), np.ndarray) else 50
    print(f"\n  RSI(14): {rsi:.1f}")
    if rsi > 70:
        print(f"    ⚠️ 超买区域")
    elif rsi < 30:
        print(f"    ⚠️ 超卖区域")
    else:
        print(f"    ✓ 正常区域")
    
    # MACD
    macd = indicators.get('MACD', np.array([0]))[-1] if isinstance(indicators.get('MACD'), np.ndarray) else 0
    macd_signal = indicators.get('MACD_Signal', np.array([0]))[-1] if isinstance(indicators.get('MACD_Signal'), np.ndarray) else 0
    
    print(f"\n  MACD: {macd:.2f}")
    print(f"  Signal: {macd_signal:.2f}")
    if macd > macd_signal:
        print(f"    ✓ 金叉 (看涨)")
    else:
        print(f"    ✗ 死叉 (看跌)")
    
    # 布林带
    bb_upper = indicators.get('BB_Upper', np.array([0]))[-1] if isinstance(indicators.get('BB_Upper'), np.ndarray) else 0
    bb_lower = indicators.get('BB_Lower', np.array([0]))[-1] if isinstance(indicators.get('BB_Lower'), np.ndarray) else 0
    bb_width = indicators.get('BB_Width', np.array([0]))[-1] if isinstance(indicators.get('BB_Width'), np.ndarray) else 0
    
    print(f"\n  布林带上轨: ${bb_upper:.2f}")
    print(f"  布林带下轨: ${bb_lower:.2f}")
    print(f"  带宽: {bb_width:.1f}%")
    
    # 3. 绩效评估
    print(f"\n📈 2. 专业绩效评估")
    print("-" * 80)
    
    returns = df['Close'].pct_change().dropna()
    benchmark = pd.Series(np.random.normal(0.0003, 0.012, len(returns)))  # 模拟基准
    
    pm = PerformanceMetrics(returns, benchmark_returns=benchmark)
    
    total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1)
    annual_return = pm.annual_return()
    annual_vol = pm.annual_volatility()
    sharpe = pm.sharpe_ratio()
    sortino = pm.sortino_ratio()
    max_dd = pm.max_drawdown()
    var_95 = pm.var(0.95)
    cvar_95 = pm.cvar(0.95)
    
    print(f"  总收益率: {total_return*100:.1f}%")
    print(f"  年化收益: {annual_return*100:.1f}%")
    print(f"  年化波动: {annual_vol*100:.1f}%")
    print(f"\n  夏普比率: {sharpe:.2f}")
    print(f"  索提诺比率: {sortino:.2f}")
    print(f"  最大回撤: {max_dd*100:.1f}%")
    print(f"\n  VaR(95%): {var_95*100:.2f}%")
    print(f"  CVaR(95%): {cvar_95*100:.2f}%")
    
    # 评级
    report = pm.full_report()
    rating = report['rating']
    print(f"\n  ⭐ 综合评级: {rating['grade']} ({rating['score']}/100)")
    
    # 4. 风险管理
    print(f"\n⚠️ 3. 专业风险管理")
    print("-" * 80)
    
    # 假设持仓
    positions = {
        '股票': 100000
    }
    
    # 单资产风险分析
    print(f"  VaR分析 (置信水平 95%):")
    print(f"    历史模拟法: {var_95*100:.2f}%")
    print(f"    参数法: {pm.var(0.95, 'parametric')*100:.2f}%")
    
    print(f"\n  CVaR分析 (预期短缺):")
    print(f"    历史模拟法: {cvar_95*100:.2f}%")
    
    print(f"\n  风险指标:")
    print(f"    日波动率: {annual_vol/np.sqrt(252)*100:.2f}%")
    print(f"    年化波动率: {annual_vol*100:.1f}%")
    print(f"    最大回撤: {max_dd*100:.1f}%")
    
    # 压力测试
    print(f"\n  压力测试:")
    stress_scenarios = {
        '温和下跌': {'股票': -0.10},
        '中度下跌': {'股票': -0.20},
        '严重下跌': {'股票': -0.35},
        '极端下跌': {'股票': -0.50}
    }
    
    rm = RiskManager(positions=positions)
    stress_results = rm.stress_test(positions, stress_scenarios)
    
    for scenario, result in stress_results.items():
        print(f"    {scenario}: {result['loss_pct']*100:+.1f}% (${result['loss']:,.0f})")
    
    # 5. 估值分析
    print(f"\n💰 4. 专业估值分析")
    print("-" * 80)
    
    try:
        vm = ValuationModels(yf_symbol)
        
        # 获取基本面数据
        info = ticker.info
        current_price = info.get('currentPrice', close)
        eps = info.get('trailingEps', 0)
        book_value = info.get('bookValue', 0)
        beta = info.get('beta', 1.0)
        
        print(f"  当前价格: ${current_price:.2f}")
        print(f"  EPS: ${eps:.2f}" if eps else "  EPS: N/A")
        print(f"  Book Value: ${book_value:.2f}" if book_value else "  Book Value: N/A")
        print(f"  Beta: {beta:.2f}")
        
        # PE估值
        if eps and eps > 0:
            pe = current_price / eps
            print(f"\n  PE估值:")
            print(f"    当前PE: {pe:.1f}")
            print(f"    行业PE(假设): 20")
            pe_fair = eps * 20
            print(f"    公允价值: ${pe_fair:.2f}")
            print(f"    涨幅空间: {(pe_fair/current_price - 1)*100:+.1f}%")
        
        # WACC计算
        wacc = vm.calculate_wacc(beta)
        print(f"\n  WACC: {wacc*100:.1f}%")
        
        # 简单DCF (假设FCF = 净利润的80%)
        net_income = info.get('netIncomeToCommon', 0)
        if net_income:
            fcf = net_income * 0.8
            dcf_result = vm.dcf_two_stage(
                fcf,
                growth_rate_high=0.15,
                growth_rate_stable=0.03,
                wacc=wacc
            )
            
            shares = info.get('sharesOutstanding', 1)
            dcf_value = dcf_result['enterprise_value'] / shares
            
            print(f"\n  DCF估值 (两阶段):")
            print(f"    企业价值: ${dcf_result['enterprise_value']/1e9:.1f}B")
            print(f"    每股价值: ${dcf_value:.2f}")
            print(f"    涨幅空间: {(dcf_value/current_price - 1)*100:+.1f}%")
        
    except Exception as e:
        print(f"  ⚠️ 估值分析失败: {e}")
    
    # 6. 综合评分
    print(f"\n⭐ 5. 综合评分")
    print("=" * 80)
    
    scores = {}
    
    # 趋势评分 (20分)
    if "多头" in trend or "偏多" in trend:
        scores['趋势'] = 18
    elif "空头" in trend or "偏空" in trend:
        scores['趋势'] = 8
    else:
        scores['趋势'] = 12
    
    # 动量评分 (20分)
    if 40 <= rsi <= 60:
        scores['动量'] = 16
    elif 30 <= rsi <= 70:
        scores['动量'] = 12
    else:
        scores['动量'] = 8
    
    # 风险评分 (30分)
    if max_dd > -0.10:
        scores['风险'] = 28
    elif max_dd > -0.20:
        scores['风险'] = 22
    elif max_dd > -0.30:
        scores['风险'] = 16
    else:
        scores['风险'] = 10
    
    # 收益评分 (30分)
    if annual_return > 0.20:
        scores['收益'] = 28
    elif annual_return > 0.10:
        scores['收益'] = 22
    elif annual_return > 0:
        scores['收益'] = 16
    else:
        scores['收益'] = 8
    
    total_score = sum(scores.values())
    
    print(f"  趋势评分: {scores['趋势']}/20")
    print(f"  动量评分: {scores['动量']}/20")
    print(f"  风险评分: {scores['风险']}/30")
    print(f"  收益评分: {scores['收益']}/30")
    print(f"\n  总分: {total_score}/100")
    
    if total_score >= 80:
        grade = 'A'
        recommendation = '强烈买入'
    elif total_score >= 65:
        grade = 'B'
        recommendation = '买入'
    elif total_score >= 50:
        grade = 'C'
        recommendation = '持有'
    elif total_score >= 35:
        grade = 'D'
        recommendation = '减仓'
    else:
        grade = 'E'
        recommendation = '卖出'
    
    print(f"  评级: {grade}")
    print(f"  建议: {recommendation}")
    
    return {
        'symbol': symbol,
        'price': close,
        'trend': trend,
        'rsi': rsi,
        'total_return': total_return,
        'annual_return': annual_return,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'var_95': var_95,
        'score': total_score,
        'grade': grade,
        'recommendation': recommendation
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='专业金融分析')
    parser.add_argument('symbol', nargs='?', default='AAPL', help='股票代码')
    parser.add_argument('--days', type=int, default=365, help='历史天数')
    
    args = parser.parse_args()
    
    result = run_comprehensive_analysis(args.symbol, args.days)
