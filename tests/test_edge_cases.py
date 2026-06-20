# -*- coding: utf-8 -*-
"""Edge case and error handling tests."""

from fractions import Fraction
from typing import Any, Dict

import pytest

from digraphx.min_cycle_ratio import MinCycleRatioSolver
from digraphx.neg_cycle import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


def test_empty_graph_neg_cycle() -> None:
    """Test negative cycle finder on completely empty graph."""
    graph = DiGraphAdapter()
    dist: Dict[str, Fraction] = {}

    finder: NegCycleFinder[str, Dict[str, Any], Fraction] = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: Fraction(edge.get("weight", 1))))
    assert len(cycles) == 0


def test_single_node_no_edges() -> None:
    """Test graph with single node and no edges."""
    graph = DiGraphAdapter()
    graph.add_node(0)

    dist = {0: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) == 0


def test_single_node_self_loop_negative() -> None:
    """Test single node with negative self-loop."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 0, weight=-1)

    dist = {0: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


def test_single_node_self_loop_positive() -> None:
    """Test single node with positive self-loop."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 0, weight=5)

    dist = {0: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) == 0


def test_disconnected_components() -> None:
    """Test graph with multiple disconnected components."""
    graph = DiGraphAdapter()

    # Component 1
    graph.add_edge(0, 1, weight=1)
    graph.add_edge(1, 0, weight=1)

    # Component 2
    graph.add_edge(10, 11, weight=1)
    graph.add_edge(11, 10, weight=-5)  # Negative cycle here

    # Component 3 (isolated)
    graph.add_node(20)

    dist = {0: 0, 1: 0, 10: 0, 11: 0, 20: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


def test_tiny_digraph_init_zero_nodes() -> None:
    """Test TinyDiGraph initialization with zero nodes."""
    graph = TinyDiGraph()
    graph.init_nodes(0)

    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0


def test_tiny_digraph_add_edge_before_init() -> None:
    """Test adding edge before initializing nodes."""
    graph = TinyDiGraph()

    with pytest.raises(Exception):
        graph.add_edge(0, 1, weight=1)


def test_non_numeric_weights() -> None:
    """Test that algorithm works with non-numeric weight types."""
    graph = DiGraphAdapter()
    graph.add_edge("a", "b", weight=Fraction(1, 2))
    graph.add_edge("b", "c", weight=Fraction(1, 3))
    graph.add_edge("c", "a", weight=Fraction(-1, 1))

    dist = {"a": Fraction(0), "b": Fraction(0), "c": Fraction(0)}
    finder: NegCycleFinder[str, Dict[str, Any], Fraction] = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: Fraction(edge["weight"])))
    assert len(cycles) > 0


