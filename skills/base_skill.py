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
