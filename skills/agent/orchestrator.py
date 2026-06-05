#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资 Agent 协调器 v2.0 (P6: data_layer integration)

重构说明:
- 移除已删除的 core/ 和 features/ 依赖
- 使用统一数据层 (data_layer) 获取行情/财务数据
- 使用 CLI 模块执行分析命令
- 保留路由逻辑和 Agent 类型定义
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

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILLS_DIR)

# 统一数据层
try:
    from skills.shared.data_layer import get_data_layer, QuoteData, KlineData
    DATALAYER_AVAILABLE = True
except ImportError:
    try:
        # Fallback: 直接导入
        sys.path.insert(0, os.path.join(SKILLS_DIR, 'skills', 'shared'))
        from data_layer import get_data_layer, QuoteData, KlineData
        DATALAYER_AVAILABLE = True
    except ImportError:
        DATALAYER_AVAILABLE = False

# 分析器
try:
    from skills.stock_skill.analyzer import StockAnalysisSkill
    ANALYZER_AVAILABLE = True
except ImportError:
    try:
        sys.path.insert(0, os.path.join(SKILLS_DIR, 'skills', 'stock-skill'))
        from analyzer import StockAnalysisSkill
        ANALYZER_AVAILABLE = True
    except ImportError:
        ANALYZER_AVAILABLE = False


