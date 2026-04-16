# sm-entry-signals Skill 评估报告

**评估时间**: 2026-04-16 05:15
**来源**: https://skills.yangsir.net/skill/sm-entry-signals
**更新**: 2026-01-17
**样本**: 5095 个交易信号

---

## 📊 整合价值评估: ⭐⭐⭐⭐⭐ (极高)

### 为什么对金融 Skills 有帮助？

| 维度 | entry-signals 能力 | 对我们的价值 |
|------|-------------------|-------------|
| **历史验证** | 基于真实交易数据 | ⭐⭐⭐⭐⭐ |
| **成功率统计** | 每个信号的成功率 | ⭐⭐⭐⭐⭐ |
| **置信度** | 60-95% 置信区间 | ⭐⭐⭐⭐⭐ |
| **多时间框架** | 15m/1h/4h 分析 | ⭐⭐⭐⭐ |
| **自动更新** | Observer Agent 生成 | ⭐⭐⭐⭐ |

---

## 🔍 核心能力分析

### 1. 高成功率信号 (Top 10)

| 信号模式 | 成功率 | 样本数 | 置信度 |
|---------|--------|--------|--------|
| **多时间框架多头对齐** (15m/1h/4h + 风险验证) | **88%** | 164 | 85% |
| **多时间框架多头对齐** + 风险验证 | **85%** | 157 | 75% |
| **多时间框架多头对齐** + 风险验证 | **85%** | 164 | 80% |
| **多时间框架多头对齐** + 风险验证 | **85%** | 164 | 85% |
| **SMA金叉 + MACD多头 + 布林中性** | **82%** | 184 | 80% |
| **SMA金叉 + MACD多头 + 布林中性** | **82%** | 184 | 85% |
| **加仓获胜仓位** | **80%** | 157 | 75% |
| **加仓获胜仓位** | **78%** | 164 | 80% |
| **多时间框架多头对齐** (大样本) | **75%** | 89 | 95% |
| **多时间框架空头对齐** | **65%** | 103 | 95% |

### 2. 信号类型分布

#### 高成功率信号 (≥70%)

```
✅ 多时间框架多头对齐 (15m/1h/4h) - 88% 成功率
✅ SMA金叉 + MACD多头 + 布林中性 - 82% 成功率
✅ 加仓获胜仓位 - 80% 成功率
✅ 多时间框架空头对齐 - 65% 成功率
```

#### 中等成功率信号 (40-70%)

```
⚠️ 相对强度背离 - 45% 成功率
⚠️ SMA/MACD空头信号 - 35% 成功率
```

#### 低成功率信号 (<40%)

```
❌ 高资金费率做多 - 35% 成功率
❌ 正资金费率做多 - 30% 成功率
❌ RSI超买 + MACD空头做空 - 30% 成功率
❌ 负资金费率做多 - 25% 成功率
❌ 反弹策略 - 20% 成功率
```

### 3. 核心信号详解

#### Multi-timeframe Bullish Alignment

```
信号: 多时间框架多头对齐 (15m/1h/4h)
成功率: 88%
样本数: 164
置信度: 85%

条件:
1. 15分钟图多头趋势
2. 1小时图多头趋势
3. 4小时图多头趋势
4. 技术指标显示多头倾向
5. 风险验证通过

描述: 
"skill_aware_oss consistently uses this with strong results (+$1236.81)"
"Multi-timeframe bullish alignment with explicit risk validation"
```

#### SMA Crossover + MACD Bullish

```
信号: SMA金叉 + MACD多头 + 布林中性
成功率: 82%
样本数: 184
置信度: 80%

条件:
1. SMA金叉 (短期均线上穿长期均线)
2. MACD 显示多头
3. 布林带中性 (价格在中轨附近)
4. 风险计算器验证通过

描述:
"Technical indicators (SMA crossover, bullish MACD, neutral Bollinger) support a long entry"
```

#### Scaling into Winning Position

```
信号: 加仓获胜仓位
成功率: 80%
样本数: 157
置信度: 75%

条件:
1. 已有盈利仓位
2. 趋势延续
3. 逐步加仓

描述:
"Scaling into existing winning position"
```

---

## 🎯 对我们的价值

### 1. 信号模式库

**我们目前缺少**:
- ❌ 历史验证的交易信号
- ❌ 成功率统计
- ❌ 置信度评估

**entry-signals 提供**:
- ✅ 30 个经过验证的信号模式
- ✅ 每个信号的成功率
- ✅ 样本数和置信度

### 2. 多时间框架分析

**我们目前有**:
- ✅ 单时间框架技术分析
- ❌ 多时间框架确认

