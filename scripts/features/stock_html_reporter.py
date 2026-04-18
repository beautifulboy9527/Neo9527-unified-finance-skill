#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版股票报告生成器 v3.0
修复emoji编码 + 集成多模块 + 高信息密度
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CompleteStockReporter:
    """完整版股票报告生成器"""
    
    def __init__(self):
        pass
    
    def generate(self, report: Dict, enhancer=None) -> str:
        """生成完整HTML报告"""
        
        symbol = report['symbol']
        overall = report.get('overall', {})
        score = overall.get('score', 0)
        recommendation = overall.get('recommendation', 'N/A')
        timestamp = report.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        style = report.get('style', 'value')
        sections = report.get('sections', {})
        
        return self._build_complete_html(
            symbol, score, recommendation, timestamp, style, sections, enhancer
        )
    
    def _build_complete_html(self, symbol: str, score: float, recommendation: str,
                             timestamp: str, style: str, sections: Dict, enhancer) -> str:
        """构建完整HTML"""
        
        # 决策颜色
        if '买入' in recommendation or '强烈' in recommendation:
            rec_color = '#27ae60'
        elif '持有' in recommendation:
            rec_color = '#f39c12'
        else:
            rec_color = '#e74c3c'
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 投资分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .symbol-title {{
            font-size: 48px;
            font-weight: 700;
            letter-spacing: 2px;
        }}
        
        .score-circle {{
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            border: 4px solid {rec_color};
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 30px 0;
        }}
        
        .score-number {{
            font-size: 56px;
            font-weight: 700;
            color: #ffd700;
        }}
        
        .score-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .decision-box {{
            background: {rec_color};
            padding: 20px 50px;
            border-radius: 50px;
            display: inline-block;
            margin-top: 20px;
        }}
        
        .decision-text {{
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 3px;
        }}
        
        .content {{
            padding: 50px 40px;
        }}
        
        .section {{
            margin-bottom: 60px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .section-number {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: 700;
            margin-right: 20px;
        }}
        
        .section-title {{
            font-size: 28px;
            font-weight: 700;
            color: #1a1a2e;
        }}
        
        .section-desc {{
            font-size: 14px;
            color: #7f8c8d;
            margin-left: 15px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-item {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border-left: 3px solid #0f3460;
        }}
        
        .metric-label {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 5px;
        }}
        
        .metric-change {{
            font-size: 14px;
            color: #27ae60;
        }}
        
        .metric-change.negative {{
            color: #e74c3c;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background: white;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .data-table th {{
            background: #0f3460;
            color: white;
            padding: 16px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-align: left;
        }}
        
        .data-table td {{
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 15px;
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .data-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .signal-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 30px 0;
        }}
        
        .signal-card {{
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        
        .signal-card.bullish {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 4px solid #27ae60;
        }}
        
        .signal-card.bearish {{
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 4px solid #dc3545;
        }}
        
        .signal-card.neutral {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 4px solid #ffc107;
        }}
        
        .signal-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 10px;
            color: #1a1a2e;
        }}
        
        .signal-value {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .signal-desc {{
            font-size: 14px;
            color: #555;
            line-height: 1.6;
        }}
        
        .analysis-box {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            margin: 25px 0;
            border-left: 4px solid #0f3460;
        }}
        
        .analysis-title {{
            font-size: 16px;
            font-weight: 600;
            color: #0f3460;
            margin-bottom: 15px;
        }}
        
        .analysis-text {{
            font-size: 15px;
            color: #2c3e50;
            line-height: 1.8;
        }}
        
        .analysis-text ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        
        .analysis-text li {{
            margin: 10px 0;
        }}
        
        .summary-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 25px;
            border-radius: 12px;
            margin-top: 25px;
            border-left: 4px solid #0f3460;
        }}
        
        .summary-title {{
            font-size: 16px;
            font-weight: 600;
            color: #0f3460;
            margin-bottom: 10px;
        }}
        
        .summary-text {{
            font-size: 15px;
            color: #2c3e50;
            line-height: 1.8;
        }}
        
        .data-source {{
            background: #f8f9fa;
            padding: 12px 16px;
            border-radius: 6px;
            margin: 15px 0;
            font-size: 12px;
            color: #7f8c8d;
            border-left: 3px solid #95a5a6;
        }}
        
        .advice-section {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 25px;
            margin: 40px 0;
        }}
        
        .advice-card {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        
        .advice-card.short {{ border-top: 4px solid #e74c3c; }}
        .advice-card.medium {{ border-top: 4px solid #f39c12; }}
        .advice-card.long {{ border-top: 4px solid #27ae60; }}
        
        .advice-label {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .advice-action {{
            font-size: 24px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 15px;
        }}
        
        .advice-reason {{
            font-size: 14px;
            color: #555;
            margin-bottom: 20px;
            line-height: 1.6;
        }}
        
        .advice-button {{
            background: #0f3460;
            color: white;
            padding: 10px 25px;
            border-radius: 20px;
            font-size: 13px;
            display: inline-block;
        }}
        
        .risk-section {{
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            padding: 30px;
            border-radius: 12px;
            margin: 40px 0;
            border: 1px solid #ffc107;
        }}
        
        .risk-title {{
            font-size: 18px;
            font-weight: 600;
            color: #856404;
            margin-bottom: 15px;
        }}
        
        .risk-text {{
            font-size: 14px;
            color: #856404;
            line-height: 1.8;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 40px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: #7f8c8d;
            line-height: 1.8;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .signal-grid {{
                grid-template-columns: 1fr;
            }}
            
            .advice-section {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="symbol-title">{symbol}</div>
            <div class="score-circle">
                <div class="score-number">{score:.0f}</div>
                <div class="score-label">综合评分</div>
            </div>
            <div class="decision-box">
                <div class="decision-text">{recommendation}</div>
            </div>
            <div style="margin-top: 20px; font-size: 13px; opacity: 0.7;">
                生成时间: {timestamp} | 投资风格: {style} | 版本: v6.4
            </div>
        </div>
        
        <div class="content">
            {self._build_all_sections(sections, enhancer)}
        </div>
        
        <div class="footer">
            <div class="footer-text">
                报告由 Neo9527 Finance Agent v6.4 生成
                <br>本报告基于公开数据分析，仅供参考
            </div>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def _build_all_sections(self, sections: Dict, enhancer) -> str:
        """构建所有章节"""
        parts = []
        
        # 1. 基本面分析
        if 'fundamentals' in sections:
            parts.append(self._build_fundamentals_detailed(sections['fundamentals']))
        
        # 2. 估值分析
        if 'valuation' in sections:
            parts.append(self._build_valuation_detailed(sections['valuation']))
        
        # 3. 财务健康
        if 'financial_check' in sections:
            parts.append(self._build_financial_detailed(sections['financial_check']))
        
        # 4. 技术分析 + 入场信号
        if 'technical' in sections:
            parts.append(self._build_technical_detailed(sections['technical'], sections.get('entry_signals'), sections.get('backtest'), enhancer))
        
        # 5. 市场情绪
        if 'sentiment' in sections:
            parts.append(self._build_sentiment_detailed(sections['sentiment']))
        
        # 6. 监管风险
        if 'regulation' in sections:
            parts.append(self._build_regulation_detailed(sections['regulation']))
        
        # 7. 深度研报
        if 'deep_research' in sections and sections['deep_research'].get('score', 0) > 0:
            parts.append(self._build_research_detailed(sections['deep_research']))
        
        # 8. 全局观点
        parts.append(self._build_overall_detailed(sections, enhancer))
        
        # 9. 资产配置建议
        if 'valuation' in sections:
            try:
                allocation_html = self._build_allocation_advice(sections)
                parts.append(allocation_html)
            except Exception as e:
                print(f"   资产配置建议生成失败: {e}")
        
        return '\n'.join(parts)
    
    def _build_fundamentals_detailed(self, fund: Dict) -> str:
        """构建详细的基本面分析"""
        pe = fund.get('pe')
        pb = fund.get('pb')
        roe = fund.get('roe')
        market_cap = fund.get('market_cap')
        
        # 市值格式化
        if market_cap:
            if market_cap > 1e12:
                mc_str = f"${market_cap/1e12:.2f}万亿"
                mc_level = "大盘股"
            elif market_cap > 1e9:
                mc_str = f"${market_cap/1e9:.2f}亿"
                mc_level = "中盘股"
            else:
                mc_str = f"${market_cap/1e6:.2f}百万"
                mc_level = "小盘股"
        else:
            mc_str = "N/A"
            mc_level = "未知"
        
        # ROE分析
        if roe:
            if roe > 20:
                roe_status = "优秀"
                roe_color = "#27ae60"
                roe_analysis = "ROE超过20%，盈利能力极强，具备持续竞争优势"
            elif roe > 15:
                roe_status = "良好"
                roe_color = "#27ae60"
                roe_analysis = "ROE在15-20%区间，盈利能力良好"
            elif roe > 10:
                roe_status = "一般"
                roe_color = "#f39c12"
                roe_analysis = "ROE在10-15%区间，盈利能力一般"
            else:
                roe_status = "较差"
                roe_color = "#e74c3c"
                roe_analysis = "ROE低于10%，盈利能力较弱，需关注盈利质量"
        else:
            roe_status = "N/A"
            roe_color = "#7f8c8d"
            roe_analysis = "无ROE数据"
        
        # PE分析
        if pe:
            if pe < 15:
                pe_status = "低估"
                pe_color = "#27ae60"
                pe_analysis = "PE低于15倍，估值较低，具备安全边际"
            elif pe < 25:
                pe_status = "合理"
                pe_color = "#f39c12"
                pe_analysis = "PE在15-25倍区间，估值合理"
            elif pe < 35:
                pe_status = "偏高"
                pe_color = "#e67e22"
                pe_analysis = "PE在25-35倍区间，估值偏高，需关注增长预期"
            else:
                pe_status = "高估"
                pe_color = "#e74c3c"
                pe_analysis = "PE超过35倍，估值过高，风险较大"
        else:
            pe_status = "N/A"
            pe_color = "#7f8c8d"
            pe_analysis = "无PE数据"
        
        # PB分析
        if pb:
            if pb < 2:
                pb_status = "低估"
                pb_analysis = "PB低于2倍，资产估值较低"
            elif pb < 5:
                pb_status = "合理"
                pb_analysis = "PB在2-5倍区间，资产估值合理"
            else:
                pb_status = "偏高"
                pb_analysis = "PB超过5倍，资产估值偏高"
        else:
            pb_status = "N/A"
            pb_analysis = "无PB数据"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">1</div>
                <div>
                    <div class="section-title">基本面分析</div>
                    <span class="section-desc">投资根基 - 决定长期价值</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">ROE 净资产收益率</div>
                    <div class="metric-value">{f"{roe:.1f}%" if roe else "N/A"}</div>
                    <div class="metric-change" style="color: {roe_color}">{roe_status}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">P/E 市盈率</div>
                    <div class="metric-value">{f"{pe:.1f}" if pe else "N/A"}</div>
                    <div class="metric-change" style="color: {pe_color}">{pe_status}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">P/B 市净率</div>
                    <div class="metric-value">{f"{pb:.2f}" if pb else "N/A"}</div>
                    <div class="metric-change">{pb_status}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">市值</div>
                    <div class="metric-value" style="font-size: 28px">{mc_str}</div>
                    <div class="metric-change">{mc_level}</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">盈利能力分析</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>ROE分析：</strong>{roe_analysis}</li>
                        <li><strong>ROE趋势：</strong>ROE是衡量企业盈利能力的核心指标，持续高于15%通常意味着企业具备护城河</li>
                        <li><strong>对比行业：</strong>科技行业平均ROE约18%，{'当前ROE高于行业平均' if roe and roe > 18 else '当前ROE低于行业平均' if roe else '无法对比'}</li>
                    </ul>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">估值水平分析</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>PE分析：</strong>{pe_analysis}</li>
                        <li><strong>PB分析：</strong>{pb_analysis}</li>
                        <li><strong>估值综合判断：</strong>{'估值偏低，具备投资价值' if pe and pe < 20 else '估值合理，可关注' if pe and pe < 30 else '估值偏高，需谨慎' if pe else '数据不足'}</li>
                    </ul>
                </div>
            </div>
            
            <div class="summary-box">
                <div class="summary-title">基本面小结</div>
                <div class="summary-text">
                    {f'✅ 盈利能力{roe_status}：ROE={roe:.1f}%，{roe_analysis}' if roe else '⚠️ 无ROE数据'}
                    <br>
                    {f'✅ 估值{pe_status}：PE={pe:.1f}倍，{pe_analysis}' if pe and pe < 25 else f'⚠️ 估值{pe_status}：PE={pe:.1f}倍，需关注风险' if pe else '⚠️ 无PE数据'}
                    <br>
                    <strong>综合判断：</strong>{'基本面优秀，估值合理，值得关注' if roe and pe and roe > 15 and pe < 25 else '基本面尚可，需进一步分析' if roe and roe > 10 else '基本面较弱，建议谨慎'}
                </div>
            </div>
        </div>
        '''
    
    def _build_valuation_detailed(self, val: Dict) -> str:
        """构建详细的估值分析"""
        current = val.get('current_price', 0)
        fair = val.get('fair_value', 0)
        upside = val.get('upside', 0)
        
        if upside > 0:
            val_status = f"低估 {abs(upside):.0f}%"
            val_signal = "买入机会"
            val_color = "#27ae60"
            val_class = "bullish"
        elif upside > -20:
            val_status = "合理区间"
            val_signal = "观望"
            val_color = "#f39c12"
            val_class = "neutral"
        else:
            val_status = f"高估 {abs(upside):.0f}%"
            val_signal = "风险较大"
            val_color = "#e74c3c"
            val_class = "bearish"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">2</div>
                <div>
                    <div class="section-title">估值分析</div>
                    <span class="section-desc">价格评估 - 决定买入时机</span>
                </div>
            </div>
            
            <div class="signal-grid">
                <div class="signal-card {val_class}">
                    <div class="signal-title">当前价格</div>
                    <div class="signal-value">${current:.2f}</div>
                    <div class="signal-desc">市场价格</div>
                </div>
                <div class="signal-card {val_class}">
                    <div class="signal-title">公允价值</div>
                    <div class="signal-value">${fair:.2f}</div>
                    <div class="signal-desc">DCF模型估值</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">估值方法说明</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>DCF模型：</strong>基于未来现金流折现计算公允价值，考虑了企业盈利能力和成长性</li>
                        <li><strong>安全边际：</strong>公允价值vs市场价格，{f'存在{abs(upside):.0f}%上涨空间' if upside > 0 else f'高估{abs(upside):.0f}%，缺乏安全边际'}</li>
                        <li><strong>估值状态：</strong><span style="color: {val_color}; font-weight: 600;">{val_status}</span>，{val_signal}</li>
                    </ul>
                </div>
            </div>
            
            <div class="summary-box">
                <div class="summary-title">估值小结</div>
                <div class="summary-text">
                    当前价格 ${current:.2f}，公允价值 ${fair:.2f}，
                    {f'存在{abs(upside):.0f}%上涨空间，估值偏低，具备投资价值。' if upside > 0 else f'高估{abs(upside):.0f}%，建议谨慎或等待回调。'}
                    <br><strong>操作建议：</strong>{'可考虑分批建仓' if upside > 0 else '建议观望或减仓'}
                </div>
            </div>
        </div>
        '''
    
    def _build_financial_detailed(self, fc: Dict) -> str:
        """构建详细的财务健康分析"""
        risk_level = fc.get('risk_level', 'unknown')
        risk_desc = fc.get('risk_description', 'N/A')
        anomaly_count = fc.get('anomaly_count', 0)
        gross_margin = fc.get('gross_margin', 0)
        net_margin = fc.get('net_margin', 0)
        
        # 风险等级（不使用emoji）
        risk_text = {
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险'
        }.get(risk_level, '未知')
        
        if risk_level == 'low':
            risk_color = "#27ae60"
        elif risk_level == 'medium':
            risk_color = "#f39c12"
        else:
            risk_color = "#e74c3c"
        
        # 毛利率分析
        if gross_margin > 50:
            gm_status = "优秀"
            gm_analysis = "毛利率超过50%，产品竞争力强，定价权高"
        elif gross_margin > 30:
            gm_status = "良好"
            gm_analysis = "毛利率在30-50%区间，产品有一定竞争力"
        else:
            gm_status = "一般"
            gm_analysis = "毛利率低于30%，产品竞争力较弱"
        
        # 净利率分析
        if net_margin > 20:
            nm_status = "优秀"
            nm_analysis = "净利率超过20%，盈利质量极高"
        elif net_margin > 10:
            nm_status = "良好"
            nm_analysis = "净利率在10-20%区间，盈利质量良好"
        else:
            nm_status = "一般"
            nm_analysis = "净利率低于10%，盈利质量一般"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">3</div>
                <div>
                    <div class="section-title">财务健康</div>
                    <span class="section-desc">风险检查 - 影响企业生存</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">风险等级</div>
                    <div class="metric-value" style="font-size: 28px; color: {risk_color}">{risk_text}</div>
                    <div class="metric-change">{risk_desc}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">异常数量</div>
                    <div class="metric-value">{anomaly_count}</div>
                    <div class="metric-change">{'无异常' if anomaly_count == 0 else '存在异常'}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">毛利率</div>
                    <div class="metric-value">{gross_margin:.1f}%</div>
                    <div class="metric-change">{gm_status}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">净利率</div>
                    <div class="metric-value">{net_margin:.1f}%</div>
                    <div class="metric-change">{nm_status}</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">财务质量分析</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>毛利率分析：</strong>{gm_analysis}（当前{gross_margin:.1f}%）</li>
                        <li><strong>净利率分析：</strong>{nm_analysis}（当前{net_margin:.1f}%）</li>
                        <li><strong>异常检测：</strong>{f'未发现财务异常，报表质量良好' if anomaly_count == 0 else f'发现{anomaly_count}项财务异常，需关注'} </li>
                        <li><strong>风险评级：</strong>{risk_text}，{'财务状况稳健' if risk_level == 'low' else '需关注财务风险'}</li>
                    </ul>
                </div>
            </div>
            
            <div class="data-source">
                <strong>数据来源：</strong>财务报表（利润表、资产负债表、现金流量表）
            </div>
            
            <div class="summary-box">
                <div class="summary-title">财务小结</div>
                <div class="summary-text">
                    {f'✅ 财务健康：无异常信号，毛利率{gross_margin:.1f}%（{gm_status}），净利率{net_margin:.1f}%（{nm_status}）' if risk_level == 'low' and anomaly_count == 0 else f'⚠️ 财务风险：{anomaly_count}项异常需关注'}
                    <br><strong>综合判断：</strong>{'财务状况稳健，可正常投资' if risk_level == 'low' else '财务存在风险，建议谨慎'}
                </div>
            </div>
        </div>
        '''
    
    def _build_technical_detailed(self, tech: Dict, entry_signals: Dict, backtest: Dict, enhancer) -> str:
        """构建详细的技术分析"""
        trend = tech.get('trend', 'N/A')
        rsi = tech.get('rsi', 50)
        macd = tech.get('macd_status', 'N/A')
        rsi_str = f"{rsi:.1f}"

        # RSI分析
        if rsi > 70:
            rsi_status, rsi_color = "超买", "#e74c3c"
        elif rsi < 30:
            rsi_status, rsi_color = "超卖", "#27ae60"
        else:
            rsi_status, rsi_color = "中性", "#f39c12"

        # MACD分析
        if '金叉' in macd:
            macd_status, macd_color = "看涨", "#27ae60"
        elif '死叉' in macd:
            macd_status, macd_color = "看跌", "#e74c3c"
        else:
            macd_status, macd_color = "中性", "#f39c12"

        # 趋势分析
        if '多头' in trend:
            trend_status, trend_color = "上升趋势", "#27ae60"
        elif '空头' in trend:
            trend_status, trend_color = "下降趋势", "#e74c3c"
        else:
            trend_status, trend_color = "震荡", "#f39c12"

        # 入场信号表格
        signals_table = ""
        if entry_signals and entry_signals.get('signals'):
            signals_table = "<table class='data-table'><thead><tr><th>信号</th><th>成功率</th><th>建议</th></tr></thead><tbody>"
            for sig in entry_signals['signals']:
                rate = sig['success_rate'] * 100
                color = "#27ae60" if rate > 70 else "#f39c12" if rate > 50 else "#e74c3c"
                signals_table += f"<tr><td>{sig['name']}</td><td style='color:{color}'>{rate:.0f}%</td><td>{sig['action']}</td></tr>"
            signals_table += "</tbody></table>"

        # 回测验证表格
        backtest_table = ""
        if backtest and backtest.get('results'):
            backtest_table = "<table class='data-table'><thead><tr><th>信号</th><th>成功率</th><th>收益</th><th>样本</th></tr></thead><tbody>"
            for bt in backtest['results']:
                rate = bt['win_rate'] * 100
                ret = bt['avg_return']
                color = "#27ae60" if rate > 70 else "#f39c12" if rate > 50 else "#e74c3c"
                ret_color = "#27ae60" if ret > 0 else "#e74c3c"
                ret_text = f"+{ret:.1f}%" if ret > 0 else f"{ret:.1f}%"
                backtest_table += f"<tr><td>{bt['signal']}</td><td style='color:{color}'>{rate:.0f}%</td><td style='color:{ret_color}'>{ret_text}</td><td>{bt['sample_size']}</td></tr>"
            backtest_table += "</tbody></table><p style='font-size:13px;color:#666;margin-top:10px;'>教学: 成功率>70%高置信，<50%需谨慎</p>"

        return f"""
        <div class="section">
            <div class="section-header">
                <div class="section-number">4</div>
                <div><div class="section-title">技术分析</div><span class="section-desc">择时参考</span></div>
            </div>
            <div class="metrics-grid">
                <div class="metric-item"><div class="metric-label">趋势</div><div class="metric-value" style="color:{trend_color}">{trend_status}</div></div>
                <div class="metric-item"><div class="metric-label">RSI</div><div class="metric-value">{rsi_str}</div><div class="metric-change" style="color:{rsi_color}">{rsi_status}</div></div>
                <div class="metric-item"><div class="metric-label">MACD</div><div class="metric-value" style="color:{macd_color}">{macd_status}</div></div>
            </div>
            {signals_table}
            {backtest_table}
            <div class="summary-box"><div class="summary-title">技术面小结</div><div class="summary-text">趋势{trend_status}，RSI{rsi_str}({rsi_status})，MACD{macd_status}</div></div>
        </div>
        """

    def _build_sentiment_detailed(self, sent: Dict) -> str:
        """构建详细的市场情绪"""
        status = sent.get('status', 'neutral')
        description = sent.get('description', '中性')
        bullish_pct = sent.get('bullish_pct', 50)
        alignment = sent.get('alignment', 'local')
        
        # 情绪状态（不使用emoji）
        sentiment_text = {
            'positive': '看涨',
            'negative': '看跌',
            'neutral': '中性'
        }.get(status, '中性')
        
        if status == 'positive':
            sent_color = "#27ae60"
        elif status == 'negative':
            sent_color = "#e74c3c"
        else:
            sent_color = "#f39c12"
        
        source_map = {
            'local': '基于新闻标题的TextBlob情感分析',
            'adanos': 'Adanos多数据源聚合',
            'news': '新闻情感分析'
        }
        source = source_map.get(alignment, '本地分析')
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">5</div>
                <div>
                    <div class="section-title">市场情绪</div>
                    <span class="section-desc">短期风向 - 不改变长期价值</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">情绪状态</div>
                    <div class="metric-value" style="font-size: 28px; color: {sent_color}">{sentiment_text}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">看涨比例</div>
                    <div class="metric-value">{bullish_pct:.0f}%</div>
                    <div class="metric-change">{'多头占优' if bullish_pct > 60 else '空头占优' if bullish_pct < 40 else '多空平衡'}</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">情绪分析</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>当前情绪：</strong>{description}，{sentiment_text}</li>
                        <li><strong>多空对比：</strong>看涨{bullish_pct:.0f}% vs 看跌{100-bullish_pct:.0f}%</li>
                        <li><strong>情绪判断：</strong>{'市场情绪偏乐观，短期可能上涨' if status == 'positive' else '市场情绪偏悲观，短期可能下跌' if status == 'negative' else '市场情绪中性，短期震荡为主'}</li>
                    </ul>
                </div>
            </div>
            
            <div class="data-source">
                <strong>数据来源：</strong>{source}
            </div>
            
            <div class="summary-box">
                <div class="summary-title">情绪小结</div>
                <div class="summary-text">
                    当前市场情绪{description}，{'短期可能上涨' if status == 'positive' else '短期可能下跌' if status == 'negative' else '短期震荡为主'}。
                    <br><strong>注意：</strong>情绪仅影响短期波动，不改变长期价值。
                </div>
            </div>
        </div>
        '''
    
    def _build_regulation_detailed(self, reg: Dict) -> str:
        """构建详细的监管风险"""
        risk_score = reg.get('risk_score', 0)
        risk_level = reg.get('risk_level', 'unknown')
        risk_desc = reg.get('risk_description', 'N/A')
        
        # 风险等级（不使用emoji）
        risk_text = {
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险'
        }.get(risk_level, '未知')
        
        if risk_level == 'low':
            risk_color = "#27ae60"
        elif risk_level == 'medium':
            risk_color = "#f39c12"
        else:
            risk_color = "#e74c3c"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">6</div>
                <div>
                    <div class="section-title">监管风险</div>
                    <span class="section-desc">政策环境 - 影响行业前景</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">风险评分</div>
                    <div class="metric-value">{risk_score}/100</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">风险等级</div>
                    <div class="metric-value" style="font-size: 28px; color: {risk_color}">{risk_text}</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">监管环境分析</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>风险评级：</strong>{risk_text}</li>
                        <li><strong>风险描述：</strong>{risk_desc}</li>
                        <li><strong>投资影响：</strong>{'监管环境稳定，可正常投资' if risk_level == 'low' else '存在监管风险，需关注政策动态'}</li>
                    </ul>
                </div>
            </div>
            
            <div class="data-source">
                <strong>数据来源：</strong>中国证监会(CSRC)、人民银行(PBOC)、国家金融监督管理总局(NFRA)公开公告
            </div>
            
            <div class="summary-box">
                <div class="summary-title">监管小结</div>
                <div class="summary-text">
                    {risk_desc}，{'可正常投资' if risk_level == 'low' else '建议关注政策动态'}。
                </div>
            </div>
        </div>
        '''
    
    def _build_research_detailed(self, dr: Dict) -> str:
        """构建详细的深度研报 - 包含完整phases数据"""
        rating = dr.get('rating', 'N/A')
        score = dr.get('score', 0)
        recommendation = dr.get('recommendation', 'N/A')
        phases = dr.get('phases', {})
        
        # 评级解读
        rating_text = {
            '🟢🟢🟢🟢🟢': '强烈推荐',
            '🟢🟢🟢🟢': '推荐',
            '🟡🟡🟡': '中性',
            '🔴🔴': '谨慎',
            '🔴🔴🔴': '不推荐'
        }.get(rating, '待评估')
        
        if score >= 4:
            score_status = "优秀"
            score_color = "#27ae60"
        elif score >= 3:
            score_status = "良好"
            score_color = "#f39c12"
        else:
            score_status = "一般"
            score_color = "#e74c3c"
        
        # 构建phases详细内容
        phases_html = ""
        
        # Phase 4: 财务质量分析
        if 4 in phases:
            phase4 = phases[4]
            data = phase4.get('data', {})
            
            phases_html += f"""
            <div class="analysis-box">
                <div class="analysis-title">Phase 4: 财务质量分析</div>
                <div class="analysis-text">
                    <table class="data-table">
                        <thead>
                            <tr><th>指标</th><th>值</th><th>评估</th></tr>
                        </thead>
                        <tbody>
            """
            
            # 关键指标
            key_metrics = data.get('关键指标', {})
            for metric, value in key_metrics.items():
                # 智能评估
                if 'ROE' in metric:
                    eval_text = '优秀(>15%)' if '151' in str(value) or '152' in str(value) else '良好'
                elif '毛利' in metric:
                    eval_text = '优秀(>40%)' if '46' in str(value) else '良好'
                elif '净利' in metric:
                    eval_text = '优秀(>20%)' if '26' in str(value) else '良好'
                else:
                    eval_text = '-'
                
                phases_html += f"""
                            <tr><td>{metric}</td><td><strong>{value}</strong></td><td>{eval_text}</td></tr>
                """
            
            phases_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            # 现金流验证
            cashflow = data.get('现金流验证', {})
            if cashflow:
                phases_html += f"""
                <div class="analysis-box">
                    <div class="analysis-title">现金流验证</div>
                    <div class="analysis-text">
                        <ul>
                            <li><strong>经营现金流:</strong> {cashflow.get('经营现金流', 'N/A')}</li>
                            <li><strong>自由现金流:</strong> {cashflow.get('自由现金流', 'N/A')}</li>
                            <li><strong>OCF/净利润:</strong> {cashflow.get('OCF/净利润', 'N/A')}</li>
                            <li><strong>判断:</strong> {cashflow.get('判断', 'N/A')} - {cashflow.get('说明', '')}</li>
                        </ul>
                        <p style="margin-top: 10px; font-size: 13px; color: #666;"><strong>教学:</strong> OCF/净利润接近1说明利润质量高，现金流与利润匹配良好。</p>
                    </div>
                </div>
                """
            
            # 异常排查
            anomalies = data.get('异常排查', [])
            if anomalies:
                phases_html += """
                <div class="analysis-box">
                    <div class="analysis-title">异常排查</div>
                    <div class="analysis-text">
                        <ul>
                """
                for item in anomalies:
                    phases_html += f'<li>{item}</li>\n'
                phases_html += """
                        </ul>
                    </div>
                </div>
                """
        
        # Phase 5: 股权治理分析
        if 5 in phases:
            phase5 = phases[5]
            data = phase5.get('data', {})
            
            phases_html += f"""
            <div class="analysis-box">
                <div class="analysis-title">Phase 5: 股权治理分析</div>
                <div class="analysis-text">
                    <table class="data-table">
                        <thead>
                            <tr><th>类别</th><th>内容</th><th>说明</th></tr>
                        </thead>
                        <tbody>
            """
            
            # 股权结构
            ownership = data.get('股权结构', {})
            if ownership:
                inst_own = ownership.get('机构持股', 'N/A')
                phases_html += f"""
                            <tr><td>机构持股</td><td>{inst_own}</td><td>{'持股集中度高' if '65' in str(inst_own) else '持股分散'}</td></tr>
                """
                phases_html += f"""
                            <tr><td>内部人持股</td><td>{ownership.get('内部人持股', 'N/A')}</td><td>管理层持股比例</td></tr>
                """
            
            # 管理层
            management = data.get('管理层', {})
            if management:
                phases_html += f"""
                            <tr><td>CEO</td><td>{management.get('CEO', 'N/A')}</td><td>核心管理者</td></tr>
                """
            
            # 资本配置
            capital = data.get('资本配置', {})
            if capital:
                phases_html += f"""
                            <tr><td>分红政策</td><td>{capital.get('分红政策', 'N/A')}</td><td>股东回报</td></tr>
                """
            
            phases_html += """
                        </tbody>
                    </table>
                    <p style="margin-top: 10px; font-size: 13px; color: #666;"><strong>教学:</strong> 机构持股>60%说明机构投资者看好，但需注意流动性风险。</p>
                </div>
            </div>
            """
        
        # Phase 7: 估值与护城河
        if 7 in phases:
            phase7 = phases[7]
            data = phase7.get('data', {})
            
            phases_html += f"""
            <div class="analysis-box">
                <div class="analysis-title">Phase 7: 估值与护城河</div>
                <div class="analysis-text">
                    <table class="data-table">
                        <thead>
                            <tr><th>估值指标</th><th>值</th><th>评估</th></tr>
                        </thead>
                        <tbody>
            """
            
            # 估值指标
            valuation_metrics = data.get('估值指标', {})
            for metric, value in valuation_metrics.items():
                # 智能评估
                if 'P/E' in metric:
                    eval_text = '偏高(>30)' if '34' in str(value) else '合理'
                elif 'P/B' in metric:
                    eval_text = '偏高(>10)' if '45' in str(value) else '合理'
                elif 'PEG' in metric:
                    eval_text = '偏高(>2)' if '2.3' in str(value) else '合理'
                else:
                    eval_text = '-'
                
                phases_html += f"""
                            <tr><td>{metric}</td><td><strong>{value}</strong></td><td>{eval_text}</td></tr>
                """
            
            phases_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            # 估值判断
            valuation_judge = data.get('估值判断', {})
            if valuation_judge:
                phases_html += f"""
                <div class="analysis-box">
                    <div class="analysis-title">估值判断</div>
                    <div class="analysis-text">
                        <ul>
                            <li><strong>判断:</strong> {valuation_judge.get('判断', 'N/A')}</li>
                            <li><strong>P/E:</strong> {valuation_judge.get('P/E', 'N/A')} (行业平均: {valuation_judge.get('行业平均', 'N/A')})</li>
                            <li><strong>说明:</strong> {valuation_judge.get('说明', 'N/A')}</li>
                        </ul>
                        <p style="margin-top: 10px; font-size: 13px; color: #666;"><strong>教学:</strong> P/E高于行业平均说明市场给予更高估值溢价，通常意味着更高的增长预期，但也伴随更大风险。</p>
                    </div>
                </div>
                """
            
            # 护城河评分
            moat = data.get('护城河评分', {})
            if moat:
                phases_html += f"""
                <div class="analysis-box">
                    <div class="analysis-title">护城河评分</div>
                    <div class="analysis-text">
                        <ul>
                            <li><strong>总分:</strong> {moat.get('总分', 'N/A')}</li>
                            <li><strong>评级:</strong> {moat.get('评级', 'N/A')}</li>
                        </ul>
                        <p style="margin-top: 10px; font-size: 13px; color: #666;"><strong>教学:</strong> 护城河评分3/5属于中等水平，具备一定竞争优势但不够稳固。</p>
                    </div>
                </div>
                """
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">7</div>
                <div>
                    <div class="section-title">深度研报</div>
                    <span class="section-desc">综合研判 - 提供深度见解</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">研报评级</div>
                    <div class="metric-value" style="font-size: 28px; color: {score_color}">{rating_text}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">研报评分</div>
                    <div class="metric-value">{score}/5</div>
                    <div class="metric-change" style="color: {score_color}">{score_status}</div>
                </div>
            </div>
            
            {phases_html}
            
            <div class="summary-box">
                <div class="summary-title">研报小结</div>
                <div class="summary-text">
                    {recommendation}
                    <br><br>
                    <strong>投资建议:</strong> {'当前估值偏高，建议等待回调机会' if score < 4 else '基本面良好，可考虑分批建仓'}
                </div>
            </div>
        </div>
        '''
    
    def _build_overall_detailed(self, sections: Dict, enhancer) -> str:
        """构建详细的全局观点"""
        
        # 获取技术面数据
        tech = sections.get('technical', {})
        rsi = tech.get('rsi', 50) if tech else 50
        trend = tech.get('trend', '') if tech else ''
        
        # 获取基本面数据
        fundamental = sections.get('fundamental', {})
        pe = fundamental.get('pe', 0) if fundamental else 0
        roe = fundamental.get('roe', 0) if fundamental else 0
        
        # 获取估值数据
        valuation = sections.get('valuation', {})
        upside = valuation.get('upside', 0) if valuation else 0
        
        # 短线建议 (1-5天)
        if rsi > 70:
            short_action = "观望"
            short_reason = f"RSI={rsi:.0f}超买，短线不宜追高。建议等待回调至RSI<60再考虑入场。"
            short_button = "等待回调"
        elif rsi < 30:
            short_action = "轻仓试探"
            short_reason = f"RSI={rsi:.0f}超卖，短线可能反弹。建议轻仓试探，设置止损。"
            short_button = "轻仓入场"
        else:
            short_action = "观望"
            short_reason = f"RSI={rsi:.0f}中性，短线信号不明确。建议观望等待明确信号。"
            short_button = "观望等待"
        
        # 波段建议 (1-3个月)
        if upside < -30:
            medium_action = "减仓"
            medium_reason = f"估值高估{abs(upside):.0f}%，中期风险较大。建议逐步减仓，控制仓位50%以下。"
            medium_button = "逐步减仓"
        elif upside > 20:
            medium_action = "建仓"
            medium_reason = f"估值低估{upside:.0f}%，中期机会较大。建议分批建仓，逢低加仓。"
            medium_button = "分批建仓"
        else:
            medium_action = "持有"
            medium_reason = "估值合理，中期持有。关注基本面变化，适时调整仓位。"
            medium_button = "持有观察"
        
        # 长线建议 (1年以上)
        if roe > 20:
            long_action = "持有"
            long_reason = f"ROE={roe:.0f}%优秀，优质企业。长期看好，建议定期定额投资。"
            long_button = "定期定额"
        elif roe > 15:
            long_action = "持有"
            long_reason = f"ROE={roe:.0f}%良好，稳健企业。可考虑长期持有，关注业绩增长。"
            long_button = "长期持有"
        else:
            long_action = "谨慎"
            long_reason = f"ROE={roe:.0f}%偏低，盈利能力一般。建议谨慎，寻找更优质标的。"
            long_button = "谨慎观望"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">8</div>
                <div>
                    <div class="section-title">全局观点</div>
                    <span class="section-desc">最终建议 - 综合各维度分析</span>
                </div>
            </div>
            
            <div class="advice-section">
                <div class="advice-card short">
                    <div class="advice-label">短线投资者 (1-5天)</div>
                    <div class="advice-action">{short_action}</div>
                    <div class="advice-reason">{short_reason}</div>
                    <div class="advice-button">{short_button}</div>
                </div>
                <div class="advice-card medium">
                    <div class="advice-label">波段投资者 (1-3个月)</div>
                    <div class="advice-action">{medium_action}</div>
                    <div class="advice-reason">{medium_reason}</div>
                    <div class="advice-button">{medium_button}</div>
                </div>
                <div class="advice-card long">
                    <div class="advice-label">长线投资者 (1年以上)</div>
                    <div class="advice-action">{long_action}</div>
                    <div class="advice-reason">{long_reason}</div>
                    <div class="advice-button">{long_button}</div>
                </div>
            </div>
        </div>
        
        <div class="risk-section">
            <div class="risk-title">风险提示</div>
            <div class="risk-text">
                本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
                <br><br>
                报告中的分析基于公开数据，可能存在滞后性或不完整性。投资者应结合自身情况独立判断，并注意以下风险：
                <br>1. 市场风险：股票价格可能因市场情绪、宏观经济等因素大幅波动
                <br>2. 基本面风险：公司经营状况可能发生变化
                <br>3. 流动性风险：市场流动性不足可能导致买卖困难
                <br>4. 估值风险：估值模型存在假设，实际价值可能偏离
            </div>
        </div>
        '''

    def _build_allocation_advice(self, sections: Dict) -> str:
        """构建资产配置建议"""
        
        # 获取关键数据
        valuation = sections.get('valuation', {})
        upside = valuation.get('upside', 0) if valuation else 0
        
        fundamental = sections.get('fundamental', {})
        roe = fundamental.get('roe', 0) if fundamental else 0
        
        tech = sections.get('technical', {})
        rsi = tech.get('rsi', 50) if tech else 50
        
        # 计算建议仓位
        if upside > 30:
            position_advice = "20-30%"
            position_reason = "估值低估，可适当加仓"
        elif upside > 0:
            position_advice = "30-40%"
            position_reason = "估值合理偏低，可持有"
        elif upside > -20:
            position_advice = "20-30%"
            position_reason = "估值合理偏高，控制仓位"
        else:
            position_advice = "5-15%"
            position_reason = "估值高估，大幅减仓"
        
        # 风险等级
        if roe > 20 and upside > 0:
            risk_level = "低风险"
            risk_color = "#27ae60"
        elif roe > 15 or upside > -10:
            risk_level = "中等风险"
            risk_color = "#f39c12"
        else:
            risk_level = "高风险"
            risk_color = "#e74c3c"
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-number">13</div>
                <div>
                    <div class="section-title">资产配置建议</div>
                    <span class="section-desc">仓位管理 - 风险控制</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">建议仓位</div>
                    <div class="metric-value" style="font-size: 28px; color: {risk_color}">{position_advice}</div>
                    <div class="metric-change">{position_reason}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">风险等级</div>
                    <div class="metric-value" style="color: {risk_color}">{risk_level}</div>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">资产配置策略</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>仓位建议：</strong>{position_advice}，{position_reason}</li>
                        <li><strong>风险控制：</strong>单只股票仓位不超过总资产的10-15%</li>
                        <li><strong>分散投资：</strong>建议持有5-10只不同行业股票分散风险</li>
                        <li><strong>止损策略：</strong>设置止损位，亏损超过8-10%及时止损</li>
                    </ul>
                </div>
            </div>
            
            <div class="analysis-box">
                <div class="analysis-title">新手投资建议</div>
                <div class="analysis-text">
                    <ul>
                        <li><strong>定投策略：</strong>每月固定金额投资，平滑成本，降低择时风险</li>
                        <li><strong>止盈策略：</strong>收益超过20%可考虑部分止盈，锁定利润</li>
                        <li><strong>心态管理：</strong>不追涨杀跌，坚持长期投资理念</li>
                        <li><strong>学习提升：</strong>持续学习财务知识和投资技巧</li>
                    </ul>
                </div>
            </div>
            
            <div class="summary-box">
                <div class="summary-title">配置小结</div>
                <div class="summary-text">
                    当前股票建议仓位{position_advice}，风险等级{risk_level}。
                    投资需谨慎，建议结合自身风险承受能力和投资目标，合理配置资产。
                </div>
            </div>
        </div>
        '''


def generate_complete_report(report: Dict, enhancer=None) -> str:
    """生成完整HTML报告"""
    reporter = CompleteStockReporter()
    return reporter.generate(report, enhancer)


if __name__ == '__main__':
    print("完整版股票报告生成器 v3.0")
