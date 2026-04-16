# sm-analyze Skill 评估报告

**评估时间**: 2026-04-16 05:10
**来源**: https://skills.yangsir.net/skill/sm-analyze
**版本**: v3.0

---

## 📊 整合价值评估: ⭐⭐⭐⭐⭐ (极高)

### 为什么对金融 Skills 有帮助？

| 维度 | sm-analyze 能力 | 对我们的价值 |
|------|----------------|-------------|
| **分析框架** | 宏观-行业-个股三层框架 | ⭐⭐⭐⭐⭐ |
| **评分体系** | 100分制综合评分 | ⭐⭐⭐⭐⭐ |
| **止损策略** | ATR动态止损 | ⭐⭐⭐⭐ |
| **数据驱动** | AKShare数据源 | ⭐⭐⭐⭐ |
| **报告模板** | 专业Markdown格式 | ⭐⭐⭐⭐⭐ |

---

## 🔍 核心能力分析

### 1. 三层分析框架

```
┌─────────────────────────────────────────────────┐
│              投资分析框架 v3.0                    │
├─────────────────────────────────────────────────┤
│ 1. 宏观环境（大势）20分                           │
│    ├─ 市场周期：牛市/熊市/震荡                    │
│    ├─ 指数趋势：沪深300 vs MA20                  │
│    ├─ 资金环境：北向资金流向                      │
│    └─ 市场情绪：涨跌比例                          │
├─────────────────────────────────────────────────┤
│ 2. 行业分析（中观）20分                           │
│    ├─ 板块强弱：相关板块排名                      │
│    ├─ 资金流向：板块净流入                        │
│    ├─ 相对强度：ETF横向对比                       │
│    └─ 政策催化：行业政策动向                      │
├─────────────────────────────────────────────────┤
│ 3. 个股分析（微观）60分                           │
│    ├─ 趋势：均线排列+多周期共振                   │
│    ├─ 动能：MACD+RSI                            │
│    ├─ 量价：量比+量价配合+背离                   │
│    └─ 位置：ATR止损+支撑压力                     │
├─────────────────────────────────────────────────┤
│ 4. 交易策略                                       │
│    ├─ 买点：理想/激进价位                        │
│    ├─ 止损：ATR动态止损                          │
│    └─ 目标：压力位参考                           │
└─────────────────────────────────────────────────┘
```

**对我们的启发**:
- ✅ 系统化的分析框架
- ✅ 量化的评分体系
- ✅ 清晰的操作建议

### 2. 评分体系 (100分制)

| 维度 | 满分 | 评估内容 |
|------|------|---------|
| **宏观** | 20 | 市场周期 + 北向资金 |
| **行业** | 20 | 相对强度 + 板块资金 |
| **技术** | 60 | 趋势 + 动能 + 量价 + 位置 |

**评分等级**:
- 80-100: 强势 - 可积极参与
- 65-79: 偏强 - 可适度参与
- 50-64: 中性 - 观望为主
- 35-49: 偏弱 - 谨慎
- 0-34: 弱势 - 回避

### 3. ATR 动态止损

```python
# 止损建议
保守: 1倍ATR
标准: 2倍ATR  # 使用 stop_loss
激进: 3倍ATR
```

**对我们的价值**:
- 我们已有 options.py，但缺少止损模块
- 可以新增 risk_management.py

---

## 🎯 整合方案

### Phase 1: 增强投研框架 (推荐立即实施)

```python
# 新增 features/analysis_framework.py

class StockAnalysisFramework:
    """
    三层分析框架
    整合自 sm-analyze
    """
    
    def analyze(self, symbol: str) -> Dict:
        # 1. 宏观分析 (20分)
        macro = self.analyze_macro()
        
        # 2. 行业分析 (20分)
        sector = self.analyze_sector(symbol)
        
        # 3. 个股技术分析 (60分)
        technical = self.analyze_technical(symbol)
        
        # 4. 综合评分
        score = macro['score'] + sector['score'] + technical['score']
        
        return {
            'macro': macro,
            'sector': sector,
            'technical': technical,
            'total_score': score,
            'rating': self.get_rating(score),
            'suggestion': self.get_suggestion(score)
        }
```

### Phase 2: 风险管理模块

```python
# 新增 features/risk_management.py

class RiskManager:
    """
    风险管理模块
    整合自 sm-analyze 的 ATR 止损
    """
    
    def calculate_stop_loss(
        self,
        symbol: str,
        atr_multiplier: float = 2.0
    ) -> Dict:
        """
        计算 ATR 动态止损
        
        Args:
            symbol: 股票代码
            atr_multiplier: ATR 倍数 (1.0保守/2.0标准/3.0激进)
            
        Returns:
            {
                'atr': 0.0382,
                'stop_loss': 1.4966,
                'stop_loss_pct': -4.86,
                'risk_level': 'medium'
            }
        """
        pass
    
    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float = 0.02,  # 单笔风险 2%
        stop_loss_pct: float = 0.05
    ) -> Dict:
        """
        计算仓位大小
        
        Returns:
            {
                'position_value': capital * risk_per_trade / stop_loss_pct,
                'shares': int(position_value / price),
                'risk_amount': capital * risk_per_trade
            }
        """
        pass
```

### Phase 3: 报告生成器增强

