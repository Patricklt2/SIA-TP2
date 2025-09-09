from .fitness.mse import mse_fitness
from .fitness.ssim import ssim_fitness
from .fitness.mixed_fitness import mixed_fitness
from .fitness.mixed_mse_ssim import mixed_fitness_mse_ssim
from .mutation.single_gene_mutation import single_gene_mutation
from .mutation.multi_gene_mutation import multi_gene_mutation
from .selection.elite import elite_selection
from .selection.torneos import tournament_selection
from .next_gen.traditional_selection import traditional_replacement
from .crossover.single_point_crossover import single_point_crossover
from .crossover.two_point_crossover import two_point_crossover
from .crossover.uniform_crossover import uniform_crossover

from .population import Population
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
# multiprocessing seed helpers
import multiprocessing

def _calculate_fitness_helper(args):
    individual, reference_img = args
    return individual.calculate_fitness(reference_img)

def main():
    target_img = Image.open("./banderas.jpg").convert("RGB")
    target_array = np.array(target_img)

    population = Population(
        population_size=20,
        n_polygons=30,
        fitness_method=mse_fitness,
        mutation_method=multi_gene_mutation,
        selection_method=tournament_selection,
        replacement_method=traditional_replacement,
        mutation_rate=0.1,
        crossover_rate=0.7,
        elite_size=2,
        target_img=target_img,
        crossover_method=two_point_crossover
    )

    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    
    initial_mutation_rate = population.mutation_rate
    max_generations = 10000

    plt.ion()
    fig, ax = plt.subplots()

    tasks = population.prepare_fitness_tasks(target_array)
    results = pool.map(_calculate_fitness_helper, tasks)
    population.update_fitness_from_results(results)

    best_image = population.best_individual.render()
    img_display = ax.imshow(best_image)

    stagnation_counter = 0
    stagnation_threshold = 20
    original_mutation_rate = 0.1
    increased_mutation_rate = 0.2
    best_fitness_last_gen = 0.0
    

    
    for generation in range(1, max_generations + 1):
        population.create_next_generation()
        
        tasks = population.prepare_fitness_tasks(target_array)
        results = pool.map(_calculate_fitness_helper, tasks)
        population.update_fitness_from_results(results)

        stats = population.get_statistics()
        current_best_fitness = stats['best_fitness']
        print(f"Gen {generation}: Best fitness = {current_best_fitness}")
        
        if current_best_fitness <= best_fitness_last_gen:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
            population.mutation_rate = original_mutation_rate
            
        if stagnation_counter >= stagnation_threshold:
            print(f"Stagnation detected. Increasing mutation rate to {increased_mutation_rate}")
            population.mutation_rate = increased_mutation_rate
            stagnation_counter = 0 
            
        best_fitness_last_gen = current_best_fitness

        best_image = population.best_individual.render()
        img_display.set_data(np.array(best_image))
        plt.pause(0.001)

        if current_best_fitness >= 0.9:
            print("Stopping criteria met: Fitness >= 0.9")
            break

    pool.close()
    pool.join()
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main()