import random
import numpy as np
from src.genetics.individual import Individual
from src.genetics.polygon import Polygon
from PIL import Image, ImageChops
from shapely.geometry import Point, Polygon as ShapelyPolygon
from .auxiliar_mutate_one_polygon import _mutate_one_polygon

def _find_polygon_at_point(polygons: list, point: tuple) -> Polygon | None:
    p = Point(point)
    for poly in reversed(polygons):
        if not poly.vertices:
            continue
        shapely_poly = ShapelyPolygon(poly.vertices)
        if shapely_poly.contains(p):
            return poly
    return None

def focused_point_mutation(individual: Individual, mutation_rate: float, target_img: Image):
    if random.random() >= mutation_rate:
        return

    rendered_img = individual.render()

    target_np = np.asarray(target_img).astype(np.int32)
    rendered_np = np.asarray(rendered_img).astype(np.int32)
    
    error_map = np.sum((target_np - rendered_np)**2, axis=2)
    
    worst_point_coords = np.unravel_index(np.argmax(error_map), error_map.shape)
    worst_point_xy = (worst_point_coords[1], worst_point_coords[0])

    poly_to_mutate = _find_polygon_at_point(individual.polygons, worst_point_xy)
    
    if poly_to_mutate:
        _mutate_one_polygon(poly_to_mutate, individual, target_img)
    elif individual.polygons:
        _mutate_one_polygon(random.choice(individual.polygons), individual, target_img)