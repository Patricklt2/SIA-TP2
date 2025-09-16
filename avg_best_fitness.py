#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Promedia best_fitness por generación **separado por método** (p.ej., selection)
y dibuja **todas las curvas en un mismo gráfico** (una línea por método).
Opcionalmente exporta un CSV agregado con method,generation,mean,std,n.

Asume archivos tipo: ./compare/selection/csv/<metodo>_rep<i>.csv
pero también puede leer el nombre del método desde la columna 'selection' si existe.

Uso típico:
  python avg_best_by_method.py \
    --csvdir ./compare/selection/csv \
    --outplot ./compare/selection/mean_best_by_method.png \
    --outcsv  ./compare/selection/mean_best_by_method.csv

Opcionales:
  --pattern "*.csv"            # glob para elegir archivos
  --labelcol selection         # columna que identifica el método (default: selection)
  --shade                      # dibuja banda ±std por método

Notas:
- Promedia solo con las corridas que tienen cada generación (no rellena faltantes).
- Búsqueda de columnas case-insensitive ('generation', 'best_fitness', y labelcol).
- Si no encuentra la columna de método, intenta inferirlo del nombre del archivo:
  '<metodo>_repX.csv' -> metodo; si no matchea, usa el basename sin extensión.
"""
import argparse
import csv
import glob
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

# ------------------- helpers -------------------

def _load_series(csv_path: str, labelcol: str) -> Tuple[str, np.ndarray, np.ndarray]:
    """Devuelve (label, generations, best_fitness) para un CSV."""
    with open(csv_path, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr, None)
        if not header:
            raise SystemExit(f"{csv_path} vacío.")
        idx = {h.strip().lower(): i for i, h in enumerate(header)}
        # columnas requeridas
        if "best_fitness" not in idx:
            raise SystemExit(f"{csv_path} no tiene 'best_fitness'. Columnas: {list(idx.keys())}")
        gen_idx = idx.get("generation", None)
        bf_idx  = idx["best_fitness"]
        # label (método)
        label = None
        if labelcol and (labelcol.lower() in idx):
            # leer de la primera fila válida
            for row in rdr:
                if not row:
                    continue
                label = row[idx[labelcol.lower()]].strip()
                break
            # rebobinar lector para volver a iterar
            f.seek(0)
            rdr = csv.reader(f); next(rdr, None)
        if not label:
            # inferir del nombre archivo: <metodo>_repX.csv
            base = os.path.basename(csv_path)
            m = re.match(r"^([A-Za-z0-9\-]+)_rep\d+\.csv$", base)
            label = m.group(1) if m else os.path.splitext(base)[0]

        gens, bests = [], []
        for i, row in enumerate(rdr):
            if not row:
                continue
            try:
                bf = float(row[bf_idx])
            except Exception:
                continue
            if gen_idx is not None:
                try:
                    g = float(row[gen_idx])
                except Exception:
                    g = float(i)
            else:
                g = float(i)
            gens.append(g); bests.append(bf)

        if not gens:
            raise SystemExit(f"Sin datos en {csv_path}.")
        return label, np.asarray(gens, dtype=float), np.asarray(bests, dtype=float)

# ------------------- main -------------------

def main():
    ap = argparse.ArgumentParser(description="Promedia best_fitness por generación agrupado por método, y grafica todas las curvas.")
    ap.add_argument("--csvdir", default="./compare/selection/csv", help="Carpeta con CSVs.")
    ap.add_argument("--pattern", default="*.csv", help="Patrón glob para CSVs (default *.csv).")
    ap.add_argument("--labelcol", default="selection", help="Columna que identifica el método (default: selection).")
    ap.add_argument("--outplot", default=None, help="Ruta para guardar el gráfico. Si no se indica, muestra ventana.")
    ap.add_argument("--outcsv",  default=None, help="Ruta para guardar CSV agregado (method,generation,mean,std,n).")
    ap.add_argument("--dpi", type=int, default=140, help="DPI al guardar figura.")
    ap.add_argument("--title", default="Mean best_fitness por método vs Generations", help="Título del gráfico.")
    ap.add_argument("--shade", action="store_true", help="Dibujar banda ±std por método.")
    args = ap.parse_args()

    pattern = os.path.join(args.csvdir, args.pattern)
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"No se encontraron CSVs con patrón: {pattern}")

    # buckets[method][generation] = list of best_fitness
    buckets: Dict[str, Dict[float, List[float]]] = defaultdict(lambda: defaultdict(list))
    file_count_for_method: Dict[str, int] = defaultdict(int)

    for fp in files:
        try:
            label, g, b = _load_series(fp, args.labelcol)
        except SystemExit as e:
            print(f"[WARN] {e}")
            continue
        file_count_for_method[label] += 1
        for gen, bf in zip(g, b):
            buckets[label][gen].append(bf)

    if not buckets:
        raise SystemExit("No se pudo leer ningún CSV válido.")

    # preparar salida CSV si se requiere
    if args.outcsv:
        os.makedirs(os.path.dirname(os.path.abspath(args.outcsv)), exist_ok=True)
        out_rows = []
        for method, gen_map in buckets.items():
            gens_sorted = sorted(gen_map.keys(), key=float)
            for gen in gens_sorted:
                arr = np.asarray(gen_map[gen], dtype=float)
                mean = float(np.nanmean(arr))
                std  = float(np.nanstd(arr, ddof=1)) if arr.size > 1 else 0.0
                n    = int(arr.size)
                out_rows.append((method, gen, mean, std, n))
        # ordenar por method, luego generación
        out_rows.sort(key=lambda x: (x[0], float(x[1])))
        with open(args.outcsv, "w", encoding="utf-8", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["method", "generation", "mean_best_fitness", "std_best_fitness", "n_runs"])
            for r in out_rows:
                wr.writerow([r[0], f"{r[1]:.6g}", f"{r[2]:.10g}", f"{r[3]:.10g}", r[4]])
        print(f"[saved] {args.outcsv}")

    # plot
    if args.outplot:
        import matplotlib
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.figure()

    # Para cada método, trazar su media (y opcionalmente banda)
    for method, gen_map in sorted(buckets.items()):
        gens_sorted = np.asarray(sorted(gen_map.keys(), key=float), dtype=float)
        vals = [np.asarray(gen_map[g], dtype=float) for g in gens_sorted]
        means = np.array([float(np.nanmean(a)) for a in vals], dtype=float)
        stds  = np.array([float(np.nanstd(a, ddof=1)) if a.size > 1 else 0.0 for a in vals], dtype=float)

        if args.shade:
            upper = means + stds
            lower = means - stds
            plt.fill_between(gens_sorted, lower, upper, alpha=0.12)

        plt.plot(gens_sorted, means, linewidth=1.8, label=f"{method} (n={file_count_for_method[method]})")

    plt.xlabel("Generación")
    plt.ylabel("best_fitness (media por método)")
    plt.title(args.title)
    plt.grid(True, alpha=0.3)
    plt.legend(ncol=2)

    if args.outplot:
        ext = os.path.splitext(args.outplot)[1].lower()
        if ext in {".jpg", ".jpeg"}:
            plt.savefig(args.outplot, dpi=args.dpi, bbox_inches="tight", quality=95)
        else:
            plt.savefig(args.outplot, dpi=args.dpi, bbox_inches="tight")
        print(f"[saved] {args.outplot}")
    else:
        plt.show()

if __name__ == "__main__":
    main()
