import numpy as np
from skimage.metrics import structural_similarity as ssim

def mixed_fitness(target, generated, alpha=0.6):
    if len(target.shape) == 3:
        target_gray = np.mean(target, axis=2)
        generated_gray = np.mean(generated, axis=2)
    else:
        target_gray = target
        generated_gray = generated

    mse_error = np.mean((target.astype(np.float32) - generated.astype(np.float32)) ** 2)
    mse_score = 1 / (1 + mse_error)

    ssim_score = ssim(target_gray, generated_gray, data_range=generated_gray.max() - generated_gray.min())

    return alpha * mse_score + (1 - alpha) * ssim_score