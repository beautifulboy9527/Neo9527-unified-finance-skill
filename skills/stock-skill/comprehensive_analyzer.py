#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票综合分析增强版 v3.0
整合所有分析维度：技术、基本面、新闻、情绪、行业、竞争
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime
import importlib.util

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_module(name, path):
    """动态加载模块"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComprehensiveStockAnalyzer:
    """股票综合分析器"""
    
    def __init__(self):
        self.name = "ComprehensiveStockAnalyzer"
        self.version = "3.0.0"
        
        # 加载模块
        self._load_modules()
    
    def _load_modules(self):
        """加载分析模块"""
        # 快速分析
        try:
            self.analyzer = load_module(
                "analyzer",
                os.path.join(BASE_DIR, "skills", "stock-skill", "analyzer.py")
            )
        except:
            self.analyzer = None
        
        # 财务异常检测
        try:
            self.financial_check = load_module(
                "financial_check",
                os.path.join(BASE_DIR, "skills", "stock-skill", "financial_check.py")
            )
        except:
            self.financial_check = None
        
        # 估值计算
        try:
            self.valuation = load_module(
                "valuation",
                os.path.join(BASE_DIR, "skills", "stock-skill", "valuation.py")
            )
        except:
            self.valuation = None
        
        # 深度研报
        try:
            sys.path.insert(0, os.path.join(BASE_DIR, "skills", "stock-skill", "deep-research"))
            self.deep_research = load_module(
                "deep_research",
                os.path.join(BASE_DIR, "skills", "stock-skill", "deep-research", "analyzer.py")
            )
        except:
            self.deep_research = None
        
        # 新闻分析
        try:
            self.news = load_module(
                "news",
                os.path.join(BASE_DIR, "scripts", "features", "news.py")
            )
            print("   新闻模块加载成功") if self.news else print("   新闻模块为空")
        except Exception as e:
            print(f"   新闻模块加载失败: {e}")
            self.news = None
        
        # 情绪分析
        try:
            self.sentiment = load_module(
                "sentiment_enhanced",
                os.path.join(BASE_DIR, "scripts", "features", "sentiment_enhanced.py")
            )
            print("   情绪模块加载成功") if self.sentiment else print("   情绪模块为空")
        except Exception as e:
            print(f"   情绪模块加载失败: {e}")
            self.sentiment = None
    
    def analyze(self, symbol: str, style: str = 'value') -> Dict:
        """
        综合分析
        
        Args:
            symbol: 股票代码
            style: 投资风格
            
        Returns:
            综合分析报告
        """
        print(f"\n{'='*70}")
        print(f" {symbol} 综合分析报告")
        print(f"{'='*70}")
        
        report = {
            'success': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'style': style,
            'sections': {},
            'overall': {}
        }
        
        # 1. 快速技术分析
        print("\n【1/7】技术分析...")
        if self.analyzer:
            try:
                result = self.analyzer.analyze_stock(symbol)
                if result['success']:
                    report['sections']['technical'] = {
                        'score': result['score'],
                        'trend': result['data'].get('technical', {}).get('trend'),
                        'rsi': result['data'].get('technical', {}).get('rsi'),
                        'macd_status': result['data'].get('technical', {}).get('macd_status'),
                        'signals': len(result['signals'])
                    }
                    print(f"   ✅ 趋势: {report['sections']['technical']['trend']}")
                    print(f"   ✅ 评分: {result['score']}/100")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 2. 基本面分析
        print("\n【2/7】基本面分析...")
        if self.analyzer:
            try:
                result = self.analyzer.analyze_stock(symbol)
                if result['success']:
                    fund = result['data'].get('fundamentals', {})
                    report['sections']['fundamentals'] = {
                        'pe': fund.get('pe'),
                        'pb': fund.get('pb'),
                        'roe': fund.get('roe'),
                        'market_cap': fund.get('market_cap'),
                    }
                    print(f"   ✅ P/E: {fund.get('pe', 'N/A')}")
                    print(f"   ✅ ROE: {fund.get('roe', 'N/A')}%")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 3. 财务异常检测
        print("\n【3/7】财务异常检测...")
        if self.financial_check:
            try:
                result = self.financial_check.check_financial_anomaly(symbol)
                if result['success']:
                    report['sections']['financial_check'] = {
                        'risk_level': result['risk_level'],
                        'risk_description': result['risk_description'],
                        'anomaly_count': result['anomaly_count'],
                        'gross_margin': result.get('financial_data', {}).get('gross_margin'),
                        'net_margin': result.get('financial_data', {}).get('net_margin'),
                    }
                    print(f"   ✅ 风险等级: {result['risk_description']}")
                    print(f"   ✅ 异常数量: {result['anomaly_count']}")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 4. 估值分析
        print("\n【4/7】估值分析...")
        if self.valuation:
            try:
                result = self.valuation.calculate_valuation(symbol)
                if result['success']:
                    report['sections']['valuation'] = {
                        'current_price': result['current_price'],
                        'fair_value': result['fair_value'],
                        'safe_price': result['safe_price'],
                        'margin_of_safety': result['margin_of_safety'],
                        'upside': ((result['fair_value'] - result['current_price']) / result['current_price'] * 100) if result['current_price'] > 0 else 0
                    }
                    print(f"   ✅ 公允价值: ${result['fair_value']:.2f}")
                    print(f"   ✅ 上涨空间: {report['sections']['valuation']['upside']:.1f}%")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 5. 新闻分析
        print("\n【5/7】新闻分析...")
        if self.news:
            try:
                # 尝试获取新闻
                result = self.news.get_financial_brief()
                if result:
                    report['sections']['news'] = {
                        'available': True,
                        'brief': str(result)[:500] if result else 'N/A'
                    }
                    print(f"   ✅ 新闻数据已获取")
            except Exception as e:
                print(f"   ⚠️ 新闻获取失败: {str(e)[:50]}")
        else:
            print(f"   ⚠️ 新闻模块未加载")
        
        # 6. 情绪分析
        print("\n【6/7】市场情绪...")
        if self.sentiment:
            try:
                result = self.sentiment.analyze_sentiment(symbol)
                if result and result.get('success'):
                    report['sections']['sentiment'] = {
                        'score': result.get('sentiment_score', 0),
                        'bullish_pct': result.get('bullish_percentage', 0),
                        'bearish_pct': result.get('bearish_percentage', 0),
                        'status': result.get('sentiment_status', 'N/A')
                    }
                    print(f"   ✅ 情绪评分: {result.get('sentiment_score', 0):.1f}/100")
                    print(f"   ✅ 看涨: {result.get('bullish_percentage', 0):.0f}%")
            except Exception as e:
                print(f"   ⚠️ 情绪分析失败: {str(e)[:50]}")
        else:
            print(f"   ⚠️ 情绪模块未加载")
        
        # 7. 深度研报
        print("\n【7/7】深度研报...")
        if self.deep_research:
            try:
                style_enum = getattr(self.deep_research.InvestmentStyle, style.upper(), self.deep_research.InvestmentStyle.VALUE)
                analyzer = self.deep_research.StockAnalyzer(style=style_enum)
                result = analyzer.analyze(symbol, depth='quick')
                if result:
                    report['sections']['deep_research'] = {
                        'rating': result['rating']['rating'],
                        'score': result['rating']['score'],
                        'recommendation': result['rating']['recommendation']
                    }
                    print(f"   ✅ 评级: {result['rating']['rating']}")
                    print(f"   ✅ 建议: {result['rating']['recommendation']}")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 计算综合评分
        report['overall'] = self._calculate_overall(report['sections'])
        
        print(f"\n{'='*70}")
        print(f" 综合评分: {report['overall']['score']}/100")
        print(f" 投资建议: {report['overall']['recommendation']}")
        print(f"{'='*70}")
        
        return report
    
    def _calculate_overall(self, sections: Dict) -> Dict:
        """计算综合评分"""
        score = 0
        weights = {
            'technical': 0.15,
            'fundamentals': 0.25,
            'financial_check': 0.20,
            'valuation': 0.20,
            'sentiment': 0.10,
            'deep_research': 0.10
        }
        
        # 技术分析
        if 'technical' in sections:
            score += sections['technical']['score'] * weights['technical']
        
        # 基本面
        if 'fundamentals' in sections:
            fund = sections['fundamentals']
            fund_score = 50  # 基础分
            if fund.get('roe') and fund['roe'] > 15:
                fund_score += 20
            if fund.get('pe') and 0 < fund['pe'] < 20:
                fund_score += 15
            score += fund_score * weights['fundamentals']
        
        # 财务异常
        if 'financial_check' in sections:
            risk_level = sections['financial_check'].get('risk_level', 0)
            if isinstance(risk_level, str):
                risk_level = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}.get(risk_level, 0)
            risk_score = 100 - (risk_level * 20)
            score += risk_score * weights['financial_check']
        
        # 估值
        if 'valuation' in sections:
            val = sections['valuation']
            if val['upside'] > 30:
                val_score = 90
            elif val['upside'] > 10:
                val_score = 70
            elif val['upside'] > 0:
                val_score = 50
            else:
                val_score = 30
            score += val_score * weights['valuation']
        
        # 情绪
        if 'sentiment' in sections:
            score += sections['sentiment']['score'] * weights['sentiment']
        
        # 深度研报
        if 'deep_research' in sections:
            deep_score = sections['deep_research']['score'] * 20
            score += deep_score * weights['deep_research']
        
        score = min(100, max(0, score))
        
        # 建议
        if score >= 80:
            recommendation = "强烈买入 🚀"
        elif score >= 65:
            recommendation = "买入 ✅"
        elif score >= 50:
            recommendation = "持有 ⏸️"
        elif score >= 35:
            recommendation = "卖出 ⚠️"
        else:
            recommendation = "强烈卖出 ❌"
        
        return {
            'score': round(score, 1),
            'recommendation': recommendation
        }
    
    def generate_report(self, report: Dict) -> str:
        """生成 Markdown 报告"""
        symbol = report['symbol']
        
        md = f"""# {symbol} 综合投资分析报告

