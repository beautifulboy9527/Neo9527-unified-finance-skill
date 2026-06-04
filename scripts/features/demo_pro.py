#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融分析专业版演示 - 使用模拟数据
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from technical_indicators_pro import TechnicalIndicators
from performance_metrics import PerformanceMetrics
from risk_management_pro import RiskManager
from valuation_pro import ValuationModels


def generate_mock_data(days: int = 365) -> pd.DataFrame:
    """生成模拟OHLCV数据"""
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 模拟价格走势 (随机游走 + 趋势)
    returns = np.random.normal(0.001, 0.02, days)
    price = 100 * np.exp(np.cumsum(returns))
    
    # OHLCV
    df = pd.DataFrame({
        'Open': price * (1 + np.random.uniform(-0.01, 0.01, days)),
        'High': price * (1 + np.random.uniform(0, 0.02, days)),
        'Low': price * (1 + np.random.uniform(-0.02, 0, days)),
        'Close': price,
        'Volume': np.random.uniform(1e6, 1e7, days)
    }, index=dates)
    
    return df


print("=" * 80)
print("📊 专业金融分析模块演示")
print("=" * 80)

# 生成模拟数据
print(f"\n📥 生成模拟数据...")
df = generate_mock_data(365)
print(f"✅ 生成 {len(df)} 天数据")

# ========================================
# 1. 专业技术指标分析
# ========================================
print(f"\n📊 1. 专业技术指标分析")
print("-" * 80)

ti = TechnicalIndicators(df)
indicators = ti.all_indicators()

close = df['Close'].iloc[-1]
sma_20 = indicators.get('SMA_20', np.array([0]))
sma_20 = sma_20[-1] if hasattr(sma_20, '__getitem__') and len(sma_20) > 0 else 0
sma_60 = indicators.get('SMA_60', np.array([0]))
sma_60 = sma_60[-1] if hasattr(sma_60, '__getitem__') and len(sma_60) > 0 else 0
rsi = indicators.get('RSI_14', np.array([50]))
rsi = rsi[-1] if hasattr(rsi, '__getitem__') and len(rsi) > 0 else 50
macd = indicators.get('MACD', np.array([0]))
macd = macd[-1] if hasattr(macd, '__getitem__') and len(macd) > 0 else 0
macd_signal = indicators.get('MACD_Signal', np.array([0]))
macd_signal = macd_signal[-1] if hasattr(macd_signal, '__getitem__') and len(macd_signal) > 0 else 0
bb_upper = indicators.get('BB_Upper', np.array([0]))
bb_upper = bb_upper.iloc[-1] if hasattr(bb_upper, 'iloc') else (bb_upper[-1] if len(bb_upper) > 0 else 0)
bb_lower = indicators.get('BB_Lower', np.array([0]))
bb_lower = bb_lower.iloc[-1] if hasattr(bb_lower, 'iloc') else (bb_lower[-1] if len(bb_lower) > 0 else 0)

print(f"  当前价格: ${close:.2f}")
print(f"  SMA(20): ${sma_20:.2f}")
print(f"  SMA(60): ${sma_60:.2f}")
print(f"  RSI(14): {rsi:.1f}")
print(f"  MACD: {macd:.2f} (Signal: {macd_signal:.2f})")
print(f"  布林带: ${bb_lower:.2f} - ${bb_upper:.2f}")

# ========================================
# 2. 专业绩效评估
# ========================================
print(f"\n📈 2. 专业绩效评估")
print("-" * 80)

returns = df['Close'].pct_change().dropna()
benchmark = pd.Series(np.random.normal(0.0003, 0.012, len(returns)))

pm = PerformanceMetrics(returns, benchmark_returns=benchmark)
report = pm.full_report()

print(f"  总收益率: {report['total_return']*100:.1f}%")
print(f"  年化收益: {report['annual_return']*100:.1f}%")
print(f"  年化波动: {report['annual_volatility']*100:.1f}%")
print(f"\n  夏普比率: {report['sharpe_ratio']:.2f}")
print(f"  索提诺比率: {report['sortino_ratio']:.2f}")
print(f"  卡尔玛比率: {report['calmar_ratio']:.2f}")
print(f"\n  最大回撤: {report['max_drawdown']*100:.1f}%")
print(f"  VaR(95%): {report['var_95']*100:.2f}%")
print(f"  CVaR(95%): {report['cvar_95']*100:.2f}%")

rating = report['rating']
print(f"\n  ⭐ 综合评级: {rating['grade']} ({rating['score']}/100)")
print(f"     {rating['description']}")

