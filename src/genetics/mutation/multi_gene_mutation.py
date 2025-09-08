import random
import numpy as np
from ..individual import Individual
from ..utils import generate_random_hex_color
from PIL import Image
from ..polygon import Polygon

def multi_gene_mutation(individual: Individual, mutation_rate: float, target_img: Image):
    if random.random() >= mutation_rate:
        return

    polygons = individual.polygons
    n_polygons = len(polygons)

    if n_polygons == 0:
        individual.polygons.append(Polygon.random(individual.width, individual.height))
        return

    n_mutations = max(1, int(n_polygons * random.uniform(0.1, 0.25)))
    mutate_indices = np.random.choice(n_polygons, n_mutations, replace=False)

    # Define the mutation types and their probabilities
    # These probabilities must sum to 1.0
    mutation_types = ['vertex', 'color', 'alpha', 'swap']
    probabilities = [0.6, 0.2, 0.1, 0.1]

    for idx in mutate_indices:
        mutation_type = random.choices(mutation_types, weights=probabilities, k=1)[0]
        poly = polygons[idx]

        # Perform the chosen mutation based on the type
        if mutation_type == 'vertex':
            if poly.vertices:
                vertices = np.array(poly.vertices)
                shifts = np.random.randint(-14, 14, size=vertices.shape)
                vertices += shifts
                vertices[:, 0] = np.clip(vertices[:, 0], 0, individual.width)
                vertices[:, 1] = np.clip(vertices[:, 1], 0, individual.height)
                poly.vertices = [tuple(v) for v in vertices]

        elif mutation_type == 'color':
            if poly.vertices:
                all_x = [v[0] for v in poly.vertices]
                all_y = [v[1] for v in poly.vertices]
                min_x, max_x = min(all_x), max(all_x)
                min_y, max_y = min(all_y), max(all_y)
                
                min_x = max(0, int(min_x))
                max_x = min(individual.width - 1, int(max_x))
                min_y = max(0, int(min_y))
                max_y = min(individual.height - 1, int(max_y))

                if min_x <= max_x and min_y <= max_y:
                    x = random.randint(min_x, max_x)
                    y = random.randint(min_y, max_y)
                    new_color = target_img.getpixel((x, y))
                    if isinstance(new_color, int):
                        new_color = (new_color, new_color, new_color, poly.color[3])
                    elif len(new_color) == 3:
                        new_color = (new_color[0], new_color[1], new_color[2], poly.color[3])
                    poly.color = new_color

        elif mutation_type == 'alpha':
            rgba_list = list(poly.color)
            current_alpha = rgba_list[3]
            new_alpha_float = current_alpha / 255.0 + random.uniform(-0.3, 0.3)
            new_alpha_float = max(0.0, min(1.0, new_alpha_float))
            rgba_list[3] = int(new_alpha_float * 255)
            poly.color = tuple(rgba_list)

        elif mutation_type == 'swap':
            swap_idx = random.randrange(n_polygons)
            polygons[idx], polygons[swap_idx] = polygons[swap_idx], polygons[idx]