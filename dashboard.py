import streamlit as st
import subprocess
import sys
import os
import glob
import json
import pandas as pd
from datetime import datetime
import re

# --- Page Configuration and Custom CSS ---
st.set_page_config(page_title="智能策略分析平台", page_icon="💎", layout="wide")

st.markdown("""
<style>
/* --- Font and Base --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* --- Main Background --- */
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(94, 234, 212, 0.1);
}

/* --- Cards & Containers --- */
.card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(94, 234, 212, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(94, 234, 212, 0.1) 100%);
    border: 1px solid rgba(94, 234, 212, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0ea5e9 0%, #5eead4 100%);
}

/* --- Custom Result Display --- */
.result-title { font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem; color: #f8fafc; }
.result-grid { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.number-pill {
    display: inline-block;
    background: linear-gradient(135deg, #0ea5e9 0%, #5eead4 100%);
    color: #0f172a;
    font-weight: 700;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 1.125rem;
}
.item-pill { padding: 5px 14px; background-color: #1e293b; border-radius: 16px; color: #e2e8f0; }
.combo-paren { font-size: 2rem; color: #5eead4; font-weight: 300; vertical-align: middle; margin: 0 4px; }
.hit { border: 2px solid #48bb78 !important; box-shadow: 0 0 15px rgba(72, 187, 120, 0.7); }
.miss { opacity: 0.6; }
</style>
""", unsafe_allow_html=True)


# --- Data Loading Functions ---
@st.cache_data
def load_json_data(file_path, default_value=None):
    if default_value is None:
        default_value = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_value
    return default_value

# --- UI Rendering Functions ---

def render_kpis(lottery_type):
    general_strategy = load_json_data(f'best_strategy_{lottery_type}.json', default_value={})
    special_strategy = load_json_data(f'best_special_strategy_{lottery_type}.json', default_value={})
    
    general_log_data = load_json_data(f'{lottery_type}_optimizer_log.json')
    special_log_data = load_json_data(f'{lottery_type}_special_optimizer_log.json')

    data_file = 'HK2025_lottery_data_complete.json' if lottery_type == 'hk' else 'lottery_data_2025_complete.json'
    lottery_data = load_json_data(data_file)

    general_score, general_lookback = "--", "--"
    if general_log_data:
        general_score = f"{general_log_data[-1]['best_fitness']:.0f}"
    if general_strategy:
        general_lookback = f"{int(general_strategy.get('trend_lookback', 0))}"

    special_score = "--"
    if special_log_data:
        special_score = f"{special_log_data[-1]['best_fitness']:.0f}"

    total_draws = "--"
    if lottery_data:
        total_draws = len(lottery_data.get('totalRecords', []))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧠 AI 通用策略得分", general_score)
    col2.metric("⌛ 通用最佳回顾期", f"{general_lookback} 期")
    col3.metric("🎯 AI 特码策略得分", special_score)
    col4.metric("📚 数据总量", f"{total_draws} 期")

