#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度投研框架 - 饕餮整合自 china-stock-research, stock-research-executor
8阶段深度投资研究框架
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


class ResearchFramework:
    """
    深度投研框架 - 饕餮整合自 china-stock-research, stock-research-executor
    
    8阶段投研流程:
    1. 公司底座 - 主营业务、盈利构成、客户基础
    2. 行业分析 - 周期阶段、供需关系、竞争格局
    3. 业务拆解 - 盈利模式、定价权、子公司
    4. 财务质量 - 趋势分析、异常检测、风险识别
    5. 公司治理 - 股权结构、管理层激励、资本配置
    6. 市场分歧 - 多空逻辑、关键验证节点
    7. 估值与护城河 - 相对/绝对估值、风险评估
    8. 综合报告 - 信号评级、投资逻辑、数据表格
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.research_dir = OUTPUT_DIR / 'reports' / f'RESEARCH_{symbol}'
        self.research_dir.mkdir(parents=True, exist_ok=True)
        
        self.phases = {
            1: '公司底座',
            2: '行业分析',
            3: '业务拆解',
            4: '财务质量',
            5: '公司治理',
            6: '市场分歧',
            7: '估值护城河',
            8: '综合报告'
        }
    
    def _get_basic_info(self) -> Dict:
        """获取基础信息"""
        result = {
            'symbol': self.symbol,
            'name': None,
            'sector': None,
            'industry': None,
            'market_cap': None,
            'employees': None,
            'website': None,
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            result.update({
                'name': info.get('longName') or info.get('shortName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'employees': info.get('fullTimeEmployees'),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else None,
                'data_source': 'yfinance'
            })
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase1_company_foundation(self) -> Dict:
        """
        Phase 1: 公司底座
        - 主营业务
        - 盈利构成
        - 客户基础
        """
        result = {
            'phase': 1,
            'name': '公司底座',
            'basic_info': {},
            'business_segments': {},
            'revenue_breakdown': {},
            'key_metrics': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 基本信息
            result['basic_info'] = {
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'country': info.get('country'),
                'city': info.get('city'),
                'employees': info.get('fullTimeEmployees'),
                'website': info.get('website'),
                'founded': info.get('startDate')
            }
            
            # 业务概述
            result['business_summary'] = info.get('longBusinessSummary', '')[:1000] if info.get('longBusinessSummary') else None
            
            # 关键财务指标
            result['key_metrics'] = {
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth')
            }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase2_industry_analysis(self) -> Dict:
        """
        Phase 2: 行业分析
        - 周期阶段
        - 供需关系
        - 竞争格局
        """
        result = {
            'phase': 2,
            'name': '行业分析',
            'industry_info': {},
            'competitors': [],
            'industry_trends': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            result['industry_info'] = {
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'industry_key': info.get('industryKey'),
                'industry_disp': info.get('industryDisp')
            }
            
            # 竞争对手 (如果可用)
            competitors = info.get('recommendationKey', '')
            result['competitors_note'] = '需要额外数据源获取竞争对手列表'
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase3_business_breakdown(self) -> Dict:
        """
        Phase 3: 业务拆解
        - 盈利模式
        - 定价权
        - 子公司
        """
        result = {
            'phase': 3,
            'name': '业务拆解',
            'business_model': {},
            'pricing_power': {},
            'subsidiaries': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 盈利模式分析 (基于毛利率)
            gross_margin = info.get('grossMargins', 0)
            operating_margin = info.get('operatingMargins', 0)
            
            result['business_model'] = {
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'net_margin': info.get('profitMargins'),
                'model_assessment': '高毛利' if gross_margin > 0.4 else ('中等毛利' if gross_margin > 0.2 else '低毛利')
            }
            
            # 定价权评估 (基于毛利率稳定性)
            result['pricing_power'] = {
                'assessment': '需要历史数据对比',
                'current_gross_margin': gross_margin
            }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase4_financial_quality(self) -> Dict:
        """
        Phase 4: 财务质量
        - 趋势分析
        - 异常检测
        - 风险识别
        """
        result = {
            'phase': 4,
            'name': '财务质量',
            'balance_sheet': {},
            'income_statement': {},
            'cash_flow': {},
            'financial_ratios': {},
            'risk_flags': [],
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 资产负债表关键指标
            result['balance_sheet'] = {
                'total_assets': info.get('totalAssets'),
                'total_liabilities': info.get('totalLiab'),
                'total_debt': info.get('totalDebt'),
                'net_debt': info.get('netDebt'),
                'total_cash': info.get('totalCash'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'debt_to_equity': info.get('debtToEquity')
            }
            
            # 利润表关键指标
            result['income_statement'] = {
                'total_revenue': info.get('totalRevenue'),
                'gross_profit': info.get('grossProfits'),
                'ebitda': info.get('ebitda'),
                'net_income': info.get('netIncomeToCompany'),
                'operating_income': info.get('operatingIncome')
            }
            
            # 现金流关键指标
            result['cash_flow'] = {
                'operating_cashflow': info.get('operatingCashflow'),
                'free_cashflow': info.get('freeCashflow'),
                'capital_expenditure': info.get('capitalExpenditures')
            }
            
            # 财务比率
            result['financial_ratios'] = {
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'roic': info.get('returnOnAssets'),  # 简化
                'asset_turnover': info.get('revenuePerShare')  # 简化
            }
            
            # 风险识别
            risk_flags = []
            
            if info.get('debtToEquity', 0) and info['debtToEquity'] > 2:
                risk_flags.append('高负债率')
            
            if info.get('currentRatio', 0) and info['currentRatio'] < 1:
                risk_flags.append('流动性风险')
            
            if info.get('operatingCashflow', 0) and info.get('netIncomeToCompany', 0):
                if info['operatingCashflow'] < info['netIncomeToCompany']:
                    risk_flags.append('现金流质量存疑')
            
            result['risk_flags'] = risk_flags if risk_flags else ['无明显风险信号']
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase5_corporate_governance(self) -> Dict:
        """
        Phase 5: 公司治理
        - 股权结构
        - 管理层激励
        - 资本配置
        """
        result = {
            'phase': 5,
            'name': '公司治理',
            'ownership_structure': {},
            'management': {},
            'capital_allocation': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 管理层信息
            result['management'] = {
                'ceo': info.get('companyOfficers', [{}])[0].get('name') if info.get('companyOfficers') else None,
                'officers_count': len(info.get('companyOfficers', []))
            }
            
            # 资本配置
            result['capital_allocation'] = {
                'dividend_rate': info.get('dividendRate'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'buy_back': info.get('shareRepurchased'),  # 可能为空
                'capex_to_revenue': None  # 需要计算
            }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase6_market_divergence(self) -> Dict:
        """
        Phase 6: 市场分歧
        - 多空逻辑
        - 关键验证节点
        """
        result = {
            'phase': 6,
            'name': '市场分歧',
            'analyst_ratings': {},
            'institutional_ownership': {},
            'short_interest': {},
            'sentiment_indicators': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 分析师评级
            result['analyst_ratings'] = {
                'recommendation': info.get('recommendationKey'),
                'target_price': info.get('targetMeanPrice'),
                'number_of_analysts': info.get('numberOfAnalystOpinions')
            }
            
            # 机构持股
            result['institutional_ownership'] = {
                'institution_ownership_ratio': info.get('heldPercentInstitutions'),
                'insider_purchases': info.get('insiderTransactions')  # 可能为空
            }
            
            # 做空情况
            result['short_interest'] = {
                'short_ratio': info.get('shortRatio'),
                'short_percent': info.get('shortPercentOfFloat')
            }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase7_valuation_moat(self) -> Dict:
        """
        Phase 7: 估值与护城河
        - 相对估值
        - 绝对估值
        - 风险评估
        """
        result = {
            'phase': 7,
            'name': '估值护城河',
            'relative_valuation': {},
            'absolute_valuation': {},
            'moat_assessment': {},
            'risk_assessment': {},
            'data_source': 'none',
            'error': None
        }
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            
            # 相对估值
            result['relative_valuation'] = {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'peg_ratio': info.get('pegRatio')
            }
            
            # 护城河评估 (简化版)
            gross_margin = info.get('grossMargins', 0)
            roe = info.get('returnOnEquity', 0)
            
            moat_score = 0
            if gross_margin > 0.4:
                moat_score += 2
            elif gross_margin > 0.25:
                moat_score += 1
            
            if roe and roe > 0.2:
                moat_score += 2
            elif roe and roe > 0.1:
                moat_score += 1
            
            moat_level = '宽护城河' if moat_score >= 4 else ('窄护城河' if moat_score >= 2 else '无明显护城河')
            
            result['moat_assessment'] = {
                'score': moat_score,
                'level': moat_level,
                'factors': {
                    'gross_margin': gross_margin,
                    'roe': roe
                }
            }
            
            # 风险评估
            risk_score = 0
            if info.get('debtToEquity', 0) and info['debtToEquity'] > 2:
                risk_score += 2
            if info.get('currentRatio', 0) and info['currentRatio'] < 1:
                risk_score += 2
            if info.get('shortPercentOfFloat', 0) and info['shortPercentOfFloat'] > 0.1:
                risk_score += 1
            
            risk_level = '高风险' if risk_score >= 4 else ('中等风险' if risk_score >= 2 else '低风险')
            
            result['risk_assessment'] = {
                'score': risk_score,
                'level': risk_level
            }
            
            result['data_source'] = 'yfinance'
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def phase8_comprehensive_report(self) -> Dict:
        """
        Phase 8: 综合报告
        - 信号评级
        - 投资逻辑
        - 数据表格
        """
        result = {
            'phase': 8,
            'name': '综合报告',
            'executive_summary': {},
            'investment_thesis': {},
            'key_signals': {},
            'recommendation': None,
            'data_source': 'yfinance',
            'error': None
        }
        
        try:
            # 收集前面各阶段的关键信息
            p1 = self.phase1_company_foundation()
            p4 = self.phase4_financial_quality()
            p7 = self.phase7_valuation_moat()
            
            # 执行摘要
            result['executive_summary'] = {
                'company_name': p1.get('basic_info', {}).get('name'),
                'sector': p1.get('basic_info', {}).get('sector'),
                'industry': p1.get('basic_info', {}).get('industry'),
                'market_cap': p1.get('key_metrics', {}).get('market_cap'),
                'pe_ratio': p1.get('key_metrics', {}).get('pe_ratio'),
                'roe': p1.get('key_metrics', {}).get('roe')
            }
            
            # 关键信号
            signals = []
            
            # 财务质量信号
            if p4.get('risk_flags'):
                signals.extend([f"风险: {flag}" for flag in p4['risk_flags']])
            else:
                signals.append("信号: 财务质量良好")
            
            # 估值信号
            moat = p7.get('moat_assessment', {}).get('level')
            if moat:
                signals.append(f"护城河: {moat}")
            
            risk = p7.get('risk_assessment', {}).get('level')
            if risk:
                signals.append(f"风险等级: {risk}")
            
            result['key_signals'] = signals
            
            # 投资建议 (简化版)
            moat_score = p7.get('moat_assessment', {}).get('score', 0)
            risk_score = p7.get('risk_assessment', {}).get('score', 0)
            pe = p1.get('key_metrics', {}).get('pe_ratio', 0)
            
            if moat_score >= 4 and risk_score < 2:
                if pe and pe < 25:
                    result['recommendation'] = '强烈买入 - 优质低估值'
                else:
                    result['recommendation'] = '买入 - 优质公司'
            elif moat_score >= 2:
                if risk_score < 2:
                    result['recommendation'] = '持有 - 稳健标的'
                else:
                    result['recommendation'] = '观望 - 需关注风险'
            else:
                result['recommendation'] = '谨慎 - 护城河不明显'
            
            result['report_generated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_full_research(self) -> Dict:
        """执行完整投研流程"""
        result = {
            'symbol': self.symbol,
            'research_date': datetime.now().strftime('%Y-%m-%d'),
            'phases': {},
            'summary': {},
            'error': None
        }
        
        try:
            # 执行所有阶段
            result['phases'] = {
                'phase1': self.phase1_company_foundation(),
                'phase2': self.phase2_industry_analysis(),
                'phase3': self.phase3_business_breakdown(),
                'phase4': self.phase4_financial_quality(),
                'phase5': self.phase5_corporate_governance(),
                'phase6': self.phase6_market_divergence(),
                'phase7': self.phase7_valuation_moat(),
                'phase8': self.phase8_comprehensive_report()
            }
            
            # 提取摘要
            p8 = result['phases']['phase8']
            result['summary'] = {
                'recommendation': p8.get('recommendation'),
                'key_signals': p8.get('key_signals'),
                'executive_summary': p8.get('executive_summary')
            }
            
        except Exception as e:
            result['error'] = str(e)
        
        return result


def run_research(symbol: str, phase: int = None) -> Dict:
    """执行投研分析"""
    framework = ResearchFramework(symbol)
    
    if phase:
        phase_methods = {
            1: framework.phase1_company_foundation,
            2: framework.phase2_industry_analysis,
            3: framework.phase3_business_breakdown,
            4: framework.phase4_financial_quality,
            5: framework.phase5_corporate_governance,
            6: framework.phase6_market_divergence,
            7: framework.phase7_valuation_moat,
            8: framework.phase8_comprehensive_report
        }
        return phase_methods.get(phase, framework.phase1_company_foundation)()
    else:
        return framework.run_full_research()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='深度投研框架 - 饕餮整合自 china-stock-research')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--phase', type=int, choices=range(1, 9), help='执行指定阶段')
    parser.add_argument('--full', action='store_true', help='执行完整分析')
    
    args = parser.parse_args()
    
    framework = ResearchFramework(args.symbol)
    
    if args.full or not args.phase:
        result = framework.run_full_research()
    else:
        result = run_research(args.symbol, args.phase)
    
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
