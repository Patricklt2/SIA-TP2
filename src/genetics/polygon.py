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
        color = generate_random_hex_color()
        return Polygon(vertices, color)
