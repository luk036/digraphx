# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx

from mywheel.lict import Lict
from digraphx.neg_cycle_q import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


def test_raw_graph_by_lict():
    def update_ok(dist, v):
        return True

    gra = Lict(
        [
            {1: 7, 2: 5},
            {0: 0, 2: 3},
            {1: 1, 0: 2},
        ]
    )

    dist = Lict([0, 0, 0])
    finder = NegCycleFinder(gra)
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

    gra = {
        "a0": {"a1": 7, "a2": 5},
        "a1": {"a0": 0, "a2": 3},
        "a2": {"a1": 1, "a0": 2},
    }

    dist = {vtx: 0 for vtx in gra}
    finder = NegCycleFinder(gra)
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
    gra = nx.cycle_graph(5, create_using=DiGraphAdapter())
    gra[1][2]["weight"] = -5
    gra.add_edges_from([(5, n) for n in gra])
    return gra


def create_test_case_timing():
    """[summary]

    Returns:
        [type]: [description]
    """
    gra = DiGraphAdapter()
    nodelist = ["a1", "a2", "a3"]
    gra.add_nodes_from(nodelist)
    gra.add_edges_from(
        [
            ("a1", "a2", {"weight": 7}),
            ("a2", "a1", {"weight": 0}),
            ("a2", "a3", {"weight": 3}),
            ("a3", "a2", {"weight": 1}),
            ("a3", "a1", {"weight": 2}),
            ("a1", "a3", {"weight": 5}),
        ]
    )
    return gra


def create_tiny_graph():
    """[summary]

    Returns:
        [type]: [description]
    """
    gra = TinyDiGraph()
    gra.init_nodes(3)
    gra.add_edges_from(
        [
            (0, 1, {"weight": 7}),
            (1, 0, {"weight": 0}),
            (1, 2, {"weight": 3}),
            (2, 1, {"weight": 1}),
            (2, 0, {"weight": 2}),
            (0, 2, {"weight": 5}),
        ]
    )
    return gra


def do_case_pred(gra, dist):
    """[summary]

    Arguments:
        gra ([type]): [description]

    Returns:
        [type]: [description]
    """
    def update_ok(dist, v):
        return True

    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(gra)
    has_neg = False
    for _ in ncf.howard_pred(dist, get_weight, update_ok):
        has_neg = True
        break
    return has_neg


def do_case_succ(gra, dist):
    """[summary]

    Arguments:
        gra ([type]): [description]

    Returns:
        [type]: [description]
    """
    def update_ok(dist, v):
        return True

    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(gra)
    has_neg = False
    for _ in ncf.howard_succ(dist, get_weight, update_ok):
        has_neg = True
        break
    return has_neg


def test_neg_cycle():
    gra = create_test_case1()
    dist = list(0 for _ in gra)
    has_neg = do_case_pred(gra, dist)
    assert has_neg
    has_neg = do_case_succ(gra, dist)
    assert has_neg


def test_timing_graph():
    gra = create_test_case_timing()
    dist = {vtx: 0 for vtx in gra}
    has_neg = do_case_pred(gra, dist)
    assert not has_neg
    has_neg = do_case_succ(gra, dist)
    assert not has_neg


def test_tiny_graph():
    gra = create_tiny_graph()
    dist = Lict([0, 0, 0])
    has_neg = do_case_pred(gra, dist)
    assert not has_neg
    has_neg = do_case_succ(gra, dist)
    assert not has_neg
