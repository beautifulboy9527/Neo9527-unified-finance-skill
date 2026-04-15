#!/usr/bin/env python3
"""
Pipeline Framework - 链式流程框架
支持自定义流程编排
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod


class PipelineNode(ABC):
    """流程节点基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.input_data = None
        self.output_data = None
        self.execution_time = 0
        self.error = None
    
    @abstractmethod
    def execute(self, input_data: Dict) -> Dict:
        """执行节点逻辑"""
        pass
    
    def run(self, input_data: Dict) -> Dict:
        """运行节点（包含计时和错误处理）"""
        start_time = time.time()
        try:
            self.input_data = input_data
            self.output_data = self.execute(input_data)
            self.execution_time = time.time() - start_time
            return self.output_data
        except Exception as e:
            self.error = str(e)
            self.execution_time = time.time() - start_time
            raise


class QuoteNode(PipelineNode):
    """行情获取节点"""
    
    def __init__(self):
        super().__init__("quote")
    
    def execute(self, input_data: Dict) -> Dict:
        symbol = input_data.get('symbol')
        if not symbol:
            raise ValueError("缺少股票代码")
        
        from multi_source_data import MultiSourceData
        msd = MultiSourceData(symbol)
        data = msd.get_quote()
        
        # 验证数据质量
        validation = msd.validate_data(data)
        
        return {
            **input_data,
            'quote': data,
            'quote_valid': validation['valid'],
            'quote_issues': validation['issues']
        }


class ChartNode(PipelineNode):
    """图表生成节点"""
    
    def __init__(self, period: str = '3mo', indicators: Dict = None):
        super().__init__("chart")
        self.period = period
        self.indicators = indicators or {'rsi': True, 'macd': True, 'bb': True}
    
    def execute(self, input_data: Dict) -> Dict:
        symbol = input_data.get('symbol')
        
        from chart_generator import generate_chart
        path = generate_chart(symbol, self.period, self.indicators)
        
        return {
            **input_data,
            'chart_path': path,
            'chart_period': self.period,
            'chart_indicators': self.indicators
        }


class AnalysisNode(PipelineNode):
    """技术分析节点"""
    
    def __init__(self):
        super().__init__("analysis")
    
    def execute(self, input_data: Dict) -> Dict:
        symbol = input_data.get('symbol')
        
        # 获取历史数据
        from multi_source_data import MultiSourceData
        msd = MultiSourceData(symbol)
        hist = msd.get_historical('3mo')
        
        if hist is None or hist.empty:
            return {
                **input_data,
                'analysis': {'error': '无法获取历史数据'}
            }
        
        # 计算技术指标
        import pandas as pd
        import numpy as np
        
        close = hist['Close']
        
        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
        avg_loss = loss.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        ema_fast = close.ewm(span=12, adjust=False, min_periods=12).mean()
        ema_slow = close.ewm(span=26, adjust=False, min_periods=26).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        
        # 布林带位置
        ma = close.rolling(20).mean()
        std = close.rolling(20).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        bb_pos = (close.iloc[-1] - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) * 100
        
        # 生成信号
        signals = []
        
        # RSI 信号
        if current_rsi > 70:
            signals.append({'type': 'rsi_overbought', 'signal': 'sell', 'strength': 'medium'})
        elif current_rsi < 30:
            signals.append({'type': 'rsi_oversold', 'signal': 'buy', 'strength': 'medium'})
        
        # MACD 信号
        if current_macd > current_signal:
            signals.append({'type': 'macd_bullish', 'signal': 'buy', 'strength': 'medium'})
        else:
            signals.append({'type': 'macd_bearish', 'signal': 'sell', 'strength': 'medium'})
        
        # 布林带信号
        if bb_pos > 80:
            signals.append({'type': 'bb_upper', 'signal': 'sell', 'strength': 'weak'})
        elif bb_pos < 20:
            signals.append({'type': 'bb_lower', 'signal': 'buy', 'strength': 'weak'})
        
        return {
            **input_data,
            'technical_analysis': {
                'rsi': float(current_rsi) if not pd.isna(current_rsi) else None,
                'macd': float(current_macd),
                'macd_signal': float(current_signal),
                'bb_position': float(bb_pos),
                'signals': signals
            }
        }


class AlertNode(PipelineNode):
    """警报检查节点"""
    
    def __init__(self):
        super().__init__("alert_check")
    
    def execute(self, input_data: Dict) -> Dict:
        from alert_manager import AlertManager
        
        manager = AlertManager()
        triggered = manager.check()
        
        return {
            **input_data,
            'alerts': triggered,
            'alert_count': len(triggered)
        }


class ReportNode(PipelineNode):
    """报告生成节点"""
    
    def __init__(self, output_format: str = 'text'):
        super().__init__("report")
        self.output_format = output_format
    
    def execute(self, input_data: Dict) -> Dict:
        # 生成综合报告
        report = {
            'symbol': input_data.get('symbol'),
            'timestamp': datetime.now().isoformat(),
            'quote': input_data.get('quote'),
            'technical_analysis': input_data.get('technical_analysis'),
            'alerts': input_data.get('alerts'),
            'chart_path': input_data.get('chart_path')
        }
        
        return {
            **input_data,
            'report': report,
            'report_generated': True
        }


