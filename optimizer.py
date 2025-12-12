import random
import json
import backtester
import operator

# --- GENETIC ALGORITHM PARAMETERS ---
POPULATION_SIZE = 60       
N_GENERATIONS = 50         
MUTATION_RATE = 0.2        
TOURNAMENT_SIZE = 5        

# --- V6 参数空间：强化组合预测 ---
PARAMETER_SPACE = {
    'trend_lookback': (5, 30),      # 分析趋势时回溯的期数
    'hot_score': (0.0, 2.0), 
    'cold_score': (0.0, 2.0), 
    'category_trend': (0.0, 3.0),
    'combo_2_diversity': (1.0, 1.5), 
    'combo_3_color_diversity': (1.0, 1.5), 
    'combo_3_element_diversity': (1.0, 1.5),
    'co_occurrence_weight': (0.0, 6.0), # 2中2 权重 (共现)
    
    # --- V6 新增基因 ---
    'triplet_weight': (0.0, 8.0)        # 3中3 权重 (三元闭环)
}

# --- GENETIC ALGORITHM IMPLEMENTATION ---

def create_individual():
    individual = {}
    for key, (min_val, max_val) in PARAMETER_SPACE.items():
        individual[key] = random.uniform(min_val, max_val)
    return individual

def create_initial_population():
    return [create_individual() for _ in range(POPULATION_SIZE)]

def calculate_population_fitness(population, lottery_type, backtest_range):
    population_with_fitness = []
    print(f"正在评估通用种群适应度 (共 {len(population)} 个个体)...")
    for i, individual in enumerate(population):
        fitness = backtester.run_backtest(lottery_type, individual, backtest_range)
        population_with_fitness.append((individual, fitness))
    return population_with_fitness

def selection(population_with_fitness):
    tournament = random.sample(population_with_fitness, TOURNAMENT_SIZE)
    return max(tournament, key=operator.itemgetter(1))[0]

def crossover(parent1, parent2):
    child = {}
    crossover_point = random.randint(1, len(PARAMETER_SPACE) - 1)
    keys = list(PARAMETER_SPACE.keys())
    
    for i, key in enumerate(keys):
        if i < crossover_point:
            child[key] = parent1[key]
        else:
            child[key] = parent2[key]
    return child

def mutate(individual):
    for key in individual:
        if random.random() < MUTATION_RATE:
            min_val, max_val = PARAMETER_SPACE[key]
            individual[key] = random.uniform(min_val, max_val)
    return individual

def run_evolution(lottery_type, backtest_range):
    print(f"--- V6: 开始为 {lottery_type.upper()} 通用数据运行优化 ---")
    print(f"种群大小: {POPULATION_SIZE}, 进化代数: {N_GENERATIONS}, 变异率: {MUTATION_RATE}")

    population = create_initial_population()
    overall_best_individual = None
    overall_best_fitness = -1
    
    fitness_log = []

    for gen in range(N_GENERATIONS):
        print(f"\n--- 第 {gen + 1}/{N_GENERATIONS} 代通用进化 ---")
        population_with_fitness = calculate_population_fitness(population, lottery_type, backtest_range)
        current_best_individual, current_best_fitness = max(population_with_fitness, key=operator.itemgetter(1))
        
        if current_best_fitness > overall_best_fitness:
            overall_best_fitness = current_best_fitness
            overall_best_individual = current_best_individual
            print(f"发现新的全局最优策略！适应度分数: {overall_best_fitness}")

        new_population = []
        for _ in range(POPULATION_SIZE):
            parent1 = selection(population_with_fitness)
            parent2 = selection(population_with_fitness)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population
        avg_fitness = sum(fit for ind, fit in population_with_fitness) / POPULATION_SIZE
        print(f"第 {gen + 1} 代总结: 平均适应度 = {avg_fitness:.2f}, 本代最高 = {current_best_fitness:.2f}, 全局最高 = {overall_best_fitness:.2f}")
        fitness_log.append({'generation': gen + 1, 'best_fitness': current_best_fitness, 'average_fitness': avg_fitness})

    print("\n--- 通用进化完成 ---")
    if overall_best_individual:
        print(f"找到的“天选策略”获得了 {overall_best_fitness:.2f} 的最终适应度分数。")
        print("最优权重参数为:")
        for key, value in overall_best_individual.items():
            print(f"  - {key}: {value:.4f}")
        
        output_filename = f'best_strategy_{lottery_type}.json'
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(overall_best_individual, f, indent=2)
            print(f"\n最优策略已保存至: {output_filename}")
        except Exception as e:
            print(f"错误: 保存最优策略失败。 {e}")
            
        log_filename = f'{lottery_type}_optimizer_log.json'
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(fitness_log, f, indent=2)
            print(f"优化过程日志已保存至: {log_filename}")
        except Exception as e:
            print(f"错误: 保存优化日志失败。 {e}")
            
    else:
        print("未能找到任何有效策略。")

if __name__ == "__main__":
    print("将分别为香港和澳门数据优化策略...")
    run_evolution('hk', backtest_range=50)
    print("\n" + "="*50 + "\n")
    run_evolution('macau', backtest_range=50)
    print("\n所有优化任务完成。")
