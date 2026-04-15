#!/usr/bin/env python3
"""
Complete Test Script - 完整功能测试
测试 unified-finance-skill 所有功能
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_quote():
    """测试行情查询"""
    print_section("测试 1: 行情查询 (多数据源)")
    
    from multi_source_data import MultiSourceData, compare_sources
    
    # 测试美股
    print("\n[1.1] 美股行情 (AAPL):")
    msd = MultiSourceData('AAPL')
    try:
        data = msd.get_quote()
        print(f"  数据源：{data['source']}")
        print(f"  价格：{data['price']:.2f} {data.get('currency', 'USD')}")
        print(f"  涨跌：{data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        # 验证数据质量
        validation = msd.validate_data(data)
        print(f"  数据质量：{'[PASS]' if validation['valid'] else '[WARN] ' + ', '.join(validation['issues'])}")
    except Exception as e:
        print(f"  失败：{e}")
    
    # 测试 A 股
    print("\n[1.2] A 股行情 (600519):")
    from data_fetcher import get_quote
    result = get_quote('600519')
    print(result[:300] if len(result) > 300 else result)
    
    # 测试港股
    print("\n[1.3] 港股行情 (00700.HK):")
    result = get_quote('00700.HK')
    print(result[:300] if len(result) > 300 else result)

def test_chart():
    """测试图表生成"""
    print_section("测试 2: 图表生成 (全市场)")
    
    from chart_generator import generate_chart
    
    # 测试 A 股
    print("\n[2.1] A 股图表 (600519):")
    path = generate_chart('600519', '3mo', {'rsi': True, 'macd': True, 'bb': True})
    print(f"  结果：{path}")
    
    # 测试港股
    print("\n[2.2] 港股图表 (00700.HK):")
    path = generate_chart('00700.HK', '3mo', {'rsi': True, 'macd': True})
    print(f"  结果：{path}")
    
    # 测试美股
    print("\n[2.3] 美股图表 (AAPL):")
    path = generate_chart('AAPL', '3mo', {'rsi': True, 'macd': True, 'bb': True})
    print(f"  结果：{path}")

def test_cache():
    """测试缓存功能"""
    print_section("测试 3: 缓存管理")
    
    from cache_manager import CacheManager
    
    cache = CacheManager(ttl=5)  # 5 秒用于测试
    
    print("\n[3.1] 设置缓存:")
    cache.set('test', {'price': 100}, 'AAPL')
    print("  已缓存 AAPL 价格")
    
    print("\n[3.2] 获取缓存:")
    data = cache.get('test', 'AAPL')
    print(f"  结果：{data}")
    
    print("\n[3.3] 缓存统计:")
    stats = cache.get_stats()
    print(f"  命中率：{stats['hit_rate']}")
    print(f"  内存缓存数：{stats['memory_cache_size']}")
    
    print("\n[3.4] 等待缓存过期 (5 秒)...")
    time.sleep(6)
    
    print("\n[3.5] 再次获取 (应过期):")
    data = cache.get('test', 'AAPL')
    print(f"  结果：{data} (None=已过期)")

def test_data_quality():
    """测试数据质量监控"""
    print_section("测试 4: 数据质量监控")
    
    from data_quality import DataQualityMonitor
    
    monitor = DataQualityMonitor()
    
    print("\n[4.1] 价格验证:")
    monitor.validate_price('AAPL', 150.0)  # 正常
    monitor.validate_price('AAPL', 200.0, 150.0)  # 波动大
    
    print("\n[4.2] 成交量验证:")
    monitor.validate_volume('AAPL', 1000000, 50000000)  # 过低
    monitor.validate_volume('AAPL', 600000000, 50000000)  # 过高
    
    print("\n[4.3] 跨数据源验证:")
    source1 = {'price': 150.0, 'change_percent': 2.5}
    source2 = {'price': 152.0, 'change_percent': 3.0}
    result = monitor.cross_validate('AAPL', source1, source2)
    print(f"  验证结果：{'通过' if result['valid'] else '未通过'}")
    if result['issues']:
        for issue in result['issues']:
            print(f"    - {issue['message']}")
    
    print("\n[4.4] 质量报告:")
    report = monitor.get_report()
    print(f"  质量分数：{report['quality_score']}")
    print(f"  评级：{report['rating']}")
    print(f"  告警总数：{report['alerts']['total']}")

def test_multi_source_compare():
    """测试多数据源对比"""
    print_section("测试 5: 多数据源对比")
    
    from multi_source_data import compare_sources
    
    print("\n[5.1] 对比 yfinance vs Alpha Vantage (AAPL):")
    result = compare_sources('AAPL')
    
    print(f"\n  数据源状态:")
    for source, data in result['sources'].items():
        if 'error' in data:
            print(f"    {source}: [FAIL] {data['error']}")
        else:
            print(f"    {source}: [OK] 价格 ${data['price']:.2f}")
    
    if result['comparison']:
        print(f"\n  差异分析:")
        print(f"    价格差异：${result['comparison']['price_difference']:.2f} ({result['comparison']['price_difference_pct']}%)")
        print(f"    数据质量：{result['comparison']['data_quality']}")

def test_industry_heatmap():
    """测试行业热力图"""
    print_section("测试 6: 行业热力图")
    
    from data_fetcher import get_heatmap
    
    print("\n[6.1] A 股市场热力图:")
    result = get_heatmap('ab')
    lines = result.split('\n')[:15]  # 显示前 15 行
    for line in lines:
        print(f"  {line}")

def test_fundflow():
    """测试资金流向"""
    print_section("测试 7: 资金流向")
    
    from data_fetcher import get_fundflow
    
    print("\n[7.1] 贵州茅台 (600519) 资金流向:")
    result = get_fundflow('600519')
    lines = result.split('\n')[:20]  # 显示前 20 行
    for line in lines:
        print(f"  {line}")

def test_alerts():
    """测试警报系统"""
    print_section("测试 8: 警报管理")
    
    from alert_manager import AlertManager
    
    manager = AlertManager()
    
    print("\n[8.1] 添加测试警报:")
    manager.add('NVDA', target=150, stop=120)
    print("  已添加 NVDA (目标:150, 止损:120)")
    
    print("\n[8.2] 列出所有警报:")
    alerts = manager.list()
    for a in alerts:
        print(f"    {a['symbol']}: 目标={a['target']}, 止损={a['stop']}")
    
    print("\n[8.3] 检查警报:")
    triggered = manager.check()
    if triggered:
        for t in triggered:
            print(f"    [ALERT] {t['message']}")
    else:
        print("    无触发警报")

def main():
    """主测试函数"""
    print("=" * 70)
    print("  Unified Finance Skill - 完整功能测试")
    print("  测试时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)
    
    tests = [
        ('行情查询', test_quote),
        ('图表生成', test_chart),
        ('缓存管理', test_cache),
        ('数据质量', test_data_quality),
        ('多源对比', test_multi_source_compare),
        ('行业热力图', test_industry_heatmap),
        ('资金流向', test_fundflow),
        ('警报管理', test_alerts),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, '[PASS]'))
        except Exception as e:
            print(f"\n[FAIL] {name} 测试失败：{e}")
            results.append((name, f'[FAIL] {e}'))
    
    # 汇总报告
    print_section("测试汇总报告")
    
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
        print("  [SUCCESS] 所有测试通过！")
    else:
        print(f"  [WARNING] {total - passed} 个测试失败，请检查")
    print("=" * 70)

if __name__ == '__main__':
    main()
