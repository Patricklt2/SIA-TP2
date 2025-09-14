import random

def annular_crossover(parent1, parent2, rng=None):
    if rng is None:
        rng = random.Random()

    if len(parent1.polygons) != len(parent2.polygons):
        raise ValueError("Parents must have the same chromosome length for crossover.")

    size = len(parent1.polygons)
    if size == 0:
        return parent1.clone(), parent2.clone()

    child1 = parent1.clone()
    child2 = parent2.clone()

    point = rng.randint(0, size - 1)
    length = rng.randint(1, size // 2)

    for i in range(length):
        idx = (point + i) % size
        child1.polygons[idx], child2.polygons[idx] = child2.polygons[idx], child1.polygons[idx]

    return child1, child2
