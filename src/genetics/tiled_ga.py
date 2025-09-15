import os
import argparse
import multiprocessing as mp
from typing import Tuple, List

import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

from .population import Population
from .fitness.mse import mse_fitness
from .mutation.multi_gene_mutation import multi_gene_mutation
from .selection.ranking import ranking_selection
try:
    from .next_gen.traditional_selection import traditional_selection
except Exception:
    # Fallback for older naming
    from .next_gen.traditional_selection import traditional_replacement as traditional_selection
from .crossover.two_point_crossover import two_point_crossover


def _eval_population(pop: Population, target_np: np.ndarray) -> None:
    tasks = pop.prepare_fitness_tasks(target_np)
    # sequential evaluation avoids nested multiprocessing issues
    results = [ind.calculate_fitness(target_np) for ind, _ in tasks]
    pop.update_fitness_from_results(results)


def _run_tile_worker(args) -> Tuple[int, int, Image.Image]:
    (tile_id, x0, y0, x1, y1, tile_np, cfg) = args

    h, w = tile_np.shape[:2]
    target_img = Image.fromarray(tile_np)

    pop = Population(
        population_size=cfg.get('population_size', 40),
        width=w,
        height=h,
        n_polygons=cfg.get('polygons_per_tile', 60),
        fitness_method=mse_fitness,
        mutation_method=multi_gene_mutation,
        selection_method=ranking_selection,
        replacement_method=traditional_selection,
        max_gen=int(cfg.get('generations', 400)),
        mutation_rate=cfg.get('mutation_rate', 0.10),
        crossover_rate=cfg.get('crossover_rate', 0.70),
        elite_size=cfg.get('elite_size', 6),
        seed_store=None,
        seed_frac=0.0,
        target_img=target_img,
        crossover_method=two_point_crossover,
        n_vertices=cfg.get('n_vertices', 3)
    )

    _eval_population(pop, tile_np)

    max_gens = int(cfg.get('generations', 400))
    stop_fit = float(cfg.get('stop_fitness', 0.90))

    for _ in range(max_gens):
        pop.create_next_generation()
        _eval_population(pop, tile_np)
        if pop.best_individual and pop.best_individual.fitness >= stop_fit:
            break

    best_img = pop.best_individual.render()
    return (x0, y0, best_img)


def _tiles_for_image(width: int, height: int, tile_size: int) -> List[Tuple[int, int, int, int]]:
    boxes = []
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            x1 = min(x + tile_size, width)
            y1 = min(y + tile_size, height)
            if x1 > x and y1 > y:
                boxes.append((x, y, x1, y1))
    return boxes


