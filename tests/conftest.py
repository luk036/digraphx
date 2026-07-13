"""
Fixtures for digraphx tests.
"""

from fractions import Fraction
from typing import List

import networkx as nx
import pytest

from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


@pytest.fixture
def high_ratio() -> Fraction:
    """A high ratio value for testing."""
    return Fraction(10000, 1)


@pytest.fixture
def create_test_case1() -> DiGraphAdapter:
    """Creates a test graph with a negative cycle."""
    digraph: DiGraphAdapter = nx.cycle_graph(5, create_using=DiGraphAdapter())
    digraph[1][2]["weight"] = -5
    digraph.add_edges_from([(5, n) for n in digraph])
    return digraph


@pytest.fixture
def create_test_case_timing() -> DiGraphAdapter:
    """Creates a test graph for timing tests."""
    digraph: DiGraphAdapter = DiGraphAdapter()
    nodelist: List[str] = ["a1", "a2", "a3"]
    digraph.add_nodes_from(nodelist)
    digraph.add_edges_from(
        [
            ("a1", "a2", {"weight": 7}),
            ("a2", "a1", {"weight": 0}),
            ("a2", "a3", {"weight": 3}),
            ("a3", "a2", {"weight": 1}),
            ("a3", "a1", {"weight": 2}),
            ("a1", "a3", {"weight": 5}),
        ]
    )
    return digraph


@pytest.fixture
def create_tiny_graph() -> TinyDiGraph:
    """Creates a TinyDiGraph for testing."""
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(3)
    digraph.add_edges_from(
        [
            (0, 1, {"weight": 7}),
            (1, 0, {"weight": 0}),
            (1, 2, {"weight": 3}),
            (2, 1, {"weight": 1}),
            (2, 0, {"weight": 2}),
            (0, 2, {"weight": 5}),
        ]
    )
    return digraph


# --- spareTSV fixtures ---


@pytest.fixture
def sample_positions():
    """Van der Corput positions (T=12, bases 2/3)."""
    from digraphx.spare_tsv import vdc

    T = 12
    xbase, ybase = 2, 3
    x = [vdc(i, xbase) for i in range(T)]
    y = [vdc(i, ybase) for i in range(T)]
    return list(zip(x, y))


@pytest.fixture
def small_graph(sample_positions):
    """Small geometric graph for spareTSV tests."""
    from digraphx.spare_tsv import formGraph

    return formGraph(12, sample_positions, 0.12, 1.6, seed=5)
