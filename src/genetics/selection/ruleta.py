import random
import numpy as np
import bisect

def roulette_selection(population, num_selected, rng=None):
    if rng is None:
        rng = random.Random()

    inds = list(population)
    if len(inds) == 0 or num_selected <= 0:
        return []

    fitness = np.array([getattr(i, "fitness", 0.0) for i in inds], dtype=float)
    # Guard against NaN/inf
    fitness = np.nan_to_num(fitness, nan=0.0, posinf=0.0, neginf=0.0)

    # Shift to non-negative
    minf = fitness.min()
    if minf < 0:
        fitness = fitness - minf

    total = float(fitness.sum())
    if total <= 0:
        # fallback: uniform random
        return [rng.choice(inds) for _ in range(num_selected)]

    probs = (fitness / total).tolist()
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)

    selected = []
    for _ in range(num_selected):
        r = rng.random()
        idx = bisect.bisect_left(cum, r)
        if idx >= len(inds):
            idx = len(inds) - 1
        selected.append(inds[idx])
    return selected