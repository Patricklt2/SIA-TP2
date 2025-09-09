import random
import numpy as np
from PIL import Image
import copy

class Polygon:
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color

    @staticmethod
    def random(width, height, n_vertices, target_img: Image) -> 'Polygon':
        vertices = [(random.randint(0, width), random.randint(0, height)) 
                    for _ in range(n_vertices)]

        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(width, max_x)
        max_y = min(height, max_y)

        if min_x < max_x and min_y < max_y:
            patch = np.array(target_img.crop((min_x, min_y, max_x, max_y)))
            avg_color = np.mean(patch, axis=(0, 1)).astype(int)
            r, g, b = avg_color[0], avg_color[1], avg_color[2]
        else:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            r, g, b = target_img.getpixel((x, y))

        a = random.randint(30, 100) 
        color = (r, g, b, a)
        
        return Polygon(vertices, color)

    def clone(self):
        cloned_vertices = copy.deepcopy(self.vertices)
        cloned_color = copy.deepcopy(self.color)
        return Polygon(cloned_vertices, cloned_color)