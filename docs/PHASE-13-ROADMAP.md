# Phase 13 开发计划

**版本目标**: v5.0 - AI Agent 原生 + 工作流自动化

---

## 📋 P0 任务 (今天完成)

### 1. GitHub Release 创建 ✅

已完成:
- ✅ 创建 Tag v4.2.0
- ✅ 推送到 GitHub

待完成:
- [ ] 在 GitHub 页面创建正式 Release
- [ ] 添加 Release Notes

### 2. PyPI 正式发布

**执行命令**:
```bash
# 构建
python setup.py sdist bdist_wheel

# 检查
twine check dist/*

# 上传
twine upload dist/*
```

**发布后验证**:
```bash
pip install neo9527-finance-skill
neo-finance --version
```

---

## 📋 P1 任务 (本周完成)

### 1. 测试覆盖 (Phase 12.4)

#### API Mocking 策略
```python
# tests/conftest.py
import pytest
import responses

@pytest.fixture
def mock_coingecko():
    """Mock CoinGecko API"""
    responses.add(
        responses.GET,
        'https://api.coingecko.com/api/v3/coins/bitcoin',
        json={'market_data': {...}},
        status=200
    )
```

#### 核心测试用例
```python
# tests/test_buff_logic.py
def test_buff_calculation():
    """测试叠buff逻辑"""
    signals = [
        {'strength': 5},  # 趋势
        {'strength': -2}, # RSI超买
        {'strength': 3},  # MACD
        {'strength': 4},  # 双底
    ]
    total = sum(s['strength'] for s in signals)
    assert total == 10

def test_pattern_detection():
    """测试形态识别"""
    result = analyze_complete('BTC-USD')
    patterns = result['patterns']
    
    assert 'trend' in patterns
    assert patterns['trend'] in ['uptrend', 'downtrend', 'sideways']
    
    if patterns.get('double_bottom'):
        assert 'double_bottom_desc' in patterns
```

#### pytest 配置
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=scripts --cov-report=html
```

**目标覆盖率**: 85%+

---

### 2. CI/CD 配置

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=scripts tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

#### PyPI 自动发布
```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install build tools
      run: |
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

---

### 3. 缓存降级策略

```python
# features/api_fallback.py
class APIFallback:
    """API 熔断/降级机制"""
    
    def __init__(self):
        self.failure_count = {}
        self.last_success = {}
        self.circuit_breaker_threshold = 3
    
    def get_with_fallback(
        self,
        primary_url: str,
        fallback_url: str = None,
        cache_key: str = None
    ):
        """带降级的API调用"""
        
        # 检查熔断器
        if self._is_circuit_open(primary_url):
            return self._use_cache_or_fallback(
                fallback_url, cache_key
            )
        
        try:
            # 尝试主API
            result = self._call_api(primary_url)
            self._record_success(primary_url)
            return result
            
        except Exception as e:
            self._record_failure(primary_url)
            
            # 尝试备用API
            if fallback_url:
                try:
                    result = self._call_api(fallback_url)
                    result['data_source'] += ' (fallback)'
                    result['is_realtime'] = False
                    return result
                except:
                    pass
            
            # 使用缓存
            return self._use_cache_or_fallback(
                None, cache_key
            )
    
    def _is_circuit_open(self, url: str) -> bool:
        """检查熔断器是否打开"""
        failures = self.failure_count.get(url, 0)
        return failures >= self.circuit_breaker_threshold
    
    def _record_failure(self, url: str):
        """记录失败"""
        self.failure_count[url] = self.failure_count.get(url, 0) + 1
    
    def _record_success(self, url: str):
        """记录成功"""
        self.failure_count[url] = 0
        self.last_success[url] = datetime.now()
```

---

## 🚀 Phase 13: AI Agent 原生接入

### 1. OpenAI Function Calling Schema 导出

