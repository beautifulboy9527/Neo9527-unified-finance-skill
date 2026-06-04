---
name: risk-monitor
description: >
  风险监控清单 - 投资后续跟踪体系
  
  功能:
  - 强化条件识别
  - 预警条件监控
  - 退出触发判断
  - 监控清单生成
  
  适用场景:
  - 投资后持续跟踪
  - 风险预警提醒
  - 条件触发决策
  
version: 1.0.0
author: Neo9527
---

# 风险监控清单 (Risk Monitor)

> 投资不是一次性行为，而是持续跟踪过程

## 一、监控清单架构

### 三级监控体系

```
┌─────────────────────────────────────────────┐
│  ✅ 强化条件 (Strengthen)                    │
│  触发后强化看涨逻辑，可考虑加仓              │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  ⚠️ 预警条件 (Warning)                       │
│  触发后需要关注，但不一定立即行动            │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  🛑 退出触发 (Exit)                          │
│  触发后立即退出，执行止损/止盈               │
└─────────────────────────────────────────────┘
```

---

## 二、加密货币监控清单

### ✅ 强化条件

| 条件 | 触发值 | 说明 |
|------|--------|------|
| TVL突破 | 创历史新高 | 生态资金持续流入 |
| 鲸鱼吸筹 | 连续7日持仓增加>2% | 大资金看好 |
| 协议收入 | 月度新高 | 真实收益增长 |
| 开发活跃 | 提交量周环比+50% | 项目持续迭代 |
| 生态扩张 | 新增协议集成>5个/月 | 生态繁荣 |
| 代币销毁 | 销毁量>1%流通量 | 通缩效应 |
| 机构入场 | 新增机构持仓披露 | 聪明钱认可 |

### ⚠️ 预警条件

| 条件 | 触发值 | 说明 |
|------|--------|------|
| TVL下降 | 单日下降>10% | 资金流出 |
| 鲸鱼派发 | 连续3日持仓减少 | 大资金流出 |
| 代币解锁 | >5%流通量解锁 | 抛压增加 |
| 开发停滞 | 2周无代码提交 | 项目停滞 |
| 安全预警 | 审计发现问题 | 安全风险 |
| 监管关注 | 监管机构问询 | 合规风险 |
| 竞争加剧 | 竞品TVL超越 | 市场份额下降 |

### 🛑 退出触发

| 条件 | 触发值 | 说明 |
|------|--------|------|
| 关键支撑破位 | 跌破支撑位>15% | 技术破位 |
| 协议被黑 | 安全事件 | 本金风险 |
| 团队争议 | 核心成员离职/争议 | 治理风险 |
| 监管重大利空 | 禁令/起诉 | 合规危机 |
| 流动性危机 | TVL下降>50% | 生态崩溃 |
| 重大漏洞 | 核心合约漏洞 | 安全危机 |

---

## 三、股票监控清单

### ✅ 强化条件

| 条件 | 触发值 | 说明 |
|------|--------|------|
| 业绩超预期 | 净利润超预期>10% | 基本面改善 |
| 订单增长 | 新增订单>预期 | 未来收入可期 |
| 机构增持 | 机构持仓增加>5% | 聪明钱认可 |
| 行业利好 | 政策支持/行业景气 | 外部环境改善 |
| 估值修复 | PE回归历史中位数 | 估值回归 |
| 分红增加 | 分红提升>10% | 股东回报提升 |

### ⚠️ 预警条件

| 条件 | 触发值 | 说明 |
|------|--------|------|
| 业绩不及预期 | 净利润低于预期>10% | 基本面恶化 |
| 现金流恶化 | 经营现金流/净利润<0.5 | 盈利质量下降 |
| 应收账款增加 | 周转天数增加>20% | 回款风险 |
| 存货积压 | 周转率下降>20% | 销售不畅 |
| 高管减持 | 核心高管减持>1% | 内部看淡 |
| 诉讼风险 | 重大诉讼 | 法律风险 |

### 🛑 退出触发

| 条件 | 触发值 | 说明 |
|------|--------|------|
| 财务造假 | 审计保留意见 | 信任危机 |
| 连续亏损 | 连续2年亏损 | 持续经营风险 |
| 债务危机 | 资产负债率>80% | 偿债风险 |
| 退市风险 | 触发退市条件 | 流动性危机 |
| 行业衰退 | 行业需求下降>30% | 基本面反转 |

---

## 四、使用方法

### Python API