class Pipeline:
    """流程编排器"""
    
    def __init__(self, name: str):
        self.name = name
        self.nodes: List[PipelineNode] = []
        self.execution_log = []
    
    def add_node(self, node: PipelineNode):
        """添加节点"""
        self.nodes.append(node)
        return self  # 支持链式调用
    
    def run(self, input_data: Dict) -> Dict:
        """运行整个流程"""
        print(f"\n启动流程：{self.name}")
        print("=" * 60)
        
        current_data = input_data
        self.execution_log = []
        
        for i, node in enumerate(self.nodes):
            step = i + 1
            print(f"\n[步骤 {step}/{len(self.nodes)}] 执行 {node.name}...")
            
            try:
                start_time = time.time()
                current_data = node.run(current_data)
                elapsed = time.time() - start_time
                
                self.execution_log.append({
                    'step': step,
                    'node': node.name,
                    'status': 'success',
                    'execution_time': elapsed
                })
                
                print(f"  [OK] 完成 ({elapsed:.2f}s)")
                
                if node.error:
                    print(f"  [WARN] {node.error}")
                
            except Exception as e:
                self.execution_log.append({
                    'step': step,
                    'node': node.name,
                    'status': 'failed',
                    'error': str(e)
                })
                
                print(f"  [FAIL] 失败：{e}")
                current_data['pipeline_error'] = str(e)
                break
        
        # 添加执行摘要
        current_data['pipeline_summary'] = {
            'name': self.name,
            'total_steps': len(self.nodes),
            'completed_steps': len(self.execution_log),
            'success': all(log['status'] == 'success' for log in self.execution_log),
            'total_time': sum(log.get('execution_time', 0) for log in self.execution_log),
            'log': self.execution_log
        }
        
        print("\n" + "=" * 60)
        if current_data['pipeline_summary']['success']:
            print(f"流程完成：{self.name}")
            print(f"总耗时：{current_data['pipeline_summary']['total_time']:.2f}s")
        else:
            print(f"流程失败：{self.name}")
        
        return current_data
    
    def get_report(self, result: Dict) -> str:
        """生成流程执行报告"""
        summary = result.get('pipeline_summary', {})
        
        report = f"""
流程执行报告
{'=' * 60}
流程名称：{self.name}
执行状态：{'成功' if summary.get('success') else '失败'}
完成进度：{summary.get('completed_steps', 0)}/{summary.get('total_steps', 0)}
总耗时：{summary.get('total_time', 0):.2f}秒

执行日志:
"""
        
        for log in summary.get('log', []):
            status_icon = '[OK]' if log['status'] == 'success' else '[FAIL]'
            report += f"  {status_icon} 步骤{log['step']}: {log['node']} ({log.get('execution_time', 0):.2f}s)\n"
            if log.get('error'):
                report += f"    错误：{log['error']}\n"
        
        return report


# 预定义流程模板

def create_daily_monitor_pipeline() -> Pipeline:
    """创建日常监控流程"""
    return (Pipeline("日常监控")
            .add_node(QuoteNode())
            .add_node(AlertNode())
            .add_node(ReportNode()))


def create_deep_analysis_pipeline() -> Pipeline:
    """创建深度分析流程"""
    return (Pipeline("深度分析")
            .add_node(QuoteNode())
            .add_node(ChartNode(period='6mo'))
            .add_node(AnalysisNode())
            .add_node(AlertNode())
            .add_node(ReportNode()))


def create_quick_check_pipeline() -> Pipeline:
    """创建快速检查流程"""
    return (Pipeline("快速检查")
            .add_node(QuoteNode())
            .add_node(AlertNode()))


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python pipeline.py <股票代码> [流程类型]")
        print("流程类型：daily, deep, quick")
        print("示例：python pipeline.py AAPL deep")
        sys.exit(1)
    
    symbol = sys.argv[1]
    pipeline_type = sys.argv[2] if len(sys.argv) > 2 else 'deep'
    
    # 选择流程
    if pipeline_type == 'daily':
        pipeline = create_daily_monitor_pipeline()
    elif pipeline_type == 'deep':
        pipeline = create_deep_analysis_pipeline()
    else:
        pipeline = create_quick_check_pipeline()
    
    # 运行流程
    result = pipeline.run({'symbol': symbol})
    
    # 输出报告
    print("\n" + pipeline.get_report(result))
    
    # 如果有技术分析，输出信号
    if 'technical_analysis' in result:
        analysis = result['technical_analysis']
        if 'signals' in analysis:
            print("\n技术信号:")
            for sig in analysis['signals']:
                print(f"  - {sig['type']}: {sig['signal']} ({sig['strength']})")
    
    # 如果有警报，输出警报
    if 'alerts' in result and result['alerts']:
        print("\n触发警报:")
        for alert in result['alerts']:
            print(f"  [ALERT] {alert.get('message', '未知警报')}")
