import random
from .individual import Individual
from .crossover.single_point_crossover import single_point_crossover
import numpy as np

class Population:
    def __init__(self, population_size, width, height, n_polygons, fitness_method, 
                 mutation_method, selection_method, replacement_method,
                 mutation_rate=0.05, crossover_rate=0.8, elite_size=1):
        self.population_size = population_size
        self.width = width
        self.height = height
        self.n_polygons = n_polygons
        self.fitness_method = fitness_method
        self.mutation_method = mutation_method
        self.selection_method = selection_method
        self.replacement_method = replacement_method
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        self.individuals = [Individual(width, height, n_polygons, fitness_method, mutation_method) 
                           for _ in range(population_size)]
        self.generation = 0
        self.best_individual = None
        self.best_fitness = float('inf')
    
    def evaluate_population(self, reference_img):
        for individual in self.individuals:
            individual.calculate_fitness(reference_img)
        
        current_best = min(self.individuals, key=lambda x: x.fitness)
        if current_best.fitness < self.best_fitness:
            self.best_individual = current_best
            self.best_fitness = current_best.fitness
        
        return self.individuals
    
    def get_statistics(self):
        fitnesses = [ind.fitness for ind in self.individuals]
        
        return {
            'generation': self.generation,
            'population_size': len(self.individuals),
            'best_fitness': min(fitnesses),
            'worst_fitness': max(fitnesses),
            'average_fitness': sum(fitnesses) / len(fitnesses),
            'best_individual': min(self.individuals, key=lambda x: x.fitness),
            'std_deviation': np.std(fitnesses) if len(fitnesses) > 1 else 0
        }

    def create_next_generation(self, reference_img):
        self.evaluate_population(reference_img)
        
        parents = self.selection_method(self.individuals, self.population_size - self.elite_size)
        
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i+1]
                
                if random.random() < self.crossover_rate:
                    child1, child2 = single_point_crossover(parent1, parent2)  ## This has to be unhardcoded
                else:
                    child1, child2 = parent1.clone(), parent2.clone()
                
                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)
                offspring.extend([child1, child2])
        
        new_population = self.replacement_method(self.individuals, offspring, self.elite_size)
        
        self.individuals = new_population
        self.generation += 1
        
        return self.individuals