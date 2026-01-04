# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction
from typing import Any, Dict, Tuple, Union

import pytest
from mywheel.map_adapter import MapAdapter

from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph

DEFAULT_COST: int = 1
DEFAULT_TIME: int = 1
NO_CYCLE_COST: int = 1
NO_CYCLE_TIME: int = 1
SELF_LOOP_COST: int = 2
SELF_LOOP_TIME: int = 1
RAW_GRAPH_A1_A2_COST: int = 7
RAW_GRAPH_A1_A2_TIME: int = 1
RAW_GRAPH_A0_A2_COST: int = 5
RAW_GRAPH_A0_A2_TIME: int = 1
RAW_GRAPH_A1_A0_COST: int = 0
RAW_GRAPH_A1_A0_TIME: int = 1
RAW_GRAPH_A1_A2_COST_2: int = 3
RAW_GRAPH_A1_A2_TIME_2: int = 1
RAW_GRAPH_A2_A1_COST: int = 1
RAW_GRAPH_A2_A1_TIME: int = 1
RAW_GRAPH_A2_A0_COST: int = 2
RAW_GRAPH_A2_A0_TIME: int = 1
TEST_CASE_1_COST: int = 5
TIMING_A1_A2_COST: int = 7
TIMING_A2_A1_COST: int = -1
TIMING_A2_A3_COST: int = 3
TIMING_A3_A2_COST: int = 0
TIMING_A3_A1_COST: int = 2
TIMING_A1_A3_COST: int = 4
TINY_GRAPH_0_1_COST: int = 7
TINY_GRAPH_1_0_COST: int = -1
TINY_GRAPH_1_2_COST: int = 3
TINY_GRAPH_2_1_COST: int = 0
TINY_GRAPH_2_0_COST: int = 2
TINY_GRAPH_0_2_COST: int = 4


@pytest.fixture
def solver(
    digraph: Union[DiGraphAdapter, TinyDiGraph, Dict[str, Dict[str, Any]]],
) -> Tuple[MinCycleRatioSolver[Any, Any, Any], Union[Dict[Any, int], MapAdapter[Any]]]:
    dist: Dict[Any, int] = {vtx: 0 for vtx in digraph}
    return MinCycleRatioSolver(digraph), dist  # type: ignore


def test_cycle_ratio_no_cycle(high_ratio: Fraction) -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, cost=NO_CYCLE_COST, time=NO_CYCLE_TIME)
    digraph.add_edge(1, 2, cost=NO_CYCLE_COST, time=NO_CYCLE_TIME)
    dist: Dict[Any, int] = {vtx: 0 for vtx in digraph}
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert not cycle


def test_cycle_ratio_self_loop(high_ratio: Fraction) -> None:
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 0, cost=SELF_LOOP_COST, time=SELF_LOOP_TIME)
    dist: Dict[Any, int] = {vtx: 0 for vtx in digraph}
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert ratio == Fraction(SELF_LOOP_COST, SELF_LOOP_TIME)
    assert cycle


def test_cycle_ratio_raw(high_ratio: Fraction) -> None:
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
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
    dist: Dict[str, int] = {vtx: 0 for vtx in digraph}
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)  # type: ignore
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(RAW_GRAPH_A2_A0_COST, RAW_GRAPH_A2_A0_TIME)


def test_cycle_ratio(create_test_case1: DiGraphAdapter, high_ratio: Fraction) -> None:
    digraph: DiGraphAdapter = create_test_case1
    set_default(digraph, "time", DEFAULT_TIME)
    set_default(digraph, "cost", DEFAULT_COST)
    digraph[1][2]["cost"] = TEST_CASE_1_COST
    dist: Dict[Any, int] = {vtx: 0 for vtx in digraph}
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing(
    create_test_case_timing: DiGraphAdapter, high_ratio: Fraction
) -> None:
    digraph: DiGraphAdapter = create_test_case_timing
    set_default(digraph, "time", DEFAULT_TIME)
    digraph["a1"]["a2"]["cost"] = TIMING_A1_A2_COST
    digraph["a2"]["a1"]["cost"] = TIMING_A2_A1_COST
    digraph["a2"]["a3"]["cost"] = TIMING_A2_A3_COST
    digraph["a3"]["a2"]["cost"] = TIMING_A3_A2_COST
    digraph["a3"]["a1"]["cost"] = TIMING_A3_A1_COST
    digraph["a1"]["a3"]["cost"] = TIMING_A1_A3_COST
    # make sure no parallel edges in above!!!
    dist: Dict[Any, Fraction] = {vtx: Fraction(0, 1) for vtx in digraph}
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)
    assert cycle
    assert ratio == Fraction(1, 1)


def test_cycle_ratio_tiny_graph(
    create_tiny_graph: TinyDiGraph, high_ratio: Fraction
) -> None:
    digraph: TinyDiGraph = create_tiny_graph
    set_default(digraph, "time", DEFAULT_TIME)
    digraph[0][1]["cost"] = TINY_GRAPH_0_1_COST
    digraph[1][0]["cost"] = TINY_GRAPH_1_0_COST
    digraph[1][2]["cost"] = TINY_GRAPH_1_2_COST
    digraph[2][1]["cost"] = TINY_GRAPH_2_1_COST
    digraph[2][0]["cost"] = TINY_GRAPH_2_0_COST
    digraph[0][2]["cost"] = TINY_GRAPH_0_2_COST
    # make sure no parallel edges in above!!!
    dist: MapAdapter[int] = MapAdapter([0 for _ in range(3)])
    solver: MinCycleRatioSolver[Any, Any, Any] = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, high_ratio)  # type: ignore
    assert cycle
    assert ratio == Fraction(1, 1)


def test_set_default_with_existing_value() -> None:
    """Test set_default when the weight already exists (missing branch)."""
    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_edge(0, 1, cost=5, time=2)
    digraph.add_edge(1, 2, cost=3)  # No time attribute

    # This should not override existing cost values
    set_default(digraph, "cost", 10)
    assert digraph[0][1]["cost"] == 5  # Should remain unchanged

    # This should add the missing time attribute
    set_default(digraph, "time", 1)
    assert digraph[1][2]["time"] == 1  # Should be set to default
