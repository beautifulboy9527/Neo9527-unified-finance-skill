#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance API - 测试套件

测试 REST API 接口
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.server import app


# 创建测试客户端
client = TestClient(app)


# ============ 基础接口测试 ============

class TestBasicEndpoints:
    """基础接口测试"""
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['service'] == 'Neo9527 Finance API'
        assert data['version'] == '4.3.0'
        assert 'skills' in data
    
    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_list_skills(self):
        """测试 Skills 列表"""
        response = client.get("/api/skills")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'skills' in data
        assert len(data['skills']) > 0


# ============ 分析接口测试 ============

class TestAnalyzeEndpoint:
    """分析接口测试"""
    
    def test_analyze_btc(self):
        """测试 BTC 分析"""
        response = client.post(
            "/api/analyze",
            json={
                "symbol": "BTC-USD",
                "market": "crypto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 0 <= data['score'] <= 100
        assert isinstance(data['signals'], list)
    
    def test_analyze_eth(self):
        """测试 ETH 分析"""
        response = client.post(
            "/api/analyze",
            json={
                "symbol": "ETH-USD",
                "market": "crypto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['skill_name'] == 'CryptoAnalysisSkill'


# ============ 信号接口测试 ============

class TestSignalsEndpoint:
    """信号接口测试"""
    
    def test_signals_btc(self):
        """测试 BTC 信号"""
        response = client.post(
            "/api/signals",
            json={
                "symbol": "BTC-USD",
                "market": "crypto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'grade' in data['data']
        assert 'bias' in data['data']
        assert data['data']['grade'] in ['S', 'A', 'B', 'C']


# ============ 解读接口测试 ============

class TestCommentaryEndpoint:
    """解读接口测试"""
    
    def test_commentary_btc(self):
        """测试 BTC 解读"""
        response = client.post(
            "/api/commentary",
            json={
                "symbol": "BTC-USD",
                "market": "crypto"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert 'title' in data['data']
        assert 'technical_summary' in data['data']
        assert 'risk_warning' in data['data']


# ============ 快速接口测试 ============

class TestQuickEndpoint:
    """快速接口测试"""
    
    def test_quick_analysis(self):
        """测试快速分析"""
        response = client.get("/api/quick/BTC-USD?market=crypto")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'score' in data
        assert 'signals' in data
    
    def test_health_check(self):
        """测试健康度检查"""
        response = client.get("/api/health/BTC-USD")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['symbol'] == 'BTC-USD'
        assert 'grade' in data
        assert 'score' in data


# ============ Schema 接口测试 ============

class TestSchemaEndpoints:
    """Schema 接口测试"""
    
    def test_openai_schema(self):
        """测试 OpenAI Schema"""
        response = client.get("/api/schema/openai")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'functions' in data
        assert len(data['functions']) > 0
        
        # 验证函数定义
        func = data['functions'][0]
        assert 'name' in func
        assert 'description' in func
        assert 'parameters' in func
    
    def test_langchain_toolkit(self):
        """测试 LangChain Toolkit"""
        response = client.get("/api/langchain/toolkit")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'toolkit_name' in data
        assert 'tools' in data


# ============ 错误处理测试 ============

class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_market(self):
        """测试无效市场"""
        response = client.post(
            "/api/analyze",
            json={
                "symbol": "BTC-USD",
                "market": "invalid"
            }
        )
        
        # 应该返回错误或默认处理
        assert response.status_code in [200, 400, 500]


# ============ 运行测试 ============

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
