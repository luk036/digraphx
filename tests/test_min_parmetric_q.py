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

    def zero_cancel(self, cycle: Cycle[Dict[str, int]]) -> Fraction:
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


def test_min_parametric_q_with_negative_cycle() -> None:
    """Test with a graph that has a negative cycle."""
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": -5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": 1, "time": 1}},
    }
    dist: Dict[str, float] = {vtx: 0.0 for vtx in digraph}
    solver: MinParametricSolver[str, Dict[str, int], Fraction, float] = (
        MinParametricSolver(digraph, MyAPI())
    )
    ratio, cycle = solver.run(dist, Fraction(-10), lambda D, d: D > d)
    # The ratio should be at least the initial value
    assert ratio >= Fraction(-10)


def test_min_parametric_q_with_pick_one_only() -> None:
    """Test with pick_one_only parameter set to True."""
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}, "c": {"cost": 3, "time": 1}},
        "b": {"a": {"cost": -2, "time": 1}},
        "c": {"a": {"cost": -1, "time": 1}},
    }
    dist: Dict[str, float] = {vtx: 0.0 for vtx in digraph}
    solver: MinParametricSolver[str, Dict[str, int], Fraction, float] = (
        MinParametricSolver(digraph, MyAPI())
    )
    ratio, cycle = solver.run(
        dist, Fraction(-5), lambda D, d: D > d, pick_one_only=True
    )
    assert ratio >= Fraction(-5)


def test_min_parametric_q_with_float_ratio() -> None:
    """Test with float ratio type."""

    class FloatAPI(MinParametricAPI[Node, Dict[str, int], float]):
        def distance(self, ratio: float, edge: Dict[str, int]) -> float:
            return edge["cost"] - ratio * edge["time"]

        def zero_cancel(self, cycle: Cycle[Dict[str, int]]) -> float:
            total_cost = sum(edge["cost"] for edge in cycle)
            total_time = sum(edge["time"] for edge in cycle)
            return total_cost / total_time if total_time != 0 else float("inf")

    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": 2, "time": 1}},
    }
    dist: Dict[str, float] = {vtx: 0.0 for vtx in digraph}
    solver: MinParametricSolver[str, Dict[str, int], float, float] = (
        MinParametricSolver(digraph, FloatAPI())
    )
    ratio, cycle = solver.run(dist, 0.0, lambda D, d: D > d)
    assert isinstance(ratio, float)


def test_min_parametric_q_complex_graph() -> None:
    """Test with a more complex graph."""
    digraph: Dict[int, Dict[int, Dict[str, int]]] = {
        0: {1: {"cost": 4, "time": 1}, 2: {"cost": 2, "time": 1}},
        1: {2: {"cost": 5, "time": 1}, 3: {"cost": 10, "time": 2}},
        2: {0: {"cost": 3, "time": 1}, 3: {"cost": 4, "time": 1}},
        3: {0: {"cost": 8, "time": 2}},
    }
    dist: Dict[int, float] = {vtx: 0.0 for vtx in digraph}
    solver: MinParametricSolver[int, Dict[str, int], Fraction, float] = (
        MinParametricSolver(digraph, MyAPI())
    )
    ratio, cycle = solver.run(dist, Fraction(-5), lambda D, d: D > d)
    assert ratio >= Fraction(-5)