class InvestmentAgent:
    """
    投资 Agent 协调器 v2.0

    能力:
    - 意图理解与路由
    - 统一数据层查询 (data_layer)
    - 股票分析 (analyzer)
    - 风险检查
    - 日志记录
    """

    # Agent 类型
    AGENT_TYPES = {
        'research': '投研分析',
        'trading': '交易信号',
        'risk': '风险评估',
        'data': '数据查询',
        'portfolio': '组合管理'
    }

    # 关键词路由
    ROUTING_KEYWORDS = {
        'research': [
            '分析', '研究', '报告', '基本面', '财务',
            '估值', '投研', '深度', '解读'
        ],
        'trading': [
            '交易', '信号', '买入', '卖出', '策略',
            '回测', '止损', '止盈', '仓位'
        ],
        'risk': [
            '风险', '评估', '流动性', '波动', 'VaR',
            '敞口', '暴露', '安全'
        ],
        'data': [
            '查询', '价格', '行情', '新闻', '热门',
            '最新', '实时', '历史'
        ],
        'portfolio': [
            '组合', '持仓', '配置', '资产', '优化',
            '分散', '对冲'
        ]
    }

    def __init__(self):
        self.output_dir = Path(SKILLS_DIR) / 'outputs'
        self.logs_dir = self.output_dir / 'logs' / 'agent'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._dl = None
        self._analyzer = None

    def _get_dl(self):
        """获取统一数据层实例"""
        if self._dl is None and DATALAYER_AVAILABLE:
            try:
                self._dl = get_data_layer()
            except Exception:
                pass
        return self._dl

    def _get_analyzer(self):
        """获取分析器实例"""
        if self._analyzer is None and ANALYZER_AVAILABLE:
            try:
                self._analyzer = StockAnalysisSkill()
            except Exception:
                pass
        return self._analyzer

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """获取实时行情 (通过 data_layer)"""
        dl = self._get_dl()
        if dl:
            try:
                quote = dl.get_quote(symbol)
                if quote and quote.has_real_data:
                    return quote.to_dict()
            except Exception:
                pass
        return None

    def analyze(self, symbol: str) -> Optional[Dict]:
        """执行股票分析 (通过 analyzer)"""
        analyzer = self._get_analyzer()
        if analyzer:
            try:
                return analyzer.analyze(symbol)
            except Exception:
                pass
        return None

    def route(self, query: str) -> str:
        """路由用户问题到对应的 Agent"""
        query_lower = query.lower()

        scores = {}
        for agent_type, keywords in self.ROUTING_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[agent_type] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return 'research'

    def process(self, query: str) -> Dict:
        """处理用户问题"""
        result = {
            'query': query,
            'agent_type': None,
            'response': None,
            'tools_used': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'disclaimer': self._get_disclaimer()
        }

        try:
            agent_type = self.route(query)
            result['agent_type'] = agent_type
            result['agent_name'] = self.AGENT_TYPES.get(agent_type, agent_type)

            if agent_type == 'research':
                response = self._execute_research_agent(query)
            elif agent_type == 'trading':
                response = self._execute_trading_agent(query)
            elif agent_type == 'risk':
                response = self._execute_risk_agent(query)
            elif agent_type == 'data':
                response = self._execute_data_agent(query)
            elif agent_type == 'portfolio':
                response = self._execute_portfolio_agent(query)
            else:
                response = self._execute_research_agent(query)

            result['response'] = response
            result['tools_used'] = response.get('tools_used', [])

        except Exception as e:
            result['error'] = str(e)

        self._log(result)
        return result

    def _execute_research_agent(self, query: str) -> Dict:
        """执行投研 Agent"""
        response = {
            'agent': 'research',
            'tools_used': [],
            'data': {},
            'summary': None
        }

        symbol = self._extract_symbol(query)

        if symbol:
            # 1. 行情 (data_layer)
            quote = self.get_quote(symbol)
            if quote:
                response['data']['quote'] = quote
                response['tools_used'].append('data_layer.quote')

            # 2. 完整分析 (analyzer)
            analysis = self.analyze(symbol)
            if analysis:
                response['data']['analysis'] = analysis
                response['tools_used'].append('analyzer')

            response['summary'] = self._generate_summary(response['data'], symbol)

        return response

    def _execute_trading_agent(self, query: str) -> Dict:
        """执行交易 Agent"""
        response = {
            'agent': 'trading',
            'tools_used': [],
            'signal': None,
            'warning': '⚠️ 仅供参考，不构成投资建议'
        }

        symbol = self._extract_symbol(query)

        if symbol:
            quote = self.get_quote(symbol)
            if quote:
                response['quote'] = quote
                response['tools_used'].append('data_layer.quote')

            analysis = self.analyze(symbol)
            if analysis:
                response['analysis'] = analysis
                response['tools_used'].append('analyzer')

            response['signal'] = {
                'symbol': symbol,
                'action': 'hold',
                'confidence': 0.5,
                'reasoning': '需进一步分析'
            }

        return response

    def _execute_risk_agent(self, query: str) -> Dict:
        """执行风险 Agent"""
        response = {
            'agent': 'risk',
            'tools_used': [],
            'risk_assessment': None
        }

        symbol = self._extract_symbol(query)

        if symbol:
            quote = self.get_quote(symbol)
            if quote:
                response['quote'] = quote
                response['tools_used'].append('data_layer.quote')

            response['risk_assessment'] = {
                'symbol': symbol,
                'liquidity_risk': 'medium',
                'volatility_risk': 'medium',
                'overall_risk': 'medium'
            }

        return response

    def _execute_data_agent(self, query: str) -> Dict:
        """执行数据 Agent"""
        response = {
            'agent': 'data',
            'tools_used': [],
            'data': {}
        }

        symbol = self._extract_symbol(query)
        if symbol:
            quote = self.get_quote(symbol)
            if quote:
                response['data']['quote'] = quote
                response['tools_used'].append('data_layer.quote')

        return response

    def _execute_portfolio_agent(self, query: str) -> Dict:
        """执行组合 Agent"""
        return {
            'agent': 'portfolio',
            'tools_used': [],
            'message': '组合管理功能开发中...'
        }

    def _extract_symbol(self, query: str) -> Optional[str]:
        """提取股票代码"""
        import re

        # 美股代码 (大写字母)
        us_match = re.search(r'\b([A-Z]{1,5})\b', query)
        if us_match:
            return us_match.group(1)

        # A股代码 (6位数字)
        cn_match = re.search(r'\b([036]\d{5})\b', query)
        if cn_match:
            return cn_match.group(1)

        return None

    def _generate_summary(self, data: Dict, symbol: str) -> str:
        """生成分析摘要"""
        summary_parts = [f"## {symbol} 分析摘要\n"]

        if 'quote' in data:
            quote = data['quote']
            price = quote.get('price')
            if price:
                summary_parts.append(f"**价格**: {price}")
                change = quote.get('change_pct')
                if change is not None:
                    summary_parts.append(f" ({change:+.2f}%)")
                summary_parts.append("\n")

        if 'analysis' in data:
            analysis = data['analysis']
            if isinstance(analysis, dict):
                signal = analysis.get('signal', {})
                if signal:
                    summary_parts.append(f"**信号**: {signal.get('action', 'N/A')}\n")

        return ''.join(summary_parts)

    def _get_disclaimer(self) -> str:
        """获取免责声明"""
        return """
⚠️ 免责声明
本分析仅供研究参考，不构成投资建议。
投资有风险，入市需谨慎。
"""

    def _log(self, result: Dict):
        """记录日志"""
        log_file = self.logs_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.jsonl"

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False, default=str) + '\n')
        except Exception:
            pass


def process_query(query: str) -> Dict:
    """处理查询的入口函数"""
    agent = InvestmentAgent()
    return agent.process(query)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='投资 Agent')
    parser.add_argument('query', nargs='+', help='用户问题')

    args = parser.parse_args()

    query = ' '.join(args.query)
    result = process_query(query)

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
