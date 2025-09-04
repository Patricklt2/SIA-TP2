from skimage.metrics import structural_similarity as ssim
import numpy as np

# Esta tiene en cuenta luminancia, contraste y estructuras
def ssim_fitness(target, generated):
    if target.ndim == 3 and target.shape[2] == 3:
        ssim_total = 0
        for i in range(3):
            ssim_total += ssim(target[:, :, i], generated[:, :, i], data_range=generated.max() - generated.min())
        return ssim_total / 3
    else:
        return ssim(target, generated, data_range=generated.max() - generated.min())