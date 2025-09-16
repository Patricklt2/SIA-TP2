import os
import argparse
import json
import multiprocessing as mp
from typing import Tuple, List
import time
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

from .fitness.mse import mse_fitness
from .fitness.ssim import ssim_fitness
from .fitness.mixed_fitness import mixed_fitness
from .fitness.mixed_mse_ssim_deltae import mixed_fitness_mse_ssim_deltaE
from .fitness.deltaE import delta_e_fitness


from .mutation.single_gene_mutation import single_gene_mutation
from .mutation.multi_gene_mutation import multi_gene_mutation
from .mutation.seed_guided_mutation import make_seed_guided_mutation
from .mutation.non_uniform_mutation import non_uniform_multi_gene_mutation
from .mutation.doomsday_mutation import doomsday_mutation
from .mutation.uniform_mutation import uniform_multi_gene_mutation
from .mutation.focused_point_mutation import focused_point_mutation

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
from .crossover.artistic_crossover import artistic_crossover

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

def _tiles_for_image(width: int, height: int, tile_size: int) -> List[Tuple[int, int, int, int]]:
    boxes = []
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            x1 = min(x + tile_size, width)
            y1 = min(y + tile_size, height)
            if x1 > x and y1 > y:
                boxes.append((x, y, x1, y1))
    return boxes


# --- mapas de nombre->función (según lo implementado) ---
fitness_map = {
    "mse": mse_fitness,
    "ssim": ssim_fitness,
    "mixed": mixed_fitness,
    "mixed_mse_ssim_deltae": mixed_fitness_mse_ssim_deltaE,
    "deltaE": delta_e_fitness,
}

mutation_map = {
    "single_gene": single_gene_mutation,
    "multi_gene": multi_gene_mutation,
    "seed_guided": make_seed_guided_mutation,
    "non_uniform_multigen": non_uniform_multi_gene_mutation,
    "doomsday": doomsday_mutation,
    "uniform": uniform_multi_gene_mutation,
    "focused": focused_point_mutation
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
    "anular": annular_crossover,
    "artistic": artistic_crossover
}