def render_analysis_results(lottery_type):
    # --- General Analysis Results ---
    st.subheader("通用分析结果 (正码推荐)", divider='blue')
    general_results = load_json_data(f'{lottery_type}_analysis_results.json')
    if not general_results:
        st.info("未找到通用分析结果。请前往“执行中心”运行每日分析。")
    else:
        # Display the period number first if it exists
        if '分析期号' in general_results:
            st.markdown(f"#### 正在显示第 **{general_results['分析期号']}** 期分析结果")
        
        for key, values in general_results.items():
            # Skip the period number as it's not an iterable list to display in the grid
            if key == '分析期号':
                continue

            st.markdown(f'<h3 class="result-title">{key}</h3>', unsafe_allow_html=True)
            html = '<div class="result-grid">'
            for value in values:
                cleaned_value = str(value).replace("'", "").replace("号码 ", "")
                numbers = re.findall(r'\d+', cleaned_value)
                
                if "组合" in key:
                    combo_html = ", ".join([f'<span class="number-pill">{num}</span>' for num in numbers])
                    html += f'<div><span class="combo-paren">(</span>{combo_html}<span class="combo-paren">)</span></div>'
                elif numbers:
                    html += f'<span class="number-pill">{cleaned_value}</span>'
                else:
                    html += f'<span class="item-pill">{cleaned_value}</span>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            st.divider()

    # --- Special Analysis Results ---
    st.subheader("特码狙击 (第7个号码)", divider='blue')
    special_results = load_json_data(f'{lottery_type}_special_analysis_results.json')
    if not special_results:
        st.info("未找到特码分析结果。请前往“执行中心”运行每日分析。")
    else:
        # Display the period number first if it exists
        if '分析期号' in special_results:
            st.markdown(f"#### 正在显示第 **{special_results['分析期号']}** 期特码分析结果")

        for key, values in special_results.items():
            # Skip the period number as it's not an iterable list to display in the grid
            if key == '分析期号':
                continue

            st.markdown(f'<h3 class="result-title">{key}</h3>', unsafe_allow_html=True)
            html = '<div class="result-grid">'
            # Handle special case for list of pre-formatted strings
            if key == "特码推荐生肖":
                for value in values:
                    # The 'value' is a pre-formatted string like "蛇 (分数: 12.50)"
                    html += f'<span class="item-pill">{value}</span>'
            # Handle special case for list of numbers
            elif key == "综合推荐号码":
                 for number in values:
                    html += f'<span class="number-pill">{number}</span>'
            # Handle other string/list values
            else:
                # Check if values is a list to iterate
                if isinstance(values, list):
                    for value in values:
                        html += f'<span class="item-pill">{value}</span>'
                else: # It's a single string (like the description)
                    html += f'<span class="item-pill" style="width: 100%; text-align: left;">{values}</span>'

            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            st.divider()

def render_learning_curve(lottery_type):
    general_log_data = load_json_data(f'{lottery_type}_optimizer_log.json')
    special_log_data = load_json_data(f'{lottery_type}_special_optimizer_log.json')

    st.markdown("##### 通用策略学习曲线")
    if general_log_data:
        df_log = pd.DataFrame(general_log_data)
        df_log.rename(columns={'generation': '代数', 'best_fitness': '每代最高分', 'average_fitness': '每代平均分'}, inplace=True)
        st.line_chart(df_log, x='代数', y=['每代最高分', '每代平均分'], color=["#5eead4", "#374151"])
    else:
        st.info("未找到通用策略优化日志。请前往“执行中心”运行策略优化。")

    st.markdown("##### 特码策略学习曲线")
    if special_log_data:
        df_log_special = pd.DataFrame(special_log_data)
        df_log_special.rename(columns={'generation': '代数', 'best_fitness': '每代最高分', 'average_fitness': '每代平均分'}, inplace=True)
        st.line_chart(df_log_special, x='代数', y=['每代最高分', '每代平均分'], color=["#facc15", "#b45309"]) # Use different colors for special
    else:
        st.info("未找到特码策略优化日志。请前往“执行中心”运行特码策略优化。")

