import random

def uniform_crossover(parent1, parent2):
    child1 = parent1.clone()
    child2 = parent2.clone()
    crossover_probability = 0.5
    num_polygons = len(parent1.polygons)
    
    for i in range(num_polygons):
        if random.random() < crossover_probability:
            child1.polygons[i], child2.polygons[i] = child2.polygons[i], child1.polygons[i]

    return child1, child2