```python
# features/agent_schema.py
def export_openai_schema() -> dict:
    """导出 OpenAI Function Calling Schema"""
    
    return {
        "name": "neo_finance_analyze",
        "description": "Multi-dimensional financial analysis with K-line charts, whale data, and signal stacking",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading symbol (e.g., BTC-USD, AAPL)"
                },
                "action": {
                    "type": "string",
                    "enum": ["analyze", "signals", "report", "kline", "onchain"],
                    "description": "Analysis action to perform"
                },
                "period": {
                    "type": "string",
                    "enum": ["short", "medium", "long"],
                    "default": "medium"
                },
                "format": {
                    "type": "string",
                    "enum": ["html", "markdown", "json"],
                    "default": "json"
                }
            },
            "required": ["symbol", "action"]
        }
    }

# CLI 命令
# python finance.py export-schema > schema.json
```

---

### 2. FastAPI 轻量服务

```python
# api/server.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="Neo9527 Finance API",
    version="4.2.0",
    description="Multi-dimensional financial analysis API"
)

@app.get("/")
async def root():
    return {"service": "Neo9527 Finance API", "version": "4.2.0"}

@app.get("/analyze/{symbol}")
async def analyze(symbol: str):
    """快速分析"""
    from features.complete_crypto_analyzer import analyze_complete
    result = analyze_complete(symbol)
    return JSONResponse(result['conclusion'])

@app.get("/signals/{symbol}")
async def signals(symbol: str):
    """信号检测"""
    from features.complete_crypto_analyzer import analyze_complete
    result = analyze_complete(symbol)
    return JSONResponse({"signals": result['signals']})

@app.get("/report/{symbol}")
async def report(symbol: str, format: str = "html"):
    """生成报告"""
    from features.report_generator_v4 import generate_crypto_report_v4
    path = generate_crypto_report_v4(symbol)
    
    if format == "html":
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    else:
        return {"report_path": path}

# 启动: uvicorn api.server:app --reload
```

**Docker 化**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt fastapi uvicorn

COPY scripts/ ./scripts/
COPY api/ ./api/

EXPOSE 8000
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. LangChain Toolkit 集成

```python
# langchain/toolkit.py
from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field

class NeoFinanceInput(BaseModel):
    """Neo Finance 工具输入"""
    symbol: str = Field(description="Trading symbol")
    action: str = Field(default="analyze", description="Action: analyze, signals, report")

class NeoFinanceToolkit(BaseTool):
    """Neo9527 Finance Toolkit for LangChain"""
    
    name = "neo_finance"
    description = "Multi-dimensional financial analysis with K-line, whale data, and signals"
    args_schema: Type[BaseModel] = NeoFinanceInput
    
    def _run(self, symbol: str, action: str = "analyze") -> str:
        from features.complete_crypto_analyzer import analyze_complete
        
        result = analyze_complete(symbol)
        
        if action == "analyze":
            conclusion = result['conclusion']
            return f"""
            分析结果:
            - 评分: {conclusion['score']}/100
            - 决策: {conclusion['decision']}
            - 置信度: {conclusion['confidence']}%
            - 信号: {conclusion['signals_count']}
            """
        elif action == "signals":
            signals = result['signals']
            bullish = [s for s in signals if s['strength'] > 0]
            bearish = [s for s in signals if s['strength'] < 0]
            
            return f"""
            信号汇总:
            - 看涨: {len(bullish)} 项
            - 看跌: {len(bearish)} 项
            - 总强度: {sum(s['strength'] for s in signals):+d}
            """
        
        return str(result)
    
    async def _arun(self, symbol: str, action: str = "analyze"):
        return self._run(symbol, action)

# 使用示例
# from neo_finance.langchain import NeoFinanceToolkit
# from langchain.agents import initialize_agent
# 
# toolkit = NeoFinanceToolkit()
# agent = initialize_agent([toolkit], llm, agent="zero-shot-react-description")
# agent.run("分析 BTC-USD 的投资信号")
```

---

### 4. 多智能体对抗辩论

