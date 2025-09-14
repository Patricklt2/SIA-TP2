from .auxiliar_mutate_one_polygon import _mutate_one_polygon
import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from src.genetics.utils import generate_random_hex_color
from PIL import Image

def multi_gene_mutation(individual: Individual, mutation_rate: float, target_img: Image):
    if random.random() >= mutation_rate:
        return

    polygons = individual.polygons
    n_polygons = len(polygons)
    if n_polygons == 0:
        return

    n_mutations = max(1, int(n_polygons * random.uniform(0.1, 0.25)))
    mutate_indices = np.random.choice(n_polygons, n_mutations, replace=False)

    for idx in mutate_indices:
        if n_polygons > 1 and random.random() < 0.1:
            swap_idx = random.randrange(n_polygons)
            polygons[idx], polygons[swap_idx] = polygons[swap_idx], polygons[idx]
        else:
            _mutate_one_polygon(polygons[idx], individual, target_img)