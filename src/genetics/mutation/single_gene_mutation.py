import random 
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color, blend_colors
from src.genetics.polygon import Polygon

def single_gene_mutation(individual, mutation_rate):
    if random.random() >= mutation_rate:
        return

    poly = random.choice(individual.polygons)
    r = random.random()

    if r < 0.3:
        new_color = generate_random_hex_color()
        poly.color = blend_colors(poly.color, new_color, alpha=0.5)
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