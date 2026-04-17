#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 报告生成器
整合多个分析模块，生成综合投资报告
"""

import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加路径
SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILLS_DIR)


class AgentReportGenerator:
    """AI Agent 报告生成器"""
    
    def __init__(self):
        self.name = "AgentReportGenerator"
        self.version = "1.0.0"
    
    def generate_comprehensive_report(
        self,
        symbol: str,
        market: str = 'auto',
        style: str = 'value'
    ) -> Dict:
        """
        生成综合投资报告
        
        Args:
            symbol: 股票代码
            market: 市场类型 (auto/us/cn)
            style: 投资风格 (value/growth/turnaround)
            
        Returns:
            综合报告
        """
        print(f"\n{'='*60}")
        print(f" {symbol} 综合投资报告")
        print(f"{'='*60}")
        
        report = {
            'success': True,
            'symbol': symbol,
            'market': market,
            'style': style,
            'timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # 1. 快速分析
        print("\n【1】快速分析...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "analyzer",
                os.path.join(SKILLS_DIR, 'stock-skill', 'analyzer.py')
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            quick_result = module.analyze_stock(symbol)
            if quick_result['success']:
                report['sections']['quick_analysis'] = {
                    'score': quick_result['score'],
                    'trend': quick_result['data'].get('technical', {}).get('trend'),
                    'signals': len(quick_result['signals']),
                    'summary': quick_result['summary']
                }
                print(f"   评分: {quick_result['score']}/100")
            else:
                print(f"   失败: {quick_result.get('error')}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 2. 财务异常检测
        print("\n【2】财务异常检测...")
        try:
            spec = importlib.util.spec_from_file_location(
                "financial_check",
                os.path.join(SKILLS_DIR, 'stock-skill', 'financial_check.py')
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            check_result = module.check_financial_anomaly(symbol)
            if check_result['success']:
                report['sections']['financial_check'] = {
                    'risk_level': check_result['risk_level'],
                    'risk_description': check_result['risk_description'],
                    'anomaly_count': check_result['anomaly_count']
                }
                print(f"   风险等级: {check_result['risk_description']}")
            else:
                print(f"   失败: {check_result.get('error')}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 3. 估值计算
        print("\n【3】估值计算...")
        try:
            spec = importlib.util.spec_from_file_location(
                "valuation",
                os.path.join(SKILLS_DIR, 'stock-skill', 'valuation.py')
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            value_result = module.calculate_valuation(symbol)
            if value_result['success']:
                report['sections']['valuation'] = {
                    'current_price': value_result['current_price'],
                    'fair_value': value_result['fair_value'],
                    'safe_price': value_result['safe_price'],
                    'margin_of_safety': value_result['margin_of_safety']
                }
                print(f"   公允价值: ${value_result['fair_value']:.2f}")
            else:
                print(f"   失败: {value_result.get('error')}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 4. 深度研报
        print("\n【4】深度研报...")
        try:
            spec = importlib.util.spec_from_file_location(
                "deep_analyzer",
                os.path.join(SKILLS_DIR, 'stock-skill', 'deep-research', 'analyzer.py')
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取投资风格
            style_enum = getattr(module.InvestmentStyle, style.upper(), module.InvestmentStyle.VALUE)
            
            deep_result = module.StockAnalyzer(style=style_enum).analyze(symbol, depth='quick')
            if deep_result:
                report['sections']['deep_research'] = {
                    'rating': deep_result['rating']['rating'],
                    'score': deep_result['rating']['score'],
                    'recommendation': deep_result['rating']['recommendation']
                }
                print(f"   评级: {deep_result['rating']['rating']}")
            else:
                print(f"   失败: 无结果")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 5. 生成综合评分
        print("\n【5】综合评分...")
        report['overall'] = self._calculate_overall_score(report['sections'])
        print(f"   综合评分: {report['overall']['score']}/100")
        print(f"   建议: {report['overall']['recommendation']}")
        
        return report
    
    def _calculate_overall_score(self, sections: Dict) -> Dict:
        """计算综合评分"""
        score = 0
        count = 0
        
        # 快速分析权重 40%
        if 'quick_analysis' in sections:
            score += sections['quick_analysis']['score'] * 0.4
            count += 1
        
        # 财务异常权重 30% (反转评分)
        if 'financial_check' in sections:
            risk_score = 100 - (sections['financial_check']['risk_level'] * 20)
            score += risk_score * 0.3
            count += 1
        
        # 估值权重 30%
        if 'valuation' in sections:
            val = sections['valuation']
            if val['current_price'] < val['fair_value']:
                val_score = min(100, (val['fair_value'] / val['current_price'] - 1) * 100 + 50)
            else:
                val_score = max(0, 50 - (val['current_price'] / val['fair_value'] - 1) * 50)
            score += val_score * 0.3
            count += 1
        
        score = min(100, max(0, score))
        
        # 生成建议
        if score >= 80:
            recommendation = "强烈买入"
        elif score >= 60:
            recommendation = "买入"
        elif score >= 40:
            recommendation = "持有"
        elif score >= 20:
            recommendation = "卖出"
        else:
            recommendation = "强烈卖出"
        
        return {
            'score': round(score, 1),
            'recommendation': recommendation
        }
    
    def generate_markdown_report(self, report: Dict) -> str:
        """生成 Markdown 格式报告"""
        md = f"""# {report['symbol']} 综合投资报告

