#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparador general: varía *una* categoría (fitness/mutation/selection/replacement/crossover),
corre N repeticiones por valor y:
  - guarda CSV por corrida
  - guarda la imagen final por corrida
  - genera barras (media ± desvío) de fitness final y tiempo total
  - escribe un CSV resumen

Ejemplos:
  # variar selección (default) con 5 reps y guardar gráficos
  python compare_vary.py --config ./configs/config.json --vary selection --reps 5 --save

  # variar crossover con una lista específica
  python compare_vary.py --config ./configs/config.json --vary crossover \
    --values single_point,two_point,uniform,anular,artistic --reps 3 --save

  # variar fitness (ojo: 'ssim' requiere scikit-image)
  python compare_vary.py --config ./configs/config.json --vary fitness --reps 3 --save
"""
import argparse
import csv
import json
import os
import sys
import subprocess
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Valores por defecto por categoría (coinciden con tu JSON)
DEFAULTS = {
    "fitness":   ["mse", "ssim", "mixed", "mixed_mse_ssim", "deltaE"],
    "mutation":  ["single_gene", "multi_gene", "seed_guided", "non_uniform_multigen", "doomsday", "uniform", "focused"],
    "selection": ["elite","tournament","roulette","universal","boltzmann","ranking"],
    "replacement": ["traditional","young_bias"],
    "crossover": ["single_point","two_point","uniform","anular","artistic"],
}

DEPENDENCY_HINTS = {
    "ssim": ("scikit-image", "La métrica 'ssim' requiere scikit-image (python -m pip install scikit-image)."),
    "focused": ("shapely", "La mutación 'focused' requiere shapely (python -m pip install shapely)."),
}

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def write_json(path: str, data: dict) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_last_values(csv_path: str) -> Tuple[float, float]:
    """Devuelve (best_fitness_final, elapsed_sec_final) del CSV."""
    last_best = None
    last_time = None
    with open(csv_path, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr, None)
        if not header:
            raise SystemExit(f"{csv_path} vacío.")
        idx = {name.strip().lower(): i for i, name in enumerate(header)}
        bf_name = "best_fitness"; time_name = "elapsed_sec"
        if bf_name not in idx or time_name not in idx:
            raise SystemExit(f"{csv_path} no contiene '{bf_name}'/'{time_name}'. Columns: {list(idx.keys())}")
        for row in rdr:
            if not row:
                continue
            try:
                last_best = float(row[idx[bf_name]])
                last_time = float(row[idx[time_name]])
            except Exception:
                continue
    if last_best is None or last_time is None:
        raise SystemExit(f"No se pudieron leer valores finales de {csv_path}.")
    return last_best, last_time

def preflight_dependencies(values: List[str]) -> None:
    # Avisos útiles antes de correr
    for v in values:
        if v in DEPENDENCY_HINTS:
            pkg, msg = DEPENDENCY_HINTS[v]
            try:
                __import__(pkg.replace("-", "_"))
            except Exception:
                print(f"[AVISO] {msg}", file=sys.stderr)

def run_once(config_path: str) -> None:
    """Ejecuta el GA con la config dada usando este intérprete (venv)."""
    cmd = [sys.executable, "-m", "src.genetics.genetics", "--config", config_path]
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    print("[run]", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

def main():
    ap = argparse.ArgumentParser(description="Benchmark general variando una categoría de operador.")
    ap.add_argument("--config", required=True, help="Ruta al JSON base.")
    ap.add_argument("--vary", choices=["fitness","mutation","selection","replacement","crossover"],
                    default="selection", help="Qué categoría variar (default: selection).")
    ap.add_argument("--values", type=str, default=None,
                    help="Lista separada por comas de valores a probar. Si no se da, usa defaults por categoría.")
    ap.add_argument("--reps", type=int, default=3, help="Repeticiones por valor (default 3).")
    ap.add_argument("--outdir", type=str, default=None,
                    help="Carpeta de salidas (configs/csv/images/plots). Default: ./compare/<vary>")
    ap.add_argument("--save", action="store_true", help="Guardar los gráficos en PNG dentro de outdir.")
    args = ap.parse_args()

    vary = args.vary
    values = [v.strip() for v in (args.values.split(",") if args.values else DEFAULTS[vary]) if v.strip()]
    outdir = args.outdir or os.path.join("./compare", vary)

    # subcarpetas
    cfg_dir = os.path.join(outdir, "configs")
    csv_dir = os.path.join(outdir, "csv")
    img_dir = os.path.join(outdir, "images")
    ensure_dir(cfg_dir); ensure_dir(csv_dir); ensure_dir(img_dir)

    # cargar config base
    with open(args.config, "r", encoding="utf-8") as f:
        base_cfg = json.load(f)


    render_mode = base_cfg.get("render_mode", None)
    if not render_mode:
        ufr = base_cfg.get("use_fast_render", None)
        if isinstance(ufr, bool):
            render_mode = "fast" if ufr else "compat"

    if render_mode:
        os.environ["GEN_RENDER_MODE"] = render_mode
        print(f"[env] GEN_RENDER_MODE={render_mode}")
    else:
        # opcional: limpiar por si quedó seteada de antes
        os.environ.pop("GEN_RENDER_MODE", None)
        print("[env] GEN_RENDER_MODE no seteada (usa default)")

    base_cfg.setdefault("show_live", False)

    # preflight deps
    preflight_dependencies(values)

    # stats
    results: Dict[str, List[Tuple[float, float]]] = {v: [] for v in values}

    for val in values:
        for rep in range(1, args.reps + 1):
            run_name = f"{val}_rep{rep}"
            cfg = dict(base_cfg)
            cfg[vary] = val                     # setear la categoría a variar
            cfg["metrics_csv"] = os.path.join(csv_dir, f"{run_name}.csv")
            cfg["output_image"] = os.path.join(img_dir, f"{run_name}.png")

            cfg_path = os.path.join(cfg_dir, f"{run_name}.json")
            write_json(cfg_path, cfg)

            # correr
            try:
                run_once(cfg_path)
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Run failed for {run_name}: {e}", file=sys.stderr)
                continue

            # leer finales
            best_final, time_final = read_last_values(cfg["metrics_csv"])
            results[val].append((best_final, time_final))
            print(f"[ok] {vary}={val} rep={rep}: best_final={best_final:.6g} time={time_final:.3f}s img={cfg['output_image']}")

    # CSV resumen
    summary_csv = os.path.join(outdir, f"summary_{vary}.csv")
    with open(summary_csv, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow([vary, "rep", "best_final", "time_sec"])
        for v in values:
            for i, (bf, tt) in enumerate(results[v], start=1):
                wr.writerow([v, i, f"{bf:.10g}", f"{tt:.6g}"])
    print("[saved]", summary_csv)

    # medias/desvíos
    vals_sorted = list(results.keys())
    bf_means, bf_stds = [], []
    tt_means, tt_stds = [], []
    for v in vals_sorted:
        arr_b = np.array([x[0] for x in results[v]], dtype=float)
        arr_t = np.array([x[1] for x in results[v]], dtype=float)
        bf_means.append(float(np.nanmean(arr_b)) if arr_b.size else np.nan)
        bf_stds.append(float(np.nanstd(arr_b, ddof=1)) if arr_b.size > 1 else 0.0)
        tt_means.append(float(np.nanmean(arr_t)) if arr_t.size else np.nan)
        tt_stds.append(float(np.nanstd(arr_t, ddof=1)) if arr_t.size > 1 else 0.0)

    # gráfico 1: fitness final
    plt.figure()
    x = np.arange(len(vals_sorted))
    plt.bar(x, bf_means, yerr=bf_stds, capsize=5)
    plt.xticks(x, vals_sorted, rotation=0)
    plt.ylabel("Fitness final (best_fitness)")
    plt.title(f"Fitness final por {vary} (n={args.reps})")
    plt.grid(axis="y", alpha=0.3)
    if args.save:
        out1 = os.path.join(outdir, f"bar_fitness_final_{vary}.png")
        plt.savefig(out1, dpi=140, bbox_inches="tight")
        print("[saved]", out1)
    else:
        plt.show()

    # gráfico 2: tiempo total
    plt.figure()
    x = np.arange(len(vals_sorted))
    plt.bar(x, tt_means, yerr=tt_stds, capsize=5)
    plt.xticks(x, vals_sorted, rotation=0)
    plt.ylabel("Tiempo total (s)")
    plt.title(f"Tiempo total por {vary} (n={args.reps})")
    plt.grid(axis="y", alpha=0.3)
    if args.save:
        out2 = os.path.join(outdir, f"bar_tiempo_total_{vary}.png")
        plt.savefig(out2, dpi=140, bbox_inches="tight")
        print("[saved]", out2)
    else:
        plt.show()

if __name__ == "__main__":
    main()
