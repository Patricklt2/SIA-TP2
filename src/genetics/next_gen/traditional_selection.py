def traditional_selection(old_population, new_individuals):
    population_size = len(old_population)
    combined_pool = old_population + new_individuals

    sorted_pool = sorted(combined_pool, key=lambda x: x.fitness, reverse=True)
    
    return sorted_pool[:population_size]