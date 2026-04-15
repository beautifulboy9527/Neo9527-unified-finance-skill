#!/usr/bin/env python3
"""
Final Integration Test - 完整功能测试
测试所有整合后的功能
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_quote():
    print_header("测试 1: 行情查询")
    from data_fetcher import get_quote
    
    print("\n[1.1] A 股 (600519):")
    result = get_quote('600519')
    print(result[:200] if len(result) > 200 else result)
    
    print("\n[1.2] 港股 (00700.HK):")
    result = get_quote('00700.HK')
    print(result[:200] if len(result) > 200 else result)
    
    print("\n[1.3] 美股 (AAPL):")
    result = get_quote('AAPL')
    print(result[:200] if len(result) > 200 else result)

def test_chart():
    print_header("测试 2: 图表生成")
    from chart_generator import generate_chart
    
    print("\n[2.1] A 股图表 (600519):")
    path = generate_chart('600519', '3mo', {'rsi': True, 'macd': True})
    print(f"结果：{path}")
    
    print("\n[2.2] 美股图表 (AAPL):")
    path = generate_chart('AAPL', '3mo', {'rsi': True, 'macd': True})
    print(f"结果：{path}")

def test_screener():
    print_header("测试 3: 多条件选股")
    from stock_screener import StockScreener, format_table
    
    screener = StockScreener()
    
    print("\n[3.1] 美股基本面筛选 (PE<25, ROE>15%):")
    df = screener.screen_us_stocks(pe_max=25, roe_min=15, limit=10)
    print(format_table(df))
    
    print("\n[3.2] 技术面筛选 (RSI 超卖):")
    df = screener.screen_by_technical(market='us', rsi_oversold=True, limit=5)
    print(format_table(df))

def test_portfolio():
    print_header("测试 4: 投资组合管理")
    from portfolio_manager import PortfolioManager, format_portfolio_summary
    
    pm = PortfolioManager()
    
    print("\n[4.1] 添加测试持仓:")
    pm.add_position('AAPL', 10, 150)
    pm.add_position('MSFT', 5, 300)
    pm.add_position('600519', 100, 1400)
    
    print("\n[4.2] 持仓列表:")
    positions = pm.get_positions()
    for pos in positions:
        print(f"  {pos['id']}. {pos['symbol']} x {pos['quantity']} @ {pos['cost_price']}")
    
    print("\n[4.3] 组合摘要:")
    summary = pm.get_summary()
    print(format_portfolio_summary(summary))
    
    print("\n[4.4] 配置分析:")
    allocation = pm.analyze_allocation()
    for alloc in allocation['allocation']:
        print(f"  {alloc['symbol']:10} {alloc['weight']:>6.2f}%")

def test_fundamentals():
    print_header("测试 5: 基本面数据")
    import yfinance as yf
    
    ticker = yf.Ticker('AAPL')
    info = ticker.info
    
    print(f"\n{info.get('longName', 'AAPL')} 基本面数据:")
    print("-" * 50)
    print(f"市值：{info.get('marketCap', 'N/A')}")
    print(f"市盈率：{info.get('forwardPE', 'N/A')}")
    print(f"市净率：{info.get('priceToBook', 'N/A')}")
    print(f"ROE: {info.get('returnOnEquity', 'N/A')}")

def test_heatmap():
    print_header("测试 6: 行业热力图")
    from data_fetcher import get_heatmap
    
    print("\n[6.1] A 股市场热力图:")
    result = get_heatmap('ab')
    lines = result.split('\n')[:10]
    for line in lines:
        print(f"  {line}")

def test_fundflow():
    print_header("测试 7: 资金流向")
    from data_fetcher import get_fundflow
    
    print("\n[7.1] 贵州茅台 (600519):")
    result = get_fundflow('600519')
    lines = result.split('\n')[:15]
    for line in lines:
        print(f"  {line}")

def test_alerts():
    print_header("测试 8: 警报系统")
    from alert_manager import AlertManager
    
    manager = AlertManager()
    
    print("\n[8.1] 添加测试警报:")
    manager.add('NVDA', target=150, stop=120)
    
    print("\n[8.2] 检查警报:")
    triggered = manager.check()
    if triggered:
        for t in triggered:
            print(f"  [ALERT] {t['message']}")
    else:
        print("  无触发警报")

def test_pipeline():
    print_header("测试 9: 链式流程")
    from pipeline import create_quick_check_pipeline
    
    pipeline = create_quick_check_pipeline()
    result = pipeline.run({'symbol': 'AAPL'})
    
    print("\n流程执行报告:")
    print(pipeline.get_report(result))

def main():
    print("=" * 70)
    print("  Unified Finance Skill - 最终整合测试")
    print("  测试时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)
    
    tests = [
        ("行情查询", test_quote),
        ("图表生成", test_chart),
        ("多条件选股", test_screener),
        ("投资组合管理", test_portfolio),
        ("基本面数据", test_fundamentals),
        ("行业热力图", test_heatmap),
        ("资金流向", test_fundflow),
        ("警报系统", test_alerts),
        ("链式流程", test_pipeline),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, '[PASS]'))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试失败：{e}")
            import traceback
            traceback.print_exc()
            results.append((name, f'[FAIL] {str(e)[:50]}'))
    
    # 汇总报告
    print_header("最终测试汇总")
    
    passed = sum(1 for _, status in results if '[PASS]' in status)
    total = len(results)
    
    print(f"\n总测试数：{total}")
    print(f"通过：{passed}")
    print(f"失败：{total - passed}")
    print(f"通过率：{passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for name, status in results:
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print("  [SUCCESS] 所有测试通过！金融 Skills 整合完成！")
    else:
        print(f"  [WARNING] {total - passed} 个测试失败")
    print("=" * 70)

if __name__ == '__main__':
    main()
