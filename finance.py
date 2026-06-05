#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo9527 Unified Finance Skill CLI (P1: modular architecture)

Commands are loaded from cli/ directory:
- cli/analysis.py: analyze, check, health, value, research
- cli/report.py: report
- cli/screening.py: screen, discover, board
- cli/earnings.py: earnings, preview, recap, compare
- cli/watchlist.py: watchlist, alerts, monitor
- cli/crypto.py: crypto (quote/orderbook/kline/trending/search/multi/analyze)
- cli/forex.py: forex (quote/analyze)
- cli/onchain.py: onchain (tvl/protocol/whale)
- cli/signal.py: signal (多市场信号检测)
- cli/portfolio.py: portfolio
- cli/system.py: data-health, doctor, ask, workbench
"""

import os
import sys

SKILLS_DIR = os.path.dirname(os.path.abspath(__file__))

# Import all command functions from cli modules
from cli.analysis import cmd_analyze, cmd_check, cmd_health, cmd_value, cmd_research
from cli.report import cmd_report
from cli.screening import cmd_screen, cmd_discover, cmd_board
from cli.earnings import cmd_earnings, cmd_preview, cmd_recap, cmd_compare
from cli.watchlist import cmd_watchlist, cmd_alerts, cmd_monitor
from cli.portfolio import cmd_portfolio
from cli.system import cmd_data_health, cmd_doctor, cmd_ask, cmd_workbench
from cli.a_share import cmd_a_share
from cli.backtest import cmd_backtest
from cli.crypto import cmd_crypto
from cli.forex import cmd_forex
from cli.onchain import cmd_onchain
from cli.signal import cmd_signal


def main():
    parser = argparse.ArgumentParser(
        description='Neo9527 Finance CLI - 统一金融分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # ask 命令 - 自然语言入口
    parser_ask = subparsers.add_parser('ask', help='自然语言入口：把一句话转成金融分析命令')
    parser_ask.add_argument('query', help='用户请求，例如：帮我看 AAPL，生成 002050 研报')
    parser_ask.add_argument('--dry-run', action='store_true', help='只显示将执行的命令，不真正运行')
    parser_ask.set_defaults(func=cmd_ask)
    
    # analyze 命令
    parser_analyze = subparsers.add_parser('analyze', help='快速分析股票')
    parser_analyze.add_argument('symbol', help='股票代码')
    parser_analyze.set_defaults(func=cmd_analyze)
    parser_analyze.add_argument('--full', action='store_true', help='全链路分析: 财务+估值+技术+信号+风控+溯源')
    parser_analyze.add_argument('--auto-report', action='store_true', help='全链路分析后自动生成HTML报告')
    parser_analyze.add_argument('--skip-fundamental', action='store_true', help='跳过财务分析')
    parser_analyze.add_argument('--skip-valuation', action='store_true', help='跳过估值分析')
    parser_analyze.add_argument('--skip-signals', action='store_true', help='跳过入场信号')
    parser_analyze.add_argument('--skip-risk', action='store_true', help='跳过风险分析')
    
    # screen 命令 (v3.0 增强版 - Phase 4)
    parser_screen = subparsers.add_parser('screen', help='A股选股 v3.0 (Phase 4)')
    parser_screen.add_argument('--scope', default='hs300', 
        choices=['hs300', 'zz500', 'a50', 'all'],
        help='选股范围，默认hs300')
    parser_screen.add_argument('--strategy', '-s',
        choices=['value', 'growth', 'dividend', 'garp', 'turnaround', 'defensive', 'quality'],
        help='预设策略: value/growth/dividend/garp/turnaround/defensive/quality')
    parser_screen.add_argument('--technical', '-t', nargs='+',
        choices=['golden-cross', 'ma-bullish', 'volume-breakout', 'rsi-oversold', 'bollinger-squeeze', 'consolidation-breakout'],
        help='技术面条件: golden-cross/ma-bullish/volume-breakout/rsi-oversold')
    parser_screen.add_argument('--scoring', action='store_true', help='启用多因子评分排序')
    parser_screen.add_argument('--industry', help='行业筛选，如: 银行, 医药')
    parser_screen.add_argument('--top', type=int, default=20, help='展示TOP N，默认20')
    parser_screen.add_argument('--pe-max', type=float, help='PE上限')
    parser_screen.add_argument('--pb-max', type=float, help='PB上限')
    parser_screen.add_argument('--roe-min', type=float, help='ROE下限百分比')
    parser_screen.add_argument('--debt-max', type=float, help='负债率上限百分比')
    parser_screen.add_argument('--margin-min', type=float, help='净利率下限百分比')
    parser_screen.add_argument('--no-fallback', action='store_true', help='禁用数据源自动降级')
    parser_screen.set_defaults(func=cmd_screen)
    
    # data-health 命令 (Phase 4 新增)
    parser_data_health = subparsers.add_parser('data-health', help='数据源健康检查')
    parser_data_health.add_argument('--test', action='store_true', help='测试数据源连通性')
    parser_data_health.add_argument('--scope', default='hs300', help='测试范围')
    parser_data_health.set_defaults(func=cmd_data_health)
    
    # watchlist 命令 (Phase 5 新增)
    parser_watchlist = subparsers.add_parser('watchlist', help='自选股管理')
    watchlist_subparsers = parser_watchlist.add_subparsers(dest='watchlist_action', help='自选股操作')
    
    # watchlist list
    wl_list = watchlist_subparsers.add_parser('list', help='列出自选股')
    wl_list.add_argument('--group', help='按分组筛选')
    wl_list.add_argument('--priority', choices=['高', '中', '低'], help='按优先级筛选')
    
    # watchlist add
    wl_add = watchlist_subparsers.add_parser('add', help='添加自选股')
    wl_add.add_argument('symbol', help='股票代码')
    wl_add.add_argument('--target', type=float, help='目标价')
    wl_add.add_argument('--stop', type=float, help='止损价')
    wl_add.add_argument('--notes', help='备注')
    wl_add.add_argument('--group', default='默认', help='分组')
    wl_add.add_argument('--priority', default='中', choices=['高', '中', '低'], help='优先级')
    
    # watchlist remove
    wl_remove = watchlist_subparsers.add_parser('remove', help='移除自选股')
    wl_remove.add_argument('id', type=int, help='自选股ID')
    
    # watchlist check
    wl_check = watchlist_subparsers.add_parser('check', help='检查触发条件')
    
    # watchlist summary
    wl_summary = watchlist_subparsers.add_parser('summary', help='统计报告')
    
    # watchlist groups
    wl_groups = watchlist_subparsers.add_parser('groups', help='列出分组')
    
    parser_watchlist.set_defaults(func=cmd_watchlist)
    
    # portfolio 命令 (Phase 5 新增)
    parser_portfolio = subparsers.add_parser('portfolio', help='组合分析')
    portfolio_subparsers = parser_portfolio.add_subparsers(dest='portfolio_action', help='组合操作')
    
    # portfolio analyze
    pf_analyze = portfolio_subparsers.add_parser('analyze', help='组合风险分析')
    pf_analyze.add_argument('symbols', help='股票代码列表 (逗号分隔)')
    pf_analyze.add_argument('--weights', help='权重列表 (逗号分隔)')
    pf_analyze.add_argument('--days', type=int, default=365, help='历史天数')
    
    # portfolio optimize
    pf_optimize = portfolio_subparsers.add_parser('optimize', help='组合优化')
    pf_optimize.add_argument('symbols', help='股票代码列表 (逗号分隔)')
    pf_optimize.add_argument('--method', default='max_sharpe',
        choices=['max_sharpe', 'min_volatility', 'risk_parity'],
        help='优化方法')
    pf_optimize.add_argument('--days', type=int, default=365, help='历史天数')
    
    # portfolio kelly
    pf_kelly = portfolio_subparsers.add_parser('kelly', help='Kelly仓位计算')
    pf_kelly.add_argument('symbol', help='股票代码')
    pf_kelly.add_argument('--days', type=int, default=365, help='历史天数')
    
    # portfolio warnings
    pf_warnings = portfolio_subparsers.add_parser('warnings', help='风险预警')
    pf_warnings.add_argument('symbols', help='股票代码列表 (逗号分隔)')
    pf_warnings.add_argument('--weights', help='权重列表 (逗号分隔)')
    pf_warnings.add_argument('--days', type=int, default=365, help='历史天数')
    
    parser_portfolio.set_defaults(func=cmd_portfolio)
    
    # check 命令
    parser_check = subparsers.add_parser('check', help='财务异常检测')
    parser_check.add_argument('symbol', help='股票代码')
    parser_check.set_defaults(func=cmd_check)

    # health 命令
    parser_health = subparsers.add_parser('health', help='财报体检评分')
    parser_health.add_argument('symbol', help='股票代码')
    parser_health.add_argument('--gross-margin', type=float, help='外部传入毛利率(%)')
    parser_health.add_argument('--net-margin', type=float, help='外部传入净利率(%)')
    parser_health.add_argument('--roe', type=float, help='外部传入ROE(%)')
    parser_health.add_argument('--debt-ratio', type=float, help='外部传入资产负债率(%)')
    parser_health.add_argument('--revenue-growth', type=float, help='外部传入收入增速(%)')
    parser_health.add_argument('--profit-growth', type=float, help='外部传入利润增速(%)')
    parser_health.add_argument('--receivable-growth', type=float, help='外部传入应收账款增速(%)')
    parser_health.add_argument('--inventory-growth', type=float, help='外部传入存货增速(%)')
    parser_health.add_argument('--operating-cash-flow', type=float, help='外部传入经营现金流')
    parser_health.add_argument('--net-income', type=float, help='外部传入净利润')
    parser_health.set_defaults(func=cmd_health)

    # alerts 命令
    parser_alerts = subparsers.add_parser('alerts', help='股票/自选股风险预警')
    parser_alerts.add_argument('symbols', nargs='+', help='股票代码，可输入多个')
    parser_alerts.set_defaults(func=cmd_alerts)

    # workbench 命令
    parser_workbench = subparsers.add_parser('workbench', help='情景估值工作台')
    parser_workbench.add_argument('symbol', help='股票代码')
    parser_workbench.add_argument('--methods', default='all', choices=['all', 'dcf', 'relative', 'ddm'], help='估值方法')
    parser_workbench.add_argument('--discount-rate', type=float, help='折现率/WACC，例如 0.10')
    parser_workbench.add_argument('--terminal-growth', type=float, help='永续增长率，例如 0.025')
    parser_workbench.add_argument('--fcf-growth', type=float, help='自由现金流增长率，例如 0.04')
    parser_workbench.add_argument('--peer-pe', type=float, help='可比公司PE中位数')
    parser_workbench.add_argument('--peer-pb', type=float, help='可比公司PB中位数')
    parser_workbench.add_argument('--margin-of-safety', type=float, help='安全边际，例如 0.30')
    parser_workbench.add_argument('--current-price', type=float, help='外部传入当前价格')
    parser_workbench.add_argument('--eps', type=float, help='外部传入每股收益')
    parser_workbench.add_argument('--bps', type=float, help='外部传入每股净资产')
    parser_workbench.add_argument('--pe', type=float, help='外部传入当前PE')
    parser_workbench.add_argument('--pb', type=float, help='外部传入当前PB')
    parser_workbench.add_argument('--free-cash-flow', type=float, help='外部传入自由现金流')
    parser_workbench.add_argument('--shares-outstanding', type=float, help='外部传入总股本')
    parser_workbench.add_argument('--total-debt', type=float, help='外部传入有息负债')
    parser_workbench.add_argument('--cash', type=float, help='外部传入现金及等价物')
    parser_workbench.add_argument('--sector', help='外部传入板块')
    parser_workbench.add_argument('--industry', help='外部传入行业')
    parser_workbench.set_defaults(func=cmd_workbench)

    # a-share 命令 - A股特色数据 (P2)
    parser_ashare = subparsers.add_parser('a-share', help='A股特色数据: 龙虎榜/解禁/北向资金')
    ashare_sub = parser_ashare.add_subparsers(dest='a_share_subcmd', help='子命令')
    
    ashare_toplist = ashare_sub.add_parser('top-list', help='龙虎榜')
    ashare_toplist.add_argument('--date', help='日期 YYYYMMDD (默认今天)')
    ashare_toplist.add_argument('--recent', type=int, help='最近N天龙虎榜')
    ashare_toplist.add_argument('--symbol', help='筛选特定股票代码')
    
    ashare_lockup = ashare_sub.add_parser('lockup', help='解禁日历')
    ashare_lockup.add_argument('--days', type=int, default=30, help='查询天数 (默认30)')
    ashare_lockup.add_argument('--symbol', help='特定股票解禁信息')
    
    ashare_north = ashare_sub.add_parser('northbound', help='北向资金')
    ashare_north.add_argument('--days', type=int, default=10, help='查询天数 (默认10)')
    ashare_north.add_argument('--date', help='日期 YYYYMMDD')
    ashare_north.add_argument('--top', action='store_true', help='十大持仓股')
    
    parser_ashare.set_defaults(func=cmd_a_share)

    # backtest 命令 - 策略回测 (P2)
    parser_backtest = subparsers.add_parser('backtest', help='策略回测')
    parser_backtest.add_argument('symbol', help='股票代码')
    parser_backtest.add_argument('--strategy', default='sma-cross', choices=['sma-cross', 'rsi-oversold'], help='策略 (默认sma-cross)')
    parser_backtest.add_argument('--days', type=int, default=365, help='回测天数 (默认365)')
    parser_backtest.add_argument('--capital', type=float, default=100000, help='初始资金 (默认10万)')
    parser_backtest.add_argument('--walk-forward', action='store_true', help='Walk-Forward 分析')
    parser_backtest.add_argument('--monte-carlo', action='store_true', help='Monte Carlo 模拟')
    parser_backtest.add_argument('--detail', action='store_true', help='显示交易明细')
    parser_backtest.set_defaults(func=cmd_backtest)

    # doctor 命令
    parser_doctor = subparsers.add_parser('doctor', help='检查本地数据源状态')
    parser_doctor.add_argument('--live', action='store_true', help='尝试请求真实数据接口，可能受网络、代理或限流影响')
    parser_doctor.add_argument('--sample-symbol', default='002050', help='实时接口探测使用的样本股票代码')
    parser_doctor.add_argument('--no-proxy', action='store_true', help='实时探测时临时屏蔽 HTTP_PROXY/HTTPS_PROXY/ALL_PROXY，用于区分代理故障和数据源故障')
    parser_doctor.set_defaults(func=cmd_doctor)

    # discover 命令
    parser_discover = subparsers.add_parser('discover', help='从真实候选池生成机会短名单')
    parser_discover.add_argument('--candidate-csv', required=True, help='候选股CSV，支持代码/名称/行业/价格/估值/财务/技术字段')
    parser_discover.add_argument('--top', type=int, default=10, help='进入短名单的数量')
    parser_discover.add_argument('--output-dir', help='HTML 输出目录')
    parser_discover.add_argument('--generate-reports', action='store_true', help='为短名单前N只股票继续生成完整Kami投研报告')
    parser_discover.add_argument('--report-count', type=int, default=3, help='批量生成完整报告的股票数量')
    parser_discover.add_argument('--price-dir', help='按股票代码匹配真实K线CSV的目录，例如 002050.csv 或 002050_prices_sample.csv')
    parser_discover.set_defaults(func=cmd_discover)

    # monitor 命令
    parser_monitor = subparsers.add_parser('monitor', help='生成自选股监控面板')
    parser_monitor.add_argument('--watchlist-csv', required=True, help='自选股CSV，支持价格/估值/支撑压力/财务/技术触发字段')
    parser_monitor.add_argument('--top', type=int, default=20, help='CLI展示的股票数量')
    parser_monitor.add_argument('--output-dir', help='HTML 输出目录')
    parser_monitor.add_argument('--generate-review-reports', action='store_true', help='为触发高/中级监控条件的股票生成复核版Kami投研报告')
    parser_monitor.add_argument('--report-count', type=int, default=3, help='批量生成复核报告的股票数量')
    parser_monitor.add_argument('--price-dir', help='按股票代码匹配真实K线CSV的目录，例如 002050.csv 或 002050_prices_sample.csv')
    parser_monitor.add_argument('--generate-plan', action='store_true', help='根据监控结果生成投资跟踪计划HTML和CSV')
    parser_monitor.set_defaults(func=cmd_monitor)

    # report 命令
    parser_report = subparsers.add_parser('report', help='生成完整 HTML 研究报告')
    parser_report.add_argument('symbol', help='股票代码')
    parser_report.add_argument('--style', default='kami', choices=['kami', 'apple'], help='报告视觉风格')
    parser_report.add_argument('--output-dir', help='HTML 输出目录')
    parser_report.add_argument('--timeframe', default='日线', help='技术面时间级别')
    parser_report.add_argument('--trend', help='技术面趋势描述')
    parser_report.add_argument('--price-csv', help='真实K线CSV路径，支持日期/开盘/最高/最低/收盘/成交量或date/open/high/low/close/volume')
    parser_report.add_argument('--offline-input-only', action='store_true', help='只使用外部传入字段和本地K线CSV生成报告，不请求行情、财报和风险接口')
    parser_report.add_argument('--live-data-check', action='store_true', help='生成前探测实时数据接口，结果只用于命令行诊断，不写入投资者报告正文')
    parser_report.add_argument('--require-technical-data', action='store_true', help='没有可验证K线数据时不生成报告，避免输出缺少技术面的报告')
    parser_report.add_argument('--strict-data', action='store_true', help='正式报告模式：公司名称、价格、K线、财务和估值核心数据不足时不生成HTML')
    parser_report.add_argument('--enforce-freshness', action='store_true', help='正式报告模式：检查K线截止日期，过期则不生成HTML')
    parser_report.add_argument('--max-price-age-days', type=int, default=10, help='允许K线截止日期距离检查日的最大天数')
    parser_report.add_argument('--business-summary', help='外部传入公司业务摘要')
    parser_report.add_argument('--moat', help='外部传入竞争优势或护城河说明')
    parser_report.add_argument('--methods', default='all', choices=['all', 'dcf', 'relative', 'ddm'], help='估值方法')
    parser_report.add_argument('--discount-rate', type=float, help='折现率/WACC，例如 0.10')
    parser_report.add_argument('--terminal-growth', type=float, help='永续增长率，例如 0.025')
    parser_report.add_argument('--fcf-growth', type=float, help='自由现金流增长率，例如 0.04')
    parser_report.add_argument('--peer-pe', type=float, help='可比公司市盈率中位数')
    parser_report.add_argument('--peer-pb', type=float, help='可比公司市净率中位数')
    parser_report.add_argument('--margin-of-safety', type=float, help='安全边际，例如 0.30')
    parser_report.add_argument('--current-price', type=float, help='外部传入当前价格')
    parser_report.add_argument('--eps', type=float, help='外部传入每股收益')
    parser_report.add_argument('--bps', type=float, help='外部传入每股净资产')
    parser_report.add_argument('--pe', type=float, help='外部传入当前市盈率')
    parser_report.add_argument('--pb', type=float, help='外部传入当前市净率')
    parser_report.add_argument('--free-cash-flow', type=float, help='外部传入自由现金流')
    parser_report.add_argument('--shares-outstanding', type=float, help='外部传入总股本')
    parser_report.add_argument('--total-debt', type=float, help='外部传入有息负债')
    parser_report.add_argument('--cash', type=float, help='外部传入现金及等价物')
    parser_report.add_argument('--sector', help='外部传入板块')
    parser_report.add_argument('--industry', help='外部传入行业')
    parser_report.add_argument('--gross-margin', type=float, help='外部传入毛利率(%)')
    parser_report.add_argument('--net-margin', type=float, help='外部传入净利率(%)')
    parser_report.add_argument('--roe', type=float, help='外部传入ROE(%)')
    parser_report.add_argument('--debt-ratio', type=float, help='外部传入资产负债率(%)')
    parser_report.add_argument('--revenue-growth', type=float, help='外部传入收入增速(%)')
    parser_report.add_argument('--profit-growth', type=float, help='外部传入利润增速(%)')
    parser_report.add_argument('--receivable-growth', type=float, help='外部传入应收账款增速(%)')
    parser_report.add_argument('--inventory-growth', type=float, help='外部传入存货增速(%)')
    parser_report.add_argument('--operating-cash-flow', type=float, help='外部传入经营现金流')
    parser_report.add_argument('--net-income', type=float, help='外部传入净利润')
    parser_report.set_defaults(func=cmd_report)
    
    # value 命令
    parser_value = subparsers.add_parser('value', help='估值计算')
    parser_value.add_argument('symbol', help='股票代码')
    parser_value.set_defaults(func=cmd_value)
    
    # research 命令
    parser_research = subparsers.add_parser('research', help='深度研报')
    parser_research.add_argument('symbol', help='股票代码')
    parser_research.add_argument('--style', choices=['value', 'growth', 'turnaround', 'dividend'], help='投资风格')
    parser_research.add_argument('--depth', choices=['quick', 'standard', 'deep'], help='分析深度')
    parser_research.set_defaults(func=cmd_research)
    
    # board 命令 (打板筛选)
    parser_board = subparsers.add_parser('board', help='打板筛选 (短线)')
    parser_board.add_argument('--type', 
        choices=['limit-up', 'strong', 'continuous', 'market', 'opportunities'],
        default='market',
        help='筛选类型: limit-up(涨停板), strong(强势股), continuous(连板), market(市场情绪), opportunities(打板机会)')
    parser_board.set_defaults(func=cmd_board)
    
    # earnings 命令 (完整财报分析)
    parser_earnings = subparsers.add_parser('earnings', help='完整财报分析 (预测+回顾)')
    parser_earnings.add_argument('symbol', help='股票代码')
    parser_earnings.add_argument('--periods', type=int, default=4, help='预测季度数 (默认4)')
    parser_earnings.set_defaults(func=cmd_earnings)
    
    # preview 命令 (财报预测)
    parser_preview = subparsers.add_parser('preview', help='财报预测 (预测未来季度业绩)')
    parser_preview.add_argument('symbol', help='股票代码')
    parser_preview.add_argument('--periods', type=int, default=4, help='预测季度数 (默认4)')
    parser_preview.set_defaults(func=cmd_preview)
    
    # recap 命令 (财报回顾)
    parser_recap = subparsers.add_parser('recap', help='财报回顾 (分析历史业绩)')
    parser_recap.add_argument('symbol', help='股票代码')
    parser_recap.set_defaults(func=cmd_recap)
    
    # compare 命令 (业绩比较)
    parser_compare = subparsers.add_parser('compare', help='多股票业绩比较')
    parser_compare.add_argument('symbols', nargs='+', help='股票代码列表 (至少2个)')
    parser_compare.set_defaults(func=cmd_compare)
    

    # ── P5: Crypto / Forex / Onchain / Signal ────────────────────

    # crypto 命令 (加密货币)
    parser_crypto = subparsers.add_parser("crypto", help="加密货币: 行情/K线/分析")
    crypto_sub = parser_crypto.add_subparsers(dest="crypto_subcmd", help="子命令")
    crypto_quote = crypto_sub.add_parser("quote", help="行情查询")
    crypto_quote.add_argument("symbol", nargs="?", default="BTC/USDT", help="币种代码 (如 BTC/USDT)")
    crypto_quote.add_argument("--exchange", default="binance", help="交易所")
    crypto_orderbook = crypto_sub.add_parser("orderbook", help="订单簿/深度")
    crypto_orderbook.add_argument("symbol", nargs="?", default="BTC/USDT", help="币种代码")
    crypto_orderbook.add_argument("--exchange", default="binance", help="交易所")
    crypto_kline = crypto_sub.add_parser("kline", help="K线数据")
    crypto_kline.add_argument("symbol", nargs="?", default="BTC/USDT", help="币种代码")
    crypto_kline.add_argument("--timeframe", default="1d", help="时间级别 (1m/5m/1h/1d)")
    crypto_kline.add_argument("--limit", type=int, default=30, help="数据条数")
    crypto_kline.add_argument("--exchange", default="binance", help="交易所")
    crypto_trending = crypto_sub.add_parser("trending", help="热门币种")
    crypto_trending.add_argument("--exchange", default="binance", help="交易所")
    crypto_search = crypto_sub.add_parser("search", help="搜索币种")
    crypto_search.add_argument("--keyword", default="bitcoin", help="搜索关键词")
    crypto_search.add_argument("--exchange", default="binance", help="交易所")
    crypto_multi = crypto_sub.add_parser("multi", help="多交易所对比")
    crypto_multi.add_argument("symbol", nargs="?", default="BTC/USDT", help="币种代码")
    crypto_analyze = crypto_sub.add_parser("analyze", help="综合分析")
    crypto_analyze.add_argument("symbol", nargs="?", default="BTC/USDT", help="币种代码")
    parser_crypto.set_defaults(func=cmd_crypto)

    # forex 命令 (外汇)
    parser_forex = subparsers.add_parser("forex", help="外汇: 汇率/技术分析")
    forex_sub = parser_forex.add_subparsers(dest="forex_subcmd", help="子命令")
    forex_quote = forex_sub.add_parser("quote", help="汇率查询")
    forex_quote.add_argument("--pair", default="USD/CNY", help="货币对 (如 USD/CNY, EUR/USD)")
    forex_analyze = forex_sub.add_parser("analyze", help="技术分析")
    forex_analyze.add_argument("--pair", default="USD/CNY", help="货币对")
    forex_analyze.add_argument("--days", type=int, default=60, help="分析天数")
    parser_forex.set_defaults(func=cmd_forex)

    # onchain 命令 (链上数据)
    parser_onchain = subparsers.add_parser("onchain", help="链上数据: TVL/鲸鱼/协议")
    onchain_sub = parser_onchain.add_subparsers(dest="onchain_subcmd", help="子命令")
    onchain_tvl = onchain_sub.add_parser("tvl", help="DeFi TVL数据")
    onchain_tvl.add_argument("--chain", default="Ethereum", help="链名称")
    onchain_protocol = onchain_sub.add_parser("protocol", help="协议详情")
    onchain_protocol.add_argument("--protocol-name", default="aave", help="协议名称")
    onchain_whale = onchain_sub.add_parser("whale", help="鲸鱼追踪")
    onchain_whale.add_argument("--symbol", default="ETH", help="币种代码")
    onchain_whale.add_argument("--chain", default="Ethereum", help="链名称")
    parser_onchain.set_defaults(func=cmd_onchain)

    # signal 命令 (信号检测)
    parser_signal = subparsers.add_parser("signal", help="信号检测: 多因子信号分级")
    parser_signal.add_argument("symbol", help="标的代码")
    parser_signal.add_argument("--market", default="stock", choices=["stock", "crypto", "forex"], help="市场类型")
    parser_signal.set_defaults(func=cmd_signal)
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main()