def render_review_center():
    st.title("🔬 复盘中心")
    st.markdown("在这里，您可以回顾历史预测的准确性，并跟踪模型的长期表现。")

    review_log_raw = load_json_data('review_log.json')
    if not review_log_raw:
        st.info("暂无复盘记录。请在“执行中心”运行“每日分析”以生成第一条复盘记录。")
        return

    # Preprocess review_log_raw to ensure all necessary keys exist and are in the correct format
    # This is crucial for older entries that might not have the new structure
    processed_review_log = []
    for entry in review_log_raw:
        # Create a mutable copy
        current_entry = entry.copy()

        # Handle old structure where general prediction data was at top level
        if 'predicted_hot_numbers' in current_entry and 'general_prediction_review' not in current_entry:
            current_entry['general_prediction_review'] = {
                'predicted_hot_numbers': current_entry.pop('predicted_hot_numbers', []),
                'predicted_combos_3': current_entry.pop('predicted_combos_3', []),
                'predicted_zodiacs': current_entry.pop('predicted_zodiacs', []),
                'hits': current_entry.pop('hits', {})
            }
            current_entry['actual_general_numbers'] = current_entry.pop('actual_numbers', [])
            current_entry['actual_general_zodiacs'] = current_entry.pop('actual_zodiacs', [])
            # Default special fields for old entries
            current_entry['actual_special_number'] = 'N/A'
            current_entry['actual_special_zodiac'] = 'N/A'
            current_entry['special_prediction_review'] = {'hits': {}, 'predicted_special_zodiacs': []}
        
        # Ensure all expected top-level keys exist with defaults
        current_entry['actual_general_numbers'] = current_entry.get('actual_general_numbers', [])
        current_entry['actual_general_zodiacs'] = current_entry.get('actual_general_zodiacs', [])
        current_entry['actual_special_number'] = current_entry.get('actual_special_number', 'N/A')
        current_entry['actual_special_zodiac'] = current_entry.get('actual_special_zodiac', 'N/A')

        # Ensure general_prediction_review structure
        general_review = current_entry.get('general_prediction_review', {})
        general_review['hits'] = general_review.get('hits', {})
        general_review['predicted_hot_numbers'] = general_review.get('predicted_hot_numbers', [])
        general_review['predicted_combos_3'] = general_review.get('predicted_combos_3', [])
        general_review['predicted_zodiacs'] = general_review.get('predicted_zodiacs', [])
        current_entry['general_prediction_review'] = general_review
        
        # Ensure special_prediction_review structure
        special_review = current_entry.get('special_prediction_review', {})
        special_review['hits'] = special_review.get('hits', {})
        special_review['predicted_special_zodiacs'] = special_review.get('predicted_special_zodiacs', [])
        current_entry['special_prediction_review'] = special_review

        processed_review_log.append(current_entry)

    df = pd.DataFrame(processed_review_log)

    st.subheader("总体表现摘要", divider='blue')
    total_reviews = len(df)
    
    # --- General Prediction KPIs ---
    total_general_hot_number_hits = sum(item['general_prediction_review']['hits'].get('hot_numbers', 0) 
                                        for item in processed_review_log)
    total_general_hot_numbers_predicted = sum(len(item['general_prediction_review']['predicted_hot_numbers']) 
                                              for item in processed_review_log)
    general_hot_number_hit_rate = (total_general_hot_number_hits / total_general_hot_numbers_predicted) * 100 if total_general_hot_numbers_predicted > 0 else 0

    total_general_zodiac_hits = sum(item['general_prediction_review']['hits'].get('zodiacs', 0) 
                                    for item in processed_review_log)
    total_general_zodiacs_predicted = sum(len(item['general_prediction_review']['predicted_zodiacs']) 
                                          for item in processed_review_log)
    general_zodiac_hit_rate = (total_general_zodiac_hits / total_general_zodiacs_predicted) * 100 if total_general_zodiacs_predicted > 0 else 0

    general_combo_2_hits = sum(item['general_prediction_review']['hits'].get('combo_2_in_2', 0) 
                               for item in processed_review_log)
    general_combo_2_hit_rate = (general_combo_2_hits / total_reviews) * 100 if total_reviews > 0 else 0

    general_combo_3_hits = sum(item['general_prediction_review']['hits'].get('combo_3_in_3', 0) 
                               for item in processed_review_log)
    general_combo_3_hit_rate = (general_combo_3_hits / total_reviews) * 100 if total_reviews > 0 else 0

    # --- Special Prediction KPIs ---
    total_special_zodiac_hits = sum(item['special_prediction_review']['hits'].get('special_zodiacs', 0) 
                                    for item in processed_review_log)
    special_zodiac_hit_rate = (total_special_zodiac_hits / total_reviews) * 100 if total_reviews > 0 else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("复盘总期数", f"{total_reviews} 期")
    col2.metric("通用-热门号码命中率", f"{general_hot_number_hit_rate:.2f}%")
    col3.metric("通用-生肖命中率", f"{general_zodiac_hit_rate:.2f}%")
    col4.metric("通用-2中2组合命中率", f"{general_combo_2_hit_rate:.2f}%")
    col5.metric("通用-3中3组合命中率", f"{general_combo_3_hit_rate:.2f}%")
    col6.metric("特码-生肖命中率", f"{special_zodiac_hit_rate:.2f}%")

    st.subheader("详细复盘日志", divider='blue')
    for index, row in df.iterrows():
        lottery_name = "香港" if row['lottery_type'] == 'hk' else "澳门"
        with st.container(border=True):
            st.markdown(f"#### {lottery_name} - 第 **{row['period']}** 期复盘")
            
            # Actual Results
            actual_general_numbers = row.get('actual_general_numbers', [])
            actual_general_zodiacs = row.get('actual_general_zodiacs', [])
            actual_special_number = row.get('actual_special_number', 'N/A')
            actual_special_zodiac = row.get('actual_special_zodiac', 'N/A')

            actual_html = f'<div class="result-title" style="margin-bottom: 0.5rem;">开奖结果 (前6个号码)</div><div class="result-grid">'
            for num in actual_general_numbers:
                actual_html += f'<span class="number-pill">{num}</span>'
            actual_html += '</div>'
            st.markdown(actual_html, unsafe_allow_html=True)

            actual_zodiac_html = f'<div class="result-title" style="margin-bottom: 0.5rem;">实际开奖生肖 (前6个)</div><div class="result-grid">'
            for zodiac in actual_general_zodiacs:
                actual_zodiac_html += f'<span class="item-pill">{zodiac}</span>'
            actual_zodiac_html += '</div>'
            st.markdown(actual_zodiac_html, unsafe_allow_html=True)

            st.markdown(f'<div class="result-title" style="margin-bottom: 0.5rem;">实际特码 (第7个号码)</div><div class="result-grid">'
                        f'<span class="number-pill">{actual_special_number}</span>'
                        f'<span class="item-pill">{actual_special_zodiac}</span>'
                        '</div>', unsafe_allow_html=True)
            
            st.markdown("---")

            # General Prediction Review
            general_review = row.get('general_prediction_review', {})
            if general_review:
                st.markdown("##### 通用预测复盘")
                
                predicted_hot_numbers = general_review.get('predicted_hot_numbers', [])
                general_hits = general_review.get('hits', {})

                pred_html = f'<div class="result-title" style="margin-bottom: 0.5rem;">热门号码预测 ({general_hits.get("hot_numbers", 0)} 命中)</div><div class="result-grid">'
                for num in predicted_hot_numbers:
                    hit_class = "hit" if num in actual_general_numbers else "miss"
                    pred_html += f'<span class="number-pill {hit_class}">{num}</span>'
                pred_html += '</div>'
                st.markdown(pred_html, unsafe_allow_html=True)

                predicted_zodiacs = general_review.get('predicted_zodiacs', [])
                pred_zodiac_html = f'<div class="result-title" style="margin-top: 1rem; margin-bottom: 0.5rem;">热门生肖预测 ({general_hits.get("zodiacs", 0)} 命中)</div><div class="result-grid">'
                for zodiac in predicted_zodiacs:
                    hit_class = "hit" if zodiac in actual_general_zodiacs else "miss"
                    pred_zodiac_html += f'<span class="item-pill {hit_class}">{zodiac}</span>'
                pred_zodiac_html += '</div>'
                st.markdown(pred_zodiac_html, unsafe_allow_html=True)

                combo_2_hit = general_hits.get('combo_2_in_2', 0)
                st.markdown(f"""
                <div class="result-title" style="margin-top: 1rem; margin-bottom: 0.5rem;">'2中2' 组合预测</div>
                <div class="result-grid">
                    <span class="item-pill {'hit' if combo_2_hit else 'miss'}">
                        {'🎉 命中' if combo_2_hit else '💨 未命中'}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                combo_3_hit = general_hits.get('combo_3_in_3', 0)
                st.markdown(f"""
                <div class="result-title" style="margin-top: 1rem; margin-bottom: 0.5rem;">'3中3' 组合预测</div>
                <div class="result-grid">
                    <span class="item-pill {'hit' if combo_3_hit else 'miss'}">
                        {'🎉 命中' if combo_3_hit else '💨 未命中'}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("未找到通用预测复盘数据。")

            st.markdown("---")

            # Special Prediction Review
            special_review = row.get('special_prediction_review', {})
            if special_review:
                st.markdown("##### 特码预测复盘")
                
                special_zodiac_hit = special_review.get('hits', {}).get('special_zodiacs', 0)
                predicted_special_zodiacs = special_review.get('predicted_special_zodiacs', [])
                
                pred_special_zodiac_html = f'<div class="result-title" style="margin-bottom: 0.5rem;">特码生肖预测 ({special_zodiac_hit} 命中)</div><div class="result-grid">'
                for zodiac in predicted_special_zodiacs:
                    hit_class = "hit" if zodiac == actual_special_zodiac else "miss"
                    pred_special_zodiac_html += f'<span class="item-pill {hit_class}">{zodiac}</span>'
                pred_special_zodiac_html += '</div>'
                st.markdown(pred_special_zodiac_html, unsafe_allow_html=True)
            else:
                st.info("未找到特码预测复盘数据。")

            st.markdown("---")

def render_v7_prediction_history():
    st.title("🚀 V7预测历史")
    st.markdown("查看所有V7预测结果（8生肖智能覆盖系统）")
    
    # 加载所有V7预测文件
    import glob
    v7_files = sorted(glob.glob('predictions/v7_prediction_*.json'), 
                     key=os.path.getctime, reverse=True)
    
    if not v7_files:
        st.info("暂无V7预测历史。请在【执行中心】运行V7预测以生成第一条记录。")
        return
    
    st.subheader(f"共有 {len(v7_files)} 条V7预测记录", divider='blue')
    
    # 加载实际开奖数据用于对比
    data_file = 'lottery_data_2025_complete.json'
    lottery_data = load_json_data(data_file, {})
    actual_results = {int(r['period']): r for r in lottery_data.get('totalRecords', [])}
    
    # 统计准确率
    total_checked = 0
    total_hits = 0
    total_number_hits = 0  # 统计号码命中
    
    for v7_file in v7_files:
        v7_pred = load_json_data(v7_file)
        if not v7_pred:
            continue
            
        period = v7_pred.get('period')
        predicted_zodiacs = v7_pred.get('predicted_zodiacs', [])
        predicted_numbers = v7_pred.get('recommended_numbers', [])
        
        # 查找实际结果
        actual = actual_results.get(period)
        hit_status = "⏳ 待开奖"
        hit_color = "gray"
        detail_info = ""
        
        if actual and 'numberList' in actual and len(actual['numberList']) >= 7:
            actual_special = actual['numberList'][-1]
            actual_zodiac = actual_special['shengXiao']
            actual_number = int(actual_special['number'])
            actual_color = ['', '红波', '蓝波', '绿波'][actual_special.get('color', 0)]
            actual_element = actual_special.get('wuXing', 'N/A')
            
            zodiac_hit = actual_zodiac in predicted_zodiacs
            number_hit = actual_number in predicted_numbers
            
            # 获取所有开出的号码用于统计
            all_actual_numbers = [int(n['number']) for n in actual['numberList']]
            all_actual_zodiacs = [n['shengXiao'] for n in actual['numberList']]
            
            # 统计推荐号码在所有7个号码中的命中数
            numbers_hit_count = sum(1 for n in predicted_numbers if n in all_actual_numbers)
            zodiacs_hit_count = sum(1 for z in predicted_zodiacs if z in all_actual_zodiacs)
            
            total_checked += 1
            
            # 判断命中情况
            if number_hit and zodiac_hit:
                total_hits += 1
                total_number_hits += 1
                hit_status = "🎯 特码精准命中"
                hit_color = "green"
                detail_info = f"✅ 特码号码命中 | ✅ 生肖命中 | 号码覆盖: {numbers_hit_count}/12 | 生肖覆盖: {zodiacs_hit_count}/8"
            elif zodiac_hit:
                total_hits += 1
                hit_status = "✓ 生肖命中"
                hit_color = "green"
                detail_info = f"❌ 特码号码未中 | ✅ 生肖命中 | 号码覆盖: {numbers_hit_count}/12 | 生肖覆盖: {zodiacs_hit_count}/8"
            elif number_hit:
                total_number_hits += 1
                hit_status = "⚡ 号码命中"
                hit_color = "orange"
                detail_info = f"✅ 特码号码命中 | ❌ 生肖未中 | 号码覆盖: {numbers_hit_count}/12 | 生肖覆盖: {zodiacs_hit_count}/8"
            else:
                hit_status = "✗ 未中"
                hit_color = "red"
                detail_info = f"❌ 特码未命中 | 号码覆盖: {numbers_hit_count}/12 | 生肖覆盖: {zodiacs_hit_count}/8"
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"#### 期号: **{period}** ")
                st.markdown(f"**推荐8生肖:** {', '.join(predicted_zodiacs)}")
                st.markdown(f"**推荐号码:** {', '.join(map(str, predicted_numbers[:12]))}")
                st.markdown(f"**波色:** {v7_pred.get('predicted_color', 'N/A')} | "
                          f"**尾数:** {v7_pred.get('predicted_tail', 'N/A')} | "
                          f"**五行:** {v7_pred.get('predicted_element', 'N/A')}")
                
                # 显示详细命中信息
                if detail_info:
                    st.markdown(f"**复盘:** {detail_info}")
            
            with col2:
                if actual:
                    actual_special = actual['numberList'][-1]
                    actual_color = ['', '红波', '蓝波', '绿波'][actual_special.get('color', 0)]
                    actual_element = actual_special.get('wuXing', 'N/A')
                    
                    st.markdown(f"**实际特码**")
                    st.markdown(f"**{actual_special['number']}** ({actual_special['shengXiao']})")
                    st.markdown(f"{actual_color} | {actual_element}")
                    st.markdown(f":{hit_color}[{hit_status}]")
                else:
                    st.markdown(f":{hit_color}[{hit_status}]")
    
    # 显示统计
    if total_checked > 0:
        zodiac_accuracy = (total_hits / total_checked) * 100
        number_accuracy = (total_number_hits / total_checked) * 100
        st.markdown("---")
        st.subheader("📊 统计摘要", divider='blue')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("总预测期数", len(v7_files))
        col2.metric("已开奖期数", total_checked)
        col3.metric("生肖命中期数", total_hits)
        col4.metric("号码命中期数", total_number_hits)
        col5.metric("生肖准确率", f"{zodiac_accuracy:.1f}%")

