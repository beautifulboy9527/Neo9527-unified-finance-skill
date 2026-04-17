#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple风格专业报告生成器 v4.9
- 纯黑背景 + 卡片式布局
- 数据可视化优先
- 支撑阻力位直观展示
- 投资警告显示
- 中英双语（中文为主）
- Phase 4: 综合结论深度优化
  - 整合 TechnicalAnalyzer
  - 概率分析
  - 场景应对方案
  - 风险提示完善
- Phase 5: 共享模块整合
  - 引用验证体系
  - 风险监控清单
"""

import sys
import os
from datetime import datetime
from typing import Dict, List
import yfinance as yf

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入技术分析模块
try:
    from technical_analyzer import TechnicalAnalyzer
    TECHNICAL_ANALYZER_AVAILABLE = True
except ImportError:
    TECHNICAL_ANALYZER_AVAILABLE = False

# 导入共享模块
try:
    from skills.shared.citation_validator.validator import CitationValidator
    from skills.shared.risk_monitor.monitor import RiskMonitor
    SHARED_MODULES_AVAILABLE = True
except ImportError:
    SHARED_MODULES_AVAILABLE = False


class AssetType:
    """资产类型"""
    CRYPTO = 'crypto'
    STOCK = 'stock'
    FOREX = 'forex'
    INDEX = 'index'


def generate_apple_style_report(symbol: str, output_dir: str = r"D:\OpenClaw\outputs\reports") -> str:
    """生成Apple风格专业报告"""
    
    print("=" * 60)
    print(f"生成 {symbol} Apple风格报告 (v4.9)")
    print("=" * 60)
    
    # 初始化共享模块
    validator = CitationValidator() if SHARED_MODULES_AVAILABLE else None
    monitor = RiskMonitor(asset_type='crypto') if SHARED_MODULES_AVAILABLE else None
    
    # 1. 获取数据 (带引用标注)
    market_data = get_real_market_data(symbol)
    if validator and market_data:
        market_data['citation'] = validator.cite('yfinance', '', datetime.now().strftime('%Y-%m-%d'))
    
    kline_data = get_real_kline_data(symbol, '3mo')
    if validator and kline_data:
        kline_data['citation'] = validator.cite('yfinance', '', datetime.now().strftime('%Y-%m-%d'))
    
    technical_data = calculate_indicators(kline_data)
    sr_levels = calculate_support_resistance(kline_data, 'fibonacci')
    onchain_data = get_onchain_data(symbol) if 'USD' in symbol else {}
    if validator and onchain_data:
        onchain_data['citation'] = validator.cite('DeFiLlama', '', datetime.now().strftime('%Y-%m-%d'))
    
    signals = generate_signals(market_data, technical_data, onchain_data, sr_levels)
    
    # 2. Phase 4: 综合结论深度分析
    total_strength = sum(s['strength'] for s in signals)
    
    # 技术分析综合
    tech_analysis = {}
    if TECHNICAL_ANALYZER_AVAILABLE and technical_data:
        tech_analysis = TechnicalAnalyzer.analyze_comprehensive(technical_data, total_strength)
    
    # 概率分析
    probability = calculate_probability(total_strength, technical_data, onchain_data)
    
    # 场景应对方案
    scenarios = generate_scenarios(market_data, technical_data, sr_levels, signals, tech_analysis)
    
    # 3. 生成监控清单
    monitoring_checklist = ''
    if monitor:
        monitoring_checklist = monitor.generate_checklist_html(symbol)
    
    # 4. 生成HTML
    html = generate_apple_html(
        symbol=symbol,
        market=market_data,
        kline=kline_data,
        technical=technical_data,
        sr=sr_levels,
        onchain=onchain_data,
        signals=signals,
        tech_analysis=tech_analysis,
        probability=probability,
        scenarios=scenarios,
        monitoring_checklist=monitoring_checklist,
        validator=validator
    )
    
    # 5. 保存
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(
        output_dir,
        f'{symbol}_apple_v4.9_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    )
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 报告已生成: {report_file}")
    return report_file


def get_real_market_data(symbol: str) -> Dict:
    """获取真实市场数据"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'price': info.get('regularMarketPrice', 0),
            'change_24h': info.get('regularMarketChangePercent', 0),
            'volume': info.get('regularMarketVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'high_24h': info.get('dayHigh', 0),
            'low_24h': info.get('dayLow', 0),
            'open': info.get('regularMarketOpen', 0),
            'previous_close': info.get('previousClose', 0),
            'data_source': 'yfinance'
        }
    except Exception as e:
        print(f"⚠️ 市场数据获取失败: {e}")
        return {'symbol': symbol, 'error': str(e)}


