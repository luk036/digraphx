# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction

import networkx as nx
import pytest

from mywheel.map_adapter import MapAdapter

from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default
from digraphx.tiny_digraph import DiGraphAdapter

from .test_neg_cycle import (
    create_test_case1,
    create_test_case_timing,
    create_tiny_graph,
)


def test_cycle_ratio_no_cycle():
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 1, cost=1, time=1)
    digraph.add_edge(1, 2, cost=1, time=1)
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    assert not cycle


def test_cycle_ratio_self_loop():
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 0, cost=2, time=1)
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    assert ratio == Fraction(2, 1)
    assert cycle


def test_cycle_ratio_raw():
    digraph = {
        "a0": {"a1": {"cost": 7, "time": 1}, "a2": {"cost": 5, "time": 1}},
        "a1": {"a0": {"cost": 0, "time": 1}, "a2": {"cost": 3, "time": 1}},
        "a2": {"a1": {"cost": 1, "time": 1}, "a0": {"cost": 2, "time": 1}},
    }
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(2, 1)


def test_cycle_ratio():
    digraph = create_test_case1()
    set_default(digraph, "time", 1)
    set_default(digraph, "cost", 1)
    digraph[1][2]["cost"] = 5
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing():
    digraph = create_test_case_timing()
    set_default(digraph, "time", 1)
    digraph["a1"]["a2"]["cost"] = 7
    digraph["a2"]["a1"]["cost"] = -1
    digraph["a2"]["a3"]["cost"] = 3
    digraph["a3"]["a2"]["cost"] = 0
    digraph["a3"]["a1"]["cost"] = 2
    digraph["a1"]["a3"]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = {vtx: Fraction(0, 1) for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)


def test_cycle_ratio_tiny_graph():
    digraph = create_tiny_graph()
    set_default(digraph, "time", 1)
    digraph[0][1]["cost"] = 7
    digraph[1][0]["cost"] = -1
    digraph[1][2]["cost"] = 3
    digraph[2][1]["cost"] = 0
    digraph[2][0]["cost"] = 2
    digraph[0][2]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = MapAdapter([0 for _ in range(3)])
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)
