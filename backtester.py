import json
from collections import Counter
import advanced_lottery_analysis as macau_analyzer
import advanced_hk_analysis as hk_analyzer

def run_backtest(lottery_type, weights, backtest_range=100):
    """
    Runs a backtest for a given lottery type with a specific set of weights.
    Returns a fitness score, balancing stability (hot numbers/zodiacs) and jackpots (combos).
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

        # 1. Check for hot number hits
        predicted_numbers = set(prediction['numbers'])
        metrics['hot_number_hits'] += len(actual_numbers.intersection(predicted_numbers))

        # 2. Check for Zodiac hits
        predicted_zodiacs = set(prediction['zodiacs'])
        metrics['zodiac_hits'] += len(actual_zodiacs.intersection(predicted_zodiacs))

        # 3. Check for combo hits
        for combo in prediction['combos_3_in_3']:
            if set(combo).issubset(actual_numbers):
                metrics['combo_3_in_3_hits'] += 1
                break 
        for combo in prediction['combos_2_in_2']:
            if set(combo).issubset(actual_numbers):
                metrics['combo_2_in_2_hits'] += 1
                break

    # --- 评分公式 (注重基础稳定性) ---
    fitness_score = (metrics['hot_number_hits'] * 10) + \
                    (metrics['zodiac_hits'] * 15) + \
                    (metrics['combo_2_in_2_hits'] * 40) + \
                    (metrics['combo_3_in_3_hits'] * 100)
    
    return fitness_score

def run_special_backtest(lottery_type, weights, backtest_range=100):
    """
    V5 升级版：特码回测 (带惩罚机制与生肖加权)
    """
    if lottery_type == 'macau':
        analyzer = macau_analyzer
    elif lottery_type == 'hk':
        analyzer = hk_analyzer
    else:
        return 0 

    full_special_history = analyzer.load_special_number_data()
    # 动态获取 lookback，确保数据足够
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

        # 从推荐列表中提取生肖和号码
        predicted_zodiacs = [p[0] for p in prediction.get('top_zodiacs', [])]
        recommended_numbers = prediction.get('recommended_numbers', [])
        
        actual_zodiac = target_special_draw['shengXiao']
        actual_number = target_special_draw['number']

        # 评分规则 V5 (响应用户要求：提高生肖命中权重)：
        # 1. 生肖命中：+100 分 (原 50 分，翻倍以强调生肖准确性)
        if actual_zodiac in predicted_zodiacs:
            total_score += 100
        
        # 2. 号码命中：+500 分 (大奖)
        if actual_number in recommended_numbers:
            total_score += 500
        else:
            # 3. 惩罚机制：号码未命中 -50 分
            # 逼迫 AI 优化排序，将正确号码挤进前8名
            total_score -= 50

    return total_score 

def display_backtest_report(lottery_type, weights, backtest_range=100):
    # 此函数保持不变，用于调试
    pass
