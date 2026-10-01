"""Runtime benchmarks for digraphx core algorithms.

Run explicitly (they are outside the default ``testpaths`` so ``pytest`` alone
skips them):

    pytest benchmarks/ --benchmark-only

Uses fixed seeds so numbers are comparable across runs and across machines.
"""

import random
from fractions import Fraction

import networkx as nx
import pytest

from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default
from digraphx.neg_cycle import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph

SEED = 1234
SIZES = [200, 1000]
MCR_SIZES = [50, 100]


def weighted_graph(n: int, deg: int, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    g: dict = {i: {} for i in range(n)}
    for i in range(n):
        for _ in range(deg):
            j = rng.randrange(n)
            if j != i:
                g[i][j] = rng.randint(1, 9)
    for i in range(n - 1):
        g[i][i + 1] = 1
    g[n - 1][0] = -n
    return g


def ratio_graph(n: int, deg: int, seed: int = SEED) -> DiGraphAdapter:
    rng = random.Random(seed)
    g = DiGraphAdapter()
    g.add_nodes_from(range(n))
    for i in range(n):
        for _ in range(deg):
            j = rng.randrange(n)
            if j != i:
                g.add_edge(i, j, cost=rng.randint(-5, 9), time=rng.randint(1, 5))
    return g


@pytest.mark.parametrize("n", SIZES)
def test_bench_tiny_build(benchmark, n: int) -> None:
    deg = 5

    def build() -> TinyDiGraph:
        g = TinyDiGraph()
        g.init_nodes(n)
        for i in range(n):
            for j in range(1, deg + 1):
                g.add_edge(i, (i + j) % n, weight=1)
        return g

    benchmark(build)


@pytest.mark.parametrize("n", SIZES)
def test_bench_adapter_build(benchmark, n: int) -> None:
    deg = 5

    def build() -> DiGraphAdapter:
        g = DiGraphAdapter()
        g.add_nodes_from(range(n))
        for i in range(n):
            for j in range(1, deg + 1):
                g.add_edge(i, (i + j) % n, weight=1)
        return g

    benchmark(build)


@pytest.mark.parametrize("n", SIZES)
def test_bench_howard_negative_cycle(benchmark, n: int) -> None:
    g = weighted_graph(n, 6)
    finder = NegCycleFinder(g)

    def run() -> None:
        dist = {v: 0 for v in g}
        list(finder.howard(dist, lambda e: e))

    benchmark(run)


@pytest.mark.parametrize("n", SIZES)
def test_bench_networkx_negative_edge_cycle(benchmark, n: int) -> None:
    g = weighted_graph(n, 6)
    h = nx.DiGraph()
    for u, nb in g.items():
        h.add_node(u)
        for v, w in nb.items():
            h.add_edge(u, v, weight=w)

    benchmark(lambda: nx.negative_edge_cycle(h, weight="weight"))


@pytest.mark.parametrize("n", MCR_SIZES)
def test_bench_mcr_fraction(benchmark, n: int) -> None:
    g = ratio_graph(n, 5)
    set_default(g, "cost", 0)
    set_default(g, "time", 1)
    solver = MinCycleRatioSolver(g)

    def run():
        dist = {v: Fraction(0) for v in g}
        return solver.run(dist, Fraction(10))

    benchmark(run)


@pytest.mark.parametrize("n", MCR_SIZES)
def test_bench_mcr_float(benchmark, n: int) -> None:
    g = ratio_graph(n, 5)
    set_default(g, "cost", 0)
    set_default(g, "time", 1)
    solver = MinCycleRatioSolver(g)

    def run():
        dist = {v: 0.0 for v in g}
        return solver.run(dist, 10.0)

    benchmark(run)
