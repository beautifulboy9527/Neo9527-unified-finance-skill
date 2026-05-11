#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance Skill 基础接口规范

所有独立 Skill 必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import importlib.util
import os


@dataclass
class SkillInput:
    """Skill 标准输入"""
    symbol: str
    market: str  # crypto, stock, forex
    timeframe: str = "medium"  # short, medium, long
    params: Dict = None
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'market': self.market,
            'timeframe': self.timeframe,
            'params': self.params or {}
        }


@dataclass
class SkillOutput:
    """Skill 标准输出"""
    skill_name: str
    success: bool
    data: Dict
    signals: List[Dict]
    score: float  # 0-100
    confidence: float  # 0-1
    timestamp: str
    data_source: List[str]
    error: str = None
    
    def to_dict(self) -> Dict:
        return {
            'skill_name': self.skill_name,
            'success': self.success,
            'data': self.data,
            'signals': self.signals,
            'score': self.score,
            'confidence': self.confidence,
            'timestamp': self.timestamp,
            'data_source': self.data_source,
            'error': self.error
        }


class BaseSkill(ABC):
    """
    Skill 基类
    
    所有独立 Skill 必须实现:
    - name: Skill 名称
    - description: 功能描述
    - version: 版本号
    - execute(): 核心执行逻辑
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.created_at = datetime.now().isoformat()
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Skill 功能描述"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Skill 版本"""
        pass
    
    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """支持的市场类型"""
        pass
    
    @abstractmethod
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """
        执行 Skill 核心逻辑
        
        Args:
            input_data: 标准输入
            
        Returns:
            SkillOutput: 标准输出
        """
        pass
    
    def validate_input(self, input_data: SkillInput) -> bool:
        """验证输入"""
        if not input_data.symbol:
            return False
        
        if input_data.market not in self.supported_markets:
            return False
        
        return True
    
    def create_error_output(self, error_msg: str) -> SkillOutput:
        """创建错误输出"""
        return SkillOutput(
            skill_name=self.name,
            success=False,
            data={},
            signals=[],
            score=0,
            confidence=0,
            timestamp=datetime.now().isoformat(),
            data_source=[],
            error=error_msg
        )


class SkillRegistry:
    """Skill 注册表"""
    
    _skills = {}
    _loaded_modules = set()
    
    @classmethod
    def register(cls, skill_class: type):
        """注册 Skill"""
        instance = skill_class()
        cls._skills[instance.name] = instance
        return instance
    
    @classmethod
    def get(cls, skill_name: str) -> BaseSkill:
        """获取 Skill"""
        return cls._skills.get(skill_name)
    
    @classmethod
    def list_all(cls) -> List[str]:
        """列出所有 Skill"""
        return list(cls._skills.keys())
    
    @classmethod
    def execute(cls, skill_name: str, input_data: SkillInput) -> SkillOutput:
        """执行指定 Skill"""
        if not cls._skills:
            load_builtin_skills()
        
        skill = cls.get(skill_name)
        
        if not skill:
            return SkillOutput(
                skill_name=skill_name,
                success=False,
                data={},
                signals=[],
                score=0,
                confidence=0,
                timestamp=datetime.now().isoformat(),
                data_source=[],
                error=f'Skill not found: {skill_name}'
            )
        
        if not skill.validate_input(input_data):
            return skill.create_error_output('Invalid input')
        
        return skill.execute(input_data)


# 装饰器：自动注册 Skill
def register_skill(cls):
    """装饰器：自动注册 Skill"""
    SkillRegistry.register(cls)
    return cls


def load_builtin_skills(base_dir: str = None) -> List[str]:
    """
    加载仓库内置 Skills。

    这些目录包含连字符，不能作为常规 Python 包导入，因此使用文件路径加载。
    API/Agent 启动时调用一次即可完成自动注册。
    """
    base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
    modules = [
        ("crypto_skill_analyze", os.path.join("crypto-skill", "analyze.py")),
        ("stock_skill_analyze", os.path.join("stock-skill", "analyze.py")),
        ("forex_skill_analyze", os.path.join("forex-skill", "analyze.py")),
        ("signal_skill_detect", os.path.join("signal-skill", "detect.py")),
        ("report_skill_commentary", os.path.join("report-skill", "commentary.py")),
        ("onchain_skill_whale", os.path.join("onchain-skill", "whale.py")),
        ("stock_skill_enhanced_screener", os.path.join("stock-skill", "enhanced_screener.py")),
    ]
    
    loaded = []
    screener_module = None
    
    for module_name, relative_path in modules:
        if module_name in SkillRegistry._loaded_modules:
            continue
        
        path = os.path.join(base_dir, relative_path)
        if not os.path.exists(path):
            continue
        
        spec = importlib.util.spec_from_file_location(module_name, path)
        if not spec or not spec.loader:
            continue
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SkillRegistry._loaded_modules.add(module_name)
        loaded.append(module_name)
        
        if module_name == "stock_skill_enhanced_screener":
            screener_module = module
    
    return loaded


@register_skill
class EnhancedScreenerSkill(BaseSkill):
    """A股智能选股 Skill - Phase 3 增强版"""
    
    description = "A股智能选股：预设策略、技术面筛选、多因子评分"
    version = "2.0.0"
    supported_markets = ["stock"]
    
    def execute(self, input_data: SkillInput) -> SkillOutput:
        """执行选股"""
        params = input_data.params or {}
        
        # 动态加载 EnhancedScreener
        base_dir = os.path.dirname(os.path.abspath(__file__))
        screener_path = os.path.join(base_dir, "stock-skill", "enhanced_screener.py")
        
        spec = importlib.util.spec_from_file_location("enhanced_screener", screener_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        screener = module.EnhancedScreener()
        result = screener.screen(
            scope=params.get('scope', 'hs300'),
            strategy=params.get('strategy'),
            criteria=params.get('criteria'),
            technical_checks=params.get('technical_checks'),
            use_scoring=params.get('scoring', False),
            industry=params.get('industry'),
            top=params.get('top', 20),
        )
        
        return SkillOutput(
            skill_name=self.name,
            success=result.get('success', False),
            data=result,
            signals=[],
            score=result.get('filtered_stocks', 0),
            confidence=0.8 if result.get('success') else 0,
            timestamp=datetime.now().isoformat(),
            data_source=['akshare'],
            error=result.get('error')
        )
