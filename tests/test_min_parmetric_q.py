# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction
from typing import Dict

from digraphx.min_parmetric_q import MinParametricAPI, MinParametricSolver
from digraphx.neg_cycle_q import Cycle, Node

# Define type variables for generic programming
# Ratio = TypeVar("Ratio", Fraction, float) # No longer needed here


class MyAPI(MinParametricAPI[Node, Dict[str, int], Fraction]):
    def distance(self, ratio: Fraction, edge: Dict[str, int]) -> Fraction:
        return edge["cost"] - ratio * edge["time"]

    def zero_cancel(self, cycle: Cycle) -> Fraction:
        total_cost: int = sum(edge["cost"] for edge in cycle)
        total_time: int = sum(edge["time"] for edge in cycle)
        return Fraction(total_cost, total_time)


def test_min_parametric_q() -> None:
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a0": {"a1": {"cost": 7, "time": 1}, "a2": {"cost": 5, "time": 1}},
        "a1": {"a0": {"cost": 0, "time": 1}, "a2": {"cost": 3, "time": 1}},
        "a2": {"a1": {"cost": 1, "time": 1}, "a0": {"cost": 2, "time": 1}},
    }
    dist: Dict[str, float] = {vtx: float("inf") for vtx in digraph}
    solver: MinParametricSolver[str, Dict[str, int], Fraction, float] = (
        MinParametricSolver(digraph, MyAPI())
    )
    ratio, cycle = solver.run(dist, Fraction(0), lambda D, d: D > d)
    assert ratio == Fraction(0, 1)
    assert cycle == []
