import random

def uniform_crossover(parent1, parent2):
    child1 = parent1.clone()
    child2 = parent2.clone()

    num_polygons = len(parent1.polygons)
    
    for i in range(num_polygons):
        if random.random() < 0.5:
            child1.polygons[i] = parent1.polygons[i].clone()
            child2.polygons[i] = parent2.polygons[i].clone()
        else:
            child1.polygons[i] = parent2.polygons[i].clone()
            child2.polygons[i] = parent1.polygons[i].clone()
            
    return child1, child2