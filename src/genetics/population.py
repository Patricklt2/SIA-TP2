import random
from .individual import Individual
from .crossover.single_point_crossover import single_point_crossover
import numpy as np

class Population:
    def __init__(self, population_size, width, height, n_polygons, fitness_method, 
                 mutation_method, selection_method, replacement_method,
                 mutation_rate=0.05, crossover_rate=0.8, elite_size=1,
                 seed_store=None, seed_frac=0.0, crossover_method=single_point_crossover):
        self.population_size = population_size
        self.width = width
        self.height = height
        self.n_polygons = n_polygons
        self.fitness_method = fitness_method
        self.crossover_method = crossover_method
        # If a seed_store is provided, wrap the mutation_method with a seed-guided variant
        if seed_store is not None:
            try:
                from .mutation.seed_guided_mutation import make_seed_guided_mutation
                self.mutation_method = make_seed_guided_mutation(mutation_method, seed_store, adopt_prob=0.6)
            except Exception:
                self.mutation_method = mutation_method
        else:
            self.mutation_method = mutation_method
        self.selection_method = selection_method
        self.replacement_method = replacement_method
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        # Optionally create a fraction of seeded individuals from seed_store
        self.individuals = []
        n_seeded = 0
        if seed_store and seed_frac and seed_frac > 0:
            n_seeded = int(population_size * float(seed_frac))
            seeds = list(seed_store) if not isinstance(seed_store, dict) else list(seed_store.values())
            # sample seeds to create seeded individuals
            for s in random.sample(seeds, min(n_seeded, len(seeds))):
                ind = self._create_seeded_individual(s, width, height, n_polygons, fitness_method, mutation_method)
                self.individuals.append(ind)

        # fill the rest randomly
        n_random = population_size - len(self.individuals)
        self.individuals.extend([
            Individual(width, height, n_polygons, fitness_method, mutation_method)
            for _ in range(n_random)
        ])
        self.generation = 0
        self.best_individual = None
        # fitness functions return higher = better, so initialize to -inf
        self.best_fitness = float('-inf')
    
    def evaluate_population(self, reference_img):
        for individual in self.individuals:
            individual.calculate_fitness(reference_img)
        
        # fitness functions in this project return higher = better
        current_best = max(self.individuals, key=lambda x: x.fitness)
        if self.best_individual is None or current_best.fitness > self.best_fitness:
            self.best_individual = current_best
            self.best_fitness = current_best.fitness
        
        return self.individuals
    
    def get_statistics(self):
        fitnesses = [ind.fitness for ind in self.individuals]
        
        return {
            'generation': self.generation,
            'population_size': len(self.individuals),
            'best_fitness': max(fitnesses),
            'worst_fitness': min(fitnesses),
            'average_fitness': sum(fitnesses) / len(fitnesses),
            'best_individual': max(self.individuals, key=lambda x: x.fitness),
            'std_deviation': np.std(fitnesses) if len(fitnesses) > 1 else 0
        }

    def create_next_generation(self, reference_img):
        # Evaluate current population and produce the next generation
        self.evaluate_population(reference_img)

        parents = self.selection_method(self.individuals, self.population_size - self.elite_size)

        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i+1]

                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover_method(parent1, parent2)
                else:
                    child1, child2 = parent1.clone(), parent2.clone()

                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)
                offspring.extend([child1, child2])

        new_population = self.replacement_method(self.individuals, offspring, self.elite_size)

        self.individuals = new_population
        # evaluate the new population so all individuals have a computed fitness
        self.evaluate_population(reference_img)
        self.generation += 1

        return self.individuals

    def _create_seeded_individual(self, seed, width, height, n_polygons, fitness_method, mutation_method):
        """Create a simple Individual seeded from a TileSeed: one polygon covering the tile with the mean color.

        Remaining polygons (if any) are random.
        """
        ind = Individual(width, height, n_polygons, fitness_method, mutation_method)

        # convert hex color to PIL-compatible color (hex works fine)
        seeded_poly = None
        try:
            # support both object with attributes and mapping (dict) seeds
            if hasattr(seed, 'bbox'):
                x0, y0, x1, y1 = seed.bbox
                mean_color = getattr(seed, 'mean_color', None)
            elif isinstance(seed, dict):
                x0, y0, x1, y1 = seed.get('bbox')
                mean_color = seed.get('mean_color')
            else:
                # try attribute access fallback
                x0, y0, x1, y1 = seed.bbox
                mean_color = getattr(seed, 'mean_color', None)
            # create triangle covering the tile (two triangles would fully cover, but we use one triangle as a seed)
            vertices = [(x0, y0), (x1, y0), (x0, y1)]
            from .polygon import Polygon
            seeded_poly = Polygon(vertices=vertices, color=mean_color)
        except Exception:
            # fallback: just return a random individual
            return ind

        # replace first polygon with seeded polygon
        ind.polygons[0] = seeded_poly
        return ind