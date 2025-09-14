from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
import random

# Blends or swaps attributes of parent poligons to create the children
def artistic_crossover(parent1: Individual, parent2: Individual, rng=None):
    if rng is None:
        rng = random.Random()

    child1 = parent1.clone()
    child2 = parent2.clone()

    for i in range(len(parent1.polygons)):
        p1_poly = parent1.polygons[i]
        p2_poly = parent2.polygons[i]

        if rng.random() < 0.5:
            blended_vertices = []
            for v1, v2 in zip(p1_poly.vertices, p2_poly.vertices):
                avg_x = int((v1[0] + v2[0]) / 2)
                avg_y = int((v1[1] + v2[1]) / 2)
                blended_vertices.append((avg_x, avg_y))
            
            blended_color = tuple(
                int((c1 + c2) / 2) for c1, c2 in zip(p1_poly.color, p2_poly.color)
            )

            child1.polygons[i] = Polygon(blended_vertices, blended_color)
            child2.polygons[i] = Polygon(blended_vertices, blended_color)

        else:
            child1.polygons[i] = p2_poly.clone()
            child2.polygons[i] = p1_poly.clone()
            
    return child1, child2