#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock Daily Analyzer - 日频技术分析
整合自 stock-daily-analysis 的技术分析能力
"""

import sys
import os
import json
import argparse
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class TechnicalIndicators:
    """技术指标"""
    ma5: float
    ma10: float
    ma20: float
    bias_ma5: float  # 乖离率
    macd_status: str  # 金叉/死叉
    rsi_status: str  # 超买/超卖/中性
    buy_signal: str  # 买入/卖出/观望
    signal_score: int  # 信号评分 0-100


@dataclass  
class AIAnalysis:
    """AI 分析结果"""
    sentiment_score: int  # 情绪评分 0-100
    operation_advice: str  # 买入/卖出/观望
    confidence_level: str  # 高/中/低
    target_price: str
    stop_loss: str


@dataclass
class AnalysisResult:
    """分析结果"""
    code: str
    name: str
    current_price: float
    change_pct: float
    technical_indicators: TechnicalIndicators
    ai_analysis: AIAnalysis


class StockAnalyzer:
    """股票日频技术分析器"""
    
    def __init__(self, code: str, name: str = ""):
        self.code = code
        self.name = name
        
    def calculate_ma(self, prices: list, period: int) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        return sum(prices[-period:]) / period
    
    def calculate_bias(self, price: float, ma: float) -> float:
        """计算乖离率"""
        return (price - ma) / ma * 100 if ma > 0 else 0
    
    def analyze_macd(self, prices: list) -> str:
        """
        分析 MACD
        简化版: 基于短期 vs 长期均线交叉
        """
        if len(prices) < 26:
            return "数据不足"
        
        ma12 = self.calculate_ma(prices, 12)
        ma26 = self.calculate_ma(prices, 26)
        
        if ma12 > ma26:
            return "金叉 (看涨)"
        else:
            return "死叉 (看跌)"
    
    def analyze_rsi(self, prices: list, period: int = 14) -> Tuple[str, float]:
        """
        分析 RSI
        返回: (状态, RSI值)
        """
        if len(prices) < period + 1:
            return "数据不足", 50
        
        gains = []
        losses = []
        
        for i in range(len(prices) - period, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return "极度强势", 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi >= 70:
            status = "超买"
        elif rsi <= 30:
            status = "超卖"
        elif rsi >= 55:
            status = "强势买入"
        elif rsi <= 45:
            status = "弱势卖出"
        else:
            status = "中性"
            
        return status, rsi
    
    def generate_buy_signal(self, 
                            ma5: float, ma10: float, ma20: float,
                            current_price: float,
                            macd_status: str,
                            rsi_status: str) -> Tuple[str, int]:
        """
        生成买卖信号
        
        Returns: (信号, 评分 0-100)
        """
        score = 50  # 基础分
        
        # 均线多头排列
        if ma5 > ma10 > ma20:
            score += 20
        elif ma5 < ma10 < ma20:
            score -= 20
            
        # 价格在均线上方
        if current_price > ma20:
            score += 10
        else:
            score -= 10
            
        # MACD 信号
        if "金叉" in macd_status:
            score += 15
        elif "死叉" in macd_status:
            score -= 15
            
        # RSI 状态
        if "超卖" in rsi_status:
            score += 10
        elif "超买" in rsi_status:
            score -= 10
        elif "强势买入" in rsi_status:
            score += 5
        elif "弱势卖出" in rsi_status:
            score -= 5
        
        # 确保分数在 0-100 范围内
        score = max(0, min(100, score))
        
        if score >= 70:
            signal = "买入"
        elif score <= 30:
            signal = "卖出"
        else:
            signal = "观望"
            
        return signal, score
    
    def determine_trend(self, 
                        ma5: float, ma10: float, ma20: float,
                        current_price: float) -> str:
        """判断趋势"""
        if ma5 > ma10 > ma20 and current_price > ma5:
            return "强势多头"
        elif ma5 < ma10 < ma20 and current_price < ma5:
            return "强势空头"
        elif ma5 > ma10 and current_price > ma5:
            return "震荡偏多"
        elif ma5 < ma10 and current_price < ma5:
            return "震荡偏空"
        else:
            return "震荡整理"
    
    def analyze(self, price_data: Dict) -> AnalysisResult:
        """
        综合技术分析
        
        Args:
            price_data: {
                "current_price": float,
                "prices_30d": list,  # 近30日收盘价
                "name": str
            }
        """
        current_price = price_data.get('current_price', 0)
        prices = price_data.get('prices_30d', [])
        name = price_data.get('name', self.name)
        
        if len(prices) < 20:
            return AnalysisResult(
                code=self.code,
                name=name,
                current_price=current_price,
                change_pct=0,
                technical_indicators=TechnicalIndicators(
                    ma5=0, ma10=0, ma20=0,
                    bias_ma5=0,
                    macd_status="数据不足",
                    rsi_status="数据不足",
                    buy_signal="观望",
                    signal_score=50
                ),
                ai_analysis=AIAnalysis(
                    sentiment_score=50,
                    operation_advice="观望",
                    confidence_level="低",
                    target_price="",
                    stop_loss=""
                )
            )
        
        # 计算均线
        ma5 = self.calculate_ma(prices, 5)
        ma10 = self.calculate_ma(prices, 10)
        ma20 = self.calculate_ma(prices, 20)
        
        # 乖离率
        bias_ma5 = self.calculate_bias(current_price, ma5)
        
        # MACD
        macd_status = self.analyze_macd(prices)
        
        # RSI
        rsi_status, rsi_value = self.analyze_rsi(prices)
        
        # 趋势
        trend = self.determine_trend(ma5, ma10, ma20, current_price)
        
        # 买卖信号
        buy_signal, signal_score = self.generate_buy_signal(
            ma5, ma10, ma20, current_price, macd_status, rsi_status
        )
        
        # 价格变化
        if len(prices) >= 2:
            change_pct = (current_price - prices[-2]) / prices[-2] * 100
        else:
            change_pct = 0
        
        # AI 分析
        sentiment_score = min(100, max(0, 50 + signal_score - 50 + (30 if change_pct > 0 else -30)))
        
        # 目标价和止损价 (简化估算)
        if buy_signal == "买入":
            target_price = f"{current_price * 1.15:.2f}"  # 15% 上涨目标
            stop_loss = f"{current_price * 0.95:.2f}"  # 5% 止损
        elif buy_signal == "卖出":
            target_price = f"{current_price * 0.85:.2f}"
            stop_loss = f"{current_price * 1.05:.2f}"
        else:
            target_price = "参考支撑/压力位"
            stop_loss = "参考支撑/压力位"
        
        confidence = "高" if signal_score >= 70 or signal_score <= 30 else "中"
        
        return AnalysisResult(
            code=self.code,
            name=name,
            current_price=current_price,
            change_pct=change_pct,
            technical_indicators=TechnicalIndicators(
                ma5=ma5,
                ma10=ma10,
                ma20=ma20,
                bias_ma5=bias_ma5,
                macd_status=macd_status,
                rsi_status=rsi_status,
                buy_signal=buy_signal,
                signal_score=signal_score
            ),
            ai_analysis=AIAnalysis(
                sentiment_score=sentiment_score,
                operation_advice=buy_signal,
                confidence_level=confidence,
                target_price=target_price,
                stop_loss=stop_loss
            )
        )


def main():
    parser = argparse.ArgumentParser(description='日频技术分析器')
    parser.add_argument('--code', required=True, help='股票代码')
    parser.add_argument('--name', default='', help='股票名称')
    parser.add_argument('--period', default='1mo', choices=['1w', '1mo', '3mo'], help='分析周期')
    parser.add_argument('--output', default='analysis_result.json', help='输出文件')
    
    args = parser.parse_args()
    
    # 示例数据 (实际使用时从 data_fetcher 获取)
    import random
    base_price = 1500.0
    sample_prices = [base_price * (1 + random.uniform(-0.03, 0.03)) for _ in range(30)]
    
    sample_data = {
        "current_price": sample_prices[-1],
        "prices_30d": sample_prices,
        "name": args.name or "示例股票"
    }
    
    analyzer = StockAnalyzer(args.code, sample_data['name'])
    result = analyzer.analyze(sample_data)
    
    print(f"[Chart] {result.code} Daily Technical Analysis")
    print(f"当前价格: {result.current_price:.2f} ({result.change_pct:+.2f}%)")
    print()
    print("【技术指标】")
    print(f"  MA5:  {result.technical_indicators.ma5:.2f}")
    print(f"  MA10: {result.technical_indicators.ma10:.2f}")
    print(f"  MA20: {result.technical_indicators.ma20:.2f}")
    print(f"  乖离率(MA5): {result.technical_indicators.bias_ma5:.2f}%")
    print(f"  MACD: {result.technical_indicators.macd_status}")
    print(f"  RSI: {result.technical_indicators.rsi_status}")
    print(f"  买卖信号: {result.technical_indicators.buy_signal} (评分: {result.technical_indicators.signal_score})")
    print()
    print("【AI 决策建议】")
    print(f"  情绪评分: {result.ai_analysis.sentiment_score}/100")
    print(f"  操作建议: {result.ai_analysis.operation_advice}")
    print(f"  置信度: {result.ai_analysis.confidence_level}")
    print(f"  目标价: {result.ai_analysis.target_price}")
    print(f"  止损价: {result.ai_analysis.stop_loss}")
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump({
            'code': result.code,
            'name': result.name,
            'current_price': result.current_price,
            'change_pct': result.change_pct,
            'technical_indicators': {
                'ma5': result.technical_indicators.ma5,
                'ma10': result.technical_indicators.ma10,
                'ma20': result.technical_indicators.ma20,
                'bias_ma5': result.technical_indicators.bias_ma5,
                'macd_status': result.technical_indicators.macd_status,
                'rsi_status': result.technical_indicators.rsi_status,
                'buy_signal': result.technical_indicators.buy_signal,
                'signal_score': result.technical_indicators.signal_score
            },
            'ai_analysis': {
                'sentiment_score': result.ai_analysis.sentiment_score,
                'operation_advice': result.ai_analysis.operation_advice,
                'confidence_level': result.ai_analysis.confidence_level,
                'target_price': result.ai_analysis.target_price,
                'stop_loss': result.ai_analysis.stop_loss
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 结果已保存到 {args.output}")


if __name__ == '__main__':
    main()
