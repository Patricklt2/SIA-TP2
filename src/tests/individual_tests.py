
from src.genetics.individual import Individual
from src.genetics.fitness.mse import mse_fitness 
from src.genetics.fitness.ssim import ssim_fitness 

if "__main__":
   individual = Individual(mse_fitness, 100, 100) 
   individual.to_image()

   individual2 = Individual(mse_fitness, 100, 100)
   individual2.to_image()
   individual.calculate_fitness(individual2.img_array)

   print(individual.fitness)

   individual3 = Individual(ssim_fitness, 100, 100) 
   individual3.to_image()

   individual4 = Individual(ssim_fitness, 100, 100)
   individual4.to_image()

   individual3.calculate_fitness(individual4.img_array)
   print(individual3.fitness)