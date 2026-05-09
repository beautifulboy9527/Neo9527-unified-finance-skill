---
name: technical-analysis-skill
description: |
  增强技术分析模块 - Phase 1。包含 VWAP、斐波那契回撤/扩展、缠论中枢/笔段、K线形态识别、趋势线识别、ADX 指标。
  适用于 A股、港股、美股的技术面分析，可与 stock-skill 的综合分析报告集成。
version: 1.0.0
---

# Technical Analysis Skill - Phase 1

增强技术分析模块，提供专业级的技术指标和形态识别能力。

## 核心功能

### 1. VWAP 指标
- **计算**: 成交量加权平均价
- **解读**: 价格在 VWAP 上方/下方反映日内多空力量
- **使用**: `calculate_vwap(hist)`

### 2. 斐波那契分析
- **回撤位**: 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
- **扩展位**: 61.8%, 100%, 161.8%, 261.8%, 423.6%
- **使用**: `calculate_fibonacci_retracements(hist)`, `calculate_fibonacci_extensions(hist)`

### 3. 缠论中枢分析
- **笔段识别**: 自动识别顶底分型和笔段
- **中枢计算**: 计算笔段重叠区域形成的中枢
- **使用**: `calculate_chan_segments(hist)`

### 4. K线形态识别
| 形态 | 类型 | 信号 |
|------|------|------|
| 锤子线 | 看涨反转 | 下跌末端底部信号 |
| 射击之星 | 看跌反转 | 上涨末端顶部信号 |
| 吞没形态 | 强烈反转 | 完全包裹前一根K线 |
| 早晨之星 | 强烈看涨 | 三日底部反转 |
| 黄昏之星 | 强烈看跌 | 三日顶部反转 |
| 十字星 | 中性犹豫 | 多空均衡待突破 |
| 纺锤线 | 中性犹豫 | 市场犹豫不决 |

### 5. 趋势线识别
- **自动拟合**: 基于局部极值点自动绘制趋势线
- **R² 检验**: 仅显示 R² > 0.7 的有效趋势线
- **使用**: `identify_trendlines(hist)`

### 6. ADX 指标
- **趋势强度**: ADX > 25 表示趋势明显
- **趋势方向**: +DI vs -DI 比较
- **使用**: `calculate_adx(hist)`

## Python 使用

```python
from skills.shared.technical_indicators import (
    calculate_vwap,
    calculate_fibonacci_retracements,
    calculate_fibonacci_extensions,
    calculate_chan_segments,
    identify_candlestick_patterns,
    identify_trendlines,
    calculate_adx,
    enhanced_technical_analysis,
)

# 单项指标
vwap = calculate_vwap(hist)
fib = calculate_fibonacci_retracements(hist)
candles = identify_candlestick_patterns(hist)
adx = calculate_adx(hist)

# 综合分析
analysis = enhanced_technical_analysis(hist, symbol="600519")
print(analysis["summary"]["overall_bias"])
```

## 集成方式

```python
from skills.shared.technical_indicators import enhanced_technical_analysis
from skills.stock_skill.stock_data_collector import collect_stock_data

# 收集基础数据
data = collect_stock_data("600519")

# 获取技术分析历史
if data.get("technical_analysis", {}).get("candles"):
    candles = data["technical_analysis"]["candles"]
    
    # 转换为 DataFrame
    import pandas as pd
    df = pd.DataFrame(candles)
    df = df.rename(columns={
        "date": "日期", "open": "开盘", 
        "high": "最高", "low": "最低", 
        "close": "收盘", "volume": "成交量"
    })
    
    # 增强分析
    enhanced = enhanced_technical_analysis(df, symbol="600519")
```

## 输出结构

```python
{
    "symbol": "600519",
    "lookback": 100,
    "indicators": {
        "vwap": {"vwap": 2850.50, "position": "价格位于VWAP上方", ...},
        "fibonacci_retracements": {"swing_high": 3000, "swing_low": 2500, ...},
        "candlestick_patterns": {"patterns": [...], "dominant_pattern": {...}},
        "adx": {"adx": 28.5, "trend": "明确上升趋势", ...},
        "trendlines": {"trendlines": [...], ...},
        "chan_analysis": {"segments_count": 15, "centers": [...], ...}
    },
    "summary": {
        "signals": [("VWAP", "看多", "..."), ...],
        "signal_count": 4,
        "bullish_count": 2,
        "bearish_count": 1,
        "overall_bias": "偏多"
    }
}
```

## 数据要求

| 指标 | 最小K线数 | 必要字段 |
|------|----------|----------|
| VWAP | 5 | 最高/最低/收盘/成交量 |
| 斐波那契 | 20 | 收盘价 |
| 缠论 | 20 | 最高/最低/收盘 |
| K线形态 | 3 | 开盘/最高/最低/收盘 |
| 趋势线 | 30 | 最高/最低/收盘 |
| ADX | 15 | 最高/最低/收盘 |

---

*v1.0.0 - 增强技术分析 Phase 1*
