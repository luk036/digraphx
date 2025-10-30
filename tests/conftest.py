"""
Fixtures for digraphx tests.
"""

from fractions import Fraction
from typing import Any, Dict, List, Tuple, Union

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
