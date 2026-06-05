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
import math
from datetime import datetime


def _clean_nan(obj):
    """Recursively replace NaN/inf with None for JSON compliance."""
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean_nan(v) for v in obj]
    return obj


def safe_json(data):
    """Return JSONResponse with NaN values cleaned."""
    return JSONResponse(_clean_nan(data))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 导入 Skills
from skills.base_skill import SkillInput, SkillRegistry, load_builtin_skills

APP_VERSION = "6.6.7"
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


class WatchlistAlertRequest(BaseModel):
    """自选股预警请求"""
    symbols: list[str]


class ValuationWorkbenchRequest(BaseModel):
    """估值工作台参数"""
    methods: str = "all"
    discount_rate: Optional[float] = None
    terminal_growth: Optional[float] = None
    fcf_growth: Optional[float] = None
    peer_pe: Optional[float] = None
    peer_pb: Optional[float] = None
    margin_of_safety: Optional[float] = None
    current_price: Optional[float] = None
    eps: Optional[float] = None
    bps: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    free_cash_flow: Optional[float] = None
    shares_outstanding: Optional[float] = None
    total_debt: Optional[float] = None
    cash: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class FinancialHealthRequest(BaseModel):
    """外部财务字段体检参数"""
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    debt_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None
    receivable_growth: Optional[float] = None
    inventory_growth: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    net_income: Optional[float] = None


class ScreenRequest(BaseModel):
    """选股请求参数"""
    scope: str = "hs300"  # hs300/zz500/all/a50
    strategy: Optional[str] = None  # value/growth/dividend/garp/turnaround/defensive/quality
    technical_checks: Optional[list[str]] = None  # golden-cross/ma-bullish等
    scoring: bool = False  # 是否启用多因子评分
    industry: Optional[str] = None  # 行业筛选
    top: int = 20  # 返回TOP N
    pe_max: Optional[float] = None
    pb_max: Optional[float] = None
    roe_min: Optional[float] = None
    debt_max: Optional[float] = None
    margin_min: Optional[float] = None


