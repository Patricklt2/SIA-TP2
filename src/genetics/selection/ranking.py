import random
import numpy as np
import bisect

def ranking_selection(population, num_selected, rng=None):
    if rng is None:
        rng = random.Random()

    inds = list(population)
    N = len(inds)
    if N == 0 or num_selected <= 0:
        return []

    # Sort by fitness ascending; best last
    sorted_inds = sorted(inds, key=lambda x: getattr(x, "fitness", float("-inf")))
    # assign weights 1..N where best gets highest weight
    weights = list(range(1, N + 1))
    total = float(sum(weights))
    probs = [w / total for w in weights]

    # cumulative
    cum = []
    s = 0.0
    for p in probs:
        s += p
        cum.append(s)

    choices = []
    for _ in range(num_selected):
        r = rng.random()
        idx = bisect.bisect_left(cum, r)
        if idx >= N:
            idx = N - 1
        choices.append(sorted_inds[idx])
    return choices