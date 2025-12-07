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
    """Loads and combines all HK lottery data."""
    all_records = {}
    try:
        with open('HK2025_lottery_data_complete.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f).get('totalRecords', [])
        for record in new_data:
            if 'period' in record:
                all_records[record['period']] = record
    except FileNotFoundError:
        print("错误: HK2025_lottery_data_complete.json 未找到。")
        return []
    sorted_periods = sorted(all_records.keys(), key=lambda p: int(p), reverse=True)
    return [all_records[p] for p in sorted_periods]

def load_special_number_data(file_path='HK2025_lottery_data_complete.json'):
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
    V5 深度升级：全域号码评分系统 (打破生肖漏斗，强化特码命中)
    """
    if not special_history:
        return None

    # 1. 动态提取回顾期 (由 AI 决定看多远)
    lookback = int(weights.get('special_lookback', 20))
    if lookback < 5: lookback = 5
    
    # 提取权重
    w_hot = weights.get('special_hot', 1.0)
    w_gap = weights.get('special_gap', 1.5)
    w_zodiac = weights.get('special_zodiac', 2.0)
    w_color = weights.get('special_color_weight', 1.0)
    w_tail = weights.get('special_tail_weight', 1.0)
    w_cold_protect = weights.get('special_cold_protect', 2.0)

    recent_specials = special_history[:lookback]

    # --- A. 基础维度分析 ---
    
    # 1. 生肖分析
    zodiac_counts = Counter(r['shengXiao'] for r in recent_specials)
    zodiac_last_seen = {z: 100 for z in ZODIAC_MAP.keys()}
    for i, record in enumerate(special_history):
        z = record['shengXiao']
        if z in zodiac_last_seen and zodiac_last_seen[z] == 100:
            zodiac_last_seen[z] = i
    coldest_zodiac = max(zodiac_last_seen, key=zodiac_last_seen.get)

    zodiac_scores = {}
    for z in ZODIAC_MAP.keys():
        score = zodiac_counts.get(z, 0) * w_hot
        gap = zodiac_last_seen[z]
        if gap > 12: score += w_gap * 2
        elif gap == 1: score += w_gap * 0.5
        zodiac_scores[z] = score
    # 生肖防守加分
    zodiac_scores[coldest_zodiac] += w_cold_protect

    # 2. 波色分析
    color_counts = Counter(r['color'] for r in recent_specials)
    total_colors = sum(color_counts.values()) or 1
    color_weights = {c: (count / total_colors) for c, count in color_counts.items()}
    top_color = color_counts.most_common(1)[0][0] if color_counts else "未知"

    # 3. 尾数分析
    tails = [r['number'] % 10 for r in recent_specials]
    tail_counts = Counter(tails)
    total_tails = sum(tail_counts.values()) or 1
    tail_weights = {t: (count / total_tails) for t, count in tail_counts.items()}
    top_tail = tail_counts.most_common(1)[0][0] if tail_counts else -1

    # 4. 号码独立遗漏分析 (New)
    number_last_seen = {}
    for i, record in enumerate(special_history):
        n = record['number']
        if n not in number_last_seen:
            number_last_seen[n] = i
    
    # --- B. 全域号码评分 (核心变更：直接对49个号码打分) ---
    number_final_scores = Counter()

    for num in range(1, 50):
        z = NUM_TO_ZODIAC.get(num)
        c = NUM_TO_CATEGORY['波色'].get(num)
        t = num % 10
        
        # 基础分：来自生肖 (权重由 AI 决定)
        score = zodiac_scores.get(z, 0) * w_zodiac
        
        # 加成分：来自波色 (模糊加权)
        score += color_weights.get(c, 0) * w_color * 10
        
        # 加成分：来自尾数 (模糊加权)
        score += tail_weights.get(t, 0) * w_tail * 10
        
        # 独立防守：如果该号码极度冷门 (例如超过40期未出)
        gap = number_last_seen.get(num, 100)
        if gap > 40:
            score += w_cold_protect * 0.5 # 号码级防守
            
        number_final_scores[num] = score

    # --- C. 结果提取 ---
    # 推荐前 8 个号码
    recommended_numbers = [num for num, s in number_final_scores.most_common(8)]
    
    # 为了展示，反推推荐生肖 (取前4名，依据zodiac_scores)
    top_zodiacs_raw = sorted(zodiac_scores.items(), key=lambda x: x[1], reverse=True)[:4]

    return {
        "top_zodiacs": top_zodiacs_raw,
        "predicted_color": top_color,
        "predicted_tail": top_tail,
        "recommended_numbers": recommended_numbers,
        "coldest_zodiac_defense": coldest_zodiac
    }

def advanced_analysis(history, weights):
    """
    Performs advanced analysis based on rules, trends, and dynamic weights.
    (已升级，包含共现矩阵分析)
    """
    if not history:
        return None

    trend_lookback = int(weights.get('trend_lookback', 10))
    if trend_lookback <= 0: trend_lookback = 10

    # --- Trend Analysis ---
    category_trends = {cat: Counter() for cat in ALL_CATEGORIES}
    actual_lookback = min(trend_lookback, len(history))
    recent_history = history[:actual_lookback]
    for record in recent_history:
        numbers = {int(n['number']) for n in record.get('numberList', [])}
        for cat_name, cat_map in ALL_CATEGORIES.items():
            counts = Counter(NUM_TO_CATEGORY[cat_name].get(n) for n in numbers)
            category_trends[cat_name].update(counts)

    # --- Number Scoring ---
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

    # --- 共现矩阵分析 ---
    pair_counts = Counter()
    for record in history:
        nums = sorted([int(n['number']) for n in record.get('numberList', [])[:-1]])
        for pair in combinations(nums, 2):
            pair_counts[pair] += 1

    # --- Combination Scoring ---
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
        combo_sum = sum(combo)
        if not (40 <= combo_sum <= 110):
            continue 

        score = sum(number_scores[n] for n in combo)
        
        colors = {NUM_TO_CATEGORY['波色'].get(n) for n in combo}
        elements = {NUM_TO_CATEGORY['五行'].get(n) for n in combo}
        
        if len(colors) > 2:
            score *= weights.get('combo_3_color_diversity', 1.1)
        if len(elements) > 2:
            score *= weights.get('combo_3_element_diversity', 1.1)
            
        combo_3_scores[combo] = score

    # --- Zodiac Scoring ---
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
    import os

    parser = argparse.ArgumentParser(description="Run advanced analysis for HK lottery.")
    parser.add_argument('--period', type=int, required=True, help='The lottery period to generate a prediction for.')
    parser.add_argument('--prediction_type', type=str, default='general', choices=['general', 'special'],
                        help='Type of prediction: "general" for all 7 numbers, "special" for the 7th number only.')
    args = parser.parse_args()
    
    prediction_period = args.period
    prediction_type = args.prediction_type
    
    RAW_PREDICTION_DIR = 'predictions'
    os.makedirs(RAW_PREDICTION_DIR, exist_ok=True)

    if prediction_type == 'general':
        STRATEGY_FILE = 'best_strategy_hk.json'
        FORMATTED_OUTPUT_FILE = 'hk_analysis_results.json'
        PREDICTION_HISTORY_FILE = 'hk_prediction_history.json'
        raw_prediction_filename = os.path.join(RAW_PREDICTION_DIR, f'hk_prediction_for_{prediction_period}.json')
        
        weights = {}
        try:
            with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
                weights = json.load(f)
            print(f"成功加载最优策略 '{STRATEGY_FILE}'。")
        except FileNotFoundError:
            print(f"注意: 未找到最优策略文件 '{STRATEGY_FILE}'。将使用默认通用策略进行分析。")
        except Exception as e:
            print(f"错误: 加载策略文件失败: {e}。将使用默认通用策略。")

        historical_data = load_data()
        if historical_data:
            print(f"为香港第 {prediction_period} 期通用分析加载了 {len(historical_data)} 条历史数据。")
            analysis_results_raw = advanced_analysis(historical_data, weights)
            
            if analysis_results_raw:
                append_to_prediction_history(analysis_results_raw, prediction_period, PREDICTION_HISTORY_FILE)

                try:
                    with open(raw_prediction_filename, 'w', encoding='utf-8') as f:
                        json.dump(analysis_results_raw, f, ensure_ascii=False, indent=2)
                    print(f"原始通用预测存档已保存至 {raw_prediction_filename}")
                except Exception as e:
                    print(f"错误: 保存原始通用预测至 {raw_prediction_filename} 失败。 {e}")

                results_formatted = {
                    "分析期号": prediction_period,
                    "热门生肖": [f"{z}" for z in analysis_results_raw["zodiacs"]],
                    "热门号码": [f"号码 {n}" for n in analysis_results_raw["numbers"]],
                    "'2中2' 组合": [f"组合 {c}" for c in analysis_results_raw["combos_2_in_2"]],
                    "'3中3' 组合": [f"组合 {c}" for c in analysis_results_raw["combos_3_in_3"]]
                }
                try:
                    with open(FORMATTED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(results_formatted, f, ensure_ascii=False, indent=2)
                    print(f"格式化通用分析结果已保存至 {FORMATTED_OUTPUT_FILE}")
                except Exception as e:
                    print(f"错误: 保存格式化通用结果至 {FORMATTED_OUTPUT_FILE} 失败。 {e}")
        else:
            print("没有足够的历史数据进行通用分析。")

    elif prediction_type == 'special':
        STRATEGY_FILE = 'best_special_strategy_hk.json'
        FORMATTED_OUTPUT_FILE = 'hk_special_analysis_results.json'
        PREDICTION_HISTORY_FILE = 'hk_special_prediction_history.json'
        raw_prediction_filename = os.path.join(RAW_PREDICTION_DIR, f'hk_special_prediction_for_{prediction_period}.json')
        
        weights = {}
        try:
            with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
                weights = json.load(f)
            print(f"成功加载最优特码策略 '{STRATEGY_FILE}'。")
        except FileNotFoundError:
            print(f"注意: 未找到最优特码策略文件 '{STRATEGY_FILE}'。将使用默认特码策略进行分析。")
        except Exception as e:
            print(f"错误: 加载特码策略文件失败: {e}。将使用默认特码策略。")

        special_historical_data = load_special_number_data()
        if special_historical_data:
            print(f"为香港第 {prediction_period} 期特码分析加载了 {len(special_historical_data)} 条历史数据。")
            analysis_results_raw = analyze_special_trend(special_historical_data, weights)
            
            if analysis_results_raw:
                append_to_prediction_history(analysis_results_raw, prediction_period, PREDICTION_HISTORY_FILE)

                try:
                    with open(raw_prediction_filename, 'w', encoding='utf-8') as f:
                        json.dump(analysis_results_raw, f, ensure_ascii=False, indent=2)
                    print(f"原始特码预测存档已保存至 {raw_prediction_filename}")
                except Exception as e:
                    print(f"错误: 保存原始特码预测至 {raw_prediction_filename} 失败。 {e}")

                results_formatted = {
                    "分析期号": prediction_period,
                    "特码推荐生肖": [f"{z[0]} (分数: {z[1]:.2f})" for z in analysis_results_raw["top_zodiacs"]],
                    "预测波色": analysis_results_raw["predicted_color"],
                    "预测尾数": analysis_results_raw["predicted_tail"],
                    "综合推荐号码": analysis_results_raw["recommended_numbers"],
                    "特码分析说明": "基于生肖、波色、尾数综合分析，推荐分数最高的号码。"
                }
                try:
                    with open(FORMATTED_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                        json.dump(results_formatted, f, ensure_ascii=False, indent=2)
                    print(f"格式化特码分析结果已保存至 {FORMATTED_OUTPUT_FILE}")
                except Exception as e:
                    print(f"错误: 保存格式化特码结果至 {FORMATTED_OUTPUT_FILE} 失败。 {e}")
        else:
            print("没有足够的历史数据进行特码分析。")