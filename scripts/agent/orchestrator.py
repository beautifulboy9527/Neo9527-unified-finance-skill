#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资 Agent 协调器
统一入口，路由到不同的子 Agent
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


class InvestmentAgent:
    """
    投资 Agent 协调器
    
    能力:
    - 意图理解与路由
    - 多 Agent 协调
    - 工具调度
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
        self.logs_dir = OUTPUT_DIR / 'logs' / 'agent'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.tools = self._load_tools()
    
    def _load_tools(self) -> Dict:
        """加载工具函数"""
        tools = {}
        
        try:
            # 行情工具
            from core.quote import get_quote
            tools['get_quote'] = get_quote
            
            # 分析工具
            from core.technical import analyze_technical
            tools['analyze_technical'] = analyze_technical
            
            from features.sentiment_enhanced import analyze_sentiment
            tools['analyze_sentiment'] = analyze_sentiment
            
            from features.liquidity import analyze_liquidity
            tools['analyze_liquidity'] = analyze_liquidity
            
            from features.valuation import get_valuation_summary
            tools['get_valuation_summary'] = get_valuation_summary
            
            from features.earnings import get_beat_miss_history
            tools['get_beat_miss_history'] = get_beat_miss_history
            
            from features.correlation import analyze_pair_correlation
            tools['analyze_pair_correlation'] = analyze_pair_correlation
            
            from features.options import calculate_all_greeks
            tools['calculate_all_greeks'] = calculate_all_greeks
            
            # 新增市场
            from features.crypto import get_crypto_quote
            tools['get_crypto_quote'] = get_crypto_quote
            
            from features.metals import get_metal_price, get_gold_silver_ratio
            tools['get_metal_price'] = get_metal_price
            tools['get_gold_silver_ratio'] = get_gold_silver_ratio
            
            # 信息工具
            from features.news import get_finance_brief
            tools['get_finance_brief'] = get_finance_brief
            
            from features.signal_tracker import scan_hot_stocks
            tools['scan_hot_stocks'] = scan_hot_stocks
            
            from features.reporter import generate_full_report
            tools['generate_full_report'] = generate_full_report
            
        except ImportError as e:
            print(f"Warning: Some tools not loaded: {e}")
        
        return tools
    
    def route(self, query: str) -> str:
        """
        路由用户问题到对应的 Agent
        
        Args:
            query: 用户问题
            
        Returns:
            Agent 类型
        """
        query_lower = query.lower()
        
        # 计算每个 Agent 的关键词匹配得分
        scores = {}
        for agent_type, keywords in self.ROUTING_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[agent_type] = score
        
        # 选择得分最高的 Agent
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        # 默认返回 research
        return 'research'
    
    def process(self, query: str) -> Dict:
        """
        处理用户问题
        
        Args:
            query: 用户问题
            
        Returns:
            处理结果
        """
        result = {
            'query': query,
            'agent_type': None,
            'response': None,
            'tools_used': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'disclaimer': self._get_disclaimer()
        }
        
        try:
            # 1. 路由
            agent_type = self.route(query)
            result['agent_type'] = agent_type
            result['agent_name'] = self.AGENT_TYPES.get(agent_type, agent_type)
            
            # 2. 执行对应 Agent
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
        
        # 3. 记录日志
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
        
        # 提取股票代码
        symbol = self._extract_symbol(query)
        
        if symbol:
            # 执行分析链
            tools_used = []
            
            # 1. 行情
            if 'get_quote' in self.tools:
                quote = self.tools['get_quote'](symbol)
                response['data']['quote'] = quote
                tools_used.append('get_quote')
            
            # 2. 技术分析
            if 'analyze_technical' in self.tools:
                tech = self.tools['analyze_technical'](symbol)
                response['data']['technical'] = tech
                tools_used.append('analyze_technical')
            
            # 3. 估值
            if 'get_valuation_summary' in self.tools:
                val = self.tools['get_valuation_summary'](symbol)
                response['data']['valuation'] = val
                tools_used.append('get_valuation_summary')
            
            # 4. 情绪
            if 'analyze_sentiment' in self.tools:
                sent = self.tools['analyze_sentiment'](symbol)
                response['data']['sentiment'] = sent
                tools_used.append('analyze_sentiment')
            
            response['tools_used'] = tools_used
            
            # 生成摘要
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
            # 获取行情和技术分析
            if 'get_quote' in self.tools:
                quote = self.tools['get_quote'](symbol)
                response['quote'] = quote
                response['tools_used'].append('get_quote')
            
            if 'analyze_technical' in self.tools:
                tech = self.tools['analyze_technical'](symbol)
                response['technical'] = tech
                response['tools_used'].append('analyze_technical')
            
            # 生成信号 (简化版)
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
            # 流动性分析
            if 'analyze_liquidity' in self.tools:
                liq = self.tools['analyze_liquidity'](symbol)
                response['liquidity'] = liq
                response['tools_used'].append('analyze_liquidity')
            
            # 风险评估
            response['risk_assessment'] = {
                'symbol': symbol,
                'liquidity_risk': 'low' if response.get('liquidity', {}).get('grade') in ['High', 'Very High'] else 'medium',
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
        
        # 检测查询类型
        if any(kw in query for kw in ['热门', 'trending', 'hot']):
            if 'scan_hot_stocks' in self.tools:
                response['data']['hot_stocks'] = self.tools['scan_hot_stocks']()
                response['tools_used'].append('scan_hot_stocks')
        
        elif any(kw in query for kw in ['新闻', 'news', '快讯']):
            if 'get_finance_brief' in self.tools:
                response['data']['news'] = self.tools['get_finance_brief']()
                response['tools_used'].append('get_finance_brief')
        
        elif any(kw in query for kw in ['黄金', 'gold', 'xau', '贵金属']):
            if 'get_metal_price' in self.tools:
                response['data']['metals'] = self.tools['get_metal_price']('XAU')
                response['tools_used'].append('get_metal_price')
        
        elif any(kw in query for kw in ['金银比', 'ratio']):
            if 'get_gold_silver_ratio' in self.tools:
                response['data']['ratio'] = self.tools['get_gold_silver_ratio']()
                response['tools_used'].append('get_gold_silver_ratio')
        
        else:
            # 提取股票代码
            symbol = self._extract_symbol(query)
            if symbol and 'get_quote' in self.tools:
                response['data']['quote'] = self.tools['get_quote'](symbol)
                response['tools_used'].append('get_quote')
            
            # 加密货币
            crypto = self._extract_crypto(query)
            if crypto and 'get_crypto_quote' in self.tools:
                response['data']['crypto'] = self.tools['get_crypto_quote'](crypto)
                response['tools_used'].append('get_crypto_quote')
        
        return response
    
    def _execute_portfolio_agent(self, query: str) -> Dict:
        """执行组合 Agent"""
        response = {
            'agent': 'portfolio',
            'tools_used': [],
            'message': '组合管理功能开发中...'
        }
        return response
    
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
    
    def _extract_crypto(self, query: str) -> Optional[str]:
        """提取加密货币代码"""
        import re
        
        # 常见加密货币
        cryptos = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE']
        
        for crypto in cryptos:
            if crypto in query.upper():
                return f"{crypto}/USDT"
        
        return None
    
    def _generate_summary(self, data: Dict, symbol: str) -> str:
        """生成分析摘要"""
        summary_parts = [f"## {symbol} 分析摘要\n"]
        
        # 行情
        if 'quote' in data:
            quote = data['quote']
            if quote.get('price'):
                summary_parts.append(f"**价格**: {quote['price']}")
                if quote.get('change_pct'):
                    summary_parts.append(f" ({quote['change_pct']:+.2f}%)")
        
        # 技术
        if 'technical' in data:
            tech = data['technical']
            basic = tech.get('basic_indicators', {})
            if basic.get('trend'):
                summary_parts.append(f"\n**趋势**: {basic['trend']}")
        
        # 估值
        if 'valuation' in data:
            val = data['valuation']
            if val.get('overall_assessment'):
                summary_parts.append(f"\n**估值**: {val['overall_assessment']}")
        
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
