import random
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color, blend_colors
from src.genetics.polygon import Polygon

def multi_gene_mutation(individual, mutation_rate):
    if random.random() >= mutation_rate:
        return

    n_mutations = max(1, int(0.2 * len(individual.polygons)))

    for _ in range(n_mutations):
        r = random.random()
        
        if r < 0.33 and individual.polygons:
            poly = random.choice(individual.polygons)
            poly.color = generate_random_hex_color()
            #poly.color = blend_colors(poly.color, new_color, alpha=0.3)

        elif r < 0.5:
            valid_polygons = [p for p in individual.polygons if len(p.vertices) > 0]
            if valid_polygons:
                poly = random.choice(valid_polygons)
                idx = random.randrange(len(poly.vertices))
                x, y = poly.vertices[idx]
                dx = random.randint(-5, 5)
                dy = random.randint(-5, 5)
                poly.vertices[idx] = (
                    min(max(x + dx, 0), individual.width),
                    min(max(y + dy, 0), individual.height)
                )

        else:
            individual.polygons.append(Polygon.random(individual.width, individual.height))
