# Phase 2: 财报预测与回顾

## 目标

实现财报预测、财报回顾和业绩比较分析功能，帮助投资者更好地理解公司业绩表现。

## 功能清单

### 2.1 财报预测模型

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 收入预测 | 基于历史增长趋势和行业数据预测收入 | P1 |
| 利润预测 | 预测毛利率、净利率趋势 | P1 |
| EPS预测 | 预测每股收益 | P1 |
| 季节性调整 | 考虑季度季节性因素 | P2 |

### 2.2 财报回顾分析

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 业绩达标检测 | 对比实际 vs 预期 | P1 |
| 利润率变化 | 同比/环比分析 | P1 |
| 资产负债表健康度 | 关键科目变化 | P1 |
| 现金流质量 | 经营现金流 vs 净利润 | P1 |

### 2.3 业绩比较分析

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 同行业对比 | 同业公司财务指标对比 | P1 |
| 时间序列对比 | 公司历史业绩趋势 | P1 |
| 预期修正追踪 | 分析师预期变化 | P2 |

## 数据来源

- **yfinance**: 美股历史财务数据
- **AkShare**: A股财报数据
- **eFinance/BAOSTOCK**: 备用数据源

## 输出结构

```python
{
    "earnings_preview": {
        "revenue_forecast": {...},
        "profit_forecast": {...},
        "eps_forecast": {...},
        "confidence": "medium",
    },
    "earnings_recap": {
        "actual_vs_expected": {...},
        "margin_analysis": {...},
        "balance_sheet_health": {...},
        "cash_flow_quality": {...},
    },
    "performance_comparison": {
        "peer_comparison": {...},
        "historical_trend": {...},
        "estimate_revisions": {...},
    }
}
```

## 技术实现

### 核心文件

- `skills/stock-skill/earnings_preview.py` - 财报预测
- `skills/stock-skill/earnings_recap.py` - 财报回顾
- `skills/stock-skill/performance_comparison.py` - 业绩比较

### 算法

- **收入预测**: 线性回归 + 季节性因子
- **利润率预测**: 移动平均 + 趋势外推
- **业绩达标**: 实际值 vs 分析师一致预期

## CLI 命令

```bash
# 财报预测
python finance.py earnings-preview AAPL

# 财报回顾
python finance.py earnings-recap AAPL

# 业绩比较
python finance.py compare AAPL MSFT
```

## API 端点

```
GET /api/earnings-preview/{symbol}
GET /api/earnings-recap/{symbol}
GET /api/performance-comparison/{symbol}
```

## 风险提示

- 预测基于历史数据，不代表实际业绩
- 需要标注预测置信度和假设条件
- 不构成投资建议

## 进度

- [x] Phase 1: 增强技术分析 (VWAP/斐波那契/缠论/K线形态/趋势线/ADX)
- [x] Phase 2: 财报预测与回顾 (已完成 2026-05-10)
  - [x] 财报预测 (收入/利润/EPS预测)
  - [x] 财报回顾 (业绩达标/利润率/资产负债/现金流)
  - [x] 业绩比较 (同比/环比/行业对比)
  - [x] CLI 集成 (finance.py earnings/preview/recap/compare)
- [ ] Phase 3: 选股器增强
- [ ] Phase 4: 数据源稳定性
- [ ] Phase 5: 产品化功能

---

*Last updated: 2026-05-10*
