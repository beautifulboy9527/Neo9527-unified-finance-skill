---
name: citation-validator
description: >
  引用验证体系 - 数据来源可信度评级
  
  功能:
  - A-E级数据来源评级
  - 自动标注数据来源
  - 交叉验证提示
  - 引用格式规范化
  
  适用场景:
  - 金融分析报告
  - 投资研究报告
  - 任何需要引用验证的内容
  
version: 1.0.0
author: Neo9527
---

# 引用验证体系 (Citation Validator)

> 数据可信度是分析报告的生命线

## 一、数据来源评级体系

### A级 - 最权威 (Primary Sources)

| 来源类型 | 示例 | 说明 |
|---------|------|------|
| 官方数据 | 区块链浏览器、交易所API | 原始数据，最高可信度 |
| 白皮书 | 项目官方白皮书 | 项目方正式声明 |
| 监管文件 | SEC文件、年报 | 法定披露文件 |
| 智能合约 | 链上合约代码 | 不可篡改的代码 |

**标注格式**:
```
> 来源: Etherscan (A级) | 2026-04-17 | [链接](url)
```

---

### B级 - 高可信 (Secondary Sources)

| 来源类型 | 示例 | 说明 |
|---------|------|------|
| 数据聚合 | DeFiLlama, CoinGecko, Dune Analytics | 多源聚合数据 |
| 区块链工具 | Etherscan, Solscan, Blockchain.com | 链上数据查询 |
| 研究机构 | Messari, Glassnode, Dune | 专业分析工具 |
| 官方渠道 | 项目官网、官方Twitter | 项目方发布 |

**标注格式**:
```
> 来源: DeFiLlama (B级) | 2026-04-17 | [链接](url)
```

---

### C级 - 中等可信 (Tertiary Sources)

| 来源类型 | 示例 | 说明 |
|---------|------|------|
| 专业媒体 | CoinDesk, The Block, Decrypt | 行业新闻媒体 |
| 分析师报告 | 投行研究报告 | 专业分析 |
| KOL分析 | 知名分析师文章 | 个人观点 |
| 社区报告 | DAO治理报告 | 社区产出 |

**标注格式**:
```
> 来源: CoinDesk (C级) | 2026-04-17 | [链接](url)
```

---

### D级 - 低可信 (Informal Sources)

| 来源类型 | 示例 | 说明 |
|---------|------|------|
| 社交媒体 | Twitter/X, Telegram, Discord | 用户生成内容 |
| 社区讨论 | Reddit, 论坛 | 社区观点 |
| 个人博客 | Medium, Substack | 个人观点 |
| 非官方渠道 | 转发消息、二手信息 | 需要验证 |

**标注格式**:
```
> 来源: Twitter @handle (D级) | 2026-04-17 | [链接](url)
```

**注意**: D级来源需要交叉验证后才能作为主要依据

---

### E级 - 未验证 (Unverified Sources)

| 来源类型 | 示例 | 说明 |
|---------|------|------|
| 未验证 | 匿名来源、未经证实消息 | 需要验证 |
| 过时数据 | 超过有效期的数据 | 可能已失效 |
| 争议内容 | 存在争议的信息 | 需要多方核实 |

**标注格式**:
```
> 来源: 未验证 (E级) | ⚠️ 需要交叉验证
```

---

## 二、使用方法

### Python API

```python
from skills.shared.citation_validator import CitationValidator

# 创建验证器
validator = CitationValidator()

# 获取来源评级
rating = validator.get_rating("DeFiLlama")
# 返回: 'B'

# 生成引用标注
citation = validator.cite(
    source="DeFiLlama",
    url="https://defillama.com/protocol/ethereum",
    date="2026-04-17"
)
# 返回: "> 来源: DeFiLlama (B级) | 2026-04-17 | [链接](https://defillama.com/protocol/ethereum)"

# 批量验证
sources = ["DeFiLlama", "CoinGecko", "Twitter @user"]
ratings = validator.batch_rate(sources)
# 返回: {'DeFiLlama': 'B', 'CoinGecko': 'B', 'Twitter @user': 'D'}
```

