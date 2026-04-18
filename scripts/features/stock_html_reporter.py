#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票HTML报告生成器 v1.0
基于模板生成专业的HTML投资分析报告
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class StockHTMLReporter:
    """股票HTML报告生成器"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        self.template_file = self.template_dir / 'stock_report_v1.html'
    
    def generate(self, report: Dict, enhancer=None) -> str:
        """
        生成HTML报告
        
        Args:
            report: 分析报告数据
            enhancer: 报告增强工具
            
        Returns:
            HTML字符串
        """
        # 读取模板
        with open(self.template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 基础信息
        symbol = report['symbol']
        overall = report.get('overall', {})
        score = overall.get('score', 0)
        recommendation = overall.get('recommendation', 'N/A')
        timestamp = report.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        style = report.get('style', 'value')
        
        # 推荐背景色
        if '买入' in recommendation or '强烈' in recommendation:
            rec_bg = '#27ae60'
        elif '持有' in recommendation:
            rec_bg = '#f39c12'
        elif '卖出' in recommendation:
            rec_bg = '#e74c3c'
        else:
            rec_bg = '#1e3c72'
        
        # 生成内容
        content = self._generate_content(report, enhancer)
        
        # 填充模板
        html = template.format(
            symbol=symbol,
            score=f"{score:.1f}",
            recommendation=recommendation,
            decision_bg=rec_bg,
            timestamp=timestamp,
            style=style,
            content=content
        )
        
        return html
    
    def _generate_content(self, report: Dict, enhancer) -> str:
        """生成报告内容"""
        sections = report.get('sections', {})
        html_parts = []
        
        # 第一部分: 基本面分析
        if 'fundamentals' in sections:
            html_parts.append(self._generate_fundamentals_section(sections['fundamentals'], enhancer))
        
        # 第二部分: 估值分析
        if 'valuation' in sections:
            html_parts.append(self._generate_valuation_section(sections['valuation']))
        
        # 第三部分: 财务健康
        if 'financial_check' in sections:
            html_parts.append(self._generate_financial_section(sections['financial_check']))
        
        # 第四部分: 技术分析
        if 'technical' in sections:
            html_parts.append(self._generate_technical_section(sections['technical'], enhancer))
        
        # 第五部分: 市场情绪
        if 'sentiment' in sections:
            html_parts.append(self._generate_sentiment_section(sections['sentiment']))
        
        # 第六部分: 监管风险
        if 'regulation' in sections:
            html_parts.append(self._generate_regulation_section(sections['regulation']))
        
        # 第七部分: 深度研报 (仅当有有效数据时)
        if 'deep_research' in sections:
            dr = sections['deep_research']
            # 检查深度研报是否有效
            if dr.get('rating') and dr.get('score', 0) > 0:
                html_parts.append(self._generate_research_section(dr))
        
        # 第八部分: 全局观点
        html_parts.append(self._generate_overall_section(report, enhancer))
        
        return '\n'.join(html_parts)
    
    def _generate_fundamentals_section(self, fund: Dict, enhancer) -> str:
        """生成基本面分析部分"""
        pe = fund.get('pe')
        pb = fund.get('pb')
        roe = fund.get('roe')
        market_cap = fund.get('market_cap')
        
        # 格式化
        pe_str = f"{pe:.1f}" if pe else "N/A"
        pb_str = f"{pb:.2f}" if pb else "N/A"
        roe_str = f"{roe:.1f}%" if roe else "N/A"
        
        # 使用增强工具
        if enhancer and pe:
            pe_interp = enhancer.interpret_pe(pe)
            pe_status = pe_interp.get('status', 'N/A')
            pe_vs = pe_interp.get('vs_industry', 'N/A')
        else:
            pe_status = 'N/A'
            pe_vs = 'N/A'
        
        if enhancer and roe:
            roe_interp = enhancer.interpret_roe(roe)
            roe_rating = roe_interp.get('rating', 'N/A')
        else:
            roe_rating = 'N/A'
        
        # 市值格式化
        if market_cap:
            if market_cap > 1e12:
                mc_str = f"${market_cap/1e12:.2f}万亿"
            elif market_cap > 1e9:
                mc_str = f"${market_cap/1e9:.2f}亿"
            else:
                mc_str = f"${market_cap/1e6:.2f}百万"
        else:
            mc_str = "N/A"
        
        # 评分计算
        roe_score = min(100, max(0, roe / 2)) if roe else 0
        pe_score = max(0, 100 - pe) if pe else 50
        
        html = f"""
        <!-- 第一部分: 基本面分析 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">1</div>
                <div>
                    <div class="section-title">基本面分析</div>
                    <div class="section-subtitle">投资根基 - 决定长期价值</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">ROE (净资产收益率)</div>
                    <div class="metric-value">{roe_str}</div>
                    <div class="metric-rating">{roe_rating}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">P/E (市盈率)</div>
                    <div class="metric-value">{pe_str}</div>
                    <div class="metric-rating">{pe_status}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">P/B (市净率)</div>
                    <div class="metric-value">{pb_str}</div>
                    <div class="metric-rating">{'低估' if pb and pb < 3 else '合理' if pb and pb < 6 else '偏高'}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">市值</div>
                    <div class="metric-value">{mc_str}</div>
                    <div class="metric-rating">大盘股</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>指标</th>
                        <th>值</th>
                        <th>行业对比</th>
                        <th>评级</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>ROE</td>
                        <td>{roe_str}</td>
                        <td>-</td>
                        <td>{roe_rating}</td>
                    </tr>
                    <tr>
                        <td>P/E</td>
                        <td>{pe_str}</td>
                        <td>{pe_vs}</td>
                        <td>{pe_status}</td>
                    </tr>
                    <tr>
                        <td>P/B</td>
                        <td>{pb_str}</td>
                        <td>-</td>
                        <td>{'低估' if pb and pb < 3 else '合理' if pb and pb < 6 else '偏高'}</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="summary">
                <div class="summary-title">📊 基本面小结</div>
                <div class="summary-content">
                    {'✅ 盈利能力优秀: ROE超过15%，具备优秀盈利能力' if roe and roe > 15 else '⚠️ 盈利能力一般: ROE在10-15%区间' if roe and roe > 10 else '❌ 盈利能力较弱'}
                    <br>
                    {'✅ 估值合理: PE低于20倍' if pe and pe < 20 else '⚠️ 估值偏高: PE在20-30倍区间' if pe and pe < 30 else '❌ 估值过高: PE超过30倍，需注意风险'}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_valuation_section(self, val: Dict) -> str:
        """生成估值分析部分"""
        current = val.get('current_price', 0)
        fair = val.get('fair_value', 0)
        upside = val.get('upside', 0)
        
        if upside > 0:
            val_status = f"低估 {abs(upside):.0f}%"
            val_signal = "买入机会"
            val_class = "success"
        elif upside > -20:
            val_status = "合理区间"
            val_signal = "观望"
            val_class = "warning"
        else:
            val_status = f"高估 {abs(upside):.0f}%"
            val_signal = "风险较大"
            val_class = "danger"
        
        html = f"""
        <!-- 第二部分: 估值分析 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">2</div>
                <div>
                    <div class="section-title">估值分析</div>
                    <div class="section-subtitle">价格评估 - 决定买入时机</div>
                </div>
            </div>
            
            <div class="card {val_class}">
                <table>
                    <thead>
                        <tr>
                            <th>估值指标</th>
                            <th>值</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>当前价格</td>
                            <td>${current:.2f}</td>
                            <td>市场价格</td>
                        </tr>
                        <tr>
                            <td>公允价值</td>
                            <td>${fair:.2f}</td>
                            <td>DCF模型估值</td>
                        </tr>
                        <tr>
                            <td>估值状态</td>
                            <td>{val_status}</td>
                            <td>{val_signal}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="summary">
                    <div class="summary-title">💡 估值信号</div>
                    <div class="summary-content">
                        当前价格 ${current:.2f}，公允价值 ${fair:.2f}，
                        {'存在' + str(abs(upside)) + '%上涨空间，具备投资价值' if upside > 0 else '高估' + str(abs(upside)) + '%，建议谨慎'}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_financial_section(self, fc: Dict) -> str:
        """生成财务健康部分"""
        risk_level = fc.get('risk_level', 'unknown')
        risk_desc = fc.get('risk_description', 'N/A')
        anomaly_count = fc.get('anomaly_count', 0)
        gross_margin = fc.get('gross_margin', 0)
        net_margin = fc.get('net_margin', 0)
        
        if risk_level == 'low':
            risk_class = "success"
        elif risk_level == 'medium':
            risk_class = "warning"
        else:
            risk_class = "danger"
        
        html = f"""
        <!-- 第三部分: 财务健康 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">3</div>
                <div>
                    <div class="section-title">财务健康</div>
                    <div class="section-subtitle">风险检查 - 影响生存能力</div>
                </div>
            </div>
            
            <div class="card {risk_class}">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">风险等级</div>
                        <div class="metric-value">{risk_desc}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">异常数量</div>
                        <div class="metric-value">{anomaly_count}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">毛利率</div>
                        <div class="metric-value">{gross_margin:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">净利率</div>
                        <div class="metric-value">{net_margin:.1f}%</div>
                    </div>
                </div>
                
                <div class="data-source">
                    <strong>数据来源:</strong> 财务报表（利润表/资产负债表）
                </div>
                
                <div class="summary">
                    <div class="summary-title">📊 财务小结</div>
                    <div class="summary-content">
                        {'✅ 财务健康: 无异常信号，盈利质量良好' if risk_level == 'low' and anomaly_count == 0 else '⚠️ 财务风险: ' + str(anomaly_count) + '项异常需关注'}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_technical_section(self, tech: Dict, enhancer) -> str:
        """生成技术分析部分"""
        trend = tech.get('trend', 'N/A')
        rsi = tech.get('rsi', 50)
        macd = tech.get('macd_status', 'N/A')
        
        # RSI解读
        if enhancer:
            rsi_interp = enhancer.interpret_rsi(rsi)
            rsi_status = rsi_interp.get('status', 'N/A')
            rsi_signal = rsi_interp.get('signal', 'N/A')
        else:
            rsi_status = '超买' if rsi > 70 else '超卖' if rsi < 30 else '中性'
            rsi_signal = '卖出' if rsi > 70 else '买入' if rsi < 30 else '观望'
        
        # MACD信号
        macd_signal = '买入' if '金叉' in macd else '卖出' if '死叉' in macd else '观望'
        
        html = f"""
        <!-- 第四部分: 技术分析 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">4</div>
                <div>
                    <div class="section-title">技术分析</div>
                    <div class="section-subtitle">择时参考 - 不改变投资方向</div>
                </div>
            </div>
            
            <div class="card">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">趋势</div>
                        <div class="metric-value">{trend}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">RSI</div>
                        <div class="metric-value">{rsi:.1f}</div>
                        <div class="metric-rating">{rsi_status}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">MACD</div>
                        <div class="metric-value">{macd}</div>
                        <div class="metric-rating">{'看涨' if '金叉' in macd else '看跌' if '死叉' in macd else '中性'}</div>
                    </div>
                </div>
                
                <div class="signal-cards">
                    <div class="signal-card {'bullish' if rsi_signal == '买入' else 'bearish'}">
                        <div class="signal-icon">{'📈' if rsi_signal == '买入' else '📉'}</div>
                        <div class="signal-name">RSI信号</div>
                        <div class="signal-desc">{rsi_status} - {rsi_signal}</div>
                    </div>
                    <div class="signal-card {'bullish' if macd_signal == '买入' else 'bearish'}">
                        <div class="signal-icon">{'📈' if macd_signal == '买入' else '📉'}</div>
                        <div class="signal-name">MACD信号</div>
                        <div class="signal-desc">{macd} - {macd_signal}</div>
                    </div>
                </div>
                
                <div class="summary">
                    <div class="summary-title">📊 技术小结</div>
                    <div class="summary-content">
                        RSI {rsi:.1f}，{rsi_status}。MACD {macd}，提供{'买入' if '金叉' in macd else '卖出' if '死叉' in macd else '中性'}信号。
                        <br><strong>注意:</strong> 技术分析仅作择时参考，投资决策应以基本面为主。
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_sentiment_section(self, sent: Dict) -> str:
        """生成市场情绪部分"""
        status = sent.get('status', 'neutral')
        description = sent.get('description', '中性')
        bullish_pct = sent.get('bullish_pct', 50)
        alignment = sent.get('alignment', 'local')
        alignment_desc = sent.get('alignment_desc', '本地分析')
        
        # 数据来源说明
        source_map = {
            'local': '基于新闻标题的TextBlob情感分析（本地模型）',
            'adanos': 'Adanos多数据源聚合API',
            'news': '新闻情感分析'
        }
        source = source_map.get(alignment, '本地分析')
        
        html = f"""
        <!-- 第五部分: 市场情绪 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">5</div>
                <div>
                    <div class="section-title">市场情绪</div>
                    <div class="section-subtitle">短期风向 - 不改变长期价值</div>
                </div>
            </div>
            
            <div class="card">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">情绪状态</div>
                        <div class="metric-value">{description}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">看涨比例</div>
                        <div class="metric-value">{bullish_pct:.0f}%</div>
                    </div>
                </div>
                
                <div class="data-source">
                    <strong>数据来源:</strong> {source}<br>
                    <strong>判断方法:</strong> {'通过新闻标题关键词分析，使用TextBlob库计算情感极性' if alignment == 'local' else '聚合多个数据源的情绪数据'}
                </div>
                
                <div class="summary">
                    <div class="summary-title">📊 情绪小结</div>
                    <div class="summary-content">
                        当前市场情绪{description}，{'短期可能上涨' if status == 'positive' else '短期可能下跌' if status == 'negative' else '短期震荡为主'}。
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_regulation_section(self, reg: Dict) -> str:
        """生成监管风险部分"""
        risk_score = reg.get('risk_score', 0)
        risk_level = reg.get('risk_level', 'unknown')
        risk_desc = reg.get('risk_description', 'N/A')
        alerts = reg.get('alerts_count', 0)
        
        if risk_level == 'low':
            risk_class = "success"
        elif risk_level == 'medium':
            risk_class = "warning"
        else:
            risk_class = "danger"
        
        html = f"""
        <!-- 第六部分: 监管风险 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">6</div>
                <div>
                    <div class="section-title">监管风险</div>
                    <div class="section-subtitle">政策环境 - 影响行业前景</div>
                </div>
            </div>
            
            <div class="card {risk_class}">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">风险评分</div>
                        <div class="metric-value">{risk_score}/100</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">风险等级</div>
                        <div class="metric-value">{risk_desc}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">监管警报</div>
                        <div class="metric-value">{alerts}条</div>
                    </div>
                </div>
                
                <div class="data-source">
                    <strong>数据来源:</strong> 中国证监会(CSRC)、人民银行(PBOC)、国家金融监督管理总局(NFRA)公开公告<br>
                    <strong>监控方法:</strong> 实时监控三大监管机构官方网站公告、政策文件、处罚决定
                </div>
                
                <div class="summary">
                    <div class="summary-title">📊 监管小结</div>
                    <div class="summary-content">
                        {risk_desc}，{'可正常投资' if risk_level == 'low' else '建议关注政策动态'}。
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_research_section(self, dr: Dict) -> str:
        """生成深度研报部分"""
        rating = dr.get('rating', 'N/A')
        score = dr.get('score', 0)
        recommendation = dr.get('recommendation', 'N/A')
        
        # 评级解读
        rating_desc = {
            '🟢🟢🟢🟢🟢': '强烈推荐',
            '🟢🟢🟢🟢': '推荐',
            '🟡🟡🟡': '中性',
            '🔴🔴': '谨慎',
            '🔴🔴🔴': '不推荐'
        }.get(rating, '待评估')
        
        html = f"""
        <!-- 第七部分: 深度研报 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">7</div>
                <div>
                    <div class="section-title">深度研报</div>
                    <div class="section-subtitle">综合研判 - 提供深度见解</div>
                </div>
            </div>
            
            <div class="card">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">评级</div>
                        <div class="metric-value" style="font-size: 32px;">{rating}</div>
                        <div class="metric-rating">{rating_desc}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">评分</div>
                        <div class="metric-value">{score}/5</div>
                        <div class="metric-rating">{'优秀' if score >= 4 else '良好' if score >= 3 else '一般'}</div>
                    </div>
                </div>
                
                <div class="summary">
                    <div class="summary-title">📊 研报小结</div>
                    <div class="summary-content">{recommendation}</div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_overall_section(self, report: Dict, enhancer) -> str:
        """生成全局观点部分"""
        overall = report.get('overall', {})
        score = overall.get('score', 0)
        sections = report.get('sections', {})
        
        # 综合评价
        if score >= 70:
            overall_view = "基本面优秀，估值合理，财务健康，技术面支持，适合投资"
        elif score >= 50:
            overall_view = "基本面尚可，但存在估值或风险问题，需谨慎投资"
        else:
            overall_view = "基本面较弱或估值过高，风险较大，建议观望"
        
        # 不同周期建议
        if enhancer:
            short = enhancer.get_investment_advice(score, 'short', sections)
            medium = enhancer.get_investment_advice(score, 'medium', sections)
            long = enhancer.get_investment_advice(score, 'long', sections)
        else:
            short = {'advice': '观望', 'reason': '技术面不确定', 'action': '等待'}
            medium = {'advice': '谨慎', 'reason': '需进一步分析', 'action': '观望'}
            long = {'advice': '持有', 'reason': '基本面尚可', 'action': '持有'}
        
        html = f"""
        <!-- 第八部分: 全局观点 -->
        <div class="section">
            <div class="section-header">
                <div class="section-number">8</div>
                <div>
                    <div class="section-title">全局观点</div>
                    <div class="section-subtitle">最终建议 - 综合各维度分析</div>
                </div>
            </div>
            
            <div class="card">
                <div class="summary">
                    <div class="summary-title">📊 综合评价</div>
                    <div class="summary-content">{overall_view}</div>
                </div>
                
                <h3 style="margin: 30px 0 20px 0; color: #2c3e50;">💡 不同周期投资者建议</h3>
                
                <div class="advice-cards">
                    <div class="advice-card short">
                        <div class="advice-label">短线投资者</div>
                        <div class="advice-value">{short['advice']}</div>
                        <div class="advice-reason">{short['reason']}</div>
                        <div class="advice-action">{short['action']}</div>
                    </div>
                    <div class="advice-card medium">
                        <div class="advice-label">波段投资者</div>
                        <div class="advice-value">{medium['advice']}</div>
                        <div class="advice-reason">{medium['reason']}</div>
                        <div class="advice-action">{medium['action']}</div>
                    </div>
                    <div class="advice-card long">
                        <div class="advice-label">长线投资者</div>
                        <div class="advice-value">{long['advice']}</div>
                        <div class="advice-reason">{long['reason']}</div>
                        <div class="advice-action">{long['action']}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 风险提示 -->
        <div class="risk-warning">
            <h3>⚠️ 风险提示</h3>
            <p>本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
            <p>报告中的分析基于公开数据，可能存在滞后性或不完整性。投资者应结合自身情况独立判断。</p>
        </div>
        """
        
        return html


# 便捷函数
def generate_html_report(report: Dict, enhancer=None) -> str:
    """生成HTML报告"""
    reporter = StockHTMLReporter()
    return reporter.generate(report, enhancer)


if __name__ == '__main__':
    print("股票HTML报告生成器 v1.0")
    print("使用方法: from stock_html_reporter import generate_html_report")
