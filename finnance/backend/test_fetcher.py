#!/usr/bin/env python3
"""
数据查询模块测试脚本
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import (
    get_fetcher_manager,
    fetch_stock_data,
    YahooFinanceFetcher,
    MockDataFetcher
)

def test_available_sources():
    """测试获取可用数据源列表"""
    print("=" * 60)
    print("测试 1: 获取可用数据源列表")
    print("=" * 60)
    manager = get_fetcher_manager()
    sources = manager.get_available_sources()
    print(f"可用数据源: {sources}")
    print()

def test_single_stock():
    """测试获取单只股票数据"""
    print("=" * 60)
    print("测试 2: 获取单只股票数据 (AAPL)")
    print("=" * 60)
    data, price, source = fetch_stock_data("AAPL")
    if data:
        print(f"数据源: {source}")
        print(f"当前价格: ${price:.2f}")
        print(f"20周均线: ${data['ma20']:.2f}")
    else:
        print("获取数据失败")
    print()

def test_multiple_stocks():
    """测试获取多只股票数据"""
    print("=" * 60)
    print("测试 3: 获取多只股票数据")
    print("=" * 60)
    symbols = ["MSFT", "GOOGL", "AMZN", "NVDA", "VOO", "QQQ", "GLD"]
    for symbol in symbols:
        data, price, source = fetch_stock_data(symbol)
        status = "✓" if data else "✗"
        print(f"{status} {symbol:6} - 价格: ${price:.2f} - 来源: {source}")
    print()

def test_custom_symbol():
    """测试自定义/未知股票代码"""
    print("=" * 60)
    print("测试 4: 自定义股票代码 (未知代码)")
    print("=" * 60)
    data, price, source = fetch_stock_data("MYSTOCK123")
    print(f"未知代码处理:")
    print(f"  数据来源: {source}")
    print(f"  生成价格: ${price:.2f}")
    print()

def test_individual_fetchers():
    """测试单个数据获取器"""
    print("=" * 60)
    print("测试 5: 单个数据获取器测试")
    print("=" * 60)
    
    yahoo = YahooFinanceFetcher()
    print(f"{yahoo.get_name()}:")
    data, price, success = yahoo.fetch_data("AAPL")
    if success:
        print(f"  ✓ 成功获取 - 价格: ${price:.2f}")
    else:
        print(f"  ✗ 获取失败")
    
    mock = MockDataFetcher()
    print(f"\n{mock.get_name()}:")
    data, price, success = mock.fetch_data("AAPL")
    if success:
        print(f"  ✓ 成功获取 - 价格: ${price:.2f}")
    else:
        print(f"  ✗ 获取失败")
    print()

def test_add_fetcher():
    """测试添加自定义数据获取器"""
    print("=" * 60)
    print("测试 6: 动态添加数据源")
    print("=" * 60)
    
    manager = get_fetcher_manager()
    original_sources = manager.get_available_sources()
    print(f"原始数据源: {original_sources}")
    
    # 创建一个简单的测试数据源
    class TestFetcher(YahooFinanceFetcher):
        def get_name(self) -> str:
            return "Test Source"
    
    manager.add_fetcher(TestFetcher())
    new_sources = manager.get_available_sources()
    print(f"添加后数据源: {new_sources}")
    print()

def main():
    print("\n" + "=" * 60)
    print("      数据查询模块测试套件")
    print("=" * 60 + "\n")
    
    try:
        test_available_sources()
        test_single_stock()
        test_multiple_stocks()
        test_custom_symbol()
        test_individual_fetchers()
        test_add_fetcher()
        
        print("=" * 60)
        print("      所有测试完成 ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
