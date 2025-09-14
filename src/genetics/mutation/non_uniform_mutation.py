import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from src.genetics.utils import generate_random_rgba_color
from PIL import Image

def non_uniform_multi_gene_mutation(
    individual: Individual,
    mutation_rate: float,
    target_img: Image,
    current_generation: int,
    max_generations: int,
    decay_factor: float = 2.0,
    rng=None
):
    if rng is None:
        rng = random.Random()

    if rng.random() >= mutation_rate:
        return

    polygons = individual.polygons
    n_polygons = len(polygons)
    if n_polygons == 0:
        return

    progress = current_generation / max_generations
    scale = (1.0 - progress) ** decay_factor

    n_mutations = max(1, int(n_polygons * rng.uniform(0.1, 0.25)))
    mutate_indices = rng.sample(range(n_polygons), k=n_mutations)

    for idx in mutate_indices:
        poly = polygons[idx]

        mutation_types = ['vertex', 'image_color', 'alpha', 'random_color', 'swap']
        probabilities = [0.50, 0.20, 0.15, 0.05, 0.10]
        mutation_type = rng.choices(mutation_types, weights=probabilities, k=1)[0]

        if mutation_type == 'vertex' and poly.vertices:
            vertex_idx = rng.randrange(len(poly.vertices))
            x, y = poly.vertices[vertex_idx]
            
            max_shift = int(1 + 14 * scale)
            dx = rng.randint(-max_shift, max_shift)
            dy = rng.randint(-max_shift, max_shift)

            new_x = max(0, min(individual.width, x + dx))
            new_y = max(0, min(individual.height, y + dy))
            poly.vertices[vertex_idx] = (new_x, new_y)

        elif mutation_type == 'image_color' and poly.vertices:
            all_x = [v[0] for v in poly.vertices]
            all_y = [v[1] for v in poly.vertices]
            min_x, max_x = int(max(0, min(all_x))), int(min(individual.width - 1, max(all_x)))
            min_y, max_y = int(max(0, min(all_y))), int(min(individual.height - 1, max(all_y)))
            if min_x <= max_x and min_y <= max_y:
                px, py = rng.randint(min_x, max_x), rng.randint(min_y, max_y)
                pixel = target_img.getpixel((px, py))
                alpha = poly.color[3]
                poly.color = (pixel[0], pixel[1], pixel[2], alpha)

        elif mutation_type == 'alpha':
            rgba_list = list(poly.color)
            
            change = rng.uniform(-0.3, 0.3) * scale
            
            new_alpha_float = (rgba_list[3] / 255.0) + change
            rgba_list[3] = int(max(0.0, min(1.0, new_alpha_float)) * 255)
            poly.color = tuple(rgba_list)

        elif mutation_type == 'random_color':
            poly.color = generate_random_rgba_color()

        elif mutation_type == 'swap' and n_polygons > 1:
            swap_idx = rng.randrange(n_polygons)
            polygons[idx], polygons[swap_idx] = polygons[swap_idx], polygons[idx]