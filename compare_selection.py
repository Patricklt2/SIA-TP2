#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparacion de métodos de selección:
- Corre src.genetics.genetics para cada método de selección (3 repeticiones por defecto)
- Guarda los CSV de métricas por corrida
- Lee el *último* valor de best_fitness y elapsed_sec de cada CSV
- Calcula media y desvío (error bars) por método
- Grafica DOS barras: (1) fitness final y (2) tiempo total
- **Nuevo**: guarda la imagen final de CADA repetición como ./compare/selection/images/<metodo>_rep<i>.png

Uso típico (activar venv antes):
  python compare_selection.py --config ./configs/config.json
  python compare_selection.py --config ./configs/config.json --reps 5 --outdir ./compare/sel --save

Opciones:
  --config   Ruta al JSON base (se sobrescribe `selection`, `metrics_csv` y `output_image` por corrida)
  --reps     Repeticiones por método (default 3)
  --methods  Lista de métodos separados por coma (default: elite,tournament,roulette,universal,boltzmann,ranking)
  --outdir   Carpeta donde colocar configs temporales, CSV, imágenes y gráficos (default ./compare/selection)
  --save     Si está presente, guarda gráficos en PNG dentro de outdir además de mostrarlos
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


DEFAULT_METHODS = ["elite","tournament","roulette","universal","boltzmann","ranking"]


def read_last_values(csv_path: str) -> Tuple[float, float]:
    """Devuelve (best_fitness_final, elapsed_sec_final) del CSV."""
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(csv_path)
    last_best = None
    last_time = None
    with open(csv_path, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr, None)
        if not header:
            raise SystemExit(f"{csv_path} vacío.")
        idx = {name.strip().lower(): i for i, name in enumerate(header)}
        # nombres esperados
        bf_name = "best_fitness"
        time_name = "elapsed_sec"
        if bf_name not in idx or time_name not in idx:
            raise SystemExit(f"{csv_path} no contiene columnas '{bf_name}' y/o '{time_name}'. Columns: {list(idx.keys())}")
        for row in rdr:
            if not row:
                continue
            try:
                last_best = float(row[idx[bf_name]])
                last_time = float(row[idx[time_name]])
            except Exception:
                # saltar filas mal formateadas
                continue
    if last_best is None or last_time is None:
        raise SystemExit(f"No se pudieron leer valores finales de {csv_path}.")
    return last_best, last_time


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def write_json(path: str, data: dict) -> None:
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_once(config_path: str) -> None:
    """Ejecuta el módulo con la config dada usando el mismo intérprete (venv)."""
    cmd = [sys.executable, "-m", "src.genetics.genetics", "--config", config_path]
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"  # evita ventanas durante el benchmark
    print("[run]", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


def main():
    ap = argparse.ArgumentParser(description="Comparacion de métodos de selección (N repeticiones por método).")
    ap.add_argument("--config", required=True, help="Ruta al JSON base de configuración.")
    ap.add_argument("--reps", type=int, default=3, help="Repeticiones por método (default 3).")
    ap.add_argument("--methods", type=str, default=",".join(DEFAULT_METHODS),
                    help=f"Métodos separados por coma. Default: {','.join(DEFAULT_METHODS)}")
    ap.add_argument("--outdir", type=str, default="./compare/selection", help="Carpeta de salidas (configs/csv/images/plots).")
    ap.add_argument("--save", action="store_true", help="Guardar los gráficos en PNG dentro de outdir.")
    args = ap.parse_args()

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    ensure_dir(args.outdir)

    # subcarpetas
    cfg_dir = os.path.join(args.outdir, "configs")
    csv_dir = os.path.join(args.outdir, "csv")
    img_dir = os.path.join(args.outdir, "images")
    ensure_dir(cfg_dir); ensure_dir(csv_dir); ensure_dir(img_dir)

    # cargar config base
    with open(args.config, "r", encoding="utf-8") as f:
        base_cfg = json.load(f)

    # fuerza parámetros útiles para bench (opcional)
    base_cfg.setdefault("show_live", False)

    # estructuras para stats
    results: Dict[str, List[Tuple[float, float]]] = {m: [] for m in methods}  # método -> [(best_final, time_final), ...]

    # correr
    for method in methods:
        for rep in range(1, args.reps + 1):
            run_name = f"{method}_rep{rep}"
            # config temporal
            cfg = dict(base_cfg)
            cfg["selection"] = method
            metrics_rel = os.path.join(csv_dir, f"{run_name}.csv")
            cfg["metrics_csv"] = metrics_rel
            # NUEVO: guardar imagen final de cada repetición
            cfg["output_image"] = os.path.join(img_dir, f"{run_name}.png")

            cfg_path = os.path.join(cfg_dir, f"{run_name}.json")
            write_json(cfg_path, cfg)

            # ejecutar
            ensure_dir(os.path.dirname(metrics_rel))
            run_once(cfg_path)

            # leer resultados finales
            best_final, time_final = read_last_values(metrics_rel)
            results[method].append((best_final, time_final))
            print(f"[ok] {run_name}: best_final={best_final:.6g}  time={time_final:.3f}s  img={cfg['output_image']}")

    # --- agregar CSV resumen ---
    summary_csv = os.path.join(args.outdir, "summary_selection.csv")
    with open(summary_csv, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["method", "rep", "best_final", "time_sec"])
        for m, lst in results.items():
            for i, (bf, tt) in enumerate(lst, start=1):
                wr.writerow([m, i, f"{bf:.10g}", f"{tt:.6g}"])
    print("[saved]", summary_csv)

    # --- calcular medias y desvíos ---
    methods_sorted = list(results.keys())
    bf_means, bf_stds = [], []
    tt_means, tt_stds = [], []

    for m in methods_sorted:
        arr_bf = np.array([x[0] for x in results[m]], dtype=float)
        arr_tt = np.array([x[1] for x in results[m]], dtype=float)
        bf_means.append(float(np.nanmean(arr_bf)))
        bf_stds.append(float(np.nanstd(arr_bf, ddof=1)) if len(arr_bf) > 1 else 0.0)
        tt_means.append(float(np.nanmean(arr_tt)))
        tt_stds.append(float(np.nanstd(arr_tt, ddof=1)) if len(arr_tt) > 1 else 0.0)

    # --- gráfico 1: barras de fitness final ---
    plt.figure()
    x = np.arange(len(methods_sorted))
    plt.bar(x, bf_means, yerr=bf_stds, capsize=5)
    plt.xticks(x, methods_sorted, rotation=0)
    plt.ylabel("Fitness final (best_fitness)")
    plt.title(f"Fitness final por método (n={args.reps})")
    plt.grid(axis="y", alpha=0.3)

    if args.save:
        out1 = os.path.join(args.outdir, "bar_fitness_final.png")
        plt.savefig(out1, dpi=140, bbox_inches="tight")
        print("[saved]", out1)
    else:
        plt.show()

    # --- gráfico 2: barras de tiempo total ---
    plt.figure()
    x = np.arange(len(methods_sorted))
    plt.bar(x, tt_means, yerr=tt_stds, capsize=5)
    plt.xticks(x, methods_sorted, rotation=0)
    plt.ylabel("Tiempo total (s)")
    plt.title(f"Tiempo total por método (n={args.reps})")
    plt.grid(axis="y", alpha=0.3)

    if args.save:
        out2 = os.path.join(args.outdir, "bar_tiempo_total.png")
        plt.savefig(out2, dpi=140, bbox_inches="tight")
        print("[saved]", out2)
    else:
        plt.show()


if __name__ == "__main__":
    main()
