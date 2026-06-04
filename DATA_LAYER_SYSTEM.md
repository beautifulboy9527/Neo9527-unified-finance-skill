# 统一数据层系统文档

## 概述

统一数据层系统是一个完整的数据质量保障框架，旨在一次性解决股票分析系统中的数据缺失、格式不一致和质量问题。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (a_share_analyzer)                 │
│                     ↓ 调用统一接口                            │
├─────────────────────────────────────────────────────────────┤
│                   UnifiedDataLayer                           │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ 数据验证      │ 质量评分      │ 缺失值处理            │    │
│  │ DataValidator│QualityScorer│MissingValueHandler   │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                 DataSourceManager                            │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │ 健康检查      │ 重试机制      │ 数据缓存              │    │
│  │HealthChecker │RetryManager  │ DataCache            │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                     数据源层                                 │
│     yfinance    eastmoney    sina    其他数据源              │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. UnifiedDataLayer (统一数据层)

**功能**：
- 统一数据访问接口
- 自动数据验证
- 智能缺失值处理
- 数据质量评分

**使用示例**：
```python
from unified_data_layer import UnifiedDataLayer

# 创建实例
layer = UnifiedDataLayer()

# 处理数据
processed_data = layer.process_data(symbol='603986', raw_data=data, hist_data=hist)

# 查看数据质量
print(f"数据质量分数: {processed_data['data_quality_score']}")
print(f"置信度: {processed_data['data_quality_label']}")
```

---

### 2. DataValidator (数据验证器)

**验证规则**：
- 价格数据：current, high, low, volume
- 技术数据：support_near, resistance_near, rsi, macd
- 财务数据：debt_ratio, current_ratio, roe

**验证结果**：
- 质量分数 (0-100)
- 是否有效 (True/False)

**示例**：
```python
from unified_data_layer import DataValidator

# 验证价格数据
price_data = {'current': 100.0, 'high': 105.0, 'low': 98.0, 'volume': 1000000}
score, is_valid = DataValidator.validate_price(price_data)
print(f"质量分数: {score}, 有效: {is_valid}")
```

---

### 3. DataQualityScorer (质量评分器)

**评分等级**：
| 分数范围 | 置信度 | 图标 | 说明 |
|---------|-------|------|------|
| 90-100 | 高置信度 | ✅ | 数据完整可靠 |
| 70-89 | 中等置信度 | ⚠️ | 部分数据为估算值 |
| 50-69 | 低置信度 | ❌ | 大量数据缺失 |
| 0-49 | 不可用 | 🚫 | 数据严重缺失 |

**示例**：
```python
from unified_data_layer import DataQualityScorer

label, icon, desc = DataQualityScorer.get_quality_label(85)
print(f"{icon} {label}: {desc}")
# 输出: ⚠️ 中等置信度: 部分数据为估算值
```

---

### 4. MissingValueHandler (缺失值处理器)

**降级策略**：

#### 支撑阻力位缺失
- **方法**: 使用ATR(平均真实波动范围)计算
- **公式**: 
  - 支撑位 = 当前价 - ATR × 2
  - 阻力位 = 当前价 + ATR × 2
- **适用场景**: 技术指标数据缺失

#### 行业信息缺失
- **方法**: 根据股票代码推断
- **规则**:
  - 60xxxx → 工业
  - 00xxxx → 科技
  - 30xxxx → 创业板
  - 68xxxx → 科创板

#### 财务数据缺失
- **方法**: 使用行业默认值
- **默认值**:
  - 资产负债率: 50%
  - 流动比率: 1.5
  - ROE: 10%
  - 毛利率: 30%

**示例**：
```python
from unified_data_layer import MissingValueHandler

# 处理缺失的支撑阻力位
estimated = MissingValueHandler.handle_missing_support(
    current_price=309.18,
    hist_data=hist_dataframe
)
print(f"估算支撑位: {estimated['support_near']}")
print(f"估算方法: {estimated['estimation_method']}")
```

---

### 5. DataSourceManager (数据源管理器)

**功能**：
- 数据源健康检查
- 自动重试机制
- 数据缓存
- 智能切换

**使用示例**：
```python
from data_source_manager import get_data_source_manager

manager = get_data_source_manager()

# 获取最佳数据源
best_source = manager.get_best_source()

# 带缓存的数据获取
data = manager.fetch_with_cache(
    key='stock_603986',
    fetch_func=lambda: fetch_stock_data('603986')
)

# 查看健康报告
manager.print_health_report()
```

---

## 数据流程

### 1. 数据获取流程

