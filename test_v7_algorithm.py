"""
测试V7算法 - 8生肖智能覆盖
验证改进后的准确率
"""
import json
import backtester_v7

print("="*70)
print(" V7 算法测试 - 8生肖智能覆盖系统")
print("="*70)

# 默认V7参数（初始版本）
default_v7_weights = {
    'special_hot': 2.5,
    'special_gap': 2.5,
    'special_zodiac': 5.0,
    'special_color_weight': 3.0,
    'special_tail_weight': 3.0,
    'special_cold_protect': 4.0,
    'special_lookback': 30,
    'special_resonance': 2.0,
    'special_cycle_weight': 2.5,
    'special_element_weight': 2.5,
    'special_balance_weight': 2.0,
    'special_diversity_bonus': 1.5
}

print("\n测试1: 使用默认V7参数（未优化）")
print("-"*70)
backtester_v7.display_backtest_report_v7('macau', default_v7_weights, backtest_range=50)

# 如果存在优化后的策略文件，也测试它
try:
    with open('best_special_strategy_macau_v7.json', 'r', encoding='utf-8') as f:
        optimized_v7_weights = json.load(f)
    
    print("\n" + "="*70)
    print("测试2: 使用优化后的V7参数")
    print("-"*70)
    backtester_v7.display_backtest_report_v7('macau', optimized_v7_weights, backtest_range=50)
except FileNotFoundError:
    print("\n提示: 优化策略文件尚未生成")
    print("运行 'python optimizer_special_v7.py' 来生成优化策略")

print("\n" + "="*70)
print("测试完成")
print("="*70)
