# -*- coding: utf-8 -*-
from __future__ import print_function

from typing import Any, Callable, Dict, Union

from mywheel.map_adapter import MapAdapter

from digraphx.neg_cycle import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph

SELF_LOOP_WEIGHT: int = -1
MULTIPLE_NEG_CYCLES_WEIGHT: int = -1


def _has_negative_cycle(
    digraph: Union[MapAdapter[Any], Dict[Any, Any], DiGraphAdapter, TinyDiGraph],
    dist: Union[MapAdapter[Any], Dict[Any, Any]],
    get_weight: Callable[[Any], Any] = lambda edge: edge.get("weight", 1),
) -> bool:
    """
    Check if a digraph has a negative cycle using Howard's algorithm.

    :param digraph: The graph to check.
    :param dist: A dictionary or MapAdapter with initial distances for each node.
    :param get_weight: A function to extract the weight from an edge.
    :return: True if a negative cycle is found, False otherwise.
    """
    finder: NegCycleFinder[Any, Any, Any] = NegCycleFinder(digraph)
    for _ in finder.howard(dist, get_weight):  # type: ignore
        return True
    return False


def test_raw_graph_by_MapAdapter() -> None:
    digraph: MapAdapter[Any] = MapAdapter(
        [
            {1: 7, 2: 5},
            {0: 0, 2: 3},
            {1: 1, 0: 2},
        ]
    )
    dist: MapAdapter[Any] = MapAdapter([0, 0, 0])
    assert not _has_negative_cycle(digraph, dist, lambda edge: edge)


def test_raw_graph_by_dict() -> None:
    digraph: Dict[str, Dict[str, int]] = {
        "a0": {"a1": 7, "a2": 5},
        "a1": {"a0": 0, "a2": 3},
        "a2": {"a1": 1, "a0": 2},
    }
    dist: Dict[str, Any] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle(digraph, dist, lambda edge: edge)


def test_neg_cycle(create_test_case1: DiGraphAdapter) -> None:
    digraph: DiGraphAdapter = create_test_case1
    dist: Dict[int, int] = {node: 0 for node in digraph}
    assert _has_negative_cycle(digraph, dist)


def test_timing_graph(create_test_case_timing: DiGraphAdapter) -> None:
    digraph: DiGraphAdapter = create_test_case_timing
    dist: Dict[str, int] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle(digraph, dist)


def test_tiny_graph(create_tiny_graph: TinyDiGraph) -> None:
    digraph: TinyDiGraph = create_tiny_graph
    dist: MapAdapter[Any] = MapAdapter([0, 0, 0])
    assert not _has_negative_cycle(digraph, dist)


def test_neg_cycle_no_edges() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_nodes_from([0, 1, 2])
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle(digraph, dist)


def test_neg_cycle_self_loop() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 0, weight=SELF_LOOP_WEIGHT)
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    assert _has_negative_cycle(digraph, dist)


def test_neg_cycle_multiple_neg_cycles() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(1, 0, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(2, 3, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(3, 2, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    finder: NegCycleFinder[Any, Any, Any] = NegCycleFinder(digraph)
    cycles = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles) >= 1  # Howard's may not find all elementary cycles


def test_neg_cycle_is_negative_edge_case() -> None:
    """Test edge case in is_negative method where triangle inequality is not violated."""
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=1)
    digraph.add_edge(1, 2, weight=1)
    digraph.add_edge(2, 0, weight=1)

    dist: Dict[int, int] = {0: 0, 1: 1, 2: 2}
    finder: NegCycleFinder[Any, Any, Any] = NegCycleFinder(digraph)

    # Set up predecessor information to create a cycle
    finder.pred = {1: (0, digraph[0][1]), 2: (1, digraph[1][2]), 0: (2, digraph[2][0])}

    # This should return False as the triangle inequality is not violated
    assert not finder.is_negative(0, dist, lambda edge: edge.get("weight", 1))
