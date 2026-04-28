#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资尽调分析器 v1.1
- 完整8阶段基本面分析
- HTML报告输出
- 数据可视化
- 框架适配股票特性
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    yf = None
    YFINANCE_AVAILABLE = False

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from skills.shared import (
        MISSING_TEXT,
        CitationValidator,
        RiskMonitor,
        assert_report_quality,
        normalize_report_text,
        safe_cn,
        stock_display_name,
        translate_industry,
        translate_rating,
        translate_sector,
    )
    SHARED_MODULES_AVAILABLE = True
except ImportError:
    MISSING_TEXT = '暂无数据'
    assert_report_quality = lambda text, require_layered_conclusion=False: None
    normalize_report_text = lambda text: text.replace('N/A', MISSING_TEXT)
    safe_cn = lambda value, default=MISSING_TEXT: default if value in (None, '', 'N/A', 'Unknown') else str(value)
    stock_display_name = lambda symbol, info=None: f"上市公司（{symbol}）"
    translate_industry = safe_cn
    translate_rating = safe_cn
    translate_sector = safe_cn
    SHARED_MODULES_AVAILABLE = False


class InvestmentStyle:
    """投资风格"""
    VALUE = 'value'        # 价值投资
    GROWTH = 'growth'      # 成长投资
    TURNAROUND = 'turnaround'  # 困境反转
    DIVIDEND = 'dividend'  # 红利投资


class SignalRating:
    """信号评级"""
    STRONG_BUY = '🟢🟢🟢'
    HOLD = '🟡🟡🟡'
    SELL = '🔴🔴'


