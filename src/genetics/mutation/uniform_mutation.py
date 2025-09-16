from .auxiliar_mutate_one_polygon import _mutate_one_polygon
import random
from src.genetics.individual import Individual
from PIL import Image

def uniform_multi_gene_mutation(individual: Individual, mutation_rate: float, target_img: Image):
    for poly in individual.polygons:
        if random.random() < mutation_rate:
            _mutate_one_polygon(poly, individual, target_img)