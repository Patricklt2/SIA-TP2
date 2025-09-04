from skimage.metrics import structural_similarity as ssim

def ssim_fitness(target, generated):
    min_dim = min(target.shape[0], target.shape[1])
    win_size = min(7, min_dim if min_dim % 2 == 1 else min_dim - 1)

    if target.ndim == 3 and target.shape[2] == 3:
        return ssim(
            target, generated,
            data_range=generated.max() - generated.min(),
            channel_axis=-1,
            win_size=win_size
        )
    else:
        return ssim(
            target, generated,
            data_range=generated.max() - generated.min(),
            win_size=win_size
        )