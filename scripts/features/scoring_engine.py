#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分引擎 - 整合三层分析 + 信号评分
生成 0-100 综合评分和操作建议
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 导入其他模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.analysis_framework import AnalysisFramework, analyze_full
from features.entry_signals import analyze_entry_signals
from features.risk_management import analyze_risk


class ScoringEngine:
    """
    综合评分引擎
    
    评分组成:
    - 宏观分析: 20分
    - 行业分析: 20分
    - 技术分析: 60分
    - 信号加成: ±10分
    """
    
    # 评分等级
    SCORE_LEVELS = {
        (80, 100): {
            'rating': 'strong',
            'level': '强势',
            'action': 'buy',
            'suggestion': '可积极参与'
        },
        (65, 79): {
            'rating': 'bullish',
            'level': '偏强',
            'action': 'buy',
            'suggestion': '可适度参与'
        },
        (50, 64): {
            'rating': 'neutral',
            'level': '中性',
            'action': 'hold',
            'suggestion': '观望为主'
        },
        (35, 49): {
            'rating': 'bearish',
            'level': '偏弱',
            'action': 'reduce',
            'suggestion': '谨慎'
        },
        (0, 34): {
            'rating': 'weak',
            'level': '弱势',
            'action': 'avoid',
            'suggestion': '回避'
        }
    }
    
    def __init__(self):
        self.framework = AnalysisFramework()
    
    def score(self, symbol: str, market: str = 'auto') -> Dict:
        """
        综合评分
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            {
                'symbol': 'AAPL',
                'total_score': 75,
                'rating': 'bullish',
                'action': 'buy',
                'breakdown': {
                    'macro': 15,
                    'sector': 15,
                    'technical': 45,
                    'signal_bonus': 0
                },
                'signals': [...],
                'risk': {...},
                'suggestion': '...'
            }
        """
        result = {
            'symbol': symbol,
            'market': market,
            'total_score': 0,
            'rating': 'neutral',
            'level': '中性',
            'action': 'hold',
            'breakdown': {},
            'signals': [],
            'risk': {},
            'suggestion': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }
        
        try:
            # 1. 三层分析
            analysis = analyze_full(symbol, market)
            
            result['breakdown'] = {
                'macro': analysis['macro']['total_score'],
                'sector': analysis['sector']['total_score'],
                'technical': analysis['stock']['total_score'],
                'signal_bonus': 0
            }
            
            result['analysis'] = analysis
            
            # 2. 入场信号
            try:
                signals_result = analyze_entry_signals(symbol)
                result['signals'] = signals_result['signals']
                result['signal_score'] = signals_result['score']
                
                # 信号加成 (±10分)
                if signals_result['score']['overall_score'] >= 80:
                    result['breakdown']['signal_bonus'] = 10
                elif signals_result['score']['overall_score'] >= 70:
                    result['breakdown']['signal_bonus'] = 5
                elif signals_result['score']['overall_score'] <= 30:
                    result['breakdown']['signal_bonus'] = -10
                elif signals_result['score']['overall_score'] <= 40:
                    result['breakdown']['signal_bonus'] = -5
            except:
                pass
            
            # 3. 风险管理
            try:
                risk_result = analyze_risk(symbol)
                result['risk'] = risk_result.get('summary', {})
            except:
                pass
            
            # 4. 计算总分
            total_score = sum(result['breakdown'].values())
            result['total_score'] = min(100, max(0, total_score))
            
            # 5. 确定评级
            for (low, high), level_info in self.SCORE_LEVELS.items():
                if low <= result['total_score'] < high:
                    result['rating'] = level_info['rating']
                    result['level'] = level_info['level']
                    result['action'] = level_info['action']
                    result['suggestion'] = level_info['suggestion']
                    break
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def batch_score(self, symbols: List[str], market: str = 'auto') -> List[Dict]:
        """批量评分"""
        results = []
        for symbol in symbols:
            try:
                result = self.score(symbol, market)
                results.append(result)
            except Exception as e:
                results.append({
                    'symbol': symbol,
                    'error': str(e),
                    'total_score': 0
                })
        
        # 按分数排序
        results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        return results
    
    def generate_report(self, symbol: str, market: str = 'auto') -> str:
        """
        生成 Markdown 分析报告
        
        Args:
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            Markdown 格式的分析报告
        """
        result = self.score(symbol, market)
        
        if result.get('error'):
            return f"# {symbol} 分析失败\n\n错误: {result['error']}"
        
        report = f"""# {symbol} 深度分析报告

**分析时间**: {result['timestamp']}  
**综合评分**: {result['total_score']}/100  
**评级**: {result['level']} ({result['rating']})  
**操作建议**: {result['suggestion']}

---

## 📊 评分明细

| 维度 | 得分 | 满分 |
|------|------|------|
| 宏观环境 | {result['breakdown']['macro']} | 20 |
| 行业分析 | {result['breakdown']['sector']} | 20 |
| 技术分析 | {result['breakdown']['technical']} | 60 |
| 信号加成 | {result['breakdown']['signal_bonus']} | ±10 |
| **总分** | **{result['total_score']}** | **100** |

---

## 🎯 入场信号

"""
        
        if result.get('signals'):
            for i, signal in enumerate(result['signals'], 1):
                report += f"""### {i}. {signal['name']}

- **成功率**: {signal['success_rate']*100:.0f}%
- **置信度**: {signal['confidence']*100:.0f}%
- **样本数**: {signal['samples']}
- **操作**: {signal['action']}
- **风险**: {signal['risk_level']}

"""
        else:
            report += "*未检测到有效入场信号*\n\n"
        
        # 风险管理
        if result.get('risk'):
            risk = result['risk']
            report += f"""---

## ⚠️ 风险管理

| 项目 | 数值 |
|------|------|
| 入场价 | {risk.get('entry_price', 'N/A')} |
| 止损价 | {risk.get('stop_loss', 'N/A')} |
| 止损比例 | {risk.get('stop_loss_pct', 'N/A')}% |
| 目标价 | {risk.get('target_price', 'N/A')} |
| 目标收益 | {risk.get('target_return_pct', 'N/A')}% |
| 建议仓位 | {risk.get('shares', 'N/A')} 股 |
| 仓位金额 | {risk.get('position_value', 'N/A')} |
| 风险金额 | {risk.get('risk_amount', 'N/A')} |
| 风险收益比 | 1:{risk.get('risk_reward_ratio', 2)} |

"""
        
        # 操作建议
        report += f"""---

## 💡 操作建议

**评级**: {result['level']}  
**操作**: {result['action']}  
**建议**: {result['suggestion']}

"""
        
        # 风险提示
        if result['total_score'] < 50:
            report += """⚠️ **风险提示**: 当前评分较低，建议谨慎操作或观望。

"""
        
        report += """---

*免责声明：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
"""
        
        return report


def score_stock(symbol: str, market: str = 'auto') -> Dict:
    """评分入口"""
    engine = ScoringEngine()
    return engine.score(symbol, market)


def generate_score_report(symbol: str, market: str = 'auto') -> str:
    """报告生成入口"""
    engine = ScoringEngine()
    return engine.generate_report(symbol, market)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评分引擎')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--market', default='auto', help='市场类型')
    parser.add_argument('--report', action='store_true', help='生成报告')
    
    args = parser.parse_args()
    
    if args.report:
        report = generate_score_report(args.symbol, args.market)
        print(report)
    else:
        result = score_stock(args.symbol, args.market)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
