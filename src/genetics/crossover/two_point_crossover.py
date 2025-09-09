import random

def two_point_crossover(parent1, parent2):
    child1 = parent1.clone()
    child2 = parent2.clone()

    size = len(parent1.polygons)
    
    if size < 2:
        return child1, child2

    points = sorted(random.sample(range(1, size), 2))
    point1, point2 = points[0], points[1]

    child1.polygons = parent1.polygons[:point1] + parent2.polygons[point1:point2] + parent1.polygons[point2:]
    child2.polygons = parent2.polygons[:point1] + parent1.polygons[point1:point2] + parent2.polygons[point2:]

    return child1, child2