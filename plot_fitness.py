#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot simple best_fitness progress for one or more metrics CSVs.
Labels are the CSV basenames.
Usage:
  python plot_fitness.py out/exp1.csv out/exp2.csv
"""
import sys
import os
import csv
import matplotlib.pyplot as plt

def read_best_series(csv_path):
    xs, ys = [], []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise SystemExit(f"{csv_path} vacío.")
        # columns
        def find(col):
            for i, name in enumerate(header):
                if name.strip().lower() == col:
                    return i
            return None
        gen_idx = find("generation")
        best_idx = find("best_fitness")
        if best_idx is None:
            raise SystemExit(f"{csv_path} no tiene columna 'best_fitness'. Columnas: {header}")
        for i, row in enumerate(reader):
            if not row:
                continue
            try:
                y = float(row[best_idx])
            except Exception:
                continue
            if gen_idx is not None:
                try:
                    x = float(row[gen_idx])
                except Exception:
                    x = float(i)
            else:
                x = float(i)
            xs.append(x); ys.append(y)
    if not xs:
        raise SystemExit(f"Sin datos en {csv_path}.")
    return xs, ys

def main():
    if len(sys.argv) < 2:
        print("Uso: python plot_fitness.py <csv1> [<csv2> ...]")
        sys.exit(1)
    csvs = sys.argv[1:]

    plt.figure()
    for path in csvs:
        label = os.path.splitext(os.path.basename(path))[0]
        x, y = read_best_series(path)
        plt.plot(x, y, label=label, linewidth=1.6)

    plt.title("Avance de fitness (best_fitness)")
    plt.xlabel("Generación")
    plt.ylabel("best_fitness")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
