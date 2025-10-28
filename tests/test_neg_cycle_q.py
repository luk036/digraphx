# -*- coding: utf-8 -*-
from __future__ import print_function

from mywheel.map_adapter import MapAdapter

from digraphx.neg_cycle_q import NegCycleFinderQ
from digraphx.tiny_digraph import DiGraphAdapter


SELF_LOOP_WEIGHT = -1
MULTIPLE_NEG_CYCLES_WEIGHT = -1


def _always_update(d, v):
    return True


def _get_weight(edge):
    return edge.get("weight", 1)


def _has_negative_cycle_pred(digraph, dist, get_weight):
    """
    Check if a digraph has a negative cycle using Howard's algorithm (predecessor version).

    :param digraph: The graph to check.
    :param dist: A dictionary or MapAdapter with initial distances for each node.
    :param get_weight: A function to extract the weight from an edge.
    :return: True if a negative cycle is found, False otherwise.
    """
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_pred(dist, get_weight, _always_update):
        return True
    return False


def _has_negative_cycle_succ(digraph, dist, get_weight):
    """
    Check if a digraph has a negative cycle using Howard's algorithm (successor version).

    :param digraph: The graph to check.
    :param dist: A dictionary or MapAdapter with initial distances for each node.
    :param get_weight: A function to extract the weight from an edge.
    :return: True if a negative cycle is found, False otherwise.
    """
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, get_weight, _always_update):
        return True
    return False


def test_raw_graph_by_MapAdapter():
    digraph = MapAdapter(
        [
            {1: 7, 2: 5},
            {0: 0, 2: 3},
            {1: 1, 0: 2},
        ]
    )
    dist = MapAdapter([0, 0, 0])
    assert not _has_negative_cycle_pred(digraph, dist, lambda edge: edge)
    assert not _has_negative_cycle_succ(digraph, dist, lambda edge: edge)


def test_raw_graph_by_dict():
    digraph = {
        "a0": {"a1": 7, "a2": 5},
        "a1": {"a0": 0, "a2": 3},
        "a2": {"a1": 1, "a0": 2},
    }
    dist = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, lambda edge: edge)
    assert not _has_negative_cycle_succ(digraph, dist, lambda edge: edge)


def test_neg_cycle(create_test_case1):
    digraph = create_test_case1
    dist = list(0 for _ in digraph)
    assert _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_timing_graph(create_test_case_timing):
    digraph = create_test_case_timing
    dist = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_tiny_graph(create_tiny_graph):
    digraph = create_tiny_graph
    dist = MapAdapter([0, 0, 0])
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_no_edges():
    digraph = DiGraphAdapter()
    digraph.add_nodes_from([0, 1, 2])
    dist = {vtx: 0 for vtx in digraph}
    assert not _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert not _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_self_loop():
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 0, weight=SELF_LOOP_WEIGHT)
    dist = {vtx: 0 for vtx in digraph}
    assert _has_negative_cycle_pred(digraph, dist, _get_weight)
    assert _has_negative_cycle_succ(digraph, dist, _get_weight)


def test_neg_cycle_q_multiple_neg_cycles():
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(1, 0, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(2, 3, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    digraph.add_edge(3, 2, weight=MULTIPLE_NEG_CYCLES_WEIGHT)
    dist = {vtx: 0 for vtx in digraph}
    finder = NegCycleFinderQ(digraph)
    cycles = list(finder.howard_pred(dist, _get_weight, _always_update))
    assert len(cycles) >= 1
    cycles = list(finder.howard_succ(dist, _get_weight, _always_update))
    assert len(cycles) >= 1
