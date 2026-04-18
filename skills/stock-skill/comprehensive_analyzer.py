#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票综合分析增强版 v6.3
整合所有分析维度：技术、基本面、情绪、监管、深度研报
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
        
        # 监管监控
        try:
            self.regulation = load_module(
                "regulation_monitor",
                os.path.join(BASE_DIR, "skills", "stock-skill", "regulation_monitor.py")
            )
            print("   监管模块加载成功") if self.regulation else print("   监管模块为空")
        except Exception as e:
            print(f"   监管模块加载失败: {e}")
            self.regulation = None
        
        # 报告增强工具
        try:
            self.report_enhancer = load_module(
                "report_enhancer",
                os.path.join(BASE_DIR, "skills", "shared", "report_enhancer.py")
            )
            print("   报告增强工具加载成功") if self.report_enhancer else print("   报告增强工具为空")
        except Exception as e:
            print(f"   报告增强工具加载失败: {e}")
            self.report_enhancer = None
        
        # 报告结构优化器
        try:
            self.report_structure = load_module(
                "report_structure",
                os.path.join(BASE_DIR, "skills", "shared", "report_structure.py")
            )
            print("   报告结构优化器加载成功") if self.report_structure else print("   报告结构优化器为空")
        except Exception as e:
            print(f"   报告结构优化器加载失败: {e}")
            self.report_structure = None
    
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
        
        # 5. 新闻分析 (用于选股，不用于个股分析)
        # 注: 新闻分析改为选股筛选使用，个股报告不再包含
        print("\n【5/8】新闻分析... (已跳过，用于选股)")
        
        # 6. 情绪分析
        print("\n【6/8】市场情绪...")
        if self.sentiment:
            try:
                result = self.sentiment.analyze_sentiment(symbol)
                if result and ('sentiment' in result or 'avg_bullish_pct' in result):
                    report['sections']['sentiment'] = {
                        'score': result.get('avg_bullish_pct', result.get('sentiment_score', 50)),
                        'bullish_pct': result.get('avg_bullish_pct', result.get('bullish_percentage', 50)),
                        'bearish_pct': 100 - result.get('avg_bullish_pct', result.get('bullish_percentage', 50)),
                        'status': result.get('sentiment', 'neutral'),
                        'description': result.get('sentiment_description', 'N/A'),
                        'alignment': result.get('alignment', 'local')
                    }
                    print(f"   ✅ 情绪状态: {result.get('sentiment', 'N/A')}")
                    print(f"   ✅ 看涨比例: {result.get('avg_bullish_pct', 0):.1f}%")
                    print(f"   ✅ 数据来源: {result.get('alignment', 'local')}")
            except Exception as e:
                print(f"   ⚠️ 情绪分析失败: {str(e)[:50]}")
        else:
            print(f"   ⚠️ 情绪模块未加载")
        
        # 7. 监管风险分析
        print("\n【7/8】监管风险分析...")
        if self.regulation:
            try:
                result = self.regulation.check_regulation_risk(symbol)
                if result['success']:
                    report['sections']['regulation'] = {
                        'risk_score': result['risk_score'],
                        'risk_level': result['risk_level'],
                        'risk_description': result['risk_description'],
                        'alerts_count': result['alerts_count']
                    }
                    print(f"   ✅ 风险等级: {result['risk_description']}")
                    print(f"   ✅ 风险评分: {result['risk_score']}/100")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 8. 深度研报
        print("\n【8/8】深度研报...")
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
            'technical': 0.12,
            'fundamentals': 0.20,
            'financial_check': 0.18,
            'valuation': 0.18,
            'sentiment': 0.08,
            'regulation': 0.12,
            'deep_research': 0.12
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
            upside = val['upside']
            if upside > 30:
                val_score = 90  # 大幅低估
            elif upside > 10:
                val_score = 70  # 适度低估
            elif upside > 0:
                val_score = 50  # 合理区间
            elif upside > -20:
                val_score = 30  # 适度高估
            elif upside > -50:
                val_score = 15  # 明显高估
            else:
                val_score = 5   # 严重高估
            score += val_score * weights['valuation']
        
        # 情绪
        if 'sentiment' in sections:
            score += sections['sentiment']['score'] * weights['sentiment']
        
        # 监管风险
        if 'regulation' in sections:
            reg_score = 100 - sections['regulation']['risk_score']
            score += reg_score * weights['regulation']
        
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
            rsi = tech.get('rsi') or 50
            macd = tech.get('macd_status') or 'N/A'
            signals = tech.get('signals') or 0
            
            # RSI 解读
            rsi_interp = self.report_enhancer.interpret_rsi(rsi)
            
            # 趋势解读
            trend_interp = self.report_enhancer.interpret_trend(trend, rsi)
            
            # 技术形态
            patterns = self.report_enhancer.get_technical_patterns(report['sections'])
            
            md += f"""### 1. 技术分析

**趋势判断**: {trend}

> {trend_interp}

**关键指标**:

| 指标 | 值 | 解读 |
|------|------|------|
| RSI | {rsi:.1f} | {rsi_interp['color']} {rsi_interp['status']} |
| MACD | {macd} | {'看涨信号' if '金叉' in macd else '看跌信号' if '死叉' in macd else '中性'} |
| 信号数 | {signals} | {'多头优势' if signals > 0 else '空头优势'} |

**RSI分析**: {rsi_interp['description']}

"""
            
            if patterns:
                md += "**技术形态**:\n"
                for p in patterns:
                    md += f"- **{p['name']}**: {p['description']} ({p['signal']})\n"
                md += "\n"
        
        # 基本面
        if 'fundamentals' in report['sections']:
            fund = report['sections']['fundamentals']
            pe = fund.get('pe')
            pb = fund.get('pb')
            roe = fund.get('roe')
            market_cap = fund.get('market_cap')
            
            # PE 解读
            pe_interp = self.report_enhancer.interpret_pe(pe) if pe else None
            
            # ROE 解读
            roe_interp = self.report_enhancer.interpret_roe(roe) if roe else None
            
            # 市值格式化
            mc_str = self.report_enhancer.format_number(market_cap, 'market_cap') if market_cap else 'N/A'
            
            pe_str = f"{pe:.1f}" if pe else "N/A"
            pb_str = f"{pb:.2f}" if pb else "N/A"
            roe_str = f"{roe:.1f}%" if roe else "N/A"
            
            pe_vs = pe_interp['vs_industry'] if pe_interp else 'N/A'
            pe_status = pe_interp['status'] if pe_interp else 'N/A'
            pb_status = '低估' if pb and pb < 3 else '合理' if pb and pb < 5 else '偏高'
            
            roe_rating = roe_interp['rating'] if roe_interp else 'N/A'
            roe_desc = roe_interp['description'] if roe_interp else 'N/A'
            
            md += f"""### 2. 基本面分析

**估值指标**:

| 指标 | 值 | 行业对比 | 解读 |
|------|------|---------|------|
| P/E | {pe_str} | {pe_vs} | {pe_status} |
| P/B | {pb_str} | - | {pb_status} |
| 市值 | {mc_str} | - | - |

**盈利能力**:

| 指标 | 值 | 评级 | 解读 |
|------|------|------|------|
| ROE | {roe_str} | {roe_rating} | {roe_desc} |

"""
            
            if pe_interp:
                md += f"**PE分析**: {pe_interp['description']}\n\n"
        
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
            upside = val['upside']
            if upside > 0:
                upside_desc = f"上涨空间 {upside:.1f}%"
            else:
                upside_desc = f"高估幅度 {abs(upside):.1f}%"
            md += f"""### 4. 估值分析

| 指标 | 值 |
|------|------|
| 当前价格 | ${val['current_price']:.2f} |
| 公允价值 | ${val['fair_value']:.2f} |
| 安全价格 | ${val['safe_price']:.2f} |
| 估值评估 | {upside_desc} |

"""
        
        # 新闻
        if 'news' in report['sections']:
            news = report['sections']['news']
            md += f"""### 5. 新闻分析

| 指标 | 值 |
|------|------|
| 新闻总数 | {news.get('total_news', 0)} |
| 数据来源 | {news.get('sources', {})} |

"""
            if news.get('headlines'):
                md += "**头条新闻**:\n"
                for h in news['headlines'][:3]:
                    md += f"- {h}\n"
                md += "\n"
        
        # 情绪
        if 'sentiment' in report['sections']:
            sent = report['sections']['sentiment']
            md += f"""### 6. 市场情绪

| 指标 | 值 |
|------|------|
| 情绪状态 | {sent.get('status', 'N/A')} |
| 情绪描述 | {sent.get('description', 'N/A')} |
| 看涨比例 | {sent['bullish_pct']:.1f}% |
| 看跌比例 | {sent['bearish_pct']:.1f}% |
| 数据来源 | {sent.get('alignment', 'local')} |

"""
        
        # 监管风险
        if 'regulation' in report['sections']:
            reg = report['sections']['regulation']
            md += f"""### 7. 监管风险

| 指标 | 值 |
|------|------|
| 风险评分 | {reg['risk_score']}/100 |
| 风险等级 | {reg['risk_level']} |
| 风险描述 | {reg['risk_description']} |
| 警报数量 | {reg['alerts_count']} |

"""
        
        # 深度研报
        if 'deep_research' in report['sections']:
            dr = report['sections']['deep_research']
            md += f"""### 8. 深度研报

| 指标 | 值 | 解读 |
|------|------|------|
| 评级 | {dr['rating']} | {'基本面良好' if dr['score'] >= 4 else '基本面一般' if dr['score'] >= 3 else '基本面存疑'} |
| 评分 | {dr['score']}/5 | {'优秀' if dr['score'] >= 4 else '良好' if dr['score'] >= 3 else '需谨慎'} |
| 建议 | {dr['recommendation']} | - |

"""
        
        # 全局观点
        md += """---

## 📌 全局观点

"""
        
        overall = report.get('overall', {})
        score = overall.get('score', 0)
        recommendation = overall.get('recommendation', '')
        
        # 综合评价
        if score >= 70:
            overall_view = "基本面优秀，技术面支持，适合投资"
        elif score >= 50:
            overall_view = "基本面尚可，需关注风险，谨慎投资"
        else:
            overall_view = "基本面较弱，风险较大，建议观望"
        
        md += f"""**综合评价**: {overall_view}

**评分**: {score}/100

"""
        
        # 不同投资者建议
        md += """---

## 💡 不同周期投资者建议

"""
        
        # 短线建议
        short_advice = self.report_enhancer.get_investment_advice(score, 'short', report['sections'])
        md += f"""### 短线投资者 (日内/隔夜)

**建议**: {short_advice['advice']}\n
**理由**: {short_advice['reason']}\n
**操作**: {short_advice['action']}\n
"""
        
        # 波段建议
        medium_advice = self.report_enhancer.get_investment_advice(score, 'medium', report['sections'])
        md += f"""### 波段投资者 (数天-数周)

**建议**: {medium_advice['advice']}\n
**理由**: {medium_advice['reason']}\n
**操作**: {medium_advice['action']}\n
"""
        
        # 长线建议
        long_advice = self.report_enhancer.get_investment_advice(score, 'long', report['sections'])
        md += f"""### 长线投资者 (数月-数年)

**建议**: {long_advice['advice']}\n
**理由**: {long_advice['reason']}\n
**操作**: {long_advice['action']}\n
"""
        
        md += """---

## ⚠️ 风险提示

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

*报告由 Neo9527 Finance Agent v6.0 生成*
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
