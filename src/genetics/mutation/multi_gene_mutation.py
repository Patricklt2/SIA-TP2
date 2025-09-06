import random
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color
from src.genetics.polygon import Polygon

def multi_gene_mutation(individual, mutation_rate):
    if random.random() < mutation_rate:
        n_mutations = max(1, int(0.2 * len(individual.polygons)))  

        for _ in range(n_mutations):
            r = random.random()
            if r < 0.10:
                individual.background = generate_random_hex_color()
            
            elif r < 0.40:
                if individual.polygons:
                    poly = random.choice(individual.polygons)
                    poly.color = generate_random_hex_color()
            
            elif r < 0.60:
                valid_polygons = [p for p in individual.polygons if len(p.vertices) > 0]
                if valid_polygons:
                    poly = random.choice(valid_polygons)
                    idx = random.randrange(len(poly.vertices))
                    poly.vertices[idx] = (
                        random.randint(0, individual.width),
                        random.randint(0, individual.height)
                    )
            else:
                if random.random() < 0.5 and len(individual.polygons) < max_polygons:
                    individual.polygons.append(Polygon.random(individual.width, individual.height))
                elif len(individual.polygons) > min_polygons:
                    individual.polygons.pop(random.randrange(len(individual.polygons)))
