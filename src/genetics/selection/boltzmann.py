import random
import numpy as np
import math
import bisect

def boltzmann_selection(population, num_selected, T=1.0, rng=None):
    """Boltzmann selection using temperature T. Higher T -> more uniform, lower T -> stronger selection."""
    if rng is None:
        rng = random.Random()

    inds = list(population)
    N = len(inds)
    if N == 0 or num_selected <= 0:
        return []

    fitness = np.array([getattr(i, "fitness", 0.0) for i in inds], dtype=float)
    fitness = np.nan_to_num(fitness, nan=0.0, posinf=0.0, neginf=0.0)
    # Stable exponentiation: subtract max
    if T <= 0:
        T = 1e-6
    scaled = fitness / T
    maxs = float(np.max(scaled))
    exps = np.exp(scaled - maxs)
    total = float(np.sum(exps))
    if total <= 0:
        return [rng.choice(inds) for _ in range(num_selected)]

    probs = (exps / total).tolist()
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)

    selected = []
    for _ in range(num_selected):
        r = rng.random()
        idx = bisect.bisect_left(cum, r)
        if idx >= N:
            idx = N - 1
        selected.append(inds[idx])
    return selected