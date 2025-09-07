import random
import numpy as np
from PIL import Image, ImageDraw
from .polygon import Polygon
from .utils import generate_random_hex_color

# The genome includes the features of each individual where each polygon has its own color and vertices, and the individual has a background color
# All of these features can be mutated or crossed over
# i.e. genome = [ [background_color, polygon1], [background, polygon2], ..., [background,polygonN]] 
# To mutate we can change color, vertices (though this would not be good for the basic version) or add/remove polygons
# Background color is part of each chromosome, its a global gene for the individual
# To crossover we can swap polygons between two individuals or blend colors/vertices
# 
# Each individual can render, calculate fitness, mutate and store its genome
class Individual:
    def __init__(self, width, height, n_polygons, fitness_method, mutation_method, target_img = None):
        # Image dimensions
        self.width = width
        self.height = height

        # Genetic methods
        self.target_img = target_img
        self.fitness_method = fitness_method
        self.mutation_method = mutation_method
        self.polygons = [Polygon.random(width, height, n_vertices=3, target_img=target_img) 
                          for _ in range(n_polygons)]

        self.fitness = float('inf')
        self.img = None

    def render(self):
        canvas = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))
        for poly in self.polygons:
            temp_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)

            temp_draw.polygon(poly.vertices, fill=poly.color)
            canvas = Image.alpha_composite(canvas, temp_img)
        canvas = canvas.convert("RGB")
        self.img = canvas
        return canvas

    def hex_to_rgba(self, hex_color, alpha=255):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)

    def calculate_fitness(self, reference_img):
        generated = np.array(self.render())
        target = np.array(reference_img)
        self.fitness = self.fitness_method(target, generated)
        return self.fitness

    def mutate(self, target_img, mutation_rate=0.05):   # Mutate according to method provided, this way Individuals can mutate differently if needed :)
        self.mutation_method(self, target_img, mutation_rate)

    def clone(self):
        new_individual = Individual(
            self.width,
            self.height,
            0,
            self.fitness_method,
            self.mutation_method
        )
        new_individual.polygons = [
            Polygon(vertices=poly.vertices[:], color=poly.color)
            for poly in self.polygons
        ]
        return new_individual