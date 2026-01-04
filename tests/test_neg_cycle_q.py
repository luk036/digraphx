# -*- coding: utf-8 -*-
from __future__ import print_function

from typing import Any, Callable, Dict, Union

from mywheel.map_adapter import MapAdapter

from digraphx.neg_cycle_q import NegCycleFinderQ
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph

SELF_LOOP_WEIGHT: int = -1
MULTIPLE_NEG_CYCLES_WEIGHT: int = -1


def _always_ok(d: Any, v: Any) -> bool:
    return True


def _get_weight(edge: Dict[str, int]) -> int:
    return edge.get("weight", 1)


def _has_negative_cycle_pred(
    digraph: Union[MapAdapter[Any], Dict[Any, Any], DiGraphAdapter, TinyDiGraph],
    dist: Union[MapAdapter[Any], Dict[Any, Any]],
    get_weight: Callable[[Any], Any],
) -> bool:
    """
    Check if a digraph has a negative cycle using Howard's algorithm (predecessor version).

    :param digraph: The graph to check.
    :param dist: A dictionary or MapAdapter with initial distances for each node.
    :param get_weight: A function to extract the weight from an edge.
    :return: True if a negative cycle is found, False otherwise.
    """
    finder: NegCycleFinderQ[Any, Any, Any] = NegCycleFinderQ(digraph)
    for _ in finder.howard_pred(dist, get_weight, _always_ok):  # type: ignore
        return True
    return False


def _has_negative_cycle_succ(
    digraph: Union[MapAdapter[Any], Dict[Any, Any], DiGraphAdapter, TinyDiGraph],
    dist: Union[MapAdapter[Any], Dict[Any, Any]],
    get_weight: Callable[[Any], Any],
) -> bool:
    """
    Check if a digraph has a negative cycle using Howard's algorithm (successor version).

    :param digraph: The graph to check.
    :param dist: A dictionary or MapAdapter with initial distances for each node.
    :param get_weight: A function to extract the weight from an edge.
    :return: True if a negative cycle is found, False otherwise.
    """
    finder: NegCycleFinderQ[Any, Any, Any] = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, get_weight, _always_ok):  # type: ignore
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
    assert not _has_negative_cycle_pred(digraph, dist, lambda edge: edge)
    assert not _has_negative_cycle_succ(digraph, dist, lambda edge: edge)


def test_raw_graph_by_dict() -> None:
    digraph: Dict[str, Dict[str, int]] = {
        "a0": {"a1": 7, "a2": 5},
        "a1": {"a0": 0, "a2": 3},
        "a2": {"a1": 1, "a0": 2},
    }
    dist: Dict[str, int] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, lambda edge: edge)
    assert not _has_negative_cycle_succ(digraph, dist, lambda edge: edge)


def test_neg_cycle(create_test_case1: DiGraphAdapter) -> None:
    digraph: DiGraphAdapter = create_test_case1
    dist: Dict[int, int] = {node: 0 for node in digraph}
    assert _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_timing_graph(create_test_case_timing: DiGraphAdapter) -> None:
    digraph: DiGraphAdapter = create_test_case_timing
    dist: Dict[str, int] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_tiny_graph(create_tiny_graph: TinyDiGraph) -> None:
    digraph: TinyDiGraph = create_tiny_graph
    dist: MapAdapter[Any] = MapAdapter([0, 0, 0])
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_no_edges() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_nodes_from([0, 1, 2])
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_self_loop() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 0, weight=SELF_LOOP_WEIGHT)
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    assert _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_multiple_neg_cycles() -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(1, 0, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(2, 3, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(3, 2, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    dist: Dict[int, int] = {vtx: 0 for vtx in digraph}
    finder: NegCycleFinderQ[Any, Any, Any] = NegCycleFinderQ(digraph)
    cycles = list(finder.howard_pred(dist, _get_weight, _always_ok))
    assert len(cycles) >= 1
    cycles = list(finder.howard_succ(dist, _get_weight, _always_ok))
    assert len(cycles) >= 1


def test_neg_cycle_q_is_negative_edge_case() -> None:
    """Test edge case in is_negative method where triangle inequality is not violated."""
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=1)
    digraph.add_edge(1, 2, weight=1)
    digraph.add_edge(2, 0, weight=1)

    dist: Dict[int, int] = {0: 0, 1: 1, 2: 2}
    finder: NegCycleFinderQ[Any, Any, Any] = NegCycleFinderQ(digraph)

    # Set up predecessor information to create a cycle
    finder.pred = {1: (0, digraph[0][1]), 2: (1, digraph[1][2]), 0: (2, digraph[2][0])}

    # This should return False as the triangle inequality is not violated
    assert not finder.is_negative(0, dist, _get_weight)
