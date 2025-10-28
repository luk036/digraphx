# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction

import pytest
from mywheel.map_adapter import MapAdapter

from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default
from digraphx.tiny_digraph import DiGraphAdapter

DEFAULT_COST = 1
DEFAULT_TIME = 1
NO_CYCLE_COST = 1
NO_CYCLE_TIME = 1
SELF_LOOP_COST = 2
SELF_LOOP_TIME = 1
RAW_GRAPH_A1_A2_COST = 7
RAW_GRAPH_A1_A2_TIME = 1
RAW_GRAPH_A0_A2_COST = 5
RAW_GRAPH_A0_A2_TIME = 1
RAW_GRAPH_A1_A0_COST = 0
RAW_GRAPH_A1_A0_TIME = 1
RAW_GRAPH_A1_A2_COST_2 = 3
RAW_GRAPH_A1_A2_TIME_2 = 1
RAW_GRAPH_A2_A1_COST = 1
RAW_GRAPH_A2_A1_TIME = 1
RAW_GRAPH_A2_A0_COST = 2
RAW_GRAPH_A2_A0_TIME = 1
TEST_CASE_1_COST = 5
TIMING_A1_A2_COST = 7
TIMING_A2_A1_COST = -1
TIMING_A2_A3_COST = 3
TIMING_A3_A2_COST = 0
TIMING_A3_A1_COST = 2
TIMING_A1_A3_COST = 4
TINY_GRAPH_0_1_COST = 7
TINY_GRAPH_1_0_COST = -1
TINY_GRAPH_1_2_COST = 3
TINY_GRAPH_2_1_COST = 0
TINY_GRAPH_2_0_COST = 2
TINY_GRAPH_0_2_COST = 4


@pytest.fixture
def solver(digraph):
    dist = {vtx: 0 for vtx in digraph}
    return MinCycleRatioSolver(digraph), dist


def test_cycle_ratio_no_cycle(high_ratio):
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 1, cost=NO_CYCLE_COST, time=NO_CYCLE_TIME)
    digraph.add_edge(1, 2, cost=NO_CYCLE_COST, time=NO_CYCLE_TIME)
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert not cycle


def test_cycle_ratio_self_loop(high_ratio):
    digraph = DiGraphAdapter()
    digraph.add_edge(0, 0, cost=SELF_LOOP_COST, time=SELF_LOOP_TIME)
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert ratio == Fraction(SELF_LOOP_COST, SELF_LOOP_TIME)
    assert cycle


def test_cycle_ratio_raw(high_ratio):
    digraph = {
        "a0": {
            "a1": {"cost": RAW_GRAPH_A1_A2_COST, "time": RAW_GRAPH_A1_A2_TIME},
            "a2": {"cost": RAW_GRAPH_A0_A2_COST, "time": RAW_GRAPH_A0_A2_TIME},
        },
        "a1": {
            "a0": {"cost": RAW_GRAPH_A1_A0_COST, "time": RAW_GRAPH_A1_A0_TIME},
            "a2": {"cost": RAW_GRAPH_A1_A2_COST_2, "time": RAW_GRAPH_A1_A2_TIME_2},
        },
        "a2": {
            "a1": {"cost": RAW_GRAPH_A2_A1_COST, "time": RAW_GRAPH_A2_A1_TIME},
            "a0": {"cost": RAW_GRAPH_A2_A0_COST, "time": RAW_GRAPH_A2_A0_TIME},
        },
    }
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(RAW_GRAPH_A2_A0_COST, RAW_GRAPH_A2_A0_TIME)


def test_cycle_ratio(create_test_case1, high_ratio):
    digraph = create_test_case1
    set_default(digraph, "time", DEFAULT_TIME)
    set_default(digraph, "cost", DEFAULT_COST)
    digraph[1][2]["cost"] = TEST_CASE_1_COST
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing(create_test_case_timing, high_ratio):
    digraph = create_test_case_timing
    set_default(digraph, "time", DEFAULT_TIME)
    digraph["a1"]["a2"]["cost"] = TIMING_A1_A2_COST
    digraph["a2"]["a1"]["cost"] = TIMING_A2_A1_COST
    digraph["a2"]["a3"]["cost"] = TIMING_A2_A3_COST
    digraph["a3"]["a2"]["cost"] = TIMING_A3_A2_COST
    digraph["a3"]["a1"]["cost"] = TIMING_A3_A1_COST
    digraph["a1"]["a3"]["cost"] = TIMING_A1_A3_COST
    # make sure no parallel edges in above!!!
    dist = {vtx: Fraction(0, 1) for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(1, 1)


def test_cycle_ratio_tiny_graph(create_tiny_graph, high_ratio):
    digraph = create_tiny_graph
    set_default(digraph, "time", DEFAULT_TIME)
    digraph[0][1]["cost"] = TINY_GRAPH_0_1_COST
    digraph[1][0]["cost"] = TINY_GRAPH_1_0_COST
    digraph[1][2]["cost"] = TINY_GRAPH_1_2_COST
    digraph[2][1]["cost"] = TINY_GRAPH_2_1_COST
    digraph[2][0]["cost"] = TINY_GRAPH_2_0_COST
    digraph[0][2]["cost"] = TINY_GRAPH_0_2_COST
    # make sure no parallel edges in above!!!
    dist = MapAdapter([0 for _ in range(3)])
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(1, 1)