**entry-signals 启发**:
```python
def check_multi_timeframe_alignment(symbol: str) -> Dict:
    """
    检查多时间框架对齐
    
    Returns:
        {
            '15m': 'bullish',
            '1h': 'bullish',
            '4h': 'bullish',
            'alignment': 'bullish',  # all bullish
            'confidence': 0.85
        }
    """
    timeframes = ['15m', '1h', '4h']
    trends = {}
    
    for tf in timeframes:
        ohlcv = get_ohlcv(symbol, timeframe=tf)
        trends[tf] = analyze_trend(ohlcv)
    
    # 检查是否全部对齐
    if all(t == 'bullish' for t in trends.values()):
        return {
            'alignment': 'bullish',
            'confidence': 0.88,  # 历史成功率
            'trends': trends
        }
    elif all(t == 'bearish' for t in trends.values()):
        return {
            'alignment': 'bearish',
            'confidence': 0.65,
            'trends': trends
        }
    else:
        return {
            'alignment': 'mixed',
            'confidence': 0.5,
            'trends': trends
        }
```

### 3. 信号评分系统

```python
# 基于历史成功率的信号评分

SIGNAL_SCORES = {
    # 高成功率信号 (≥80%)
    'multi_timeframe_bullish': {
        'success_rate': 0.88,
        'samples': 164,
        'confidence': 0.85,
        'action': 'buy',
        'risk_level': 'low'
    },
    'sma_macd_bullish': {
        'success_rate': 0.82,
        'samples': 184,
        'confidence': 0.80,
        'action': 'buy',
        'risk_level': 'low'
    },
    'scale_winning': {
        'success_rate': 0.80,
        'samples': 157,
        'confidence': 0.75,
        'action': 'add_position',
        'risk_level': 'medium'
    },
    
    # 中等成功率信号 (40-80%)
    'multi_timeframe_bearish': {
        'success_rate': 0.65,
        'samples': 103,
        'confidence': 0.95,
        'action': 'sell',
        'risk_level': 'medium'
    },
    'rsi_divergence': {
        'success_rate': 0.45,
        'samples': 79,
        'confidence': 0.60,
        'action': 'watch',
        'risk_level': 'high'
    },
    
    # 低成功率信号 (<40%)
    'high_funding_rate': {
        'success_rate': 0.35,
        'samples': 248,
        'confidence': 0.75,
        'action': 'avoid',
        'risk_level': 'very_high'
    }
}
```

---

## 🔧 整合方案

### Phase 1: 信号模式库 (立即实施)

```python
# 新增 features/entry_signals.py

class EntrySignalAnalyzer:
    """
    入场信号分析器
    
    整合自 sm-entry-signals
    """
    
    # 高成功率信号 (>80%)
    HIGH_CONFIDENCE_SIGNALS = {
        'multi_timeframe_bullish': {
            'pattern': '多时间框架多头对齐',
            'success_rate': 0.88,
            'timeframes': ['15m', '1h', '4h'],
            'risk_validation': True
        },
        'sma_macd_bullish': {
            'pattern': 'SMA金叉 + MACD多头',
            'success_rate': 0.82,
            'indicators': ['SMA', 'MACD', 'Bollinger']
        },
        'scale_winning': {
            'pattern': '加仓获胜仓位',
            'success_rate': 0.80,
            'condition': 'profitable_position'
        }
    }
    
    def detect_signals(self, symbol: str) -> List[Dict]:
        """
        检测入场信号
        
        Returns:
            [
                {
                    'signal': 'multi_timeframe_bullish',
                    'success_rate': 0.88,
                    'confidence': 0.85,
                    'action': 'buy',
                    'description': '...'
                }
            ]
        """
        signals = []
        
        # 1. 检查多时间框架对齐
        mtf = self.check_multi_timeframe(symbol)
        if mtf['alignment'] == 'bullish':
            signals.append({
                'signal': 'multi_timeframe_bullish',
                'success_rate': 0.88,
                'confidence': 0.85,
                'action': 'buy',
                'description': mtf['description']
            })
        
        # 2. 检查 SMA + MACD 组合
        sma_macd = self.check_sma_macd(symbol)
        if sma_macd['bullish']:
            signals.append({
                'signal': 'sma_macd_bullish',
                'success_rate': 0.82,
                'confidence': 0.80,
                'action': 'buy',
                'description': sma_macd['description']
            })
        
        # 3. 其他信号...
        
        return signals
```

### Phase 2: 多时间框架分析