def main():
    ap = argparse.ArgumentParser(description='Tile-based GA renderer (parallel-friendly).')
    ap.add_argument('--image', required=True, help='Path to input image')
    ap.add_argument('--tile', type=int, default=64, help='Tile size (pixels)')
    ap.add_argument('--out', default='out/tiled_best.png', help='Output path for composed image')
    ap.add_argument('--processes', type=int, default=0, help='Parallel processes (0 => sequential)')
    ap.add_argument('--polys-per-tile', type=int, default=60, help='Polygons per tile')
    ap.add_argument('--vertx', type=int, default=3, help='Vertices per poligon')
    ap.add_argument('--pop', type=int, default=40, help='Population per tile')
    ap.add_argument('--gens', type=int, default=400, help='Generations per tile')
    ap.add_argument('--elite', type=int, default=6, help='Elite size per tile')
    ap.add_argument('--mut', type=float, default=0.10, help='Mutation rate')
    ap.add_argument('--cross', type=float, default=0.70, help='Crossover rate')
    ap.add_argument('--preview', action='store_true', help='Show live composite while tiles finish')
    ap.add_argument('--preview-interval', type=int, default=8, help='Update preview every N tiles completed')
    ap.add_argument('--preview-save-dir', default='out/previews', help='If GUI not available, save previews here')
    args = ap.parse_args()

    img = Image.open(args.image).convert('RGB')
    W, H = img.size
    full_np = np.asarray(img)

    boxes = _tiles_for_image(W, H, args.tile)

    cfg = {
        'population_size': args.pop,
        'polygons_per_tile': args.polys_per_tile,
        'generations': args.gens,
        'elite_size': args.elite,
        'mutation_rate': args.mut,
        'crossover_rate': args.cross,
        'stop_fitness': 0.98,
        'n_vertices': args.vertx
    }

    tasks = []
    for (x0, y0, x1, y1) in boxes:
        tile_np = full_np[y0:y1, x0:x1].copy()
        tasks.append((len(tasks), x0, y0, x1, y1, tile_np, cfg))

    # Compose output incrementally
    canvas = Image.new('RGB', (W, H), (255, 255, 255))

    # Mirror genetics.py: always attempt to show an interactive window when preview is requested.
    show_gui = bool(args.preview)
    img_display = None
    if show_gui:
        plt.ion()
        fig, ax = plt.subplots()
        img_display = ax.imshow(canvas)
        ax.set_title('Tiled composite (in progress)')
        try:
            plt.show(block=False)
        except Exception:
            pass

    # def _draw_border(x0, y0, im: Image.Image):
    #     try:
    #         dr = ImageDraw.Draw(canvas)
    #         w, h = im.size
    #         dr.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=(255, 0, 0), width=1)
    #     except Exception:
    #         pass

    # Two execution modes:
    # 1) Parallel/processes > 1: evolve tiles independently; preview on completion of tiles
    # 2) Sequential (default): step all tiles generation-by-generation; preview every N generations
    if args.processes and args.processes > 1:
        completed = 0
        def _handle_result(res):
            nonlocal completed, img_display
            x0, y0, best_img = res
            canvas.paste(best_img, (x0, y0))
            # _draw_border(x0, y0, best_img)
            completed += 1
            if args.preview and (completed % max(1, args.preview_interval) == 0):
                if show_gui and img_display is not None:
                    img_display.set_data(np.asarray(canvas))
                    plt.pause(0.001)
                # also save a snapshot for debugging
                out_path = os.path.join(args.preview_save_dir, f"preview_{completed:05d}.png")
                os.makedirs(args.preview_save_dir, exist_ok=True)
                canvas.save(out_path)

        print(f"Tiles: {len(tasks)} | processes: {args.processes}")
        with mp.Pool(processes=args.processes) as pool:
            for res in pool.imap_unordered(_run_tile_worker, tasks):
                _handle_result(res)
    else:
        # Sequential, generation-synchronized mode with logs each generation
        print(f"Tiles: {len(tasks)} | sequential mode with per-generation preview interval {args.preview_interval}")
        # Build a population per tile
        tile_objs = []
        for (_, x0, y0, x1, y1, tile_np, _) in tasks:
            h, w = tile_np.shape[:2]
            timg = Image.fromarray(tile_np)
            pop = Population(
                population_size=cfg.get('population_size', 40),
                width=w,
                height=h,
                n_polygons=cfg.get('polygons_per_tile', cfg.get('n_polygons', 60)),
                fitness_method=mse_fitness,
                mutation_method=multi_gene_mutation,
                selection_method=ranking_selection,
                replacement_method=traditional_selection,
                max_gen=int(cfg.get('generations', cfg.get('max_generations', args.gens))),
                mutation_rate=cfg.get('mutation_rate', 0.10),
                crossover_rate=cfg.get('crossover_rate', 0.70),
                elite_size=cfg.get('elite_size', 6),
                seed_store=None,
                seed_frac=0.0,
                target_img=timg,
                crossover_method=two_point_crossover,
                n_vertices=cfg.get('n_vertices', 3)
            )

            tile_objs.append((x0, y0, tile_np, pop))

        # Initial eval
        for (_, _, tile_np, pop) in tile_objs:
            _eval_population(pop, tile_np)

        def _compose_current():
            for (x0, y0, _, pop) in tile_objs:
                im = pop.best_individual.render()
                canvas.paste(im, (x0, y0))
                # _draw_border(x0, y0, im)

        # Log + preview gen 0
        fits = [pop.get_statistics()['best_fitness'] for (_, _, _, pop) in tile_objs]
        print(f"Gen 0: avg_best={np.mean(fits):.6f} min_best={np.min(fits):.6f}")
        if args.preview and (0 % max(1, args.preview_interval) == 0):
            _compose_current()
            if show_gui and img_display is not None:
                img_display.set_data(np.asarray(canvas))
                plt.pause(0.001)
            out_path = os.path.join(args.preview_save_dir, f"preview_00000.png")
            os.makedirs(args.preview_save_dir, exist_ok=True)
            canvas.save(out_path)

        # Step generations
        for gen in range(1, args.gens + 1):
            for (_, _, tile_np, pop) in tile_objs:
                pop.create_next_generation()
                _eval_population(pop, tile_np)
            fits = [pop.get_statistics()['best_fitness'] for (_, _, _, pop) in tile_objs]
            print(f"Gen {gen}: avg_best={np.mean(fits):.6f} min_best={np.min(fits):.6f}")
            if args.preview and (gen % max(1, args.preview_interval) == 0):
                _compose_current()
                if show_gui and img_display is not None:
                    img_display.set_data(np.asarray(canvas))
                    plt.pause(0.001)
                out_path = os.path.join(args.preview_save_dir, f"preview_{gen:05d}.png")
                os.makedirs(args.preview_save_dir, exist_ok=True)
                canvas.save(out_path)

    # Final save and optional final show
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    canvas.save(args.out)
    print(f'Saved composed image: {args.out}')
    if show_gui:
        plt.ioff()
        plt.show()


if __name__ == '__main__':
    main()
