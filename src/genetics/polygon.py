import random
import numpy as np
from PIL import Image, ImageDraw
from src.genetics.utils import generate_random_hex_color

class Polygon:
    def __init__(self, vertices, color):
        self.vertices = vertices
        self.color = color

    @staticmethod
    def random(width, height, n_vertices=3):
        vertices = [(random.randint(0, width), random.randint(0, height)) 
                    for _ in range(n_vertices)]
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(30, 100)  
        color = (r, g, b, a)
        return Polygon(vertices, color)