class StockAnalyzer:
    """股票投资尽调分析器"""
    
    # 行业周期判断指标
    INDUSTRY_CYCLES = {
        'Technology': {'cycle': '成长期', 'growth_rate': 15},
        'Healthcare': {'cycle': '成长期', 'growth_rate': 10},
        'Financial Services': {'cycle': '成熟期', 'growth_rate': 5},
        'Consumer Cyclical': {'cycle': '周期型', 'growth_rate': 3},
        'Consumer Defensive': {'cycle': '防御型', 'growth_rate': 5},
        'Energy': {'cycle': '周期型', 'growth_rate': 0},
        'Industrials': {'cycle': '成熟期', 'growth_rate': 5},
        'Basic Materials': {'cycle': '周期型', 'growth_rate': 3},
        'Real Estate': {'cycle': '成熟期', 'growth_rate': 5},
        'Utilities': {'cycle': '成熟期', 'growth_rate': 3},
        'Communication Services': {'cycle': '成熟期', 'growth_rate': 8},
    }
    
    def __init__(self, style: str = InvestmentStyle.VALUE):
        """
        初始化分析器
        
        Args:
            style: 投资风格 (value/growth/turnaround/dividend)
        """
        self.style = style
        self.validator = CitationValidator() if SHARED_MODULES_AVAILABLE and CitationValidator else None
        self.monitor = RiskMonitor(asset_type='stock') if SHARED_MODULES_AVAILABLE and RiskMonitor else None
        
        # 根据投资风格设置阶段优先级
        self.phase_priority = self._get_phase_priority(style)
    
    def _get_phase_priority(self, style: str) -> Dict:
        """根据投资风格获取阶段优先级"""
        priorities = {
            InvestmentStyle.VALUE: {
                'core': [4, 5, 7],      # 财务、治理、估值
                'secondary': [1, 2, 3],  # 业务、行业、拆解
                'optional': [6]          # 市场分歧
            },
            InvestmentStyle.GROWTH: {
                'core': [1, 2, 3],       # 业务、行业、拆解
                'secondary': [4, 7],     # 财务、估值
                'optional': [5, 6]       # 治理、分歧
            },
            InvestmentStyle.TURNAROUND: {
                'core': [4, 5],          # 财务、治理
                'secondary': [1, 6],     # 业务、分歧
                'optional': [2, 3, 7]    # 行业、拆解、估值
            },
            InvestmentStyle.DIVIDEND: {
                'core': [4, 5, 7],       # 财务、治理、估值
                'secondary': [1, 3],     # 业务、拆解
                'optional': [2, 6]       # 行业、分歧
            }
        }
        return priorities.get(style, priorities[InvestmentStyle.VALUE])
    
    def analyze(self, symbol: str, depth: str = 'standard') -> Dict:
        """
        执行完整分析
        
        Args:
            symbol: 股票代码
            depth: 分析深度 (quick/standard/deep)
            
        Returns:
            分析结果字典
        """
        print(f"开始分析 {symbol} (风格: {self.style}, 深度: {depth})")
        if not YFINANCE_AVAILABLE:
            return {
                'symbol': symbol,
                'display_name': stock_display_name(symbol, {}),
                'style': self.style,
                'timestamp': datetime.now().isoformat(),
                'phases': {},
                'rating': {
                    'rating': SignalRating.HOLD,
                    'score': 0,
                    'max_score': 5,
                    'recommendation': '行情数据依赖未安装，无法形成充分验证的研究结论'
                },
                'warnings': ['yfinance未安装，未拉取行情与财务数据；报告不得使用模拟数据补齐。']
            }
        
        display_name = stock_display_name(symbol, {})
        results = {
            'symbol': symbol,
            'display_name': display_name,
            'style': self.style,
            'timestamp': datetime.now().isoformat(),
            'phases': {}
        }
        
        # 根据深度决定执行哪些阶段
        if depth == 'quick':
            phases_to_run = self.phase_priority['core']
        elif depth == 'standard':
            phases_to_run = self.phase_priority['core'] + self.phase_priority['secondary']
        else:  # deep
            phases_to_run = list(range(1, 9))
        
        # 执行各阶段分析
        for phase_num in phases_to_run:
            phase_method = getattr(self, f'_phase{phase_num}', None)
            if phase_method:
                print(f"  Phase {phase_num}...")
                results['phases'][phase_num] = phase_method(symbol)
                if phase_num == 1:
                    basic = results['phases'][phase_num].get('data', {}).get('公司基本信息', {})
                    if basic.get('股票名称'):
                        results['display_name'] = basic['股票名称']
        
        # 综合评分
        results['rating'] = self._calculate_rating(results)
        
        # 生成监控清单
        if self.monitor:
            results['monitoring_checklist'] = self.monitor.generate_checklist(symbol)
        
        return results
    
    def _phase1(self, symbol: str) -> Dict:
        """Phase 1: 公司事实底座"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取收入构成 (如果有)
            revenue_breakdown = self._get_revenue_breakdown(ticker)
            
            display_name = stock_display_name(symbol, info)
            return {
                'name': '公司事实底座',
                'data': {
                    '公司基本信息': {
                        '股票名称': display_name,
                        '股票代码': symbol,
                        '公司名称': display_name,
                        '所属行业': translate_industry(info.get('industry')),
                        '所属板块': translate_sector(info.get('sector')),
                        '员工数量': f"{info.get('fullTimeEmployees', 0):,}" if info.get('fullTimeEmployees') else MISSING_TEXT,
                        '成立时间': safe_cn(info.get('startDate')),
                        '总部地址': self._format_headquarters(info),
                    },
                    '主营业务': {
                        '业务描述': info.get('longBusinessSummary', '')[:500] + '...' if len(info.get('longBusinessSummary', '')) > 500 else info.get('longBusinessSummary', ''),
                        '主要产品': self._extract_products(info),
                    },
                    '收入构成': revenue_breakdown,
                    '产业链位置': self._analyze_value_chain(info),
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '公司事实底座'}
    
    def _phase2(self, symbol: str) -> Dict:
        """Phase 2: 行业周期分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            # 获取行业周期信息
            cycle_info = self.INDUSTRY_CYCLES.get(sector, {'cycle': '未知', 'growth_rate': 0})
            
            # 获取行业相关数据
            industry_trend = self._analyze_industry_trend(info)
            competition = self._analyze_competition(info)
            
            return {
                'name': '行业周期分析',
                'data': {
                    '行业概况': {
                        '所属行业': translate_industry(industry),
                        '所属板块': translate_sector(sector),
                        '周期阶段': cycle_info['cycle'],
                        '行业增速': f"{cycle_info['growth_rate']}%",
                    },
                    '供需格局': industry_trend,
                    '竞争态势': competition,
                    '政策影响': self._analyze_policy_impact(sector),
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '行业周期分析'}
    
    def _phase3(self, symbol: str) -> Dict:
        """Phase 3: 业务拆解"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 业务板块分析
            segments = self._analyze_segments(ticker, info)
            
            # 赚钱机制
            profit_model = self._analyze_profit_model(info)
            
            # 定价权分析
            pricing_power = self._analyze_pricing_power(info)
            
            return {
                'name': '业务拆解',
                'data': {
                    '业务板块': segments,
                    '赚钱机制': profit_model,
                    '定价权分析': pricing_power,
                    '商业本质': self._summarize_business_model(info),
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '业务拆解'}
    
    def _phase4(self, symbol: str) -> Dict:
        """Phase 4: 财务质量分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取财务报表数据
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            print(f'    财务报表状态: fin={not financials.empty}, bs={not balance_sheet.empty}, cf={not cashflow.empty}')
            
            # 从财务报表获取数据（更可靠）
            net_income = 0
            total_revenue = 0
            gross_profit = 0
            operating_income = 0
            ebitda = 0
            total_assets = 0
            total_debt = 0
            stockholders_equity = 0
            current_assets = 0
            current_liabilities = 0
            cash = 0
            operating_cf = 0
            free_cf = 0
            capex = 0
            
            try:
                # 损益表数据
                if not financials.empty:
                    if 'Net Income' in financials.index:
                        net_income = float(financials.loc['Net Income'].iloc[0])
                    if 'Total Revenue' in financials.index:
                        total_revenue = float(financials.loc['Total Revenue'].iloc[0])
                    if 'Gross Profit' in financials.index:
                        gross_profit = float(financials.loc['Gross Profit'].iloc[0])
                    if 'Operating Income' in financials.index:
                        operating_income = float(financials.loc['Operating Income'].iloc[0])
                    if 'EBITDA' in financials.index:
                        ebitda = float(financials.loc['EBITDA'].iloc[0])
                
                # 资产负债表数据
                if not balance_sheet.empty:
                    if 'Total Assets' in balance_sheet.index:
                        total_assets = float(balance_sheet.loc['Total Assets'].iloc[0])
                    if 'Total Debt' in balance_sheet.index:
                        total_debt = float(balance_sheet.loc['Total Debt'].iloc[0])
                    if 'Stockholders Equity' in balance_sheet.index:
                        stockholders_equity = float(balance_sheet.loc['Stockholders Equity'].iloc[0])
                    if 'Current Assets' in balance_sheet.index:
                        current_assets = float(balance_sheet.loc['Current Assets'].iloc[0])
                    if 'Current Liabilities' in balance_sheet.index:
                        current_liabilities = float(balance_sheet.loc['Current Liabilities'].iloc[0])
                    if 'Cash And Cash Equivalents' in balance_sheet.index:
                        cash = float(balance_sheet.loc['Cash And Cash Equivalents'].iloc[0])
                
                # 现金流量表数据
                if not cashflow.empty:
                    if 'Operating Cash Flow' in cashflow.index:
                        operating_cf = float(cashflow.loc['Operating Cash Flow'].iloc[0])
                    if 'Free Cash Flow' in cashflow.index:
                        free_cf = float(cashflow.loc['Free Cash Flow'].iloc[0])
                    if 'Capital Expenditure' in cashflow.index:
                        capex = float(cashflow.loc['Capital Expenditure'].iloc[0])
                
                print(f'    数据获取: NI={net_income/1e9:.1f}B, Equity={stockholders_equity/1e9:.1f}B, OCF={operating_cf/1e9:.1f}B')
                
            except Exception as e:
                print(f'    财务报表获取失败: {e}')
            
            # 备用：从info获取
            if net_income == 0:
                net_income = info.get('netIncomeToCommon', 0) or info.get('netIncome', 0) or 0
            if total_revenue == 0:
                total_revenue = info.get('totalRevenue', 0) or 0
            if stockholders_equity == 0:
                stockholders_equity = info.get('totalStockholderEquity', 0) or 0
            if operating_cf == 0:
                operating_cf = info.get('operatingCashflow', 0) or 0
            
            # 计算关键指标
            roe = (net_income / stockholders_equity * 100) if stockholders_equity and stockholders_equity > 0 else 0
            roa = (net_income / total_assets * 100) if total_assets and total_assets > 0 else 0
            
            # 毛利率和净利率
            if gross_profit > 0 and total_revenue > 0:
                gross_margin = gross_profit / total_revenue
            else:
                gross_margin = info.get('grossMargins', 0) or 0
            
            if net_income > 0 and total_revenue > 0:
                net_margin = net_income / total_revenue
            else:
                net_margin = info.get('profitMargins', 0) or 0
            
            ocf_to_ni = (operating_cf / net_income) if net_income and net_income != 0 else 0
            debt_to_equity = (total_debt / stockholders_equity) if stockholders_equity and stockholders_equity > 0 else 0
            current_ratio = (current_assets / current_liabilities) if current_liabilities and current_liabilities > 0 else 0
            
            # 现金流验证判断
            if ocf_to_ni > 1.0:
                cashflow_check = '✅ 优秀'
                cashflow_desc = '利润质量高，现金流充沛'
            elif ocf_to_ni > 0.8:
                cashflow_check = '✅ 良好'
                cashflow_desc = '现金流与利润匹配良好'
            elif ocf_to_ni > 0.5:
                cashflow_check = '⚠️ 一般'
                cashflow_desc = '现金流偏弱，需关注'
            else:
                cashflow_check = '❌ 较差'
                cashflow_desc = '现金流差，需警惕利润质量'
            
            # 异常排查
            warnings = self._check_financial_warnings(info, ocf_to_ni, debt_to_equity)
            
            # 同行对比
            peer_comparison = self._get_peer_comparison(symbol, info)
            
            return {
                'name': '财务质量分析',
                'data': {
                    '关键指标': {
                        'ROE': f'{roe:.1f}%',
                        'ROA': f'{roa:.1f}%',
                        '毛利率': f'{gross_margin*100:.1f}%' if gross_margin < 1 else f'{gross_margin:.1f}%',
                        '净利率': f'{net_margin*100:.1f}%' if net_margin < 1 else f'{net_margin:.1f}%',
                        '负债率': f'{debt_to_equity:.2f}',
                        '流动比率': f'{current_ratio:.2f}' if current_ratio else MISSING_TEXT,
                    },
                    '现金流验证': {
                        '经营现金流': f'${operating_cf/1e9:.1f}B' if operating_cf else MISSING_TEXT,
                        '自由现金流': f'${free_cf/1e9:.1f}B' if free_cf else MISSING_TEXT,
                        'OCF/净利润': f'{ocf_to_ni:.2f}',
                        '判断': cashflow_check,
                        '说明': cashflow_desc,
                    },
                    '异常排查': warnings,
                    '同行对比': peer_comparison,
                    '数据来源': 'yfinance财务报表',
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
            
        except Exception as e:
            return {'error': str(e), 'name': '财务质量分析'}
    
    def _phase5(self, symbol: str) -> Dict:
        """Phase 5: 股权治理分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 股权结构
            institutional_ownership = info.get('heldPercentInstitutions', 0) * 100
            insider_ownership = info.get('heldPercentInsiders', 0) * 100
            
            # 管理层信息
            management = self._get_management_info(info)
            
            # 资本配置历史
            capital_allocation = self._analyze_capital_allocation(info)
            
            # ROIC计算
            roic = self._calculate_roic(info)
            
            return {
                'name': '股权治理分析',
                'data': {
                    '股权结构': {
                        '机构持股': f'{institutional_ownership:.1f}%',
                        '内部人持股': f'{insider_ownership:.1f}%',
                        '流通股': f"{info.get('floatShares', 0):,}" if info.get('floatShares') else MISSING_TEXT,
                        '总股本': f"{info.get('sharesOutstanding', 0):,}" if info.get('sharesOutstanding') else MISSING_TEXT,
                    },
                    '管理层': management,
                    '资本配置': capital_allocation,
                    'ROIC': f'{roic:.1f}%' if roic else MISSING_TEXT,
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '股权治理分析'}
    
    def _phase6(self, symbol: str) -> Dict:
        """Phase 6: 市场分歧分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('currentPrice', 0)
            target_price = info.get('targetMeanPrice', 0)
            
            # 多空逻辑
            bull_case = self._build_bull_case(info)
            bear_case = self._build_bear_case(info)
            
            # 关键验证节点
            verification_nodes = self._identify_verification_nodes(info)
            
            # 分析师观点
            recommendation = info.get('recommendationKey', 'hold')
            analyst_count = info.get('numberOfAnalystOpinions', 0)
            
            return {
                'name': '市场分歧分析',
                'data': {
                    '分析师观点': {
                        '评级': translate_rating(recommendation),
                        '目标价': f'${target_price:.2f}' if target_price else MISSING_TEXT,
                        '当前价': f'${current_price:.2f}' if current_price else MISSING_TEXT,
                        '潜在空间': f'{(target_price/current_price - 1)*100:.1f}%' if target_price and current_price else MISSING_TEXT,
                        '分析师数量': analyst_count,
                    },
                    '多方逻辑': bull_case,
                    '空方逻辑': bear_case,
                    '关键验证节点': verification_nodes,
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '市场分歧分析'}
    
    def _phase7(self, symbol: str) -> Dict:
        """Phase 7: 估值与护城河分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 估值指标
            pe_ratio = info.get('trailingPE', 0) or info.get('forwardPE', 0)
            pb_ratio = info.get('priceToBook', 0)
            ps_ratio = info.get('priceToSalesTrailing12Months', 0)
            ev_ebitda = info.get('enterpriseToEbitda', 0)
            peg_ratio = info.get('pegRatio', 0)
            
            # 估值分位 (简化判断)
            valuation_level = self._assess_valuation_level(pe_ratio, pb_ratio, info.get('sector', ''))
            
            # 护城河评分
            moat_score = self._estimate_moat(info)
            moat_details = self._get_moat_details(info)
            
            # DCF简化估值
            dcf_value = self._simple_dcf(info)
            
            return {
                'name': '估值与护城河',
                'data': {
                    '估值指标': {
                        'P/E (TTM)': f'{pe_ratio:.1f}' if pe_ratio else MISSING_TEXT,
                        'P/B': f'{pb_ratio:.1f}' if pb_ratio else MISSING_TEXT,
                        'P/S': f'{ps_ratio:.1f}' if ps_ratio else MISSING_TEXT,
                        'EV/EBITDA': f'{ev_ebitda:.1f}' if ev_ebitda else MISSING_TEXT,
                        'PEG': f'{peg_ratio:.2f}' if peg_ratio else MISSING_TEXT,
                    },
                    '估值判断': valuation_level,
                    '护城河评分': {
                        '总分': f'{moat_score}/5',
                        '评级': self._get_moat_desc(moat_score),
                        '详细分析': moat_details,
                    },
                    'DCF估值': dcf_value,
                },
                'citation': self._cite('yfinance') if self.validator else None
            }
        except Exception as e:
            return {'error': str(e), 'name': '估值与护城河'}
    
    def _phase8(self, symbol: str) -> Dict:
        """Phase 8: 综合报告"""
        return {
            'name': '综合报告',
            'signal_rating': '待计算',
            'investment_thesis': '待生成'
        }
    
    # ==================== 辅助方法 ====================
    
    def _get_revenue_breakdown(self, ticker) -> Dict:
        """获取收入构成"""
        try:
            # yfinance 不直接提供收入分解，使用简化判断
            return {
                '主营业务': '占主要收入',
                '其他业务': '补充收入',
                '说明': '详细收入分解需查阅年报'
            }
        except:
            return {'说明': '数据暂不可用'}

    def _format_headquarters(self, info: Dict) -> str:
        """格式化总部信息，避免英文缺失占位进入中文报告。"""
        city = safe_cn(info.get('city'), '')
        country = safe_cn(info.get('country'), '')
        parts = [part for part in [city, country] if part]
        return '，'.join(parts) if parts else MISSING_TEXT
    
    def _extract_products(self, info: Dict) -> str:
        """提取主要产品"""
        industry = translate_industry(info.get('industry'))
        sector = info.get('sector', '')
        
        # 简化产品描述
        if 'Technology' in sector:
            return '软件/硬件产品和服务'
        elif 'Healthcare' in sector:
            return '医疗产品/服务'
        elif 'Financial' in sector:
            return '金融服务'
        else:
            return f'{industry}相关产品或服务' if industry != MISSING_TEXT else '主要产品或服务需查阅年报'
    
    def _analyze_value_chain(self, info: Dict) -> Dict:
        """分析产业链位置"""
        return {
            '上游': '原材料/零部件供应商',
            '中游': stock_display_name('', info).replace('（未知代码）', ''),
            '下游': '终端客户/消费者',
            '地位': '需进一步分析市场地位'
        }
    
    def _analyze_industry_trend(self, info: Dict) -> Dict:
        """分析行业趋势"""
        sector = info.get('sector', '')
        cycle_info = self.INDUSTRY_CYCLES.get(sector, {'cycle': '未知', 'growth_rate': 0})
        
        return {
            '趋势': cycle_info['cycle'],
            '增长预期': f"{cycle_info['growth_rate']}% 年均增速",
            '驱动因素': '需查阅行业研究报告'
        }
    
    def _analyze_competition(self, info: Dict) -> Dict:
        """分析竞争态势"""
        market_cap = info.get('marketCap', 0)
        
        if market_cap > 1e11:  # 1000亿
            position = '行业龙头'
        elif market_cap > 1e10:  # 100亿
            position = '行业前列'
        else:
            position = '行业参与者'
        
        return {
            '市场地位': position,
            '竞争格局': '需进一步分析竞争者情况',
        }
    
    def _analyze_policy_impact(self, sector: str) -> str:
        """分析政策影响"""
        policy_map = {
            'Technology': '科技政策、数据安全法规影响较大',
            'Healthcare': '医保政策、药品审批影响较大',
            'Financial Services': '金融监管政策影响大',
            'Energy': '环保政策、能源政策影响大',
            'Real Estate': '房地产调控政策影响大',
        }
        return policy_map.get(sector, '行业政策需关注')
    
    def _analyze_segments(self, ticker, info: Dict) -> Dict:
        """分析业务板块"""
        return {
            '主营业务': {
                '描述': translate_industry(info.get('industry')),
                '收入占比': '占主要部分',
            },
            '说明': '详细业务分解需查阅年报分部报告'
        }
    
    def _analyze_profit_model(self, info: Dict) -> Dict:
        """分析赚钱机制"""
        gross_margin = info.get('grossMargins', 0) * 100
        net_margin = info.get('profitMargins', 0) * 100
        
        if gross_margin > 50:
            model = '高毛利模式 (品牌/技术溢价)'
        elif gross_margin > 30:
            model = '中等毛利模式 (差异化竞争)'
        else:
            model = '低毛利模式 (成本竞争)'
        
        return {
            '盈利模式': model,
            '毛利率水平': f'{gross_margin:.1f}%',
            '净利率水平': f'{net_margin:.1f}%',
        }
    
    def _analyze_pricing_power(self, info: Dict) -> Dict:
        """分析定价权"""
        gross_margin = info.get('grossMargins', 0)
        
        if gross_margin > 0.5:
            return {
                '定价权': '较强',
                '依据': f'毛利率{gross_margin*100:.1f}%，说明有一定定价能力'
            }
        else:
            return {
                '定价权': '一般',
                '依据': f'毛利率{gross_margin*100:.1f}%，竞争可能较激烈'
            }
    
    def _summarize_business_model(self, info: Dict) -> str:
        """总结商业模式"""
        industry = translate_industry(info.get('industry'))
        sector = translate_sector(info.get('sector'))
        
        return f"主营{industry}业务，属于{sector}板块"
    
    def _calculate_financial_trends(self, info: Dict) -> Dict:
        """计算财务趋势"""
        return {
            '说明': '需多年财务数据，建议查阅年报',
        }
    
    def _check_financial_warnings(self, info: Dict, ocf_to_ni: float, debt_to_equity: float) -> List[str]:
        """检查财务异常"""
        warnings = []
        
        # 现金流检查
        if ocf_to_ni < 0.5:
            warnings.append('⚠️ OCF/净利润 < 0.5，利润质量存疑')
        else:
            warnings.append('✅ 现金流健康')
        
        # 负债检查
        if debt_to_equity > 2:
            warnings.append('⚠️ 负债率 > 2，财务杠杆较高')
        elif debt_to_equity > 1:
            warnings.append('⚠️ 负债率 > 1，需关注偿债能力')
        else:
            warnings.append('✅ 负债率健康')
        
        # 盈利检查
        if info.get('profitMargins', 0) < 0:
            warnings.append('❌ 净利率为负，处于亏损状态')
        else:
            warnings.append('✅ 盈利正常')
        
        return warnings
    
    def _get_peer_comparison(self, symbol: str, info: Dict) -> Dict:
        """获取同行对比"""
        return {
            '说明': '同行对比需获取同行业公司数据',
            '建议': f'比较{translate_industry(info.get("industry"))}其他公司指标'
        }
    
    def _get_management_info(self, info: Dict) -> Dict:
        """获取管理层信息"""
        return {
            'CEO': info.get('companyOfficers', [{}])[0].get('name', MISSING_TEXT) if info.get('companyOfficers') else MISSING_TEXT,
            '说明': '详细管理层信息需查阅公司治理报告'
        }
    
    def _analyze_capital_allocation(self, info: Dict) -> Dict:
        """分析资本配置"""
        return {
            '分红政策': f"股息率 {info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else '不分红',
            '回购': '需查阅公告',
            '投资': '需查阅年报资本支出'
        }
    
    def _calculate_roic(self, info: Dict) -> Optional[float]:
        """计算ROIC"""
        try:
            ebit = info.get('ebit', 0)
            total_debt = info.get('totalDebt', 0)
            equity = info.get('totalStockholderEquity', 0)
            cash = info.get('totalCash', 0)
            
            invested_capital = total_debt + equity - cash
            if invested_capital > 0 and ebit:
                return ebit / invested_capital * 100
        except:
            pass
        return None
    
    def _build_bull_case(self, info: Dict) -> List[str]:
        """构建多方逻辑"""
        bull_points = []
        
        if info.get('grossMargins', 0) > 0.4:
            bull_points.append('毛利率高，盈利能力强')
        
        if info.get('returnOnEquity', 0) > 0.15:
            bull_points.append(f"ROE {info.get('returnOnEquity', 0)*100:.1f}%，资本回报优秀")
        
        if info.get('revenueGrowth', 0) > 0.1:
            bull_points.append(f"收入增长 {info.get('revenueGrowth', 0)*100:.1f}%，成长性好")
        
        if not bull_points:
            bull_points.append('需进一步分析竞争优势')
        
        return bull_points
    
    def _build_bear_case(self, info: Dict) -> List[str]:
        """构建空方逻辑"""
        bear_points = []
        
        if info.get('trailingPE', 0) > 30:
            bear_points.append(f"P/E {info.get('trailingPE', 0):.1f}，估值偏高")
        
        if info.get('totalDebt', 0) / info.get('totalStockholderEquity', 1) > 1:
            bear_points.append('负债率较高，财务风险')
        
        if info.get('profitMargins', 0) < 0.1:
            bear_points.append('净利率偏低，盈利能力存疑')
        
        if not bear_points:
            bear_points.append('风险因素需进一步研究')
        
        return bear_points
    
    def _identify_verification_nodes(self, info: Dict) -> List[str]:
        """识别验证节点"""
        return [
            '下季度财报发布',
            '年度业绩预告',
            '行业政策变化',
            '竞争对手动态'
        ]
    
    def _assess_valuation_level(self, pe: float, pb: float, sector: str) -> Dict:
        """评估估值水平"""
        if not pe:
            return {'判断': '数据不足', '说明': '无法判断估值水平'}
        
        # 行业PE参考
        sector_pe = {
            'Technology': 25,
            'Healthcare': 20,
            'Financial Services': 12,
            'Consumer Cyclical': 18,
            'Consumer Defensive': 15,
            'Energy': 10,
            'Industrials': 15,
        }
        
        avg_pe = sector_pe.get(sector, 15)
        
        if pe < avg_pe * 0.8:
            level = '低估'
            color = '🟢'
        elif pe < avg_pe * 1.2:
            level = '合理'
            color = '🟡'
        else:
            level = '高估'
            color = '🔴'
        
        return {
            '判断': f'{color} {level}',
            'P/E': f'{pe:.1f}',
            '行业平均': f'{avg_pe:.1f}',
            '说明': f'相对行业平均{avg_pe}倍PE，当前估值{level}'
        }
    
    def _estimate_moat(self, info: Dict) -> int:
        """估算护城河评分"""
        score = 0
        
        # 毛利率 (定价权)
        gross_margin = info.get('grossMargins', 0)
        if gross_margin > 0.5:
            score += 1
        if gross_margin > 0.7:
            score += 1
        
        # 市值 (规模效应)
        market_cap = info.get('marketCap', 0)
        if market_cap > 1e11:
            score += 1
        
        # ROE (盈利能力)
        roe = info.get('returnOnEquity', 0)
        if roe > 0.15:
            score += 1
        if roe > 0.20:
            score += 1
        
        # 品牌溢价 (简化判断)
        if info.get('grossMargins', 0) > 0.6:
            score += 1
        
        return min(score, 5)
    
    def _get_moat_details(self, info: Dict) -> Dict:
        """护城河详细分析"""
        gross_margin = info.get('grossMargins', 0)
        roe = info.get('returnOnEquity', 0)
        market_cap = info.get('marketCap', 0)
        
        return {
            '定价权': f'{gross_margin*100:.1f}% 毛利率' + (' (强)' if gross_margin > 0.5 else ''),
            '盈利能力': f'{roe*100:.1f}% ROE' + (' (优秀)' if roe > 0.15 else ''),
            '规模效应': f'{market_cap/1e9:.0f}亿市值' + (' (龙头)' if market_cap > 1e11 else ''),
        }
    
    def _get_moat_desc(self, score: int) -> str:
        """获取护城河描述"""
        if score >= 5:
            return '强护城河'
        elif score >= 3:
            return '中等护城河'
        else:
            return '弱护城河'
    
    def _simple_dcf(self, info: Dict) -> Dict:
        """简化DCF估值"""
        return {
            '说明': 'DCF估值需更多财务数据和假设',
            '建议': '建议使用专业估值模型'
        }
    
    def _calculate_rating(self, results: Dict) -> Dict:
        """计算综合评级"""
        score = 0
        
        # 财务质量评分
        if 4 in results['phases']:
            phase4 = results['phases'][4]
            if 'data' in phase4:
                cf_check = phase4['data'].get('现金流验证', {}).get('判断', '')
                if '优秀' in cf_check:
                    score += 2
                elif '良好' in cf_check:
                    score += 1.5
                elif '一般' in cf_check:
                    score += 1
                
                warnings = phase4['data'].get('异常排查', [])
                healthy_count = sum(1 for w in warnings if '✅' in w)
                score += healthy_count * 0.5
        
        # 估值评分
        if 7 in results['phases']:
            phase7 = results['phases'][7]
            if 'data' in phase7:
                moat = phase7['data'].get('护城河评分', {}).get('总分', '0/5')
                moat_score = int(moat.split('/')[0]) if '/' in moat else 0
                if moat_score >= 4:
                    score += 2
                elif moat_score >= 3:
                    score += 1
        
        # 确定评级
        if score >= 4:
            rating = SignalRating.STRONG_BUY
            recommendation = '基本面强劲，值得深入研究'
        elif score >= 2.5:
            rating = SignalRating.HOLD
            recommendation = '基本面尚可，需进一步分析'
        else:
            rating = SignalRating.SELL
            recommendation = '基本面存疑，建议谨慎'
        
        return {
            'rating': rating,
            'score': score,
            'max_score': 5,
            'recommendation': recommendation
        }
    
    def _cite(self, source: str) -> str:
        """生成引用"""
        if self.validator:
            return self.validator.cite(source, '', datetime.now().strftime('%Y-%m-%d'))
        return f"来源: {source}"
    
    def generate_report_markdown(self, results: Dict) -> str:
        """生成 Markdown 报告"""
        display_name = results.get('display_name') or stock_display_name(results.get('symbol', ''), {})
        md = f"""# {display_name}投资尽调报告

**股票名称**: {display_name}  
**股票代码**: {results['symbol']}  
**投资风格**: {results['style']}  
**分析时间**: {results['timestamp']}  

---

## 综合评级

**信号评级**: {results['rating']['rating']}  
**评分**: {results['rating']['score']}/{results['rating']['max_score']}  
**建议**: {results['rating']['recommendation']}  

---

"""
        
        # 添加各阶段分析
        for phase_num in sorted(results['phases'].keys()):
            phase = results['phases'][phase_num]
            md += f"## Phase {phase_num}: {phase.get('name', '未知')}\n\n"
            
            if 'error' in phase:
                md += f"❌ 分析失败: {phase['error']}\n\n"
            else:
                for key, value in phase.get('data', {}).items():
                    if isinstance(value, dict):
                        md += f"### {key}\n\n"
                        md += "| 指标 | 值 |\n|------|------|\n"
                        for k, v in value.items():
                            md += f"| {k} | {v} |\n"
                        md += "\n"
                    elif isinstance(value, list):
                        md += f"### {key}\n\n"
                        for v in value:
                            md += f"- {v}\n"
                        md += "\n"
                    else:
                        md += f"- **{key}**: {value}\n"
                md += "\n"
            
            if phase.get('citation'):
                md += f"> {phase['citation']}\n\n"
        
        # 添加监控清单
        if 'monitoring_checklist' in results:
            md += "---\n\n"
            md += results['monitoring_checklist']
        
        # 免责声明
        md += """
---

## ⚠️ 免责声明

本报告仅供参考，不构成投资建议。所有分析基于公开信息，可能存在滞后或不完整。投资有风险，决策需谨慎。

---

*by Neo9527 Finance Skill v6.6.5*
"""
        
        md = normalize_report_text(md)
        assert_report_quality(md)
        return md
    
    def generate_report(self, symbol: str, output_dir: str = './reports', format: str = 'markdown') -> str:
        """生成分析报告"""
        results = self.analyze(symbol)
        
        os.makedirs(output_dir, exist_ok=True)
        
        if format == 'markdown':
            report_content = self.generate_report_markdown(results)
            report_file = os.path.join(
                output_dir,
                f"STOCK_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
        else:
            report_file = self.generate_report_html(results, output_dir)
            return report_file
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✅ 报告已生成: {report_file}")
        return report_file
    
    def generate_report_html(self, results: Dict, output_dir: str) -> str:
        """生成 HTML 报告"""
        display_name = results.get('display_name') or stock_display_name(results.get('symbol', ''), {})
        conclusion = self._build_conclusion_layers(results)
        basis_items = ''.join(f"<li>{item}</li>" for item in conclusion['关键依据'])
        risk_items = ''.join(f"<li>{item}</li>" for item in conclusion['风险与验证'])
        phase_cards = ''.join(self._phase_summary_card(num, phase) for num, phase in sorted(results.get('phases', {}).items()))
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{display_name} 投资尽调报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 p-8">
    <div class="max-w-5xl mx-auto">
        <h1 class="text-4xl font-bold mb-2">{display_name}</h1>
        <p class="text-slate-400 mb-8">股票投资尽调报告 | {results['timestamp']}</p>
        
        <div class="bg-slate-900 border border-slate-800 rounded-lg p-6 mb-8">
            <div class="text-3xl font-bold mb-2">{results['rating']['rating']}</div>
            <div class="text-slate-300">{results['rating']['recommendation']}</div>
            <div class="text-slate-400 mt-2">评分：{results['rating']['score']}/{results['rating']['max_score']}</div>
        </div>

        <section class="mb-8">
            <h2 class="text-2xl font-bold mb-4">综合结论</h2>
            <div class="bg-slate-900 border border-slate-800 rounded-lg p-6 space-y-5">
                <div>
                    <h3 class="text-lg font-semibold mb-2">一、综合观点</h3>
                    <p class="text-slate-300 leading-7">{conclusion['综合观点']}</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-2">二、关键依据</h3>
                    <ul class="list-disc pl-6 text-slate-300 leading-7">{basis_items}</ul>
                </div>
                <div>
                    <h3 class="text-lg font-semibold mb-2">三、风险与验证</h3>
                    <ul class="list-disc pl-6 text-slate-300 leading-7">{risk_items}</ul>
                </div>
            </div>
        </section>

        <section class="mb-8">
            <h2 class="text-2xl font-bold mb-4">分项小结</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {phase_cards}
            </div>
        </section>

        <div class="bg-slate-900 border border-slate-800 rounded-lg p-5 mb-8">
            <h2 class="text-xl font-bold mb-2">报告小结</h2>
            <p class="text-slate-300 leading-7">本报告先确认公司事实底座，再进入行业周期、业务质量、财务质量、治理结构、市场分歧和估值护城河分析。若关键数据缺失，结论仅保留为待验证判断，不使用模拟数据补齐。</p>
        </div>
        
        <p class="text-slate-500 text-sm mt-8">
            本报告仅供研究参考，不构成投资建议。所有判断依赖公开数据，需结合公告、财报和个人风险承受能力复核。
        </p>
    </div>
</body>
</html>"""
        html = normalize_report_text(html)
        assert_report_quality(html, require_layered_conclusion=True)
        
        report_file = os.path.join(
            output_dir,
            f"STOCK_{results['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return report_file

    def _build_conclusion_layers(self, results: Dict) -> Dict:
        rating = results.get('rating', {})
        phases = results.get('phases', {})
        basis = []
        risks = []

        phase1 = phases.get(1, {}).get('data', {}).get('公司基本信息', {})
        if phase1:
            basis.append(f"公司归属{phase1.get('所属板块', MISSING_TEXT)}板块、{phase1.get('所属行业', MISSING_TEXT)}行业，先以业务事实作为分析起点。")

        phase4 = phases.get(4, {}).get('data', {})
        if phase4:
            cashflow = phase4.get('现金流验证', {}).get('判断', MISSING_TEXT)
            basis.append(f"财务质量重点观察现金流与利润匹配度，当前现金流判断为{cashflow}。")
            warnings = phase4.get('异常排查', [])
            risks.extend(warnings[:2])

        phase7 = phases.get(7, {}).get('data', {})
        if phase7:
            valuation = phase7.get('估值水平', {}).get('判断', MISSING_TEXT)
            moat = phase7.get('护城河评分', {}).get('评级', MISSING_TEXT)
            basis.append(f"估值与护城河共同校验安全边际，当前估值判断为{valuation}，护城河为{moat}。")

        if not basis:
            basis.append("当前公开数据不足，无法形成充分验证的投资结论。")
        if not risks:
            risks.append("需继续验证财报、公告、行业景气度和估值假设，避免单一指标驱动结论。")

        score = rating.get('score', 0)
        max_score = rating.get('max_score', 5)
        recommendation = rating.get('recommendation', '需进一步验证')
        viewpoint = f"综合评分为{score}/{max_score}，当前结论为：{recommendation}。该结论按事实底座、经营质量、财务质量和估值验证逐层形成，数据不足处不做确定性推断。"
        return {'综合观点': viewpoint, '关键依据': basis[:4], '风险与验证': risks[:4]}

    def _phase_summary_card(self, phase_num: int, phase: Dict) -> str:
        name = phase.get('name', '未知阶段')
        if 'error' in phase:
            summary = f"该阶段分析失败：{phase['error']}。"
        else:
            keys = list(phase.get('data', {}).keys())
            summary = '、'.join(keys[:4]) if keys else '该阶段暂无可展示数据'
        return f"""
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-5">
                    <div class="text-sm text-slate-500 mb-1">第{phase_num}阶段</div>
                    <h3 class="text-lg font-semibold mb-2">{name}</h3>
                    <p class="text-slate-300 leading-7">{summary}</p>
                </div>
        """


# 快速使用函数
def analyze_stock(symbol: str, style: str = 'value') -> Dict:
    """快速分析股票"""
    analyzer = StockAnalyzer(style=style)
    return analyzer.analyze(symbol)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("股票投资尽调分析器 v1.1 测试")
    print("=" * 60)
    
    analyzer = StockAnalyzer(style=InvestmentStyle.VALUE)
    results = analyzer.analyze('AAPL', depth='standard')
    
    print(f"\n综合评级: {results['rating']['rating']}")
    print(f"评分: {results['rating']['score']}/{results['rating']['max_score']}")
    print(f"建议: {results['rating']['recommendation']}")
    
    # 测试生成报告
    report_file = analyzer.generate_report('AAPL', output_dir='./outputs/reports')
