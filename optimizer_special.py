import random
import json
import backtester
import operator

# --- GENETIC ALGORITHM PARAMETERS ---
POPULATION_SIZE = 60
N_GENERATIONS = 50
MUTATION_RATE = 0.2
TOURNAMENT_SIZE = 5

# --- PARAMETER SPACE (V5 Upgrade) ---
PARAMETER_SPACE = {
    'special_hot': (0.0, 3.0),
    'special_gap': (0.0, 3.0),
    'special_zodiac': (0.0, 5.0), # 提高生肖权重上限，响应用户"精准命中生肖"的要求
    'special_color_weight': (0.0, 5.0), 
    'special_tail_weight': (0.0, 5.0),  
    'special_cold_protect': (0.0, 5.0),
    'special_lookback': (5, 50)         # 新增：动态回顾期
}

# --- GENETIC ALGORITHM IMPLEMENTATION ---

def create_individual():
    """Creates a single individual (a strategy with random weights)."""
    individual = {}
    for key, (min_val, max_val) in PARAMETER_SPACE.items():
        individual[key] = random.uniform(min_val, max_val)
    return individual

def create_initial_population():
    """Creates the first generation of random individuals."""
    return [create_individual() for _ in range(POPULATION_SIZE)]

def calculate_population_fitness(population, lottery_type, backtest_range):
    """Calculates the fitness for each individual in the population using special backtest."""
    population_with_fitness = []
    print(f"正在评估特码种群适应度 (共 {len(population)} 个个体)...")
    for i, individual in enumerate(population):
        # individual 字典现在会自动包含 special_lookback
        fitness = backtester.run_special_backtest(lottery_type, individual, backtest_range)
        population_with_fitness.append((individual, fitness))
    return population_with_fitness

def selection(population_with_fitness):
    """Selects one individual using tournament selection."""
    tournament = random.sample(population_with_fitness, TOURNAMENT_SIZE)
    return max(tournament, key=operator.itemgetter(1))[0]

def crossover(parent1, parent2):
    """Creates a child strategy from two parents using single-point crossover."""
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
    """Applies mutation to an individual's genes."""
    for key in individual:
        if random.random() < MUTATION_RATE:
            min_val, max_val = PARAMETER_SPACE[key]
            individual[key] = random.uniform(min_val, max_val)
    return individual

def run_evolution(lottery_type, backtest_range):
    """Runs the main genetic algorithm evolution process for special numbers."""
    print(f"--- 开始为 {lottery_type.upper()} 特码数据运行遗传算法优化 ---")
    print(f"种群大小: {POPULATION_SIZE}, 进化代数: {N_GENERATIONS}, 变异率: {MUTATION_RATE}")

    population = create_initial_population()
    overall_best_individual = None
    overall_best_fitness = -float('inf')
    
    fitness_log = []

    for gen in range(N_GENERATIONS):
        print(f"\n--- 第 {gen + 1}/{N_GENERATIONS} 代特码进化 ---")
        
        population_with_fitness = calculate_population_fitness(population, lottery_type, backtest_range)
        
        current_best_individual, current_best_fitness = max(population_with_fitness, key=operator.itemgetter(1))
        
        if current_best_fitness > overall_best_fitness:
            overall_best_fitness = current_best_fitness
            overall_best_individual = current_best_individual
            print(f"发现新的全局最优特码策略！适应度分数: {overall_best_fitness}")

        new_population = []
        for _ in range(POPULATION_SIZE):
            parent1 = selection(population_with_fitness)
            parent2 = selection(population_with_fitness)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        
        population = new_population
        
        avg_fitness = sum(fit for ind, fit in population_with_fitness) / POPULATION_SIZE
        print(f"第 {gen + 1} 代特码总结: 平均适应度 = {avg_fitness:.2f}, 本代最高 = {current_best_fitness:.2f}, 全局最高 = {overall_best_fitness:.2f}")
        
        fitness_log.append({'generation': gen + 1, 'best_fitness': current_best_fitness, 'average_fitness': avg_fitness})

    print("\n--- 特码进化完成 ---")
    if overall_best_individual:
        print(f"找到的“天选特码策略”获得了 {overall_best_fitness:.2f} 的最终适应度分数。")
        print("最优权重参数为:")
        for key, value in overall_best_individual.items():
            print(f"  - {key}: {value:.4f}")
        
        output_filename = f'best_special_strategy_{lottery_type}.json' 
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(overall_best_individual, f, indent=2)
            print(f"\n最优特码策略已保存至: {output_filename}")
        except Exception as e:
            print(f"错误: 保存最优特码策略失败。 {e}")
            
        log_filename = f'{lottery_type}_special_optimizer_log.json' 
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(fitness_log, f, indent=2)
            print(f"特码优化过程日志已保存至: {log_filename}")
        except Exception as e:
            print(f"错误: 保存特码优化日志失败。 {e}")
            
    else:
        print("未能找到任何有效特码策略。")

if __name__ == "__main__":
    print("将分别为香港和澳门数据优化特码策略...")
    run_evolution('hk', backtest_range=50)
    print("\n" + "="*50 + "\n")
    run_evolution('macau', backtest_range=50)
    print("\n所有特码优化任务完成。")