def main():
    ap = argparse.ArgumentParser(description='Tile-based GA renderer (parallel-friendly).')
    ap.add_argument('--config', help='Path to JSON config (overrides CLI defaults)')
 
    args = ap.parse_args()

    # Load config JSON if provided and prefer its values
    cfg_json = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            cfg_json = json.load(f) or {}

    render_mode = cfg_json.get('render_mode')
    if render_mode is None and cfg_json.get('use_fast_render') is not None:
        render_mode = 'fast' if bool(cfg_json.get('use_fast_render')) else 'compat'
    if render_mode:
        os.environ['GEN_RENDER_MODE'] = str(render_mode)

    # Resolve inputs with config taking precedence
    image_path = cfg_json.get('image_path')
    if not image_path:
        raise SystemExit("Missing input image. Provide --image or config.image_path")

    tile_size = int(cfg_json.get('tile_size', 64))
    out_path = str(cfg_json.get('output_image', 'out/tiled_best.png'))
    # preview flags: allow either tile_preview or show_live in config
    cfg_preview = bool(cfg_json.get('tile_preview', cfg_json.get('show_live', False)))
    preview_flag = bool(cfg_preview)
    preview_interval = int(cfg_json.get('tile_preview_interval', cfg_json.get('plot_interval', 8)))
    preview_save_dir = cfg_json.get('preview_save_dir', 'out/previews')
    save_previews = bool(cfg_json.get('save_previews', True))

    img = Image.open(image_path).convert('RGB')
    W, H = img.size
    full_np = np.asarray(img)

    boxes = _tiles_for_image(W, H, tile_size)

    # Merge JSON config with CLI fallbacks
    cfg = dict(cfg_json)
    cfg.setdefault('population_size', 40)
    cfg.setdefault('polygons_per_tile', cfg.get('n_polygons', 60))
    cfg.setdefault('generations', cfg.get('max_generations', 400))
    cfg.setdefault('elite_size', 6)
    cfg.setdefault('mutation_rate', 0.10)
    cfg.setdefault('crossover_rate', 0.70)
    cfg.setdefault('stop_fitness', cfg_json.get('stop_fitness', 0.98))
    cfg.setdefault('n_vertices', cfg.get('n_vertices', 3))
    cfg.setdefault('fitness', cfg_json.get('fitness', 'mse'))
    cfg.setdefault('mutation', cfg_json.get('mutation', 'multi_gene'))
    cfg.setdefault('selection', cfg_json.get('selection', 'ranking'))
    cfg.setdefault('replacement', cfg_json.get('replacement', 'traditional'))
    cfg.setdefault('crossover', cfg_json.get('crossover', 'two_point'))

    tasks = []
    for (x0, y0, x1, y1) in boxes:
        tile_np = full_np[y0:y1, x0:x1].copy()
        tasks.append((len(tasks), x0, y0, x1, y1, tile_np, cfg))

    # Compose output incrementally
    canvas = Image.new('RGB', (W, H), (255, 255, 255))

    show_gui = bool(preview_flag)
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

        # Sequential, generation-synchronized mode with logs each generation
    print(f"Tiles: {len(tasks)} | sequential mode with per-generation preview interval {preview_interval}")
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
            fitness_method=fitness_map[cfg.get("fitness", "mse")],
            mutation_method=mutation_map[cfg.get("mutation", "multi_gene")],
            selection_method=selection_map[cfg.get("selection", "ranking")],
            replacement_method=replacement_map[cfg.get("replacement", "traditional")],
            max_gen=int(cfg.get('generations', cfg.get('max_generations', 400))),
            mutation_rate=cfg.get('mutation_rate', 0.10),
            crossover_rate=cfg.get('crossover_rate', 0.70),
            elite_size=cfg.get('elite_size', 6),
            seed_store=None,
            seed_frac=0.0,
            target_img=timg,
            crossover_method=crossover_map[cfg.get("crossover", "two_point")],
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
            # _draw_border(x0, y0, im) #debug: show tile borders

    # Log + preview gen 0
    fits = [pop.get_statistics()['best_fitness'] for (_, _, _, pop) in tile_objs]
    print(f"Gen 0: avg_best={np.mean(fits):.6f} min_best={np.min(fits):.6f}")
    if preview_flag and (0 % max(1, preview_interval) == 0):
        _compose_current()
        if show_gui and img_display is not None:
            img_display.set_data(np.asarray(canvas))
            plt.pause(0.001)
        if save_previews:
            outp0 = os.path.join(preview_save_dir, f"preview_00000.png")
            os.makedirs(preview_save_dir, exist_ok=True)
            canvas.save(outp0)

    # Step generations
    for gen in range(1, int(cfg.get('generations', 400)) + 1):
        for (_, _, tile_np, pop) in tile_objs:
            pop.create_next_generation()
            _eval_population(pop, tile_np)
        fits = [pop.get_statistics()['best_fitness'] for (_, _, _, pop) in tile_objs]
        print(f"Gen {gen}: avg_best={np.mean(fits):.6f} min_best={np.min(fits):.6f}")
        if preview_flag and (gen % max(1, preview_interval) == 0):
            _compose_current()
            if show_gui and img_display is not None:
                img_display.set_data(np.asarray(canvas))
                plt.pause(0.001)
            if save_previews:
                outpg = os.path.join(preview_save_dir, f"preview_{gen:05d}.png")
                os.makedirs(preview_save_dir, exist_ok=True)
                canvas.save(outpg)

    # Final save and optional final show
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    canvas.save(out_path)
    print(f'Saved composed image: {out_path}')
    if show_gui:
        plt.ioff()
        plt.show()


if __name__ == '__main__':
    main()
