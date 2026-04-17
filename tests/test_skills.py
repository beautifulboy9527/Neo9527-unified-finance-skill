#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance Skills - 测试套件

覆盖:
- Skills 基础接口
- 各独立 Skill
- API 接口
"""

import pytest
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.base_skill import (
    BaseSkill,
    SkillInput,
    SkillOutput,
    SkillRegistry
)


# ============ 基础接口测试 ============

class TestSkillInput:
    """SkillInput 测试"""
    
    def test_create_input(self):
        """测试创建输入"""
        input_data = SkillInput(
            symbol='BTC-USD',
            market='crypto'
        )
        
        assert input_data.symbol == 'BTC-USD'
        assert input_data.market == 'crypto'
        assert input_data.timeframe == 'medium'
    
    def test_to_dict(self):
        """测试转换为字典"""
        input_data = SkillInput(
            symbol='ETH-USD',
            market='crypto',
            timeframe='short'
        )
        
        result = input_data.to_dict()
        
        assert result['symbol'] == 'ETH-USD'
        assert result['market'] == 'crypto'
        assert result['timeframe'] == 'short'


class TestSkillOutput:
    """SkillOutput 测试"""
    
    def test_create_output(self):
        """测试创建输出"""
        output = SkillOutput(
            skill_name='TestSkill',
            success=True,
            data={'test': 'data'},
            signals=[],
            score=75,
            confidence=0.8,
            timestamp='2026-04-17',
            data_source=['test']
        )
        
        assert output.skill_name == 'TestSkill'
        assert output.success is True
        assert output.score == 75
        assert output.confidence == 0.8
    
    def test_to_dict(self):
        """测试转换为字典"""
        output = SkillOutput(
            skill_name='TestSkill',
            success=True,
            data={},
            signals=[],
            score=50,
            confidence=0.5,
            timestamp='2026-04-17',
            data_source=[]
        )
        
        result = output.to_dict()
        
        assert isinstance(result, dict)
        assert result['skill_name'] == 'TestSkill'


class TestSkillRegistry:
    """SkillRegistry 测试"""
    
    def test_list_skills(self):
        """测试列出 Skills"""
        skills = SkillRegistry.list_all()
        
        assert isinstance(skills, list)
        assert 'CryptoAnalysisSkill' in skills
        assert 'SignalDetectionSkill' in skills
        assert 'AICommentarySkill' in skills
    
    def test_get_skill(self):
        """测试获取 Skill"""
        skill = SkillRegistry.get('CryptoAnalysisSkill')
        
        assert skill is not None
        assert skill.name == 'CryptoAnalysisSkill'
    
    def test_execute_skill(self):
        """测试执行 Skill"""
        output = SkillRegistry.execute(
            'CryptoAnalysisSkill',
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert output is not None
        assert output.skill_name == 'CryptoAnalysisSkill'
        assert isinstance(output.success, bool)


# ============ CryptoAnalysisSkill 测试 ============

class TestCryptoAnalysisSkill:
    """CryptoAnalysisSkill 测试"""
    
    @pytest.fixture
    def skill(self):
        """获取 Skill 实例"""
        return SkillRegistry.get('CryptoAnalysisSkill')
    
    def test_skill_properties(self, skill):
        """测试 Skill 属性"""
        assert skill.name == 'CryptoAnalysisSkill'
        assert skill.version == '1.0.0'
        assert 'crypto' in skill.supported_markets
    
    def test_execute_btc(self, skill):
        """测试 BTC 分析"""
        input_data = SkillInput(
            symbol='BTC-USD',
            market='crypto'
        )
        
        output = skill.execute(input_data)
        
        assert output.skill_name == 'CryptoAnalysisSkill'
        assert 0 <= output.score <= 100
        assert 0 <= output.confidence <= 1
    
    def test_execute_eth(self, skill):
        """测试 ETH 分析"""
        input_data = SkillInput(
            symbol='ETH-USD',
            market='crypto'
        )
        
        output = skill.execute(input_data)
        
        assert output.success is True
        assert isinstance(output.signals, list)


# ============ SignalDetectionSkill 测试 ============

class TestSignalDetectionSkill:
    """SignalDetectionSkill 测试"""
    
    @pytest.fixture
    def skill(self):
        """获取 Skill 实例"""
        return SkillRegistry.get('SignalDetectionSkill')
    
    def test_skill_properties(self, skill):
        """测试 Skill 属性"""
        assert skill.name == 'SignalDetectionSkill'
        assert 'crypto' in skill.supported_markets
        assert 'stock' in skill.supported_markets
    
    def test_grade_calculation(self, skill):
        """测试信号分级"""
        # S级
        grade, bias = skill._calculate_grade(15, 5, 1, 80)
        assert grade.value == 'S'
        
        # A级
        grade, bias = skill._calculate_grade(8, 3, 1, 70)
        assert grade.value == 'A'
        
        # B级
        grade, bias = skill._calculate_grade(2, 2, 2, 50)
        assert grade.value == 'B'
        
        # C级
        grade, bias = skill._calculate_grade(-8, 1, 5, 30)
        assert grade.value == 'C'
    
    def test_execute_signals(self, skill):
        """测试信号检测"""
        output = skill.execute(
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert output.success is True
        assert 'grade' in output.data
        assert 'bias' in output.data
        assert output.data['grade'] in ['S', 'A', 'B', 'C']


# ============ AICommentarySkill 测试 ============

class TestAICommentarySkill:
    """AICommentarySkill 测试"""
    
    @pytest.fixture
    def skill(self):
        """获取 Skill 实例"""
        return SkillRegistry.get('AICommentarySkill')
    
    def test_skill_properties(self, skill):
        """测试 Skill 属性"""
        assert skill.name == 'AICommentarySkill'
        assert skill.version == '1.0.0'
    
    def test_generate_title(self, skill):
        """测试标题生成"""
        result = {
            'symbol': 'BTC-USD',
            'conclusion': {'score': 75, 'decision': 'BUY'}
        }
        
        title = skill._generate_title(result)
        
        assert 'BTC-USD' in title
        assert '75' in title
    
    def test_execute_commentary(self, skill):
        """测试解读生成"""
        output = skill.execute(
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert output.success is True
        assert 'title' in output.data
        assert 'technical_summary' in output.data
        assert 'risk_warning' in output.data
        assert 'action_advice' in output.data
        assert 'one_sentence' in output.data


# ============ 集成测试 ============

class TestIntegration:
    """集成测试"""
    
    def test_full_analysis_pipeline(self):
        """测试完整分析流程"""
        # 1. 分析
        analyze_output = SkillRegistry.execute(
            'CryptoAnalysisSkill',
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert analyze_output.success is True
        
        # 2. 信号检测
        signal_output = SkillRegistry.execute(
            'SignalDetectionSkill',
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert signal_output.success is True
        assert signal_output.data['grade'] in ['S', 'A', 'B', 'C']
        
        # 3. AI解读
        commentary_output = SkillRegistry.execute(
            'AICommentarySkill',
            SkillInput(symbol='BTC-USD', market='crypto')
        )
        
        assert commentary_output.success is True
        assert len(commentary_output.data['one_sentence']) > 0


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
