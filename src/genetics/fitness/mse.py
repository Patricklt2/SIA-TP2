import numpy as np

# Solo tiene en cuenta la diferencia pixel a pixel
def mse_fitness(target, generated):
    error = np.mean((target.astype(np.float32) - generated.astype(np.float32)) ** 2)
    return 1 / (1 + error) 