import json
from collections import Counter
import advanced_lottery_analysis as macau_analyzer
import advanced_hk_analysis as hk_analyzer

def run_backtest(lottery_type, weights, backtest_range=100):
    """
    V6 通用回测：权重调整
    优先级：3中3 > 2中2 > 热门生肖/号码
    """
    if lottery_type == 'macau':
        analyzer = macau_analyzer
    elif lottery_type == 'hk':
        analyzer = hk_analyzer
    else:
        return 0 

    full_history = analyzer.load_data()
    min_lookback = 30 
    
    if not full_history or len(full_history) <= min_lookback:
        return 0 

    actual_backtest_range = min(backtest_range, len(full_history) - min_lookback)
    
    metrics = {
        'combo_3_in_3_hits': 0, 
        'combo_2_in_2_hits': 0, 
        'hot_number_hits': 0,
        'zodiac_hits': 0
    }

    for i in range(actual_backtest_range):
        target_draw = full_history[i]
        history_for_prediction = full_history[i+1:]
        
        if not history_for_prediction: continue

        actual_numbers = {int(n['number']) for n in target_draw.get('numberList', [])}
        actual_zodiacs = {n.get('shengXiao') for n in target_draw.get('numberList', [])}
        
        prediction = analyzer.advanced_analysis(history_for_prediction, weights)
        if not prediction: continue

        # 1. 热门号码 (权重降低，作为基础)
        predicted_numbers = set(prediction['numbers'])
        metrics['hot_number_hits'] += len(actual_numbers.intersection(predicted_numbers))

        # 2. 热门生肖 (权重适中)
        predicted_zodiacs = set(prediction['zodiacs'])
        metrics['zodiac_hits'] += len(actual_zodiacs.intersection(predicted_zodiacs))

        # 3. 组合检测 (重中之重)
        for combo in prediction['combos_3_in_3']:
            if set(combo).issubset(actual_numbers):
                metrics['combo_3_in_3_hits'] += 1
                break 
        for combo in prediction['combos_2_in_2']:
            if set(combo).issubset(actual_numbers):
                metrics['combo_2_in_2_hits'] += 1
                break

    # --- V6 评分公式 (严格层级) ---
    # 3中3：大奖，权重 500 (Tier 2)
    # 2中2：中奖，权重 100 (Tier 2)
    # 生肖：基础，权重 10 (Tier 3)
    # 号码：基础，权重 5 (Tier 4)
    fitness_score = (metrics['hot_number_hits'] * 5) + \
                    (metrics['zodiac_hits'] * 10) + \
                    (metrics['combo_2_in_2_hits'] * 100) + \
                    (metrics['combo_3_in_3_hits'] * 500)
    
    return fitness_score

def run_special_backtest(lottery_type, weights, backtest_range=100):
    """
    V6 特码回测：第一梯队 (Tier 1)
    特点：高额奖励命中，严厉惩罚失误
    """
    if lottery_type == 'macau':
        analyzer = macau_analyzer
    elif lottery_type == 'hk':
        analyzer = hk_analyzer
    else:
        return 0 

    full_special_history = analyzer.load_special_number_data()
    lookback = int(weights.get('special_lookback', 20))
    min_lookback = lookback + 5 
    
    if not full_special_history or len(full_special_history) <= min_lookback:
        return 0 

    actual_backtest_range = min(backtest_range, len(full_special_history) - min_lookback)
    
    total_score = 0
    
    for i in range(actual_backtest_range):
        target_special_draw = full_special_history[i]
        history_for_prediction = full_special_history[i+1:]
        
        if not history_for_prediction: continue

        prediction = analyzer.analyze_special_trend(history_for_prediction, weights)
        if not prediction: continue

        predicted_zodiacs = [p[0] for p in prediction.get('top_zodiacs', [])]
        recommended_numbers = prediction.get('recommended_numbers', [])
        
        actual_zodiac = target_special_draw['shengXiao']
        actual_number = target_special_draw['number']

        # V6 极刑评分规则：
        # 1. 生肖命中：+100 分 (辅助指标)
        if actual_zodiac in predicted_zodiacs:
            total_score += 100
        
        # 2. 特码数字命中：+500 分 (核心目标 - Tier 1)
        if actual_number in recommended_numbers:
            total_score += 500
        else:
            # 3. 惩罚机制：未命中 -100 分 (翻倍惩罚，逼迫AI精准)
            total_score -= 100

    return total_score 

def display_backtest_report(lottery_type, weights, backtest_range=100):
    pass