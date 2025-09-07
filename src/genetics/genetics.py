from .fitness.mse import mse_fitness
from .fitness.ssim import ssim_fitness
from .fitness.mixed_fitness import mixed_fitness

from .mutation.single_gene_mutation import single_gene_mutation
from .mutation.multi_gene_mutation import multi_gene_mutation
from .selection.elite import elite_selection
from .selection.torneos import tournament_selection
from .next_gen.traditional_selection import traditional_replacement
from .crossover.single_point_crossover import single_point_crossover

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

def _calculate_fitness_helper(args):
    individual, reference_img = args
    return individual.calculate_fitness(reference_img)

def main():
    target_img = Image.open("./monalisa.webp").convert("RGB")
    target_img = target_img.resize((128, 128))
    width, height = target_img.size
    target_array = np.array(target_img)

    population = Population(
        population_size=100,
        width=width,
        height=height,
        n_polygons=300,
        fitness_method=mse_fitness,
        mutation_method=multi_gene_mutation,
        selection_method=tournament_selection,
        replacement_method=traditional_replacement,
        mutation_rate=0.8,
        crossover_rate=0.7,
        elite_size=5,
        seed_store=None,
        seed_frac=0.0
    )

    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    
    initial_mutation_rate = population.mutation_rate
    max_generations = 10000

    plt.ion()
    fig, ax = plt.subplots()

    tasks = population.prepare_fitness_tasks(target_array)
    results = pool.map(_calculate_fitness_helper, tasks)
    population.update_fitness_from_results(results)

    best_image = population.best_individual.render()
    img_display = ax.imshow(best_image)

    for generation in range(1, max_generations + 1):
        current_mutation_rate = initial_mutation_rate * (1 - (generation / max_generations))
        population.mutation_rate = current_mutation_rate

        population.create_next_generation()

        tasks = population.prepare_fitness_tasks(target_array)
        results = pool.map(_calculate_fitness_helper, tasks)
        population.update_fitness_from_results(results)

        stats = population.get_statistics()
        print(f"Gen {generation}: Best fitness = {stats['best_fitness']}")

        best_image = population.best_individual.render()
        img_display.set_data(np.array(best_image))
        plt.pause(0.001)

        if stats['best_fitness'] >= 0.9:
            print("Stopping criteria met: Fitness >= 0.9")
            break

    pool.close()
    pool.join()
    plt.ioff()
    plt.show()


def _worker_process(worker_id, shared_seeds, target_array, config):
    """Worker runs a small GA loop and updates shared_seeds when it finds better tile candidates.

    This is a lightweight prototype: each worker runs its own Population for a number of local generations and
    occasionally tries to publish improved tile colors for the tiles it intersects.
    """
    print(f"Worker {worker_id} started")
    pop = Population(
        population_size=config.get('population_size', 50),
        width=target_array.shape[1],
        height=target_array.shape[0],
        n_polygons=config.get('n_polygons', 2),
        fitness_method=mse_fitness,
        mutation_method=multi_gene_mutation,
        selection_method=tournament_selection,
        replacement_method=traditional_replacement,
        mutation_rate=config.get('mutation_rate', 0.15),
        crossover_rate=config.get('crossover_rate', 0.55),
        elite_size=config.get('elite_size', 1),
        seed_store=None,
        seed_frac=0.0
    )

    local_gens = config.get('local_gens', 10)
    sample_top_k = config.get('sample_top_k', 3)
    refine_steps = config.get('color_refine_steps', 6)
    refine_mag = config.get('color_refine_mag', 12)  # max per-channel perturbation during refinement
    min_improv = config.get('min_improvement_frac', 0.02)

    for gen in range(local_gens):
        pop.create_next_generation(target_array)
        stats = pop.get_statistics()

        # sample several of the best individuals (sorted by fitness; get_statistics uses min as best)
        try:
            candidates = sorted(pop.individuals, key=lambda x: x.fitness)[:sample_top_k]
        except Exception:
            candidates = [stats.get('best_individual')]

        for ind in candidates:
            if ind is None:
                continue
            for poly in ind.polygons:
                xs = [v[0] for v in poly.vertices]
                ys = [v[1] for v in poly.vertices]
                x0, x1 = max(0, min(xs)), min(pop.width, max(xs))
                y0, y1 = max(0, min(ys)), min(pop.height, max(ys))
                if x1 <= x0 or y1 <= y0:
                    continue
                patch = target_array[y0:y1, x0:x1]
                if patch.size == 0:
                    continue

                # current polygon color -> numpy array RGB
                try:
                    c = poly.color
                    if isinstance(c, str) and c.startswith('#'):
                        r = int(c[1:3], 16)
                        g = int(c[3:5], 16)
                        b = int(c[5:7], 16)
                        base_col = np.array([r, g, b], dtype=np.float32)
                    else:
                        base_col = np.array(c[:3], dtype=np.float32)
                except Exception:
                    continue

                pixels = patch.reshape(-1, patch.shape[2])[:, :3]

                # evaluate base mse
                base_mse = float(np.mean((pixels.astype(np.float32) - base_col) ** 2))

                # local color refinement: sample small perturbations around base_col
                best_col = base_col.copy()
                best_mse = base_mse
                for _ in range(refine_steps):
                    delta = np.random.randint(-refine_mag, refine_mag + 1, size=3)
                    cand = np.clip(best_col + delta, 0, 255)
                    cand_mse = float(np.mean((pixels.astype(np.float32) - cand) ** 2))
                    if cand_mse < best_mse:
                        best_mse = cand_mse
                        best_col = cand

                # If refinement found improvement, consider publishing to shared store
                # find overlapping seed (tile) by polygon centroid
                cx = (x0 + x1) // 2
                cy = (y0 + y1) // 2
                res = find_seed_by_point(shared_seeds, cx, cy)
                if res:
                    tid, sd = res
                    cur_mse = sd.get('mse') if sd.get('mse') is not None else float('inf')
                    if best_mse < cur_mse * (1.0 - min_improv):
                        # convert best_col to hex
                        rc, gc, bc = int(best_col[0]), int(best_col[1]), int(best_col[2])
                        hex_col = '#{:02x}{:02x}{:02x}'.format(rc, gc, bc)
                        updated = update_seed_if_better(shared_seeds, tid, hex_col, best_mse, min_improvement_frac=min_improv)
                        if updated:
                            # optional: print a lightweight trace
                            print(f"Worker {worker_id} updated seed {tid}: mse {cur_mse:.2f} -> {best_mse:.2f}")

        # small sleep to yield
        time.sleep(0.01)

    print(f"Worker {worker_id} finished")


def run_with_workers(target_array, n_workers=2, tile_size=8):
    # compute seeds
    seeds = compute_tile_seeds(target_array, tile_size=tile_size)
    mgr, shared = create_shared_seed_store(seeds)

    config = {
        'population_size': 50,
        'n_polygons': 2,
        'mutation_rate': 0.15,
        'crossover_rate': 0.55,
        'elite_size': 1,
        'local_gens': 20
    }

    processes = []
    for i in range(n_workers):
        p = multiprocessing.Process(target=_worker_process, args=(i, shared, target_array, config))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    # return shared store for inspection
    return shared


if __name__ == "__main__":
    main()