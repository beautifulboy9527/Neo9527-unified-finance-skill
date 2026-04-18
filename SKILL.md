---
name: unified-finance-skill
description: >
  多维度金融分析系统 - Skills 生态架构
  
  核心能力:
  - 结构化报告 (8部分逻辑递进)
  - 数据来源标注 (情绪/监管/财务)
  - 打板筛选 (涨停板/强势股/连板)
  - 多因子信号叠加 (叠buff)
  - AI专业解读 (AI Commentary)
  - REST API 服务 (FastAPI)
  - 深度研报验证 (Phase 4/5/7)
  - 交易周期支持 (日内到长线)
  
  Skills 架构:
  - crypto-skill: 加密货币分析
  - stock-skill: 股票综合分析
  - signal-skill: 信号检测
  - onchain-skill: 链上数据
  
  触发: 股票分析、打板筛选、财务检测、估值计算、深度研报
version: 6.3.0
integration: full
tested: 2026-04-18
skills:
  - crypto-skill
  - stock-skill
  - signal-skill
  - onchain-skill
  - shared
  - report-skill
api: true
cli: true
---

# Neo9527 Unified Finance Skill - Skills 生态版

> 从单体工具到可组合的金融 AI 能力平台

## ✅ 测试状态

**最后测试**: 2026-04-18 11:30
**测试结果**: 全部通过 ✅

| 测试项 | 状态 |
|--------|------|
| 综合分析 (AAPL) | ✅ |
| 报告结构 (8部分) | ✅ |
| 数据来源标注 | ✅ |
| 打板筛选 | ✅ |
| 财务异常检测 | ✅ |
| 估值计算 | ✅ |
| 深度研报 | ✅ |
| CLI 命令 | ✅ |

---

## Skills 架构

```
skills/
├── base_skill.py           # 标准接口规范
├── crypto-skill/           # 加密货币分析
│   └── analyze.py
├── signal-skill/           # 信号检测
│   └── detect.py
├── report-skill/           # AI解读
│   └── commentary.py
└── onchain-skill/          # 链上数据
    └── whale.py
```

### 每个 Skill 特性

- ✅ ≤ 300行代码
- ✅ 标准输入输出
- ✅ 可独立调用
- ✅ 可组合编排
- ✅ 带 data_source 字段

---

## 快速开始

### 方式1: CLI

```bash
# 安装
pip install neo9527-finance-skill

# 分析
neo-finance analyze BTC-USD

# 信号
neo-finance signals BTC-USD

# K线
neo-finance kline BTC-USD --save

# 链上
neo-finance onchain BTC
```

### 方式2: Python API

```python
from skills.base_skill import SkillInput, SkillRegistry

# 执行分析
output = SkillRegistry.execute(
    'CryptoAnalysisSkill',
    SkillInput(symbol='BTC-USD', market='crypto')
)

print(f"Score: {output.score}/100")
print(f"Signals: {len(output.signals)}")
```

### 方式3: REST API

```bash
# 启动服务
uvicorn api.server:app --reload

# 调用
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"BTC-USD","market":"crypto"}'
```

---

## 核心 Skills

### 1. CryptoAnalysisSkill

**功能**: 多维度加密货币分析

**输入**:
```python
SkillInput(
    symbol='BTC-USD',
    market='crypto',
    timeframe='medium'
)
```

**输出**:
```python
SkillOutput(
    score=75,  # 0-100
    confidence=0.78,
    signals=[...],
    data={
        'market': {...},
        'technical': {...},
        'conclusion': {...}
    }
)
```

---

### 2. SignalDetectionSkill

**功能**: 多因子信号检测 + 分级

**信号分级**:
- S级: 强度≥10 + 置信度≥75%
- A级: 强度≥5 + 置信度≥60%
- B级: 强度 -5~5
- C级: 强度≤-5

**时间维度**:
- short: 1-7天
- medium: 1-3月
- long: 3月+

---

### 3. AICommentarySkill

**功能**: 专业分析师解读

**输出**:
- 标题
- 技术面总结
- 风险提示
- 操作建议
- 一句话总结

---

### 4. OnchainWhaleSkill

**功能**: 链上鲸鱼数据

**数据源**: DeFiLlama (免费)

**输出**:
- TVL 变化
- 协议排名
- 资金流信号

---

## FastAPI 服务

### 接口列表

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/analyze` | 综合分析 |
| POST | `/api/signals` | 信号检测 |
| POST | `/api/commentary` | AI解读 |
| GET | `/api/quick/{symbol}` | 快速分析 |
| GET | `/api/schema/openai` | OpenAI Schema |

### OpenAI Function Calling

```json
{
  "functions": [{
    "name": "analyze_crypto",
    "description": "Multi-dimensional crypto analysis",
    "parameters": {
      "symbol": "string",
      "market": "string",
      "timeframe": "string"
    }
  }]
}
```

---

## 数据来源

| 类型 | API | 状态 |
|------|-----|------|
| 市场数据 | CoinGecko | ✅ 免费 |
| 技术指标 | yfinance | ✅ 免费 |
| K线数据 | yfinance | ✅ 免费 |
| 链上数据 | Blockchain.com | ✅ 免费 |
| DeFi数据 | DeFiLlama | ✅ 免费 |
| 情绪指数 | alternative.me | ✅ 免费 |

---

## 依赖

```bash
pip install neo9527-finance-skill
```

---

## 项目结构

```
unified-finance-skill/
├── SKILL.md              # 本文件
├── README.md             # 完整文档
├── setup.py              # PyPI 配置
├── requirements.txt      # 依赖列表
│
├── skills/               # Skills 生态
│   ├── base_skill.py
│   ├── crypto-skill/
│   ├── signal-skill/
│   ├── report-skill/
│   └── onchain-skill/
│
├── api/                  # REST API
│   └── server.py
│
├── scripts/              # 核心模块
│   ├── finance.py        # CLI 入口
│   ├── features/
│   └── core/
│
└── docs/                 # 文档
    ├── PHASE-12-ROADMAP.md
    └── PHASE-13-ROADMAP.md
```

---

## 版本历史

- **v4.3**: Skills 生态架构 + FastAPI
- **v4.2**: K线图 + 鲸鱼数据 + CLI
- **v4.0**: 叠buff + 形态识别
- **v3.2**: 插件系统 + 回测

---

*Skills 生态 v4.3.0 - 可组合的金融 AI 平台 by Neo9527 🚀*
