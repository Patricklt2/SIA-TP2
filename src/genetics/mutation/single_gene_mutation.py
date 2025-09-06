import random 
from src.genetics.individual import Individual
from src.genetics.utils import generate_random_hex_color
from src.genetics.polygon import Polygon

# This will only mutate one gene at a time, be it background color, polygon color or polygon vertex
# It reffers to the first gene mutation method described on the ppt
def single_gene_mutation(individual, mutation_rate):
    if random.random() < mutation_rate:
        r = random.random()
        
        if r < 0.10:
            individual.background = generate_random_hex_color()
        elif r < 0.40:
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
        elif r < 0.90:
            individual.polygons.append(Polygon.random(individual.width, individual.height))
        else:
            individual.polygons.pop(random.randrange(len(individual.polygons)))