# ========================================
# 3. 专业风险管理
# ========================================
print(f"\n⚠️ 3. 专业风险管理")
print("-" * 80)

positions = {'股票': 500000, '债券': 300000, '商品': 200000}
rm = RiskManager(positions=positions)

# VaR分析
var_90 = rm.var_historical(returns, 0.90)
var_95 = rm.var_historical(returns, 0.95)
var_99 = rm.var_historical(returns, 0.99)

print(f"  VaR分析:")
print(f"    90%置信: {var_90*100:.2f}%")
print(f"    95%置信: {var_95*100:.2f}%")
print(f"    99%置信: {var_99*100:.2f}%")

# 压力测试
stress_scenarios = {
    '温和下跌': {'股票': -0.10, '债券': -0.02, '商品': -0.05},
    '中度下跌': {'股票': -0.20, '债券': -0.05, '商品': -0.10},
    '严重下跌': {'股票': -0.35, '债券': -0.10, '商品': -0.20},
    '极端下跌': {'股票': -0.50, '债券': -0.15, '商品': -0.30}
}

print(f"\n  压力测试 (组合价值: ¥1,000,000):")
stress_results = rm.stress_test(positions, stress_scenarios)
for scenario, result in stress_results.items():
    print(f"    {scenario}: {result['loss_pct']*100:+.1f}% (¥{result['loss']:,.0f})")

# ========================================
# 4. 专业估值模型
# ========================================
print(f"\n💰 4. 专业估值模型")
print("-" * 80)

# DCF估值 (假设数据)
current_fcf = 10e9  # 100亿

vm = ValuationModels('AAPL')

# 两阶段DCF
dcf_2stage = vm.dcf_two_stage(
    current_fcf,
    growth_rate_high=0.15,
    growth_rate_stable=0.03,
    high_growth_years=5,
    wacc=0.10
)

print(f"  两阶段DCF:")
print(f"    当前FCF: ${current_fcf/1e9:.1f}B")
print(f"    企业价值: ${dcf_2stage['enterprise_value']/1e9:.1f}B")
print(f"    高增长期现值: ${dcf_2stage['high_growth_value']/1e9:.1f}B")
print(f"    终值现值: ${dcf_2stage['terminal_pv']/1e9:.1f}B")

# 三阶段DCF
dcf_3stage = vm.dcf_three_stage(
    current_fcf,
    growth_rate_high=0.20,
    growth_rate_transition=0.10,
    growth_rate_stable=0.03
)

print(f"\n  三阶段DCF:")
print(f"    企业价值: ${dcf_3stage['enterprise_value']/1e9:.1f}B")

# H模型
dcf_h = vm.dcf_h_model(
    current_fcf,
    growth_rate_initial=0.20,
    growth_rate_stable=0.03,
    half_life=5
)

print(f"\n  H模型:")
print(f"    企业价值: ${dcf_h['enterprise_value']/1e9:.1f}B")

# 相对估值
relative = vm.relative_valuation(
    current_price=180,
    eps=6.0,
    book_value_per_share=4.0,
    industry_pe=25,
    industry_pb=8
)

print(f"\n  相对估值:")
if 'pe' in relative:
    print(f"    PE估值: ${relative['pe']['fair_value']:.2f} (当前PE: {relative['pe']['current_pe']:.1f})")
if 'pb' in relative:
    print(f"    PB估值: ${relative['pb']['fair_value']:.2f} (当前PB: {relative['pb']['current_pb']:.1f})")

# ========================================
# 5. 综合评分
# ========================================
print(f"\n⭐ 5. 综合评分")
print("=" * 80)

scores = {}

# 趋势评分
if close > sma_20 > sma_60:
    scores['趋势'] = 18
elif close > sma_20:
    scores['趋势'] = 14
else:
    scores['趋势'] = 10

# 动量评分
if 40 <= rsi <= 60:
    scores['动量'] = 16
elif 30 <= rsi <= 70:
    scores['动量'] = 12
else:
    scores['动量'] = 8

# 风险评分
max_dd = report['max_drawdown']
if max_dd > -0.10:
    scores['风险'] = 28
elif max_dd > -0.20:
    scores['风险'] = 22
else:
    scores['风险'] = 16

# 收益评分
ann_ret = report['annual_return']
if ann_ret > 0.20:
    scores['收益'] = 28
elif ann_ret > 0.10:
    scores['收益'] = 22
else:
    scores['收益'] = 16

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
else:
    grade = 'D'
    recommendation = '观望'

print(f"  评级: {grade}")
print(f"  建议: {recommendation}")

print(f"\n" + "=" * 80)
print("✅ 专业金融分析演示完成")
print("=" * 80)
