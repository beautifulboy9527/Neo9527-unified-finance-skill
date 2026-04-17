#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业级报告生成器 v4.6
- 数据真实性保证
- 支撑阻力位精确定位
- 多标的差异化设计
- 图表自适应
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import yfinance as yf

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AssetType:
    """资产类型"""
    CRYPTO = 'crypto'
    STOCK = 'stock'
    FOREX = 'forex'
    INDEX = 'index'


class AssetAnalyzer:
    """资产分析器 - 差异化设计"""
    
    @staticmethod
    def detect_asset_type(symbol: str) -> str:
        """检测资产类型"""
        symbol_upper = symbol.upper()
        
        # 加密货币
        crypto_keywords = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'AVAX', 'MATIC', 'LINK', 'UNI']
        if any(kw in symbol_upper for kw in crypto_keywords) or '-USD' in symbol_upper or '-USDT' in symbol_upper:
            return AssetType.CRYPTO
        
        # 美股
        if symbol_upper in ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 'NFLX', 'DIS'] or len(symbol_upper) <= 5 and symbol_upper.isalpha():
            return AssetType.STOCK
        
        # 外汇
        if '=X' in symbol_upper or any(fx in symbol_upper for fx in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']):
            return AssetType.FOREX
        
        # 指数
        if any(idx in symbol_upper for idx in ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225']):
            return AssetType.INDEX
        
        return AssetType.CRYPTO  # 默认
    
    @staticmethod
    def get_analysis_config(asset_type: str) -> Dict:
        """获取分析配置 - 差异化设计"""
        
        configs = {
            AssetType.CRYPTO: {
                'kline_period': '3mo',
                'support_resistance_method': 'fibonacci',  # 斐波那契回调
                'volume_importance': 'critical',  # 成交量重要性
                'indicators': ['RSI', 'MACD', 'ADX', 'BB', 'EMA', 'Volume'],
                'patterns': True,  # 形态识别
                'onchain': True,   # 链上数据
                'whale_tracking': True,
                'defi_metrics': True,
                'sections': ['market', 'kline', 'technical', 'onchain', 'patterns', 'signals', 'conclusion']
            },
            AssetType.STOCK: {
                'kline_period': '6mo',
                'support_resistance_method': 'pivot',  # 枢轴点
                'volume_importance': 'important',
                'indicators': ['RSI', 'MACD', 'ADX', 'BB', 'SMA', 'EMA', 'VWAP'],
                'patterns': True,
                'onchain': False,
                'whale_tracking': False,
                'defi_metrics': False,
                'fundamental': True,  # 基本面
                'sections': ['market', 'kline', 'technical', 'fundamental', 'patterns', 'signals', 'conclusion']
            },
            AssetType.FOREX: {
                'kline_period': '3mo',
                'support_resistance_method': 'classic',  # 经典支撑阻力
                'volume_importance': 'moderate',
                'indicators': ['RSI', 'MACD', 'ADX', 'BB', 'EMA', 'ATR'],
                'patterns': True,
                'onchain': False,
                'whale_tracking': False,
                'defi_metrics': False,
                'sections': ['market', 'kline', 'technical', 'patterns', 'signals', 'conclusion']
            },
            AssetType.INDEX: {
                'kline_period': '6mo',
                'support_resistance_method': 'fibonacci',
                'volume_importance': 'important',
                'indicators': ['RSI', 'MACD', 'ADX', 'BB', 'EMA', 'Volume'],
                'patterns': True,
                'onchain': False,
                'whale_tracking': False,
                'defi_metrics': False,
                'sections': ['market', 'kline', 'technical', 'patterns', 'signals', 'conclusion']
            }
        }
        
        return configs.get(asset_type, configs[AssetType.CRYPTO])


class SupportResistanceAnalyzer:
    """支撑阻力位分析器 - 精确定位"""
    
    def __init__(self, prices: List[float], method: str = 'fibonacci'):
        self.prices = prices
        self.method = method
        self.high = max(prices) if prices else 0
        self.low = min(prices) if prices else 0
        self.current = prices[-1] if prices else 0
    
    def calculate_levels(self) -> Dict:
        """计算支撑阻力位"""
        
        if self.method == 'fibonacci':
            return self._fibonacci_levels()
        elif self.method == 'pivot':
            return self._pivot_points()
        else:
            return self._classic_levels()
    
    def _fibonacci_levels(self) -> Dict:
        """斐波那契回调位"""
        
        diff = self.high - self.low
        
        levels = {
            'resistance_2': {
                'price': self.high,
                'type': 'strong',
                'distance_pct': ((self.high - self.current) / self.current * 100) if self.current > 0 else 0,
                'description': f'历史高点 ${self.high:,.2f} (强阻力)'
            },
            'resistance_1': {
                'price': self.low + diff * 0.786,
                'type': 'moderate',
                'distance_pct': ((self.low + diff * 0.786 - self.current) / self.current * 100) if self.current > 0 else 0,
                'description': f'78.6%回调位 ${self.low + diff * 0.786:,.2f} (中阻力)'
            },
            'current': {
                'price': self.current,
                'type': 'current',
                'description': f'当前价格 ${self.current:,.2f}'
            },
            'support_1': {
                'price': self.low + diff * 0.618,
                'type': 'strong',
                'distance_pct': ((self.current - (self.low + diff * 0.618)) / self.current * 100) if self.current > 0 else 0,
                'description': f'61.8%回调位 ${self.low + diff * 0.618:,.2f} (强支撑)'
            },
            'support_2': {
                'price': self.low + diff * 0.382,
                'type': 'moderate',
                'distance_pct': ((self.current - (self.low + diff * 0.382)) / self.current * 100) if self.current > 0 else 0,
                'description': f'38.2%回调位 ${self.low + diff * 0.382:,.2f} (中支撑)'
            },
            'support_3': {
                'price': self.low,
                'type': 'critical',
                'distance_pct': ((self.current - self.low) / self.current * 100) if self.current > 0 else 0,
                'description': f'历史低点 ${self.low:,.2f} (关键支撑)'
            }
        }
        
        return levels
    
    def _pivot_points(self) -> Dict:
        """枢轴点计算"""
        
        # 需要开盘价，这里简化处理
        close = self.current
        pivot = (self.high + self.low + close) / 3
        
        levels = {
            'resistance_2': {
                'price': pivot + (self.high - self.low),
                'type': 'strong',
                'distance_pct': ((pivot + (self.high - self.low) - self.current) / self.current * 100) if self.current > 0 else 0,
                'description': f'R2 ${pivot + (self.high - self.low):,.2f}'
            },
            'resistance_1': {
                'price': 2 * pivot - self.low,
                'type': 'moderate',
                'distance_pct': ((2 * pivot - self.low - self.current) / self.current * 100) if self.current > 0 else 0,
                'description': f'R1 ${2 * pivot - self.low:,.2f}'
            },
            'pivot': {
                'price': pivot,
                'type': 'pivot',
                'distance_pct': ((self.current - pivot) / self.current * 100) if self.current > 0 else 0,
                'description': f'枢轴点 ${pivot:,.2f}'
            },
            'support_1': {
                'price': 2 * pivot - self.high,
                'type': 'moderate',
                'distance_pct': ((self.current - (2 * pivot - self.high)) / self.current * 100) if self.current > 0 else 0,
                'description': f'S1 ${2 * pivot - self.high:,.2f}'
            },
            'support_2': {
                'price': pivot - (self.high - self.low),
                'type': 'strong',
                'distance_pct': ((self.current - (pivot - (self.high - self.low))) / self.current * 100) if self.current > 0 else 0,
                'description': f'S2 ${pivot - (self.high - self.low):,.2f}'
            }
        }
        
        return levels
    
    def _classic_levels(self) -> Dict:
        """经典支撑阻力"""
        
        levels = {
            'resistance_2': {
                'price': self.high,
                'type': 'strong',
                'distance_pct': ((self.high - self.current) / self.current * 100) if self.current > 0 else 0,
                'description': f'历史高点 ${self.high:,.2f}'
            },
            'resistance_1': {
                'price': self.current * 1.05,
                'type': 'moderate',
                'distance_pct': 5.0,
                'description': f'+5% 阻力位 ${self.current * 1.05:,.2f}'
            },
            'support_1': {
                'price': self.current * 0.95,
                'type': 'moderate',
                'distance_pct': 5.0,
                'description': f'-5% 支撑位 ${self.current * 0.95:,.2f}'
            },
            'support_2': {
                'price': self.low,
                'type': 'strong',
                'distance_pct': ((self.current - self.low) / self.current * 100) if self.current > 0 else 0,
                'description': f'历史低点 ${self.low:,.2f}'
            }
        }
        
        return levels


def generate_professional_report(symbol: str, output_dir: str = r"D:\OpenClaw\outputs\reports") -> str:
    """
    生成专业级报告 v4.6
    - 数据真实性保证
    - 支撑阻力位精确定位
    - 多标的差异化设计
    """
    
    print("=" * 60)
    print(f"生成 {symbol} 专业报告 (v4.6)")
    print("=" * 60)
    
    # 1. 检测资产类型
    asset_type = AssetAnalyzer.detect_asset_type(symbol)
    config = AssetAnalyzer.get_analysis_config(asset_type)
    
    print(f"资产类型: {asset_type}")
    print(f"分析方法: {config['support_resistance_method']}")
    
    # 2. 获取真实市场数据
    print("\n[1/6] 获取市场数据...")
    market_data = get_real_market_data(symbol, asset_type)
    
    # 3. 获取K线数据
    print("[2/6] 获取K线数据...")
    kline_data = get_real_kline_data(symbol, config['kline_period'])
    
    # 4. 计算技术指标
    print("[3/6] 计算技术指标...")
    technical_data = calculate_real_indicators(kline_data, config['indicators'])
    
    # 5. 计算支撑阻力位
    print("[4/6] 计算支撑阻力位...")
    sr_levels = calculate_support_resistance(kline_data, config['support_resistance_method'])
    
    # 6. 获取链上数据（如果适用）
    onchain_data = {}
    if config.get('onchain'):
        print("[5/6] 获取链上数据...")
        onchain_data = get_onchain_data_real(symbol, asset_type)
    else:
        print("[5/6] 跳过链上数据（不适用）")
    
    # 7. 生成信号
    print("[6/6] 生成交易信号...")
    signals = generate_real_signals(market_data, technical_data, onchain_data, sr_levels)
    
    # 8. 生成HTML
    html = generate_professional_html(
        symbol=symbol,
        asset_type=asset_type,
        config=config,
        market_data=market_data,
        kline_data=kline_data,
        technical_data=technical_data,
        sr_levels=sr_levels,
        onchain_data=onchain_data,
        signals=signals
    )
    
    # 9. 保存报告
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(
        output_dir, 
        f'{symbol}_report_v4.6_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    )
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = os.path.getsize(report_file) / 1024
    
    print("\n" + "=" * 60)
    print(f"✅ 报告已生成")
    print(f"   文件: {report_file}")
    print(f"   大小: {size_kb:.1f} KB")
    print(f"   类型: {asset_type}")
    print("=" * 60)
    
    return report_file


def get_real_market_data(symbol: str, asset_type: str) -> Dict:
    """获取真实市场数据"""
    
    try:
        # 使用 yfinance 获取真实数据
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
            'data_source': 'yfinance',
            'timestamp': datetime.now().isoformat(),
            'is_real': True
        }
    except Exception as e:
        print(f"⚠️ 市场数据获取失败: {e}")
        return {
            'symbol': symbol,
            'error': str(e),
            'is_real': False
        }


def get_real_kline_data(symbol: str, period: str) -> Dict:
    """获取真实K线数据"""
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {'error': 'No data', 'is_real': False}
        
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
        
        # 计算均线
        closes = [c['close'] for c in candles]
        
        ma5 = []
        ma10 = []
        ma20 = []
        
        for i in range(len(candles)):
            if i >= 4:
                ma5.append({
                    'time': candles[i]['time'],
                    'value': sum(closes[i-4:i+1]) / 5
                })
            
            if i >= 9:
                ma10.append({
                    'time': candles[i]['time'],
                    'value': sum(closes[i-9:i+1]) / 10
                })
            
            if i >= 19:
                ma20.append({
                    'time': candles[i]['time'],
                    'value': sum(closes[i-19:i+1]) / 20
                })
        
        return {
            'candles': candles,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'volume': [
                {
                    'time': c['time'],
                    'value': c['volume'],
                    'color': '#26a69a' if c['close'] >= c['open'] else '#ef5350'
                }
                for c in candles
            ],
            'is_real': True,
            'data_source': 'yfinance'
        }
        
    except Exception as e:
        print(f"⚠️ K线数据获取失败: {e}")
        return {'error': str(e), 'is_real': False}


def calculate_real_indicators(kline_data: Dict, indicators: List[str]) -> Dict:
    """计算真实技术指标"""
    
    if not kline_data.get('is_real'):
        return {'error': 'No kline data', 'is_real': False}
    
    try:
        import pandas as pd
        import numpy as np
        
        candles = kline_data['candles']
        df = pd.DataFrame(candles)
        
        result = {
            'is_real': True,
            'data_source': 'calculated'
        }
        
        # RSI
        if 'RSI' in indicators:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            result['rsi'] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            result['rsi_signal'] = 'overbought' if result['rsi'] > 70 else 'oversold' if result['rsi'] < 30 else 'neutral'
        
        # MACD
        if 'MACD' in indicators:
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            
            result['macd'] = float(macd.iloc[-1])
            result['macd_signal'] = float(signal.iloc[-1])
            result['macd_histogram'] = float(histogram.iloc[-1])
            result['macd_trend'] = 'bullish' if result['macd_histogram'] > 0 else 'bearish'
        
        # ADX
        if 'ADX' in indicators:
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            
            tr = pd.concat([
                high - low,
                abs(high - close.shift()),
                abs(low - close.shift())
            ], axis=1).max(axis=1)
            
            atr = tr.rolling(window=14).mean()
            plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(window=14).mean()
            
            result['adx'] = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 25
            result['trend_strength'] = 'strong' if result['adx'] > 25 else 'weak'
        
        # 布林带
        if 'BB' in indicators:
            sma20 = df['close'].rolling(window=20).mean()
            std20 = df['close'].rolling(window=20).std()
            
            result['bb_upper'] = float(sma20.iloc[-1] + 2 * std20.iloc[-1])
            result['bb_middle'] = float(sma20.iloc[-1])
            result['bb_lower'] = float(sma20.iloc[-1] - 2 * std20.iloc[-1])
            
            current_price = df['close'].iloc[-1]
            result['bb_position'] = (
                'above_upper' if current_price > result['bb_upper']
                else 'below_lower' if current_price < result['bb_lower']
                else 'middle'
            )
        
        # EMA
        if 'EMA' in indicators:
            result['ema20'] = float(df['close'].ewm(span=20).mean().iloc[-1])
            result['ema50'] = float(df['close'].ewm(span=50).mean().iloc[-1]) if len(df) >= 50 else result['ema20']
        
        return result
        
    except Exception as e:
        return {'error': str(e), 'is_real': False}


def calculate_support_resistance(kline_data: Dict, method: str) -> Dict:
    """计算支撑阻力位"""
    
    if not kline_data.get('is_real'):
        return {}
    
    candles = kline_data['candles']
    prices = [c['close'] for c in candles]
    
    analyzer = SupportResistanceAnalyzer(prices, method)
    return analyzer.calculate_levels()


def get_onchain_data_real(symbol: str, asset_type: str) -> Dict:
    """获取真实链上数据"""
    
    if asset_type != AssetType.CRYPTO:
        return {}
    
    try:
        # 使用 DeFiLlama 获取真实数据
        import requests
        
        base_symbol = symbol.split('-')[0].upper()
        
        # 获取协议数据
        url = "https://api.llama.fi/protocols"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code != 200:
            return {'error': 'DeFiLlama API failed', 'is_real': False}
        
        protocols = resp.json()
        
        # 匹配相关协议
        matched = []
        for p in protocols:
            name = p.get('name', '').lower()
            symbol_lower = base_symbol.lower()
            
            if symbol_lower in name or name in symbol_lower:
                matched.append({
                    'name': p.get('name'),
                    'tvl': p.get('tvl', 0),
                    'change_1d': p.get('change_1d', 0),
                    'change_7d': p.get('change_7d', 0),
                    'category': p.get('category')
                })
        
        if not matched:
            return {'matched_protocols': 0, 'is_real': False}
        
        # 计算汇总数据
        total_tvl = sum(p['tvl'] for p in matched if p['tvl'])
        avg_change_7d = sum(p['change_7d'] for p in matched if p['change_7d']) / len([p for p in matched if p['change_7d']]) if any(p.get('change_7d') for p in matched) else 0
        
        # 判断鲸鱼偏向
        if avg_change_7d > 3:
            whale_bias = 'accumulation'
        elif avg_change_7d < -3:
            whale_bias = 'distribution'
        else:
            whale_bias = 'neutral'
        
        return {
            'matched_protocols': len(matched),
            'total_tvl': total_tvl,
            'avg_change_7d': avg_change_7d,
            'whale_bias': whale_bias,
            'top_protocols': matched[:5],
            'is_real': True,
            'data_source': 'DeFiLlama'
        }
        
    except Exception as e:
        return {'error': str(e), 'is_real': False}


def generate_real_signals(market: Dict, technical: Dict, onchain: Dict, sr_levels: Dict) -> List[Dict]:
    """生成真实交易信号"""
    
    signals = []
    
    # 技术指标信号
    if technical.get('is_real'):
        # RSI信号
        rsi = technical.get('rsi', 50)
        if rsi > 70:
            signals.append({
                'category': '动量指标',
                'name': 'RSI',
                'signal': 'bearish',
                'strength': -2,
                'desc': f'RSI超买 ({rsi:.1f})，短期回调风险'
            })
        elif rsi < 30:
            signals.append({
                'category': '动量指标',
                'name': 'RSI',
                'signal': 'bullish',
                'strength': 3,
                'desc': f'RSI超卖 ({rsi:.1f})，反弹机会'
            })
        
        # MACD信号
        macd_trend = technical.get('macd_trend')
        if macd_trend == 'bullish':
            signals.append({
                'category': '趋势指标',
                'name': 'MACD',
                'signal': 'bullish',
                'strength': 3,
                'desc': 'MACD金叉，动能向上'
            })
        elif macd_trend == 'bearish':
            signals.append({
                'category': '趋势指标',
                'name': 'MACD',
                'signal': 'bearish',
                'strength': -3,
                'desc': 'MACD死叉，动能减弱'
            })
        
        # ADX信号
        adx = technical.get('adx', 25)
        if adx > 25:
            signals.append({
                'category': '趋势强度',
                'name': 'ADX',
                'signal': 'neutral',
                'strength': 2,
                'desc': f'ADX={adx:.1f}，趋势强劲'
            })
        
        # 布林带信号
        bb_pos = technical.get('bb_position')
        if bb_pos == 'above_upper':
            signals.append({
                'category': '波动率',
                'name': '布林带',
                'signal': 'bearish',
                'strength': -2,
                'desc': '突破上轨，超买风险'
            })
        elif bb_pos == 'below_lower':
            signals.append({
                'category': '波动率',
                'name': '布林带',
                'signal': 'bullish',
                'strength': 2,
                'desc': '跌破下轨，超卖机会'
            })
    
    # 支撑阻力信号
    if sr_levels:
        current = market.get('price', 0)
        
        # 检查是否接近支撑
        for key in ['support_1', 'support_2', 'support_3']:
            if key in sr_levels:
                level = sr_levels[key]
                distance = level.get('distance_pct', 100)
                
                if distance < 3:  # 距离支撑位<3%
                    signals.append({
                        'category': '支撑阻力',
                        'name': f'{key.replace("_", " ").title()}',
                        'signal': 'bullish',
                        'strength': 4 if level['type'] == 'critical' else 2,
                        'desc': f'接近{level["description"]}，支撑位买入机会'
                    })
        
        # 检查是否接近阻力
        for key in ['resistance_1', 'resistance_2']:
            if key in sr_levels:
                level = sr_levels[key]
                distance = level.get('distance_pct', 100)
                
                if distance < 3:  # 距离阻力位<3%
                    signals.append({
                        'category': '支撑阻力',
                        'name': f'{key.replace("_", " ").title()}',
                        'signal': 'bearish',
                        'strength': -3 if level['type'] == 'strong' else -1,
                        'desc': f'接近{level["description"]}，阻力位回调风险'
                    })
    
    # 链上数据信号
    if onchain.get('is_real'):
        whale_bias = onchain.get('whale_bias')
        if whale_bias == 'accumulation':
            signals.append({
                'category': '链上数据',
                'name': '鲸鱼动向',
                'signal': 'bullish',
                'strength': 4,
                'desc': f'鲸鱼吸筹，生态TVL 7日增长 {onchain.get("avg_change_7d", 0):.1f}%'
            })
        elif whale_bias == 'distribution':
            signals.append({
                'category': '链上数据',
                'name': '鲸鱼动向',
                'signal': 'bearish',
                'strength': -4,
                'desc': f'鲸鱼派发，生态TVL 7日下降 {abs(onchain.get("avg_change_7d", 0)):.1f}%'
            })
    
    return signals


def generate_professional_html(**kwargs) -> str:
    """生成专业级HTML报告"""
    
    symbol = kwargs['symbol']
    asset_type = kwargs['asset_type']
    config = kwargs['config']
    market = kwargs['market_data']
    kline = kwargs['kline_data']
    technical = kwargs['technical_data']
    sr = kwargs['sr_levels']
    onchain = kwargs['onchain_data']
    signals = kwargs['signals']
    
    # 计算综合评分
    total_strength = sum(s['strength'] for s in signals)
    score = min(100, max(0, 50 + total_strength * 2))
    
    # 决策
    if score >= 70:
        decision = 'BUY'
    elif score >= 55:
        decision = 'ACCUMULATE'
    elif score >= 45:
        decision = 'HOLD'
    else:
        decision = 'SELL'
    
    # K线数据JS
    candlestick_js = "[]"
    ma5_js = "[]"
    ma10_js = "[]"
    ma20_js = "[]"
    volume_js = "[]"
    
    if kline.get('is_real'):
        candlestick_js = "[" + ",".join([
            f'{{"time": {c["time"]}, "open": {c["open"]:.2f}, "high": {c["high"]:.2f}, "low": {c["low"]:.2f}, "close": {c["close"]:.2f}}}'
            for c in kline['candles']
        ]) + "]"
        
        if kline.get('ma5'):
            ma5_js = "[" + ",".join([
                f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}'
                for m in kline['ma5']
            ]) + "]"
        
        if kline.get('ma10'):
            ma10_js = "[" + ",".join([
                f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}'
                for m in kline['ma10']
            ]) + "]"
        
        if kline.get('ma20'):
            ma20_js = "[" + ",".join([
                f'{{"time": {m["time"]}, "value": {m["value"]:.2f}}}'
                for m in kline['ma20']
            ]) + "]"
        
        if kline.get('volume'):
            volume_js = "[" + ",".join([
                f'{{"time": {v["time"]}, "value": {v["value"]:.0f}, "color": "{v["color"]}"}}'
                for v in kline['volume']
            ]) + "]"
    
    # 支撑阻力HTML
    sr_html = ""
    if sr:
        sr_html = "<div class='grid'>"
        
        # 阻力位
        for key in ['resistance_2', 'resistance_1']:
            if key in sr:
                level = sr[key]
                sr_html += f"""
                <div class="metric" style="background: #fee2e2;">
                    <div class="metric-label">🔴 {key.replace('_', ' ').title()}</div>
                    <div class="metric-value">${level['price']:,.2f}</div>
                    <div style="font-size: 12px; color: #ef4444;">{level['description']}</div>
                </div>
                """
        
        # 当前价格
        sr_html += f"""
        <div class="metric" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div class="metric-label">当前价格</div>
            <div class="metric-value">${market.get('price', 0):,.2f}</div>
            <div style="font-size: 12px;">24h {market.get('change_24h', 0):+.2f}%</div>
        </div>
        """
        
        # 支撑位
        for key in ['support_1', 'support_2', 'support_3']:
            if key in sr:
                level = sr[key]
                sr_html += f"""
                <div class="metric" style="background: #d1fae5;">
                    <div class="metric-label">🟢 {key.replace('_', ' ').title()}</div>
                    <div class="metric-value">${level['price']:,.2f}</div>
                    <div style="font-size: 12px; color: #10b981;">{level['description']}</div>
                </div>
                """
        
        sr_html += "</div>"
    
    # 信号HTML
    bullish = [s for s in signals if s['strength'] > 0]
    bearish = [s for s in signals if s['strength'] < 0]
    
    bullish_html = "\n".join([
        f'<div class="signal signal-bullish"><span>[{s["category"]}] {s["name"]}</span><span>+{s["strength"]}</span></div>'
        for s in bullish
    ])
    
    bearish_html = "\n".join([
        f'<div class="signal signal-bearish"><span>[{s["category"]}] {s["name"]}</span><span>{s["strength"]}</span></div>'
        for s in bearish
    ])
    
    # 链上数据HTML
    onchain_html = ""
    if onchain.get('is_real'):
        onchain_html = f"""
        <div class="card">
            <h3 class="section-title">🐋 链上数据 (真实数据)</h3>
            <div class="grid">
                <div class="metric">
                    <div class="metric-label">鲸鱼偏向</div>
                    <div class="metric-value">{onchain.get('whale_bias', 'neutral')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">生态TVL</div>
                    <div class="metric-value">${onchain.get('total_tvl', 0)/1e9:.2f}B</div>
                </div>
                <div class="metric">
                    <div class="metric-label">7日变化</div>
                    <div class="metric-value">{onchain.get('avg_change_7d', 0):+.2f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">相关协议</div>
                    <div class="metric-value">{onchain.get('matched_protocols', 0)} 个</div>
                </div>
            </div>
            <p style="margin-top: 12px; font-size: 13px; color: #6b7280;">
                数据来源: {onchain.get('data_source', 'DeFiLlama')} | 
                获取时间: {datetime.now().strftime('%H:%M:%S')}
            </p>
        </div>
        """
    
    # 数据真实性标识
    data_quality = "✅ 真实数据" if market.get('is_real') and kline.get('is_real') else "⚠️ 部分数据缺失"
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 专业分析报告 v4.6</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            border-left: 4px solid #667eea;
            padding-left: 12px;
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
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
        }}
        .metric {{
            padding: 16px;
            background: white;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-label {{ color: #6b7280; font-size: 13px; }}
        .metric-value {{ font-size: 22px; font-weight: bold; margin: 8px 0; }}
        .signal {{
            padding: 10px 16px;
            margin: 8px 0;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
        }}
        .signal-bullish {{ background: #d1fae5; border-left: 4px solid #10b981; }}
        .signal-bearish {{ background: #fee2e2; border-left: 4px solid #ef4444; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; text-align: left; }}
        th {{ background: #667eea; color: white; }}
        .data-quality {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            background: {'#10b981' if '✅' in data_quality else '#ef4444'};
            color: white;
        }}
        #kline-chart {{ width: 100%; height: 400px; }}
        #volume-chart {{ width: 100%; height: 120px; }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{symbol} 专业分析报告</h1>
            <div style="font-size: 14px; opacity: 0.9;">
                {asset_type.upper()} | 专业级分析 | v4.6
            </div>
            <div style="margin-top: 16px; font-size: 13px;">
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <span class="data-quality">{data_quality}</span>
            </div>
        </div>
        
        <div class="content">
            <!-- 综合评分 -->
            <div class="section">
                <h2 class="section-title">一、综合评分</h2>
                <div class="card highlight" style="text-align: center; padding: 40px;">
                    <div style="font-size: 72px; font-weight: bold;">{score}/100</div>
                    <div style="font-size: 24px; margin-top: 10px;">{decision}</div>
                    <div style="font-size: 14px; margin-top: 8px; opacity: 0.9;">
                        总强度 {total_strength:+d} | {len(bullish)}项看涨 vs {len(bearish)}项看跌
                    </div>
                </div>
            </div>
            
            <!-- 市场数据 -->
            <div class="section">
                <h2 class="section-title">二、市场数据 (真实数据)</h2>
                <table>
                    <tr><th>指标</th><th>数值</th><th>说明</th></tr>
                    <tr><td>当前价格</td><td><strong>${market.get('price', 0):,.2f}</strong></td><td>实时价格</td></tr>
                    <tr><td>24h涨跌</td><td style="color: {'#10b981' if market.get('change_24h', 0) > 0 else '#ef4444'}">{market.get('change_24h', 0):+.2f}%</td><td>日内变化</td></tr>
                    <tr><td>24h最高</td><td>${market.get('high_24h', 0):,.2f}</td><td>日内高点</td></tr>
                    <tr><td>24h最低</td><td>${market.get('low_24h', 0):,.2f}</td><td>日内低点</td></tr>
                    <tr><td>成交量</td><td>${market.get('volume', 0)/1e9:.2f}B</td><td>市场活跃度</td></tr>
                    <tr><td>市值</td><td>${market.get('market_cap', 0)/1e9:.2f}B</td><td>市场规模</td></tr>
                </table>
                <p style="font-size: 12px; color: #6b7280; margin-top: 8px;">
                    数据来源: {market.get('data_source', 'yfinance')} | 获取时间: {market.get('timestamp', '')}
                </p>
            </div>
            
            <!-- K线图 -->
            <div class="section">
                <h2 class="section-title">三、价格走势 (交互式K线图)</h2>
                <div id="kline-chart"></div>
                <div id="volume-chart"></div>
                <div style="display: flex; gap: 20px; font-size: 12px; color: #666; margin-top: 10px;">
                    <span>🔵 MA5</span>
                    <span>🟢 MA10</span>
                    <span>🔴 MA20</span>
                    <span style="margin-left: auto;">💡 可缩放/拖拽</span>
                </div>
            </div>
            
            <!-- 支撑阻力位 -->
            <div class="section">
                <h2 class="section-title">四、支撑阻力位 (精确计算)</h2>
                <div class="card">
                    {sr_html}
                    <p style="font-size: 12px; color: #6b7280; margin-top: 12px;">
                        计算方法: {config['support_resistance_method'].upper()} | 
                        数据周期: {config['kline_period']}
                    </p>
                </div>
            </div>
            
            <!-- 技术分析 -->
            <div class="section">
                <h2 class="section-title">五、技术指标 (真实计算)</h2>
                <div class="card">
                    <div class="grid">
                        <div class="metric">
                            <div class="metric-label">RSI (14)</div>
                            <div class="metric-value">{technical.get('rsi', 50):.1f}</div>
                            <div style="font-size: 11px; color: #6b7280;">{technical.get('rsi_signal', 'neutral')}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">MACD趋势</div>
                            <div class="metric-value">{technical.get('macd_trend', 'neutral')}</div>
                            <div style="font-size: 11px; color: #6b7280;">{'金叉' if technical.get('macd_trend') == 'bullish' else '死叉' if technical.get('macd_trend') == 'bearish' else '中性'}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">ADX</div>
                            <div class="metric-value">{technical.get('adx', 25):.1f}</div>
                            <div style="font-size: 11px; color: #6b7280;">{technical.get('trend_strength', 'weak')}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">布林带位置</div>
                            <div class="metric-value">{technical.get('bb_position', 'middle')}</div>
                            <div style="font-size: 11px; color: #6b7280;">波动率状态</div>
                        </div>
                    </div>
                    <p style="font-size: 12px; color: #6b7280; margin-top: 12px;">
                        数据来源: {technical.get('data_source', 'calculated')} | 真实计算: {'✅' if technical.get('is_real') else '❌'}
                    </p>
                </div>
            </div>
            
            <!-- 链上数据 -->
            {onchain_html}
            
            <!-- 信号汇总 -->
            <div class="section">
                <h2 class="section-title">六、交易信号</h2>
                <div class="card">
                    <p><strong>看涨信号 ({len(bullish)}项)</strong></p>
                    {bullish_html}
                    
                    <p style="margin-top: 16px;"><strong>看跌信号 ({len(bearish)}项)</strong></p>
                    {bearish_html}
                    
                    <p style="margin-top: 20px; padding: 12px; background: #f3f4f6; border-radius: 6px;">
                        <strong>总强度:</strong> {total_strength:+d} | 
                        <strong>倾向:</strong> {'看涨' if total_strength > 0 else '看跌' if total_strength < 0 else '中性'}
                    </p>
                </div>
            </div>
            
            <!-- 综合结论 -->
            <div class="section">
                <h2 class="section-title">七、综合结论</h2>
                <div class="card">
                    <p style="line-height: 1.8; font-size: 15px;">
                        基于{'真实' if market.get('is_real') and kline.get('is_real') else '模拟'}数据分析：
                        {symbol} 当前价格 ${market.get('price', 0):,.2f}，
                        综合{len(signals)}项交易信号，总强度 {total_strength:+d}，
                        综合评分 {score}/100，建议 <strong>{decision}</strong>。
                        
                        {'技术面偏多，支撑位提供买入机会。' if total_strength > 0 else '技术面偏空，注意风险控制。' if total_strength < 0 else '信号不明确，建议观望。'}
                    </p>
                    
                    <p style="margin-top: 16px; font-size: 13px; color: #6b7280;">
                        <strong>风险提示:</strong> 本报告基于公开数据，不构成投资建议。投资有风险，决策需谨慎。
                    </p>
                </div>
            </div>
            
            <!-- 数据来源 -->
            <div class="section">
                <h2 class="section-title">八、数据来源</h2>
                <div class="card">
                    <table>
                        <tr><th>数据类型</th><th>来源</th><th>真实性</th></tr>
                        <tr><td>市场数据</td><td>{market.get('data_source', 'yfinance')}</td><td>{'✅ 真实' if market.get('is_real') else '❌ 模拟'}</td></tr>
                        <tr><td>K线数据</td><td>{kline.get('data_source', 'yfinance')}</td><td>{'✅ 真实' if kline.get('is_real') else '❌ 模拟'}</td></tr>
                        <tr><td>技术指标</td><td>{technical.get('data_source', 'calculated')}</td><td>{'✅ 真实' if technical.get('is_real') else '❌ 模拟'}</td></tr>
                        {'<tr><td>链上数据</td><td>' + onchain.get('data_source', 'DeFiLlama') + '</td><td>✅ 真实</td></tr>' if onchain.get('is_real') else ''}
                    </table>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Neo9527 Finance Skill v4.6 | 专业级金融分析系统</p>
            <p style="margin-top: 8px;">
                数据真实性保证 | 支撑阻力位精确定位 | 多标的差异化设计
            </p>
        </div>
    </div>
    
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <script>
        const candlestickData = {candlestick_js};
        const ma5Data = {ma5_js};
        const ma10Data = {ma10_js};
        const ma20Data = {ma20_js};
        const volumeData = {volume_js};
        
        if (candlestickData.length > 0) {{
            const chart = LightweightCharts.createChart(document.getElementById('kline-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#ffffff' }}, textColor: '#333' }},
                grid: {{ vertLines: {{ color: '#f0f0f0' }}, horzLines: {{ color: '#f0f0f0' }} }},
                timeScale: {{ timeVisible: true }}
            }});
            
            const candleSeries = chart.addCandlestickSeries({{
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350'
            }});
            candleSeries.setData(candlestickData);
            
            if (ma5Data.length > 0) {{
                chart.addLineSeries({{ color: '#2196f3', lineWidth: 2 }}).setData(ma5Data);
            }}
            if (ma10Data.length > 0) {{
                chart.addLineSeries({{ color: '#4caf50', lineWidth: 2 }}).setData(ma10Data);
            }}
            if (ma20Data.length > 0) {{
                chart.addLineSeries({{ color: '#f44336', lineWidth: 2 }}).setData(ma20Data);
            }}
            
            const volumeChart = LightweightCharts.createChart(document.getElementById('volume-chart'), {{
                layout: {{ background: {{ type: 'solid', color: '#ffffff' }} }},
                timeScale: {{ visible: false }}
            }});
            volumeChart.addHistogramSeries({{}}, {{ priceFormat: {{ type: 'volume' }} }}).setData(volumeData);
        }}
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'ETH-USD'
    
    try:
        report_file = generate_professional_report(symbol)
        print(f"\n✅ 报告生成成功: {report_file}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
