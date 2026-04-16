#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一技术分析模块 - 整合 agent-stock + stock-daily-analysis + stock-market-pro
基础指标 + 高级指标 + AI决策
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.quote import detect_market


class TechnicalAnalyzer:
    """技术分析整合器"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.market = detect_market(symbol)
        
    def get_basic_indicators(self) -> Dict:
        """
        获取基础技术指标 (agent-stock + yfinance 备用)
        """
        result = {
            'symbol': self.symbol,
            'indicators': {},
            'data_source': 'none',
            'error': None
        }
        
        # 方法1: 尝试 agent-stock
        try:
            import subprocess
            
            proc = subprocess.run(
                ['python', '-m', 'stock', 'kline', self.symbol, '--count', '60'],
                capture_output=True,
                text=True,
                cwd=r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\agent-stock',
                timeout=30
            )
            
            if proc.returncode == 0:
                output = proc.stdout
                
                # 解析K线数据
                lines = output.strip().split('\n')
                closes = []
                
                for line in lines[1:]:  # 跳过标题行
                    parts = line.split(',')
                    if len(parts) >= 5:
                        try:
                            close = float(parts[4])  # 收盘价
                            closes.append(close)
                        except:
                            continue
                
                if len(closes) >= 20:
                    # 计算均线
                    ma5 = sum(closes[-5:]) / 5
                    ma10 = sum(closes[-10:]) / 10
                    ma20 = sum(closes[-20:]) / 20
                    
                    # 计算乖离率
                    current_price = closes[-1]
                    bias_ma5 = (current_price - ma5) / ma5 * 100
                    
                    # 计算RSI (简化版)
                    rsi = self._calculate_rsi(closes)
                    
                    result['indicators'] = {
                        'current_price': round(current_price, 2),
                        'ma5': round(ma5, 2),
                        'ma10': round(ma10, 2),
                        'ma20': round(ma20, 2),
                        'bias_ma5': round(bias_ma5, 2),
                        'rsi': round(rsi, 2) if rsi else None,
                        'trend': 'uptrend' if current_price > ma5 > ma10 else 'downtrend'
                    }
                    result['data_source'] = 'agent-stock'
                    return result
                    
        except Exception as e:
            result['error'] = str(e)
        
        # 方法2: yfinance 备用 (适用于加密货币)
        try:
            import yfinance as yf
            import pandas as pd
            
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period='3mo')
            
            if not hist.empty and len(hist) >= 20:
                closes = hist['Close'].tolist()
                
                # 计算均线
                ma5 = sum(closes[-5:]) / 5
                ma10 = sum(closes[-10:]) / 10
                ma20 = sum(closes[-20:]) / 20
                
                current_price = closes[-1]
                
                # 计算RSI
                rsi = self._calculate_rsi(closes)
                
                # 计算ATR (波动率)
                highs = hist['High'].tolist()[-14:]
                lows = hist['Low'].tolist()[-14:]
                closes_14 = closes[-14:]
                
                tr_list = []
                for i in range(1, len(highs)):
                    tr = max(highs[i] - lows[i], abs(highs[i] - closes_14[i-1]), abs(lows[i] - closes_14[i-1]))
                    tr_list.append(tr)
                
                atr = sum(tr_list) / len(tr_list) if tr_list else 0
                
                result['indicators'] = {
                    'current_price': round(current_price, 2),
                    'ma5': round(ma5, 2),
                    'ma10': round(ma10, 2),
                    'ma20': round(ma20, 2),
                    'rsi': round(rsi, 2) if rsi else None,
                    'atr': round(atr, 2),
                    'trend': 'uptrend' if current_price > ma5 > ma10 else 'downtrend' if current_price < ma5 < ma10 else 'sideways'
                }
                result['data_source'] = 'yfinance'
                result['error'] = None
                
        except Exception as e:
            if result.get('error'):
                result['error'] += f'; yfinance failed: {str(e)}'
            else:
                result['error'] = f'yfinance failed: {str(e)}'
        
        return result
    
    def _calculate_rsi(self, closes: list, period: int = 14) -> Optional[float]:
        """计算RSI"""
        if len(closes) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return None
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_ai_decision(self) -> Dict:
        """
        获取AI决策建议 (stock-daily-analysis)
        """
        result = {
            'symbol': self.symbol,
            'ai_analysis': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            # 导入 analyzer 模块
            sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\scripts')
            from analyzer import analyze_stock
            
            # 先获取基础指标
            basic = self.get_basic_indicators()
            basic_indicators = basic.get('indicators', {})
            
            # 调用 AI 分析
            analysis = analyze_stock(self.symbol, basic_indicators)
            
            if analysis:
                result['ai_analysis'] = analysis
                result['data_source'] = 'analyzer'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def analyze(self) -> Dict:
        """
        完整技术分析 - 整合基础指标 + AI决策
        """
        basic = self.get_basic_indicators()
        ai = self.get_ai_decision()
        
        return {
            'symbol': self.symbol,
            'market': self.market,
            'basic_indicators': basic.get('indicators', {}),
            'ai_decision': ai.get('ai_analysis', {}),
            'data_sources': {
                'basic': basic.get('data_source'),
                'ai': ai.get('data_source')
            },
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'errors': {
                'basic': basic.get('error'),
                'ai': ai.get('error')
            }
        }


def analyze_technical(symbol: str) -> Dict:
    """技术分析入口"""
    analyzer = TechnicalAnalyzer(symbol)
    return analyzer.analyze()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='统一技术分析')
    parser.add_argument('--symbol', required=True, help='股票代码')
    
    args = parser.parse_args()
    
    result = analyze_technical(args.symbol)
    print(json.dumps(result, indent=2, ensure_ascii=False))
