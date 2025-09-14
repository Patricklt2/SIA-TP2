from .auxiliar_mutate_one_polygon import _mutate_one_polygon
import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from src.genetics.utils import generate_random_hex_color
from PIL import Image

def single_gene_mutation(individual: Individual, mutation_rate: float, target_img: Image):
    if random.random() >= mutation_rate:
        return
        
    if not individual.polygons:
        return
        
    poly_to_mutate = random.choice(individual.polygons)
    _mutate_one_polygon(poly_to_mutate, individual, target_img)