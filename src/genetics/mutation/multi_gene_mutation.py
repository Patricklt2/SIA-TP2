import random
import numpy as np
from ..individual import Individual
from ..utils import generate_random_hex_color, blend_colors

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

        if r < 0.3:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            current_alpha = poly.color[3]
            poly.color = (r, g, b, current_alpha)
        elif r < 0.6:
            if poly.vertices:
                vertices = np.array(poly.vertices)
                shifts = np.random.randint(-15, 16, size=vertices.shape)
                vertices += shifts
                vertices[:, 0] = np.clip(vertices[:, 0], 0, individual.width)
                vertices[:, 1] = np.clip(vertices[:, 1], 0, individual.height)
                poly.vertices = [tuple(v) for v in vertices]
        elif r < 0.9:
            rgba_list = list(poly.color)
            current_alpha = rgba_list[3]
            new_alpha_float = current_alpha / 255.0 + random.uniform(-0.3, 0.3)
            new_alpha_float = max(0.0, min(1.0, new_alpha_float))
            rgba_list[3] = int(new_alpha_float * 255)
            poly.color = tuple(rgba_list)
        else:
            swap_idx = random.randrange(n_polygons)
            polygons[idx], polygons[swap_idx] = polygons[swap_idx], polygons[idx]