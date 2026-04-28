#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Finance API - FastAPI 服务

轻量级 REST API，让 Skills 可被外部系统调用
"""

import sys
import os
import importlib.util
from typing import Optional

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入 Skills
from skills.base_skill import SkillInput, SkillRegistry, load_builtin_skills

APP_VERSION = "6.6.4"
load_builtin_skills()

# 创建 FastAPI 应用
app = FastAPI(
    title="Neo9527 Finance API",
    description="Multi-dimensional financial analysis with Skills",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置（允许前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class AnalyzeRequest(BaseModel):
    """分析请求"""
    symbol: str
    market: str = "crypto"
    timeframe: str = "medium"


class SignalRequest(BaseModel):
    """信号请求"""
    symbol: str
    market: str = "crypto"


class CommentaryRequest(BaseModel):
    """解读请求"""
    symbol: str
    market: str = "crypto"


def get_analysis_skill(market: str) -> str:
    """按市场选择分析 Skill。"""
    skill_map = {
        "crypto": "CryptoAnalysisSkill",
        "stock": "StockAnalysisSkill",
        "forex": "ForexAnalysisSkill",
    }
    if market not in skill_map:
        raise HTTPException(status_code=400, detail=f"Unsupported market: {market}")
    return skill_map[market]


def load_stock_module(file_name: str, module_name: str):
    """Load stock-skill modules whose parent directory contains a hyphen."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills",
        "stock-skill",
        file_name,
    )
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise HTTPException(status_code=500, detail=f"Cannot load module: {file_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ============ 健康检查 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Neo9527 Finance API",
        "version": APP_VERSION,
        "skills": SkillRegistry.list_all(),
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


# ============ 核心接口 ============

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    """
    综合分析
    
    按 market 调用对应分析 Skill 执行完整分析
    """
    try:
        skill_name = get_analysis_skill(request.market)
        output = SkillRegistry.execute(
            skill_name,
            SkillInput(
                symbol=request.symbol,
                market=request.market,
                timeframe=request.timeframe
            )
        )
        
        return JSONResponse(output.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/signals")
async def signals(request: SignalRequest):
    """
    信号检测
    
    调用 SignalDetectionSkill 执行信号分析
    """
    try:
        output = SkillRegistry.execute(
            'SignalDetectionSkill',
            SkillInput(
                symbol=request.symbol,
                market=request.market
            )
        )
        
        return JSONResponse(output.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/commentary")
async def commentary(request: CommentaryRequest):
    """
    AI 解读
    
    调用 AICommentarySkill 生成专业解读
    """
    try:
        output = SkillRegistry.execute(
            'AICommentarySkill',
            SkillInput(
                symbol=request.symbol,
                market=request.market
            )
        )
        
        return JSONResponse(output.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 便捷接口 ============

@app.get("/api/quick/{symbol}")
async def quick_analysis(
    symbol: str,
    market: str = Query("crypto", description="Market type"),
    skill: Optional[str] = Query(None, description="Skill to use; defaults by market")
):
    """
    快速分析（GET 请求）
    
    示例: GET /api/quick/BTC-USD?market=crypto
    """
    try:
        skill_name = skill or get_analysis_skill(market)
        output = SkillRegistry.execute(
            skill_name,
            SkillInput(symbol=symbol, market=market)
        )
        
        return JSONResponse(output.to_dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health/{symbol}")
async def symbol_health(
    symbol: str,
    market: str = Query("crypto", description="Market type")
):
    """
    健康度检查
    
    快速返回评分和信号
    """
    try:
        output = SkillRegistry.execute(
            'SignalDetectionSkill',
            SkillInput(symbol=symbol, market=market)
        )
        
        return {
            "symbol": symbol,
            "grade": output.data.get('grade', 'B'),
            "bias": output.data.get('bias', 'neutral'),
            "score": output.score,
            "confidence": output.confidence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/financial-health/{symbol}")
async def financial_health(symbol: str):
    """
    财报体检

    返回财务健康分、分项体检、风险旗标、数据完整度和证据摘要。
    """
    try:
        module = load_stock_module("financial_health.py", "stock_financial_health")
        result = module.analyze_financial_health(symbol)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Skills 管理 ============

@app.get("/api/skills")
async def list_skills():
    """列出所有可用 Skills"""
    return {
        "skills": [
            {
                "name": name,
                "description": SkillRegistry.get(name).description if SkillRegistry.get(name) else ""
            }
            for name in SkillRegistry.list_all()
        ]
    }


# ============ OpenAI Function Calling Schema ============

@app.get("/api/schema/openai")
async def openai_schema():
    """
    导出 OpenAI Function Calling Schema
    
    可直接用于 ChatGPT / LangChain
    """
    return {
        "functions": [
            {
                "name": "analyze_crypto",
                "description": "Multi-dimensional crypto analysis with K-line, whale data, and signals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol (e.g., BTC-USD, ETH-USD)"
                        },
                        "market": {
                            "type": "string",
                            "enum": ["crypto", "stock", "forex"],
                            "default": "crypto",
                            "description": "Market type"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["short", "medium", "long"],
                            "default": "medium",
                            "description": "Analysis timeframe"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "detect_signals",
                "description": "Multi-factor signal detection with S/A/B/C grading",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol"
                        },
                        "market": {
                            "type": "string",
                            "default": "crypto"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "generate_commentary",
                "description": "Generate professional analyst commentary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol"
                        },
                        "market": {
                            "type": "string",
                            "default": "crypto"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    }


# ============ LangChain 兼容接口 ============

@app.get("/api/langchain/toolkit")
async def langchain_toolkit():
    """
    LangChain Toolkit 配置
    
    返回可直接用于 LangChain 的配置
    """
    return {
        "toolkit_name": "neo9527_finance",
        "tools": [
            {
                "name": "analyze",
                "description": "Multi-dimensional financial analysis",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "market": {"type": "string", "default": "crypto"}
                    }
                }
            },
            {
                "name": "signals",
                "description": "Signal detection with grading",
                "args_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"}
                    }
                }
            }
        ],
        "usage": """
from langchain.agents import initialize_agent
from neo_finance.langchain import NeoFinanceToolkit

toolkit = NeoFinanceToolkit()
agent = initialize_agent(toolkit.get_tools(), llm)
agent.run("Analyze BTC-USD")
"""
    }


if __name__ == '__main__':
    import uvicorn
    
    print("=" * 60)
    print("Neo9527 Finance API Server")
    print("=" * 60)
    print(f"Version: {APP_VERSION}")
    print(f"Skills: {', '.join(SkillRegistry.list_all())}")
    print(f"Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
