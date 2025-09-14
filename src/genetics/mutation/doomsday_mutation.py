import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from PIL import Image

# Would've dinosaur ender :)
def doomsday_mutation(
    individual: Individual,
    target_img: Image,
    rng=None
):
    if rng is None:
        rng = random.Random()
    
    polygons = individual.polygons
    n_polygons = len(polygons)
    if n_polygons == 0:
        return

    num_to_mutate = int(n_polygons * rng.uniform(0.5, 0.8))
    indices_to_mutate = rng.sample(range(n_polygons), k=num_to_mutate)

    for idx in indices_to_mutate:
        if rng.random() < 0.2:
            polygons[idx] = Polygon.random(individual.width, individual.height, individual.n_vertices, target_img)
            continue

        poly = polygons[idx]
        
        new_vertices = []
        for x, y in poly.vertices:
            dx = rng.randint(-30, 30)
            dy = rng.randint(-30, 30)
            new_x = max(0, min(individual.width, x + dx))
            new_y = max(0, min(individual.height, y + dy))
            new_vertices.append((new_x, new_y))
        poly.vertices = new_vertices

        r, g, b, a = poly.color
        r_change = rng.randint(-64, 64)
        g_change = rng.randint(-64, 64)
        b_change = rng.randint(-64, 64)
        a_change = rng.randint(-64, 64)
        poly.color = (
            max(0, min(255, r + r_change)),
            max(0, min(255, g + g_change)),
            max(0, min(255, b + b_change)),
            max(0, min(255, a + a_change)),
        )

    individual.img = None
    individual.fitness = float('inf')