def render_prediction_history():
    st.title("📜 预测历史 (V6)")
    st.markdown("在这里，您可以查看所有V6历史预测结果。")

    lottery_type_selection = st.radio(
        "选择彩票类型",
        ["澳门", "香港"],
        index=0,
        horizontal=True
    )
    
    lottery_type_key = "macau" if lottery_type_selection == "澳门" else "hk"
    
    # --- General Prediction History ---
    st.subheader(f"{lottery_type_selection} - 通用预测历史", divider='blue')
    general_history_file = f'{lottery_type_key}_prediction_history.json'
    general_prediction_history = load_json_data(general_history_file)
    
    if not general_prediction_history:
        st.info(f"未找到 {lottery_type_selection} 的通用预测历史。请先运行每日分析以生成预测。")
    else:
        for entry in general_prediction_history:
            with st.container(border=True):
                st.markdown(f"#### 期号: **{entry.get('period', 'N/A')}**")
                st.markdown(f"**热门生肖:** {', '.join(entry.get('zodiacs', []))}")
                st.markdown(f"**热门号码:** {', '.join(map(str, entry.get('numbers', [])))}")
                
                combos_2_in_2 = entry.get('combos_2_in_2', [])
                if combos_2_in_2:
                    st.markdown(f"**'2中2' 组合:** {', '.join([str(tuple(c)) for c in combos_2_in_2])}")
                
                combos_3_in_3 = entry.get('combos_3_in_3', [])
                if combos_3_in_3:
                    st.markdown(f"**'3中3' 组合:** {', '.join([str(tuple(c)) for c in combos_3_in_3])}")
                
                st.markdown("---")

    # --- Special Prediction History ---
    st.subheader(f"{lottery_type_selection} - 特码预测历史", divider='blue')
    special_history_file = f'{lottery_type_key}_special_prediction_history.json'
    special_prediction_history = load_json_data(special_history_file)

    if not special_prediction_history:
        st.info(f"未找到 {lottery_type_selection} 的特码预测历史。请先运行每日分析以生成特码预测。")
    else:
        for entry in special_prediction_history:
            with st.container(border=True):
                st.markdown(f"#### 期号: **{entry.get('period', 'N/A')}**")
                special_zodiacs = entry.get('special_zodiacs', [])
                if special_zodiacs:
                    # special_zodiacs is a list of tuples (zodiac, score), extract just zodiac
                    display_zodiacs = [z for z, score in special_zodiacs] if isinstance(special_zodiacs[0], list) else special_zodiacs
                    st.markdown(f"**特码推荐生肖:** {', '.join(display_zodiacs)}")
                st.markdown(f"**特码分析说明:** {entry.get('special_number_prediction_logic', 'N/A')}")
                st.markdown("---")

