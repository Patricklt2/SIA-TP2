import random


def tournament_selection(population, num_selected, k=3, replacement=True, rng=None):
    if rng is None:
        rng = random.Random()

    inds = list(population)
    N = len(inds)
    if N == 0 or num_selected <= 0:
        return []

    selected = []
    for _ in range(num_selected):
        if replacement:
            # sample k competitors with replacement
            competitors = [rng.choice(inds) for _ in range(k)]
        else:
            # sample k distinct competitors (or all if k > N)
            competitors = rng.sample(inds, k=min(k, N))
        # choose best by fitness (higher is better)
        best = max(competitors, key=lambda i: getattr(i, "fitness", float("-inf")))
        selected.append(best)
    return selected


def probabilistic_tournament_selection(population, num_selected, k=3, p=0.75, replacement=True, rng=None):
    if rng is None:
        rng = random.Random()

    inds = list(population)
    N = len(inds)
    if N == 0 or num_selected <= 0:
        return []

    # clamp p
    if p <= 0:
        p = 0.01
    if p > 1:
        p = 1.0

    selected = []
    for _ in range(num_selected):
        if replacement:
            competitors = [rng.choice(inds) for _ in range(k)]
        else:
            competitors = rng.sample(inds, k=min(k, N))

        # sort competitors by fitness descending (best first)
        competitors_sorted = sorted(competitors, key=lambda i: getattr(i, "fitness", float("-inf")), reverse=True)

        chosen = None
        for idx, cand in enumerate(competitors_sorted[:-1]):
            if rng.random() < p:
                chosen = cand
                break
            # continue to next with same p (geometric)
        if chosen is None:
            chosen = competitors_sorted[-1]
        selected.append(chosen)

    return selected

