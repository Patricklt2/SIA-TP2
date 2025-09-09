def traditional_replacement(old_population, new_individuals, population_size):
    combined = old_population + new_individuals
    sorted_combined = sorted(combined, key=lambda x: x.fitness, reverse=True)
    return sorted_combined[:population_size]