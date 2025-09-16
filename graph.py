#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot bar graphs for summary_mutation.csv, similar to compare_selection.py.
- Reads the CSV
- Groups by mutation, calculates mean and std for best_final and time_sec
- Plots two bar graphs with error bars: (1) best_final and (2) time_sec
- Saves plots as PNG if --save is used

Usage:
  python graph.py --outdir ./compare/mutation/plots --save
"""
import argparse
import csv
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def main():
    ap = argparse.ArgumentParser(description="Plot bar graphs for summary_mutation.csv.")
    ap.add_argument("--csv", type=str, default="./compare/mutation/summary_mutation.csv", help="Path to summary_mutation.csv.")
    ap.add_argument("--outdir", type=str, default="./compare/mutation/plots", help="Output directory for plots.")
    ap.add_argument("--save", action="store_true", help="Save plots as PNG.")
    args = ap.parse_args()

    ensure_dir(args.outdir)

    # Read CSV
    df = pd.read_csv(args.csv)

    # Group by mutation and calculate mean and std
    grouped = df.groupby('mutation')
    mutations = list(grouped.groups.keys())
    bf_means = grouped['best_final'].mean().tolist()
    bf_stds = grouped['best_final'].std(ddof=1).tolist()  # sample std
    tt_means = grouped['time_sec'].mean().tolist()
    tt_stds = grouped['time_sec'].std(ddof=1).tolist()

    # Plot 1: Best Final Fitness
    plt.figure(figsize=(10, 6))
    x = np.arange(len(mutations))
    plt.bar(x, bf_means, yerr=bf_stds, capsize=5)
    plt.xticks(x, mutations, rotation=45, ha='right')
    plt.ylabel("Best Final Fitness")
    plt.title("Best Final Fitness Across Mutations (Mean ± Std, n=5)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    if args.save:
        out1 = os.path.join(args.outdir, "bar_best_final.png")
        plt.savefig(out1, dpi=140, bbox_inches="tight")
        print(f"[saved] {out1}")
    else:
        plt.show()

    # Plot 2: Time in Seconds
    plt.figure(figsize=(10, 6))
    plt.bar(x, tt_means, yerr=tt_stds, capsize=5)
    plt.xticks(x, mutations, rotation=45, ha='right')
    plt.ylabel("Time (s)")
    plt.title("Time Across Mutations (Mean ± Std, n=5)")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    if args.save:
        out2 = os.path.join(args.outdir, "bar_time.png")
        plt.savefig(out2, dpi=140, bbox_inches="tight")
        print(f"[saved] {out2}")
    else:
        plt.show()


if __name__ == "__main__":
    main()