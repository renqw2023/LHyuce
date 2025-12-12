"""
V7性能可视化
生成性能对比和趋势分析
"""
import json
from collections import Counter

def analyze_v7_performance():
    """分析V7性能并生成报告"""
    
    # 设置stdout编码为UTF-8（解决Windows乱码）
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("="*70)
    print(" V7 性能分析报告")
    print("="*70)
    
    # 加载数据
    try:
        with open('lottery_data_2025_complete.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        records = data['totalRecords']
        records.sort(key=lambda x: int(x['period']), reverse=True)
        
        with open('best_special_strategy_macau_v7.json', 'r', encoding='utf-8') as f:
            v7_weights = json.load(f)
    except Exception as e:
        print(f"错误: 无法加载数据 - {e}")
        return
    
    # 导入分析器
    import advanced_lottery_analysis_v7 as analyzer
    
    # 加载历史数据
    special_history = analyzer.load_special_number_data()
    
    print(f"\n数据概览:")
    print(f"  总期数: {len(special_history)}")
    print(f"  分析期数: 最近50期")
    
    # 回测最近50期
    lookback = 30
    test_results = []
    
    for i in range(50):
        if i + lookback >= len(special_history):
            break
            
        target = special_history[i]
        history = special_history[i+1:]
        
        prediction = analyzer.analyze_special_trend(history, v7_weights)
        if not prediction:
            continue
        
        predicted_zodiacs = [z[0] for z in prediction['top_zodiacs']]
        actual_zodiac = target['shengXiao']
        
        hit = actual_zodiac in predicted_zodiacs
        test_results.append({
            'period': target['period'],
            'actual': actual_zodiac,
            'predicted': predicted_zodiacs,
            'hit': hit
        })
    
    # 统计
    total = len(test_results)
    hits = sum(1 for r in test_results if r['hit'])
    accuracy = (hits / total * 100) if total > 0 else 0
    
    print(f"\n" + "="*70)
    print(f" 整体统计")
    print(f"="*70)
    print(f"  测试期数: {total}")
    print(f"  命中期数: {hits}")
    print(f"  失误期数: {total - hits}")
    print(f"  准确率: {accuracy:.2f}%")
    print(f"  失误率: {100 - accuracy:.2f}%")
    
    # 分段统计
    print(f"\n" + "="*70)
    print(f" 分段表现")
    print(f"="*70)
    
    segments = [
        ("最近10期", test_results[:10]),
        ("10-20期", test_results[10:20]),
        ("20-30期", test_results[20:30]),
        ("30-40期", test_results[30:40]),
        ("40-50期", test_results[40:50])
    ]
    
    for name, segment in segments:
        if not segment:
            continue
        seg_hits = sum(1 for r in segment if r['hit'])
        seg_total = len(segment)
        seg_acc = (seg_hits / seg_total * 100) if seg_total > 0 else 0
        
        bar_length = int(seg_acc / 2)
        bar = "#" * bar_length + "-" * (50 - bar_length)
        
        print(f"\n  {name:12} {seg_hits:2}/{seg_total:2}  {seg_acc:5.1f}%  [{bar}]")
    
    # 生肖分布分析
    print(f"\n" + "="*70)
    print(f" 生肖命中分析")
    print(f"="*70)
    
    zodiac_stats = {}
    for z in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']:
        actual_count = sum(1 for r in test_results if r['actual'] == z)
        hit_count = sum(1 for r in test_results if r['actual'] == z and r['hit'])
        zodiac_stats[z] = {
            'actual': actual_count,
            'hit': hit_count,
            'rate': (hit_count / actual_count * 100) if actual_count > 0 else 0
        }
    
    print(f"\n  {'生肖':<6} {'出现次数':<8} {'命中次数':<8} {'命中率'}")
    print(f"  {'-'*50}")
    
    for z, stats in sorted(zodiac_stats.items(), key=lambda x: x[1]['actual'], reverse=True):
        if stats['actual'] == 0:
            continue
        bar_len = int(stats['rate'] / 5)
        bar = "#" * bar_len
        print(f"  {z:<6} {stats['actual']:<8} {stats['hit']:<8} {stats['rate']:5.1f}% [{bar}]")
    
    # 连续命中/失误分析
    print(f"\n" + "="*70)
    print(f" 连续性分析")
    print(f"="*70)
    
    max_hit_streak = 0
    max_miss_streak = 0
    current_hit = 0
    current_miss = 0
    
    for r in test_results:
        if r['hit']:
            current_hit += 1
            current_miss = 0
            max_hit_streak = max(max_hit_streak, current_hit)
        else:
            current_miss += 1
            current_hit = 0
            max_miss_streak = max(max_miss_streak, current_miss)
    
    print(f"\n  最长连续命中: {max_hit_streak} 期")
    print(f"  最长连续失误: {max_miss_streak} 期")
    
    # V6 vs V7 对比
    print(f"\n" + "="*70)
    print(f" V6 vs V7 性能对比")
    print(f"="*70)
    
    comparison = [
        ("生肖数量", "4个", "8个", "+100%"),
        ("准确率", "41.2%", f"{accuracy:.1f}%", f"+{(accuracy/41.2-1)*100:.0f}%"),
        ("失误率", "58.8%", f"{100-accuracy:.1f}%", f"-{(1-((100-accuracy)/58.8))*100:.0f}%"),
        ("理论覆盖", "33.3%", "66.7%", "+100%")
    ]
    
    print(f"\n  {'指标':<12} {'V6':<12} {'V7':<12} {'提升'}")
    print(f"  {'-'*50}")
    for metric, v6, v7, change in comparison:
        print(f"  {metric:<12} {v6:<12} {v7:<12} {change}")
    
    # 最新预测
    print(f"\n" + "="*70)
    print(f" 最新5期详情")
    print(f"="*70)
    
    for i, r in enumerate(test_results[:5], 1):
        status = "命中" if r['hit'] else "失误"
        status_symbol = "[HIT]" if r['hit'] else "[MISS]"
        
        print(f"\n  第{i}期 - 期号{r['period']}")
        print(f"    实际生肖: {r['actual']}")
        print(f"    预测8肖: {', '.join(r['predicted'])}")
        print(f"    结果: {status_symbol} {status}")
    
    print(f"\n" + "="*70)
    print(f" 分析完成")
    print(f"="*70)
    
    # 保存报告
    report = {
        "total_tests": total,
        "hits": hits,
        "accuracy": accuracy,
        "miss_rate": 100 - accuracy,
        "max_hit_streak": max_hit_streak,
        "max_miss_streak": max_miss_streak,
        "zodiac_stats": zodiac_stats,
        "recent_5": test_results[:5]
    }
    
    try:
        with open('v7_performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存至: v7_performance_report.json")
    except Exception as e:
        print(f"\n警告: 保存报告失败 - {e}")

if __name__ == "__main__":
    analyze_v7_performance()
