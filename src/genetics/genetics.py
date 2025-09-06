from .fitness.mse import mse_fitness
from .fitness.ssim import ssim_fitness
from .fitness.mixed_fitness import mixed_fitness

from .mutation.single_gene_mutation import single_gene_mutation
from .mutation.multi_gene_mutation import multi_gene_mutation
from .selection.elite import elite_selection
from .next_gen.traditional_selection import traditional_replacement
from .crossover.single_point_crossover import single_point_crossover
from .population import Population
import numpy as np
from PIL import Image, ImageDraw
import random

def main():

    """target_img = Image.open("./monalisa.webp").convert("RGB")
    target_img = target_img.resize((128, 128))
    width, height = target_img.size
    target_array = np.array(target_img)"""

    
    width, height = 64, 64
    target_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(target_img)
    draw.polygon([(32, 10), (10, 50), (54, 50)], fill="red")
    target_array = np.array(target_img)
    

    population = Population(
        population_size=30,
        width=width,
        height=height,
        n_polygons=2,
        fitness_method=mse_fitness,
        mutation_method=single_gene_mutation,
        selection_method=elite_selection,
        replacement_method=traditional_replacement,
        mutation_rate=0.15,
        crossover_rate=0.55,
        elite_size=2
    )
    
    for generation in range(20000):
        population.create_next_generation(target_array)
        stats = population.get_statistics()
        print(f"Gen {generation}: Best fitness = {stats['best_fitness']}")
            
    
    best_individual = population.best_individual
    best_image = best_individual.render()
    best_image.show()
    target_img.show()

if __name__ == "__main__":
    main()