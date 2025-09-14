import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from src.genetics.utils import generate_random_rgba_color
from PIL import Image

def _mutate_one_polygon(poly: Polygon, individual: Individual, target_img: Image):
    mutation_types = ['vertex', 'image_color', 'alpha', 'random_color']
    probabilities = [0.5, 0.23, 0.2, 0.07]
    mutation_type = random.choices(mutation_types, weights=probabilities, k=1)[0]

    if mutation_type == 'vertex' and poly.vertices:
        vertex_idx = random.randrange(len(poly.vertices))
        x, y = poly.vertices[vertex_idx]
        dx, dy = random.randint(-10, 10), random.randint(-10, 10)
        new_x = max(0, min(individual.width, x + dx))
        new_y = max(0, min(individual.height, y + dy))
        poly.vertices[vertex_idx] = (new_x, new_y)

    elif mutation_type == 'image_color' and poly.vertices:
        all_x = [v[0] for v in poly.vertices]
        all_y = [v[1] for v in poly.vertices]
        min_x, max_x = int(max(0, min(all_x))), int(min(individual.width - 1, max(all_x)))
        min_y, max_y = int(max(0, min(all_y))), int(min(individual.height - 1, max(all_y)))
        if min_x <= max_x and min_y <= max_y:
            x, y = random.randint(min_x, max_x), random.randint(min_y, max_y)
            new_color = target_img.getpixel((x, y))
            alpha = poly.color[3]
            poly.color = (new_color[0], new_color[1], new_color[2], alpha)

    elif mutation_type == 'alpha':
        rgba_list = list(poly.color)
        new_alpha_float = (rgba_list[3] / 255.0) + random.uniform(-0.3, 0.3)
        rgba_list[3] = int(max(0.0, min(1.0, new_alpha_float)) * 255)
        poly.color = tuple(rgba_list)

    elif mutation_type == 'random_color':
        random_rgb = generate_random_rgba_color(poly.color[3])
        poly.color = (random_rgb[0], random_rgb[1], random_rgb[2], poly.color[3])