def create_execution_tab():
    st.title("⚙️ 执行中心")
    st.markdown("在这里，您可以手动触发数据获取、AI优化和报告生成。")

    # V7 快速预测区
    with st.container(border=True):
        st.subheader("🚀 V7 快速预测 (8生肖智能覆盖)")
        st.markdown("**推荐使用！** 使用优化后的V7算法快速生成下期预测。准确率：**76%**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 运行V7预测 (澳门)", use_container_width=True, type="primary"):
                with st.spinner("正在生成V7预测..."):
                    result = subprocess.run([sys.executable, "run_v7_prediction.py"], 
                                          capture_output=True, 
                                          encoding='utf-8',
                                          errors='replace')
                    output = result.stdout + "\n" + result.stderr
                    st.code(output, language='bash')
                    
                    # 加载并显示预测结果
                    try:
                        import glob
                        latest_v7_file = max(glob.glob('predictions/v7_prediction_*.json'), 
                                           key=os.path.getctime, default=None)
                        if latest_v7_file:
                            v7_result = load_json_data(latest_v7_file)
                            st.success("V7预测完成！")
                            
                            # 显示格式化结果
                            st.markdown("### 📊 预测结果")
                            st.markdown(f"**期号:** {v7_result.get('period', 'N/A')}")
                            st.markdown(f"**推荐8生肖:** {', '.join(v7_result.get('predicted_zodiacs', []))}")
                            st.markdown(f"**波色:** {v7_result.get('predicted_color', 'N/A')}")
                            st.markdown(f"**尾数:** {v7_result.get('predicted_tail', 'N/A')}")
                            st.markdown(f"**五行:** {v7_result.get('predicted_element', 'N/A')}")
                            st.markdown(f"**推荐号码:** {', '.join(map(str, v7_result.get('recommended_numbers', [])[:12]))}")
                    except Exception as e:
                        st.error(f"显示预测结果时出错: {e}")
                    
                    st.cache_data.clear()
        
        with col2:
            if st.button("📊 查看V7性能", use_container_width=True):
                with st.spinner("正在分析V7性能..."):
                    result = subprocess.run([sys.executable, "visualize_v7_performance.py"], 
                                          capture_output=True,
                                          encoding='utf-8',
                                          errors='replace')
                    output = result.stdout + "\n" + result.stderr
                    st.code(output, language='bash')
                    
                    # 加载并显示性能报告
                    try:
                        v7_perf = load_json_data('v7_performance_report.json')
                        if v7_perf:
                            st.success("性能分析完成！")
                            st.markdown("### 📈 V7性能摘要")
                            col_a, col_b, col_c = st.columns(3)
                            col_a.metric("测试期数", v7_perf.get('total_tests', 0))
                            col_b.metric("命中期数", v7_perf.get('hits', 0))
                            col_c.metric("准确率", f"{v7_perf.get('accuracy', 0):.1f}%")
                    except Exception as e:
                        st.error(f"显示性能报告时出错: {e}")
                    
                    st.success("性能分析完成！")

    with st.container(border=True):
        st.subheader("📅 日常分析 (包含复盘)")
        st.markdown("获取最新数据，复盘上一期预测，并为下一期生成新预测。")
        if st.button("🚀 运行每日分析", use_container_width=True):
            with st.spinner("正在执行每日分析..."):
                result = subprocess.run([sys.executable, "run_daily_analysis.py"], 
                                      capture_output=True,
                                      encoding='utf-8',
                                      errors='replace')
                output = result.stdout + "\n" + result.stderr
                st.code(output, language='bash')
                st.success("执行完毕！请刷新页面查看最新报告和复盘记录。")
                st.cache_data.clear()
                st.rerun()

    with st.container(border=True):
        st.subheader("🧠 AI策略优化 (V6版本)")
        st.markdown("启动遗传算法，让AI学习并演进出新的最优通用策略。**此过程非常耗时。**")
        if st.button("🧠 运行通用策略优化 (V6)", use_container_width=True):
            with st.spinner("正在运行通用策略优化，可能需要数分钟..."):
                result = subprocess.run([sys.executable, "optimizer.py"], 
                                      capture_output=True,
                                      encoding='utf-8',
                                      errors='replace')
                output = result.stdout + "\n" + result.stderr
                st.code(output, language='bash')
                st.success("通用策略优化完成！请刷新页面查看新策略和学习曲线。")
                st.cache_data.clear()
                st.rerun()
        
        st.markdown("---")
        st.markdown("启动遗传算法，让AI学习并演进出新的最优特码策略 (V6)。**此过程非常耗时。**")
        if st.button("🎯 运行特码策略优化 (V6)", use_container_width=True):
            with st.spinner("正在运行特码策略优化，可能需要数分钟..."):
                result = subprocess.run([sys.executable, "optimizer_special.py"], 
                                      capture_output=True,
                                      encoding='utf-8',
                                      errors='replace')
                output = result.stdout + "\n" + result.stderr
                st.code(output, language='bash')
                st.success("特码策略优化完成！请刷新页面查看新策略和学习曲线。")
                st.cache_data.clear()
                st.rerun()
    
    with st.container(border=True):
        st.subheader("⚡ V7策略优化 (高级)")
        st.markdown("重新优化V7算法参数（8生肖系统）。**约需5-10分钟。**")
        if st.button("🎯 运行V7特码优化", use_container_width=True):
            with st.spinner("正在运行V7优化，请耐心等待..."):
                result = subprocess.run([sys.executable, "optimizer_special_v7.py"], 
                                      capture_output=True,
                                      encoding='utf-8',
                                      errors='replace')
                output = result.stdout + "\n" + result.stderr
                st.code(output, language='bash')
                st.success("V7策略优化完成！")
                st.cache_data.clear()
                st.rerun()