def test_mixed_node_types() -> None:
    """Test graph with mixed node types (strings and ints)."""
    graph = DiGraphAdapter()
    graph.add_edge("a", 0, weight=1)
    graph.add_edge(0, "b", weight=2)
    graph.add_edge("b", "a", weight=-5)

    dist = {"a": 0, "b": 0, 0: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


def test_zero_weight_cycle() -> None:
    """Test cycle with all zero weights."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 1, weight=0)
    graph.add_edge(1, 2, weight=0)
    graph.add_edge(2, 0, weight=0)

    dist = {0: 0, 1: 0, 2: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) == 0  # Zero cycle is not negative


def test_very_large_weights() -> None:
    """Test with very large weight values."""
    graph = DiGraphAdapter()
    large_weight = 10**15
    graph.add_edge(0, 1, weight=large_weight)
    graph.add_edge(1, 2, weight=large_weight)
    graph.add_edge(2, 0, weight=-3 * large_weight)

    dist = {0: 0, 1: 0, 2: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


def test_digraph_adapter_mixed_edge_attributes() -> None:
    """Test DiGraphAdapter with mixed edge attributes."""
    graph = DiGraphAdapter()
    graph.add_edge("a", "b", weight=5, cost=10, time=2, label="edge1")
    graph.add_edge("b", "c", weight=3, cost=6, time=1, label="edge2")
    graph.add_edge("c", "a", weight=-2, cost=0, time=1, label="edge3")

    assert graph["a"]["b"]["weight"] == 5
    assert graph["a"]["b"]["cost"] == 10
    assert graph["a"]["b"]["label"] == "edge1"


def test_min_cycle_ratio_empty_graph() -> None:
    """Test minimum cycle ratio solver on empty graph."""
    graph = DiGraphAdapter()
    dist: Dict[str, Fraction] = {}

    solver: MinCycleRatioSolver[str, Dict[str, int], Fraction] = MinCycleRatioSolver(
        graph
    )
    ratio, cycle = solver.run(dist, Fraction(10))
    assert ratio == Fraction(10)  # No cycles found, returns initial ratio
    assert len(cycle) == 0


def test_min_cycle_ratio_single_node() -> None:
    """Test minimum cycle ratio solver on single node graph."""
    graph = DiGraphAdapter()
    graph.add_edge("a", "a", cost=5, time=1)

    dist = {"a": Fraction(0)}
    solver: MinCycleRatioSolver[str, Dict[str, int], Fraction] = MinCycleRatioSolver(
        graph
    )
    ratio, cycle = solver.run(dist, Fraction(10))
    assert isinstance(ratio, (Fraction, float))


def test_invalid_weight_extraction() -> None:
    """Test handling of edges with missing weight attributes."""
    graph = DiGraphAdapter()
    graph.add_edge("a", "b", weight=5)
    graph.add_edge("b", "c")  # No weight attribute

    dist = {"a": 0, "b": 0, "c": 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) == 0


def test_directed_graph_orientation() -> None:
    """Test that algorithm respects edge direction."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 1, weight=1)
    graph.add_edge(1, 2, weight=1)
    graph.add_edge(2, 0, weight=-5)

    dist = {0: 0, 1: 0, 2: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0  # 0->1->2->0 forms negative cycle


def test_multiple_edges_same_nodes() -> None:
    """Test graph with multiple edges between same node pair (parallel edges)."""
    graph = DiGraphAdapter()
    # NetworkX typically replaces parallel edges, but test behavior
    graph.add_edge(0, 1, weight=5)
    graph.add_edge(0, 1, weight=-5)  # This replaces the previous edge

    dist = {0: 0, 1: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) == 0  # Single edge can't form cycle


def test_floating_point_weights() -> None:
    """Test with floating point weights."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 1, weight=0.1)
    graph.add_edge(1, 2, weight=0.2)
    graph.add_edge(2, 0, weight=-0.5)

    dist: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0}
    finder: NegCycleFinder[int, Dict[str, Any], float] = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1.0)))
    assert len(cycles) > 0


def test_negative_self_loop() -> None:
    """Test negative self-loop detection."""
    graph = DiGraphAdapter()
    graph.add_edge(0, 1, weight=1)
    graph.add_edge(1, 0, weight=1)
    graph.add_edge(2, 2, weight=-1)  # Negative self-loop

    dist = {0: 0, 1: 0, 2: 0}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


def test_no_path_between_components() -> None:
    """Test that negative cycle in one component is detected even when other components exist."""
    graph = DiGraphAdapter()
    # Component 1: no cycle
    graph.add_edge(0, 1, weight=1)
    graph.add_edge(2, 3, weight=1)

    # Component 2: negative cycle
    graph.add_edge(10, 11, weight=1)
    graph.add_edge(11, 10, weight=-2)

    dist = {node: 0 for node in [0, 1, 2, 3, 10, 11]}
    finder = NegCycleFinder(graph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) > 0


# ── Multi-edge (parallel edge) tests ─────────────────────────────────────────


def test_multi_edge_list_of_lists_no_cycle() -> None:
    """Multi-edge graph using list-of-lists (like C++ test_neg_cycle_raw.cpp).

    Two parallel edges from node 2 to node 0, none forming a negative cycle.
    """
    digraph = {
        0: [(1, 7.0), (2, 5.0)],
        1: [(0, 0.0), (2, 3.0)],
        2: [(1, 1.0), (0, 2.0), (0, 1.0)],  # two parallel edges 2→0
    }
    dist = {0: 0.0, 1: 0.0, 2: 0.0}
    finder: NegCycleFinder[int, float, float] = NegCycleFinder(digraph)
    cycles = list(finder.howard(dist, lambda w: w))
    assert len(cycles) == 0


def test_multi_edge_list_of_lists_with_cycle() -> None:
    """Multi-edge graph with a negative cycle formed by parallel edges."""
    digraph = {
        0: [(1, 1.0)],
        1: [(2, 1.0)],
        2: [(0, -3.0), (0, 2.0)],  # one negative, one positive parallel edge
    }
    dist = {0: 0.0, 1: 0.0, 2: 0.0}
    finder: NegCycleFinder[int, float, float] = NegCycleFinder(digraph)
    cycles = list(finder.howard(dist, lambda w: w))
    assert len(cycles) > 0


def test_multi_edge_q_variant() -> None:
    """NegCycleFinderQ with multi-edge graph (predecessor variant)."""
    from digraphx.neg_cycle_q import NegCycleFinderQ

    digraph = {
        0: [(1, 7.0), (2, 5.0)],
        1: [(0, 0.0), (2, 3.0)],
        2: [(1, 1.0), (0, 2.0), (0, 1.0)],  # two parallel edges 2→0
    }
    dist = {0: 0.0, 1: 0.0, 2: 0.0}
    update_ok = lambda old, new: True
    finder: NegCycleFinderQ[int, float, float] = NegCycleFinderQ(digraph)
    cycles = list(finder.howard_pred(dist, lambda w: w, update_ok))
    assert len(cycles) == 0


def test_multi_edge_dict_backward_compat() -> None:
    """Dict-based graphs still work (backward compatibility)."""
    digraph = {
        0: {1: 7.0, 2: 5.0},
        1: {0: 0.0, 2: 3.0},
        2: {1: 1.0, 0: 2.0},
    }
    dist = {0: 0.0, 1: 0.0, 2: 0.0}
    finder: NegCycleFinder[int, float, float] = NegCycleFinder(digraph)
    cycles = list(finder.howard(dist, lambda w: w))
    assert len(cycles) == 0
