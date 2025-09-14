import random
import numpy as np
import bisect

def stochastic_universal_sampling(population, num_selected, rng=None):
    if rng is None:
        rng = random.Random()

    inds = list(population)
    N = len(inds)
    if N == 0 or num_selected <= 0:
        return []

    fitness = np.array([getattr(i, "fitness", 0.0) for i in inds], dtype=float)
    fitness = np.nan_to_num(fitness, nan=0.0, posinf=0.0, neginf=0.0)
    minf = fitness.min()
    if minf < 0:
        fitness = fitness - minf

    total = float(fitness.sum())
    if total <= 0:
        # fallback uniform selection without replacement
        return list(rng.sample(inds, k=min(num_selected, N)))

    probs = (fitness / total).tolist()
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)

    start = rng.random() / num_selected
    pointers = [start + i / num_selected for i in range(num_selected)]
    selected = []
    for p in pointers:
        # wrap p into [0,1)
        r = p % 1.0
        idx = bisect.bisect_left(cum, r)
        if idx >= N:
            idx = N - 1
        selected.append(inds[idx])
    return selected