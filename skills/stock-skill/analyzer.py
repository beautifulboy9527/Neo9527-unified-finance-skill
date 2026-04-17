#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析 Skill v2.1

功能:
- 自动市场检测 (A股/港股/美股)
- 技术分析 (MA/RSI/MACD/趋势)
- 基本面数据 (PE/PB/市值)
- 资金流向 (仅A股)
- 信号生成和评分
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
import numpy as np

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


class StockAnalysisSkill:
    """股票分析 Skill - 快速分析模式"""
    
    def __init__(self):
        self.name = "StockAnalysisSkill"
        self.version = "2.1.0"
    
    def execute(self, symbol: str) -> Dict:
        """
        执行分析
        
        Args:
            symbol: 股票代码
            
        Returns:
            分析结果字典
        """
        print(f"开始分析 {symbol}...")
        
        # 检测市场
        market = self._detect_market(symbol)
        print(f"  市场类型: {market}")
        
        # 获取数据
        if market == 'cn':
            data = self._analyze_cn_stock(symbol)
        elif market == 'us':
            data = self._analyze_us_stock(symbol)
        else:
            data = self._analyze_hk_stock(symbol)
        
        # 生成信号
        signals = self._generate_signals(data)
        
        # 计算评分
        score = self._calculate_score(data, signals)
        
        # 整合结果
        result = {
            'skill_name': self.name,
            'success': True,
            'symbol': symbol,
            'market': market,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'signals': signals,
            'score': score,
            'summary': self._generate_summary(data, signals, score)
        }
        
        return result
    
    def _detect_market(self, symbol: str) -> str:
        """检测市场类型"""
        if symbol.isdigit() and len(symbol) == 6:
            return 'cn'  # A股
        elif symbol.endswith('.HK'):
            return 'hk'  # 港股
        else:
            return 'us'  # 美股
    
    def _analyze_cn_stock(self, symbol: str) -> Dict:
        """分析A股"""
        data = {
            'symbol': symbol,
            'market': 'cn',
            'data_source': ['akshare', 'yfinance']
        }
        
        try:
            if AKSHARE_AVAILABLE:
                # 使用 AkShare 获取A股数据
                try:
                    # 实时行情
                    df = ak.stock_zh_a_spot_em()
                    stock_data = df[df['代码'] == symbol]
                    
                    if not stock_data.empty:
                        row = stock_data.iloc[0]
                        data['name'] = row.get('名称', '')
                        data['price'] = float(row.get('最新价', 0))
                        data['change_pct'] = float(row.get('涨跌幅', 0))
                        data['volume'] = float(row.get('成交量', 0))
                        data['amount'] = float(row.get('成交额', 0))
                        data['high'] = float(row.get('最高', 0))
                        data['low'] = float(row.get('最低', 0))
                        data['open'] = float(row.get('今开', 0))
                        data['prev_close'] = float(row.get('昨收', 0))
                except Exception as e:
                    print(f"  AkShare实时行情失败: {e}")
                
                # 技术指标
                try:
                    tech_data = self._get_cn_technical(symbol)
                    data['technical'] = tech_data
                except Exception as e:
                    print(f"  技术指标失败: {e}")
                
                # 资金流向
                try:
                    flow_data = self._get_cn_fundflow(symbol)
                    data['fundflow'] = flow_data
                except Exception as e:
                    print(f"  资金流向失败: {e}")
                
                # 基本面
                try:
                    fin_data = self._get_cn_fundamentals(symbol)
                    data['fundamentals'] = fin_data
                except Exception as e:
                    print(f"  基本面失败: {e}")
            
            # 备用：使用 yfinance
            if 'price' not in data or data.get('price') == 0:
                yf_data = self._get_yf_data(symbol + '.SS')  # 上交所
                if yf_data:
                    data.update(yf_data)
                else:
                    yf_data = self._get_yf_data(symbol + '.SZ')  # 深交所
                    if yf_data:
                        data.update(yf_data)
        
        except Exception as e:
            print(f"  A股分析失败: {e}")
            data['error'] = str(e)
        
        return data
    
    def _analyze_us_stock(self, symbol: str) -> Dict:
        """分析美股"""
        data = {
            'symbol': symbol,
            'market': 'us',
            'data_source': ['yfinance']
        }
        
        try:
            yf_data = self._get_yf_data(symbol)
            if yf_data:
                data.update(yf_data)
                
                # 技术指标
                tech_data = self._get_technical_from_yf(symbol)
                data['technical'] = tech_data
                
                # 基本面
                fin_data = self._get_fundamentals_from_yf(symbol)
                data['fundamentals'] = fin_data
            else:
                data['error'] = '无法获取数据'
        
        except Exception as e:
            print(f"  美股分析失败: {e}")
            data['error'] = str(e)
        
        return data
    
    def _analyze_hk_stock(self, symbol: str) -> Dict:
        """分析港股"""
        data = {
            'symbol': symbol,
            'market': 'hk',
            'data_source': ['yfinance']
        }
        
        try:
            yf_data = self._get_yf_data(symbol)
            if yf_data:
                data.update(yf_data)
                
                # 技术指标
                tech_data = self._get_technical_from_yf(symbol)
                data['technical'] = tech_data
                
                # 基本面
                fin_data = self._get_fundamentals_from_yf(symbol)
                data['fundamentals'] = fin_data
            else:
                data['error'] = '无法获取数据'
        
        except Exception as e:
            print(f"  港股分析失败: {e}")
            data['error'] = str(e)
        
        return data
    
    def _get_yf_data(self, symbol: str) -> Optional[Dict]:
        """从 yfinance 获取数据"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取历史数据
            hist = ticker.history(period='1mo')
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            
            return {
                'name': info.get('longName', symbol),
                'price': float(latest['Close']),
                'change_pct': ((latest['Close'] - latest['Open']) / latest['Open'] * 100) if latest['Open'] else 0,
                'volume': float(latest['Volume']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'open': float(latest['Open']),
                'prev_close': float(hist.iloc[-2]['Close']) if len(hist) > 1 else float(latest['Open']),
            }
        except Exception as e:
            print(f"    yfinance获取失败: {e}")
            return None
    
    def _get_cn_technical(self, symbol: str) -> Dict:
        """获取A股技术指标"""
        tech = {}
        
        try:
            if AKSHARE_AVAILABLE:
                # 获取历史数据
                df = ak.stock_zh_a_hist(symbol=symbol, period='daily', adjust='qfq')
                
                if df is not None and not df.empty:
                    close = df['收盘'].astype(float)
                    volume = df['成交量'].astype(float)
                    
                    # MA
                    tech['ma5'] = float(close.rolling(5).mean().iloc[-1])
                    tech['ma10'] = float(close.rolling(10).mean().iloc[-1])
                    tech['ma20'] = float(close.rolling(20).mean().iloc[-1])
                    
                    # RSI
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs = gain / loss
                    tech['rsi'] = float(100 - (100 / (1 + rs.iloc[-1])))
                    
                    # 趋势判断
                    current_price = float(close.iloc[-1])
                    if current_price > tech['ma5'] > tech['ma10'] > tech['ma20']:
                        tech['trend'] = '强势多头'
                    elif current_price > tech['ma10'] > tech['ma20']:
                        tech['trend'] = '多头'
                    elif current_price < tech['ma5'] < tech['ma10'] < tech['ma20']:
                        tech['trend'] = '强势空头'
                    elif current_price < tech['ma10'] < tech['ma20']:
                        tech['trend'] = '空头'
                    else:
                        tech['trend'] = '震荡'
                    
                    # MACD
                    exp12 = close.ewm(span=12, adjust=False).mean()
                    exp26 = close.ewm(span=26, adjust=False).mean()
                    macd = exp12 - exp26
                    signal = macd.ewm(span=9, adjust=False).mean()
                    hist = macd - signal
                    
                    tech['macd'] = float(macd.iloc[-1])
                    tech['macd_signal'] = float(signal.iloc[-1])
                    tech['macd_hist'] = float(hist.iloc[-1])
                    tech['macd_status'] = '金叉' if hist.iloc[-1] > 0 else '死叉'
        
        except Exception as e:
            print(f"      技术指标计算失败: {e}")
        
        return tech
    
    def _get_cn_fundflow(self, symbol: str) -> Dict:
        """获取A股资金流向"""
        flow = {}
        
        try:
            if AKSHARE_AVAILABLE:
                # 个股资金流
                df = ak.stock_individual_fund_flow(stock=symbol, market='sh' if symbol.startswith('6') else 'sz')
                
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    flow['main_inflow'] = float(latest.get('主力净流入-净额', 0))
                    flow['main_inflow_pct'] = float(latest.get('主力净流入-净占比', 0))
                    flow['retail_inflow'] = float(latest.get('小单净流入-净额', 0))
                    flow['retail_inflow_pct'] = float(latest.get('小单净流入-净占比', 0))
        
        except Exception as e:
            print(f"      资金流向获取失败: {e}")
        
        return flow
    
    def _get_cn_fundamentals(self, symbol: str) -> Dict:
        """获取A股基本面"""
        fund = {}
        
        try:
            if AKSHARE_AVAILABLE:
                # 财务指标
                df = ak.stock_financial_analysis_indicator(symbol=symbol)
                
                if df is not None and not df.empty:
                    latest = df.iloc[0]
                    fund['pe'] = float(latest.get('市盈率', 0))
                    fund['pb'] = float(latest.get('市净率', 0))
                    fund['roe'] = float(latest.get('净资产收益率', 0))
                    fund['debt_ratio'] = float(latest.get('资产负债率', 0))
                    fund['gross_margin'] = float(latest.get('销售毛利率', 0))
                    fund['net_margin'] = float(latest.get('销售净利率', 0))
        
        except Exception as e:
            print(f"      基本面获取失败: {e}")
        
        return fund
    
    def _get_technical_from_yf(self, symbol: str) -> Dict:
        """从 yfinance 获取技术指标"""
        tech = {}
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='3mo')
            
            if not hist.empty:
                close = hist['Close']
                
                # MA
                tech['ma5'] = float(close.rolling(5).mean().iloc[-1])
                tech['ma10'] = float(close.rolling(10).mean().iloc[-1])
                tech['ma20'] = float(close.rolling(20).mean().iloc[-1])
                
                # RSI
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                tech['rsi'] = float(100 - (100 / (1 + rs.iloc[-1])))
                
                # 趋势判断
                current_price = float(close.iloc[-1])
                if current_price > tech['ma5'] > tech['ma10'] > tech['ma20']:
                    tech['trend'] = '强势多头'
                elif current_price > tech['ma10'] > tech['ma20']:
                    tech['trend'] = '多头'
                elif current_price < tech['ma5'] < tech['ma10'] < tech['ma20']:
                    tech['trend'] = '强势空头'
                elif current_price < tech['ma10'] < tech['ma20']:
                    tech['trend'] = '空头'
                else:
                    tech['trend'] = '震荡'
                
                # MACD
                exp12 = close.ewm(span=12, adjust=False).mean()
                exp26 = close.ewm(span=26, adjust=False).mean()
                macd = exp12 - exp26
                signal = macd.ewm(span=9, adjust=False).mean()
                hist_macd = macd - signal
                
                tech['macd'] = float(macd.iloc[-1])
                tech['macd_signal'] = float(signal.iloc[-1])
                tech['macd_hist'] = float(hist_macd.iloc[-1])
                tech['macd_status'] = '金叉' if hist_macd.iloc[-1] > 0 else '死叉'
        
        except Exception as e:
            print(f"      技术指标计算失败: {e}")
        
        return tech
    
    def _get_fundamentals_from_yf(self, symbol: str) -> Dict:
        """从 yfinance 获取基本面"""
        fund = {}
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fund['pe'] = info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0
            fund['pb'] = info.get('priceToBook', 0) or 0
            fund['market_cap'] = info.get('marketCap', 0) or 0
            fund['dividend_yield'] = (info.get('dividendYield', 0) or 0) * 100
            fund['beta'] = info.get('beta', 0) or 0
            
            # 从财务报表获取更多数据
            try:
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet
                
                if not financials.empty and not balance_sheet.empty:
                    net_income = float(financials.loc['Net Income'].iloc[0]) if 'Net Income' in financials.index else 0
                    equity = float(balance_sheet.loc['Stockholders Equity'].iloc[0]) if 'Stockholders Equity' in balance_sheet.index else 0
                    
                    if equity > 0:
                        fund['roe'] = (net_income / equity) * 100
                    else:
                        fund['roe'] = info.get('returnOnEquity', 0) or 0
            except:
                fund['roe'] = info.get('returnOnEquity', 0) or 0
            
            fund['gross_margin'] = (info.get('grossMargins', 0) or 0) * 100
            fund['net_margin'] = (info.get('profitMargins', 0) or 0) * 100
        
        except Exception as e:
            print(f"      基本面获取失败: {e}")
        
        return fund
    
    def _generate_signals(self, data: Dict) -> List[Dict]:
        """生成交易信号"""
        signals = []
        
        # 技术信号
        tech = data.get('technical', {})
        if tech:
            # RSI信号
            rsi = tech.get('rsi', 50)
            if rsi < 30:
                signals.append({
                    'type': 'technical',
                    'name': 'RSI超卖',
                    'signal': 'buy',
                    'strength': 2,
                    'description': f'RSI={rsi:.1f}，超卖区间'
                })
            elif rsi > 70:
                signals.append({
                    'type': 'technical',
                    'name': 'RSI超买',
                    'signal': 'sell',
                    'strength': 2,
                    'description': f'RSI={rsi:.1f}，超买区间'
                })
            
            # MACD信号
            macd_status = tech.get('macd_status', '')
            if '金叉' in macd_status:
                signals.append({
                    'type': 'technical',
                    'name': 'MACD金叉',
                    'signal': 'buy',
                    'strength': 1,
                    'description': 'MACD金叉，看涨信号'
                })
            elif '死叉' in macd_status:
                signals.append({
                    'type': 'technical',
                    'name': 'MACD死叉',
                    'signal': 'sell',
                    'strength': 1,
                    'description': 'MACD死叉，看跌信号'
                })
            
            # 趋势信号
            trend = tech.get('trend', '')
            if '多头' in trend:
                signals.append({
                    'type': 'technical',
                    'name': '趋势向上',
                    'signal': 'buy',
                    'strength': 1 if '强势' not in trend else 2,
                    'description': f'趋势: {trend}'
                })
            elif '空头' in trend:
                signals.append({
                    'type': 'technical',
                    'name': '趋势向下',
                    'signal': 'sell',
                    'strength': 1 if '强势' not in trend else 2,
                    'description': f'趋势: {trend}'
                })
        
        # 资金流向信号 (仅A股)
        flow = data.get('fundflow', {})
        if flow:
            main_pct = flow.get('main_inflow_pct', 0)
            if main_pct > 5:
                signals.append({
                    'type': 'fundflow',
                    'name': '主力资金流入',
                    'signal': 'buy',
                    'strength': 2,
                    'description': f'主力净流入{main_pct:.1f}%'
                })
            elif main_pct < -5:
                signals.append({
                    'type': 'fundflow',
                    'name': '主力资金流出',
                    'signal': 'sell',
                    'strength': 2,
                    'description': f'主力净流出{abs(main_pct):.1f}%'
                })
        
        return signals
    
    def _calculate_score(self, data: Dict, signals: List[Dict]) -> int:
        """计算综合评分 (0-100)"""
        base_score = 50
        
        # 信号权重
        for signal in signals:
            if signal['signal'] == 'buy':
                base_score += signal['strength'] * 5
            else:
                base_score -= signal['strength'] * 5
        
        # 基本面调整
        fund = data.get('fundamentals', {})
        if fund:
            # ROE
            roe = fund.get('roe', 0)
            if roe > 20:
                base_score += 5
            elif roe > 15:
                base_score += 3
            elif roe < 5:
                base_score -= 5
            
            # PE
            pe = fund.get('pe', 0)
            if 0 < pe < 15:
                base_score += 5
            elif pe > 50:
                base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _generate_summary(self, data: Dict, signals: List[Dict], score: int) -> str:
        """生成摘要"""
        trend = data.get('technical', {}).get('trend', '未知')
        
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if score >= 70:
            rating = '买入'
        elif score >= 55:
            rating = '持有偏多'
        elif score >= 45:
            rating = '持有'
        elif score >= 30:
            rating = '持有偏空'
        else:
            rating = '卖出'
        
        summary = f"综合评分: {score}/100, 建议: {rating}, 趋势: {trend}"
        
        if buy_signals:
            summary += f", 买入信号: {len(buy_signals)}个"
        if sell_signals:
            summary += f", 卖出信号: {len(sell_signals)}个"
        
        return summary


# 快速使用函数
def analyze_stock(symbol: str) -> Dict:
    """快速分析股票"""
    skill = StockAnalysisSkill()
    return skill.execute(symbol)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("股票分析 Skill v2.1 测试")
    print("=" * 60)
    
    # 测试美股
    result = analyze_stock('AAPL')
    print(f"\n=== {result['symbol']} ({result['market']}) ===")
    print(f"名称: {result['data'].get('name', 'N/A')}")
    print(f"价格: ${result['data'].get('price', 0):.2f}")
    print(f"评分: {result['score']}/100")
    print(f"信号: {len(result['signals'])}个")
    print(f"摘要: {result['summary']}")
