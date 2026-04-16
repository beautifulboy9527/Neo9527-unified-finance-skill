#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币专用分析模块
提供链上指标、市场情绪、加密特有信号
"""

import sys
import os
from datetime import datetime
from typing import Dict, Optional

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CryptoAnalyzer:
    """
    加密货币分析器
    
    功能:
    - 链上数据分析 (活跃地址、交易量)
    - 市场情绪指标 (恐慌贪婪指数)
    - 加密特有信号 (Funding Rate、Long/Short)
    - 技术分析 (适配加密货币波动特征)
    """
    
    def analyze(self, symbol: str) -> Dict:
        """
        综合分析加密货币
        
        Args:
            symbol: 加密货币代码 (如 BTC-USD, ETH-USD)
            
        Returns:
            分析结果
        """
        result = {
            'symbol': symbol,
            'type': 'crypto',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'onchain': {},
            'sentiment': {},
            'technical': {},
            'signals': {},
            'score': 0,
            'recommendation': 'hold'
        }
        
        # 1. 链上分析
        result['onchain'] = self._analyze_onchain(symbol)
        
        # 2. 市场情绪
        result['sentiment'] = self._analyze_sentiment(symbol)
        
        # 3. 技术分析 (加密适配)
        result['technical'] = self._analyze_technical_crypto(symbol)
        
        # 4. 信号检测
        result['signals'] = self._detect_crypto_signals(symbol)
        
        # 5. 综合评分
        result['score'] = self._calculate_score(result)
        
        # 6. 生成建议
        result['recommendation'] = self._generate_recommendation(result)
        
        return result
    
    def _analyze_onchain(self, symbol: str) -> Dict:
        """
        链上数据分析 - 使用 CoinGecko API
        
        Returns:
            链上指标
        """
        # CoinGecko API 获取市场数据
        try:
            import requests
            
            # 转换 symbol 格式: ETH-USD → ethereum
            coin_id = self._symbol_to_coingecko_id(symbol)
            
            # CoinGecko API (免费)
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                return {
                    'current_price_usd': market_data.get('current_price', {}).get('usd'),
                    'price_change_24h': market_data.get('price_change_percentage_24h'),
                    'price_change_7d': market_data.get('price_change_percentage_7d'),
                    'volume_24h': market_data.get('total_volume', {}).get('usd'),
                    'market_cap': market_data.get('market_cap', {}).get('usd'),
                    'market_cap_rank': data.get('market_cap_rank'),
                    'total_supply': market_data.get('total_supply'),
                    'circulating_supply': market_data.get('circulating_supply'),
                    'high_24h': market_data.get('high_24h', {}).get('usd'),
                    'low_24h': market_data.get('low_24h', {}).get('usd'),
                    'ath': market_data.get('ath', {}).get('usd'),
                    'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd'),
                    'data_source': 'CoinGecko API',
                    'source_url': f'https://www.coingecko.com/en/coins/{coin_id}',
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        except Exception as e:
            print(f"⚠️ CoinGecko 数据获取失败: {e}")
        
        return {
            'active_addresses_24h': 'N/A',
            'transaction_volume': 'N/A',
            'data_source': 'fallback',
            'note': '链上数据获取失败，请检查网络连接'
        }
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """
        将交易对转换为 CoinGecko ID
        
        Args:
            symbol: 如 ETH-USD, BTC-USD
            
        Returns:
            CoinGecko coin id: 如 ethereum, bitcoin
        """
        # 常见映射
        mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'LTC': 'litecoin',
            'SHIB': 'shiba-inu',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'ATOM': 'cosmos',
            'UNI': 'uniswap',
            'XMR': 'monero',
            'ETC': 'ethereum-classic',
            'XLM': 'stellar',
            'BCH': 'bitcoin-cash',
            'ALGO': 'algorand',
            'AAVE': 'aave',
            'COMP': 'compound-governance-token',
            'MKR': 'maker',
        }
        
        # 提取基础货币
        base = symbol.upper().split('-')[0].replace('USDT', '').replace('USDC', '')
        
        return mapping.get(base, base.lower())
    
    def _analyze_sentiment(self, symbol: str) -> Dict:
        """
        市场情绪分析 - 使用 alternative.me API
        
        Returns:
            情绪指标
        """
        try:
            # 使用 Alternative.me Fear & Greed Index API (免费)
            import requests
            
            response = requests.get(
                'https://api.alternative.me/fng/',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()['data'][0]
                fear_greed_value = int(data['value'])
                fear_greed_class = data['value_classification']
                timestamp = int(data['timestamp'])
                
                return {
                    'fear_greed_index': fear_greed_value,
                    'fear_greed_class': fear_greed_class,
                    'sentiment_score': self._map_sentiment_to_score(fear_greed_value),
                    'data_source': 'alternative.me API',
                    'source_url': 'https://alternative.me/crypto/fear-and-greed-index/',
                    'update_time': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                    'description': f"恐慌贪婪指数: {fear_greed_value} ({fear_greed_class})"
                }
        except Exception as e:
            print(f"⚠️ 情绪数据获取失败: {e}")
        
        return {
            'fear_greed_index': 'N/A',
            'fear_greed_class': 'N/A',
            'sentiment_score': 50,
            'data_source': 'fallback',
            'note': '情绪数据获取失败'
        }
    
    def _map_sentiment_to_score(self, value: int) -> int:
        """将恐慌贪婪指数映射为评分"""
        # 0-25: 极度恐惧 → 70分 (逆向买入机会)
        # 25-50: 恐惧 → 60分
        # 50-75: 贪婪 → 50分
        # 75-100: 极度贪婪 → 30分 (风险较高)
        
        if value <= 25:
            return 70
        elif value <= 50:
            return 60
        elif value <= 75:
            return 50
        else:
            return 30
    
    def _analyze_technical_crypto(self, symbol: str) -> Dict:
        """
        加密货币技术分析 (适配高波动 + 多指标)
        """
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from core.technical import analyze_technical
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            result = analyze_technical(symbol)
            
            # 确保 indicators 字典存在
            if 'indicators' not in result:
                result['indicators'] = {}
            
            # 加密货币特有的风险评估
            basic = result.get('basic_indicators', {})
            
            # 将 basic_indicators 合并到 indicators
            result['indicators'].update(basic)
            
            # ATR倍数调整 (加密货币波动更大)
            atr = basic.get('atr', 0)
            current_price = basic.get('current_price', 0)
            
            if atr and current_price:
                volatility_ratio = atr / current_price
                
                # 高波动警告
                if volatility_ratio > 0.05:  # ATR > 5% 价格
                    result['volatility_warning'] = f"⚠️ 高波动率: {volatility_ratio*100:.1f}% (建议ATR止损倍数3-4)"
            
            # 新增: 更多技术指标 (使用 CoinGecko OHLC)
            try:
                import yfinance as yf
                import pandas as pd
                import numpy as np
                
                # 使用 yfinance 获取 OHLCV 数据
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='6mo')
                
                if not hist.empty and len(hist) >= 30:
                    closes = hist['Close']
                    highs = hist['High']
                    lows = hist['Low']
                    volumes = hist['Volume']
                    
                    # MACD
                    exp1 = closes.ewm(span=12, adjust=False).mean()
                    exp2 = closes.ewm(span=26, adjust=False).mean()
                    macd = exp1 - exp2
                    signal = macd.ewm(span=9, adjust=False).mean()
                    histogram = macd - signal
                    
                    result['indicators']['macd'] = round(float(macd.iloc[-1]), 4)
                    result['indicators']['macd_signal'] = round(float(signal.iloc[-1]), 4)
                    result['indicators']['macd_histogram'] = round(float(histogram.iloc[-1]), 4)
                    result['indicators']['macd_trend'] = 'bullish' if float(histogram.iloc[-1]) > 0 else 'bearish'
                    
                    # Bollinger Bands
                    bb_middle = closes.rolling(window=20).mean()
                    bb_std = closes.rolling(window=20).std()
                    bb_upper = bb_middle + (bb_std * 2)
                    bb_lower = bb_middle - (bb_std * 2)
                    
                    result['indicators']['bb_upper'] = round(float(bb_upper.iloc[-1]), 2)
                    result['indicators']['bb_middle'] = round(float(bb_middle.iloc[-1]), 2)
                    result['indicators']['bb_lower'] = round(float(bb_lower.iloc[-1]), 2)
                    
                    current_price = float(current_price) if current_price else float(closes.iloc[-1])
                    
                    if current_price > float(bb_upper.iloc[-1]):
                        result['indicators']['bb_position'] = 'above_upper'
                    elif current_price < float(bb_lower.iloc[-1]):
                        result['indicators']['bb_position'] = 'below_lower'
                    else:
                        result['indicators']['bb_position'] = 'middle'
                    
                    # Volume Analysis
                    avg_volume_20 = float(volumes.rolling(window=20).mean().iloc[-1])
                    current_volume = float(volumes.iloc[-1])
                    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
                    
                    result['indicators']['volume_ratio'] = round(volume_ratio, 2)
                    result['indicators']['volume_trend'] = 'high' if volume_ratio > 1.5 else 'low' if volume_ratio < 0.7 else 'normal'
                    
                    # Stochastic
                    low_14 = lows.rolling(window=14).min()
                    high_14 = highs.rolling(window=14).max()
                    k = 100 * (closes - low_14) / (high_14 - low_14 + 0.0001)  # 避免除零
                    d = k.rolling(window=3).mean()
                    
                    result['indicators']['stoch_k'] = round(float(k.iloc[-1]), 2)
                    result['indicators']['stoch_d'] = round(float(d.iloc[-1]), 2)
                    
                    # ADX (趋势强度)
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
                    atr_14 = tr.rolling(window=14).mean()
                    
                    plus_di = 100 * (plus_dm.rolling(window=14).mean() / (atr_14 + 0.0001))
                    minus_di = 100 * (minus_dm.rolling(window=14).mean() / (atr_14 + 0.0001))
                    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 0.0001)
                    adx = dx.rolling(window=14).mean()
                    
                    result['indicators']['adx'] = round(float(adx.iloc[-1]), 2)
                    result['indicators']['plus_di'] = round(float(plus_di.iloc[-1]), 2)
                    result['indicators']['minus_di'] = round(float(minus_di.iloc[-1]), 2)
                    
                    adx_value = float(adx.iloc[-1])
                    if adx_value > 25:
                        result['indicators']['trend_strength'] = 'strong'
                    elif adx_value < 20:
                        result['indicators']['trend_strength'] = 'weak'
                    else:
                        result['indicators']['trend_strength'] = 'moderate'
                    
                    result['data_source'] = 'yfinance + pandas'
                    
            except Exception as e:
                print(f"⚠️ 扩展指标计算失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 新增: 生成专业文字解读
            result['narrative'] = self._generate_technical_narrative(result['indicators'], symbol)
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_technical_narrative(self, indicators: Dict, symbol: str) -> str:
        """
        生成技术面专业文字解读 (多指标共振分析)
        
        Args:
            indicators: 技术指标字典
            symbol: 股票代码
            
        Returns:
            专业解读文字
        """
        if not indicators or indicators.get('current_price') is None:
            return "技术数据不足，无法生成解读。"
        
        current_price = indicators.get('current_price', 0)
        trend = indicators.get('trend', 'unknown')
        rsi = indicators.get('rsi', 0)
        ma5 = indicators.get('ma5', 0)
        ma10 = indicators.get('ma10', 0)
        ma20 = indicators.get('ma20', 0)
        
        # 新增指标
        macd_trend = indicators.get('macd_trend')
        bb_position = indicators.get('bb_position')
        volume_ratio = indicators.get('volume_ratio', 1)
        stoch_k = indicators.get('stoch_k', 50)
        adx = indicators.get('adx', 0)
        trend_strength = indicators.get('trend_strength', 'unknown')
        
        # 构建解读
        paragraphs = []
        
        # 1. 趋势分析 (增强)
        if trend == 'uptrend':
            trend_desc = (
                f"{symbol} 当前处于上升趋势，价格({current_price:.2f})站上MA5({ma5:.2f})、MA10({ma10:.2f})、MA20({ma20:.2f})三条均线，"
                f"形成多头排列。"
            )
            if adx:
                trend_desc += f" ADX为{adx:.1f}，趋势{'强度充足' if adx > 25 else '强度一般'}。"
            paragraphs.append(trend_desc)
        elif trend == 'downtrend':
            paragraphs.append(
                f"{symbol} 当前处于下降趋势，价格({current_price:.2f})低于MA5、MA10、MA20均线，"
                f"空头排列明显。ADX为{adx:.1f}，趋势强度{'较强' if adx > 25 else '较弱'}。"
            )
        else:
            paragraphs.append(
                f"{symbol} 当前处于震荡整理阶段，价格({current_price:.2f})在均线间反复，"
                f"方向不明确。ADX为{adx:.1f}，趋势强度较弱。"
            )
        
        # 2. RSI + Stochastic 共振分析
        momentum_parts = []
        if rsi:
            if rsi > 70:
                momentum_parts.append(f"RSI达{rsi:.1f}超买区")
            elif rsi > 60:
                momentum_parts.append(f"RSI为{rsi:.1f}偏强")
            elif rsi < 30:
                momentum_parts.append(f"RSI仅{rsi:.1f}超卖区")
            else:
                momentum_parts.append(f"RSI为{rsi:.1f}中性")
        
        if stoch_k:
            if stoch_k > 80:
                momentum_parts.append(f"Stochastic %K达{stoch_k:.1f}超买")
            elif stoch_k < 20:
                momentum_parts.append(f"Stochastic %K仅{stoch_k:.1f}超卖")
        
        if momentum_parts:
            momentum_text = "，".join(momentum_parts) + "。"
            paragraphs.append(momentum_text)
        
        # 3. MACD 分析
        if macd_trend:
            macd_text = (
                f"MACD {'多头排列' if macd_trend == 'bullish' else '空头排列'}，"
                f"{'柱状图为正，动能向上' if macd_trend == 'bullish' else '柱状图为负，动能向下'}。"
            )
            paragraphs.append(macd_text)
        
        # 4. Bollinger Bands 分析
        if bb_position:
            if bb_position == 'above_upper':
                paragraphs.append(
                    f"价格突破布林带上轨，波动率放大，短期可能进入加速上涨或面临回调。"
                )
            elif bb_position == 'below_lower':
                paragraphs.append(
                    f"价格跌破布林带下轨，超卖迹象明显，可能存在反弹机会。"
                )
            else:
                bb_upper = indicators.get('bb_upper', 0)
                bb_lower = indicators.get('bb_lower', 0)
                paragraphs.append(
                    f"价格在布林带区间内运行，上轨{bb_upper:.2f}为阻力，下轨{bb_lower:.2f}为支撑。"
                )
        
        # 5. 成交量分析
        if volume_ratio:
            if volume_ratio > 1.5:
                vol_text = f"成交量放大{volume_ratio:.1f}倍，市场活跃度提升。"
                if trend == 'uptrend':
                    vol_text += "趋势确认有效。"
                else:
                    vol_text += "需警惕量价背离。"
                paragraphs.append(vol_text)
            elif volume_ratio < 0.7:
                paragraphs.append(
                    f"成交量萎缩至{volume_ratio:.1f}倍均值，市场观望情绪浓厚。"
                )
        
        # 6. 综合操作建议 (多因素共振)
        bullish_signals = 0
        bearish_signals = 0
        
        if trend == 'uptrend': bullish_signals += 1
        elif trend == 'downtrend': bearish_signals += 1
        
        if macd_trend == 'bullish': bullish_signals += 1
        elif macd_trend == 'bearish': bearish_signals += 1
        
        if rsi and 40 < rsi < 70: bullish_signals += 1
        elif rsi and rsi > 70: bearish_signals += 1
        
        if volume_ratio and volume_ratio > 1.2: bullish_signals += 1
        elif volume_ratio and volume_ratio < 0.8: bearish_signals += 1
        
        if bullish_signals > bearish_signals + 1:
            conclusion = (
                f"综合来看，{symbol}技术面偏多({bullish_signals}项看多信号 vs {bearish_signals}项看空信号)。"
                f"建议在MA20({ma20:.2f})附近设置止损，目标看前高附近。"
                f"严格执行止损纪律，仓位控制在10-20%。"
            )
        elif bearish_signals > bullish_signals + 1:
            conclusion = (
                f"综合来看，{symbol}技术面偏空({bearish_signals}项看空信号 vs {bullish_signals}项看多信号)。"
                f"建议观望为主，等待技术面修复后再考虑入场。"
            )
        else:
            conclusion = (
                f"综合来看，{symbol}技术面信号混杂({bullish_signals}多 vs {bearish_signals}空)，"
                f"建议等待更明确的趋势信号再操作。关注MA20得失和成交量变化。"
            )
        
        paragraphs.append(conclusion)
        
        return "\n\n".join(paragraphs)
    
    def _detect_crypto_signals(self, symbol: str) -> Dict:
        """
        加密货币特有信号
        """
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.entry_signals import analyze_entry_signals
            
            result = analyze_entry_signals(symbol)
            
            # 加密货币信号权重调整
            # 可以添加加密特有信号如:
            # - Funding Rate 极端值
            # - Long/Short Ratio
            # - 交易所流入流出
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_score(self, result: Dict) -> int:
        """
        计算加密货币综合评分
        
        权重:
        - 技术面: 50%
        - 信号: 25%
        - 情绪: 15%
        - 链上: 10%
        """
        score = 0
        
        # 技术面 (50分)
        tech = result.get('technical', {})
        ai_decision = tech.get('ai_decision', {})
        if ai_decision.get('recommendation') == 'buy':
            score += 35
        elif ai_decision.get('recommendation') == 'hold':
            score += 20
        
        tech_score = ai_decision.get('confidence', 0)
        score += int(tech_score * 0.15)
        
        # 信号 (25分)
        signals = result.get('signals', {})
        signal_score = signals.get('score', {}).get('overall_score', 0)
        score += int(signal_score * 0.25)
        
        # 情绪 (15分)
        sentiment = result.get('sentiment', {})
        sentiment_score = sentiment.get('sentiment_score', 50)
        score += int(sentiment_score * 0.15)
        
        # 链上 (10分)
        onchain = result.get('onchain', {})
        if onchain.get('whale_activity') == 'accumulating':
            score += 10
        elif onchain.get('whale_activity') == 'distributing':
            score += 0
        else:
            score += 5  # 数据缺失给中性分
        
        return min(100, max(0, score))
    
    def _generate_recommendation(self, result: Dict) -> str:
        """生成投资建议"""
        score = result['score']
        
        if score >= 70:
            return 'buy'
        elif score >= 50:
            return 'hold'
        elif score >= 30:
            return 'reduce'
        else:
            return 'avoid'


# ============================================
# 便捷函数
# ============================================

def analyze_crypto(symbol: str) -> Dict:
    """分析加密货币"""
    analyzer = CryptoAnalyzer()
    return analyzer.analyze(symbol)


if __name__ == '__main__':
    symbol = 'ETH-USD'
    
    print("=" * 60)
    print(f"加密货币分析: {symbol}")
    print("=" * 60)
    
    result = analyze_crypto(symbol)
    
    print(f"\n综合评分: {result['score']}/100")
    print(f"建议操作: {result['recommendation']}")
    
    # 情绪
    sentiment = result['sentiment']
    print(f"\n市场情绪:")
    print(f"  恐慌贪婪指数: {sentiment.get('fear_greed_index', 'N/A')}")
    print(f"  分类: {sentiment.get('fear_greed_class', 'N/A')}")
    print(f"  数据源: {sentiment.get('data_source', 'N/A')}")
    
    # 技术面
    tech = result['technical']
    basic = tech.get('basic_indicators', {})
    print(f"\n技术面:")
    print(f"  趋势: {basic.get('trend', 'N/A')}")
    print(f"  RSI: {basic.get('rsi', 'N/A')}")
    if 'volatility_warning' in tech:
        print(f"  {tech['volatility_warning']}")
