---
name: deep-research-skill
description: |
  股票深度研报 - 8阶段投研框架。
  包含公司事实底座、行业周期、业务拆解、财务质量、股权治理、市场分歧、估值护城河、综合报告。
  输出专业HTML研报。
metadata:
  openclaw:
    emoji: "📊"
    triggers:
      - "深度研报"
      - "投资尽调"
      - "8阶段"
      - "研报"
version: 1.2.0
---

# Deep Research Skill

股票深度研报模块，基于8阶段投研框架。

## 使用方式

```python
from skills.stock_skill.deep_research.analyzer import StockAnalyzer
from skills.stock_skill.deep_research.report_html import generate_stock_html

# 分析
analyzer = StockAnalyzer(style='value')
result = analyzer.analyze('AAPL', depth='standard')

# 生成HTML报告
html = generate_stock_html(result)
```

## 8阶段框架

1. **Phase 1**: 公司事实底座
2. **Phase 2**: 行业周期分析
3. **Phase 3**: 业务拆解
4. **Phase 4**: 财务质量分析 ⭐
5. **Phase 5**: 股权治理分析
6. **Phase 6**: 市场分歧分析
7. **Phase 7**: 估值与护城河 ⭐
8. **Phase 8**: 综合报告

## 投资风格

- `value`: 价值投资 (侧重财务、治理、估值)
- `growth`: 成长投资 (侧重业务、行业)
- `turnaround`: 困境反转 (侧重财务、治理)
- `dividend`: 红利投资 (侧重财务、估值)

## 输出

- 综合评级: 🟢🟢🟢 / 🟡🟡🟡 / 🔴🔴
- 评分: 0-5分
- HTML研报: 深蓝/金色主题

---

*v1.2 - 专业研报模块*
