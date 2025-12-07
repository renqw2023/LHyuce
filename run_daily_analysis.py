import json
import os
import subprocess
import sys
from datetime import datetime
import locale

# --- Configuration ---
PREDICTION_DIR = 'predictions'
REVIEW_LOG_FILE = 'review_log.json'
LOTTERY_CONFIG = {
    'hk': {
        'data_file': 'HK2025_lottery_data_complete.json',
        'analysis_script': 'advanced_hk_analysis.py'
    },
    'macau': {
        'data_file': 'lottery_data_2025_complete.json',
        'analysis_script': 'advanced_lottery_analysis.py'
    }
}

# --- Helper Functions ---

def load_json(file_path, default=[]):
    """Safely load a JSON file."""
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json(data, file_path):
    """Safely save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def run_command(command, description):
    """Runs a command, prints status, and checks for errors."""
    print(f"正在执行: {description}...")
    try:
        # Use the system's preferred encoding for robust output handling
        preferred_encoding = locale.getpreferredencoding()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding=preferred_encoding,
            errors='replace' # Replace characters that can't be decoded
        )
        if result.returncode != 0:
            print(f"  -> 错误: {description} 执行失败。")
            print(result.stderr)
            return False
        print(f"  -> 成功。")
        return True
    except Exception as e:
        print(f"  -> 错误: 执行命令时发生异常: {e}")
        return False

# --- Core Logic ---

def perform_review(lottery_type, config):
    """
    Performs a review of the last general and special predictions against the latest results.
    """
    print(f"\n--- 开始为 {lottery_type.upper()} 数据进行复盘 ---")
    
    # 1. Load historical data to find the latest result
    all_data = load_json(config['data_file'])
    if not all_data or 'totalRecords' not in all_data or not all_data['totalRecords']:
        print("  -> 无法加载历史数据，跳过复盘。")
        return None
    
    latest_result = all_data['totalRecords'][0]
    latest_period = int(latest_result['period'])
    
    # Extract actual numbers and zodiacs from the latest result
    actual_numbers_list = latest_result.get('numberList', [])
    if len(actual_numbers_list) < 7:
        print(f"  -> 期号 {latest_period} 的开奖结果不完整 (少于7个号码)，跳过复盘。")
        return None

    actual_general_numbers = {int(n['number']) for n in actual_numbers_list[:-1]} # First 6 numbers
    actual_general_zodiacs = {n['shengXiao'] for n in actual_numbers_list[:-1]} # Zodiacs of first 6 numbers
    actual_special_number = int(actual_numbers_list[-1]['number']) # The 7th number
    actual_special_zodiac = actual_numbers_list[-1]['shengXiao'] # Zodiac of the 7th number

    # --- Review General Prediction ---
    general_prediction_file = os.path.join(PREDICTION_DIR, f'{lottery_type}_prediction_for_{latest_period}.json')
    general_prediction_data = load_json(general_prediction_file, default={})
    
    general_review_results = {}
    if general_prediction_data:
        print(f"  -> 成功加载期号 {latest_period} 的通用预测，开始比对...")
        all_actual_winning_numbers = actual_general_numbers.union({actual_special_number})
        general_hits = {
            'hot_numbers': len(all_actual_winning_numbers.intersection(set(general_prediction_data.get('numbers', [])))),
            'combo_2_in_2': 1 if any(set(c).issubset(actual_general_numbers) for c in general_prediction_data.get('combos_2_in_2', [])) else 0,
            'combo_3_in_3': 1 if any(set(c).issubset(actual_general_numbers) for c in general_prediction_data.get('combos_3_in_3', [])) else 0,
            'zodiacs': len(actual_general_zodiacs.intersection(set(general_prediction_data.get('zodiacs', []))))
        }
        general_review_results = {
            'predicted_hot_numbers': general_prediction_data.get('numbers', []),
            'predicted_combos_3': general_prediction_data.get('combos_3_in_3', []),
            'predicted_zodiacs': general_prediction_data.get('zodiacs', []),
            'hits': general_hits
        }
        print(f"  -> 通用复盘结果: 热门号码命中 {general_hits['hot_numbers']} 个, '2中2' {'命中' if general_hits['combo_2_in_2'] else '未命中'}, '3中3' {'命中' if general_hits['combo_3_in_3'] else '未命中'}, 生肖命中 {general_hits['zodiacs']} 个")
    else:
        print(f"  -> 未找到期号 {latest_period} 的通用预测文件或为空，跳过通用复盘。")

    # --- Review Special Prediction ---
    special_prediction_file = os.path.join(PREDICTION_DIR, f'{lottery_type}_special_prediction_for_{latest_period}.json')
    special_prediction_data = load_json(special_prediction_file, default={})

    special_review_results = {}
    if special_prediction_data:
        print(f"  -> 成功加载期号 {latest_period} 的特码预测，开始比对...")
        # FIX: Use 'top_zodiacs' which is the correct key from the new analysis script output
        predicted_special_zodiacs = [z for z, score in special_prediction_data.get('top_zodiacs', [])]
        special_hits = {
            'special_zodiacs': 1 if actual_special_zodiac in predicted_special_zodiacs else 0
        }
        special_review_results = {
            'predicted_special_zodiacs': predicted_special_zodiacs,
            'hits': special_hits
        }
        print(f"  -> 特码复盘结果: 特码生肖 {'命中' if special_hits['special_zodiacs'] else '未命中'}")
    else:
        print(f"  -> 未找到期号 {latest_period} 的特码预测文件或为空，跳过特码复盘。")

    # --- Combine and Log Review ---
    review_entry = {
        'lottery_type': lottery_type,
        'period': latest_period,
        'review_time': datetime.now().isoformat(),
        'actual_general_numbers': sorted(list(actual_general_numbers)),
        'actual_general_zodiacs': sorted(list(actual_general_zodiacs)),
        'actual_special_number': actual_special_number,
        'actual_special_zodiac': actual_special_zodiac,
        'general_prediction_review': general_review_results,
        'special_prediction_review': special_review_results
    }
    
    review_log = load_json(REVIEW_LOG_FILE)
    # Avoid duplicates based on lottery_type and period
    if not any(r['lottery_type'] == lottery_type and r['period'] == latest_period for r in review_log):
        review_log.insert(0, review_entry) # Add to the top
        save_json(review_log, REVIEW_LOG_FILE)
        print(f"  -> 复盘结果已记录至 {REVIEW_LOG_FILE}")
    else:
        print(f"  -> 期号 {latest_period} 的复盘已存在于 {REVIEW_LOG_FILE} 中，跳过追加。")
        
    return review_entry

def generate_new_prediction(lottery_type, config):
    """
    Generates new general and special predictions for the next upcoming period.
    """
    print(f"\n--- 开始为 {lottery_type.upper()} 数据生成新预测 ---")
    
    all_data = load_json(config['data_file'])
    if not all_data or 'totalRecords' not in all_data or not all_data['totalRecords']:
        print("  -> 无法加载历史数据，跳过预测。")
        return
        
    latest_period = int(all_data['totalRecords'][0]['period'])
    next_period = latest_period + 1
    
    print(f"  -> 最新期号为 {latest_period}，将为第 {next_period} 期生成预测。")
    
    # Generate General Prediction
    general_command = f"{sys.executable} {config['analysis_script']} --period {next_period} --prediction_type general"
    run_command(general_command, f"运行 {lottery_type.upper()} 通用分析脚本")

    # Generate Special Prediction
    special_command = f"{sys.executable} {config['analysis_script']} --period {next_period} --prediction_type special"
    run_command(special_command, f"运行 {lottery_type.upper()} 特码分析脚本")

def main():
    """
    Main function to run the full Optimize -> Fetch -> Review -> Predict cycle.
    """
    print("--- 开始每日复盘与预测流程 ---")
    
    # --- Step 1: Optimize Strategies ---
    print("\n--- 开始优化通用策略 ---")
    run_command(f"{sys.executable} optimizer.py", "运行通用策略优化器")
    print("\n--- 开始优化特码策略 ---")
    run_command(f"{sys.executable} optimizer_special.py", "运行特码策略优化器")

    # --- Step 2: Fetch latest data ---
    print("\n--- 开始获取最新彩票数据 ---")
    run_command(f"{sys.executable} fetch_lottery_data.py", "获取最新的澳门彩票数据")
    run_command(f"{sys.executable} fetch_hk_lottery_data.py", "获取最新的香港彩票数据")
    
    # --- Step 3 & 4: Review and Predict for each lottery type ---
    for lottery_type, config in LOTTERY_CONFIG.items():
        perform_review(lottery_type, config)
        generate_new_prediction(lottery_type, config)
        
    print("\n--- 所有任务完成 ---")

if __name__ == "__main__":
    main()