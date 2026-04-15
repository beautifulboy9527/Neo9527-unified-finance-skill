#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号追踪模块 - 饕餮整合自 alphaear-signal-tracker + moltbot
投资信号演化追踪、热门股票扫描、谣言扫描
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import OUTPUT_DIR
except ImportError:
    OUTPUT_DIR = Path(r'D:\OpenClaw\outputs')


class SignalTracker:
    """
    信号追踪器 - 饕餮整合自 alphaear-signal-tracker + moltbot
    
    能力:
    - 投资信号演化追踪 (强化/弱化/证伪)
    - 热门股票扫描
    - 谣言扫描 (M&A、内部交易、分析师评级)
    - 信号置信度管理
    """
    
    def __init__(self):
        self.data_dir = OUTPUT_DIR / 'data' / 'signals'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.signals_file = self.data_dir / 'tracked_signals.json'
        self._load_signals()
    
    def _load_signals(self):
        """加载已追踪的信号"""
        if self.signals_file.exists():
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    self.signals = json.load(f)
            except:
                self.signals = {}
        else:
            self.signals = {}
    
    def _save_signals(self):
        """保存信号"""
        with open(self.signals_file, 'w', encoding='utf-8') as f:
            json.dump(self.signals, f, ensure_ascii=False, indent=2)
    
    def create_signal(
        self,
        symbol: str,
        signal_type: str,
        thesis: str,
        confidence: float = 0.5,
        data: Dict = None
    ) -> Dict:
        """
        创建新信号
        
        Args:
            symbol: 股票代码
            signal_type: 信号类型 (bullish/bearish/neutral)
            thesis: 核心论点
            confidence: 初始置信度 (0-1)
            data: 支持数据
            
        Returns:
            创建的信号
        """
        signal_id = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        signal = {
            'id': signal_id,
            'symbol': symbol,
            'type': signal_type,
            'thesis': thesis,
            'confidence': confidence,
            'intensity': self._calculate_intensity(confidence),
            'status': 'active',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'evolution': [],
            'supporting_data': data or {}
        }
        
        self.signals[signal_id] = signal
        self._save_signals()
        
        return signal
    
    def _calculate_intensity(self, confidence: float) -> str:
        """计算信号强度"""
        if confidence >= 0.8:
            return 'strong'
        elif confidence >= 0.6:
            return 'moderate'
        elif confidence >= 0.4:
            return 'weak'
        else:
            return 'very_weak'
    
    def track_signal(
        self,
        signal_id: str,
        new_info: Dict
    ) -> Dict:
        """
        追踪信号演化
        
        Args:
            signal_id: 信号 ID
            new_info: 新信息
            
        Returns:
            更新后的信号
        """
        result = {
            'signal_id': signal_id,
            'evolution': None,
            'error': None
        }
        
        if signal_id not in self.signals:
            result['error'] = '信号不存在'
            return result
        
        signal = self.signals[signal_id]
        
        # 分析新信息对信号的影响
        impact = self._analyze_impact(signal, new_info)
        
        # 更新置信度
        old_confidence = signal['confidence']
        confidence_change = impact['confidence_delta']
        new_confidence = max(0, min(1, old_confidence + confidence_change))
        
        # 记录演化
        evolution_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'direction': impact['direction'],
            'confidence_before': old_confidence,
            'confidence_after': new_confidence,
            'reason': impact['reason'],
            'evidence': new_info
        }
        
        signal['evolution'].append(evolution_entry)
        signal['confidence'] = new_confidence
        signal['intensity'] = self._calculate_intensity(new_confidence)
        signal['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 检查是否证伪
        if new_confidence < 0.2:
            signal['status'] = 'falsified'
        elif len(signal['evolution']) >= 3:
            recent_directions = [e['direction'] for e in signal['evolution'][-3:]]
            if all(d == 'weakened' for d in recent_directions):
                signal['status'] = 'weakened'
            elif all(d == 'strengthened' for d in recent_directions):
                signal['status'] = 'strengthened'
        
        self._save_signals()
        
        result['evolution'] = evolution_entry
        result['signal'] = signal
        
        return result
    
    def _analyze_impact(self, signal: Dict, new_info: Dict) -> Dict:
        """
        分析新信息对信号的影响
        
        Returns:
            {
                'direction': 'strengthened' | 'weakened' | 'unchanged',
                'confidence_delta': float,
                'reason': str
            }
        """
        impact = {
            'direction': 'unchanged',
            'confidence_delta': 0,
            'reason': '无显著影响'
        }
        
        info_type = new_info.get('type', '')
        info_sentiment = new_info.get('sentiment', 'neutral')
        signal_type = signal['type']
        
        # 价格变动
        if info_type == 'price_change':
            price_change = new_info.get('change_pct', 0)
            
            if signal_type == 'bullish':
                if price_change > 5:
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.1
                    impact['reason'] = f'价格上涨 {price_change:.1f}%，支持看涨论点'
                elif price_change < -5:
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.15
                    impact['reason'] = f'价格下跌 {abs(price_change):.1f}%，削弱看涨论点'
            
            elif signal_type == 'bearish':
                if price_change < -5:
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.1
                    impact['reason'] = f'价格下跌 {abs(price_change):.1f}%，支持看跌论点'
                elif price_change > 5:
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.15
                    impact['reason'] = f'价格上涨 {price_change:.1f}%，削弱看跌论点'
        
        # 新闻事件
        elif info_type == 'news':
            if signal_type == 'bullish':
                if info_sentiment == 'positive':
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.05
                    impact['reason'] = '正面新闻支持看涨论点'
                elif info_sentiment == 'negative':
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.1
                    impact['reason'] = '负面新闻削弱看涨论点'
            
            elif signal_type == 'bearish':
                if info_sentiment == 'negative':
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.05
                    impact['reason'] = '负面新闻支持看跌论点'
                elif info_sentiment == 'positive':
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.1
                    impact['reason'] = '正面新闻削弱看跌论点'
        
        # 分析师评级
        elif info_type == 'analyst_rating':
            rating = new_info.get('rating', '')
            
            if signal_type == 'bullish':
                if rating in ['buy', 'strong_buy', 'outperform']:
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.08
                    impact['reason'] = f'分析师评级 {rating} 支持看涨'
                elif rating in ['sell', 'underperform']:
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.12
                    impact['reason'] = f'分析师评级 {rating} 削弱看涨'
            
            elif signal_type == 'bearish':
                if rating in ['sell', 'underperform']:
                    impact['direction'] = 'strengthened'
                    impact['confidence_delta'] = 0.08
                    impact['reason'] = f'分析师评级 {rating} 支持看跌'
                elif rating in ['buy', 'strong_buy']:
                    impact['direction'] = 'weakened'
                    impact['confidence_delta'] = -0.12
                    impact['reason'] = f'分析师评级 {rating} 削弱看跌'
        
        return impact
    
    def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """获取活跃信号"""
        signals = []
        for sig in self.signals.values():
            if sig['status'] == 'active':
                if symbol is None or sig['symbol'] == symbol:
                    signals.append(sig)
        return signals
    
    def scan_hot_stocks(self) -> Dict:
        """
        扫描热门股票
        
        Returns:
            热门股票列表
        """
        result = {
            'hot_stocks': [],
            'sources': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 使用 yfinance 获取市场涨跌幅
            import yfinance as yf
            
            # 热门美股
            hot_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B']
            
            hot_stocks = []
            for symbol in hot_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_price = hist['Close'].iloc[0]
                        change_pct = (current_price - prev_price) / prev_price * 100
                        
                        info = ticker.info
                        
                        hot_stocks.append({
                            'symbol': symbol,
                            'name': info.get('shortName', symbol),
                            'price': round(current_price, 2),
                            'change_pct': round(change_pct, 2),
                            'volume': hist['Volume'].iloc[-1] if 'Volume' in hist else None,
                            'market_cap': info.get('marketCap'),
                            'pe_ratio': info.get('trailingPE')
                        })
                except:
                    pass
            
            # 按涨跌幅排序
            hot_stocks.sort(key=lambda x: abs(x['change_pct']), reverse=True)
            
            result['hot_stocks'] = hot_stocks
            result['sources'] = {'yfinance': len(hot_stocks)}
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def scan_rumors(self) -> Dict:
        """
        扫描谣言和早期信号
        
        Returns:
            谣言和早期信号列表
        """
        result = {
            'rumors': [],
            'insider_activity': [],
            'analyst_changes': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            import yfinance as yf
            
            # 扫描分析师评级变化
            symbols_to_check = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
            
            for symbol in symbols_to_check:
                try:
                    ticker = yf.Ticker(symbol)
                    recommendations = ticker.recommendations
                    
                    if recommendations is not None and not recommendations.empty:
                        # 获取最近评级
                        latest = recommendations.iloc[-1] if len(recommendations) > 0 else None
                        
                        if latest is not None:
                            result['analyst_changes'].append({
                                'symbol': symbol,
                                'strong_buy': int(latest.get('strongBuy', 0)),
                                'buy': int(latest.get('buy', 0)),
                                'hold': int(latest.get('hold', 0)),
                                'sell': int(latest.get('sell', 0)),
                                'strong_sell': int(latest.get('strongSell', 0))
                            })
                except:
                    pass
            
            # 注: 真正的谣言扫描需要更专业的数据源
            result['note'] = '分析师评级变化已获取。M&A谣言和内部交易需要专业数据源。'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def create_signal(symbol: str, signal_type: str, thesis: str, confidence: float = 0.5) -> Dict:
    """创建信号"""
    tracker = SignalTracker()
    return tracker.create_signal(symbol, signal_type, thesis, confidence)


def track_signal(signal_id: str, new_info: Dict) -> Dict:
    """追踪信号"""
    tracker = SignalTracker()
    return tracker.track_signal(signal_id, new_info)


def get_active_signals(symbol: str = None) -> List[Dict]:
    """获取活跃信号"""
    tracker = SignalTracker()
    return tracker.get_active_signals(symbol)


def scan_hot_stocks() -> Dict:
    """扫描热门股票"""
    tracker = SignalTracker()
    return tracker.scan_hot_stocks()


def scan_rumors() -> Dict:
    """扫描谣言"""
    tracker = SignalTracker()
    return tracker.scan_rumors()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='信号追踪 - 饕餮整合自 alphaear-signal-tracker + moltbot')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create
    create_parser = subparsers.add_parser('create', help='创建信号')
    create_parser.add_argument('symbol', help='股票代码')
    create_parser.add_argument('--type', choices=['bullish', 'bearish', 'neutral'], default='bullish', help='信号类型')
    create_parser.add_argument('--thesis', required=True, help='核心论点')
    create_parser.add_argument('--confidence', type=float, default=0.5, help='初始置信度')
    
    # track
    track_parser = subparsers.add_parser('track', help='追踪信号')
    track_parser.add_argument('signal_id', help='信号 ID')
    track_parser.add_argument('--type', default='news', help='信息类型')
    track_parser.add_argument('--sentiment', default='neutral', help='情绪')
    
    # list
    list_parser = subparsers.add_parser('list', help='列出信号')
    list_parser.add_argument('--symbol', help='股票代码')
    
    # hot
    subparsers.add_parser('hot', help='热门扫描')
    
    # rumors
    subparsers.add_parser('rumors', help='谣言扫描')
    
    args = parser.parse_args()
    
    tracker = SignalTracker()
    
    if args.command == 'create':
        result = tracker.create_signal(args.symbol, args.type, args.thesis, args.confidence)
    elif args.command == 'track':
        new_info = {'type': args.type, 'sentiment': args.sentiment}
        result = tracker.track_signal(args.signal_id, new_info)
    elif args.command == 'list':
        result = tracker.get_active_signals(args.symbol)
    elif args.command == 'hot':
        result = tracker.scan_hot_stocks()
    elif args.command == 'rumors':
        result = tracker.scan_rumors()
    else:
        result = tracker.scan_hot_stocks()
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
