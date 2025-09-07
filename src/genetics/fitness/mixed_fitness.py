import numpy as np
from skimage.metrics import structural_similarity as ssim
from .ssim import ssim_fitness
from .deltaE import delta_e_fitness

def mixed_fitness(target, generated, alpha=0.5):
    ssim_score = ssim_fitness(target, generated)
    delta_e_score = 1.0 - (delta_e_fitness(target, generated)) 
    
    return (alpha * ssim_score) + ((1 - alpha) * delta_e_score)