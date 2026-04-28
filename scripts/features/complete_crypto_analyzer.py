#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币完整数据获取模块
整合: 市场数据 + 技术分析 + 链上数据 + 合约数据
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CompleteCryptoAnalyzer:
    """完整加密货币分析器"""
    
    def __init__(self):
        self.cache = {}
    
    def analyze_all(self, symbol: str) -> Dict:
        """
        全面分析
        
        Returns:
            {
                'market': 市场数据,
                'technical': 技术分析,
                'onchain': 链上数据,
                'futures': 合约数据,
                'patterns': 形态识别,
                'conclusion': 综合结论
            }
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'market': {},
            'technical': {},
            'onchain': {},
            'futures': {},
            'patterns': {},
            'signals': [],
            'conclusion': {}
        }
        
        # 1. 市场数据
        result['market'] = self._get_market_data(symbol)
        
        # 2. 技术分析 (含形态识别)
        result['technical'] = self._get_technical_analysis(symbol)
        result['patterns'] = result['technical'].get('patterns', {})
        
        # 3. 链上数据
        result['onchain'] = self._get_onchain_data(symbol)
        
        # 4. 合约数据
        result['futures'] = self._get_futures_data(symbol)
        
        # 5. 综合信号 (叠buff)
        result['signals'] = self._generate_signals(result)
        
        # 6. 最终结论
        result['conclusion'] = self._generate_conclusion(result)
        
        return result
    
    def _get_market_data(self, symbol: str) -> Dict:
        """获取市场数据"""
        try:
            import requests
            
            # 转换符号: BTC-USD -> bitcoin
            coin_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'SOL': 'solana'
            }
            
            base = symbol.split('-')[0]
            coin_id = coin_ids.get(base, base.lower())
            
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            return {
                'price': data['market_data']['current_price']['usd'],
                'change_24h': data['market_data']['price_change_percentage_24h'],
                'volume_24h': data['market_data']['total_volume']['usd'],
                'market_cap': data['market_data']['market_cap']['usd'],
                'market_cap_rank': data['market_cap_rank'],
                'high_24h': data['market_data']['high_24h']['usd'],
                'low_24h': data['market_data']['low_24h']['usd'],
                'circulating_supply': data['market_data']['circulating_supply'],
                'data_source': 'CoinGecko API'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_technical_analysis(self, symbol: str) -> Dict:
        """获取技术分析 + 形态识别"""
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='6mo')
            
            if hist.empty:
                return {'error': 'No data'}
            
            closes = hist['Close']
            highs = hist['High']
            lows = hist['Low']
            volumes = hist['Volume']
            
            result = {
                'indicators': {},
                'patterns': {}
            }
            
            # 基础指标
            result['indicators']['price'] = float(closes.iloc[-1])
            result['indicators']['ma5'] = float(closes.rolling(5).mean().iloc[-1])
            result['indicators']['ma10'] = float(closes.rolling(10).mean().iloc[-1])
            result['indicators']['ma20'] = float(closes.rolling(20).mean().iloc[-1])
            result['indicators']['ma60'] = float(closes.rolling(60).mean().iloc[-1]) if len(closes) >= 60 else None
            
            # RSI
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            result['indicators']['rsi'] = float((100 - (100 / (1 + rs.iloc[-1]))))
            
            # MACD
            exp1 = closes.ewm(span=12, adjust=False).mean()
            exp2 = closes.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            result['indicators']['macd'] = float(macd.iloc[-1])
            result['indicators']['macd_signal'] = float(signal.iloc[-1])
            result['indicators']['macd_histogram'] = float((macd - signal).iloc[-1])
            
            # Bollinger Bands
            bb_mid = closes.rolling(20).mean()
            bb_std = closes.rolling(20).std()
            result['indicators']['bb_upper'] = float((bb_mid + 2*bb_std).iloc[-1])
            result['indicators']['bb_lower'] = float((bb_mid - 2*bb_std).iloc[-1])
            
            # ADX
            high = highs
            low = lows
            close = closes
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm = plus_dm.where(plus_dm > 0, 0)
            minus_dm = minus_dm.where(minus_dm < 0, 0).abs()
            
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            
            plus_di = 100 * (plus_dm.rolling(14).mean() / (atr + 0.0001))
            minus_di = 100 * (minus_dm.rolling(14).mean() / (atr + 0.0001))
            dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 0.0001)
            adx = dx.rolling(14).mean()
            
            result['indicators']['adx'] = float(adx.iloc[-1])
            result['indicators']['plus_di'] = float(plus_di.iloc[-1])
            result['indicators']['minus_di'] = float(minus_di.iloc[-1])
            
            # 成交量比率
            vol_ma = volumes.rolling(20).mean()
            result['indicators']['volume_ratio'] = float(volumes.iloc[-1] / vol_ma.iloc[-1]) if vol_ma.iloc[-1] > 0 else 1.0
            
            # ========== 形态识别 ==========
            patterns = {}
            
            # 1. 趋势判断
            price = result['indicators']['price']
            ma5 = result['indicators']['ma5']
            ma10 = result['indicators']['ma10']
            ma20 = result['indicators']['ma20']
            
            if price > ma5 > ma10 > ma20:
                patterns['trend'] = 'strong_uptrend'
                patterns['trend_desc'] = '多头排列 (强势上涨)'
            elif price > ma20:
                patterns['trend'] = 'uptrend'
                patterns['trend_desc'] = '上升趋势'
            elif price < ma5 < ma10 < ma20:
                patterns['trend'] = 'strong_downtrend'
                patterns['trend_desc'] = '空头排列 (强势下跌)'
            elif price < ma20:
                patterns['trend'] = 'downtrend'
                patterns['trend_desc'] = '下降趋势'
            else:
                patterns['trend'] = 'sideways'
                patterns['trend_desc'] = '震荡整理'
            
            # 2. 支撑阻力位
            high_20 = highs.iloc[-20:].max()
            low_20 = lows.iloc[-20:].min()
            patterns['resistance'] = float(high_20)
            patterns['support'] = float(low_20)
            patterns['resistance_desc'] = f'阻力位: ${high_20:,.2f} (近20日高点)'
            patterns['support_desc'] = f'支撑位: ${low_20:,.2f} (近20日低点)'
            
            # 3. 头肩形态检测
            if len(closes) >= 30:
                recent = closes.iloc[-30:]
                left_shoulder = recent.iloc[5:10].max()
                head = recent.iloc[10:20].max()
                right_shoulder = recent.iloc[20:25].max()
                
                if head > left_shoulder and head > right_shoulder:
                    if abs(left_shoulder - right_shoulder) / head < 0.05:  # 两肩相近
                        patterns['head_shoulders'] = 'head_and_shoulders_top'
                        patterns['head_shoulders_desc'] = '头肩顶 (看跌形态)'
                    else:
                        patterns['head_shoulders'] = 'potential_top'
                        patterns['head_shoulders_desc'] = '潜在顶部形态'
            
            # 4. 双顶双底检测 (基于日线，检测最近20个交易日)
            # 时间周期: 日线级别
            if len(closes) >= 20:
                recent_highs = highs.iloc[-20:]
                recent_lows = lows.iloc[-20:]
                
                # 查找峰值和谷值
                peaks = []
                for i in range(1, len(recent_highs)-1):
                    if recent_highs.iloc[i] > recent_highs.iloc[i-1] and recent_highs.iloc[i] > recent_highs.iloc[i+1]:
                        peaks.append((i, recent_highs.iloc[i]))
                
                troughs = []
                for i in range(1, len(recent_lows)-1):
                    if recent_lows.iloc[i] < recent_lows.iloc[i-1] and recent_lows.iloc[i] < recent_lows.iloc[i+1]:
                        troughs.append((i, recent_lows.iloc[i]))
                
                # 双顶检测 - 日线级别，最近20个交易日内
                if len(peaks) >= 2:
                    if abs(peaks[-1][1] - peaks[-2][1]) / peaks[-1][1] < 0.02:  # 两顶相差<2%
                        patterns['double_top'] = True
                        patterns['double_top_desc'] = '双顶形态 (日线, 看跌) - 过去20个交易日内两次冲击高点失败'
                
                # 双底检测 - 日线级别，最近20个交易日内
                # 双顶和双底是互斥的，只能存在一个
                if len(troughs) >= 2 and not patterns.get('double_top'):
                    if abs(troughs[-1][1] - troughs[-2][1]) / troughs[-1][1] < 0.02:
                        patterns['double_bottom'] = True
                        patterns['double_bottom_desc'] = '双底形态 (日线, 看涨) - 过去20个交易日内两次下探低点获得支撑'
            
            # 5. RSI形态
            rsi = result['indicators']['rsi']
            if rsi > 70:
                patterns['rsi_signal'] = 'overbought'
                patterns['rsi_desc'] = 'RSI超买 (回调风险)'
            elif rsi < 30:
                patterns['rsi_signal'] = 'oversold'
                patterns['rsi_desc'] = 'RSI超卖 (反弹机会)'
            elif rsi > 60:
                patterns['rsi_signal'] = 'bullish'
                patterns['rsi_desc'] = 'RSI偏强 (多头动能)'
            elif rsi < 40:
                patterns['rsi_signal'] = 'bearish'
                patterns['rsi_desc'] = 'RSI偏弱 (空头动能)'
            
            # 6. MACD形态
            macd_val = result['indicators']['macd']
            signal_val = result['indicators']['macd_signal']
            histogram = result['indicators']['macd_histogram']
            
            if histogram > 0:
                patterns['macd_signal'] = 'bullish'
                patterns['macd_desc'] = 'MACD金叉 (看涨)'
            else:
                patterns['macd_signal'] = 'bearish'
                patterns['macd_desc'] = 'MACD死叉 (看跌)'
            
            # 7. 布林带位置
            bb_upper = result['indicators']['bb_upper']
            bb_lower = result['indicators']['bb_lower']
            
            if price > bb_upper:
                patterns['bb_signal'] = 'breakout_up'
                patterns['bb_desc'] = '突破布林上轨 (强势或回调)'
            elif price < bb_lower:
                patterns['bb_signal'] = 'breakdown'
                patterns['bb_desc'] = '跌破布林下轨 (超卖或加速下跌)'
            else:
                patterns['bb_signal'] = 'range'
                patterns['bb_desc'] = '布林带区间内运行'
            
            result['patterns'] = patterns
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_onchain_data(self, symbol: str) -> Dict:
        """获取链上数据 (简化版，使用公开API)"""
        try:
            # 使用 Blockchain.com 公开API (BTC)
            base = symbol.split('-')[0]
            
            if base == 'BTC':
                import requests
                
                # BTC 链上数据
                url = "https://api.blockchain.info/stats"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                
                return {
                    'hashrate': data.get('hash_rate', 0) / 1e18,  # EH/s
                    'difficulty': data.get('difficulty', 0) / 1e12,  # T
                    'block_size': data.get('block_size', 0) / 1e6,  # MB
                    'total_btc': data.get('totalbc', 0) / 1e8,  # BTC
                    'data_source': 'Blockchain.com API'
                }
            else:
                return {
                    'note': f'{base} 链上数据暂不支持',
                    'data_source': 'N/A'
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_futures_data(self, symbol: str) -> Dict:
        """获取合约数据"""
        return {
            'note': '合约数据需要CCXT + 代理',
            'data_source': 'N/A (API受限)'
        }
    
    def _generate_signals(self, result: Dict) -> List[Dict]:
        """
        生成信号列表 (叠buff逻辑)
        
        Returns:
            [
                {'name': '技术形态', 'signal': 'bullish', 'strength': 3, 'desc': '...'},
                ...
            ]
        """
        signals = []
        
        # 1. 趋势信号
        patterns = result.get('patterns', {})
        trend = patterns.get('trend', '')
        
        if trend in ['strong_uptrend']:
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': '强烈看涨',
                'strength': 5,
                'desc': patterns.get('trend_desc', '')
            })
        elif trend == 'uptrend':
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': '看涨',
                'strength': 3,
                'desc': patterns.get('trend_desc', '')
            })
        elif trend in ['strong_downtrend']:
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': '强烈看跌',
                'strength': -5,
                'desc': patterns.get('trend_desc', '')
            })
        elif trend == 'downtrend':
            signals.append({
                'category': '技术形态',
                'name': '趋势',
                'signal': '看跌',
                'strength': -3,
                'desc': patterns.get('trend_desc', '')
            })
        
        # 2. RSI信号
        rsi_signal = patterns.get('rsi_signal', '')
        if rsi_signal == 'oversold':
            signals.append({
                'category': '动量指标',
                'name': 'RSI',
                'signal': '超卖反弹',
                'strength': 3,
                'desc': patterns.get('rsi_desc', '')
            })
        elif rsi_signal == 'overbought':
            signals.append({
                'category': '动量指标',
                'name': 'RSI',
                'signal': '超买回调',
                'strength': -2,
                'desc': patterns.get('rsi_desc', '')
            })
        elif rsi_signal == 'bullish':
            signals.append({
                'category': '动量指标',
                'name': 'RSI',
                'signal': '偏强',
                'strength': 2,
                'desc': patterns.get('rsi_desc', '')
            })
        
        # 3. MACD信号
        macd_signal = patterns.get('macd_signal', '')
        if macd_signal == 'bullish':
            signals.append({
                'category': '趋势指标',
                'name': 'MACD',
                'signal': '金叉看涨',
                'strength': 3,
                'desc': patterns.get('macd_desc', '')
            })
        else:
            signals.append({
                'category': '趋势指标',
                'name': 'MACD',
                'signal': '死叉看跌',
                'strength': -3,
                'desc': patterns.get('macd_desc', '')
            })
        
        # 4. 布林带信号
        bb_signal = patterns.get('bb_signal', '')
        if bb_signal == 'breakout_up':
            signals.append({
                'category': '波动指标',
                'name': '布林带',
                'signal': '突破上轨',
                'strength': 2,
                'desc': patterns.get('bb_desc', '')
            })
        elif bb_signal == 'breakdown':
            signals.append({
                'category': '波动指标',
                'name': '布林带',
                'signal': '超卖反弹',
                'strength': 2,
                'desc': patterns.get('bb_desc', '')
            })
        
        # 5. 形态信号
        if patterns.get('double_bottom'):
            signals.append({
                'category': '经典形态',
                'name': '双底',
                'signal': '看涨',
                'strength': 4,
                'desc': patterns.get('double_bottom_desc', '')
            })
        
        if patterns.get('double_top'):
            signals.append({
                'category': '经典形态',
                'name': '双顶',
                'signal': '看跌',
                'strength': -4,
                'desc': patterns.get('double_top_desc', '')
            })
        
        if patterns.get('head_shoulders') == 'head_and_shoulders_top':
            signals.append({
                'category': '经典形态',
                'name': '头肩顶',
                'signal': '看跌',
                'strength': -5,
                'desc': patterns.get('head_shoulders_desc', '')
            })
        
        # 6. 市场情绪 (极度恐惧=逆向买入)
        market = result.get('market', {})
        change_24h = market.get('change_24h', 0)
        
        if change_24h < -5:
            signals.append({
                'category': '市场情绪',
                'name': '24h跌幅',
                'signal': '恐慌抛售',
                'strength': 2,
                'desc': f'24h跌幅{change_24h:.1f}%，逆向买入机会'
            })
        elif change_24h > 5:
            signals.append({
                'category': '市场情绪',
                'name': '24h涨幅',
                'signal': '过度上涨',
                'strength': -2,
                'desc': f'24h涨幅{change_24h:.1f}%，追高风险'
            })
        
        return signals
    
    def _generate_conclusion(self, result: Dict) -> Dict:
        """
        生成最终结论 (叠buff计算)
        
        Returns:
            {
                'score': 综合评分,
                'decision': BUY/HOLD/SELL,
                'confidence': 置信度,
                'signals_count': {'bullish': 5, 'bearish': 2},
                'narrative': 综合叙述
            }
        """
        signals = result.get('signals', [])
        
        # 计算信号强度
        total_strength = sum(s['strength'] for s in signals)
        bullish_count = len([s for s in signals if s['strength'] > 0])
        bearish_count = len([s for s in signals if s['strength'] < 0])
        
        # 综合评分 (0-100)
        # 最大可能强度: 假设所有信号都是+5
        max_strength = len(signals) * 5 if signals else 1
        score = 50 + (total_strength / max_strength) * 50
        score = max(0, min(100, score))
        
        # 决策
        if score >= 65:
            decision = 'BUY'
        elif score >= 45:
            decision = 'HOLD'
        else:
            decision = 'SELL'
        
        # 置信度
        if bullish_count + bearish_count > 0:
            confidence = max(bullish_count, bearish_count) / (bullish_count + bearish_count) * 100
        else:
            confidence = 50
        
        # 综合叙述
        narrative_parts = []
        
        if bullish_count > bearish_count:
            narrative_parts.append(f"综合{bullish_count}项看涨信号 vs {bearish_count}项看跌信号，技术面偏多。")
        elif bearish_count > bullish_count:
            narrative_parts.append(f"综合{bearish_count}项看跌信号 vs {bullish_count}项看涨信号，技术面偏空。")
        else:
            narrative_parts.append(f"看涨看跌信号各{bullish_count}项，技术面中性。")
        
        narrative_parts.append(f"综合评分{score:.0f}/100，建议{decision}。")
        
        if confidence > 70:
            narrative_parts.append(f"置信度{confidence:.0f}%，信号一致性较高。")
        else:
            narrative_parts.append(f"置信度{confidence:.0f}%，建议谨慎。")
        
        return {
            'score': round(score),
            'decision': decision,
            'confidence': round(confidence),
            'signals_count': {
                'bullish': bullish_count,
                'bearish': bearish_count
            },
            'total_strength': total_strength,
            'narrative': ' '.join(narrative_parts)
        }


def analyze_complete(symbol: str) -> Dict:
    """便捷函数"""
    analyzer = CompleteCryptoAnalyzer()
    return analyzer.analyze_all(symbol)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='加密货币分析')
    parser.add_argument('--symbol', default='BTC-USD', help='交易对，如 ETH-USD')
    args = parser.parse_args()
    
    print(f"分析 {args.symbol}...")
    print("=" * 60)
    
    result = analyze_complete(args.symbol)
    
    print(f"Symbol: {result['symbol']}")
    print(f"Price: ${result['market'].get('price', 0):,.2f}")
    print(f"Pattern: {result['patterns'].get('trend_desc', 'N/A')}")
    print()
    print("Signals:")
    for s in result['signals']:
        print(f"  [{s['category']}] {s['name']}: {s['signal']} (strength={s['strength']})")
    print()
    print(f"Conclusion: {result['conclusion']['narrative']}")
    print("=" * 60)
