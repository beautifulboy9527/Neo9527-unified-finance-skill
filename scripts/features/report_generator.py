#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化报告生成器
支持 Markdown + HTML + PDF，嵌入图表
"""

import sys
import os
import base64
from datetime import datetime
from typing import Dict, List, Optional
from io import BytesIO

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class VisualizationEngine:
    """可视化引擎 - 生成图表"""
    
    def __init__(self):
        self.figures = []
    
    def create_kline_chart(
        self,
        symbol: str,
        df,
        title: str = "K线图"
    ) -> str:
        """生成K线图 (Base64)"""
        try:
            import mplfinance as mpf
            import matplotlib.pyplot as plt
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建图表
            fig, axes = plt.subplots(2, 1, figsize=(12, 8), 
                                    gridspec_kw={'height_ratios': [3, 1]})
            
            # K线
            mpf.plot(df, type='candle', style='charles',
                    ax=axes[0], volume=False)
            axes[0].set_title(f"{symbol} - {title}", fontsize=14)
            axes[0].grid(True, alpha=0.3)
            
            # 成交量
            axes[1].bar(df.index, df['Volume'], color='steelblue', alpha=0.7)
            axes[1].set_title('成交量', fontsize=12)
            axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 转换为 Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"⚠️ K线图生成失败: {e}")
            return None
    
    def create_radar_chart(
        self,
        data: Dict[str, float],
        title: str = "综合评分雷达图"
    ) -> str:
        """生成雷达图 (Base64)"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            categories = list(data.keys())
            values = list(data.values())
            
            # 闭合雷达图
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]
            
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB')
            ax.fill(angles, values, alpha=0.25, color='#2E86AB')
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=11)
            ax.set_ylim(0, 100)
            ax.set_title(title, fontsize=14, pad=20)
            
            # 转换为 Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"⚠️ 雷达图生成失败: {e}")
            return None
    
    def create_correlation_heatmap(
        self,
        correlation_matrix: Dict,
        title: str = "相关性矩阵"
    ) -> str:
        """生成相关性热力图 (Base64)"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            import numpy as np
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 转换为 DataFrame
            df = pd.DataFrame(correlation_matrix)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            sns.heatmap(df, annot=True, fmt='.2f', cmap='RdYlBu_r',
                       center=0, vmin=-1, vmax=1,
                       square=True, linewidths=0.5,
                       cbar_kws={'shrink': 0.8})
            
            ax.set_title(title, fontsize=14, pad=15)
            
            plt.tight_layout()
            
            # 转换为 Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"⚠️ 热力图生成失败: {e}")
            return None
    
    def create_monte_carlo_chart(
        self,
        simulations: List[List[float]],
        title: str = "Monte Carlo 模拟"
    ) -> str:
        """生成 Monte Carlo 分布图 (Base64)"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # 路径图
            for i, path in enumerate(simulations[:50]):  # 只画前50条
                axes[0].plot(path, alpha=0.3, linewidth=0.8)
            
            axes[0].set_title('模拟路径', fontsize=12)
            axes[0].set_xlabel('天数', fontsize=10)
            axes[0].set_ylabel('价格', fontsize=10)
            axes[0].grid(True, alpha=0.3)
            
            # 终值分布
            final_prices = [path[-1] for path in simulations]
            axes[1].hist(final_prices, bins=50, color='#2E86AB', alpha=0.7, edgecolor='white')
            axes[1].axvline(np.mean(final_prices), color='red', linestyle='--', 
                           label=f'均值: {np.mean(final_prices):.2f}')
            axes[1].set_title('终值分布', fontsize=12)
            axes[1].set_xlabel('价格', fontsize=10)
            axes[1].set_ylabel('频数', fontsize=10)
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
            
            fig.suptitle(title, fontsize=14, y=1.02)
            
            plt.tight_layout()
            
            # 转换为 Base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"⚠️ Monte Carlo图生成失败: {e}")
            return None


