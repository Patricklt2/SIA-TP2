import random 
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color, blend_colors
from src.genetics.polygon import Polygon

def single_gene_mutation(individual, mutation_rate, target_img):
    if random.random() >= mutation_rate:
        return

    poly = random.choice(individual.polygons)
    r = random.random()

    if r < 0.3:
        x = random.randint(0, individual.width - 1)
        y = random.randint(0, individual.height - 1)
        new_color = target_img.getpixel((x, y))
        
        alpha = poly.color[3]
        poly.color = (new_color[0], new_color[1], new_color[2], alpha)
    elif r < 0.6:
        valid_vertices = [v for v in poly.vertices]
        if valid_vertices:
            idx = random.randrange(len(valid_vertices))
            x, y = valid_vertices[idx]
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            poly.vertices[idx] = (
                min(max(x + dx, 0), individual.width),
                min(max(y + dy, 0), individual.height)
            )
    else:
        current_alpha = poly.color[3] if isinstance(poly.color, tuple) else poly.alpha
        new_alpha = current_alpha + random.uniform(-0.1, 0.1)
        new_alpha = max(0.0, min(1.0, new_alpha))
        
        if isinstance(poly.color, tuple):
            poly.color = (poly.color[0], poly.color[1], poly.color[2], new_alpha)
        else:
            poly.alpha = new_alpha