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
    def __init__(self, width, height, n_polygons, fitness_method, mutation_method):
        # Image dimensions
        self.width = width
        self.height = height

        # Genetic methods
        self.fitness_method = fitness_method
        self.mutation_method = mutation_method

        self.polygons = [Polygon.random(width, height) for _ in range(n_polygons)]

        self.fitness = float('inf')
        self.img = None

    def render(self):
        canvas = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(canvas, 'RGB')
        for poly in self.polygons:
            draw.polygon(poly.vertices, fill=poly.color)
        self.img = canvas
        return canvas

    def calculate_fitness(self, reference_img):
        generated = np.array(self.render())  # Process the rendered image as a numpy array
        target = np.array(reference_img)
        self.fitness = self.fitness_method(target, generated)
        return self.fitness

    def mutate(self, mutation_rate=0.05):   # Mutate according to method provided, this way Individuals can mutate differently if needed :)
        self.mutation_method(self, mutation_rate)

    def clone(self):
        new_individual = Individual(
            self.width,
            self.height,
            len(self.polygons),
            self.fitness_method,
            self.mutation_method
        )
        
        new_individual.polygons = []
        for poly in self.polygons:
            new_poly = Polygon(
                vertices=poly.vertices[:],
                color=poly.color
            )
            new_individual.polygons.append(new_poly)
        
        return new_individual