### 在报告中使用

```python
# 在分析报告中添加引用
def add_citation_to_report(data_point, source, url):
    validator = CitationValidator()
    rating = validator.get_rating(source)
    
    return {
        'data': data_point,
        'source': source,
        'rating': rating,
        'citation': validator.cite(source, url)
    }
```

---

## 三、交叉验证规则

### 规则1: 核心数据必须A/B级

```python
def validate_core_data(source_rating):
    if source_rating in ['E', 'D']:
        return {
            'valid': False,
            'warning': '核心数据必须来自A/B级来源'
        }
    return {'valid': True}
```

### 规则2: D级来源需要交叉验证

```python
def validate_d_level(sources):
    d_sources = [s for s in sources if get_rating(s) == 'D']
    if d_sources:
        return {
            'valid': False,
            'warning': f'D级来源需要交叉验证: {d_sources}',
            'action': '请用A/B级来源核实'
        }
    return {'valid': True}
```

### 规则3: 关键结论至少2个独立来源

```python
def validate_conclusion(sources):
    unique_sources = set(sources)
    if len(unique_sources) < 2:
        return {
            'valid': False,
            'warning': '关键结论需要至少2个独立来源'
        }
    return {'valid': True}
```

---

## 四、来源识别映射

### 加密货币数据源

| 来源名称 | 评级 | 类别 |
|---------|------|------|
| Etherscan | A | 区块链浏览器 |
| DeFiLlama | B | 数据聚合 |
| CoinGecko | B | 价格数据 |
| CoinMarketCap | B | 价格数据 |
| Dune Analytics | B | 链上分析 |
| Glassnode | B | 链上分析 |
| Messari | B | 研究机构 |
| Nansen | B | 链上分析 |
| CoinDesk | C | 媒体 |
| The Block | C | 媒体 |
| Decrypt | C | 媒体 |
| Twitter/X | D | 社交媒体 |
| Telegram | D | 社交媒体 |
| Discord | D | 社交媒体 |
| Reddit | D | 社区 |

### 股票数据源

| 来源名称 | 评级 | 类别 |
|---------|------|------|
| 交易所公告 | A | 官方 |
| SEC文件 | A | 监管 |
| 年报/季报 | A | 官方 |
| Wind | B | 数据终端 |
| Bloomberg | B | 数据终端 |
| Reuters | B | 新闻机构 |
| 财经媒体 | C | 媒体 |
| 分析师报告 | C | 分析 |

---

## 五、报告模板集成

### 在HTML报告中显示

```html
<div class="citation-card">
    <div class="data-point">
        {{ data_point }}
    </div>
    <div class="source-rating {{ rating_class }}">
        {{ source }} ({{ rating }}级)
    </div>
    <div class="citation-date">
        {{ date }}
    </div>
</div>
```

### 样式建议

```css
.rating-A { color: #10b981; } /* 绿色 */
.rating-B { color: #3b82f6; } /* 蓝色 */
.rating-C { color: #f59e0b; } /* 黄色 */
.rating-D { color: #ef4444; } /* 红色 */
.rating-E { color: #6b7280; } /* 灰色 */
```

---

## 六、自动化验证

### 在报告生成时自动验证

```python
def generate_report_with_validation(symbol):
    # 获取数据
    data = fetch_data(symbol)
    
    # 验证每个数据点
    for point in data:
        point['citation'] = validator.cite(
            source=point['source'],
            url=point['url'],
            date=point['date']
        )
        
        # 低评级数据添加警告
        if validator.get_rating(point['source']) in ['D', 'E']:
            point['warning'] = '⚠️ 需要交叉验证'
    
    return generate_html(data)
```

---

## 七、最佳实践

1. **核心数据优先A/B级**: 价格、TVL、链上数据等核心指标
2. **观点类可用C/D级**: 分析观点、市场情绪
3. **D/E级必须标注**: 明确告知用户可信度
4. **关键结论多源验证**: 至少2个独立来源
5. **定期更新评级**: 来源可信度可能变化

---

*by Neo9527 Finance Skill v4.8 | 2026-04-17*
