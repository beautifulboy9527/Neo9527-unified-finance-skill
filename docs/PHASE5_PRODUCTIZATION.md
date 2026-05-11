# Phase 5: 产品化功能 - 监控告警、自选股管理、报告生成

## 概述

Phase 5 整合现有产品化功能模块，提供完整的投资者工具链：

- **监控告警** - 基于 `alert_manager.py` 的目标价/止损价监控
- **自选股管理** - 整合 `alerts.json` + `portfolio_manager.py`
- **报告生成** - 整合 `investment_plan.py` + `opportunity_pipeline.py`

## 参考模块

| 功能 | 参考文件 | 核心逻辑 |
|------|----------|----------|
| 警报管理 | `scripts/alert_manager.py` | 目标价/止损价触发检查 |
| 组合管理 | `scripts/features/portfolio_manager.py` | VaR/CVaR、Markowitz优化 |
| 投资计划 | `skills/stock-skill/investment_plan.py` | HTML/CSV报告生成 |
| 机会短名单 | `skills/stock-skill/opportunity_pipeline.py` | 评分排名 |

## 实现方案

### 5.1 WatchlistManager (自选股管理)

**整合点**：
- `alerts.json` → 持久化存储
- `alert_manager.py` → 增删改查 + 触发检查
- 扩展：添加备注、分组、优先级

**新增字段**：
```json
{
  "id": 1,
  "symbol": "002241",
  "target": 28.0,
  "stop": 18.0,
  "notes": "歌尔股份，VR龙头",
  "group": "科技成长",
  "priority": "高",
  "created_at": "...",
  "last_triggered": null,
  "enabled": true
}
```

### 5.2 PortfolioSkill (组合分析)

**整合点**：
- `portfolio_manager.py` → VaR/CVaR、相关性矩阵
- 扩展：组合风险评分、仓位建议

**新增功能**：
- 组合健康度评分
- 风险预警（单股占比过高）
- Kelly仓位建议

### 5.3 ReportGenerator (报告生成)

**整合点**：
- `investment_plan.py` → 投资跟踪计划
- `opportunity_pipeline.py` → 机会短名单
- 扩展：一键生成完整投研报告

**报告类型**：
- 投资跟踪计划 (HTML/CSV)
- 机会短名单 (HTML)
- 组合风险报告 (JSON)

## API 端点设计

```
/api/watchlist          # GET: 列表, POST: 添加
/api/watchlist/{id}     # DELETE: 移除, PATCH: 更新
/api/watchlist/check    # POST: 检查触发警报

/api/portfolio          # POST: 组合风险分析
/api/portfolio/optimize # POST: Markowitz优化

/api/report/plan        # POST: 投资跟踪计划
/api/report/shortlist   # POST: 机会短名单
/api/report/portfolio   # POST: 组合报告
```

## CLI 命令设计

```bash
# 自选股管理
python finance.py watchlist list
python finance.py watchlist add <symbol> --target 28 --stop 18 --notes "备注"
python finance.py watchlist remove <id>
python finance.py watchlist check

# 组合分析
python finance.py portfolio analyze <symbols> --weights 0.3,0.3,0.4
python finance.py portfolio optimize <symbols> --method markowitz|riskparity

# 报告生成
python finance.py report plan --output plan.html
python finance.py report shortlist candidates.csv --top 10 --output shortlist.html
python finance.py report portfolio <symbols> --output portfolio.json
```

## Skills 规范检查清单

- [x] YAML frontmatter (name, description, version)
- [x] 三层架构 (L1 SKILL.md + L2 主体 + L3 references)
- [x] CLI 命令支持
- [x] API 端点支持
- [x] Skill 注册到 SkillRegistry
- [x] 文档更新 (SKILL.md)

## 文件结构

```
skills/stock-skill/
├── watchlist_manager.py    # 新增：自选股管理
├── portfolio_skill.py      # 新增：组合分析 Skill
├── report_generator.py     # 新增：报告生成整合
├── enhanced_screener.py    # Phase 3 已完成
├── screener_data_source.py # Phase 4 已完成
└── SKILL.md                # 更新：添加 Phase 5 模块
```

## 开发顺序

1. ✅ 创建 Phase 5 文档
2. ⏳ WatchlistManager 实现
3. ⏳ PortfolioSkill 实现
4. ⏳ API 端点添加
5. ⏳ CLI 命令添加
6. ⏳ SKILL.md 更新
7. ⏳ Git 提交