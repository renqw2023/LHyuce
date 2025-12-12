import random
import json
import backtester_v7
import operator

# --- GENETIC ALGORITHM PARAMETERS ---
POPULATION_SIZE = 80       # 增加种群大小以提高搜索空间
N_GENERATIONS = 60         # 增加进化代数
MUTATION_RATE = 0.2
TOURNAMENT_SIZE = 6

# --- V7 参数空间：8生肖优化 ---
PARAMETER_SPACE = {
    'special_hot': (0.0, 5.0),              # 热度权重
    'special_gap': (0.0, 5.0),              # 遗漏权重
    'special_zodiac': (0.0, 10.0),          # 生肖权重（提升上限）
    'special_color_weight': (0.0, 6.0),     # 波色权重
    'special_tail_weight': (0.0, 6.0),      # 尾数权重
    'special_cold_protect': (0.0, 8.0),     # 防守权重（提升）
    'special_lookback': (5, 100),           # 动态回顾期（扩大范围）
    
    # V7 新增基因
    'special_resonance': (1.0, 4.0),        # 共振系数
    'special_cycle_weight': (0.0, 5.0),     # 周期性权重
    'special_element_weight': (0.0, 5.0),   # 五行权重
    'special_balance_weight': (0.0, 4.0),   # 平衡性权重
    'special_diversity_bonus': (0.0, 3.0)   # 多样性奖励
}

def create_individual():
    """创建一个包含随机权重的个体"""
    individual = {}
    for key, (min_val, max_val) in PARAMETER_SPACE.items():
        individual[key] = random.uniform(min_val, max_val)
    return individual

def create_initial_population():
    """创建初始种群"""
    return [create_individual() for _ in range(POPULATION_SIZE)]

def calculate_population_fitness(population, lottery_type, backtest_range):
    """计算种群中每个个体的适应度"""
    population_with_fitness = []
    print(f"正在评估V7特码种群适应度 (共 {len(population)} 个个体)...")
    for i, individual in enumerate(population):
        if (i + 1) % 10 == 0:
            print(f"  进度: {i + 1}/{len(population)}")
        fitness = backtester_v7.run_special_backtest_v7(lottery_type, individual, backtest_range)
        population_with_fitness.append((individual, fitness))
    return population_with_fitness

def selection(population_with_fitness):
    """锦标赛选择法"""
    tournament = random.sample(population_with_fitness, TOURNAMENT_SIZE)
    return max(tournament, key=operator.itemgetter(1))[0]

def crossover(parent1, parent2):
    """单点交叉"""
    child = {}
    keys = list(PARAMETER_SPACE.keys())
    if len(keys) > 1:
        crossover_point = random.randint(1, len(keys) - 1)
    else: 
        crossover_point = 1
    
    for i, key in enumerate(keys):
        if i < crossover_point:
            child[key] = parent1[key]
        else:
            child[key] = parent2[key]
    return child

def mutate(individual):
    """基因变异"""
    for key in individual:
        if random.random() < MUTATION_RATE:
            min_val, max_val = PARAMETER_SPACE[key]
            individual[key] = random.uniform(min_val, max_val)
    return individual

def run_evolution(lottery_type, backtest_range):
    """运行V7特码策略的遗传算法优化"""
    print(f"--- V7: 开始为 {lottery_type.upper()} 特码数据运行8生肖优化 ---")
    print(f"种群大小: {POPULATION_SIZE}, 进化代数: {N_GENERATIONS}, 变异率: {MUTATION_RATE}")
    print(f"目标: 8生肖覆盖，理论准确率67%+，实际目标70%+")

    population = create_initial_population()
    overall_best_individual = None
    overall_best_fitness = -float('inf')
    
    fitness_log = []

    for gen in range(N_GENERATIONS):
        print(f"\n--- 第 {gen + 1}/{N_GENERATIONS} 代V7特码进化 ---")
        
        population_with_fitness = calculate_population_fitness(population, lottery_type, backtest_range)
        
        current_best_individual, current_best_fitness = max(population_with_fitness, key=operator.itemgetter(1))
        
        if current_best_fitness > overall_best_fitness:
            overall_best_fitness = current_best_fitness
            overall_best_individual = current_best_individual
            print(f"★ 发现新的全局最优V7特码策略！适应度分数: {overall_best_fitness}")

        new_population = []
        for _ in range(POPULATION_SIZE):
            parent1 = selection(population_with_fitness)
            parent2 = selection(population_with_fitness)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population
        
        avg_fitness = sum(fit for ind, fit in population_with_fitness) / POPULATION_SIZE
        print(f"第 {gen + 1} 代总结: 平均={avg_fitness:.2f}, 本代最高={current_best_fitness:.2f}, 全局最高={overall_best_fitness:.2f}")
        
        fitness_log.append({
            'generation': gen + 1, 
            'best_fitness': current_best_fitness, 
            'average_fitness': avg_fitness,
            'global_best': overall_best_fitness
        })

    print("\n" + "="*60)
    print("V7特码进化完成")
    print("="*60)
    
    if overall_best_individual:
        print(f"找到的天选V7特码策略获得了 {overall_best_fitness:.2f} 的最终适应度分数。")
        print("\n最优权重参数为:")
        for key, value in overall_best_individual.items():
            print(f"  - {key}: {value:.4f}")
        
        output_filename = f'best_special_strategy_{lottery_type}_v7.json' 
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(overall_best_individual, f, indent=2)
            print(f"\n[OK] 最优V7特码策略已保存至: {output_filename}")
        except Exception as e:
            print(f"错误: 保存失败 {e}")
            
        log_filename = f'{lottery_type}_special_optimizer_log_v7.json' 
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(fitness_log, f, indent=2)
            print(f"[OK] V7优化日志已保存至: {log_filename}")
        except Exception as e:
            print(f"错误: 保存日志失败 {e}")
            
    else:
        print("未能找到任何有效V7特码策略。")

if __name__ == "__main__":
    print("="*60)
    print("V7 特码优化器 - 8生肖智能覆盖")
    print("="*60)
    print("将分别为香港和澳门数据优化V7特码策略...")
    print("\n正在优化澳门数据...")
    run_evolution('macau', backtest_range=80)
    print("\n" + "="*60 + "\n")
    print("正在优化香港数据...")
    run_evolution('hk', backtest_range=80)
    print("\n所有V7特码优化任务完成。")
