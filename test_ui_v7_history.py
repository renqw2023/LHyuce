"""
测试V7历史页面的逻辑
"""
import json
import glob
import os
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print(" 测试V7预测历史页面逻辑")
print("="*70)

# 1. 加载所有V7预测文件
v7_files = sorted(glob.glob('predictions/v7_prediction_*.json'), 
                 key=os.path.getctime, reverse=True)

print(f"\n找到 {len(v7_files)} 个V7预测文件:")
for f in v7_files:
    print(f"  - {f}")

# 2. 加载开奖数据
data_file = 'lottery_data_2025_complete.json'
with open(data_file, 'r', encoding='utf-8') as f:
    lottery_data = json.load(f)

actual_results = {int(r['period']): r for r in lottery_data.get('totalRecords', [])}
print(f"\n加载了 {len(actual_results)} 期开奖数据")

# 3. 测试每个预测文件
print("\n" + "="*70)
print(" 逐个测试预测文件")
print("="*70)

total_checked = 0
total_hits = 0

for v7_file in v7_files:
    with open(v7_file, 'r', encoding='utf-8') as f:
        v7_pred = json.load(f)
    
    period = v7_pred.get('period')
    predicted_zodiacs = v7_pred.get('predicted_zodiacs', [])
    predicted_numbers = v7_pred.get('recommended_numbers', [])
    
    print(f"\n期号: {period}")
    print(f"  预测8生肖: {', '.join(predicted_zodiacs)}")
    
    # 查找实际结果
    actual = actual_results.get(period)
    
    if actual and 'numberList' in actual and len(actual['numberList']) >= 7:
        actual_special = actual['numberList'][-1]
        actual_zodiac = actual_special['shengXiao']
        actual_number = int(actual_special['number'])
        
        zodiac_hit = actual_zodiac in predicted_zodiacs
        number_hit = actual_number in predicted_numbers
        
        total_checked += 1
        if zodiac_hit:
            total_hits += 1
            print(f"  实际特码: {actual_number} ({actual_zodiac})")
            print(f"  结果: ✅ 命中")
        else:
            print(f"  实际特码: {actual_number} ({actual_zodiac})")
            print(f"  结果: ❌ 未中")
    else:
        print(f"  状态: ⏳ 待开奖或数据缺失")

# 4. 统计
print("\n" + "="*70)
print(" 统计摘要")
print("="*70)
print(f"总预测期数: {len(v7_files)}")
print(f"已开奖期数: {total_checked}")
print(f"命中期数: {total_hits}")
if total_checked > 0:
    accuracy = (total_hits / total_checked) * 100
    print(f"准确率: {accuracy:.1f}%")
else:
    print(f"准确率: 无法计算（无已开奖期数）")

print("="*70)
