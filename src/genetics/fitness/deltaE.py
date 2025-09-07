import numpy as np
from skimage import color
from skimage.color import deltaE_ciede2000

def delta_e_fitness(target_img: np.ndarray, generated_img: np.ndarray) -> float:
    target_float = target_img.astype(np.float32) / 255.0
    generated_float = generated_img.astype(np.float32) / 255.0
    
    target_lab = color.rgb2lab(target_float)
    generated_lab = color.rgb2lab(generated_float)
    
    delta_e = deltaE_ciede2000(target_lab, generated_lab)
    
    return np.mean(delta_e)