```python
from skills.shared.risk_monitor import RiskMonitor

# 创建监控器
monitor = RiskMonitor(asset_type='crypto')

# 检查条件
status = monitor.check({
    'tvl_change_24h': -12,
    'whale_holding_change_7d': 3,
    'price_drop_from_support': -5
})

# 返回:
# {
#     'alerts': ['⚠️ TVL单日下降>10%'],
#     'strengthens': ['✅ 鲸鱼连续7日持仓增加>2%'],
#     'exits': [],
#     'recommendation': 'monitor'  # hold/monitor/exit
# }

# 生成监控清单
checklist = monitor.generate_checklist(symbol='ETH')
```

### 在报告中使用

```python
# 在分析报告中添加监控清单
def add_monitoring_checklist(report, symbol):
    monitor = RiskMonitor(asset_type='crypto')
    checklist = monitor.generate_checklist(symbol)
    
    report.add_section('监控清单', checklist)
    return report
```

---

## 五、监控清单生成模板

### Markdown格式

```markdown
## 📊 监控清单

### ✅ 强化条件
- [ ] TVL突破历史新高
- [ ] 鲸鱼持仓连续7日增加
- [ ] 协议收入创月度新高
- [ ] 开发活跃度提升

### ⚠️ 预警条件
- [ ] TVL单日下降>10%
- [ ] 鲸鱼持仓连续3日减少
- [ ] 代币大规模解锁(>5%流通量)
- [ ] 安全审计发现问题

### 🛑 退出触发
- [ ] 跌破关键支撑位>15%
- [ ] 协议被黑客攻击
- [ ] 核心团队离职/争议
- [ ] 监管重大利空
```

### HTML格式

```html
<div class="monitoring-checklist">
    <h3>📊 监控清单</h3>
    
    <div class="strengthen-section">
        <h4>✅ 强化条件</h4>
        <ul>
            <li>TVL突破历史新高 → 考虑加仓</li>
            <li>鲸鱼持仓连续7日增加 → 强化持有</li>
        </ul>
    </div>
    
    <div class="warning-section">
        <h4>⚠️ 预警条件</h4>
        <ul>
            <li>TVL单日下降>10% → 密切关注</li>
            <li>鲸鱼持仓连续3日减少 → 准备减仓</li>
        </ul>
    </div>
    
    <div class="exit-section">
        <h4>🛑 退出触发</h4>
        <ul>
            <li>跌破关键支撑位>15% → 立即止损</li>
            <li>协议被黑客攻击 → 立即退出</li>
        </ul>
    </div>
</div>
```

---

## 六、自动化监控

### 定时检查脚本

```python
import schedule
import time

def monitor_positions():
    """定时监控持仓"""
    positions = load_positions()  # 加载持仓
    
    for pos in positions:
        monitor = RiskMonitor(asset_type=pos['type'])
        data = fetch_latest_data(pos['symbol'])
        status = monitor.check(data)
        
        if status['exits']:
            send_alert(f"🛑 退出警报: {pos['symbol']}\n" + 
                      "\n".join(status['exits']))
        elif status['alerts']:
            send_alert(f"⚠️ 预警: {pos['symbol']}\n" + 
                      "\n".join(status['alerts']))

# 每小时检查一次
schedule.every().hour.do(monitor_positions)
```

---

## 七、与其他模块集成

### 与引用验证集成

```python
# 检查监控条件时标注数据来源
def check_with_citation(monitor, data):
    from skills.shared.citation_validator import CitationValidator
    validator = CitationValidator()
    
    results = monitor.check(data)
    
    # 为每个判断添加引用
    for alert in results['alerts']:
        alert['citation'] = validator.cite(
            source=data['source'],
            url=data['url'],
            date=data['date']
        )
    
    return results
```

### 与报告生成器集成

```python
# 在报告末尾自动添加监控清单
def generate_report_with_monitoring(symbol, asset_type='crypto'):
    # 生成分析报告
    report = generate_analysis_report(symbol)
    
    # 添加监控清单
    monitor = RiskMonitor(asset_type=asset_type)
    checklist = monitor.generate_checklist(symbol)
    report.add_section('监控清单', checklist)
    
    return report
```

---

## 八、最佳实践

1. **定期检查**: 建议每日/每周检查监控条件
2. **多维度验证**: 不要只看单一指标
3. **及时响应**: 退出触发出现时果断行动
4. **记录跟踪**: 记录每次触发和后续行动
5. **动态调整**: 根据市场变化调整监控条件

---

*by Neo9527 Finance Skill v4.8 | 2026-04-17*
