import random

def generate_random_hex_color():
    random_int = random.randint(0, 0xFFFFFF)
    hex_color = '#{:06x}'.format(random_int)
    return hex_color

def blend_colors(c1, c2):
    r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
    r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    return f'#{r:02x}{g:02x}{b:02x}'