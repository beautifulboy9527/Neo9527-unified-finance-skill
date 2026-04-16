# 饕餮整合方案 - 三大高价值模块

**整合时间**: 2026-04-16 05:20
**方法论**: 饕餮整合 + Darwin Skill 评估
**目标**: 整合 sm-analyze、entry-signals、signal_score 等高价值能力

---

## 📊 饕餮分析矩阵

### 待整合能力评估

| 能力 | 来源 | 价值 | 当前状态 | 整合难度 | 优先级 |
|------|------|------|---------|---------|--------|
| **三层分析框架** | sm-analyze | ⭐⭐⭐⭐⭐ | ❌ 缺失 | 中 | P0 |
| **100分评分体系** | sm-analyze | ⭐⭐⭐⭐⭐ | ❌ 缺失 | 低 | P0 |
| **ATR止损** | sm-analyze | ⭐⭐⭐⭐ | ❌ 缺失 | 低 | P0 |
| **入场信号库** | entry-signals | ⭐⭐⭐⭐⭐ | ❌ 缺失 | 中 | P0 |
| **signal_score** | sm-stock-daily | ⭐⭐⭐⭐ | ❌ 缺失 | 低 | P1 |
| **target_price/stop_loss** | sm-stock-daily | ⭐⭐⭐⭐ | ❌ 缺失 | 低 | P1 |

---

## 🎯 整合方案

### 模块架构

```
features/
├── analysis_framework.py   # 三层分析框架 (新增)
│   ├── MacroAnalyzer       # 宏观分析 (20分)
│   ├── SectorAnalyzer      # 行业分析 (20分)
│   └── StockAnalyzer       # 个股分析 (60分)
│
├── scoring_engine.py       # 评分引擎 (新增)
│   ├── score_macro()       # 宏观评分
│   ├── score_sector()      # 行业评分
│   ├── score_technical()   # 技术评分
│   └── calculate_total()   # 总分计算
│
├── entry_signals.py        # 入场信号库 (新增)
│   ├── SignalDetector      # 信号检测
│   ├── SignalScorer        # 信号评分
│   └── MultiTimeframeAnalyzer # 多时间框架
│
├── risk_management.py      # 风险管理 (新增)
│   ├── ATRStopLoss         # ATR止损
│   ├── PositionSizer       # 仓位计算
│   └── TargetCalculator    # 目标价计算
│
└── reporter_enhanced.py    # 增强报告 (增强)
    └── generate_analysis_report() # 完整分析报告
```

---

## 🔧 Phase 1: 核心模块开发

