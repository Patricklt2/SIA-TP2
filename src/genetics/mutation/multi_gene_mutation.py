import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color, blend_colors
from src.genetics.polygon import Polygon

def multi_gene_mutation(individual: Individual, mutation_rate: float):
    if random.random() >= mutation_rate:
        return

    polygons = individual.polygons
    n_polygons = len(polygons)
    if n_polygons == 0:
        individual.polygons.append(Polygon.random(individual.width, individual.height))
        return

    n_mutations = max(1, int(n_polygons * random.uniform(0.3, 0.5)))

    mutate_indices = np.random.choice(n_polygons, n_mutations, replace=False)

    for idx in mutate_indices:
        poly = polygons[idx]
        r = random.random()

        if r < 0.4:
            new_color = generate_random_hex_color()
            poly.color = blend_colors(poly.color, new_color, alpha=random.uniform(0.1, 0.3))

        elif r < 0.6 and len(poly.vertices) > 0:
            vertices = np.array(poly.vertices)
            shifts = np.random.randint(-15, 16, size=vertices.shape)
            vertices += shifts
            vertices[:, 0] = np.clip(vertices[:, 0], 0, individual.width)
            vertices[:, 1] = np.clip(vertices[:, 1], 0, individual.height)
            poly.vertices = [tuple(v) for v in vertices]

        else:
            individual.polygons.append(Polygon.random(individual.width, individual.height))