```python
# features/multi_agent_debate.py
class AnalystAgent:
    """分析师智能体"""
    
    def __init__(self, role: str, focus: list):
        self.role = role
        self.focus = focus  # 关注维度
    
    def analyze(self, data: dict) -> str:
        """基于关注维度生成观点"""
        points = []
        
        for dimension in self.focus:
            if dimension == 'onchain':
                whale = data.get('whale', {})
                if whale.get('net_flow', 0) > 0:
                    points.append(f"鲸鱼净流入 {whale['net_flow']:+,}，累积信号看涨")
            
            elif dimension == 'technical':
                patterns = data.get('patterns', {})
                if patterns.get('trend') == 'uptrend':
                    points.append("技术面多头排列，趋势向上")
                
                rsi = data.get('indicators', {}).get('rsi', 50)
                if rsi > 70:
                    points.append(f"RSI {rsi:.1f} 超买，短期回调风险")
        
        return "\n".join(points)

class DebateEngine:
    """辩论引擎"""
    
    def __init__(self):
        self.bull_analyst = AnalystAgent(
            role="看多分析师",
            focus=['onchain', 'defi', 'sentiment']
        )
        self.bear_analyst = AnalystAgent(
            role="风控专员",
            focus=['technical', 'risk']
        )
    
    def debate(self, symbol: str) -> dict:
        """生成辩论报告"""
        from features.complete_crypto_analyzer import analyze_complete
        
        data = analyze_complete(symbol)
        
        bull_view = self.bull_analyst.analyze(data)
        bear_view = self.bear_analyst.analyze(data)
        
        conclusion = data['conclusion']
        
        return {
            'symbol': symbol,
            'bull_view': bull_view,
            'bear_view': bear_view,
            'final_decision': conclusion['decision'],
            'confidence': conclusion['confidence'],
            'score': conclusion['score']
        }
    
    def generate_debate_html(self, debate_result: dict) -> str:
        """生成辩论 HTML"""
        return f"""
        <div class="debate-section">
            <h2>🤔 多空辩论</h2>
            
            <div class="bull-view" style="background: #e8f5e9; padding: 20px; border-radius: 10px;">
                <h3>📈 看多分析师观点</h3>
                <p>{debate_result['bull_view']}</p>
            </div>
            
            <div class="bear-view" style="background: #ffebee; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h3>📉 风控专员观点</h3>
                <p>{debate_result['bear_view']}</p>
            </div>
            
            <div class="final-decision" style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h3>⚖️ 最终决策</h3>
                <p><strong>{debate_result['final_decision']}</strong> - 置信度 {debate_result['confidence']}%</p>
                <p>综合评分: {debate_result['score']}/100</p>
            </div>
        </div>
        """

# 使用
# from features.multi_agent_debate import DebateEngine
# engine = DebateEngine()
# result = engine.debate('BTC-USD')
# html = engine.generate_debate_html(result)
```

---

## 📅 时间表

### Week 1 (2026-04-17 ~ 04-23)
- [x] Day 1: GitHub Release 创建
- [ ] Day 1: PyPI 发布
- [ ] Day 2-3: pytest 测试覆盖
- [ ] Day 4: CI/CD 配置
- [ ] Day 5: API 降级策略

### Week 2 (2026-04-24 ~ 04-30)
- [ ] Day 1-2: OpenAI Schema 导出
- [ ] Day 3: FastAPI 服务
- [ ] Day 4: LangChain Toolkit
- [ ] Day 5: 多智能体辩论

### Week 3 (2026-05-01 ~ 05-07)
- [ ] 文档完善
- [ ] 示例代码
- [ ] 社区发布

---

## 🎯 成功指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 代码行数 | 6,200 | 7,000 |
| 测试覆盖率 | 0% | 85% |
| PyPI 下载量 | 0 | 500+ |
| GitHub Stars | 1 | 100+ |
| 集成平台 | 0 | 3+ |

---

## 📝 集成平台目标

- [ ] LangChain Hub
- [ ] n8n Workflow
- [ ] Zapier
- [ ] Make.com

---

**创建时间**: 2026-04-17  
**状态**: 📝 规划中
