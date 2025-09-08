import random

def two_point_crossover(parent1, parent2):
    child1 = parent1.clone()
    child2 = parent2.clone()

    size = len(parent1.polygons)
    point1 = random.randint(1, size - 1)
    point2 = random.randint(1, size - 1)
    
    if point1 > point2:
        point1, point2 = point2, point1

    child1.polygons = parent1.polygons[:point1] + parent2.polygons[point1:point2] + parent1.polygons[point2:]
    child2.polygons = parent2.polygons[:point1] + parent1.polygons[point1:point2] + parent2.polygons[point2:]
    
    return child1, child2