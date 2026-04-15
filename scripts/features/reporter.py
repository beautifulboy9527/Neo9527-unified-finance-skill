#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报生成模块 - 饕餮整合自 alphaear-reporter
专业研报规划、撰写、编辑、图表配置
"""

import sys
import os
import json
from datetime import datetime
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


class ReportGenerator:
    """
    研报生成器 - 饕餮整合自 alphaear-reporter
    
    能力:
    - 研报结构规划
    - 分段撰写
    - 编辑润色
    - 图表配置生成
    """
    
    def __init__(self):
        self.reports_dir = OUTPUT_DIR / 'reports'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def plan_report(
        self,
        topic: str,
        signals: List[Dict] = None
    ) -> Dict:
        """
        规划研报结构
        
        Args:
            topic: 研报主题
            signals: 输入信号列表
            
        Returns:
            研报规划
        """
        result = {
            'topic': topic,
            'structure': {},
            'signals': signals or [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 生成标准研报结构
            result['structure'] = {
                'title': f'{topic} 分析报告',
                'sections': [
                    {
                        'name': '摘要',
                        'content': '核心观点和关键发现',
                        'order': 1
                    },
                    {
                        'name': '背景分析',
                        'content': '市场环境和行业背景',
                        'order': 2
                    },
                    {
                        'name': '核心分析',
                        'content': '主要分析内容和数据支撑',
                        'order': 3
                    },
                    {
                        'name': '风险提示',
                        'content': '潜在风险和不确定性',
                        'order': 4
                    },
                    {
                        'name': '结论与建议',
                        'content': '总结和投资建议',
                        'order': 5
                    }
                ]
            }
            
            # 如果有信号，进行聚类
            if signals:
                result['signal_clusters'] = self._cluster_signals(signals)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _cluster_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        聚类信号
        
        Args:
            signals: 信号列表
            
        Returns:
            聚类结果
        """
        clusters = []
        
        # 简单分类
        positive = [s for s in signals if s.get('sentiment') == 'positive']
        negative = [s for s in signals if s.get('sentiment') == 'negative']
        neutral = [s for s in signals if s.get('sentiment') == 'neutral']
        
        if positive:
            clusters.append({
                'type': 'positive',
                'count': len(positive),
                'signals': positive[:5]
            })
        
        if negative:
            clusters.append({
                'type': 'negative',
                'count': len(negative),
                'signals': negative[:5]
            })
        
        if neutral:
            clusters.append({
                'type': 'neutral',
                'count': len(neutral),
                'signals': neutral[:5]
            })
        
        return clusters
    
    def write_section(
        self,
        section_name: str,
        data: Dict,
        style: str = 'professional'
    ) -> Dict:
        """
        撰写报告段落
        
        Args:
            section_name: 段落名称
            data: 数据内容
            style: 写作风格
            
        Returns:
            段落内容
        """
        result = {
            'section': section_name,
            'content': '',
            'charts': [],
            'style': style,
            'error': None
        }
        
        try:
            # 根据段落类型生成内容
            if section_name == '摘要':
                result['content'] = self._write_summary(data)
            elif section_name == '背景分析':
                result['content'] = self._write_background(data)
            elif section_name == '核心分析':
                result['content'] = self._write_analysis(data)
            elif section_name == '风险提示':
                result['content'] = self._write_risks(data)
            elif section_name == '结论与建议':
                result['content'] = self._write_conclusion(data)
            else:
                result['content'] = self._write_generic(section_name, data)
            
            # 生成图表配置
            if data.get('generate_chart'):
                result['charts'] = self._generate_chart_config(data)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _write_summary(self, data: Dict) -> str:
        """撰写摘要"""
        lines = []
        lines.append(f"## 摘要\n")
        
        if data.get('title'):
            lines.append(f"**主题**: {data['title']}\n")
        
        if data.get('key_findings'):
            lines.append("**关键发现**:")
            for finding in data['key_findings'][:5]:
                lines.append(f"- {finding}")
        
        if data.get('recommendation'):
            lines.append(f"\n**核心建议**: {data['recommendation']}")
        
        return '\n'.join(lines)
    
    def _write_background(self, data: Dict) -> str:
        """撰写背景"""
        lines = []
        lines.append(f"## 背景分析\n")
        
        if data.get('market_context'):
            lines.append(f"**市场环境**: {data['market_context']}\n")
        
        if data.get('industry_trend'):
            lines.append(f"**行业趋势**: {data['industry_trend']}\n")
        
        if data.get('macro_factors'):
            lines.append("**宏观因素**:")
            for factor in data['macro_factors']:
                lines.append(f"- {factor}")
        
        return '\n'.join(lines)
    
    def _write_analysis(self, data: Dict) -> str:
        """撰写核心分析"""
        lines = []
        lines.append(f"## 核心分析\n")
        
        if data.get('financial_metrics'):
            lines.append("**财务指标**:")
            for metric, value in data['financial_metrics'].items():
                lines.append(f"- {metric}: {value}")
            lines.append("")
        
        if data.get('technical_signals'):
            lines.append("**技术信号**:")
            for signal in data['technical_signals']:
                lines.append(f"- {signal}")
            lines.append("")
        
        if data.get('sentiment_analysis'):
            lines.append(f"**市场情绪**: {data['sentiment_analysis']}\n")
        
        return '\n'.join(lines)
    
    def _write_risks(self, data: Dict) -> str:
        """撰写风险提示"""
        lines = []
        lines.append(f"## 风险提示\n")
        
        if data.get('risks'):
            for risk in data['risks']:
                lines.append(f"- ⚠️ {risk}")
        else:
            lines.append("- ⚠️ 市场波动风险")
            lines.append("- ⚠️ 政策变动风险")
            lines.append("- ⚠️ 流动性风险")
        
        lines.append("\n**免责声明**: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
        
        return '\n'.join(lines)
    
    def _write_conclusion(self, data: Dict) -> str:
        """撰写结论"""
        lines = []
        lines.append(f"## 结论与建议\n")
        
        if data.get('conclusion'):
            lines.append(f"**总结**: {data['conclusion']}\n")
        
        if data.get('rating'):
            lines.append(f"**评级**: {data['rating']}\n")
        
        if data.get('action'):
            lines.append(f"**建议操作**: {data['action']}\n")
        
        if data.get('price_target'):
            lines.append(f"**目标价位**: {data['price_target']}\n")
        
        return '\n'.join(lines)
    
    def _write_generic(self, section_name: str, data: Dict) -> str:
        """撰写通用段落"""
        lines = []
        lines.append(f"## {section_name}\n")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key not in ['generate_chart']:
                    lines.append(f"**{key}**: {value}")
        
        return '\n'.join(lines)
    
    def _generate_chart_config(self, data: Dict) -> List[Dict]:
        """生成图表配置"""
        charts = []
        
        # K线图
        if data.get('symbol'):
            charts.append({
                'type': 'candlestick',
                'symbol': data['symbol'],
                'title': f"{data.get('symbol')} K线图"
            })
        
        # 技术指标图
        if data.get('indicators'):
            charts.append({
                'type': 'technical',
                'indicators': data['indicators'],
                'title': '技术指标'
            })
        
        return charts
    
    def generate_full_report(
        self,
        topic: str,
        data: Dict
    ) -> Dict:
        """
        生成完整研报
        
        Args:
            topic: 主题
            data: 数据
            
        Returns:
            完整研报
        """
        result = {
            'topic': topic,
            'sections': {},
            'full_content': '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 规划结构
            plan = self.plan_report(topic, data.get('signals'))
            
            # 撰写各段落
            full_content = []
            full_content.append(f"# {topic} 分析报告\n")
            full_content.append(f"生成时间: {result['created_at']}\n")
            full_content.append("---\n")
            
            for section in plan['structure']['sections']:
                section_result = self.write_section(
                    section['name'],
                    data.get(section['name'].lower().replace(' ', '_'), data)
                )
                
                result['sections'][section['name']] = section_result
                full_content.append(section_result['content'])
                full_content.append("\n")
            
            result['full_content'] = '\n'.join(full_content)
            
            # 保存报告
            report_file = self.reports_dir / f"{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(result['full_content'])
            
            result['saved_to'] = str(report_file)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def plan_report(topic: str, signals: List[Dict] = None) -> Dict:
    """规划研报"""
    generator = ReportGenerator()
    return generator.plan_report(topic, signals)


def write_section(section_name: str, data: Dict) -> Dict:
    """撰写段落"""
    generator = ReportGenerator()
    return generator.write_section(section_name, data)


def generate_full_report(topic: str, data: Dict) -> Dict:
    """生成完整研报"""
    generator = ReportGenerator()
    return generator.generate_full_report(topic, data)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='研报生成 - 饕餮整合自 alphaear-reporter')
    parser.add_argument('topic', help='研报主题')
    parser.add_argument('--symbol', help='股票代码')
    parser.add_argument('--data', help='JSON 数据文件')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    
    # 简单数据
    data = {
        'title': args.topic,
        'symbol': args.symbol
    }
    
    result = generator.generate_full_report(args.topic, data)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
