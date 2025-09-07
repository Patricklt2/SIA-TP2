import random

def generate_random_hex_color():
    random_int = random.randint(0, 0xFFFFFF)
    hex_color = '#{:06x}'.format(random_int)
    return hex_color

def blend_colors(c1, c2, alpha=0.5):
    r = int(int(c1[1:3], 16)*(1-alpha) + int(c2[1:3], 16)*alpha)
    g = int(int(c1[3:5], 16)*(1-alpha) + int(c2[3:5], 16)*alpha)
    b = int(int(c1[5:7], 16)*(1-alpha) + int(c2[5:7], 16)*alpha)
    return f"#{r:02x}{g:02x}{b:02x}"

def smart_color_mutation(individual, target_img, mutation_rate=0.05):
    for poly in individual.polygons:
        if random.random() < mutation_rate:
            x = random.randint(0, individual.width - 1)
            y = random.randint(0, individual.height - 1)
            new_color = target_img.getpixel((x, y))
            poly.color = (new_color[0], new_color[1], new_color[2], poly.color[3])

    return individual