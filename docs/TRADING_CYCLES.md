# 交易周期支持文档

## 交易策略分类

### 📈 短线交易 (日内/隔夜)

**打板策略**:
- `scripts/features/board_scanner.py` - 打板筛选器
  * 涨停板实时扫描
  * 强势股筛选 (涨幅>7%)
  * 连板数据统计
  * 打板市场情绪分析
  * 打板机会识别

**使用方式**:
```bash
# 涨停板扫描
python scripts/features/board_scanner.py --type limit-up

# 强势股筛选
python scripts/features/board_scanner.py --type strong

# 连板分析
python scripts/features/board_scanner.py --type continuous

# 市场情绪
python scripts/features/board_scanner.py --type market

# 打板机会
python scripts/features/board_scanner.py --type opportunities
```

**信号追踪**:
- `scripts/features/signal_tracker.py` - 信号追踪
- `scripts/features/entry_signals.py` - 入场信号
- `scripts/features/volume_validator.py` - 量价验证

---

### 📊 波段交易 (数天-数周)

**技术分析**:
- `scripts/features/technical_analyzer.py` - 技术分析器
- `scripts/features/kline_chart.py` - K线图表
- `scripts/features/chart.py` - 图表生成

**回测引擎**:
- `scripts/features/backtest_engine.py` - 回测引擎

**风险管理**:
- `scripts/features/risk_management.py` - 风险管理
- `scripts/features/liquidity.py` - 流动性分析

---

### 💰 中长期投资 (数月-数年)

**综合分析器** (v3.0):
- `skills/stock-skill/comprehensive_analyzer.py`
  * 8维度综合分析
  * 适合价值投资

**深度研报**:
- `skills/stock-skill/deep-research/analyzer.py`
  * 8阶段深度分析
  * 投资风格适配

**估值模型**:
- `skills/stock-skill/valuation.py`
  * DCF/DDM估值
  * 安全边际计算

---

### 🎯 策略建议

| 交易周期 | 推荐模块 | 时间框架 | 风险等级 |
|---------|---------|---------|---------|
| **日内** | board_scanner, signal_tracker | 分钟级 | 高 |
| **短线** | technical_analyzer, entry_signals | 小时级 | 高 |
| **波段** | backtest_engine, risk_management | 日级 | 中 |
| **中线** | comprehensive_analyzer | 周级 | 中 |
| **长线** | deep-research, valuation | 月级 | 低 |

---

## CLI 命令汇总

### 短线交易
```bash
# 打板扫描
python scripts/features/board_scanner.py --type limit-up

# 信号追踪
python scripts/features/signal_tracker.py AAPL
```

### 波段交易
```bash
# 技术分析
python scripts/features/technical_analyzer.py AAPL

# 回测
python scripts/features/backtest_engine.py AAPL --strategy ma_cross
```

### 中长期投资
```bash
# 综合分析
python skills/stock-skill/comprehensive_analyzer.py AAPL

# 深度研报
python skills/stock-skill/deep-research/analyzer.py AAPL

# 估值计算
python skills/stock-skill/valuation.py AAPL
```

---

## 数据源说明

### 短线数据
- 东方财富 API (实时行情)
- AkShare (A股数据)

### 中长期数据
- yfinance (美股/港股)
- AkShare (A股财务)

---

## 待开发功能

1. **日内策略**
   - [ ] 高频数据获取
   - [ ] Level-2 数据
   - [ ] 分时图分析

2. **波段策略**
   - [ ] 多因子模型
   - [ ] 行业轮动
   - [ ] 板块热点

3. **风险控制**
   - [ ] 止损止盈
   - [ ] 仓位管理
   - [ ] 组合优化

---

*最后更新: 2026-04-18*