def get_real_kline_data(symbol: str, period: str) -> Dict:
    """获取真实K线数据"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {'error': 'No data'}
        
        candles = []
        for idx, row in hist.iterrows():
            candles.append({
                'time': int(idx.timestamp()),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume'])
            })
        
        closes = [c['close'] for c in candles]
        
        ma5 = []
        ma10 = []
        ma20 = []
        volume_data = []
        
        for i in range(len(candles)):
            if i >= 4:
                ma5.append({'time': candles[i]['time'], 'value': sum(closes[i-4:i+1]) / 5})
            
            if i >= 9:
                ma10.append({'time': candles[i]['time'], 'value': sum(closes[i-9:i+1]) / 10})
            
            if i >= 19:
                ma20.append({'time': candles[i]['time'], 'value': sum(closes[i-19:i+1]) / 20})
            
            volume_data.append({
                'time': candles[i]['time'],
                'value': candles[i]['volume'],
                'color': '#10b981' if candles[i]['close'] >= candles[i]['open'] else '#ef4444'
            })
        
        return {
            'candles': candles,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'volume': volume_data,
            'data_source': 'yfinance'
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_indicators(kline_data: Dict) -> Dict:
    """计算技术指标"""
    if not kline_data.get('candles'):
        return {}
    
    try:
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(kline_data['candles'])
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        # ADX
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=14).mean()
        
        # 布林带
        sma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        
        return {
            'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50,
            'macd': float(macd.iloc[-1]),
            'macd_signal': float(signal.iloc[-1]),
            'macd_histogram': float(histogram.iloc[-1]),
            'adx': float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 25,
            'bb_upper': float(sma20.iloc[-1] + 2 * std20.iloc[-1]),
            'bb_middle': float(sma20.iloc[-1]),
            'bb_lower': float(sma20.iloc[-1] - 2 * std20.iloc[-1]),
            'plus_di': float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else 20,
            'minus_di': float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else 20,
            'current_price': df['close'].iloc[-1],
            'data_source': '计算'
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_support_resistance(kline_data: Dict, method: str) -> Dict:
    """
    计算支撑阻力位（改进版）
    
    支撑位: 在当前价格下方，价格下跌时可能止跌的位置
    阻力位: 在当前价格上方，价格上涨时可能受阻的位置
    """
    if not kline_data.get('candles'):
        return {}
    
    candles = kline_data['candles']
    prices = [c['close'] for c in candles]
    current = prices[-1]
    
    high = max(prices)
    low = min(prices)
    diff = high - low
    
    # 斐波那契回调位（从高点往下算）
    # 阻力位（当前价上方）
    resistances = []
    
    r1 = high  # 历史高点
    if r1 > current:
        resistances.append({
            'name': 'resistance_2',
            'price': r1,
            'distance_pct': (r1 - current) / current * 100,
            'desc': '历史高点'
        })
    
    r2 = high - diff * 0.236  # 23.6%回调
    if r2 > current:
        resistances.append({
            'name': 'resistance_1',
            'price': r2,
            'distance_pct': (r2 - current) / current * 100,
            'desc': '23.6%回调位'
        })
    
    # 支撑位（当前价下方）
    supports = []
    
    s1 = high - diff * 0.382  # 38.2%回调
    if s1 < current:
        supports.append({
            'name': 'support_1',
            'price': s1,
            'distance_pct': (current - s1) / current * 100,
            'desc': '38.2%回调位'
        })
    
    s2 = high - diff * 0.5  # 50%回调
    if s2 < current:
        supports.append({
            'name': 'support_2',
            'price': s2,
            'distance_pct': (current - s2) / current * 100,
            'desc': '50%回调位'
        })
    
    s3 = high - diff * 0.618  # 61.8%回调（黄金分割）
    if s3 < current:
        supports.append({
            'name': 'support_3',
            'price': s3,
            'distance_pct': (current - s3) / current * 100,
            'desc': '61.8%回调位'
        })
    
    s4 = low  # 历史低点
    if s4 < current:
        supports.append({
            'name': 'support_4',
            'price': s4,
            'distance_pct': (current - s4) / current * 100,
            'desc': '历史低点'
        })
    
    # 构建返回字典
    result = {'current': {'price': current}}
    
    # 添加阻力位（按价格从低到高）
    for i, r in enumerate(sorted(resistances, key=lambda x: x['price'])):
        result[f'resistance_{i+1}'] = {
            'price': r['price'],
            'distance_pct': r['distance_pct'],
            'desc': r['desc']
        }
    
    # 添加支撑位（按价格从高到低）
    for i, s in enumerate(sorted(supports, key=lambda x: x['price'], reverse=True)):
        result[f'support_{i+1}'] = {
            'price': s['price'],
            'distance_pct': s['distance_pct'],
            'desc': s['desc']
        }
    
    return result


def calculate_probability(total_strength: int, technical: Dict, onchain: Dict) -> Dict:
    """
    概率分析 - 计算后续走势概率
    
    Returns:
        {
            'up': 60,  # 上涨概率
            'sideways': 20,  # 震荡概率
            'down': 20,  # 下跌概率
            'factors': {...},  # 影响因素
            'confidence': 0.7  # 置信度
        }
    """
    
    # 基础概率（基于总强度）
    if total_strength >= 10:
        base_up, base_sideways, base_down = 70, 15, 15
    elif total_strength >= 5:
        base_up, base_sideways, base_down = 60, 20, 20
    elif total_strength > 0:
        base_up, base_sideways, base_down = 50, 30, 20
    elif total_strength > -5:
        base_up, base_sideways, base_down = 35, 35, 30
    elif total_strength > -10:
        base_up, base_sideways, base_down = 25, 25, 50
    else:
        base_up, base_sideways, base_down = 15, 20, 65
    
    # 技术指标调整
    adjustments = {'up': 0, 'sideways': 0, 'down': 0}
    factors = []
    
    if technical:
        rsi = technical.get('rsi', 50)
        macd_hist = technical.get('macd_histogram', 0)
        adx = technical.get('adx', 25)
        plus_di = technical.get('plus_di', 20)
        minus_di = technical.get('minus_di', 20)
        
        # RSI调整
        if rsi > 70:
            adjustments['down'] += 10
            adjustments['up'] -= 5
            factors.append(f'RSI超买({rsi:.1f})，回调风险增加')
        elif rsi < 30:
            adjustments['up'] += 10
            adjustments['down'] -= 5
            factors.append(f'RSI超卖({rsi:.1f})，反弹机会增加')
        
        # MACD调整
        if macd_hist > 0:
            adjustments['up'] += 5
            factors.append('MACD金叉，动能向上')
        else:
            adjustments['down'] += 5
            factors.append('MACD死叉，动能减弱')
        
        # ADX调整
        if adx > 25:
            if plus_di > minus_di:
                adjustments['up'] += 5
                factors.append(f'ADX={adx:.1f}，上涨趋势明确')
            else:
                adjustments['down'] += 5
                factors.append(f'ADX={adx:.1f}，下跌趋势明确')
        else:
            adjustments['sideways'] += 10
            factors.append(f'ADX={adx:.1f}，趋势不明')
    
    # 链上数据调整
    if onchain:
        bias = onchain.get('whale_bias', 'neutral')
        avg_change = onchain.get('avg_change_7d', 0)
        
        if bias == 'accumulation':
            adjustments['up'] += 5
            factors.append(f'链上鲸鱼吸筹，7日TVL+{avg_change:.1f}%')
        elif bias == 'distribution':
            adjustments['down'] += 5
            factors.append(f'链上鲸鱼派发，7日TVL{avg_change:.1f}%')
    
    # 应用调整
    up = max(5, min(90, base_up + adjustments['up']))
    down = max(5, min(90, base_down + adjustments['down']))
    sideways = max(5, 100 - up - down)
    
    # 归一化
    total = up + sideways + down
    up = round(up / total * 100)
    sideways = round(sideways / total * 100)
    down = 100 - up - sideways
    
    # 置信度
    confidence = 0.5 + abs(up - down) / 100 * 0.5
    if technical and technical.get('adx', 25) > 25:
        confidence = min(0.9, confidence + 0.1)
    
    return {
        'up': up,
        'sideways': sideways,
        'down': down,
        'factors': factors[:5],
        'confidence': confidence,
        'direction': 'up' if up > max(sideways, down) else 'down' if down > max(sideways, up) else 'sideways'
    }


def generate_scenarios(market: Dict, technical: Dict, sr: Dict, signals: List, tech_analysis: Dict) -> Dict:
    """
    生成场景应对方案
    
    Returns:
        {
            'primary': {...},  # 主要场景
            'scenarios': [
                {'name': '场景A', 'trigger': '...', 'action': '...', ...},
                ...
            ],
            'risk_alerts': [...]  # 风险提示
        }
    """
    
    current_price = market.get('price', 0)
    change_24h = market.get('change_24h', 0)
    
    # 获取最近的支撑/阻力位
    nearest_support = None
    nearest_resistance = None
    
    if sr:
        if 'support_1' in sr:
            nearest_support = sr['support_1']
        if 'resistance_1' in sr:
            nearest_resistance = sr['resistance_1']
    
    # 技术指标
    rsi = technical.get('rsi', 50) if technical else 50
    macd_hist = technical.get('macd_histogram', 0) if technical else 0
    adx = technical.get('adx', 25) if technical else 25
    
    # 链上数据
    whale_bias = signals and any(s.get('name') == '鲸鱼吸筹' for s in signals)
    whale_distribution = signals and any(s.get('name') == '鲸鱼派发' for s in signals)
    
    # 确定主要场景
    if tech_analysis and 'scenario' in tech_analysis:
        primary_scenario = tech_analysis['scenario']
    else:
        # 基于信号判断
        total_strength = sum(s['strength'] for s in signals) if signals else 0
        if total_strength >= 10:
            primary_scenario = {'name': '强势上涨', 'type': 'strong_bullish'}
        elif total_strength >= 5:
            primary_scenario = {'name': '偏强震荡', 'type': 'bullish'}
        elif total_strength <= -10:
            primary_scenario = {'name': '弱势下跌', 'type': 'strong_bearish'}
        elif total_strength <= -5:
            primary_scenario = {'name': '偏弱震荡', 'type': 'bearish'}
        else:
            primary_scenario = {'name': '震荡整理', 'type': 'neutral'}
    
    # 场景A: 上涨突破
    scenario_a = {
        'name': '场景A: 上涨突破',
        'trigger': f'价格突破 ${nearest_resistance["price"]:,.0f}' if nearest_resistance else '价格突破近期高点',
        'probability': 30 if rsi < 70 and macd_hist > 0 else 20,
        'action': '加仓追涨',
        'strategy': '突破确认后加仓，目标下一阻力位',
        'stop_loss': f'跌破突破位-3% (${current_price * 0.97:,.0f})',
        'position': '加仓10-15%',
        'risk': '假突破风险，注意成交量确认'
    }
    
    # 场景B: 回调买入
    scenario_b = {
        'name': '场景B: 回调买入',
        'trigger': f'价格回调至 ${nearest_support["price"]:,.0f}' if nearest_support else '价格回调至支撑位',
        'probability': 40 if rsi < 70 else 30,
        'action': '分批建仓',
        'strategy': '第一笔15%在支撑位附近，第二笔15%在-3%，第三笔10%在-5%',
        'stop_loss': f'跌破支撑位-3% (${nearest_support["price"] * 0.97:,.0f})' if nearest_support else '跌破-5%止损',
        'position': '总仓位40%',
        'risk': '支撑位失效风险，严格止损'
    }
    
    # 场景C: 震荡观望
    scenario_c = {
        'name': '场景C: 震荡观望',
        'trigger': '在支撑阻力区间震荡，趋势不明',
        'probability': 30 if adx < 25 else 20,
        'action': '区间操作',
        'strategy': '高抛低吸，不追涨杀跌，控制仓位',
        'stop_loss': '不适用',
        'position': '保持30-40%',
        'risk': '突破风险，设置预警'
    }
    
    # 风险提示
    risk_alerts = []
    
    if rsi > 70:
        risk_alerts.append({
            'level': 'high',
            'icon': '⚠️',
            'text': f'RSI超买({rsi:.1f})，短期回调风险较高'
        })
    
    if change_24h > 10:
        risk_alerts.append({
            'level': 'medium',
            'icon': '⚠️',
            'text': f'24h涨幅过大({change_24h:+.1f}%)，追高风险高'
        })
    
    if whale_distribution:
        risk_alerts.append({
            'level': 'high',
            'icon': '🐋',
            'text': '链上鲸鱼派发，大资金流出'
        })
    
    if adx < 20:
        risk_alerts.append({
            'level': 'low',
            'icon': '📊',
            'text': f'趋势不明(ADX={adx:.1f})，建议观望'
        })
    
    if macd_hist < 0 and rsi > 50:
        risk_alerts.append({
            'level': 'medium',
            'icon': '📉',
            'text': 'MACD死叉且RSI偏高，动能减弱'
        })
    
    return {
        'primary': primary_scenario,
        'scenarios': [scenario_a, scenario_b, scenario_c],
        'risk_alerts': risk_alerts,
        'support': nearest_support,
        'resistance': nearest_resistance
    }


def get_onchain_data(symbol: str) -> Dict:
    """获取链上数据"""
    try:
        import requests
        
        base_symbol = symbol.split('-')[0].upper()
        url = "https://api.llama.fi/protocols"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code != 200:
            return {}
        
        protocols = resp.json()
        matched = [p for p in protocols if base_symbol.lower() in p.get('name', '').lower()][:5]
        
        if not matched:
            return {}
        
        total_tvl = sum(p.get('tvl', 0) for p in matched)
        avg_change = sum(p.get('change_7d', 0) for p in matched if p.get('change_7d')) / max(1, len([p for p in matched if p.get('change_7d')]))
        
        return {
            'whale_bias': 'accumulation' if avg_change > 3 else 'distribution' if avg_change < -3 else 'neutral',
            'total_tvl': total_tvl,
            'avg_change_7d': avg_change,
            'matched_protocols': len(matched),
            'data_source': 'DeFiLlama'
        }
        
    except:
        return {}


def generate_signals(market: Dict, technical: Dict, onchain: Dict, sr: Dict) -> List[Dict]:
    """生成交易信号"""
    signals = []
    
    # 技术指标信号
    if technical:
        rsi = technical.get('rsi', 50)
        if rsi > 70:
            signals.append({'category': '动量指标', 'name': 'RSI超买', 'strength': -2, 'desc': f'RSI={rsi:.1f}，短期回调风险'})
        elif rsi < 30:
            signals.append({'category': '动量指标', 'name': 'RSI超卖', 'strength': 3, 'desc': f'RSI={rsi:.1f}，反弹机会'})
        
        macd_hist = technical.get('macd_histogram', 0)
        if macd_hist > 0:
            signals.append({'category': '趋势指标', 'name': 'MACD金叉', 'strength': 3, 'desc': '动能向上'})
        elif macd_hist < 0:
            signals.append({'category': '趋势指标', 'name': 'MACD死叉', 'strength': -3, 'desc': '动能减弱'})
        
        adx = technical.get('adx', 25)
        if adx > 25:
            signals.append({'category': '趋势强度', 'name': 'ADX强趋势', 'strength': 2, 'desc': f'ADX={adx:.1f}，趋势明确'})
    
    # 支撑阻力信号
    if sr:
        current = market.get('price', 0) or (sr.get('current', {}).get('price', 0))
        
        # 检查支撑位（在当前价格下方）
        for i in range(1, 5):  # support_1, support_2, support_3, support_4
            key = f'support_{i}'
            if key in sr:
                level = sr[key]
                support_price = level.get('price', 0)
                
                # 确保支撑位在当前价格下方
                if support_price < current:
                    distance = level.get('distance_pct', 100)
                    
                    if distance < 5:  # 距离支撑位<5%
                        strength = 4 if distance < 2 else 3 if distance < 3 else 2
                        signals.append({
                            'category': '支撑位',
                            'name': level.get('desc', key.replace('_', ' ').title()),
                            'strength': strength,
                            'desc': f'接近支撑位${support_price:,.0f}，距离{distance:.1f}%，逢低买入机会'
                        })
        
        # 检查阻力位（在当前价格上方）
        for i in range(1, 3):  # resistance_1, resistance_2
            key = f'resistance_{i}'
            if key in sr:
                level = sr[key]
                resistance_price = level.get('price', 0)
                
                # 确保阻力位在当前价格上方
                if resistance_price > current:
                    distance = level.get('distance_pct', 100)
                    
                    if distance < 5:  # 距离阻力位<5%
                        strength = -3 if distance < 2 else -2
                        signals.append({
                            'category': '阻力位',
                            'name': level.get('desc', key.replace('_', ' ').title()),
                            'strength': strength,
                            'desc': f'接近阻力位${resistance_price:,.0f}，距离{distance:.1f}%，短期回调风险'
                        })
    
    # 链上数据信号
    if onchain:
        bias = onchain.get('whale_bias')
        if bias == 'accumulation':
            signals.append({'category': '链上数据', 'name': '鲸鱼吸筹', 'strength': 4, 'desc': f'TVL 7日+{onchain.get("avg_change_7d", 0):.1f}%'})
        elif bias == 'distribution':
            signals.append({'category': '链上数据', 'name': '鲸鱼派发', 'strength': -4, 'desc': f'TVL 7日{onchain.get("avg_change_7d", 0):.1f}%'})
    
    return signals


def generate_apple_html(**kwargs) -> str:
    """生成Apple风格HTML"""
    
    symbol = kwargs['symbol']
    market = kwargs['market']
    kline = kwargs['kline']
    technical = kwargs['technical']
    sr = kwargs['sr']
    onchain = kwargs['onchain']
    signals = kwargs['signals']
    tech_analysis = kwargs.get('tech_analysis', {})
    probability = kwargs.get('probability', {})
    scenarios = kwargs.get('scenarios', {})
    monitoring_checklist = kwargs.get('monitoring_checklist', '')
    validator = kwargs.get('validator', None)
    
    # 计算评分
    total_strength = sum(s['strength'] for s in signals)
    score = min(100, max(0, 50 + total_strength * 2))
    
    if score >= 70:
        decision = '买入'
        decision_en = 'BUY'
    elif score >= 55:
        decision = '逢低买入'
        decision_en = 'ACCUMULATE'
    elif score >= 45:
        decision = '持有'
        decision_en = 'HOLD'
    else:
        decision = '卖出'
        decision_en = 'SELL'
    
    # K线数据
    candlestick_js = "[]"
    ma5_js = "[]"
    ma10_js = "[]"
    ma20_js = "[]"
    volume_js = "[]"
    
    if kline.get('candles'):
        candlestick_js = "[" + ",".join([
            f'{{"time": {c["time"]}, "open": {c["open"]:.2f}, "high": {c["high"]:.2f}, "low": {c["low"]:.2f}, "close": {c["close"]:.2f}}}'
            for c in kline['candles']
        ]) + "]"
        
        if kline.get('ma5'):
            ma5_js = "[" + ",".join([f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}' for m in kline['ma5']]) + "]"
        
        if kline.get('ma10'):
            ma10_js = "[" + ",".join([f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}' for m in kline['ma10']]) + "]"
        
        if kline.get('ma20'):
            ma20_js = "[" + ",".join([f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}' for m in kline['ma20']]) + "]"
        
        if kline.get('volume'):
            volume_js = "[" + ",".join([f'{{"time": {v["time"]}, "value": {v["value"]:.0f}, "color": "{v["color"]}"}}' for v in kline['volume']]) + "]"
    
    # MACD数据
    macd_js = "[]"
    if kline.get('candles') and technical:
        try:
            import pandas as pd
            import numpy as np
            
            df = pd.DataFrame(kline['candles'])
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            macd_js = "[" + ",".join([
                f'{{"time": {kline["candles"][i]["time"]}, "macd": {macd_line.iloc[i]:.2f}, "signal": {signal_line.iloc[i]:.2f}, "histogram": {histogram.iloc[i]:.2f}}}'
                for i in range(len(kline['candles'])) if not pd.isna(macd_line.iloc[i])
            ]) + "]"
        except:
            pass
    
    bullish = [s for s in signals if s['strength'] > 0]
    bearish = [s for s in signals if s['strength'] < 0]
    
    current_price = market.get('price', 0)
    
    # 支撑阻力位HTML（优化显示）
    sr_html = ""
    if sr:
        # 阻力位（在当前价格上方）
        resistances = []
        for key in ['resistance_1', 'resistance_2']:
            if key in sr and sr[key]['price'] > current_price:
                resistances.append({
                    'name': key.replace('_', ' ').title(),
                    'price': sr[key]['price'],
                    'distance': sr[key]['distance_pct']
                })
        
        # 支撑位（在当前价格下方）
        supports = []
        for key in ['support_1', 'support_2', 'support_3']:
            if key in sr and sr[key]['price'] < current_price:
                supports.append({
                    'name': key.replace('_', ' ').title(),
                    'price': sr[key]['price'],
                    'distance': sr[key]['distance_pct']
                })
        
        # 生成阻力位HTML
        resistance_items = ""
        for r in reversed(resistances):
            resistance_items += f"""
                    <div class="flex justify-between items-center p-3 bg-red-500/10 rounded-lg">
                        <span class="text-gray-300">{r['name']}</span>
                        <div class="text-right">
                            <div class="text-lg font-bold text-red-400">${r['price']:,.2f}</div>
                            <div class="text-xs text-gray-400">+{r['distance']:.1f}%</div>
                        </div>
                    </div>
            """
        
        # 生成支撑位HTML
        support_items = ""
        for s in supports:
            support_items += f"""
                    <div class="flex justify-between items-center p-3 bg-green-500/10 rounded-lg">
                        <span class="text-gray-300">{s['name']}</span>
                        <div class="text-right">
                            <div class="text-lg font-bold text-green-400">${s['price']:,.2f}</div>
                            <div class="text-xs text-gray-400">-{s['distance']:.1f}%</div>
                        </div>
                    </div>
            """
        
        change_24h = market.get('change_24h', 0)
        change_color = 'text-green-400' if change_24h > 0 else 'text-red-400'
        
        sr_html = f"""
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 阻力位 -->
            <div class="bg-gradient-to-br from-red-900/20 to-red-800/10 rounded-xl p-6 border border-red-500/30">
                <h3 class="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
                    <i class="fas fa-arrow-up"></i> 阻力位 (上方)
                </h3>
                <div class="space-y-3">
                    {resistance_items}
                </div>
            </div>
            
            <!-- 支撑位 -->
            <div class="bg-gradient-to-br from-green-900/20 to-green-800/10 rounded-xl p-6 border border-green-500/30">
                <h3 class="text-xl font-bold text-green-400 mb-4 flex items-center gap-2">
                    <i class="fas fa-arrow-down"></i> 支撑位 (下方)
                </h3>
                <div class="space-y-3">
                    {support_items}
                </div>
            </div>
        </div>
        
        <!-- 当前价格 -->
        <div class="mt-6 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-6 border border-blue-500/30">
            <div class="text-center">
                <div class="text-sm text-gray-400 mb-2">当前价格 Current Price</div>
                <div class="text-5xl font-bold text-white">${current_price:,.2f}</div>
                <div class="text-lg mt-2 {change_color}">
                    {change_24h:+.2f}% 24h
                </div>
            </div>
        </div>
        """
    
    # 技术指标HTML（优化解读）
    tech_html = ""
    if technical:
        rsi = technical.get('rsi', 50)
        rsi_status = '超买 (卖出信号)' if rsi > 70 else '超卖 (买入信号)' if rsi < 30 else '中性'
        rsi_color = 'text-red-400' if rsi > 70 else 'text-green-400' if rsi < 30 else 'text-gray-300'
        
        macd_hist = technical.get('macd_histogram', 0)
        macd_status = '金叉 (看涨)' if macd_hist > 0 else '死叉 (看跌)'
        macd_color = 'text-green-400' if macd_hist > 0 else 'text-red-400'
        
        adx = technical.get('adx', 25)
        adx_status = '强趋势' if adx > 25 else '弱趋势'
        adx_color = 'text-green-400' if adx > 25 else 'text-yellow-400'
        
        plus_di = technical.get('plus_di', 20)
        minus_di = technical.get('minus_di', 20)
        di_status = '多头主导' if plus_di > minus_di else '空头主导'
        di_color = 'text-green-400' if plus_di > minus_di else 'text-red-400'
        
        tech_html = f"""
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <!-- RSI -->
            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div class="text-4xl font-bold {rsi_color} mb-2">{rsi:.1f}</div>
                <div class="text-sm text-gray-400 mb-1">RSI (相对强弱指数)</div>
                <div class="text-xs {rsi_color}">{rsi_status}</div>
            </div>
            
            <!-- MACD -->
            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div class="text-4xl font-bold {macd_color} mb-2">{macd_hist:.2f}</div>
                <div class="text-sm text-gray-400 mb-1">MACD (柱状图)</div>
                <div class="text-xs {macd_color}">{macd_status}</div>
            </div>
            
            <!-- ADX -->
            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div class="text-4xl font-bold {adx_color} mb-2">{adx:.1f}</div>
                <div class="text-sm text-gray-400 mb-1">ADX (趋势强度)</div>
                <div class="text-xs {adx_color}">{adx_status}</div>
            </div>
            
            <!-- DI -->
            <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
                <div class="text-4xl font-bold {di_color} mb-2">{plus_di:.1f}/{minus_di:.1f}</div>
                <div class="text-sm text-gray-400 mb-1">+DI/-DI (方向指标)</div>
                <div class="text-xs {di_color}">{di_status}</div>
            </div>
        </div>
        
        <!-- 技术指标解读 -->
        <div class="mt-6 bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <h3 class="text-lg font-bold text-white mb-4">📊 技术指标综合解读</h3>
            <div class="space-y-4">
                """
        
        # 综合分析各指标
        trend_signals = []
        momentum_signals = []
        
        # 趋势信号
        if adx > 25:
            trend_signals.append('趋势强劲')
        else:
            trend_signals.append('趋势不明显')
        
        if plus_di > minus_di:
            trend_signals.append('多头主导')
        else:
            trend_signals.append('空头主导')
        
        # 动量信号
        if rsi > 70:
            momentum_signals.append('超买')
        elif rsi < 30:
            momentum_signals.append('超卖')
        else:
            momentum_signals.append('中性')
        
        if macd_hist > 0:
            momentum_signals.append('动能向上')
        else:
            momentum_signals.append('动能减弱')
        
        # 综合建议
        if total_strength > 5:
            suggestion = '技术面偏多，建议逢低买入'
            suggestion_color = 'text-green-400'
        elif total_strength < -5:
            suggestion = '技术面偏空，建议谨慎观望'
            suggestion_color = 'text-red-400'
        else:
            suggestion = '技术面信号不明确，建议观望'
            suggestion_color = 'text-yellow-400'
        
        tech_html += f"""
                <!-- 趋势分析 -->
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <h4 class="text-base font-bold text-orange-400 mb-2 flex items-center gap-2">
                        <i class="fas fa-chart-line"></i> 趋势分析
                    </h4>
                    <p class="text-sm text-gray-300">
                        <span class="text-white font-semibold">ADX {adx:.1f}</span> {', '.join(trend_signals)}；
                        <span class="text-white font-semibold">+DI/-DI {plus_di:.1f}/{minus_di:.1f}</span>，
                        {'多头力量占优，上涨趋势更强' if plus_di > minus_di else '空头力量占优，下跌趋势更强'}。
                    </p>
                </div>
                
                <!-- 动量分析 -->
                <div class="bg-gray-900/50 rounded-lg p-4">
                    <h4 class="text-base font-bold text-orange-400 mb-2 flex items-center gap-2">
                        <i class="fas fa-bolt"></i> 动量分析
                    </h4>
                    <p class="text-sm text-gray-300">
                        <span class="text-white font-semibold">RSI {rsi:.1f}</span> {', '.join(momentum_signals)}；
                        <span class="text-white font-semibold">MACD</span> 
                        {'柱状图为正，金叉形成，动能向上' if macd_hist > 0 else '柱状图为负，死叉形成，动能减弱'}。
                    </p>
                </div>
                
                <!-- 综合建议 -->
                <div class="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-lg p-4 border border-blue-500/30">
                    <h4 class="text-base font-bold text-blue-400 mb-2 flex items-center gap-2">
                        <i class="fas fa-lightbulb"></i> 综合建议
                    </h4>
                    <p class="text-sm text-gray-300">
                        {f'当前RSI处于超买区域({rsi:.1f})，短期面临回调压力；但MACD金叉且趋势强劲，建议谨慎追高，等待回调后逢低布局。' if rsi > 70 and macd_hist > 0 and adx > 25 else ''}
                        {f'当前RSI处于超卖区域({rsi:.1f})，存在反弹机会；配合MACD金叉信号，可考虑分批建仓。' if rsi < 30 and macd_hist > 0 else ''}
                        {f'趋势强劲(ADX={adx:.1f})且多头主导，RSI和MACD均显示中性偏多，建议顺势交易。' if adx > 25 and plus_di > minus_di and 30 <= rsi <= 70 else ''}
                        {f'趋势不明显(ADX={adx:.1f})，市场可能震荡，建议观望等待明确信号。' if adx <= 25 else ''}
                        {f'虽然MACD显示动能向上，但RSI超买({rsi:.1f})，建议谨慎，等待RSI回归中性区域。' if macd_hist > 0 and rsi > 70 else ''}
                    </p>
                    <p class="text-base font-bold {suggestion_color} mt-3">{suggestion}</p>
                </div>
            </div>
        </div>
        """
    
    # 链上数据HTML
    onchain_html = ""
    if onchain:
        bias = onchain.get('whale_bias', 'neutral')
        bias_text = '吸筹' if bias == 'accumulation' else '派发' if bias == 'distribution' else '中性'
        bias_color = 'text-green-400' if bias == 'accumulation' else 'text-red-400' if bias == 'distribution' else 'text-gray-400'
        
        avg_change = onchain.get('avg_change_7d', 0)
        change_color = 'text-green-400' if avg_change > 0 else 'text-red-400'
        
        onchain_html = f"""
        <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <i class="fas fa-water"></i> 链上数据
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                    <div class="text-3xl font-bold {bias_color} mb-1">{bias_text}</div>
                    <div class="text-xs text-gray-400">鲸鱼偏向</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-white mb-1">${onchain.get('total_tvl', 0)/1e9:.1f}B</div>
                    <div class="text-xs text-gray-400">生态TVL</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold {change_color} mb-1">
                        {avg_change:+.1f}%
                    </div>
                    <div class="text-xs text-gray-400">7日变化</div>
                </div>
                <div class="text-center">
                    <div class="text-3xl font-bold text-white mb-1">{onchain.get('matched_protocols', 0)}</div>
                    <div class="text-xs text-gray-400">相关协议</div>
                </div>
            </div>
        </div>
        """
    
    # 信号HTML
    signals_html = ""
    if signals:
        # 看涨信号
        bullish_items = ""
        for s in bullish:
            bullish_items += f"""
                    <div class="flex justify-between items-center p-3 bg-green-500/10 rounded-lg">
                        <div>
                            <div class="text-white font-semibold">{s['name']}</div>
                            <div class="text-xs text-gray-400">{s['category']}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-lg font-bold text-green-400">+{s['strength']}</div>
                            <div class="text-xs text-gray-400">{s['desc']}</div>
                        </div>
                    </div>
            """
        
        # 看跌信号
        bearish_items = ""
        for s in bearish:
            bearish_items += f"""
                    <div class="flex justify-between items-center p-3 bg-red-500/10 rounded-lg">
                        <div>
                            <div class="text-white font-semibold">{s['name']}</div>
                            <div class="text-xs text-gray-400">{s['category']}</div>
                        </div>
                        <div class="text-right">
                            <div class="text-lg font-bold text-red-400">{s['strength']}</div>
                            <div class="text-xs text-gray-400">{s['desc']}</div>
                        </div>
                    </div>
            """
        
        signals_html = f"""
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 看涨信号 -->
            <div class="bg-gradient-to-br from-green-900/20 to-green-800/10 rounded-xl p-6 border border-green-500/30">
                <h3 class="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
                    <i class="fas fa-arrow-trend-up"></i> 看涨信号 ({len(bullish)}项)
                </h3>
                <div class="space-y-3">
                    {bullish_items}
                </div>
            </div>
            
            <!-- 看跌信号 -->
            <div class="bg-gradient-to-br from-red-900/20 to-red-800/10 rounded-xl p-6 border border-red-500/30">
                <h3 class="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
                    <i class="fas fa-arrow-trend-down"></i> 看跌信号 ({len(bearish)}项)
                </h3>
                <div class="space-y-3">
                    {bearish_items}
                </div>
            </div>
        </div>
        """
    
    # 支撑阻力位价格（用于K线图标注）
    sr_prices_js = "[]"
    if sr:
        sr_prices = []
        for key in ['resistance_2', 'resistance_1', 'support_1', 'support_2', 'support_3']:
            if key in sr:
                sr_prices.append({
                    'price': sr[key]['price'],
                    'type': 'resistance' if 'resistance' in key else 'support',
                    'name': key.replace('_', ' ').title()
                })
        sr_prices_js = "[" + ",".join([
            f'{{"price": {p["price"]:.2f}, "type": "{p["type"]}", "name": "{p["name"]}"}}'
            for p in sr_prices
        ]) + "]"
    
    # Phase 4: 概率分析HTML
    probability_html = ""
    if probability:
        up_prob = probability.get('up', 33)
        sideway_prob = probability.get('sideways', 34)
        down_prob = probability.get('down', 33)
        confidence = probability.get('confidence', 0.5)
        factors = probability.get('factors', [])
        
        factors_html = ''.join([f'<li class="text-gray-400">• {f}</li>' for f in factors[:3]])
        
        probability_html = f"""
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-dice text-orange-400"></i> 后续走势概率分析
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <!-- 上涨概率 -->
                <div class="bg-gradient-to-br from-green-900/30 to-green-800/10 rounded-xl p-6 border border-green-500/30 text-center">
                    <div class="text-5xl font-bold text-green-400 mb-2">{up_prob}%</div>
                    <div class="text-sm text-gray-400">上涨概率</div>
                    <div class="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div class="h-full bg-green-400 rounded-full" style="width: {up_prob}%"></div>
                    </div>
                </div>
                
                <!-- 震荡概率 -->
                <div class="bg-gradient-to-br from-yellow-900/30 to-yellow-800/10 rounded-xl p-6 border border-yellow-500/30 text-center">
                    <div class="text-5xl font-bold text-yellow-400 mb-2">{sideway_prob}%</div>
                    <div class="text-sm text-gray-400">震荡概率</div>
                    <div class="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div class="h-full bg-yellow-400 rounded-full" style="width: {sideway_prob}%"></div>
                    </div>
                </div>
                
                <!-- 下跌概率 -->
                <div class="bg-gradient-to-br from-red-900/30 to-red-800/10 rounded-xl p-6 border border-red-500/30 text-center">
                    <div class="text-5xl font-bold text-red-400 mb-2">{down_prob}%</div>
                    <div class="text-sm text-gray-400">下跌概率</div>
                    <div class="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div class="h-full bg-red-400 rounded-full" style="width: {down_prob}%"></div>
                    </div>
                </div>
            </div>
            
            <!-- 影响因素 -->
            <div class="bg-gray-800/50 rounded-lg p-4">
                <h4 class="text-sm font-bold text-gray-400 mb-2">影响因素</h4>
                <ul class="text-sm space-y-1">
                    {factors_html}
                </ul>
                <div class="mt-3 text-xs text-gray-500">
                    置信度: {confidence*100:.0f}%
                </div>
            </div>
        </div>
        """
    
    # Phase 4: 场景应对方案HTML
    scenarios_html = ""
    if scenarios:
        scenario_list = scenarios.get('scenarios', [])
        primary = scenarios.get('primary', {})
        
        scenario_items = ""
        for s in scenario_list:
            color = 'green' if 'A' in s['name'] else 'blue' if 'B' in s['name'] else 'yellow'
            scenario_items += f"""
            <div class="bg-gray-800/50 rounded-lg p-5 border border-gray-700">
                <div class="flex justify-between items-start mb-3">
                    <h4 class="font-bold text-{color}-400 text-lg">{s['name']}</h4>
                    <span class="text-xs bg-gray-700 px-2 py-1 rounded">{s['probability']}%</span>
                </div>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span class="text-gray-400">触发条件:</span>
                        <span class="text-white">{s['trigger']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">操作策略:</span>
                        <span class="text-white">{s['action']} - {s['strategy']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">止损设置:</span>
                        <span class="text-red-400">{s['stop_loss']}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">仓位建议:</span>
                        <span class="text-green-400">{s['position']}</span>
                    </div>
                </div>
            </div>
            """
        
        scenarios_html = f"""
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-chess text-orange-400"></i> 场景应对方案
            </h2>
            
            <!-- 当前场景 -->
            <div class="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl p-4 mb-6 border border-blue-500/30">
                <div class="flex items-center gap-2">
                    <span class="text-2xl">🎯</span>
                    <span class="text-lg font-bold text-white">当前场景: {primary.get('name', '分析中')}</span>
                </div>
                {f'<p class="text-sm text-gray-400 mt-2">{primary.get("suggestion", "")}</p>' if primary.get('suggestion') else ''}
            </div>
            
            <!-- 场景列表 -->
            <div class="space-y-4">
                {scenario_items}
            </div>
        </div>
        """
    
    # Phase 4: 风险提示HTML
    risk_alerts_html = ""
    if scenarios and scenarios.get('risk_alerts'):
        alerts = scenarios['risk_alerts']
        alert_items = ""
        for alert in alerts:
            level_color = 'red' if alert['level'] == 'high' else 'yellow' if alert['level'] == 'medium' else 'gray'
            alert_items += f"""
            <div class="flex items-start gap-3 p-3 bg-{level_color}-900/20 rounded-lg border border-{level_color}-500/30">
                <span class="text-xl">{alert['icon']}</span>
                <span class="text-sm text-gray-300">{alert['text']}</span>
            </div>
            """
        
        risk_alerts_html = f"""
        <div class="bg-red-900/10 border border-red-500/30 rounded-xl p-6 mb-8 fade-in">
            <h2 class="text-xl font-bold text-red-400 mb-4 flex items-center gap-3">
                <i class="fas fa-exclamation-circle"></i> 风险警示
            </h2>
            <div class="space-y-2">
                {alert_items}
            </div>
        </div>
        """
    
    # ... 其他代码
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 投资分析报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            background: #000000;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        
        .card {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 16px;
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            border-color: #FF6900;
            transform: translateY(-2px);
        }}
        
        .gradient-text {{
            background: linear-gradient(135deg, #FF6900 0%, #FF8C00 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
</head>
<body class="min-h-screen">
    <!-- 主容器 -->
    <div class="max-w-7xl mx-auto px-4 py-8">
        
        <!-- 标题区域 -->
        <div class="text-center mb-12 fade-in">
            <h1 class="text-6xl font-bold gradient-text mb-3">{symbol}</h1>
            <p class="text-2xl text-gray-300">投资分析报告 Investment Analysis</p>
            <p class="text-sm text-gray-500 mt-2">{datetime.now().strftime('%Y年%m月%d日 %H:%M')} | v4.8</p>
        </div>
        
        <!-- 综合评分卡片 -->
        <div class="card p-8 mb-8 fade-in">
            <div class="text-center">
                <div class="text-7xl font-bold gradient-text mb-2">{score}/100</div>
                <div class="text-3xl font-bold text-white mb-2">{decision}</div>
                <div class="text-lg text-gray-400">{decision_en}</div>
                <div class="mt-4 flex justify-center gap-8 text-sm text-gray-400">
                    <span>总强度: <span class="text-white font-bold">{total_strength:+d}</span></span>
                    <span>看涨: <span class="text-green-400 font-bold">{len(bullish)}</span>项</span>
                    <span>看跌: <span class="text-red-400 font-bold">{len(bearish)}</span>项</span>
                </div>
            </div>
        </div>
        
        <!-- 投资警告 -->
        <div class="bg-red-900/20 border border-red-500/50 rounded-xl p-6 mb-8 fade-in">
            <div class="flex items-start gap-4">
                <i class="fas fa-exclamation-triangle text-3xl text-red-400"></i>
                <div>
                    <h3 class="text-xl font-bold text-red-400 mb-2">⚠️ 投资风险提示</h3>
                    <p class="text-gray-300 text-sm leading-relaxed">
                        本报告基于公开数据分析，仅供参考，不构成投资建议。加密货币市场波动极大，可能导致资金全部损失。
                        投资前请充分了解风险，根据自身风险承受能力谨慎决策。切勿投入超过您承受能力的资金。
                    </p>
                </div>
            </div>
        </div>
        
        <!-- 市场数据 -->
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-chart-line text-orange-400"></i> 市场数据
            </h2>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold text-white">${market.get('price', 0):,.2f}</div>
                    <div class="text-xs text-gray-400 mt-1">当前价格</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold {('text-green-400' if market.get('change_24h', 0) > 0 else 'text-red-400')}">
                        {market.get('change_24h', 0):+.2f}%
                    </div>
                    <div class="text-xs text-gray-400 mt-1">24h涨跌</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold text-white">${market.get('high_24h', 0):,.2f}</div>
                    <div class="text-xs text-gray-400 mt-1">24h最高</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold text-white">${market.get('low_24h', 0):,.2f}</div>
                    <div class="text-xs text-gray-400 mt-1">24h最低</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold text-white">${market.get('volume', 0)/1e9:.2f}B</div>
                    <div class="text-xs text-gray-400 mt-1">成交量</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-4 text-center">
                    <div class="text-2xl font-bold text-white">${market.get('market_cap', 0)/1e9:.2f}B</div>
                    <div class="text-xs text-gray-400 mt-1">市值</div>
                </div>
            </div>
        </div>
        
        <!-- K线图 + 成交量图 -->
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-3">
                <i class="fas fa-chart-area text-orange-400"></i> 价格走势
            </h2>
            
            <!-- K线图 -->
            <div id="kline-chart" style="width: 100%; height: 400px;"></div>
            
            <!-- 成交量图 -->
            <div id="volume-chart" style="width: 100%; height: 100px; margin-top: 8px;"></div>
            
            <!-- 图例 -->
            <div class="flex justify-center gap-6 text-sm text-gray-400 mt-3">
                <span><span class="inline-block w-4 h-0.5 bg-blue-400 mr-1"></span>MA5</span>
                <span><span class="inline-block w-4 h-0.5 bg-green-400 mr-1"></span>MA10</span>
                <span><span class="inline-block w-4 h-0.5 bg-red-400 mr-1"></span>MA20</span>
                <span class="text-red-400"><span class="inline-block w-4 h-0.5 border-dashed border-t-2 border-red-400 mr-1"></span>阻力位</span>
                <span class="text-green-400"><span class="inline-block w-4 h-0.5 border-dashed border-t-2 border-green-400 mr-1"></span>支撑位</span>
            </div>
        </div>
        
        <!-- 支撑阻力位 -->
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-layer-group text-orange-400"></i> 支撑阻力位
            </h2>
            {sr_html}
        </div>
        
        <!-- 技术面分析（整合技术指标+交易信号）-->
        <div class="card p-6 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-chart-bar text-orange-400"></i> 技术面分析
            </h2>
            {tech_html}
            
            <!-- 交易信号 -->
            <div class="mt-6">
                <h3 class="text-lg font-bold text-white mb-4">交易信号</h3>
                {signals_html}
            </div>
        </div>
        
        <!-- 链上数据 -->
        {onchain_html}
        
        <!-- Phase 4: 概率分析 -->
        {probability_html}
        
        <!-- Phase 4: 场景应对方案 -->
        {scenarios_html}
        
        <!-- Phase 4: 风险提示 -->
        {risk_alerts_html}
        
        <!-- 综合结论 -->
        <div class="card p-8 mb-8 fade-in">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <i class="fas fa-lightbulb text-orange-400"></i> 综合结论
            </h2>
            <div class="space-y-4 text-gray-300">
                <p class="text-lg">
                    <strong class="text-white">{symbol}</strong> 当前价格 
                    <strong class="text-orange-400">${current_price:,.2f}</strong>，
                    综合 <strong class="text-white">{len(signals)}</strong> 项交易信号分析。
                </p>
                
                <p class="text-lg">
                    总强度 <strong class="{('text-green-400' if total_strength > 0 else 'text-red-400')}">{total_strength:+d}</strong>，
                    综合评分 <strong class="text-white text-2xl">{score}/100</strong>，
                    建议 <strong class="text-orange-400 text-xl">{decision}</strong>。
                </p>
                
                <div class="mt-6 p-4 bg-gray-800 rounded-lg">
                    <p class="text-sm">
                        {'技术面偏多，支撑位提供买入机会，建议逢低布局。' if total_strength > 0 else '技术面偏空，注意风险控制，建议观望或轻仓。' if total_strength < 0 else '信号不明确，市场可能震荡，建议观望。'}
                    </p>
                    {'<p class="text-sm mt-2 text-green-400">链上数据显示鲸鱼正在吸筹，长期看涨。</p>' if onchain.get('whale_bias') == 'accumulation' else ''}
                </div>
                
                <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="p-4 bg-green-900/20 border border-green-500/30 rounded-lg">
                        <h4 class="font-bold text-green-400 mb-2">✅ 支持因素</h4>
                        <ul class="text-sm space-y-1">
                            {''.join([f'<li>• {s["name"]}: {s["desc"]}</li>' for s in bullish[:3]])}
                        </ul>
                    </div>
                    <div class="p-4 bg-red-900/20 border border-red-500/30 rounded-lg">
                        <h4 class="font-bold text-red-400 mb-2">⚠️ 风险因素</h4>
                        <ul class="text-sm space-y-1">
                            {''.join([f'<li>• {s["name"]}: {s["desc"]}</li>' for s in bearish[:3]])}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 数据来源 -->
        <div class="card p-6 fade-in">
            <h2 class="text-xl font-bold text-white mb-4">数据来源</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div class="bg-gray-800 rounded-lg p-3 text-center">
                    <i class="fas fa-database text-orange-400 mb-1"></i>
                    <div class="text-gray-400">市场数据</div>
                    <div class="text-white font-bold">{market.get('data_source', 'yfinance')}</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-3 text-center">
                    <i class="fas fa-chart-line text-orange-400 mb-1"></i>
                    <div class="text-gray-400">K线数据</div>
                    <div class="text-white font-bold">{kline.get('data_source', 'yfinance')}</div>
                </div>
                <div class="bg-gray-800 rounded-lg p-3 text-center">
                    <i class="fas fa-calculator text-orange-400 mb-1"></i>
                    <div class="text-gray-400">技术指标</div>
                    <div class="text-white font-bold">{technical.get('data_source', '计算')}</div>
                </div>
                {f'<div class="bg-gray-800 rounded-lg p-3 text-center"><i class="fas fa-link text-orange-400 mb-1"></i><div class="text-gray-400">链上数据</div><div class="text-white font-bold">{onchain.get("data_source", "DeFiLlama")}</div></div>' if onchain else ''}
            </div>
            
            <!-- 引用评级说明 -->
            <div class="mt-4 p-4 bg-gray-800/50 rounded-lg text-xs text-gray-400">
                <p><strong class="text-white">数据来源评级:</strong>
                <span class="text-green-400">A</span> (最权威) | 
                <span class="text-blue-400">B</span> (高可信) | 
                <span class="text-yellow-400">C</span> (中等可信) | 
                <span class="text-red-400">D</span> (低可信) | 
                <span class="text-gray-400">E</span> (未验证)</p>
            </div>
        </div>
        
        <!-- 监控清单 -->
        {monitoring_checklist}
        
        <!-- 页脚 -->
        <div class="text-center mt-12 pb-8 text-gray-500 text-sm">
            <p>Neo9527 Finance Skill v4.9 | 专业级金融分析系统</p>
            <p class="mt-2">Apple风格设计 | 数据真实可靠 | 分析专业深入 | 引用验证 + 风险监控</p>
        </div>
    </div>
    
    <script>
        // 滚动动画
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, {{ threshold: 0.1 }});
        
        document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
        
        // K线图数据
        const candlestickData = {candlestick_js};
        const ma5Data = {ma5_js};
        const ma10Data = {ma10_js};
        const ma20Data = {ma20_js};
        const volumeData = {volume_js};
        const srPrices = {sr_prices_js};
        
        // 图表实例
        let klineChart, volumeChart, macdChartInstance;
        
        if (candlestickData.length > 0) {{
            // K线图配置（固定，禁用缩放）
            klineChart = LightweightCharts.createChart(document.getElementById('kline-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#1a1a1a' }}, textColor: '#9ca3af' }},
                grid: {{ vertLines: {{ color: '#2a2a2a' }}, horzLines: {{ color: '#2a2a2a' }} }},
                timeScale: {{
                    timeVisible: true,
                    borderColor: '#333',
                    rightBarStaysOnScroll: true,
                    borderVisible: true,
                    fixLeftEdge: true,
                    fixRightEdge: true
                }},
                handleScroll: {{
                    mouseWheel: false,
                    pressedMouseMove: false,
                    horzTouchDrag: false,
                    vertTouchDrag: false
                }},
                handleScale: {{
                    axisPressedMouseMove: false,
                    mouseWheel: false,
                    pinch: false
                }}
            }});
            
            // K线系列
            const candleSeries = klineChart.addCandlestickSeries({{
                upColor: '#10b981',
                downColor: '#ef4444',
                borderUpColor: '#10b981',
                borderDownColor: '#ef4444',
                wickUpColor: '#10b981',
                wickDownColor: '#ef4444'
            }});
            candleSeries.setData(candlestickData);
            
            // 均线
            if (ma5Data.length > 0) klineChart.addLineSeries({{ color: '#3b82f6', lineWidth: 1, title: 'MA5' }}).setData(ma5Data);
            if (ma10Data.length > 0) klineChart.addLineSeries({{ color: '#10b981', lineWidth: 1, title: 'MA10' }}).setData(ma10Data);
            if (ma20Data.length > 0) klineChart.addLineSeries({{ color: '#ef4444', lineWidth: 1, title: 'MA20' }}).setData(ma20Data);
            
            // 支撑阻力位标注
            srPrices.forEach(sr => {{
                const color = sr.type === 'resistance' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)';
                const lineColor = sr.type === 'resistance' ? '#ef4444' : '#10b981';
                
                klineChart.addLineSeries({{
                    color: lineColor,
                    lineWidth: 1,
                    lineStyle: LightweightCharts.LineStyle.Dashed,
                    priceLineVisible: false,
                    lastValueVisible: false,
                    crosshairMarkerVisible: false
                }}).setData(candlestickData.map(c => ({{ time: c.time, value: sr.price }})));
            }});
            
            // 成交量图
            volumeChart = LightweightCharts.createChart(document.getElementById('volume-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#1a1a1a' }}, textColor: '#9ca3af' }},
                grid: {{ vertLines: {{ color: '#2a2a2a' }}, horzLines: {{ color: '#2a2a2a' }} }},
                timeScale: {{ visible: false }}
            }});
            
            // 成交量图（共享时间轴）
            volumeChart = LightweightCharts.createChart(document.getElementById('volume-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#1a1a1a' }}, textColor: '#9ca3af' }},
                grid: {{ vertLines: {{ color: '#2a2a2a' }}, horzLines: {{ color: '#2a2a2a' }} }},
                timeScale: {{ visible: false }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Hidden
                }}
            }});
            
            volumeChart.addHistogramSeries({{ priceFormat: {{ type: 'volume' }} }}).setData(volumeData);
            
            // 同步时间轴：K线图和成交量图
            klineChart.timeScale().subscribeVisibleLogicalRangeChange(range => {{
                if (range && volumeChart) {{
                    volumeChart.timeScale().setVisibleLogicalRange(range);
                }}
            }});
            
            volumeChart.timeScale().subscribeVisibleLogicalRangeChange(range => {{
                if (range && klineChart) {{
                    klineChart.timeScale().setVisibleLogicalRange(range);
                }}
            }});
        }}
        
        // MACD图表（已移除）
        const macdData = [];
        
        // 支撑阻力位开关
        let showSRLines = true;
        
        // 图表大小自适应
        window.addEventListener('resize', () => {{
            if (klineChart) klineChart.applyOptions({{ width: document.getElementById('kline-chart').parentElement.clientWidth }});
            if (volumeChart) volumeChart.applyOptions({{ width: document.getElementById('volume-chart').parentElement.clientWidth }});
        }});
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'ETH-USD'
    
    try:
        report_file = generate_apple_style_report(symbol)
        print(f"\n✅ Apple风格报告生成成功: {report_file}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