class PriceBar(BaseModel):
    """外部传入的真实K线字段"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class StockReportRequest(BaseModel):
    """投资者HTML报告请求"""
    style: str = "kami"
    price_csv: Optional[str] = None
    price_rows: Optional[list[PriceBar]] = None
    strict_data: bool = True
    require_technical_data: bool = True
    live_data_check: bool = False
    enforce_freshness: bool = False
    max_price_age_days: int = 10
    timeframe: str = "日线"
    trend: Optional[str] = None
    business_summary: Optional[str] = None
    moat: Optional[str] = None
    industry: Optional[str] = None
    methods: str = "all"
    discount_rate: Optional[float] = None
    terminal_growth: Optional[float] = None
    fcf_growth: Optional[float] = None
    peer_pe: Optional[float] = None
    peer_pb: Optional[float] = None
    margin_of_safety: Optional[float] = None
    current_price: Optional[float] = None
    eps: Optional[float] = None
    bps: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    free_cash_flow: Optional[float] = None
    shares_outstanding: Optional[float] = None
    total_debt: Optional[float] = None
    cash: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    debt_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None
    receivable_growth: Optional[float] = None
    inventory_growth: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    net_income: Optional[float] = None


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


def _dump_model(model: BaseModel) -> dict:
    return model.model_dump(exclude_none=True) if hasattr(model, "model_dump") else model.dict(exclude_none=True)


def _build_stock_report_context(symbol: str, request: StockReportRequest) -> dict:
    from skills.shared import check_data_sources, stock_display_name

    health_module = load_stock_module("financial_health.py", "api_stock_financial_health")
    workbench_module = load_stock_module("valuation_workbench.py", "api_stock_valuation_workbench")
    risk_module = load_stock_module("risk_alerts.py", "api_stock_risk_alerts")
    collector_module = load_stock_module("stock_data_collector.py", "api_stock_data_collector")
    preflight_module = load_stock_module("report_preflight.py", "api_stock_report_preflight")

    payload = _dump_model(request)
    data_sources = check_data_sources(
        live=request.live_data_check,
        sample_symbol=symbol if str(symbol).isdigit() else "002050",
    )
    collected_data = collector_module.collect_stock_data(symbol)
    if request.price_csv:
        csv_data = collector_module.collect_price_csv(request.price_csv, symbol=symbol, timeframe=request.timeframe)
        if csv_data.get("technical_analysis"):
            collected_data["technical_analysis"] = csv_data["technical_analysis"]
        if csv_data.get("market_data", {}).get("price") is not None:
            collected_data.setdefault("market_data", {}).update(csv_data.get("market_data", {}))
            collected_data.setdefault("valuation_fields", {}).update(csv_data.get("valuation_fields", {}))
        collected_data.setdefault("warnings", []).extend(csv_data.get("warnings", []))
        collected_data.setdefault("sources", []).extend(csv_data.get("sources", []))
        collected_data["success"] = collected_data.get("success") or csv_data.get("success", False)
    if request.price_rows:
        rows = [_dump_model(row) for row in request.price_rows]
        row_data = collector_module.collect_price_rows(rows, symbol=symbol, timeframe=request.timeframe)
        if row_data.get("technical_analysis"):
            collected_data["technical_analysis"] = row_data["technical_analysis"]
        if row_data.get("market_data", {}).get("price") is not None:
            collected_data.setdefault("market_data", {}).update(row_data.get("market_data", {}))
            collected_data.setdefault("valuation_fields", {}).update(row_data.get("valuation_fields", {}))
        collected_data.setdefault("warnings", []).extend(row_data.get("warnings", []))
        collected_data.setdefault("sources", []).extend(row_data.get("sources", []))
        collected_data["success"] = collected_data.get("success") or row_data.get("success", False)

    data_sources["collection"] = {
        "success": collected_data.get("success", False),
        "warnings": collected_data.get("warnings", []),
        "sources": collected_data.get("sources", []),
    }

    health_keys = {
        "gross_margin", "net_margin", "roe", "debt_ratio", "revenue_growth",
        "profit_growth", "receivable_growth", "inventory_growth",
        "operating_cash_flow", "net_income",
    }
    valuation_keys = {
        "methods", "discount_rate", "terminal_growth", "fcf_growth", "peer_pe",
        "peer_pb", "margin_of_safety", "current_price", "eps", "bps", "pe",
        "pb", "free_cash_flow", "shares_outstanding", "total_debt", "cash",
        "industry",
    }
    health_params = {key: payload[key] for key in health_keys if key in payload}
    valuation_params = {key: payload[key] for key in valuation_keys if key in payload}

    merged_health_params = dict(collected_data.get("financial_fields", {}))
    merged_health_params.update(health_params)
    merged_valuation_params = dict(collected_data.get("valuation_fields", {}))
    merged_valuation_params.update(valuation_params)

    financial_health = health_module.analyze_financial_health(symbol, **merged_health_params)
    valuation_workbench = workbench_module.analyze_valuation_workbench(symbol, **merged_valuation_params)
    alerts_result = risk_module.analyze_watchlist_alerts([symbol])
    risk_alerts = alerts_result.get("items", [{}])[0] if alerts_result.get("items") else {}
    risk_alerts = preflight_module.reconcile_risk_alerts_with_financials(risk_alerts, financial_health)
    fundamental = {
        **collected_data.get("fundamental_analysis", {}),
        "industry": request.industry or collected_data.get("fundamental_analysis", {}).get("industry") or "行业信息暂未验证",
        "business_summary": request.business_summary or collected_data.get("fundamental_analysis", {}).get("business_summary"),
        "moat": request.moat,
    }
    technical = dict(collected_data.get("technical_analysis", {}))
    if request.trend:
        technical.update({"timeframe": request.timeframe, "trend": request.trend})

    preflight_collected = {
        **collected_data,
        "financial_fields": merged_health_params,
        "valuation_fields": merged_valuation_params,
    }
    if merged_valuation_params.get("current_price") is not None:
        preflight_collected.setdefault("market_data", {})
        preflight_collected["market_data"] = {
            **preflight_collected.get("market_data", {}),
            "price": merged_valuation_params.get("current_price"),
        }

    display_name = stock_display_name(symbol, collected_data.get("profile", {}))
    preflight = preflight_module.assess_report_readiness(
        symbol=symbol,
        display_name=display_name,
        collected_data=preflight_collected,
        financial_health=financial_health,
        valuation_workbench=valuation_workbench,
        technical_analysis=technical,
        fundamental_analysis=fundamental,
        mode="full",
        enforce_freshness=request.enforce_freshness,
        max_price_age_days=request.max_price_age_days,
    )
    data_sources["preflight"] = preflight
    return {
        "symbol": symbol,
        "display_name": display_name,
        "data_sources": data_sources,
        "collected_data": collected_data,
        "financial_health": financial_health,
        "valuation_workbench": valuation_workbench,
        "risk_alerts": risk_alerts,
        "fundamental_analysis": fundamental,
        "technical_analysis": technical,
        "preflight": preflight,
    }


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
        
        return safe_json(output.to_dict())
        
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
        
        return safe_json(output.to_dict())
        
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
        
        return safe_json(output.to_dict())
        
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
        
        return safe_json(output.to_dict())
        
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
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/financial-health/{symbol}")
async def financial_health_with_inputs(symbol: str, request: FinancialHealthRequest):
    """使用外部已验证财务字段执行财报体检"""
    try:
        module = load_stock_module("financial_health.py", "stock_financial_health")
        params = request.model_dump(exclude_none=True) if hasattr(request, "model_dump") else request.dict(exclude_none=True)
        result = module.analyze_financial_health(symbol, **params)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/risk-alerts/{symbol}")
async def risk_alerts(symbol: str):
    """单只股票风险预警"""
    try:
        module = load_stock_module("risk_alerts.py", "stock_risk_alerts")
        result = module.analyze_risk_alerts(symbol)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/watchlist/alerts")
async def watchlist_alerts(request: WatchlistAlertRequest):
    """自选股批量风险预警"""
    try:
        module = load_stock_module("risk_alerts.py", "stock_risk_alerts")
        result = module.analyze_watchlist_alerts(request.symbols)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/screen")
async def screen_stocks(request: ScreenRequest):
    """
    A股智能选股 (Phase 3 增强版)
    
    支持:
    - 预设策略: value/growth/dividend/garp/turnaround/defensive/quality
    - 技术面筛选: golden-cross/ma-bullish/volume-breakout/rsi-oversold/bollinger-squeeze/consolidation-breakout
    - 多因子评分: 估值/盈利/成长/安全/动量
    - 行业筛选
    
    示例:
    POST /api/screen {"scope": "hs300", "strategy": "value", "scoring": true, "top": 20}
    """
    try:
        module = load_stock_module("enhanced_screener.py", "stock_enhanced_screener")
        screener = module.EnhancedScreener()
        
        # 构建自定义条件
        criteria = {}
        if request.pe_max:
            criteria['pe_max'] = request.pe_max
        if request.pb_max:
            criteria['pb_max'] = request.pb_max
        if request.roe_min:
            criteria['roe_min'] = request.roe_min
        if request.debt_max:
            criteria['debt_ratio_max'] = request.debt_max
        if request.margin_min:
            criteria['net_margin_min'] = request.margin_min
        
        result = screener.screen(
            scope=request.scope,
            strategy=request.strategy,
            criteria=criteria if criteria else None,
            technical_checks=request.technical_checks,
            use_scoring=request.scoring,
            industry=request.industry,
            top=request.top,
        )
        
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screen/strategies")
async def list_screening_strategies():
    """列出所有预设选股策略"""
    try:
        module = load_stock_module("screening_strategies.py", "stock_screening_strategies")
        strategies = module.list_strategies()
        return JSONResponse({
            "success": True,
            "strategies": strategies,
            "count": len(strategies)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screen/technical-checks")
async def list_technical_checks():
    """列出所有技术面筛选条件"""
    try:
        module = load_stock_module("technical_screener.py", "stock_technical_screener")
        checks = module.list_technical_checks()
        return JSONResponse({
            "success": True,
            "checks": checks,
            "count": len(checks)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/valuation-workbench/{symbol}")
async def valuation_workbench(symbol: str, request: ValuationWorkbenchRequest):
    """情景估值工作台"""
    try:
        params = request.model_dump(exclude_none=True) if hasattr(request, "model_dump") else request.dict(exclude_none=True)
        module = load_stock_module("valuation_workbench.py", "stock_valuation_workbench")
        result = module.analyze_valuation_workbench(symbol, **params)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report/preflight/{symbol}")
async def report_preflight(symbol: str, request: StockReportRequest):
    """正式报告生成前的数据完整性检查"""
    try:
        context = _build_stock_report_context(symbol, request)
        return JSONResponse({
            "symbol": symbol,
            "display_name": context["display_name"],
            "preflight": context["preflight"],
            "data_source_status": context["data_sources"].get("status"),
            "collection": context["data_sources"].get("collection"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/report/html/{symbol}")
async def report_html(symbol: str, request: StockReportRequest):
    """生成投资者可读HTML报告；严格模式下核心数据不足则拒绝输出"""
    try:
        context = _build_stock_report_context(symbol, request)
        preflight = context["preflight"]
        if request.require_technical_data and not context["technical_analysis"].get("candles"):
            return JSONResponse(
                {
                    "success": False,
                    "symbol": symbol,
                    "reason": "没有取得可验证K线数据，无法展示技术面、支撑位和压力位。",
                    "preflight": preflight,
                },
                status_code=422,
            )
        if request.strict_data and not preflight.get("can_generate"):
            return JSONResponse(
                {
                    "success": False,
                    "symbol": symbol,
                    "reason": "核心数据不足，严格模式下不生成正式HTML报告。",
                    "preflight": preflight,
                },
                status_code=422,
            )

        if request.style == "apple":
            report_module = load_stock_module("apple_style_report.py", "api_apple_style_report")
            report_class = report_module.AppleStyleStockReport
        else:
            report_module = load_stock_module("kami_style_report.py", "api_kami_style_report")
            report_class = report_module.KamiStyleStockReport

        html_text = report_class().generate(
            symbol,
            display_name=context["display_name"],
            financial_health=context["financial_health"],
            valuation_workbench=context["valuation_workbench"],
            risk_alerts=context["risk_alerts"],
            technical_analysis=context["technical_analysis"],
            fundamental_analysis=context["fundamental_analysis"],
            data_sources=context["data_sources"],
        )
        return HTMLResponse(html_text)
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


# ============ Phase 4: 数据源稳定性 API ============

class DataSourceTestRequest(BaseModel):
    """数据源测试请求"""
    source: str = Field(default="akshare", description="数据源名称")
    test_scope: Optional[str] = Field(default="hs300", description="测试范围")


@app.get("/api/data-source/health")
async def get_data_source_health():
    """获取数据源健康报告"""
    try:
        module = load_stock_module("screener_data_source.py", "screener_data_source")
        manager = module.get_screener_data_manager()
        report = manager.get_health_report()
        
        return {
            "success": True,
            "health_report": report,
            "best_source": manager.get_best_source(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/data-source/status")
async def get_data_source_status():
    """获取当前可用数据源状态"""
    try:
        module = load_stock_module("screener_data_source.py", "screener_data_source")
        manager = module.get_screener_data_manager()
        
        available = [s for s, h in manager.health_checker.items() if h.is_available]
        unavailable = [s for s, h in manager.health_checker.items() if not h.is_available]
        
        return {
            "success": True,
            "available_sources": available,
            "unavailable_sources": unavailable,
            "best_source": manager.get_best_source(),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/data-source/test")
async def test_data_source(request: DataSourceTestRequest):
    """测试指定数据源"""
    try:
        module = load_stock_module("screener_data_source.py", "screener_data_source")
        manager = module.get_screener_data_manager()
        
        import time
        test_scope = request.test_scope or "hs300"
        start_time = time.time()
        
        try:
            stocks = manager.get_stock_pool_with_fallback(test_scope)
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "source": request.source,
                "test_scope": test_scope,
                "stocks_count": len(stocks),
                "response_time": f"{response_time:.2f}s",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "source": request.source,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ Phase 5: 产品化功能 API ============

# 自选股管理请求模型
class WatchlistAddRequest(BaseModel):
    """添加自选股请求"""
    symbol: str
    target: Optional[float] = None
    stop: Optional[float] = None
    notes: Optional[str] = ""
    group: Optional[str] = "默认"
    priority: Optional[str] = "中"


class WatchlistUpdateRequest(BaseModel):
    """更新自选股请求"""
    id: int
    target: Optional[float] = None
    stop: Optional[float] = None
    notes: Optional[str] = None
    group: Optional[str] = None
    priority: Optional[str] = None
    enabled: Optional[bool] = None


class WatchlistRemoveRequest(BaseModel):
    """移除自选股请求"""
    id: int


# 组合分析请求模型
class PortfolioAnalyzeRequest(BaseModel):
    """组合分析请求"""
    symbols: list[str]
    weights: Optional[list[float]] = None
    days: Optional[int] = 365


class PortfolioOptimizeRequest(BaseModel):
    """组合优化请求"""
    symbols: list[str]
    method: Optional[str] = "max_sharpe"  # max_sharpe, min_volatility, risk_parity
    days: Optional[int] = 365


class PortfolioKellyRequest(BaseModel):
    """Kelly仓位请求"""
    symbol: str
    days: Optional[int] = 365


# ============ 自选股管理 API ============

@app.get("/api/watchlist")
async def list_watchlist(
    group: Optional[str] = None,
    priority: Optional[str] = None,
    enabled_only: Optional[bool] = True
):
    """
    列出自选股
    
    Args:
        group: 按分组筛选
        priority: 按优先级筛选
        enabled_only: 只返回启用的
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('list', group=group, priority=priority, enabled_only=enabled_only)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/watchlist")
async def add_watchlist(request: WatchlistAddRequest):
    """
    添加自选股
    
    Args:
        symbol: 股票代码
        target: 目标价
        stop: 止损价
        notes: 备注
        group: 分组
        priority: 优先级
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('add',
            symbol=request.symbol,
            target=request.target,
            stop=request.stop,
            notes=request.notes or "",
            group=request.group or "默认",
            priority=request.priority or "中"
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/watchlist/{item_id}")
async def remove_watchlist(item_id: int):
    """
    移除自选股
    
    Args:
        item_id: 自选股ID
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('remove', id=item_id)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.patch("/api/watchlist/{item_id}")
async def update_watchlist(item_id: int, request: WatchlistUpdateRequest):
    """
    更新自选股
    
    Args:
        item_id: 自选股ID
        request: 更新参数
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('update',
            id=item_id,
            target=request.target,
            stop=request.stop,
            notes=request.notes,
            group=request.group,
            priority=request.priority,
            enabled=request.enabled
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/watchlist/check")
async def check_watchlist():
    """
    检查自选股触发条件
    
    检查所有启用自选股的目标价/止损价触发情况
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('check')
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/watchlist/summary")
async def watchlist_summary():
    """
    自选股统计报告
    
    返回总数、分组分布、优先级分布、监控设置率等
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('summary')
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/watchlist/groups")
async def list_watchlist_groups():
    """
    列出分组
    
    返回所有分组及各分组股票数量
    """
    try:
        module = load_stock_module("watchlist_manager.py", "watchlist_manager")
        skill = module.WatchlistSkill()
        result = skill.execute('list_groups')
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ 组合分析 API ============

@app.post("/api/portfolio/analyze")
async def analyze_portfolio(request: PortfolioAnalyzeRequest):
    """
    组合风险分析
    
    Args:
        symbols: 股票代码列表
        weights: 权重列表 (None = 等权)
        days: 历史天数
    
    Returns:
        VaR/CVaR、Sharpe、最大回撤、相关性矩阵、健康度评分
    """
    try:
        module = load_stock_module("portfolio_skill.py", "portfolio_skill")
        skill = module.PortfolioSkill()
        result = skill.execute('analyze',
            symbols=request.symbols,
            weights=request.weights,
            days=request.days or 365
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizeRequest):
    """
    组合优化
    
    Args:
        symbols: 股票代码列表
        method: 优化方法 (max_sharpe / min_volatility / risk_parity)
        days: 历史天数
    
    Returns:
        最优权重分配、预期收益、波动率
    """
    try:
        module = load_stock_module("portfolio_skill.py", "portfolio_skill")
        skill = module.PortfolioSkill()
        result = skill.execute('optimize',
            symbols=request.symbols,
            method=request.method or "max_sharpe",
            days=request.days or 365
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/portfolio/kelly")
async def calculate_kelly(request: PortfolioKellyRequest):
    """
    Kelly仓位计算
    
    Args:
        symbol: 股票代码
        days: 历史天数
    
    Returns:
        胜率、盈亏比、Kelly%仓位建议
    """
    try:
        module = load_stock_module("portfolio_skill.py", "portfolio_skill")
        skill = module.PortfolioSkill()
        result = skill.execute('kelly',
            symbol=request.symbol,
            days=request.days or 365
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/portfolio/warnings")
async def check_portfolio_warnings(request: PortfolioAnalyzeRequest):
    """
    组合风险预警
    
    Args:
        symbols: 股票代码列表
        weights: 权重列表
        days: 历史天数
    
    Returns:
        风险预警列表 (集中度过高、相关性过高等)
    """
    try:
        module = load_stock_module("portfolio_skill.py", "portfolio_skill")
        skill = module.PortfolioSkill()
        result = skill.execute('warnings',
            symbols=request.symbols,
            weights=request.weights,
            days=request.days or 365
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}




# ============ Crypto / Forex 专用端点 ============

@app.get("/api/crypto/quote/{symbol}")
async def crypto_quote(symbol: str, exchange: str = Query(default="binance")):
    """
    加密货币实时行情

    Args:
        symbol: 交易对 (如 BTC/USDT)
        exchange: 交易所 (默认 binance)
    """
    try:
        from skills.crypto_skill.crypto import CryptoAnalyzer
        analyzer = CryptoAnalyzer(exchange)
        result = analyzer.get_quote(symbol)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crypto/kline/{symbol}")
async def crypto_kline(
    symbol: str,
    timeframe: str = Query(default="1d"),
    limit: int = Query(default=30),
    exchange: str = Query(default="binance")
):
    """
    加密货币K线数据

    Args:
        symbol: 交易对
        timeframe: 时间级别 (1m/5m/1h/1d)
        limit: 数据条数
        exchange: 交易所
    """
    try:
        from skills.crypto_skill.crypto import CryptoAnalyzer
        analyzer = CryptoAnalyzer(exchange)
        result = analyzer.get_kline(symbol, timeframe, limit)
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/crypto/trending")
async def crypto_trending(exchange: str = Query(default="binance")):
    """热门加密货币"""
    try:
        from skills.crypto_skill.crypto import CryptoAnalyzer
        analyzer = CryptoAnalyzer(exchange)
        result = analyzer.get_trending()
        return safe_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/forex/quote/{pair}")
async def forex_quote(pair: str = "USD/CNY"):
    """
    外汇汇率查询

    Args:
        pair: 货币对 (如 USD/CNY, EUR/USD)
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "forex_analyze",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "skills", "forex-skill", "analyze.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        skill = module.ForexAnalysisSkill()
        from skills.base_skill import SkillInput
        output = skill.execute(SkillInput(symbol=pair, market="forex"))
        return safe_json(output.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/forex/analyze/{pair}")
async def forex_analyze(pair: str = "USD/CNY", days: int = Query(default=60)):
    """
    外汇技术分析

    Args:
        pair: 货币对
        days: 分析天数
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "forex_analyze",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "skills", "forex-skill", "analyze.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        skill = module.ForexAnalysisSkill()
        from skills.base_skill import SkillInput
        output = skill.execute(SkillInput(symbol=pair, market="forex", params={"days": days}))
        return safe_json(output.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
