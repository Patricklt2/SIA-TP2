import random
from ..utils import blend_colors

def single_point_crossover(parent1, parent2):
    child1 = parent1.clone()
    child2 = parent2.clone()
    
    min_len = min(len(parent1.polygons), len(parent2.polygons))
    if min_len < 2:
        return child1, child2
    
    crossover_point = random.randint(1, min_len - 1)

    child1.polygons = parent1.polygons[:crossover_point] + parent2.polygons[crossover_point:]
    child2.polygons = parent2.polygons[:crossover_point] + parent1.polygons[crossover_point:]
    
    return child1, child2