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
    def __init__(self, width, height, n_polygons, fitness_method, mutation_method, target_img=None, n_vertices=3):
        self.width = width
        self.height = height
        self.fitness_method = fitness_method
        self.mutation_method = mutation_method
        self.polygons = [Polygon.random(width, height, n_vertices, target_img=target_img) 
                         for _ in range(n_polygons)]

        self.fitness = float('inf')
        self.img = None

    def render(self, use_cache=True):
        if use_cache and self.img is not None:
            return self.img

        canvas = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))
        for poly in self.polygons:
            temp_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_layer)

            temp_draw.polygon(poly.vertices, fill=poly.color)
            canvas = Image.alpha_composite(canvas, temp_layer)

        canvas_rgb = canvas.convert("RGB")
        self.img = canvas_rgb
        return self.img

    def calculate_fitness(self, reference_img_array, use_cache=True):
        if use_cache and self.fitness != float('inf'):
            return self.fitness
        
        generated_img = self.render(use_cache=use_cache)
        generated_array = np.array(generated_img)
        
        self.fitness = self.fitness_method(reference_img_array, generated_array)
        return self.fitness

    def mutate(self, **kwargs):
        self.mutation_method(
            self, 
            **kwargs
        )
        
        self.img = None
        self.fitness = float('inf')

    def clone(self):
        new_individual = Individual(
            self.width,
            self.height,
            0,
            self.fitness_method,
            self.mutation_method
        )

        new_individual.polygons = [p.clone() for p in self.polygons]
        return new_individual

    def hex_to_rgba(self, hex_color, alpha=255):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)