**生成时间**: {report['timestamp']}  
**投资风格**: {report['style']}  
**市场**: {report['market']}

---

## 综合评分

| 评分 | 建议 |
|------|------|
| **{report['overall']['score']}/100** | {report['overall']['recommendation']} |

---

## 分析详情

"""
        
        # 快速分析
        if 'quick_analysis' in report['sections']:
            qa = report['sections']['quick_analysis']
            md += f"""### 1. 快速分析

- **评分**: {qa['score']}/100
- **趋势**: {qa.get('trend', 'N/A')}
- **信号数**: {qa['signals']}
- **摘要**: {qa['summary']}

"""
        
        # 财务异常
        if 'financial_check' in report['sections']:
            fc = report['sections']['financial_check']
            md += f"""### 2. 财务异常检测

- **风险等级**: {fc['risk_description']}
- **异常数量**: {fc['anomaly_count']}

"""
        
        # 估值
        if 'valuation' in report['sections']:
            val = report['sections']['valuation']
            md += f"""### 3. 估值分析

| 指标 | 值 |
|------|------|
| 当前价格 | ${val['current_price']:.2f} |
| 公允价值 | ${val['fair_value']:.2f} |
| 安全价格 | ${val['safe_price']:.2f} |
| 安全边际 | {val['margin_of_safety']*100:.0f}% |

"""
        
        # 深度研报
        if 'deep_research' in report['sections']:
            dr = report['sections']['deep_research']
            md += f"""### 4. 深度研报

- **评级**: {dr['rating']}
- **评分**: {dr['score']}/5
- **建议**: {dr['recommendation']}

"""
        
        md += """---

*报告由 Neo9527 Finance Agent 生成*
"""
        
        return md


# 快速使用函数
def generate_agent_report(symbol: str, style: str = 'value') -> Dict:
    """生成 Agent 报告"""
    generator = AgentReportGenerator()
    return generator.generate_comprehensive_report(symbol, style=style)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("Agent 报告生成器测试")
    print("=" * 60)
    
    generator = AgentReportGenerator()
    report = generator.generate_comprehensive_report('AAPL', style='value')
    
    if report['success']:
        print(f"\n{'='*60}")
        print(f" 综合报告生成完成")
        print(f"{'='*60}")
        
        # 生成 Markdown
        md = generator.generate_markdown_report(report)
        
        # 保存
        output_file = r'D:\OpenClaw\outputs\reports\agent_report_AAPL.md'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"\n✅ 报告已保存: {output_file}")
    else:
        print(f"\n❌ 报告生成失败")