```python
# 增强 features/reporter.py

def generate_analysis_report(
    symbol: str,
    framework: Dict
) -> str:
    """
    生成专业分析报告
    
    模板来自 sm-analyze
    """
    report = f"""
# {symbol} 深度分析

分析时间：{datetime.now()}
数据来源：AKShare
分析框架：宏观-行业-个股

---

## 快速摘要

| 层级 | 判断 | 得分 |
|------|------|------|
| 宏观环境 | {framework['macro']['trend']} | {framework['macro']['score']}/20 |
| 行业强度 | {framework['sector']['strength']} | {framework['sector']['score']}/20 |
| 技术形态 | {framework['technical']['trend']} | {framework['technical']['score']}/60 |
| **综合** | **{framework['rating']}** | **{framework['total_score']}/100** |

---

## 一、宏观环境（大势）

{framework['macro']['analysis']}

---

## 二、行业分析（中观）

{framework['sector']['analysis']}

---

## 三、技术分析（微观）

{framework['technical']['analysis']}

---

## 四、交易策略

### ATR 动态止损
- 当前 ATR: {framework['atr']}
- 建议止损: {framework['stop_loss']} ({framework['stop_loss_pct']}%)

### 操作建议
| 场景 | 价格 | 说明 |
|------|------|------|
| 理想买点 | {framework['ideal_buy']} | 回调到支撑位 |
| 激进买点 | {framework['aggressive_buy']} | 突破确认 |
| 止损位 | {framework['stop_loss']} | 2倍ATR |
| 目标位 | {framework['target']} | 压力位附近 |

---

⚠️ 免责声明：本分析基于历史数据，不构成投资建议
"""
    return report
```

---

## 📊 与我们现有能力的对比

| 功能 | 我们现有 | sm-analyze | 整合价值 |
|------|---------|-----------|---------|
| **行情数据** | ✅ | ✅ | - |
| **技术分析** | ✅ 简单 | ✅ 完整 | ⭐⭐⭐⭐ |
| **宏观分析** | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| **行业分析** | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| **评分体系** | ❌ | ✅ | ⭐⭐⭐⭐⭐ |
| **止损策略** | ❌ | ✅ ATR | ⭐⭐⭐⭐ |
| **报告模板** | ✅ 基础 | ✅ 专业 | ⭐⭐⭐⭐ |

### 我们缺少的核心能力

1. **宏观分析**
   - 市场周期判断
   - 北向资金流向
   - 市场情绪指标

2. **行业分析**
   - 板块相对强度
   - ETF 横向对比
   - 板块资金流向

3. **评分体系**
   - 100分制量化评分
   - 等级划分
   - 操作建议

4. **风险管理**
   - ATR 动态止损
   - 仓位计算
   - 风险控制

---

## 🔧 实施计划

### Week 1: 核心框架

```python
# 创建文件结构
features/
├── analysis_framework.py   # 三层分析框架
├── macro_analyzer.py       # 宏观分析
├── sector_analyzer.py      # 行业分析
└── risk_management.py      # 风险管理
```

### Week 2: 数据集成

```python
# 整合数据源
from akshare import stock_zh_a_spot_em  # A股行情
from akshare import stock_hk_spot       # 港股行情
from akshare import stock_em_hsgt_north_net_flow_in  # 北向资金

# 宏观数据
def get_macro_data():
    return {
        'hs300': get_hs300(),
        'north_flow': get_north_flow(),
        'market_sentiment': get_market_sentiment()
    }
```

### Week 3: 评分系统

```python
# 评分引擎
class ScoringEngine:
    def score_macro(self, data) -> int:
        """宏观评分 (20分)"""
        score = 0
        
        # 市场周期 (12分)
        if data['hs300'] > data['hs300_ma20']:
            score += 12  # 牛市
        elif data['hs300'] < data['hs300_ma20'] * 0.9:
            score += 4   # 熊市
        else:
            score += 8   # 震荡
        
        # 北向资金 (8分)
        if data['north_flow_5d'] > 50:
            score += 8
        elif data['north_flow_5d'] < -50:
            score += 2
        else:
            score += 4
        
        return score
    
    def score_sector(self, data) -> int:
        """行业评分 (20分)"""
        pass
    
    def score_technical(self, data) -> int:
        """技术评分 (60分)"""
        pass
```

---

## 💡 核心启发

### 1. 系统化思维

```
宏观 → 行业 → 个股 → 策略
 ↓       ↓       ↓       ↓
20分    20分    60分    操作
```

**启发**: 投资决策需要层层递进的分析框架

### 2. 量化评分

**启发**: 将定性分析转化为量化评分，便于比较和决策

### 3. 风险管理

**启发**: 
- 永远设置止损
- ATR 是优秀的动态止损工具
- 控制单笔风险 (建议 2%)

### 4. 报告规范

**启发**: 
- 结构化输出
- 明确数据来源
- 必须有免责声明

---

## ⚠️ 注意事项

### 1. 数据源依赖

- 主要依赖 AKShare
- 需要稳定的 A股/港股数据源
- 我们已有 akshare 模块，可以直接复用

### 2. 市场差异

- sm-analyze 主要针对 A股
- 我们需要扩展到美股、加密货币
- 不同市场的宏观指标不同

### 3. 实时性

- 部分数据需要实时更新
- 缓存策略很重要
- 建议设置数据有效期

---

## 🏆 最终结论

### 是否有帮助？

**✅ 强烈推荐整合！**

| 理由 | 说明 |
|------|------|
| **框架完整** | 宏观-行业-个股三层框架 |
| **量化评分** | 100分制，易于决策 |
| **风险控制** | ATR止损 + 仓位管理 |
| **专业模板** | 标准化报告格式 |
| **开源精神** | 可学习其设计思路 |

### 整合优先级

```
P0: 三层分析框架 (Week 1-2)
P1: 评分体系 (Week 2-3)
P2: 风险管理 (Week 3)
P3: 报告模板优化 (持续)
```

### 下一步行动

1. **本周**: 创建 analysis_framework.py
2. **下周**: 实现宏观和行业分析
3. **本月**: 完成评分体系和风险管理

---

**sm-analyze 的三层分析框架和评分体系是我们可以立即借鉴的宝贵设计，强烈推荐整合！** 🚀