### 1. analysis_framework.py - 三层分析框架

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三层分析框架 - 整合自 sm-analyze
宏观(20分) → 行业(20分) → 个股(60分) → 综合评分(100分)
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MacroAnalyzer:
    """
    宏观分析器 (20分)
    
    评估内容:
    - 市场周期: 牛市/熊市/震荡 (12分)
    - 北向资金: 流入/流出 (8分)
    """
    
    def analyze(self, market: str = 'cn') -> Dict:
        """
        分析宏观环境
        
        Args:
            market: 市场类型 ('cn' / 'us' / 'hk')
            
        Returns:
            {
                'cycle': 'bull/bear/range',
                'cycle_score': 12,
                'north_flow': {...},
                'flow_score': 8,
                'total_score': 20,
                'analysis': '...'
            }
        """
        result = {
            'market': market,
            'cycle': 'range',
            'cycle_score': 8,  # 默认震荡
            'north_flow': None,
            'flow_score': 4,  # 默认中性
            'total_score': 12,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            if market == 'cn':
                # 获取沪深300数据
                result = self._analyze_cn_market()
            elif market == 'us':
                # 获取标普500数据
                result = self._analyze_us_market()
            elif market == 'hk':
                # 获取恒生指数数据
                result = self._analyze_hk_market()
        except Exception as e:
            result['error'] = str(e)
        
        # 计算总分
        result['total_score'] = result['cycle_score'] + result['flow_score']
        
        return result
    
    def _analyze_cn_market(self) -> Dict:
        """分析A股市场"""
        result = {
            'market': 'cn',
            'cycle': 'range',
            'cycle_score': 8,
            'flow_score': 4
        }
        
        try:
            import akshare as ak
            
            # 获取沪深300数据
            df = ak.stock_zh_index_daily(symbol="sh000300")
            
            if not df.empty:
                close = df['close'].iloc[-1]
                ma20 = df['close'].rolling(20).mean().iloc[-1]
                change_60d = (close - df['close'].iloc[-60]) / df['close'].iloc[-60] * 100
                
                # 判断市场周期
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                    result['cycle_desc'] = '牛市'
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                    result['cycle_desc'] = '熊市'
                else:
                    result['cycle'] = 'range'
                    result['cycle_score'] = 8
                    result['cycle_desc'] = '震荡'
                
                result['hs300'] = round(close, 2)
                result['hs300_ma20'] = round(ma20, 2)
                result['hs300_change_60d'] = round(change_60d, 2)
            
            # 获取北向资金
            try:
                north_flow = ak.stock_em_hsgt_north_net_flow_in(indicator="北向资金")
                if not north_flow.empty:
                    flow_5d = north_flow['北向资金'].tail(5).sum()
                    result['north_flow_5d'] = round(flow_5d, 2)
                    
                    if flow_5d > 50:
                        result['flow_score'] = 8
                        result['flow_signal'] = '外资积极'
                    elif flow_5d < -50:
                        result['flow_score'] = 2
                        result['flow_signal'] = '外资撤退'
                    else:
                        result['flow_score'] = 4
                        result['flow_signal'] = '外资观望'
            except:
                pass
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _analyze_us_market(self) -> Dict:
        """分析美股市场"""
        result = {
            'market': 'us',
            'cycle': 'range',
            'cycle_score': 8,
            'flow_score': 4
        }
        
        try:
            import yfinance as yf
            
            # 获取标普500数据
            sp500 = yf.Ticker("^GSPC")
            hist = sp500.history(period="3mo")
            
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change_60d = (close - hist['Close'].iloc[-60]) / hist['Close'].iloc[-60] * 100
                
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                else:
                    result['cycle'] = 'range'
                    result['cycle_score'] = 8
                
                result['sp500'] = round(close, 2)
                result['sp500_change_60d'] = round(change_60d, 2)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _analyze_hk_market(self) -> Dict:
        """分析港股市场"""
        result = {
            'market': 'hk',
            'cycle': 'range',
            'cycle_score': 8,
            'flow_score': 4
        }
        
        try:
            import yfinance as yf
            
            # 获取恒生指数数据
            hsi = yf.Ticker("^HSI")
            hist = hsi.history(period="3mo")
            
            if not hist.empty:
                close = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change_60d = (close - hist['Close'].iloc[-60]) / hist['Close'].iloc[-60] * 100
                
                if close > ma20 and change_60d > 0:
                    result['cycle'] = 'bull'
                    result['cycle_score'] = 12
                elif close < ma20 and change_60d < -10:
                    result['cycle'] = 'bear'
                    result['cycle_score'] = 4
                else:
                    result['cycle'] = 'range'
                    result['cycle_score'] = 8
                
                result['hsi'] = round(close, 2)
                result['hsi_change_60d'] = round(change_60d, 2)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


class SectorAnalyzer:
    """
    行业分析器 (20分)
    
    评估内容:
    - 板块相对强度: 领涨/跟涨/跟跌 (15分)
    - 板块资金流向 (5分)
    """
    
    def analyze(self, symbol: str) -> Dict:
        """
        分析行业环境
        
        Args:
            symbol: 股票代码
            
        Returns:
            {
                'relative_strength': 'leading/following/lagging',
                'strength_score': 15,
                'sector_flow': {...},
                'flow_score': 5,
                'total_score': 20
            }
        """
        result = {
            'symbol': symbol,
            'relative_strength': 'following',
            'strength_score': 10,
            'sector_flow': None,
            'flow_score': 3,
            'total_score': 13,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 获取股票所属板块
            sectors = self._get_sectors(symbol)
            result['sectors'] = sectors
            
            if sectors:
                # 分析板块表现
                result = self._analyze_sector_performance(sectors, result)
        
        except Exception as e:
            result['error'] = str(e)
        
        # 计算总分
        result['total_score'] = result['strength_score'] + result['flow_score']
        
        return result
    
    def _get_sectors(self, symbol: str) -> List[Dict]:
        """获取股票所属板块"""
        sectors = []
        
        try:
            # A股
            if symbol.isdigit():
                import akshare as ak
                df = ak.stock_individual_info_em(symbol=symbol)
                if not df.empty:
                    # 提取行业信息
                    for _, row in df.iterrows():
                        if '行业' in str(row['item']) or '概念' in str(row['item']):
                            sectors.append({
                                'name': row['item'],
                                'value': row['value']
                            })
            # 美股
            else:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info.get('sector'):
                    sectors.append({'name': 'sector', 'value': info['sector']})
                if info.get('industry'):
                    sectors.append({'name': 'industry', 'value': info['industry']})
        
        except Exception as e:
            pass
        
        return sectors
    
    def _analyze_sector_performance(self, sectors: List[Dict], result: Dict) -> Dict:
        """分析板块表现"""
        # 简化实现，实际需要获取板块涨跌数据
        result['relative_strength'] = 'following'
        result['strength_score'] = 10
        result['flow_score'] = 3
        
        return result


class StockAnalyzer:
    """
    个股技术分析器 (60分)
    
    评估内容:
    - 趋势: 均线排列 (25分)
    - 动能: MACD/RSI (15分)
    - 量价: 量比/量价配合 (10分)
    - 位置: ATR止损 (10分)
    """
    
    def analyze(self, symbol: str) -> Dict:
        """
        分析个股技术面
        
        Args:
            symbol: 股票代码
            
        Returns:
            {
                'trend_score': 25,
                'momentum_score': 15,
                'volume_score': 10,
                'position_score': 10,
                'total_score': 60
            }
        """
        result = {
            'symbol': symbol,
            'trend': {},
            'trend_score': 0,
            'momentum': {},
            'momentum_score': 0,
            'volume': {},
            'volume_score': 0,
            'position': {},
            'position_score': 0,
            'total_score': 0,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 获取行情数据
            ohlcv = self._get_ohlcv(symbol)
            
            if ohlcv is not None and not ohlcv.empty:
                # 1. 趋势分析 (25分)
                result['trend'] = self._analyze_trend(ohlcv)
                result['trend_score'] = result['trend']['score']
                
                # 2. 动能分析 (15分)
                result['momentum'] = self._analyze_momentum(ohlcv)
                result['momentum_score'] = result['momentum']['score']
                
                # 3. 量价分析 (10分)
                result['volume'] = self._analyze_volume(ohlcv)
                result['volume_score'] = result['volume']['score']
                
                # 4. 位置分析 (10分)
                result['position'] = self._analyze_position(ohlcv)
                result['position_score'] = result['position']['score']
        
        except Exception as e:
            result['error'] = str(e)
        
        # 计算总分
        result['total_score'] = (
            result['trend_score'] + 
            result['momentum_score'] + 
            result['volume_score'] + 
            result['position_score']
        )
        
        return result
    
    def _get_ohlcv(self, symbol: str):
        """获取K线数据"""
        try:
            # 美股
            if symbol.isalpha():
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                return ticker.history(period="6mo")
            # A股
            else:
                import akshare as ak
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
                return df
        except:
            return None
    
    def _analyze_trend(self, ohlcv) -> Dict:
        """趋势分析 (25分)"""
        result = {
            'status': 'mixed',
            'score': 10,
            'ma5': None,
            'ma10': None,
            'ma20': None,
            'ma60': None
        }
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            result['ma5'] = close.rolling(5).mean().iloc[-1]
            result['ma10'] = close.rolling(10).mean().iloc[-1]
            result['ma20'] = close.rolling(20).mean().iloc[-1]
            result['ma60'] = close.rolling(60).mean().iloc[-1]
            
            # 判断均线排列
            if result['ma5'] > result['ma10'] > result['ma20'] > result['ma60']:
                result['status'] = 'strong_bullish'
                result['score'] = 25
                result['desc'] = '强势多头排列'
            elif result['ma5'] > result['ma20']:
                result['status'] = 'bullish'
                result['score'] = 15
                result['desc'] = '偏多'
            elif result['ma5'] < result['ma10'] < result['ma20'] < result['ma60']:
                result['status'] = 'strong_bearish'
                result['score'] = 5
                result['desc'] = '强势空头排列'
            elif result['ma5'] < result['ma20']:
                result['status'] = 'bearish'
                result['score'] = 8
                result['desc'] = '偏空'
            else:
                result['status'] = 'mixed'
                result['score'] = 10
                result['desc'] = '均线纠缠'
        
        except:
            pass
        
        return result
    
    def _analyze_momentum(self, ohlcv) -> Dict:
        """动能分析 (15分)"""
        result = {
            'macd': {},
            'rsi': {},
            'score': 8
        }
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            result['rsi']['value'] = round(rsi.iloc[-1], 2)
            
            if result['rsi']['value'] > 70:
                result['rsi']['status'] = 'overbought'
                result['rsi']['score'] = 3
            elif result['rsi']['value'] < 30:
                result['rsi']['status'] = 'oversold'
                result['rsi']['score'] = 5
            else:
                result['rsi']['status'] = 'neutral'
                result['rsi']['score'] = 5
            
            # MACD (简化)
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            
            result['macd']['value'] = round(macd.iloc[-1], 4)
            result['macd']['signal'] = round(signal.iloc[-1], 4)
            
            if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
                result['macd']['status'] = 'golden_cross'
                result['macd']['score'] = 10
            elif macd.iloc[-1] > 0:
                result['macd']['status'] = 'bullish'
                result['macd']['score'] = 7
            elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
                result['macd']['status'] = 'death_cross'
                result['macd']['score'] = 3
            else:
                result['macd']['status'] = 'bearish'
                result['macd']['score'] = 5
            
            # 总分
            result['score'] = (result['rsi']['score'] + result['macd']['score']) // 2 + 1
        
        except:
            pass
        
        return result
    
    def _analyze_volume(self, ohlcv) -> Dict:
        """量价分析 (10分)"""
        result = {
            'ratio': 1.0,
            'status': 'normal',
            'score': 6
        }
        
        try:
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            volume = ohlcv['Volume'] if 'Volume' in ohlcv else ohlcv['成交量']
            
            # 量比
            avg_volume = volume.rolling(20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            result['ratio'] = round(current_volume / avg_volume, 2)
            
            # 量价配合
            price_change = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100
            
            if price_change > 0 and result['ratio'] > 1.5:
                result['status'] = 'volume_up'
                result['score'] = 10
                result['desc'] = '放量上涨'
            elif price_change > 0 and result['ratio'] < 0.7:
                result['status'] = 'volume_down'
                result['score'] = 4
                result['desc'] = '缩量上涨'
            elif price_change < 0 and result['ratio'] > 1.5:
                result['status'] = 'volume_drop'
                result['score'] = 2
                result['desc'] = '放量下跌'
            else:
                result['status'] = 'normal'
                result['score'] = 6
                result['desc'] = '量价平稳'
        
        except:
            pass
        
        return result
    
    def _analyze_position(self, ohlcv) -> Dict:
        """位置分析 (10分)"""
        result = {
            'atr': None,
            'atr_pct': None,
            'score': 8
        }
        
        try:
            high = ohlcv['High'] if 'High' in ohlcv else ohlcv['最高']
            low = ohlcv['Low'] if 'Low' in ohlcv else ohlcv['最低']
            close = ohlcv['Close'] if 'Close' in ohlcv else ohlcv['收盘']
            
            # ATR
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            
            result['atr'] = round(atr, 4)
            result['atr_pct'] = round(atr / close.iloc[-1] * 100, 2)
            
            # 基于波动率评分
            if result['atr_pct'] < 2:
                result['score'] = 10
                result['volatility'] = 'low'
            elif result['atr_pct'] < 4:
                result['score'] = 8
                result['volatility'] = 'medium'
            else:
                result['score'] = 5
                result['volatility'] = 'high'
        
        except:
            pass
        
        return result


class AnalysisFramework:
    """
    完整的三层分析框架
    """
    
    def __init__(self):
        self.macro = MacroAnalyzer()
        self.sector = SectorAnalyzer()
        self.stock = StockAnalyzer()
    
    def analyze(self, symbol: str, market: str = 'auto') -> Dict:
        """
        完整分析
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            {
                'macro': {..., 'score': 20},
                'sector': {..., 'score': 20},
                'stock': {..., 'score': 60},
                'total_score': 100,
                'rating': 'strong/bullish/neutral/bearish/weak',
                'suggestion': '...'
            }
        """
        # 自动检测市场
        if market == 'auto':
            if symbol.isdigit():
                market = 'cn'
            elif symbol.isdigit() and len(symbol) == 5:
                market = 'hk'
            else:
                market = 'us'
        
        # 三层分析
        macro_result = self.macro.analyze(market)
        sector_result = self.sector.analyze(symbol)
        stock_result = self.stock.analyze(symbol)
        
        # 总分
        total_score = (
            macro_result['total_score'] +
            sector_result['total_score'] +
            stock_result['total_score']
        )
        
        # 评级
        if total_score >= 80:
            rating = 'strong'
            suggestion = '强势 - 可积极参与'
        elif total_score >= 65:
            rating = 'bullish'
            suggestion = '偏强 - 可适度参与'
        elif total_score >= 50:
            rating = 'neutral'
            suggestion = '中性 - 观望为主'
        elif total_score >= 35:
            rating = 'bearish'
            suggestion = '偏弱 - 谨慎'
        else:
            rating = 'weak'
            suggestion = '弱势 - 回避'
        
        return {
            'symbol': symbol,
            'market': market,
            'macro': macro_result,
            'sector': sector_result,
            'stock': stock_result,
            'total_score': total_score,
            'rating': rating,
            'suggestion': suggestion,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def analyze_full(symbol: str, market: str = 'auto') -> Dict:
    """完整分析入口"""
    framework = AnalysisFramework()
    return framework.analyze(symbol, market)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='三层分析框架')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--market', default='auto', help='市场类型')
    
    args = parser.parse_args()
    
    result = analyze_full(args.symbol, args.market)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
```

---

## 📊 Darwin Skill 评估标准

整合后的模块将通过以下 8 维度评估：

| 维度 | 权重 | 评估要点 |
|------|------|---------|
| **Frontmatter质量** | 8 | name规范、description完整 |
| **工作流清晰度** | 15 | 步骤明确、输入输出清晰 |
| **边界条件覆盖** | 10 | 异常处理、fallback |
| **检查点设计** | 7 | 用户确认点 |
| **指令具体性** | 15 | 参数明确、可执行 |
| **资源整合度** | 5 | 路径正确 |
| **整体架构** | 15 | 层次清晰 |
| **实测表现** | 25 | 测试prompt验证 |

---

## 🎯 下一步

1. 创建上述模块文件
2. 运行测试验证
3. 使用 Darwin Skill 评估
4. 持续优化迭代

---

**饕餮整合方案已规划，立即开始实施！** 🚀
