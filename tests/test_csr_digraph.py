"""Unit tests for CSRDiGraph — memory‑efficient CSR‑backed directed graph."""

from fractions import Fraction

import pytest

from digraphx.csr_digraph import CSRDiGraph, _CSRNeighbors
from digraphx.min_cycle_ratio import MinCycleRatioSolver
from digraphx.neg_cycle import NegCycleFinder

# =============================================================================
# Construction
# =============================================================================


def test_init_nodes():
    g = CSRDiGraph()
    g.init_nodes(5)
    assert len(g) == 5
    assert list(g) == [0, 1, 2, 3, 4]


def test_init_nodes_zero():
    g = CSRDiGraph()
    g.init_nodes(0)
    assert len(g) == 0
    assert list(g) == []


def test_add_edge_simple():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=7)
    g.freeze()
    assert 1 in g[0]
    assert g[0][1] == {"weight": 7}


def test_add_edge_no_attrs():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1)
    g.freeze()
    assert g[0][1] == {}


def test_add_edge_frozen_raises():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1)
    g.freeze()
    with pytest.raises(AssertionError, match="frozen"):
        g.add_edge(1, 0)


def test_freeze_idempotent():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1)
    g.freeze()
    g.freeze()  # second call should be a no‑op
    assert g[0][1] == {}


def test_auto_freeze_on_getitem():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1, weight=3)
    # No explicit freeze — __getitem__ triggers it
    assert g[0][1]["weight"] == 3


def test_auto_freeze_on_items():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1, weight=3)
    items = list(g.items())
    assert len(items) == 2
    assert dict(items[0][1].items()) == {1: {"weight": 3}}


# =============================================================================
# _CSRNeighbors view
# =============================================================================


def test_neighbors_view_items():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=7)
    g.add_edge(0, 2, weight=5)
    g.freeze()
    nbrs = g[0]
    assert sorted(nbrs.items()) == [(1, {"weight": 7}), (2, {"weight": 5})]


def test_neighbors_view_keys():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=7)
    g.add_edge(0, 2, weight=5)
    g.freeze()
    assert sorted(g[0].keys()) == [1, 2]


def test_neighbors_view_values():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=7)
    g.add_edge(0, 2, weight=5)
    g.freeze()
    vals = list(g[0].values())
    assert {"weight": 7} in vals
    assert {"weight": 5} in vals


def test_neighbors_view_contains():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1)
    g.freeze()
    assert 1 in g[0]
    assert 2 not in g[0]
    assert 99 not in g[0]


def test_neighbors_view_len():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.freeze()
    assert len(g[0]) == 2
    assert len(g[1]) == 0


def test_neighbors_view_getitem_missing():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1)
    g.freeze()
    with pytest.raises(KeyError, match="2"):
        g[0][2]


def test_neighbors_view_is_mapping():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 1)
    g.freeze()
    assert isinstance(g[0], _CSRNeighbors)


# =============================================================================
# Mapping protocol
# =============================================================================


def test_contains():
    g = CSRDiGraph()
    g.init_nodes(5)
    assert 0 in g
    assert 4 in g
    assert 5 not in g
    assert "a" not in g


def test_iter():
    g = CSRDiGraph()
    g.init_nodes(4)
    assert list(g) == [0, 1, 2, 3]


def test_len():
    g = CSRDiGraph()
    g.init_nodes(100)
    assert len(g) == 100


def test_items_yields_all_nodes():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1)
    g.freeze()
    nodes = [u for u, _ in g.items()]
    assert nodes == [0, 1, 2]


# =============================================================================
# Node helpers
# =============================================================================


def test_nodes():
    g = CSRDiGraph()
    g.init_nodes(4)
    assert list(g.nodes()) == [0, 1, 2, 3]


# =============================================================================
# Edge cases
# =============================================================================


def test_no_edges():
    g = CSRDiGraph()
    g.init_nodes(5)
    g.freeze()
    assert len(g) == 5
    for u in g:
        assert len(g[u]) == 0


