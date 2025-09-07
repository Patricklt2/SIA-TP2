import random
from ..preprocessing.shared_seed_store import find_seed_by_point


def make_seed_guided_mutation(base_mutation, seed_store, adopt_prob=0.5):
    """Return a mutation function that first runs base_mutation then, with some probability,
    replaces polygon colors with nearby tile seed mean colors from seed_store.

    base_mutation: function(individual, mutation_rate)
    seed_store: dict-like mapping tile_id->seed dict (as produced by create_shared_seed_store)
    adopt_prob: relative chance to try adopting a seed color per polygon (0..1)
    """
    def mutation(individual, mutation_rate):
        # run the base mutation first to preserve existing behavior
        try:
            base_mutation(individual, mutation_rate)
        except Exception:
            # if base fails for any reason, continue with seed-guided steps
            pass

        if seed_store is None:
            return

        # For each polygon, sometimes try to adopt the seed color for the tile containing the polygon centroid
        for poly in individual.polygons:
            if random.random() >= (mutation_rate * adopt_prob):
                continue

            xs = [v[0] for v in poly.vertices]
            ys = [v[1] for v in poly.vertices]
            if not xs or not ys:
                continue
            cx = int(sum(xs) / len(xs))
            cy = int(sum(ys) / len(ys))

            res = find_seed_by_point(seed_store, cx, cy)
            if not res:
                continue
            _, sd = res
            mean_color = sd.get('mean_color')
            if mean_color:
                # adopt the seed color
                poly.color = mean_color

    return mutation