**生成时间**: {report['timestamp']}  
**投资风格**: {report['style']}

---

## 📊 综合评分

| 评分 | 建议 |
|------|------|
| **{report['overall']['score']}/100** | {report['overall']['recommendation']} |

---

## 分析详情

"""
        
        # 技术分析
        if 'technical' in report['sections']:
            tech = report['sections']['technical']
            trend = tech.get('trend') or 'N/A'
            rsi = tech.get('rsi') or 0
            macd = tech.get('macd_status') or 'N/A'
            signals = tech.get('signals') or 0
            md += f"""### 1. 技术分析

| 指标 | 值 |
|------|------|
| 趋势 | {trend} |
| RSI | {rsi:.1f} |
| MACD | {macd} |
| 信号数 | {signals} |

"""
        
        # 基本面
        if 'fundamentals' in report['sections']:
            fund = report['sections']['fundamentals']
            md += f"""### 2. 基本面分析 💼

| 指标 | 值 |
|------|------|
| P/E | {fund.get('pe', 'N/A')} |
| P/B | {fund.get('pb', 'N/A')} |
| ROE | {fund.get('roe', 'N/A')}% |
| 市值 | {fund.get('market_cap', 'N/A')} |

"""
        
        # 财务异常
        if 'financial_check' in report['sections']:
            fc = report['sections']['financial_check']
            md += f"""### 3. 财务异常检测 🔍

