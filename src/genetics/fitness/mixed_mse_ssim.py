from .mse import mse_fitness
from .ssim import ssim_fitness
import numpy as np

def mixed_fitness_mse_ssim(target: np.ndarray, generated: np.ndarray, alpha=0.5) -> float:
    mse_fit = mse_fitness(target, generated)

    ssim_fit = ssim_fitness(target, generated)

    combined_fitness = (alpha * mse_fit) + ((1 - alpha) * ssim_fit)

    return combined_fitness