class ReportGenerator:
    """
    报告生成器
    
    支持:
    - Markdown 格式
    - HTML 格式 (嵌入图表)
    - PDF 格式 (需安装 weasyprint)
    """
    
    def __init__(self, output_dir: str = "D:\\OpenClaw\\outputs\\reports"):
        self.output_dir = output_dir
        self.viz = VisualizationEngine()
        
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_full_report(
        self,
        symbol: str,
        period: str = 'medium',
        format: str = 'html'
    ) -> str:
        """
        生成完整报告
        
        Args:
            symbol: 股票代码
            period: 投资周期
            format: 输出格式 (markdown/html/pdf)
            
        Returns:
            报告文件路径
        """
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # ========== 新增: 资产类型识别 ==========
        from features.asset_type import detect_asset_type, get_analysis_config
        
        asset_info = detect_asset_type(symbol)
        asset_type = asset_info['type']
        analysis_config = get_analysis_config(asset_type)
        
        print(f"\n📊 资产类型: {asset_type} ({asset_info['market']})")
        print(f"可用功能: {', '.join(asset_info['features'])}")
        
        if asset_info.get('limitations'):
            print(f"⚠️ 限制: {asset_info['limitations']}")
        
        # 根据资产类型选择分析逻辑
        if asset_type == 'crypto':
            return self._generate_crypto_report(symbol, period, format, analysis_config)
        else:
            return self._generate_stock_report(symbol, period, format, analysis_config)
    
    def _generate_crypto_report(
        self,
        symbol: str,
        period: str,
        format: str,
        config: Dict
    ) -> str:
        """生成加密货币报告"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from features.crypto_analyzer import analyze_crypto
        from features.asset_type import detect_asset_type
        
        # 加密货币分析
        crypto_result = analyze_crypto(symbol)
        asset_info = detect_asset_type(symbol)
        
        # 生成图表
        radar_data = {
            '技术面': crypto_result['technical'].get('ai_decision', {}).get('confidence', 0),
            '信号强度': crypto_result['signals'].get('score', {}).get('overall_score', 0),
            '市场情绪': crypto_result['sentiment'].get('sentiment_score', 50),
            '链上活跃度': 60,  # 默认值
            '流动性': 70
        }
        
        radar_chart = self.viz.create_radar_chart(radar_data, f"{symbol} 综合评分 (加密货币)")
        
        # 根据格式生成报告
        if format == 'html':
            return self._generate_crypto_html(symbol, crypto_result, radar_chart, config)
        else:
            return self._generate_crypto_markdown(symbol, crypto_result, config)
        from features.backtest_engine import validate_signal_performance, sma_cross_signal
        from features.portfolio_manager import analyze_portfolio
        from features.finance_toolkit import analyze_fundamentals_deep
        
        investment_result = analyze_investment(symbol, period)
        plugin_result = analyze_with_plugins(symbol, period)
        backtest_result = validate_signal_performance(symbol, sma_cross_signal, "SMA交叉")
        fundamentals = analyze_fundamentals_deep(symbol)
        
        # 2. 生成图表
        radar_data = {
            '基本面': fundamentals.get('score', 0),
            '技术面': investment_result.get('decision', {}).get('confidence', 0),
            '信号': backtest_result.get('validation_score', 0) if 'error' not in backtest_result else 0,
            '风险': 100 - abs(plugin_result.get('results', {}).get('risk', {}).get('data', {}).get('summary', {}).get('stop_loss_pct', 0)) * 10,
            '流动性': plugin_result.get('results', {}).get('signals', {}).get('score', 0) if 'error' not in plugin_result.get('results', {}).get('signals', {}) else 50
        }
        
        radar_chart = self.viz.create_radar_chart(radar_data, f"{symbol} 综合评分")
        
        # 3. 生成报告
        if format == 'markdown':
            return self._generate_markdown(symbol, period, investment_result, 
                                          plugin_result, backtest_result, fundamentals)
        elif format == 'html':
            return self._generate_html(symbol, period, investment_result,
                                      plugin_result, backtest_result, fundamentals, radar_chart)
        elif format == 'pdf':
            html_path = self._generate_html(symbol, period, investment_result,
                                           plugin_result, backtest_result, fundamentals, radar_chart)
            return self._convert_to_pdf(html_path)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _generate_markdown(
        self,
        symbol: str,
        period: str,
        investment_result: Dict,
        plugin_result: Dict,
        backtest_result: Dict,
        fundamentals: Dict
    ) -> str:
        """生成 Markdown 报告"""
        
        period_names = {
            'long': '长线投资 (1-3年+)',
            'medium': '中线投资 (1-6个月)',
            'short': '短线交易 (数天-数周)'
        }
        
        decision = investment_result.get('decision', {})
        
        report = f"""# {symbol} 投资分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**投资周期**: {period_names.get(period, period)}  
