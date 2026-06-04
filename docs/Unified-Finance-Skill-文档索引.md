# Unified Finance Skill - 文档索引

> **最后更新**: 2026-04-16 08:07
> **版本**: v3.1

---

## 📚 文档清单

### 核心文档

| 文档名称 | 路径 | 说明 | 用途 |
|---------|------|------|------|
| **开发历程** | `D:\OpenClaw\outputs\Unified-Finance-Skill-开发历程.md` | 完整的开发文档 | 开发日志 + README |
| **快速参考** | `D:\OpenClaw\outputs\Unified-Finance-Skill-快速参考.md` | 快速参考卡 | 日常使用速查 |

### 整合文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| 饕餮整合方案 | `skills/unified-finance-skill/TAOTIE-INTEGRATION-PLAN.md` | 整合方法论 |
| 饕餮整合报告 | `skills/unified-finance-skill/TAOTIE-COMPLETION-REPORT.md` | Phase 3 完成报告 |
| 技术分析评估 | `skills/unified-finance-skill/TECHNICAL-ANALYSIS-EVALUATION.md` | Phase 4 评估 |
| sm-analyze评估 | `skills/unified-finance-skill/SM-ANALYZE-INTEGRATION-PLAN.md` | 三层框架评估 |
| 入场信号评估 | `skills/unified-finance-skill/ENTRY-SIGNALS-INTEGRATION-PLAN.md` | 信号库评估 |
| gmgn评估 | `skills/unified-finance-skill/GMGN-MARKET-EVALUATION.md` | DEX数据评估 |

---

## 📂 文件组织规范

### 输出目录结构

```
D:\OpenClaw\outputs\
├── reports\           # 分析报告
├── charts\            # 图表文件
├── data\              # 数据文件
├── logs\              # 日志文件
├── Unified-Finance-Skill-开发历程.md  # 开发文档
└── Unified-Finance-Skill-快速参考.md  # 快速参考
```

### ⚠️ 重要规定

**禁止**:
- ❌ 不要将输出文件写入 skills 安装目录
- ❌ 不要将输出文件写入 workspace 目录
- ❌ **不要在 C 盘生成大文件**

**规定来源**: `AGENTS.md` - Output Directory 章节

---

## 🔄 文档更新流程

### 新增文档

```bash
# 1. 创建文档
# 2. 保存到 D:\OpenClaw\outputs\
# 3. 更新本索引文件
```

### 更新文档

```bash
# 1. 编辑文档
# 2. 更新 "最后更新" 时间
# 3. 如有重大变更，更新版本号
```

---

## 📊 文档统计

| 项目 | 数量 |
|------|------|
| 核心文档 | 2 |
| 整合文档 | 6 |
| 总字数 | 20,000+ |
| 最后更新 | 2026-04-16 |

---

## 🔗 快速链接

### 项目资源
- **GitHub**: https://github.com/beautifulboy9527/unified-finance-skill
- **本地路径**: `C:\Users\Administrator\.openclaw\workspace\.agents\skills\unified-finance-skill\`

### 相关文件
- **主入口**: `scripts/finance.py`
- **配置文件**: `scripts/config.json`
- **测试文件**: `scripts/test_*.py`

---

*文档索引 | 遵循 AGENTS.md 输出规范*
