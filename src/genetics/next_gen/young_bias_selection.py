def young_bias_selection(old_population, new_individuals):
    n_size = len(old_population)
    k_size = len(new_individuals)

    if k_size > n_size:
        sorted_new = sorted(new_individuals, key=lambda x: x.fitness, reverse=True)
        return sorted_new[:n_size]
    else:
        next_generation = new_individuals
        
        num_from_old = n_size - k_size
        if num_from_old > 0:
            sorted_old = sorted(old_population, key=lambda x: x.fitness, reverse=True)
            next_generation.extend(sorted_old[:num_from_old])
        
        return next_generation