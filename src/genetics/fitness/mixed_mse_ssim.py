from .mse import mse_fitness
from .ssim import ssim_fitness
from ..individual import Individual
from .deltaE import delta_e_fitness

def mixed_fitness_mse_ssim(
    target,
    generated,
    weight_mse=0.66,
    weight_ssim=0.15,
    weight_deltae=0.19
):
    mse_fit = mse_fitness(target, generated)
    raw_ssim_score = ssim_fitness(target, generated)
    delta_e_fit = delta_e_fitness(target, generated)

    normalized_ssim_fit = (raw_ssim_score + 1) / 2

    combined_fitness = (
        (weight_mse * mse_fit) +
        (weight_ssim * normalized_ssim_fit) +
        (weight_deltae * delta_e_fit)
    )

    return combined_fitness