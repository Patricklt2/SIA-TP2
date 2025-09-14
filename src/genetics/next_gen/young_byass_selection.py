def young_bias_selection(old_population, new_individuals, elite_size=1):
    sorted_old_pop = sorted(old_population, key=lambda x: x.fitness, reverse=True)
    elite = sorted_old_pop[:elite_size]

    next_generation = []
    next_generation.extend(new_individuals)
    
    return elite + new_individuals[:len(old_population) - elite_size]