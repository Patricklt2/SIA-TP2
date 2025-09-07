import random
import numpy as np
from PIL import Image, ImageDraw
from src.genetics.utils import generate_random_hex_color

class Polygon:
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color

    @staticmethod
    def random(width, height, n_vertices, target_img: Image) -> 'Polygon':
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        r, g, b = target_img.getpixel((x, y))

        a = random.randint(30, 100) 
        color = (r, g, b, a)
        
        vertices = [(random.randint(0, width), random.randint(0, height)) 
                     for _ in range(n_vertices)]
        
        return Polygon(vertices, color)