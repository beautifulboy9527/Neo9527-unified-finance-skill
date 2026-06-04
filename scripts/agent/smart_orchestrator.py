#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 智能调度器
基于用户意图自动选择和执行 Skills
"""

import sys
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class IntentAnalyzer:
    """
    意图分析器
    
    分析用户输入，识别意图和参数
    """
    
    # 意图模式库
    INTENT_PATTERNS = {
        'stock_analysis': {
            'patterns': [
                r'分析\s*(\d{6})',
                r'(\d{6})\s*分析',
                r'查看\s*(\d{6})',
                r'(\d{6})\s*怎么样',
                r'分析\s*([A-Z]+)',
            ],
            'skills': ['investment_framework', 'plugin_system'],
            'params': {'period': 'medium'}
        },
        'signal_backtest': {
            'patterns': [
                r'回测\s*(\d{6})',
                r'验证.*信号',
                r'(\d{6})\s*信号',
            ],
            'skills': ['backtest_engine'],
            'params': {}
        },
        'portfolio_optimize': {
            'patterns': [
                r'优化.*组合',
                r'组合.*优化',
                r'构建.*组合',
                r'(\d{6}).*组合',
            ],
            'skills': ['portfolio_manager'],
            'params': {}
        },
        'generate_report': {
            'patterns': [
                r'生成.*报告',
                r'报告.*(\d{6})',
                r'导出.*报告',
                r'(\d{6})\s*报告',
            ],
            'skills': ['report_generator'],
            'params': {'format': 'html'}
        },
        'fundamental_analysis': {
            'patterns': [
                r'基本面.*分析',
                r'财务.*分析',
                r'(\d{6})\s*基本面',
            ],
            'skills': ['finance_toolkit'],
            'params': {}
        }
    }
    
    def analyze(self, query: str) -> Dict:
        """
        分析用户意图
        
        Args:
            query: 用户输入
            
        Returns:
            意图分析结果
        """
        result = {
            'query': query,
            'intent': None,
            'symbols': [],
            'skills': [],
            'params': {},
            'confidence': 0
        }
        
        # 提取股票代码
        symbols = self._extract_symbols(query)
        result['symbols'] = symbols
        
        # 匹配意图
        best_match = None
        best_confidence = 0
        
        for intent_name, intent_data in self.INTENT_PATTERNS.items():
            for pattern in intent_data['patterns']:
                if re.search(pattern, query, re.IGNORECASE):
                    confidence = 0.8 if symbols else 0.6
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent_name
                        result['skills'] = intent_data['skills']
                        result['params'] = intent_data['params'].copy()
        
        if best_match:
            result['intent'] = best_match
            result['confidence'] = best_confidence
        
        return result
    
    def _extract_symbols(self, query: str) -> List[str]:
        """提取股票代码"""
        symbols = []
        
        # A股代码 (6位数字)
        cn_pattern = r'\b(\d{6})\b'
        cn_matches = re.findall(cn_pattern, query)
        symbols.extend(cn_matches)
        
        # 美股代码 (大写字母)
        us_pattern = r'\b([A-Z]{1,5})\b'
        us_matches = re.findall(us_pattern, query)
        symbols.extend(us_matches)
        
        return list(set(symbols))  # 去重


class SkillOrchestrator:
    """
    Skill 编排器
    
    根据意图自动选择和执行 Skills
    """
    
    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.skill_costs = {
            'investment_framework': {'time': 5, 'api_calls': 3},
            'plugin_system': {'time': 10, 'api_calls': 5},
            'backtest_engine': {'time': 30, 'api_calls': 10},
            'portfolio_manager': {'time': 15, 'api_calls': 8},
            'report_generator': {'time': 20, 'api_calls': 12},
            'finance_toolkit': {'time': 8, 'api_calls': 5}
        }
    
    def process_query(self, query: str) -> Dict:
        """
        处理用户查询
        
        Args:
            query: 用户输入
            
        Returns:
            处理结果
        """
        # 1. 分析意图
        intent_result = self.intent_analyzer.analyze(query)
        
        if not intent_result['intent']:
            return {
                'error': '无法识别意图',
                'suggestion': '尝试: "分析 002241" 或 "生成报告 600519"'
            }
        
        # 2. 估算成本
        cost_estimate = self._estimate_cost(intent_result['skills'])
        
        # 3. 执行 Skills
        execution_result = self._execute_skills(intent_result)
        
        return {
            'query': query,
            'intent': intent_result['intent'],
            'symbols': intent_result['symbols'],
            'skills_used': intent_result['skills'],
            'cost_estimate': cost_estimate,
            'result': execution_result,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _estimate_cost(self, skills: List[str]) -> Dict:
        """估算执行成本"""
        total_time = 0
        total_api_calls = 0
        
        for skill in skills:
            if skill in self.skill_costs:
                total_time += self.skill_costs[skill]['time']
                total_api_calls += self.skill_costs[skill]['api_calls']
        
        return {
            'estimated_time_seconds': total_time,
            'estimated_api_calls': total_api_calls,
            'cost_level': 'low' if total_time < 15 else 'medium' if total_time < 30 else 'high'
        }
    
    def _execute_skills(self, intent_result: Dict) -> Dict:
        """执行 Skills"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        result = {}
        symbols = intent_result['symbols']
        
        if not symbols:
            return {'error': '未识别到股票代码'}
        
        symbol = symbols[0]  # 取第一个
        intent = intent_result['intent']
        params = intent_result['params']
        
        try:
            if intent == 'stock_analysis':
                from features.investment_framework import analyze_investment
                result = analyze_investment(symbol, params.get('period', 'medium'))
            
            elif intent == 'signal_backtest':
                from features.backtest_engine import validate_signal_performance, sma_cross_signal
                result = validate_signal_performance(symbol, sma_cross_signal, "SMA交叉")
            
            elif intent == 'portfolio_optimize':
                from features.portfolio_manager import analyze_portfolio
                result = analyze_portfolio(symbols)
            
            elif intent == 'generate_report':
                from features.report_generator import generate_report
                report_path = generate_report(symbol, params.get('period', 'medium'), params.get('format', 'html'))
                result = {'report_path': report_path}
            
            elif intent == 'fundamental_analysis':
                from features.finance_toolkit import analyze_fundamentals_deep
                result = analyze_fundamentals_deep(symbol)
            
            else:
                result = {'error': f'未知意图: {intent}'}
        
        except Exception as e:
            result = {'error': str(e)}
        
        return result


# ============================================
# 便捷函数
# ============================================

def process_query(query: str) -> Dict:
    """
    处理用户查询
    
    Args:
        query: 用户输入
        
    Returns:
        处理结果
    """
    orchestrator = SkillOrchestrator()
    return orchestrator.process_query(query)


if __name__ == '__main__':
    # 测试
    queries = [
        "分析 002241",
        "回测 002241 的信号",
        "优化组合",
        "生成报告 600519",
        "分析 AAPL 的基本面"
    ]
    
    print("=" * 60)
    print("Agent 智能调度测试")
    print("=" * 60)
    
    for query in queries:
        print(f"\n查询: {query}")
        print("-" * 60)
        
        result = process_query(query)
        
        if 'error' in result:
            print(f"❌ 错误: {result['error']}")
            if 'suggestion' in result:
                print(f"💡 建议: {result['suggestion']}")
        else:
            print(f"意图: {result['intent']}")
            print(f"股票: {result['symbols']}")
            print(f"Skills: {result['skills_used']}")
            print(f"预估时间: {result['cost_estimate']['estimated_time_seconds']}秒")
            print(f"API调用: {result['cost_estimate']['estimated_api_calls']}次")
            print(f"成本级别: {result['cost_estimate']['cost_level']}")
