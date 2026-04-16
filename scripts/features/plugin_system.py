#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件系统 - 可扩展的分析框架
支持动态加载、优先级排序、自动发现
"""

import sys
import os
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class AnalysisPlugin(ABC):
    """
    分析插件基类
    
    所有插件必须继承此类并实现 execute() 方法
    """
    
    # 插件元信息
    name: str = "base_plugin"
    description: str = "基础插件"
    version: str = "1.0.0"
    
    # 优先级 (数字越小越先执行)
    priority: int = 100
    
    # 适用的投资周期
    applicable_periods: List[str] = ['long', 'medium', 'short']
    
    # 依赖的其他插件
    dependencies: List[str] = []
    
    @abstractmethod
    def execute(self, symbol: str, context: Dict) -> Dict:
        """
        执行分析
        
        Args:
            symbol: 股票代码
            context: 共享上下文 (之前插件的结果)
            
        Returns:
            分析结果字典
        """
        pass
    
    def validate_dependencies(self, context: Dict) -> bool:
        """检查依赖是否满足"""
        for dep in self.dependencies:
            if dep not in context:
                return False
        return True


class PluginRegistry:
    """
    插件注册表
    
    管理所有注册的插件，支持:
    - 动态注册/注销
    - 优先级排序
    - 自动发现
    """
    
    def __init__(self):
        self._plugins: Dict[str, AnalysisPlugin] = {}
        self._execution_order: List[str] = []
    
    def register(self, plugin: AnalysisPlugin) -> None:
        """注册插件"""
        self._plugins[plugin.name] = plugin
        self._update_execution_order()
    
    def unregister(self, name: str) -> None:
        """注销插件"""
        if name in self._plugins:
            del self._plugins[name]
            self._update_execution_order()
    
    def get(self, name: str) -> Optional[AnalysisPlugin]:
        """获取插件"""
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """列出所有插件"""
        return list(self._plugins.keys())
    
    def _update_execution_order(self) -> None:
        """更新执行顺序 (按优先级)"""
        sorted_plugins = sorted(
            self._plugins.values(),
            key=lambda p: p.priority
        )
        self._execution_order = [p.name for p in sorted_plugins]
    
    def auto_discover(self, plugin_dir: str) -> int:
        """
        自动发现插件
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            发现的插件数量
        """
        discovered = 0
        
        if not os.path.exists(plugin_dir):
            return 0
        
        # 遍历目录
        for file in os.listdir(plugin_dir):
            if file.endswith('_plugin.py'):
                module_name = file[:-3]  # 去掉 .py
                
                try:
                    # 动态导入
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(plugin_dir, file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找插件类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, AnalysisPlugin) and 
                            attr != AnalysisPlugin):
                            # 实例化并注册
                            plugin = attr()
                            self.register(plugin)
                            discovered += 1
                            
                except Exception as e:
                    print(f"Failed to load plugin {file}: {e}")
        
        return discovered


class PluginOrchestrator:
    """
    插件编排器
    
    执行插件链，管理上下文
    """
    
    def __init__(self, registry: PluginRegistry):
        self.registry = registry
    
    def run_analysis(
        self, 
        symbol: str, 
        period: str = 'medium',
        plugins: Optional[List[str]] = None
    ) -> Dict:
        """
        运行分析
        
        Args:
            symbol: 股票代码
            period: 投资周期 (long/medium/short)
            plugins: 指定要运行的插件 (None = 全部)
            
        Returns:
            分析结果
        """
        context = {
            'symbol': symbol,
            'period': period,
            'results': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 确定要运行的插件
        if plugins:
            plugin_names = plugins
        else:
            plugin_names = self.registry._execution_order
        
        # 按优先级执行
        for name in plugin_names:
            plugin = self.registry.get(name)
            
            if not plugin:
                continue
            
            # 检查投资周期适用性
            if period not in plugin.applicable_periods:
                continue
            
            # 检查依赖
            if not plugin.validate_dependencies(context['results']):
                context['results'][name] = {
                    'error': '依赖未满足',
                    'dependencies': plugin.dependencies
                }
                continue
            
            # 执行
            try:
                result = plugin.execute(symbol, context)
                context['results'][name] = result
            except Exception as e:
                context['results'][name] = {'error': str(e)}
        
        return context


# ============================================
# 内置插件实现
# ============================================

class MacroAnalysisPlugin(AnalysisPlugin):
    """宏观分析插件"""
    
    name = "macro"
    description = "宏观环境分析"
    priority = 10  # 最先执行
    applicable_periods = ['long', 'medium']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行宏观分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.analysis_framework import AnalysisFramework
            
            framework = AnalysisFramework()
            result = framework._analyze_macro(context.get('market', 'cn'))
            
            return {
                'score': result.get('total_score', 0),
                'cycle': result.get('cycle_desc', 'unknown'),
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class SectorAnalysisPlugin(AnalysisPlugin):
    """行业分析插件"""
    
    name = "sector"
    description = "行业板块分析"
    priority = 20
    applicable_periods = ['long', 'medium']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行行业分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.analysis_framework import AnalysisFramework
            
            framework = AnalysisFramework()
            result = framework._analyze_sector(symbol)
            
            return {
                'score': result.get('total_score', 0),
                'strength': result.get('relative_strength', 'unknown'),
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class TechnicalAnalysisPlugin(AnalysisPlugin):
    """技术分析插件"""
    
    name = "technical"
    description = "技术面分析"
    priority = 30
    applicable_periods = ['medium', 'short']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行技术分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from core.technical import analyze_technical
            
            result = analyze_technical(symbol)
            basic = result.get('basic_indicators', {})
            ai = result.get('ai_decision', {})
            
            return {
                'trend': basic.get('trend', 'unknown'),
                'rsi': basic.get('rsi', 0),
                'recommendation': ai.get('recommendation', 'hold'),
                'confidence': ai.get('confidence', 0),
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class SignalDetectionPlugin(AnalysisPlugin):
    """信号检测插件"""
    
    name = "signals"
    description = "入场信号检测"
    priority = 40
    applicable_periods = ['medium', 'short']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行信号检测"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.entry_signals import analyze_entry_signals
            
            result = analyze_entry_signals(symbol)
            score = result.get('score', {})
            
            return {
                'score': score.get('overall_score', 0),
                'action': score.get('action', 'hold'),
                'signals': [s.get('name') for s in result.get('signals', [])],
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class RiskManagementPlugin(AnalysisPlugin):
    """风险管理插件"""
    
    name = "risk"
    description = "风险管理分析"
    priority = 50
    applicable_periods = ['medium', 'short']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行风险管理分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.risk_management import analyze_risk
            
            result = analyze_risk(symbol)
            summary = result.get('summary', {})
            
            return {
                'entry_price': summary.get('entry_price'),
                'stop_loss': summary.get('stop_loss'),
                'target_price': summary.get('target_price'),
                'position_value': summary.get('position_value'),
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class FundamentalPlugin(AnalysisPlugin):
    """基本面分析插件"""
    
    name = "fundamental"
    description = "基本面深度分析"
    priority = 25
    applicable_periods = ['long']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行基本面分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from core.financial import get_financial_summary
            
            result = get_financial_summary(symbol)
            
            # 计算基本面评分
            score = 0
            reasons = []
            
            # ROE > 15%
            roe = result.get('roe')
            if roe and roe > 15:
                score += 30
                reasons.append(f"ROE {roe}% > 15%")
            
            # 负债率 < 60%
            debt = result.get('debt_ratio')
            if debt and debt < 60:
                score += 25
                reasons.append(f"负债率 {debt}% < 60%")
            
            return {
                'score': score,
                'reasons': reasons,
                'roe': roe,
                'debt_ratio': debt,
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


class ValuationPlugin(AnalysisPlugin):
    """估值分析插件"""
    
    name = "valuation"
    description = "估值分析"
    priority = 35
    applicable_periods = ['long', 'medium']
    
    def execute(self, symbol: str, context: Dict) -> Dict:
        """执行估值分析"""
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        try:
            from features.valuation import get_valuation_summary
            
            result = get_valuation_summary(symbol)
            
            return {
                'pe_level': result.get('pe_analysis', {}).get('level'),
                'pb_level': result.get('pb_analysis', {}).get('level'),
                'assessment': result.get('overall_assessment'),
                'data': result
            }
        except Exception as e:
            return {'error': str(e)}


# ============================================
# 便捷函数
# ============================================

def create_default_registry() -> PluginRegistry:
    """创建默认插件注册表"""
    registry = PluginRegistry()
    
    # 注册内置插件
    registry.register(MacroAnalysisPlugin())
    registry.register(SectorAnalysisPlugin())
    registry.register(FundamentalPlugin())
    registry.register(ValuationPlugin())
    registry.register(TechnicalAnalysisPlugin())
    registry.register(SignalDetectionPlugin())
    registry.register(RiskManagementPlugin())
    
    return registry


def analyze_with_plugins(
    symbol: str, 
    period: str = 'medium',
    plugins: Optional[List[str]] = None
) -> Dict:
    """
    使用插件系统进行分析
    
    Args:
        symbol: 股票代码
        period: 投资周期
        plugins: 指定插件 (None = 全部)
        
    Returns:
        分析结果
    """
    registry = create_default_registry()
    orchestrator = PluginOrchestrator(registry)
    return orchestrator.run_analysis(symbol, period, plugins)


if __name__ == '__main__':
    import json
    
    # 测试
    print("=" * 60)
    print("插件系统测试")
    print("=" * 60)
    
    # 创建注册表
    registry = create_default_registry()
    print(f"\n已注册插件: {registry.list_plugins()}")
    
    # 运行分析
    symbol = '002241'
    
    print(f"\n分析股票: {symbol}")
    print("-" * 60)
    
    for period in ['long', 'medium', 'short']:
        print(f"\n投资周期: {period}")
        result = analyze_with_plugins(symbol, period)
        
        for plugin_name, plugin_result in result['results'].items():
            if 'error' not in plugin_result:
                print(f"  {plugin_name}: {plugin_result.get('score', plugin_result.get('trend', 'N/A'))}")
            else:
                print(f"  {plugin_name}: 错误 - {plugin_result['error']}")
