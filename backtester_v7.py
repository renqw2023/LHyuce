import json
from collections import Counter
import advanced_lottery_analysis_v7 as macau_analyzer_v7
# 如果有HK版本，可以添加：import advanced_hk_analysis_v7 as hk_analyzer_v7

def run_special_backtest_v7(lottery_type, weights, backtest_range=100):
    """
    V7 特码回测：8生肖评估系统
    
    评分规则：
    - 生肖命中（8选1）: +100 分（基础得分）
    - 特码数字命中（推荐号码中）: +500 分（核心目标）
    - 未命中惩罚: -50 分（相比V6减少惩罚，因为8生肖覆盖更广）
    
    目标准确率：70%+（理论值67%）
    """
    if lottery_type == 'macau':
        analyzer = macau_analyzer_v7
    elif lottery_type == 'hk':
        # 如果有HK V7版本，使用它；否则回退到macau
        analyzer = macau_analyzer_v7
    else:
        return 0 

    full_special_history = analyzer.load_special_number_data()
    lookback = int(weights.get('special_lookback', 20))
    min_lookback = lookback + 5 
    
    if not full_special_history or len(full_special_history) <= min_lookback:
        return 0 

    actual_backtest_range = min(backtest_range, len(full_special_history) - min_lookback)
    
    total_score = 0
    zodiac_hits = 0
    number_hits = 0
    total_tests = 0
    
    for i in range(actual_backtest_range):
        target_special_draw = full_special_history[i]
        history_for_prediction = full_special_history[i+1:]
        
        if not history_for_prediction: 
            continue

        prediction = analyzer.analyze_special_trend(history_for_prediction, weights)
        if not prediction: 
            continue

        # 提取预测的8个生肖
        predicted_zodiacs = [p[0] for p in prediction.get('top_zodiacs', [])]
        recommended_numbers = prediction.get('recommended_numbers', [])
        
        actual_zodiac = target_special_draw['shengXiao']
        actual_number = target_special_draw['number']

        total_tests += 1

        # V7 评分规则（针对8生肖优化）
        # 1. 生肖命中：+100 分
        if actual_zodiac in predicted_zodiacs:
            total_score += 100
            zodiac_hits += 1
        
        # 2. 特码数字命中：+500 分（核心目标）
        if actual_number in recommended_numbers:
            total_score += 500
            number_hits += 1
        else:
            # 3. 未命中惩罚：-50 分（相比V6减少惩罚）
            total_score -= 50

    # 输出统计信息（调试用）
    if total_tests > 0:
        zodiac_accuracy = (zodiac_hits / total_tests) * 100
        number_accuracy = (number_hits / total_tests) * 100
        # 不打印详细信息，避免优化过程输出过多

    return total_score 

def display_backtest_report_v7(lottery_type, weights, backtest_range=50):
    """
    显示详细的V7回测报告
    """
    print(f"\n{'='*60}")
    print(f"V7 特码回测报告 - {lottery_type.upper()}")
    print(f"{'='*60}")
    
    if lottery_type == 'macau':
        analyzer = macau_analyzer_v7
    elif lottery_type == 'hk':
        analyzer = macau_analyzer_v7
    else:
        print("不支持的彩票类型")
        return

    full_special_history = analyzer.load_special_number_data()
    lookback = int(weights.get('special_lookback', 20))
    min_lookback = lookback + 5
    
    if not full_special_history or len(full_special_history) <= min_lookback:
        print("历史数据不足")
        return

    actual_backtest_range = min(backtest_range, len(full_special_history) - min_lookback)
    
    zodiac_hits = 0
    number_hits = 0
    total_tests = 0
    
    detailed_results = []
    
    for i in range(actual_backtest_range):
        target_special_draw = full_special_history[i]
        history_for_prediction = full_special_history[i+1:]
        
        if not history_for_prediction:
            continue

        prediction = analyzer.analyze_special_trend(history_for_prediction, weights)
        if not prediction:
            continue

        predicted_zodiacs = [p[0] for p in prediction.get('top_zodiacs', [])]
        recommended_numbers = prediction.get('recommended_numbers', [])
        
        actual_zodiac = target_special_draw['shengXiao']
        actual_number = target_special_draw['number']
        period = target_special_draw['period']

        total_tests += 1
        
        zodiac_hit = actual_zodiac in predicted_zodiacs
        number_hit = actual_number in recommended_numbers
        
        if zodiac_hit:
            zodiac_hits += 1
        if number_hit:
            number_hits += 1
            
        detailed_results.append({
            'period': period,
            'actual_number': actual_number,
            'actual_zodiac': actual_zodiac,
            'predicted_zodiacs': predicted_zodiacs,
            'zodiac_hit': zodiac_hit,
            'number_hit': number_hit
        })
    
    # 输出统计
    print(f"\n回测期数: {total_tests}")
    print(f"{'='*60}")
    
    if total_tests > 0:
        zodiac_accuracy = (zodiac_hits / total_tests) * 100
        number_accuracy = (number_hits / total_tests) * 100
        
        print(f"\n【8生肖命中】")
        print(f"  命中次数: {zodiac_hits}/{total_tests}")
        print(f"  准确率: {zodiac_accuracy:.2f}%")
        print(f"  失误率: {100 - zodiac_accuracy:.2f}%")
        
        print(f"\n【推荐号码命中】")
        print(f"  命中次数: {number_hits}/{total_tests}")
        print(f"  准确率: {number_accuracy:.2f}%")
        
        # 目标评估
        print(f"\n【目标评估】")
        print(f"  理论准确率（8/12生肖）: 66.7%")
        print(f"  实际准确率: {zodiac_accuracy:.2f}%")
        
        if zodiac_accuracy >= 70:
            print(f"  [SUCCESS] 超越目标！（70%+）")
        elif zodiac_accuracy >= 67:
            print(f"  [GOOD] 达到理论预期（67%+）")
        else:
            print(f"  [NEED IMPROVEMENT] 未达标，需要继续优化")
    
    # 显示最近10期详情
    print(f"\n{'='*60}")
    print(f"最近10期详细结果")
    print(f"{'='*60}")
    for result in detailed_results[:10]:
        status = "HIT" if result['zodiac_hit'] else "MISS"
        print(f"\n期号 {result['period']}:")
        print(f"  实际特码: {result['actual_number']} ({result['actual_zodiac']})")
        print(f"  预测8肖: {result['predicted_zodiacs']}")
        print(f"  结果: {status}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    print("V7回测器测试")
    print("\n使用默认V7参数进行测试...")
    
    # 默认V7参数
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
    
    display_backtest_report_v7('macau', default_v7_weights, backtest_range=50)
