# Phase 3: 选股器增强

## 目标

将选股器从基础的条件过滤升级为多维度智能选股系统，支持预设策略、技术面筛选、多因子评分。

## 功能清单

### 3.1 预设策略

| 策略 | 说明 | 核心条件 |
|------|------|----------|
| 价值投资 | 低估值+高ROE | PE<20, PB<3, ROE>15% |
| 成长股 | 高增长+合理估值 | 收益增长>20%, PE<40 |
| 高股息 | 稳定分红 | 股息率>3%, 连续3年分红 |
| GARP | 成长+价值平衡 | PEG<1, ROE>12% |
| 困境反转 | 业绩拐点 | 近4季度利润环比改善 |
| 防御型 | 低波动+高现金流 | Beta<0.8, 经营现金流/净利润>1 |

### 3.2 技术面筛选

| 条件 | 说明 | 优先级 |
|------|------|--------|
| 均线多头排列 | MA5>MA10>MA20>MA60 | P1 |
| MACD金叉 | DIF上穿DEA | P1 |
| RSI超卖反弹 | RSI从<30回升 | P2 |
| 成交量放大 | 近5日量>20日均量1.5倍 | P2 |
| 突破盘整 | 价格突破近20日高点 | P2 |
| 布林带收口 | 带宽<10%，准备突破 | P3 |

### 3.3 多因子评分

| 因子类别 | 权重 | 包含指标 |
|----------|------|----------|
| 估值因子 | 25% | PE/PB/PS/PEG |
| 盈利因子 | 25% | ROE/ROA/毛利率/净利率 |
| 成长因子 | 20% | 收益增长/利润增长/营收增长 |
| 质量因子 | 15% | 负债率/现金流/利息保障 |
| 动量因子 | 15% | 近1月涨幅/相对强弱 |

### 3.4 行业筛选

- 支持按行业/板块筛选
- 行业内排名（百分位）
- 行业轮动信号

## CLI 命令

```bash
# 预设策略选股
python finance.py screen --strategy value        # 价值投资
python finance.py screen --strategy growth       # 成长股
python finance.py screen --strategy dividend     # 高股息
python finance.py screen --strategy garp         # GARP
python finance.py screen --strategy turnaround   # 困境反转
python finance.py screen --strategy defensive    # 防御型

# 技术面选股
python finance.py screen --technical golden-cross    # MACD金叉
python finance.py screen --technical ma-bullish      # 均线多头
python finance.py screen --technical volume-breakout # 放量突破

# 多因子评分
python finance.py screen --scoring --top 20          # 按综合评分排序TOP20

# 行业筛选
python finance.py screen --industry 银行 --top 10    # 银行板块TOP10

# 组合条件
python finance.py screen --strategy value --technical golden-cross --top 10
```

## API 端点

```
POST /api/screen
{
  "scope": "hs300",
  "strategy": "value",
  "technical": ["golden-cross", "ma-bullish"],
  "scoring": true,
  "top": 20
}
```

## 核心文件

- `skills/stock-skill/screener.py` - 增强选股器
- `skills/stock-skill/screening_strategies.py` - 预设策略
- `skills/stock-skill/technical_screener.py` - 技术面筛选
- `skills/stock-skill/scoring_engine.py` - 多因子评分

## 进度

- [x] Phase 1: 增强技术分析 (VWAP/斐波那契/缠论/K线形态/趋势线/ADX)
- [x] Phase 2: 财报预测与回顾
- [x] Phase 3: 选股器增强 ✅ **2026-05-11 完成**
  - [x] 预设策略 (7种: value/growth/dividend/garp/turnaround/defensive/quality)
  - [x] 技术面筛选 (6种: golden-cross/ma-bullish/volume-breakout/rsi-oversold/bollinger-squeeze/consolidation-breakout)
  - [x] 多因子评分 (估值25%/盈利25%/成长20%/安全15%/动量15%)
  - [x] 行业筛选
  - [x] CLI 集成 (`python finance.py screen`)
  - [x] API 端点 (`POST /api/screen`, `GET /api/screen/strategies`, `GET /api/screen/technical-checks`)
- [ ] Phase 4: 数据源稳定性
- [ ] Phase 5: 产品化功能

## 完成文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `skills/stock-skill/enhanced_screener.py` | 选股器 v2.0 核心引擎 | ✅ |
| `skills/stock-skill/screening_strategies.py` | 7种预设策略定义 | ✅ |
| `skills/stock-skill/technical_screener.py` | 6种技术面筛选条件 | ✅ |
| `skills/stock-skill/SKILL.md` | Phase 3 文档更新 | ✅ |
| `api/server.py` | API 端点 `/api/screen` | ✅ |

---

*Completed: 2026-05-11*