| 指标 | 值 |
|------|------|
| 风险等级 | {fc['risk_description']} |
| 异常数量 | {fc['anomaly_count']} |
| 毛利率 | {fc.get('gross_margin', 0):.1f}% |
| 净利率 | {fc.get('net_margin', 0):.1f}% |

"""
        
        # 估值
        if 'valuation' in report['sections']:
            val = report['sections']['valuation']
            md += f"""### 4. 估值分析 💰

| 指标 | 值 |
|------|------|
| 当前价格 | ${val['current_price']:.2f} |
| 公允价值 | ${val['fair_value']:.2f} |
| 安全价格 | ${val['safe_price']:.2f} |
| 上涨空间 | {val['upside']:.1f}% |

"""
        
        # 情绪
        if 'sentiment' in report['sections']:
            sent = report['sections']['sentiment']
            md += f"""### 5. 市场情绪 😊

| 指标 | 值 |
|------|------|
| 情绪评分 | {sent['score']:.1f}/100 |
| 看涨比例 | {sent['bullish_pct']:.0f}% |
| 看跌比例 | {sent['bearish_pct']:.0f}% |
| 状态 | {sent['status']} |

"""
        
        # 深度研报
        if 'deep_research' in report['sections']:
            dr = report['sections']['deep_research']
            md += f"""### 6. 深度研报 📑

| 指标 | 值 |
|------|------|
| 评级 | {dr['rating']} |
| 评分 | {dr['score']}/5 |
| 建议 | {dr['recommendation']} |

"""
        
        md += """---

## ⚠️ 风险提示

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

*报告由 Neo9527 Finance Agent v5.3 生成*
"""
        
        return md


# 快速使用函数
def analyze_comprehensive(symbol: str, style: str = 'value') -> Dict:
    """综合分析"""
    analyzer = ComprehensiveStockAnalyzer()
    return analyzer.analyze(symbol, style)


# 测试
if __name__ == '__main__':
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else '002050'
    
    analyzer = ComprehensiveStockAnalyzer()
    report = analyzer.analyze(symbol, style='value')
    
    # 生成报告
    md = analyzer.generate_report(report)
    
    # 保存
    output_file = f'D:\\OpenClaw\\outputs\\reports\\comprehensive_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"\n✅ 报告已保存: {output_file}")
