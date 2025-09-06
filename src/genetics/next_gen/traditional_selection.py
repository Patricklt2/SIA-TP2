def traditional_replacement(old_population, new_individuals, elite_size=1):
    elite = sorted(old_population, key=lambda x: x.fitness, reverse=True)[:elite_size]
    return elite + new_individuals[:len(old_population) - elite_size]