# --- Main App Layout ---

with st.sidebar:
    st.markdown('<div style="font-size: 1.5rem; font-weight: 700; color: #5eead4; display: flex; align-items: center; gap: 0.75rem;"><i class="fas fa-chart-line"></i><span>智能策略平台</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "导航菜单",
        ["总览看板", "澳门分析", "香港分析", "复盘中心", "预测历史", "V7预测历史", "执行中心"],
        captions=["关键指标与学习曲线", "澳门数据深度分析", "香港数据深度分析", "历史预测准确率追踪", "V6历史预测结果", "V7历史预测结果", "运行任务与日志"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info(f"欢迎回来！\n\n今天是 {datetime.now().strftime('%Y-%m-%d')}")

if page == "总览看板":
    st.title("📊 总览看板")
    st.markdown("展示项目核心指标和AI学习过程。")
    
    st.subheader("关键指标概览", divider='blue')
    col1, col2 = st.columns(2)
    with col1:
        score = "--"
        log = load_json_data('macau_optimizer_log.json')
        if log: score = f"{log[-1]['best_fitness']:.0f}"
        st.metric("🇲🇴 澳门 AI 策略得分", score)
    with col2:
        score = "--"
        log = load_json_data('hk_optimizer_log.json')
        if log: score = f"{log[-1]['best_fitness']:.0f}"
        st.metric("🇭🇰 香港 AI 策略得分", score)

    st.subheader("香港策略学习曲线", divider='blue')
    with st.container(border=True, height=600): # Increased height to accommodate two charts
        render_learning_curve('hk')

    st.subheader("澳门策略学习曲线", divider='blue')
    with st.container(border=True, height=600): # Increased height to accommodate two charts
        render_learning_curve('macau')

elif page in ["澳门分析", "香港分析"]:
    lottery_type = 'macau' if page == "澳门分析" else 'hk'
    name = "澳门" if lottery_type == 'macau' else "香港"
    st.title(f"{'🇲🇴' if lottery_type == 'macau' else '🇭🇰'} {name}数据深度分析")
    
    render_kpis(lottery_type)
    st.markdown("---")
    render_analysis_results(lottery_type)

elif page == "复盘中心":
    render_review_center()

elif page == "预测历史":
    render_prediction_history()

elif page == "V7预测历史":
    render_v7_prediction_history()

elif page == "执行中心":
    create_execution_tab()