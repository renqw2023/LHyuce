import json
from collections import Counter
from itertools import combinations
import os

# --- Helper Functions for JSON ---
def load_json_safe(file_path, default_value=None):
    if default_value is None:
        default_value = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_value
    return default_value

def save_json_safe(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def append_to_prediction_history(prediction_data, prediction_period, history_file):
    history = load_json_safe(history_file)
    if not any(entry.get('period') == prediction_period for entry in history):
        prediction_data_with_period = prediction_data.copy()
        prediction_data_with_period['period'] = prediction_period
        history.insert(0, prediction_data_with_period)
        save_json_safe(history, history_file)
        print(f"预测结果已追加到历史文件: {history_file}")
    else:
        print(f"期号 {prediction_period} 的预测已存在于历史文件 {history_file} 中，跳过追加。")

# --- RULE DEFINITIONS ---
ZODIAC_MAP = {
    '鼠': {6, 18, 30, 42}, '牛': {5, 17, 29, 41}, '虎': {4, 16, 28, 40},
    '兔': {3, 15, 27, 39}, '龙': {2, 14, 26, 38}, '蛇': {1, 13, 25, 37, 49},
    '马': {12, 24, 36, 48}, '羊': {11, 23, 35, 47}, '猴': {10, 22, 34, 46},
    '鸡': {9, 21, 33, 45}, '狗': {8, 20, 32, 44}, '猪': {7, 19, 31, 43}
}

COLOR_MAP = {
    '绿波': {5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49},
    '红波': {1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46},
    '蓝波': {3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48}
}

ELEMENT_MAP = {
    '金': {3, 4, 11, 12, 25, 26, 33, 34, 41, 42},
    '木': {7, 8, 15, 16, 23, 24, 37, 38, 45, 46},
    '水': {13, 14, 21, 22, 29, 30, 43, 44},
    '火': {1, 2, 9, 10, 17, 18, 31, 32, 39, 40, 47, 48},
    '土': {5, 6, 19, 20, 27, 28, 35, 36, 49}
}

# Binary classifications & Categories
HEAVEN_EARTH_MAP = {'天肖': {'兔', '牛', '马', '猴', '猪', '龙'}, '地肖': {'鼠', '虎', '蛇', '羊', '鸡', '狗'}}
YIN_YANG_MAP = {'阳肖': {'鼠', '虎', '龙', '马', '猴', '狗'}, '阴肖': {'牛', '兔', '蛇', '羊', '鸡', '猪'}}
MALE_FEMALE_MAP = {'男肖': {'鼠', '牛', '虎', '龙', '马', '猴', '狗'}, '女肖': {'兔', '蛇', '羊', '鸡', '猪'}}
AUSPICIOUS_MAP = {'吉肖': {'兔', '龙', '蛇', '马', '羊', '鸡'}, '凶肖': {'鼠', '牛', '虎', '猴', '狗', '猪'}}
SEASON_MAP = {
    '春天': {'虎', '兔', '龙'}, '夏天': {'蛇', '马', '羊'},
    '秋天': {'猴', '鸡', '狗'}, '冬天': {'鼠', '猪', '牛'}
}

ALL_CATEGORIES = {
    "波色": COLOR_MAP, "五行": ELEMENT_MAP, "天地": HEAVEN_EARTH_MAP,
    "阴阳": YIN_YANG_MAP, "男女": MALE_FEMALE_MAP, "吉凶": AUSPICIOUS_MAP, "季节": SEASON_MAP
}

# Reverse mapping
NUM_TO_ZODIAC = {num: z for z, nums in ZODIAC_MAP.items() for num in nums}
NUM_TO_CATEGORY = {cat_name: {num: k for k, v in cat_map.items() for num in v}
                   for cat_name, cat_map in {**{"波色": COLOR_MAP, "五行": ELEMENT_MAP}}.items()}

for cat_name, cat_map in ALL_CATEGORIES.items():
    if cat_name not in NUM_TO_CATEGORY:
        NUM_TO_CATEGORY[cat_name] = {
            num: k for k, z_set in cat_map.items() for z in z_set for num in ZODIAC_MAP[z]
        }

def load_data():
    """Loads and combines all lottery data."""
    all_records = {}
    try:
        with open('lottery_data_2025_complete.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f).get('totalRecords', [])
        for record in new_data:
            if 'period' in record:
                all_records[record['period']] = record
    except FileNotFoundError:
        print("错误: lottery_data_2025_complete.json 未找到。")
        return []
    sorted_periods = sorted(all_records.keys(), key=lambda p: int(p), reverse=True)
    return [all_records[p] for p in sorted_periods]

def load_special_number_data(file_path='lottery_data_2025_complete.json'):
    import json
    import os
    if not os.path.exists(file_path): return []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    special_history = []
    records = data.get('totalRecords', [])
    records.sort(key=lambda x: int(x['period']), reverse=True)
    for record in records:
        if 'numberList' in record and len(record['numberList']) >= 7:
            special_ball = record['numberList'][-1] 
            ball_number = int(special_ball['number'])
            entry = {
                'period': record['period'],
                'number': ball_number,
                'shengXiao': special_ball['shengXiao'],
                'color': NUM_TO_CATEGORY['波色'].get(ball_number, '未知'),
                'wuXing': special_ball['wuXing']
            }
            special_history.append(entry)
    return special_history

def analyze_special_trend(special_history, weights):
    """
    V7 核心算法：8生肖智能覆盖 + 多维度深度分析
    目标：通过8个生肖实现最高准确率（理论值67%+）
    策略：热门生肖(6) + 防守冷门(2) + 多维度交叉验证
    """
    if not special_history:
        return None

    lookback = int(weights.get('special_lookback', 20))
    if lookback < 5: lookback = 5
    
    # 提取基础权重
    w_hot = weights.get('special_hot', 1.0)
    w_gap = weights.get('special_gap', 1.5)
    w_zodiac = weights.get('special_zodiac', 2.0)
    w_color = weights.get('special_color_weight', 1.0)
    w_tail = weights.get('special_tail_weight', 1.0)
    w_cold_protect = weights.get('special_cold_protect', 2.0)
    w_element = weights.get('special_element_weight', 1.0)
    w_balance = weights.get('special_balance_weight', 1.0)
    
    # V7 新增权重
    w_resonance = weights.get('special_resonance', 1.5)
    w_cycle = weights.get('special_cycle_weight', 1.0)
    w_diversity = weights.get('special_diversity_bonus', 1.0)

    recent_specials = special_history[:lookback]

    # --- 1. 多维统计增强版 ---
    # 生肖统计
    zodiac_counts = Counter(r['shengXiao'] for r in recent_specials)
    zodiac_last_seen = {z: 100 for z in ZODIAC_MAP.keys()}
    zodiac_streak = {z: 0 for z in ZODIAC_MAP.keys()}
    
    for i, record in enumerate(special_history):
        z = record['shengXiao']
        if z in zodiac_last_seen and zodiac_last_seen[z] == 100:
            zodiac_last_seen[z] = i
    
    for z in ZODIAC_MAP.keys():
        zodiac_streak[z] = zodiac_last_seen[z]

    # 波色统计
    color_counts = Counter(r['color'] for r in recent_specials)
    total_colors = sum(color_counts.values()) or 1
    color_weights = {c: (count / total_colors) for c, count in color_counts.items()}
    top_colors = {c for c, _ in color_counts.most_common(2)}

    # 尾数统计
    tails = [r['number'] % 10 for r in recent_specials]
    tail_counts = Counter(tails)
    total_tails = sum(tail_counts.values()) or 1
    tail_weights = {t: (count / total_tails) for t, count in tail_counts.items()}
    top_tails = {t for t, _ in tail_counts.most_common(3)}

    # V7 新增：五行统计
    element_counts = Counter(r.get('wuXing', '未知') for r in recent_specials if r.get('wuXing'))
    total_elements = sum(element_counts.values()) or 1
    element_weights = {e: (count / total_elements) for e, count in element_counts.items()}
    
    # V7 新增：周期性分析
    recent_5_zodiacs = [r['shengXiao'] for r in special_history[:5]]
    cycle_pattern = Counter(recent_5_zodiacs)

    # --- 2. 智能评分系统 (生肖层级) ---
    zodiac_scores = {}
    
    for z in ZODIAC_MAP.keys():
        score = 0.0
        
        # 2.1 热度评分
        heat_score = zodiac_counts.get(z, 0) * w_hot
        score += heat_score
        
        # 2.2 遗漏评分（分段加权）
        gap = zodiac_last_seen[z]
        if gap >= 20:
            score += w_gap * 3.0
        elif gap >= 12:
            score += w_gap * 2.0
        elif gap >= 6:
            score += w_gap * 1.0
        elif gap <= 2:
            score += w_gap * 0.3
        
        # 2.3 周期性加分
        if z in cycle_pattern:
            score += cycle_pattern[z] * w_cycle
        
        # 2.4 平衡性加分
        avg_count = sum(zodiac_counts.values()) / 12
        if zodiac_counts.get(z, 0) < avg_count:
            score += w_balance * (avg_count - zodiac_counts.get(z, 0))
        
        zodiac_scores[z] = score
    
    # --- 3. 多维度交叉验证 ---
    for z in ZODIAC_MAP.keys():
        z_numbers = ZODIAC_MAP[z]
        
        color_match = 0
        tail_match = 0
        element_match = 0
        
        for num in z_numbers:
            c = NUM_TO_CATEGORY['波色'].get(num)
            t = num % 10
            e = NUM_TO_CATEGORY['五行'].get(num)
            
            if c in top_colors:
                color_match += 1
            if t in top_tails:
                tail_match += 1
            if e in element_weights:
                element_match += element_weights[e]
        
        # 属性匹配加分
        zodiac_scores[z] += (color_match / len(z_numbers)) * w_color * 5
        zodiac_scores[z] += (tail_match / len(z_numbers)) * w_tail * 5
        zodiac_scores[z] += element_match * w_element * 2
    
    # --- 4. 最终8生肖智能选择 ---
    # 策略：前6名热门 + 2个防守位（遗漏最久的）
    sorted_zodiacs = sorted(zodiac_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 选择前6名
    selected_8_zodiacs = sorted_zodiacs[:6]
    
    # 添加2个防守位
    remaining_zodiacs = sorted_zodiacs[6:]
    defense_candidates = sorted(remaining_zodiacs, key=lambda x: zodiac_last_seen[x[0]], reverse=True)
    selected_8_zodiacs.extend(defense_candidates[:2])
    
    # --- 5. 号码推荐（基于8生肖） ---
    number_final_scores = Counter()
    selected_zodiac_names = {z[0] for z in selected_8_zodiacs}
    top_6_zodiacs = [z[0] for z in sorted_zodiacs[:6]]
    
    for num in range(1, 50):
        z = NUM_TO_ZODIAC.get(num)
        
        # 只考虑8个推荐生肖中的号码
        if z not in selected_zodiac_names:
            continue
            
        c = NUM_TO_CATEGORY['波色'].get(num)
        t = num % 10
        e = NUM_TO_CATEGORY['五行'].get(num)
        
        # 基础分
        score = zodiac_scores.get(z, 0) * w_zodiac
        score += color_weights.get(c, 0) * w_color * 10
        score += tail_weights.get(t, 0) * w_tail * 10
        score += element_weights.get(e, 0) * w_element * 5
        
        # 共振检测
        resonance_level = 0
        if z in top_6_zodiacs:
            resonance_level += 1
        if c in top_colors:
            resonance_level += 1
        if t in top_tails:
            resonance_level += 1
        
        if resonance_level >= 2:
            score *= w_resonance
        
        number_final_scores[num] = score
    
    # --- 结果 ---
    recommended_numbers = [num for num, s in number_final_scores.most_common(12)]
    
    predicted_color = color_counts.most_common(1)[0][0] if color_counts else "未知"
    predicted_tail = tail_counts.most_common(1)[0][0] if tail_counts else -1
    predicted_element = element_counts.most_common(1)[0][0] if element_counts else "未知"

    return {
        "top_zodiacs": selected_8_zodiacs,
        "predicted_color": predicted_color,
        "predicted_tail": predicted_tail,
        "predicted_element": predicted_element,
        "recommended_numbers": recommended_numbers,
        "defense_info": {
            "coldest_zodiacs": [z for z, gap in sorted(zodiac_last_seen.items(), key=lambda x: x[1], reverse=True)[:3]]
        }
    }

def advanced_analysis(history, weights):
    """V6 通用分析（保持不变）"""
    if not history:
        return None

    trend_lookback = int(weights.get('trend_lookback', 10))
    if trend_lookback <= 0: trend_lookback = 10

    category_trends = {cat: Counter() for cat in ALL_CATEGORIES}
    actual_lookback = min(trend_lookback, len(history))
    recent_history = history[:actual_lookback]
    for record in recent_history:
        numbers = {int(n['number']) for n in record.get('numberList', [])}
        for cat_name, cat_map in ALL_CATEGORIES.items():
            counts = Counter(NUM_TO_CATEGORY[cat_name].get(n) for n in numbers)
            category_trends[cat_name].update(counts)

    number_scores = Counter()
    all_numbers = set(range(1, 50))
    number_freq = Counter(int(n['number']) for r in history for n in r.get('numberList', []))
    last_seen = {n: len(history) for n in all_numbers}
    for i, record in enumerate(history):
        numbers = {int(n['number']) for n in record.get('numberList', [])}
        for n in numbers:
            if n in last_seen and last_seen[n] == len(history):
                 last_seen[n] = i
    
    for num in all_numbers:
        number_scores[num] += number_freq.get(num, 0) * weights.get('hot_score', 0.5)
        number_scores[num] += last_seen.get(num, 0) * weights.get('cold_score', 0.8)

    for num in all_numbers:
        for cat_name, trend_counts in category_trends.items():
            num_cat = NUM_TO_CATEGORY[cat_name].get(num)
            if num_cat:
                score = trend_counts.get(num_cat, 0)
                number_scores[num] += score * weights.get('category_trend', 1.0)

    pair_counts = Counter()
    for record in history:
        nums = sorted([int(n['number']) for n in record.get('numberList', [])[:-1]])
        for pair in combinations(nums, 2):
            pair_counts[pair] += 1

    triplet_counts = Counter()
    for record in history:
        nums = sorted([int(n['number']) for n in record.get('numberList', [])[:-1]])
        for triplet in combinations(nums, 3):
            triplet_counts[triplet] += 1
            
    top_20_numbers = [num for num, score in number_scores.most_common(20)]
    
    combo_2_scores = Counter()
    for combo in combinations(top_20_numbers, 2):
        sorted_combo = tuple(sorted(combo))
        score = sum(number_scores[n] for n in sorted_combo)
        
        colors = {NUM_TO_CATEGORY['波色'].get(n) for n in sorted_combo}
        if len(colors) > 1:
            score *= weights.get('combo_2_diversity', 1.1)
            
        co_occurrence_bonus = pair_counts.get(sorted_combo, 0) * weights.get('co_occurrence_weight', 1.0)
        score += co_occurrence_bonus
        combo_2_scores[sorted_combo] = score

    combo_3_scores = Counter()
    for combo in combinations(top_20_numbers, 3):
        sorted_combo = tuple(sorted(combo))
        combo_sum = sum(combo)
        if not (40 <= combo_sum <= 110): continue 

        score = sum(number_scores[n] for n in combo)
        
        colors = {NUM_TO_CATEGORY['波色'].get(n) for n in combo}
        elements = {NUM_TO_CATEGORY['五行'].get(n) for n in combo}
        
        if len(colors) > 2:
            score *= weights.get('combo_3_color_diversity', 1.1)
        if len(elements) > 2:
            score *= weights.get('combo_3_element_diversity', 1.1)
        
        triplet_bonus = triplet_counts.get(sorted_combo, 0) * weights.get('triplet_weight', 1.0) * 10
        score += triplet_bonus
            
        combo_3_scores[combo] = score

    zodiac_scores_general = Counter()
    for z, nums in ZODIAC_MAP.items():
        score = sum(number_scores[n] for n in nums)
        zodiac_scores_general[z] = score

    results_raw = {
        "zodiacs": [z for z, score in zodiac_scores_general.most_common(5)],
        "numbers": [n for n, score in number_scores.most_common(10)],
        "combos_2_in_2": [c for c, score in combo_2_scores.most_common(5)],
        "combos_3_in_3": [c for c, score in combo_3_scores.most_common(5)],
        "special_number": number_scores.most_common(1)[0][0] if number_scores else None,
        "special_zodiac": zodiac_scores_general.most_common(1)[0][0] if zodiac_scores_general else None
    }
    return results_raw


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run V7 advanced analysis for lottery.")
    parser.add_argument('--period', type=int, required=True)
    parser.add_argument('--prediction_type', type=str, default='special', choices=['general', 'special'])
    args = parser.parse_args()
    
    prediction_period = args.period
    prediction_type = args.prediction_type
    
    RAW_PREDICTION_DIR = 'predictions'
    os.makedirs(RAW_PREDICTION_DIR, exist_ok=True)

    if prediction_type == 'special':
        STRATEGY_FILE = 'best_special_strategy_macau_v7.json'
        FORMATTED_OUTPUT_FILE = 'macau_special_analysis_results_v7.json'
        PREDICTION_HISTORY_FILE = 'macau_special_prediction_history_v7.json'
        raw_prediction_filename = os.path.join(RAW_PREDICTION_DIR, f'macau_special_prediction_v7_for_{prediction_period}.json')
        
        weights = {}
        try:
            with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
                weights = json.load(f)
            print(f"成功加载V7最优特码策略 '{STRATEGY_FILE}'。")
        except FileNotFoundError:
            print(f"注意: 未找到V7策略文件，将使用默认V7策略。")

        special_historical_data = load_special_number_data()
        if special_historical_data:
            print(f"为澳门第 {prediction_period} 期V7特码分析加载了 {len(special_historical_data)} 条历史数据。")
            analysis_results_raw = analyze_special_trend(special_historical_data, weights)
            
            if analysis_results_raw:
                append_to_prediction_history(analysis_results_raw, prediction_period, PREDICTION_HISTORY_FILE)

                try:
                    with open(raw_prediction_filename, 'w', encoding='utf-8') as f:
                        json.dump(analysis_results_raw, f, ensure_ascii=False, indent=2)
                    print(f"V7原始特码预测存档已保存至 {raw_prediction_filename}")
                except Exception as e:
                    print(f"错误: {e}")

                results_formatted = {
                    "分析期号": prediction_period,
                    "V7特码推荐生肖(8个)": [f"{z[0]} (分数: {z[1]:.2f})" for z in analysis_results_raw["top_zodiacs"]],
                    "预测波色": analysis_results_raw["predicted_color"],
                    "预测尾数": analysis_results_raw["predicted_tail"],
                    "预测五行": analysis_results_raw.get("predicted_element", "未知"),
                    "综合推荐号码": analysis_results_raw["recommended_numbers"],
                    "防守信息": analysis_results_raw.get("defense_info", {}),
                    "算法版本": "V7 - 8生肖智能覆盖"
                }
                try:
                    with open(FORMATTED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(results_formatted, f, ensure_ascii=False, indent=2)
                    print(f"V7格式化特码分析结果已保存至 {FORMATTED_OUTPUT_FILE}")
                except Exception as e:
                    print(f"错误: {e}")
        else:
            print("没有足够的历史数据进行V7特码分析。")
