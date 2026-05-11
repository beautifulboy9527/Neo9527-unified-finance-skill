# Phase 4: 数据源稳定性

**目标**: 确保选股器在数据源故障时仍能正常工作，并提供数据质量评分

---

## 参考架构

参考项目中已有成熟的数据处理模块：

| 模块 | 文件 | 功能 |
|------|------|------|
| DataSourceHealth | `data_source_manager.py` | 数据源健康状态跟踪 |
| DataCache | `data_source_manager.py` | 数据缓存（TTL 5分钟） |
| RetryManager | `data_source_manager.py` | 重试管理器（指数退避） |
| DataSourceManager | `data_source_manager.py` | 健康检查 + 缓存 + 重试 |
| MultiSourceManager | `multi_source_manager.py` | 多数据源自动降级 |
| UnifiedDataLayer | `unified_data_layer.py` | 数据验证 + 缺失值处理 + 质量评分 |

---

## 降级策略

```
优先级:
1. yfinance (主源) - 全球市场支持
2. akshare/东方财富 (备用) - A股专用
3. 新浪财经 (兜底) - 实时行情

自动切换逻辑:
- 主源失败 → 立即切换备用源
- 连续失败3次 → 标记不可用，排除优先级
- 成功后 → 恢复优先级
```

---

## 实现步骤

### 1. 整合 MultiSourceManager

```python
# 选股器数据获取改为:
from scripts.features.multi_source_manager import get_stock_data_with_fallback

# 替代直接调用 akshare
data = get_stock_data_with_fallback(symbol)
```

### 2. 整合 UnifiedDataLayer

```python
# 选股结果添加数据质量评分
from scripts.features.unified_data_layer import process_stock_data

processed = process_stock_data(symbol, raw_data, hist_data)
# 返回包含 data_quality_score 的结果
```

### 3. API 端点

```
GET /api/data-source/health     # 数据源健康报告
GET /api/data-source/status     # 当前可用数据源
POST /api/data-source/test      # 测试指定数据源
```

### 4. CLI 支持

```bash
python finance.py screen --source yfinance    # 指定数据源
python finance.py screen --fallback           # 启用自动降级
python finance.py data-health                 # 查看数据源健康报告
```

---

## 数据质量评分

| 分数 | 标签 | 说明 |
|------|------|------|
| ≥90 | 高置信度 ✅ | 数据完整可靠 |
| ≥70 | 中等置信度 ⚠️ | 部分数据为估算值 |
| ≥50 | 低置信度 ❌ | 大量数据缺失 |
| <50 | 不可用 🚫 | 数据严重缺失 |

---

## 缺失值降级方案

参考 `unified_data_layer.py` 中的实现：

1. **支撑阻力位缺失** → 使用 ATR 计算
2. **行业信息缺失** → 根据股票代码推断
3. **财务数据缺失** → 使用行业默认值
4. **价格数据缺失** → 从备用数据源补充

---

## 进度

- [x] 整合 MultiSourceManager 到 enhanced_screener.py ✅
- [x] 整合 UnifiedDataLayer 数据质量评分 ✅
- [x] API 端点 `/api/data-source/health` ✅
- [x] CLI 支持 `--no-fallback` 和 `data-health` ✅
- [x] 测试数据源降级场景 ✅

---

*Completed: 2026-05-11*