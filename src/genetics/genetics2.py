from .fitness.mse import mse_fitness
from .fitness.ssim import ssim_fitness
from .fitness.mixed_fitness import mixed_fitness
from .fitness.mixed_mse_ssim import mixed_fitness_mse_ssim
from .fitness.deltaE import delta_e_fitness

from .mutation.single_gene_mutation import single_gene_mutation
from .mutation.multi_gene_mutation import multi_gene_mutation
from .mutation.seed_guided_mutation import make_seed_guided_mutation
from .mutation.non_uniform_mutation import non_uniform_multi_gene_mutation

from .selection.elite import elite_selection
from .selection.torneos import tournament_selection
from .selection.ruleta import roulette_selection
from .selection.universal import stochastic_universal_sampling
from .selection.boltzmann import boltzmann_selection
from .selection.ranking import ranking_selection

from .next_gen.traditional_selection import traditional_selection
from .next_gen.young_bias_selection import young_bias_selection

from .crossover.single_point_crossover import single_point_crossover
from .crossover.two_point_crossover import two_point_crossover
from .crossover.uniform_crossover import uniform_crossover
from .crossover.circular_crossover import annular_crossover

from .population import Population
import numpy as np
from PIL import Image, ImageDraw
import random
import os
import matplotlib.pyplot as plt
# multiprocessing seed helpers
from .preprocessing.tiling import compute_tile_seeds
from .preprocessing.shared_seed_store import create_shared_seed_store, update_seed_if_better, find_seed_by_point
import multiprocessing
import time
import argparse
import json


def _calculate_fitness_helper(args):
    individual, reference_img = args
    return individual.calculate_fitness(reference_img)