```python
# 增强 features/chart.py

def analyze_multi_timeframe(
    symbol: str,
    timeframes: List[str] = ['15m', '1h', '4h']
) -> Dict:
    """
    多时间框架分析
    
    来自 entry-signals 的最佳实践
    """
    results = {}
    
    for tf in timeframes:
        ohlcv = get_ohlcv(symbol, timeframe=tf, limit=100)
        results[tf] = {
            'trend': detect_trend(ohlcv),
            'ma_status': check_ma_alignment(ohlcv),
            'macd_status': check_macd(ohlcv),
            'rsi_status': check_rsi(ohlcv)
        }
    
    # 判断对齐
    trends = [r['trend'] for r in results.values()]
    
    if all(t == 'bullish' for t in trends):
        alignment = 'bullish'
        success_rate = 0.88
    elif all(t == 'bearish' for t in trends):
        alignment = 'bearish'
        success_rate = 0.65
    else:
        alignment = 'mixed'
        success_rate = 0.50
    
    return {
        'timeframes': results,
        'alignment': alignment,
        'success_rate': success_rate,
        'confidence': min(len([t for t in trends if t == alignment]) / len(trends), 0.95)
    }
```

### Phase 3: 信号置信度系统

```python
# 新增 agent/signal_confidence.py

class SignalConfidenceScorer:
    """
    信号置信度评分器
    
    基于历史成功率
    """
    
    def calculate_confidence(
        self,
        signals: List[Dict],
        market_context: Dict
    ) -> Dict:
        """
        计算综合置信度
        
        Args:
            signals: 检测到的信号列表
            market_context: 市场环境
            
        Returns:
            {
                'overall_confidence': 0.85,
                'action': 'buy',
                'risk_level': 'low',
                'signals_used': [...],
                'warnings': [...]
            }
        """
        if not signals:
            return {
                'overall_confidence': 0,
                'action': 'hold',
                'risk_level': 'unknown'
            }
        
        # 加权平均成功率
        total_weight = sum(s.get('samples', 100) for s in signals)
        weighted_success = sum(
            s['success_rate'] * s.get('samples', 100) 
            for s in signals
        ) / total_weight
        
        # 调整置信度
        confidence = weighted_success
        
        # 市场环境调整
        if market_context.get('volatility') == 'high':
            confidence *= 0.8
        
        # 确定操作
        if confidence >= 0.80:
            action = 'buy'
            risk = 'low'
        elif confidence >= 0.60:
            action = 'buy'
            risk = 'medium'
        elif confidence >= 0.40:
            action = 'watch'
            risk = 'high'
        else:
            action = 'avoid'
            risk = 'very_high'
        
        return {
            'overall_confidence': round(confidence, 2),
            'action': action,
            'risk_level': risk,
            'signals_used': signals,
            'warnings': self._get_warnings(signals, market_context)
        }
```

---

## 📊 预期效果

### 新增能力

| 能力 | 描述 | 价值 |
|------|------|------|
| **信号模式库** | 30个验证过的交易信号 | ⭐⭐⭐⭐⭐ |
| **成功率统计** | 每个信号的历史成功率 | ⭐⭐⭐⭐⭐ |
| **多时间框架** | 15m/1h/4h 对齐检测 | ⭐⭐⭐⭐ |
| **置信度评分** | 基于历史的置信度 | ⭐⭐⭐⭐⭐ |

### CLI 命令

```bash
# 检测入场信号
python finance.py signals 600519

# 多时间框架分析
python finance.py mtf 600519 --timeframes 15m 1h 4h

# 信号置信度评分
python finance.py confidence 600519
```

---

## ⚠️ 注意事项

### 1. 数据依赖

- 需要历史K线数据
- 多时间框架数据获取
- 我们已有 yfinance/akshare，可用

### 2. 市场差异

- entry-signals 主要针对加密货币
- 股票市场需要调整参数
- 成功率可能不同

### 3. 样本量

- 高成功率信号样本较小 (100-200)
- 需要持续积累数据
- 自动更新机制很重要

---

## 🏆 最终结论

### 是否有帮助？

**✅ 强烈推荐整合！**

| 理由 | 说明 |
|------|------|
| **历史验证** | 基于真实交易数据 |
| **成功率统计** | 每个信号量化成功率 |
| **多时间框架** | 最佳实践验证 |
| **置信度系统** | 决策支持 |
| **自动更新** | Observer Agent |

### 整合优先级

```
P0: 信号模式库 (本周)
P1: 多时间框架分析 (下周)
P2: 置信度评分系统 (下周)
P3: 自动更新机制 (长期)
```

### 下一步行动

1. **本周**: 创建 `features/entry_signals.py`
2. **下周**: 实现多时间框架检测
3. **下周**: 添加置信度评分

---

**entry-signals 提供了经过历史验证的交易信号模式库，成功率统计和置信度评估是我们目前最缺少的，强烈推荐优先整合！** 🎯
