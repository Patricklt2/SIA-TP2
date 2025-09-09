import numpy as np
import random

from genetics.selection.ruleta import roulette_selection
from genetics.selection.universal import stochastic_universal_sampling
from genetics.selection.ranking import ranking_selection
from genetics.selection.boltzmann import boltzmann_selection
from genetics.selection.torneos import tournament_selection

class Dummy:
    def __init__(self, fitness, ident):
        self.fitness = fitness
        self.id = ident

def make_pop(fitnesses):
    return [Dummy(f, i) for i, f in enumerate(fitnesses)]

def ids_of(selected):
    return [s.id for s in selected]

def test_roulette_basic():
    np.random.seed(1)
    pop = make_pop([0.0, 1.0, 2.0, 3.0, 4.0])
    out = roulette_selection(pop, 10)
    assert len(out) == 10
    assert all(isinstance(x, Dummy) for x in out)
    assert all(x in pop for x in out)

def test_roulette_zero_total_fallback():
    np.random.seed(2)
    pop = make_pop([0.0, 0.0, 0.0])
    out = roulette_selection(pop, 5)
    assert len(out) == 5
    assert all(x in pop for x in out)

def test_universal_basic():
    np.random.seed(1)
    pop = make_pop([0.0, 1.0, 2.0, 3.0, 4.0])
    out = stochastic_universal_sampling(pop, 4)
    assert len(out) == 4
    assert all(x in pop for x in out)

def test_ranking_basic():
    np.random.seed(3)
    pop = make_pop([0.1, 0.2, 0.3, 0.4])
    out = ranking_selection(pop, 6)
    assert len(out) == 6
    assert all(x in pop for x in out)

def test_boltzmann_basic():
    np.random.seed(4)
    pop = make_pop([0.0, 1.0, 2.0, 3.0])
    out = boltzmann_selection(pop, 5, T=1.0)
    assert len(out) == 5
    assert all(x in pop for x in out)

def test_tournament_with_replacement():
    rng = random.Random(1)
    pop = make_pop([0.0, 1.0, 2.0, 3.0, 4.0])
    out = tournament_selection(pop, 6, k=3, replacement=True, rng=rng)
    assert len(out) == 6
    assert all(x in pop for x in out)

def test_tournament_without_replacement():
    rng = random.Random(2)
    pop = make_pop([0.0, 1.0, 2.0, 3.0])
    out = tournament_selection(pop, 3, k=3, replacement=False, rng=rng)
    assert len(out) == 3
    assert all(x in pop for x in out)