def main():
    parser = argparse.ArgumentParser(description="Run GA image approximator from JSON config.")
    parser.add_argument("--config", required=True, help="Path to JSON config with inputs & hyperparameters.")
    args = parser.parse_args()

    # ------------------ leer config ------------------
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # --- mapas de nombre->función (según lo implementado) ---
    fitness_map = {
        "mse": mse_fitness,
        "ssim": ssim_fitness,
        "mixed": mixed_fitness,
        "mixed_mse_ssim": mixed_fitness_mse_ssim,
        "deltaE": delta_e_fitness,
    }
    mutation_map = {
        "single_gene": single_gene_mutation,
        "multi_gene": multi_gene_mutation,
        "seed_guided": make_seed_guided_mutation,
        "non_uniform_multigen": non_uniform_multi_gene_mutation
    }
    selection_map = {
        "elite": elite_selection,
        "tournament": tournament_selection,
        "roulette": roulette_selection,
        "universal": stochastic_universal_sampling,
        "boltzmann": boltzmann_selection,
        "ranking": ranking_selection,

    }
    replacement_map = {
        "traditional": traditional_selection,
        "young_bias": young_bias_selection
    }
    crossover_map = {
        "single_point": single_point_crossover,
        "two_point": two_point_crossover,
        "uniform": uniform_crossover,
        "anular": annular_crossover
    }

    # ------------------ inputs obligatorios ------------------
    img_path = cfg.get("image_path")
    if not img_path:
        raise SystemExit("Falta 'image_path' en el JSON.")
    if not os.path.exists(img_path):
        raise SystemExit(f"No se encontró la imagen en: {img_path}")

    target_img = Image.open(img_path).convert("RGB")
    width, height = target_img.size
    target_array = np.array(target_img)

    n_polygons = int(cfg.get("n_polygons", 100))
    n_vertices = int(cfg.get("n_vertices", 3))

    # ------------------ hiperparámetros ------------------
    pop_size = int(cfg.get("population_size", 100))
    mutation_rate = float(cfg.get("mutation_rate", 0.1))
    crossover_rate = float(cfg.get("crossover_rate", 0.7))
    elite_size = int(cfg.get("elite_size", 7))
    max_generations = int(cfg.get("max_generations", 10000))
    stop_fitness = float(cfg.get("stop_fitness", 0.9))

    # anti-estancamiento
    stagnation_threshold = int(cfg.get("stagnation_threshold", 20))
    original_mutation_rate = float(cfg.get("original_mutation_rate", mutation_rate))
    increased_mutation_rate = float(cfg.get("increased_mutation_rate", mutation_rate * 4.0))

    # operadores (por nombre)
    fitness_name = cfg.get("fitness", "mse")
    mutation_name = cfg.get("mutation", "multi_gene")
    selection_name = cfg.get("selection", "tournament")
    replacement_name = cfg.get("replacement", "traditional")
    crossover_name = cfg.get("crossover", "two_point")

    fitness_fn = fitness_map.get(fitness_name)
    mutation_fn = mutation_map.get(mutation_name)
    selection_fn = selection_map.get(selection_name)
    replacement_fn = replacement_map.get(replacement_name)
    crossover_fn = crossover_map.get(crossover_name)

    if fitness_fn is None:
        raise SystemExit(f"fitness '{fitness_name}' no disponible")
    if mutation_fn is None:
        raise SystemExit(f"mutation '{mutation_name}' no disponible")
    if selection_fn is None:
        raise SystemExit(f"selection '{selection_name}' no disponible")
    if replacement_fn is None:
        raise SystemExit(f"replacement '{replacement_name}' no disponible")
    if crossover_fn is None:
        raise SystemExit(f"crossover '{crossover_name}' no disponible")

    # ------------------ población inicial ------------------
    population = Population(
        population_size=pop_size,
        width=width,
        height=height,
        n_polygons=n_polygons,
        n_vertices=n_vertices,
        fitness_method=fitness_fn,
        mutation_method=mutation_fn,
        selection_method=selection_fn,
        replacement_method=replacement_fn,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elite_size=elite_size,
        seed_store=None,
        seed_frac=0.0,
        target_img=target_img,
        crossover_method=crossover_fn,
        max_gen=max_generations
    )

    # ------------------ evaluación inicial (paralelo) ------------------
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)

    tasks = population.prepare_fitness_tasks(target_array)
    results = pool.map(_calculate_fitness_helper, tasks)
    population.update_fitness_from_results(results)

    # ------------------ plot en vivo ------------------
    plt.ion()
    fig, ax = plt.subplots()
    best_image = population.best_individual.render()
    img_display = ax.imshow(best_image)
    ax.set_title("Best individual")

    stagnation_counter = 0
    best_fitness_last_gen = 0.0

    # ------------------ loop evolutivo ------------------
    for generation in range(1, max_generations + 1):
        population.create_next_generation()

        tasks = population.prepare_fitness_tasks(target_array)
        results = pool.map(_calculate_fitness_helper, tasks)
        population.update_fitness_from_results(results)

        stats = population.get_statistics()
        current_best_fitness = stats['best_fitness']
        print(f"Gen {generation}: Best fitness = {current_best_fitness:.6f}")

        # anti-estancamiento
        if current_best_fitness <= best_fitness_last_gen:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
            population.mutation_rate = original_mutation_rate

        if stagnation_counter >= stagnation_threshold:
            print(f"Stagnation detected. Increasing mutation rate to {increased_mutation_rate}")
            population.mutation_rate = increased_mutation_rate
            stagnation_counter = 0

        best_fitness_last_gen = current_best_fitness

        # actualizar preview
        best_image = population.best_individual.render()
        img_display.set_data(np.array(best_image))
        plt.pause(0.001)

        # criterio de corte
        if current_best_fitness >= stop_fitness:
            print(f"Stopping criteria met: Fitness >= {stop_fitness}")
            break

    pool.close()
    pool.join()
    plt.ioff()

    # ------------------ guardar salida ------------------
    output_image = cfg.get("output_image")
    if output_image:
        population.best_individual.render().save(output_image)
        print(f"Guardado: {output_image}")

    # mostrar figura si se desea
    if bool(cfg.get("show_plot", True)):
        plt.show()


if __name__ == "__main__":
    main()