def test_self_loop():
    g = CSRDiGraph()
    g.init_nodes(2)
    g.add_edge(0, 0, weight=-1)
    g.freeze()
    assert g[0][0] == {"weight": -1}
    assert len(g[0]) == 1


def test_multiple_edges_same_source():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=1)
    g.add_edge(0, 2, weight=2)
    g.add_edge(0, 1, weight=3)  # second edge to same target
    g.freeze()
    # __getitem__ returns the first stored instance
    assert g[0][1] == {"weight": 1}
    # Both entries are present in the adjacency
    data = list(g[0].items())
    assert len(data) == 3
    assert (1, {"weight": 1}) in data
    assert (2, {"weight": 2}) in data
    assert (1, {"weight": 3}) in data


def test_large_graph():
    g = CSRDiGraph()
    n = 100_000
    g.init_nodes(n)
    for i in range(n):
        g.add_edge(i, (i + 1) % n, weight=1)
    g.freeze()
    assert len(g) == n
    assert len(g[0]) == 1
    assert len(g[42]) == 1


def test_repr_before_init():
    g = CSRDiGraph()
    assert "0 nodes" in repr(g)


def test_repr_after_init():
    g = CSRDiGraph()
    g.init_nodes(5)
    assert "5 nodes" in repr(g) and "0 edges" in repr(g)


def test_repr_after_freeze():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1)
    g.freeze()
    r = repr(g)
    assert "3 nodes" in r
    assert "1 edges" in r or "1 edge" in r  # handle plural


# =============================================================================
# Algorithm integration
# =============================================================================


def test_neg_cycle_finder_no_cycle():
    g = CSRDiGraph()
    g.init_nodes(4)
    g.add_edge(0, 1, weight=1)
    g.add_edge(1, 2, weight=1)
    g.add_edge(2, 3, weight=1)
    g.freeze()

    dist = {n: 0 for n in g}
    finder = NegCycleFinder(g)
    cycles = list(finder.howard(dist, lambda e: e["weight"]))
    assert len(cycles) == 0


def test_neg_cycle_finder_with_cycle():
    g = CSRDiGraph()
    g.init_nodes(3)
    g.add_edge(0, 1, weight=5)
    g.add_edge(1, 2, weight=-10)
    g.add_edge(2, 0, weight=1)
    g.freeze()

    dist = {n: 0 for n in g}
    finder = NegCycleFinder(g)
    cycles = list(finder.howard(dist, lambda e: e["weight"]))
    assert len(cycles) > 0


def test_min_cycle_ratio():
    g = CSRDiGraph()
    g.init_nodes(4)
    g.add_edge(0, 1, cost=5, time=1)
    g.add_edge(1, 2, cost=3, time=1)
    g.add_edge(2, 3, cost=1, time=1)
    g.add_edge(3, 0, cost=-2, time=1)
    g.freeze()

    solver = MinCycleRatioSolver(g)
    dist = {n: Fraction(0) for n in g}
    ratio, cycle = solver.run(dist, Fraction(10))
    assert isinstance(ratio, Fraction)
    assert len(cycle) > 0


def test_neg_cycle_finder_large_csr():
    """Stress test — large CSR graph with NegCycleFinder."""
    g = CSRDiGraph()
    n = 10_000
    g.init_nodes(n)
    for i in range(n):
        g.add_edge(i, (i + 1) % n, weight=1)
    g.freeze()

    dist = {i: 0 for i in g}
    finder = NegCycleFinder(g)
    cycles = list(finder.howard(dist, lambda e: e["weight"]))
    assert len(cycles) == 0


def test_min_cycle_ratio_large_csr():
    """Stress test — large CSR graph with MinCycleRatioSolver."""
    g = CSRDiGraph()
    n = 2_000
    g.init_nodes(n)
    for i in range(n - 1):
        g.add_edge(i, i + 1, cost=1, time=1)
    g.add_edge(n - 1, 0, cost=-5, time=1)
    g.freeze()

    solver = MinCycleRatioSolver(g)
    dist = {i: Fraction(0) for i in g}
    ratio, cycle = solver.run(dist, Fraction(10))
    assert isinstance(ratio, Fraction)
