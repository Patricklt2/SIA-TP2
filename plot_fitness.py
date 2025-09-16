#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot best_fitness vs generation para uno o más CSVs.
Además marca con triángulos (^) los puntos donde se incrementó mutation_rate
(usual cuando hubo estancamiento y se subió la tasa).

Uso:
  python plot_fitness.py out/exp1.csv out/exp2.csv
"""
import sys
import os
import csv
import math
import matplotlib.pyplot as plt

def read_series(csv_path):
    """Lee generation, best_fitness, mutation_rate (si existe)."""
    gens, bests, muts = [], [], []
    has_mut = False
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise SystemExit(f"{csv_path} vacío.")

        # columnas (case-insensitive)
        def find(col):
            for i, name in enumerate(header):
                if name.strip().lower() == col:
                    return i
            return None

        gen_idx = find("generation")
        best_idx = find("best_fitness")
        mut_idx  = find("mutation_rate")

        if best_idx is None:
            raise SystemExit(f"{csv_path} no tiene columna 'best_fitness'. Columnas: {header}")

        for i, row in enumerate(reader):
            if not row:
                continue
            # best
            try:
                bf = float(row[best_idx])
            except Exception:
                continue
            # gen
            if gen_idx is not None:
                try:
                    g = float(row[gen_idx])
                except Exception:
                    g = float(i)
            else:
                g = float(i)
            # mutation
            if mut_idx is not None:
                try:
                    mu = float(row[mut_idx])
                    has_mut = True
                except Exception:
                    mu = math.nan
            else:
                mu = math.nan

            gens.append(g)
            bests.append(bf)
            muts.append(mu)

    if not gens:
        raise SystemExit(f"Sin datos en {csv_path}.")
    return gens, bests, (muts if has_mut else None)

def mutation_increase_indices(muts):
    """Devuelve índices donde mutation_rate sube respecto a la fila anterior."""
    if muts is None:
        return []
    idxs = []
    eps = 1e-12
    for i in range(1, len(muts)):
        a, b = muts[i-1], muts[i]
        if (not math.isnan(a)) and (not math.isnan(b)) and (b > a + eps):
            idxs.append(i)
    return idxs

def main():
    if len(sys.argv) < 2:
        print("Uso: python plot_fitness.py <csv1> [<csv2> ...]")
        sys.exit(1)
    csvs = sys.argv[1:]

    os.makedirs("out", exist_ok=True)
    plt.figure()

    any_markers = False
    for path in csvs:
        label = os.path.splitext(os.path.basename(path))[0]
        x, y, mut = read_series(path)
        # curva principal
        line, = plt.plot(x, y, label=label, linewidth=1.8)
        color = line.get_color()

        # marcar subas de mutation_rate
        inc_idxs = mutation_increase_indices(mut)
        if inc_idxs:
            any_markers = True
            mx = [x[i] for i in inc_idxs]
            my = [y[i] for i in inc_idxs]
            # triángulos con borde negro para destacar
            plt.scatter(mx, my, marker="^", s=60, facecolors=color, edgecolors="k", zorder=5,
                        label=None)  # no duplicar leyenda por cada serie

        # si no hay columna mutation_rate avisamos
        if mut is None:
            print(f"[WARN] {label}: CSV sin columna 'mutation_rate'; no se marcan subas.")

    plt.title("Avance de fitness (best_fitness) + subas de mutation_rate (^) ")
    plt.xlabel("Generación")
    plt.ylabel("best_fitness")
    plt.grid(True, alpha=0.3)

    # agregar una entrada de leyenda para los marcadores si se usaron
    if any_markers:
        # handle "falso" solo para la leyenda del marcador
        from matplotlib.lines import Line2D
        marker_legend = Line2D([0], [0], marker="^", color="w", label="Suba mutation_rate",
                               markerfacecolor="gray", markeredgecolor="k", markersize=8, linewidth=0)
        leg_handles, leg_labels = plt.gca().get_legend_handles_labels()
        leg_handles.append(marker_legend); leg_labels.append("Suba mutation_rate")
        plt.legend(leg_handles, leg_labels)
    else:
        plt.legend()

    # Guardar antes de mostrar (evita figuras vacías en algunos backends)
    out_path = "out/plot_fitness.png"
    plt.savefig(out_path, dpi=140, bbox_inches="tight")
    print("[saved]", out_path)

    # Mostrar (opcional)
    plt.show()

if __name__ == "__main__":
    main()