```
用户请求 → a_share_analyzer.analyze()
    ↓
UnifiedDataLayer.process_data()
    ↓
┌──────────────┐
│ 数据验证      │ → 检测缺失/无效数据
├──────────────┤
│ 质量评分      │ → 计算质量分数
├──────────────┤
│ 缺失值处理    │ → 降级计算/估算
├──────────────┤
│ 质量标记      │ → 添加质量标签
└──────────────┘
    ↓
返回完整数据 + 质量信息
```

### 2. 数据缺失处理流程

```
检测到数据缺失
    ↓
判断数据类型 (价格/技术/财务)
    ↓
选择降级策略
    ↓
┌──────────────┬──────────────┬──────────────┐
│ 价格数据      │ 技术数据      │ 财务数据      │
│ → 网络重试    │ → ATR计算    │ → 默认值     │
└──────────────┴──────────────┴──────────────┘
    ↓
标记为估算数据 (data_quality='estimated')
    ↓
添加估算方法说明 (estimation_method)
```

---

## 报告中的数据质量显示

### Markdown报告示例

```markdown
## 数据质量说明

**数据质量分数**: 65.3/100
**置信度**: ❌ 低置信度
**说明**: 大量数据缺失，建议谨慎使用

**注意**: 部分技术指标数据使用估算值（ATR计算），建议结合其他分析工具验证。
```

### HTML报告示例

```html
<div class="quality-box">
    <h3>数据质量说明</h3>
    <div class="quality-score">65.3/100</div>
    <div class="quality-label">❌ 低置信度</div>
    <div class="quality-desc">大量数据缺失，建议谨慎使用</div>
</div>
```

---

## 配置选项

### 缓存配置
```python
cache = DataCache(
    max_size=100,        # 最大缓存条目数
    ttl_seconds=300      # 缓存有效期(秒)
)
```

### 重试配置
```python
retry_manager = RetryManager(
    max_retries=3,       # 最大重试次数
    base_delay=1.0       # 基础延迟(秒)
)
```

### 数据源配置
```python
manager = DataSourceManager()
manager.sources = ['yfinance', 'eastmoney', 'sina', 'tushare']
```

---

## 最佳实践

### 1. 始终检查数据质量
```python
result = analyzer.analyze(symbol)

# 检查数据质量
if result['data_quality_score'] < 70:
    print("⚠️ 数据质量较低，建议谨慎使用")
```

### 2. 处理估算数据
```python
tech = result['technical']

if tech.get('data_quality') == 'estimated':
    method = tech.get('estimation_method')
    print(f"部分数据使用 {method} 估算")
```

### 3. 查看健康报告
```python
manager = get_data_source_manager()
report = manager.get_health_report()

for source, health in report.items():
    if not health['available']:
        print(f"⚠️ 数据源 {source} 不可用")
```

---

## 故障排查

### 问题1: 数据质量分数过低

**原因**: 
- 数据源连接失败
- 股票代码不正确
- 市场休市/停牌

**解决**:
```python
# 检查健康报告
manager.print_health_report()

# 查看具体缺失字段
if result['price']['quality_score'] < 50:
    print("价格数据缺失严重")
```

### 问题2: 支撑阻力位显示异常

**原因**: 
- 历史数据不足
- ATR计算失败

**解决**:
```python
tech = result['technical']
if tech.get('data_quality') == 'estimated':
    method = tech.get('estimation_method', '未知')
    print(f"支撑阻力位使用 {method} 估算")
```

### 问题3: 数据源频繁切换

**原因**: 
- 网络不稳定
- 数据源限流

**解决**:
```python
# 查看数据源健康状态
for source, health in manager.health_checker.items():
    if health.failure_count > 3:
        print(f"数据源 {source} 频繁失败: {health.last_error}")
```

---

## 未来改进

### 短期 (1-2周)
- [ ] 添加更多数据源支持 (tushare, baostock)
- [ ] 完善财务数据验证规则
- [ ] 添加数据一致性检查

### 中期 (1-2月)
- [ ] 实现数据质量监控告警
- [ ] 添加机器学习预测模型
- [ ] 构建数据质量仪表盘

### 长期 (3-6月)
- [ ] 实时数据质量追踪
- [ ] 自动数据源切换策略
- [ ] 完整的数据治理平台

---

## 维护说明

### 日常维护
1. 定期查看健康报告
2. 监控数据质量分数
3. 更新数据源配置

### 异常处理
1. 数据源不可用 → 自动切换备用源
2. 数据质量过低 → 警告用户并标注
3. 系统异常 → 记录日志并通知

---

**文档版本**: v1.0
**最后更新**: 2026-04-22
**作者**: 小灰灰 🐕
