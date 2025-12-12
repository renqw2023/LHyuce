"""
手动测试342期验证功能
"""
import json
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print(" 342期预测验证测试")
print("="*70)

# 1. 读取V7预测
with open('predictions/v7_prediction_342.json', 'r', encoding='utf-8') as f:
    v7_pred = json.load(f)

print("\nV7预测内容:")
print(f"  期号: {v7_pred['period']}")
print(f"  推荐8生肖: {', '.join(v7_pred['predicted_zodiacs'])}")
print(f"  推荐号码: {v7_pred['recommended_numbers'][:12]}")

# 2. 读取开奖数据
with open('lottery_data_2025_complete.json', 'r', encoding='utf-8') as f:
    lottery_data = json.load(f)

# 3. 查找342期
records_342 = [r for r in lottery_data['totalRecords'] if int(r['period']) == 342]

print("\n" + "="*70)
if not records_342:
    print("❌ 问题：lottery_data_2025_complete.json中没有342期数据")
    print("\n解决方案:")
    print("1. 请运行: python fetch_lottery_data.py")
    print("2. 或者手动告诉我342期的开奖号码，我帮您添加")
else:
    record_342 = records_342[0]
    print("✓ 找到342期开奖数据")
    
    if 'numberList' in record_342 and len(record_342['numberList']) >= 7:
        special = record_342['numberList'][-1]
        actual_number = int(special['number'])
        actual_zodiac = special['shengXiao']
        
        print(f"\n实际开奖:")
        print(f"  特码号码: {actual_number}")
        print(f"  特码生肖: {actual_zodiac}")
        
        # 验证
        zodiac_hit = actual_zodiac in v7_pred['predicted_zodiacs']
        number_hit = actual_number in v7_pred['recommended_numbers']
        
        print(f"\n验证结果:")
        if zodiac_hit:
            print(f"  ✓ 生肖命中！ {actual_zodiac} 在推荐的8生肖中")
        else:
            print(f"  ✗ 生肖未中！ {actual_zodiac} 不在推荐的8生肖中")
        
        if number_hit:
            print(f"  ✓ 号码命中！ {actual_number} 在推荐的12个号码中")
        else:
            print(f"  ✗ 号码未中！ {actual_number} 不在推荐的12个号码中")
        
        print(f"\n最终结果:")
        if zodiac_hit:
            print(f"  🎉 预测成功！准确命中！")
        else:
            print(f"  ❌ 预测失败")
    else:
        print("❌ 342期数据格式不完整")

print("="*70)
