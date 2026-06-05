# Phase 6 Natural Language Entry

目标：让用户不用记 `finance.py` 的完整命令，只用一句自然语言就能触发已有金融能力。

## 新增入口

```bash
python finance.py ask "帮我看下 AAPL"
python finance.py ask "生成 002050 的正式研报"
python finance.py ask "把 002241 加到自选，目标 28，止损 18"
python finance.py ask "分析组合风险：600519 40%，002241 30%，000858 30%"
python finance.py ask "筛选前10只价值股，要求金叉并按评分排序"
```

如果只想看系统会调用什么命令：

```bash
python finance.py ask "生成 002050 的正式研报" --dry-run
```

## 当前支持的用户说法

| 用户意图 | 示例说法 | 路由到 |
|---|---|---|
| 快速看一只股票 | 帮我看下 AAPL | `analyze AAPL` |
| 生成正式研报 | 生成 002050 的正式研报 | `report 002050 --style kami --live-data-check --require-technical-data --strict-data --enforce-freshness` |
| 财报体检 | 给 AAPL 做财报体检 | `health AAPL` |
| 财务异常检测 | 检查 600519 有没有财务异常 | `check 600519` |
| 风险预警 | 看看 AAPL MSFT 的风险 | `alerts AAPL MSFT` |
| 估值 | 算一下 AAPL 估值 | `value AAPL` |
| 情景估值 | 给 AAPL 做估值工作台 | `workbench AAPL` |
| 财报预测 | 预测 AAPL 财报 | `preview AAPL` |
| 财报回顾 | 回顾 AAPL 财报 | `recap AAPL` |
| 多股业绩比较 | 对比 AAPL MSFT GOOGL 业绩 | `compare AAPL MSFT GOOGL` |
| A股筛选 | 筛选价值股，要求金叉并按评分排序 | `screen --strategy value --technical golden-cross --scoring` |
| 自选股添加 | 把 002241 加到自选，目标 28，止损 18 | `watchlist add 002241 --target 28 --stop 18` |
| 自选股检查 | 检查自选股风险 | `watchlist check` |
| 组合风险 | 分析组合风险：600519 40%，002241 30% | `portfolio warnings 600519,002241 --weights 0.4,0.3` |
| 数据源体检 | 检查数据源状态 | `doctor` |

## 设计原则

1. 先做确定性规则，不引入 LLM 依赖，保证 CLI/API 都能稳定复用。
2. 自然语言入口只负责路由，不改动底层金融分析、估值、研报生成逻辑。
3. 对正式报告默认开启严格数据、新鲜度和技术数据检查，避免给用户生成看似完整但输入不足的报告。
4. 对无法识别的请求返回可执行提示，而不是猜测高风险动作。

## 后续升级建议

1. 将 `route_query()` 暴露到 API：新增 `/api/ask/route` 和 `/api/ask/execute`。
2. 为 Codex skill 增加用户触发短语，把“帮我看、帮我筛、帮我盯、帮我出报告”写入 `SKILL.md`。
3. 增加交互式缺参补全：例如用户说“生成研报”但没有股票代码时，返回需要补充的字段。
4. 增加场景模板：快速分析、正式研报、自选股托管、组合风险、A股筛选。
