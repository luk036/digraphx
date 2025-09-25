# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx
from mywheel.map_adapter import MapAdapter

from digraphx.neg_cycle_q import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


def test_raw_graph_by_MapAdapter():
    def update_ok(dist, v):
        return True

    digraph = MapAdapter(
        [
            {1: 7, 2: 5},
            {0: 0, 2: 3},
            {1: 1, 0: 2},
        ]
    )

    dist = MapAdapter([0, 0, 0])
    finder = NegCycleFinder(digraph)
    has_neg = False
    for _ in finder.howard_pred(dist, lambda edge: edge, update_ok):
        has_neg = True
        break
    assert not has_neg
    has_neg = False
    for _ in finder.howard_succ(dist, lambda edge: edge, update_ok):
        has_neg = True
        break
    assert not has_neg


def test_raw_graph_by_dict():
    def update_ok(dist, v):
        return True

    digraph = {
        "a0": {"a1": 7, "a2": 5},
        "a1": {"a0": 0, "a2": 3},
        "a2": {"a1": 1, "a0": 2},
    }

    dist = {vtx: 0 for vtx in digraph}
    finder = NegCycleFinder(digraph)
    has_neg = False
    for _ in finder.howard_pred(dist, lambda edge: edge, update_ok):
        has_neg = True
        break
    assert not has_neg
    has_neg = False
    for _ in finder.howard_succ(dist, lambda edge: edge, update_ok):
        has_neg = True
        break
    assert not has_neg


def create_test_case1():
    """[summary]

    Returns:
        [type]: [description]
    """
    digraph = nx.cycle_graph(5, create_using=DiGraphAdapter())
    digraph[1][2]["weight"] = -5
    digraph.add_edges_from([(5, n) for n in digraph])
    return digraph


def create_test_case_timing():
    """[summary]

    Returns:
        [type]: [description]
    """
    digraph = DiGraphAdapter()
    nodelist = ["a1", "a2", "a3"]
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


def create_tiny_graph():
    """[summary]

    Returns:
        [type]: [description]
    """
    digraph = TinyDiGraph()
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


def do_case_pred(digraph, dist):
    """[summary]

    Arguments:
        digraph ([type]): [description]

    Returns:
        [type]: [description]
    """

    def update_ok(dist, v):
        return True

    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(digraph)
    has_neg = False
    for _ in ncf.howard_pred(dist, get_weight, update_ok):
        has_neg = True
        break
    return has_neg


def do_case_succ(digraph, dist):
    """[summary]

    Arguments:
        digraph ([type]): [description]

    Returns:
        [type]: [description]
    """

    def update_ok(dist, v):
        return True

    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(digraph)
    has_neg = False
    for _ in ncf.howard_succ(dist, get_weight, update_ok):
        has_neg = True
        break
    return has_neg


def test_neg_cycle():
    digraph = create_test_case1()
    dist = list(0 for _ in digraph)
    has_neg = do_case_pred(digraph, dist)
    assert has_neg
    has_neg = do_case_succ(digraph, dist)
    assert has_neg


def test_timing_graph():
    digraph = create_test_case_timing()
    dist = {vtx: 0 for vtx in digraph}
    has_neg = do_case_pred(digraph, dist)
    assert not has_neg
    has_neg = do_case_succ(digraph, dist)
    assert not has_neg


def test_tiny_graph():
    digraph = create_tiny_graph()
    dist = MapAdapter([0, 0, 0])
    has_neg = do_case_pred(digraph, dist)
    assert not has_neg
    has_neg = do_case_succ(digraph, dist)
    assert not has_neg


def test_neg_cycle_q_no_edges():
    def update_ok(dist, v):
        return True

    digraph = DiGraphAdapter()
    digraph.add_nodes_from([0, 1, 2])
    dist = {vtx: 0 for vtx in digraph}
    finder = NegCycleFinder(digraph)
    has_neg = False
    for _ in finder.howard_pred(dist, lambda edge: edge.get("weight", 1), update_ok):
        has_neg = True
        break
    assert not has_neg
    has_neg = False
    for _ in finder.howard_succ(dist, lambda edge: edge.get("weight", 1), update_ok):
        has_neg = True
        break
    assert not has_neg


def test_neg_cycle_q_self_loop():
    def update_ok(dist, v):
        return True

    digraph = DiGraphAdapter()
    digraph.add_edge(0, 0, weight=-1)
    dist = {vtx: 0 for vtx in digraph}
    finder = NegCycleFinder(digraph)
    has_neg = False
    for _ in finder.howard_pred(dist, lambda edge: edge.get("weight", 1), update_ok):
        has_neg = True
        break
    assert has_neg
    has_neg = False
    for _ in finder.howard_succ(dist, lambda edge: edge.get("weight", 1), update_ok):
        has_neg = True
        break
    assert has_neg


def test_neg_cycle_q_multiple_neg_cycles():
    def update_ok(dist, v):
        return True

    digraph = DiGraphAdapter()
    digraph.add_edge(0, 1, weight=-1)
    digraph.add_edge(1, 0, weight=-1)
    digraph.add_edge(2, 3, weight=-1)
    digraph.add_edge(3, 2, weight=-1)
    dist = {vtx: 0 for vtx in digraph}
    finder = NegCycleFinder(digraph)
    cycles = list(finder.howard_pred(dist, lambda edge: edge.get("weight", 1), update_ok))
    assert len(cycles) >= 1
    cycles = list(finder.howard_succ(dist, lambda edge: edge.get("weight", 1), update_ok))
    assert len(cycles) >= 1
