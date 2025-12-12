import json
from collections import Counter

# Load lottery data
with open('lottery_data_2025_complete.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get('totalRecords', [])
records.sort(key=lambda x: int(x['period']), reverse=True)

# Load prediction history
with open('macau_special_prediction_history.json', 'r', encoding='utf-8') as f:
    predictions = json.load(f)

print("="*60)
print("特码预测准确率分析")
print("="*60)

# Analyze last 50 periods special number zodiac distribution
zodiac_count = {}
for i, record in enumerate(records[:50]):
    if 'numberList' in record and len(record['numberList']) >= 7:
        special = record['numberList'][-1]
        zodiac = special['shengXiao']
        number = int(special['number'])
        zodiac_count[zodiac] = zodiac_count.get(zodiac, 0) + 1

print('\n最近50期特码生肖分布:')
for z, c in sorted(zodiac_count.items(), key=lambda x: x[1], reverse=True):
    print(f'  {z}: {c}期 ({c/50*100:.1f}%)')

# Check prediction accuracy
print("\n" + "="*60)
print("预测准确率检查 (最近20期)")
print("="*60)

hits_4 = 0
hits_6 = 0
hits_7 = 0
total_checked = 0

for pred in predictions[:20]:
    period = pred.get('period')
    
    # Find actual result
    actual_record = None
    for record in records:
        if int(record['period']) == period:
            actual_record = record
            break
    
    if not actual_record:
        continue
    
    if 'numberList' not in actual_record or len(actual_record['numberList']) < 7:
        continue
        
    actual_special = actual_record['numberList'][-1]
    actual_zodiac = actual_special['shengXiao']
    actual_number = int(actual_special['number'])
    
    predicted_zodiacs_4 = [z[0] for z in pred.get('top_zodiacs', [])][:4]
    predicted_zodiacs_6 = [z[0] for z in pred.get('top_zodiacs', [])][:6] if len(pred.get('top_zodiacs', [])) >= 6 else predicted_zodiacs_4
    predicted_zodiacs_7 = [z[0] for z in pred.get('top_zodiacs', [])][:7] if len(pred.get('top_zodiacs', [])) >= 7 else predicted_zodiacs_6
    
    hit_4 = actual_zodiac in predicted_zodiacs_4
    hit_6 = actual_zodiac in predicted_zodiacs_6
    hit_7 = actual_zodiac in predicted_zodiacs_7
    
    if hit_4:
        hits_4 += 1
    if hit_6:
        hits_6 += 1
    if hit_7:
        hits_7 += 1
    
    total_checked += 1
    
    status_4 = "HIT" if hit_4 else "MISS"
    status_6 = "HIT" if hit_6 else "MISS"
    status_7 = "HIT" if hit_7 else "MISS"
    
    print(f"\n期号 {period}:")
    print(f"  实际特码: {actual_number} ({actual_zodiac})")
    print(f"  预测4肖: {predicted_zodiacs_4} - {status_4}")
    print(f"  预测6肖: {predicted_zodiacs_6} - {status_6}")
    print(f"  预测7肖: {predicted_zodiacs_7} - {status_7}")

print("\n" + "="*60)
print("统计结果")
print("="*60)
print(f"总检查期数: {total_checked}")
print(f"预测4肖命中: {hits_4}/{total_checked} ({hits_4/total_checked*100:.1f}%)")
print(f"预测6肖命中: {hits_6}/{total_checked} ({hits_6/total_checked*100:.1f}%)")
print(f"预测7肖命中: {hits_7}/{total_checked} ({hits_7/total_checked*100:.1f}%)")
print(f"\n4肖失误率: {(total_checked-hits_4)/total_checked*100:.1f}%")
print(f"6肖失误率: {(total_checked-hits_6)/total_checked*100:.1f}%")
print(f"7肖失误率: {(total_checked-hits_7)/total_checked*100:.1f}%")