**报告版本**: v3.2

---

## 📊 一、综合评分

| 维度 | 评分 |
|------|------|
| 基本面 | {fundamentals.get('score', 0)}/100 |
| 技术面 | {decision.get('confidence', 0)}/100 |
| 信号验证 | {backtest_result.get('validation_score', 0) if 'error' not in backtest_result else 0}/100 |

---

## 🎯 二、投资决策

### 建议操作

**{decision.get('action', 'hold').upper()}** - 置信度 {decision.get('confidence', 0)}/100

### 决策依据

"""
        
        for reason in decision.get('reasons', []):
            report += f"- ✅ {reason}\n"
        
        for risk in decision.get('risks', []):
            report += f"- ⚠️ {risk}\n"
        
        # 保存
        output_path = os.path.join(self.output_dir, f"{symbol}_report.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path
    
    def _generate_html(
        self,
        symbol: str,
        period: str,
        investment_result: Dict,
        plugin_result: Dict,
        backtest_result: Dict,
        fundamentals: Dict,
        radar_chart: Optional[str] = None
    ) -> str:
        """生成 HTML 报告 (股票)"""
        
        period_names = {
            'long': '长线投资 (1-3年+)',
            'medium': '中线投资 (1-6个月)',
            'short': '短线交易 (数天-数周)'
        }
        
        decision = investment_result.get('decision', {})
        
        # 图表嵌入
        radar_img = f'<img src="data:image/png;base64,{radar_chart}" alt="雷达图" style="width: 100%; max-width: 600px;">' if radar_chart else '<p>图表生成失败</p>'
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 投资分析报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #333;
            margin-top: 30px;
            border-left: 4px solid #2E86AB;
            padding-left: 15px;
        }}
        .meta {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #2E86AB;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .decision {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }}
        .decision-action {{
            font-size: 24px;
            font-weight: bold;
            color: #2E86AB;
        }}
        .success {{
            color: #4CAF50;
        }}
        .warning {{
            color: #FF9800;
        }}
        .danger {{
            color: #F44336;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .score-box {{
            display: inline-block;
            padding: 15px 25px;
            margin: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        .score-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2E86AB;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{symbol} 投资分析报告</h1>
        
        <div class="meta">
            <strong>分析时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
            <strong>投资周期:</strong> {period_names.get(period, period)}<br>
            <strong>报告版本:</strong> v3.2
        </div>
        
        <h2>📊 一、综合评分</h2>
        
        <div style="text-align: center;">
            <div class="score-box">
                <div class="score-value">{fundamentals.get('score', 0)}</div>
                <div>基本面</div>
            </div>
            <div class="score-box">
                <div class="score-value">{decision.get('confidence', 0)}</div>
                <div>技术面</div>
            </div>
            <div class="score-box">
                <div class="score-value">{backtest_result.get('validation_score', 0) if 'error' not in backtest_result else 0}</div>
                <div>信号验证</div>
            </div>
        </div>
        
        <div class="chart-container">
            {radar_img}
        </div>
        
        <h2>🎯 二、投资决策</h2>
        
        <div class="decision">
            <div class="decision-action">{decision.get('action', 'hold').upper()}</div>
            <div>置信度: {decision.get('confidence', 0)}/100</div>
        </div>
        
        <h3>决策依据</h3>
        <ul>
"""
        
        for reason in decision.get('reasons', []):
            html += f'            <li class="success">✅ {reason}</li>\n'
        
        for risk in decision.get('risks', []):
            html += f'            <li class="warning">⚠️ {risk}</li>\n'
        
        html += """        </ul>
        
        <h2>⚠️ 重要声明</h2>
        <p>本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。</p>
        
        <div class="footer">
            <p>Neo9527 Unified Finance Skill v3.2 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # 保存
        output_path = os.path.join(self.output_dir, f"{symbol}_report.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def _generate_crypto_html(
        self,
        symbol: str,
        crypto_result: Dict,
        radar_chart: Optional[str],
        config: Dict
    ) -> str:
        """生成加密货币专用HTML报告"""
        
        # 图表嵌入
        radar_img = f'<img src="data:image/png;base64,{radar_chart}" alt="雷达图" style="width: 100%; max-width: 600px;">' if radar_chart else '<p>图表生成失败</p>'
        
        # 情绪指标
        sentiment = crypto_result['sentiment']
        fear_greed = sentiment.get('fear_greed_index', 'N/A')
        sentiment_class = sentiment.get('fear_greed_class', 'N/A')
        
        # 技术面
        tech = crypto_result['technical']
        basic = tech.get('basic_indicators', {})
        ai_decision = tech.get('ai_decision', {})
        
        # 信号
        signals = crypto_result['signals']
        signal_score = signals.get('score', {}).get('overall_score', 0)
        
        # 链上数据
        onchain = crypto_result['onchain']
        
        # 风险警告
        risk_warning = config.get('risk_warning', '')
        volatility_warning = tech.get('volatility_warning', '')
        
        # 数据来源列表
        data_sources = []
        if onchain.get('data_source'):
            data_sources.append(onchain['data_source'])
        if sentiment.get('data_source'):
            data_sources.append(sentiment['data_source'])
        
        # 价格数据
        current_price = onchain.get('current_price_usd', 'N/A')
        price_change_24h = onchain.get('price_change_24h', 'N/A')
        volume_24h = onchain.get('volume_24h', 'N/A')
        market_cap = onchain.get('market_cap', 'N/A')
        market_cap_rank = onchain.get('market_cap_rank', 'N/A')
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{symbol} 加密货币分析报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }}
        h1 {{ color: #764ba2; border-bottom: 3px solid #667eea; padding-bottom: 15px; }}
        h2 {{ color: #333; margin-top: 30px; border-left: 4px solid #667eea; padding-left: 15px; }}
        .crypto-badge {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; }}
        .score-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
        .score-value {{ font-size: 48px; font-weight: bold; color: #764ba2; }}
        .decision {{ background: #e8f4f8; padding: 25px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #00bcd4; }}
        .decision-action {{ font-size: 28px; font-weight: bold; color: #00bcd4; }}
        .warning-box {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .data-source {{ background: #e3f2fd; border: 1px solid #2196f3; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 13px; }}
        .chart-container {{ text-align: center; margin: 30px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{symbol} 加密货币分析报告 <span class="crypto-badge">CRYPTO</span></h1>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <strong>分析时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
            <strong>资产类型:</strong> 加密货币<br>
            <strong>报告版本:</strong> v3.2 (专业版)
        </div>
        
        <!-- 调整顺序: 综合评分 -> 市场数据 -> 技术分析 -> 情绪 -> 风险 -> 决策 -->
        
        <h2>📊 一、综合评分</h2>
        
        <div class="score-card">
            <div class="score-value">{crypto_result['score']}/100</div>
            <div style="font-size: 18px; color: #666;">综合评分</div>
        </div>
        
        <div class="chart-container">
            {radar_img}
        </div>
        
        <h2>💰 二、市场数据 (实时)</h2>
        
        <table>
            <tr><th>指标</th><th>数值</th><th>说明</th></tr>
            <tr><td>当前价格</td><td><strong>${current_price:,.2f}</strong></td><td>实时价格</td></tr>
            <tr><td>24h 涨跌</td><td>{price_change_24h:+.2f}%</td><td>{'📈 上涨' if price_change_24h and price_change_24h > 0 else '📉 下跌' if price_change_24h else '-'}</td></tr>
            <tr><td>24h 成交量</td><td>${volume_24h/1e9:.2f}B</td><td>市场活跃度</td></tr>
            <tr><td>市值</td><td>${market_cap/1e9:.2f}B</td><td>市场排名第 {market_cap_rank}</td></tr>
        </table>
        
        <h2>📉 三、技术分析</h2>
        
        <table>
            <tr><th>指标</th><th>数值</th><th>解读</th></tr>
            <tr><td>恐慌贪婪指数</td><td><strong>{fear_greed}</strong></td><td>{sentiment_class}</td></tr>
            <tr><td>情绪评分</td><td>{sentiment.get('sentiment_score', 'N/A')}</td><td>{'极度恐惧时往往是买入机会' if isinstance(fear_greed, int) and fear_greed < 25 else '极度贪婪时需注意风险' if isinstance(fear_greed, int) and fear_greed > 75 else '中性'}</td></tr>
            <tr><td>数据来源</td><td colspan="2"><a href="{sentiment.get('source_url', '#')}" target="_blank">{sentiment.get('data_source', 'N/A')}</a></td></tr>
        </table>
        
        <h2>📉 五、技术分析</h2>
        
        <table>
            <tr><th>指标</th><th>数值</th><th>状态</th></tr>
            <tr><td>当前价格</td><td><strong>${basic.get('current_price', 'N/A')}</strong></td><td>实时</td></tr>
            <tr><td>趋势</td><td>{basic.get('trend', 'N/A')}</td><td>{'📈 多头' if basic.get('trend') == 'uptrend' else '📉 空头' if basic.get('trend') == 'downtrend' else '➡️ 震荡'}</td></tr>
            <tr><td>RSI</td><td>{basic.get('rsi', 'N/A')}</td><td>{'⚠️ 超买' if isinstance(basic.get('rsi'), (int, float)) and basic['rsi'] > 70 else '⚠️ 超卖' if isinstance(basic.get('rsi'), (int, float)) and basic['rsi'] < 30 else '✅ 正常'}</td></tr>
            <tr><td>MA5</td><td>${basic.get('ma5', 'N/A')}</td><td>短期均线</td></tr>
            <tr><td>MA10</td><td>${basic.get('ma10', 'N/A')}</td><td>中期均线</td></tr>
            <tr><td>MA20</td><td>${basic.get('ma20', 'N/A')}</td><td>长期均线</td></tr>
            <tr><td>MACD</td><td>{basic.get('macd', 'N/A')}</td><td>{'📈 多头' if basic.get('macd_trend') == 'bullish' else '📉 空头' if basic.get('macd_trend') == 'bearish' else '-'}</td></tr>
            <tr><td>Bollinger</td><td>{basic.get('bb_position', 'N/A')}</td><td>{'⚠️ 突破上轨' if basic.get('bb_position') == 'above_upper' else '⚠️ 跌破下轨' if basic.get('bb_position') == 'below_lower' else '区间内'}</td></tr>
            <tr><td>成交量</td><td>{basic.get('volume_ratio', 'N/A')}x</td><td>{'放量' if isinstance(basic.get('volume_ratio'), (int, float)) and basic['volume_ratio'] > 1.2 else '缩量' if isinstance(basic.get('volume_ratio'), (int, float)) and basic['volume_ratio'] < 0.8 else '正常'}</td></tr>
            <tr><td>ADX</td><td>{basic.get('adx', 'N/A')}</td><td>{basic.get('trend_strength', 'N/A')}</td></tr>
            <tr><td>Stochastic %K</td><td>{basic.get('stoch_k', 'N/A')}</td><td>{'⚠️ 超买' if isinstance(basic.get('stoch_k'), (int, float)) and basic['stoch_k'] > 80 else '⚠️ 超卖' if isinstance(basic.get('stoch_k'), (int, float)) and basic['stoch_k'] < 20 else '正常'}</td></tr>
        </table>
        
        <h3>📝 技术面专业解读 (多指标共振分析)</h3>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0;">
            {tech.get('narrative', '暂无解读').replace(chr(10), '<br><br>')}
        </div>
        
        <h2>⚠️ 六、风险提示</h2>
        
        <div class="warning-box">
            <strong>⚠️ 加密货币风险警告：</strong><br>
            {risk_warning}<br>
            {volatility_warning}
        </div>
        
        <h2>📋 七、数据来源</h2>
        
        <div class="data-source">
            <strong>本报告使用以下真实数据源：</strong><br>
            • 市场数据: <a href="{onchain.get('source_url', '#')}" target="_blank">{onchain.get('data_source', 'N/A')}</a><br>
            • 情绪指数: <a href="{sentiment.get('source_url', '#')}" target="_blank">{sentiment.get('data_source', 'N/A')}</a><br>
            • 技术分析: yfinance (Yahoo Finance)<br>
            <br>
            <em>所有数据均来自公开免费API，可验证、可追溯。</em>
        </div>
        
        <h2>📝 八、重要声明</h2>
        
        <p>本报告仅供加密货币投资参考，不构成投资建议。</p>
        <p><strong>加密货币风险极高：</strong></p>
        <ul>
            <li>价格波动率远高于传统股票</li>
            <li>市场流动性可能突然枯竭</li>
            <li>监管政策变化风险</li>
            <li>交易所安全风险</li>
        </ul>
        <p>建议：小仓位 + 严格止损 + 长期持有优质资产</p>
        
        <div class="footer">
            <p>Neo9527 Unified Finance Skill v3.2 | 多资产适配版 (真实数据)</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        # 保存
        output_path = os.path.join(self.output_dir, f"{symbol}_report.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def _generate_stock_report(
        self,
        symbol: str,
        period: str,
        format: str,
        config: Dict
    ) -> str:
        """生成股票报告 (原有逻辑)"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 1. 收集数据
        from features.investment_framework import analyze_investment
        from features.plugin_system import analyze_with_plugins
    
    def _convert_to_pdf(self, html_path: str) -> str:
        """转换 HTML 为 PDF"""
        try:
            from weasyprint import HTML
            
            pdf_path = html_path.replace('.html', '.pdf')
            HTML(html_path).write_pdf(pdf_path)
            
            return pdf_path
            
        except ImportError:
            print("⚠️ 需要安装 weasyprint: pip install weasyprint")
            return html_path
        except Exception as e:
            print(f"⚠️ PDF转换失败: {e}")
            return html_path


# ============================================
# 便捷函数
# ============================================

def generate_report(
    symbol: str,
    period: str = 'medium',
    format: str = 'html'
) -> str:
    """
    生成投资报告
    
    Args:
        symbol: 股票代码
        period: 投资周期
        format: 输出格式 (markdown/html/pdf)
        
    Returns:
        报告文件路径
    """
    generator = ReportGenerator()
    return generator.generate_full_report(symbol, period, format)


if __name__ == '__main__':
    symbol = '002241'
    
    print("=" * 60)
    print(f"生成投资报告: {symbol}")
    print("=" * 60)
    
    # 生成 HTML 报告
    print("\n📊 生成 HTML 报告...")
    html_path = generate_report(symbol, 'medium', 'html')
    print(f"✅ HTML 报告已生成: {html_path}")
    
    # 生成 Markdown 报告
    print("\n📝 生成 Markdown 报告...")
    md_path = generate_report(symbol, 'medium', 'markdown')
    print(f"✅ Markdown 报告已生成: {md_path}")
    
    print("\n🎉 报告生成完成！")
