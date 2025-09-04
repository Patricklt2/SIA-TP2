import random
from PIL import Image, ImageDraw
import numpy as np

# Voy a querer pasarle 1. la img, 2. la funcion de fitness, 3. la mutacion y 4. la seleccion
class Individual:
    def __init__(self, fitness_method, l, w):
        self.length = l
        self.width = w
        self.fitness_method = fitness_method
        self.fitness = float('inf')
        self.img = None
        self.img_array = None

        self.create_random_image()

    @staticmethod
    def generate_random_hex_color():
        random_int = random.randint(0, 0xFFFFFF)
        hex_color = '#{:06x}'.format(random_int)
        return hex_color

    def calculate_fitness(self, reference_img):
        target = np.array(reference_img)
        generated = np.array(self.img)
        self.fitness = self.fitness_method(target, generated)

    def create_random_image(self):
        canvas = Image.new("RGB", (self.width, self.length), self.generate_random_hex_color())
        img = ImageDraw.Draw(canvas)

        region = (self.length + self.width)//8

        ITERATIONS = 10
        POLIGON_VERTEXES = 3 # triangles at first, but this could become variable

        for i in range(ITERATIONS):
            # Select a random subregion in the canvas
            region_x = random.randint(0, self.length) 
            region_y = random.randint(0, self.width)

            # Select 3 random points in the subregion
            xy = []
            for j in range(POLIGON_VERTEXES):
                xy.append((random.randint(region_x - region, region_x + region),
                           random.randint(region_y - region, region_y + region)))
        
            img.polygon(xy, fill=self.generate_random_hex_color())

        self.img = canvas
        self.img_array = np.array(canvas)
    

    def to_image(self):
        i = Image.fromarray(self.img_array)
        i.show()

