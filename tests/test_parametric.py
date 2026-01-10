# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction
from typing import Dict

from digraphx.neg_cycle import Cycle, Node
from digraphx.parametric import MaxParametricSolver, ParametricAPI


class TestParametricAPI(ParametricAPI[Node, Dict[str, int], Fraction]):
    """Test implementation of ParametricAPI for testing purposes."""

    def distance(self, ratio: Fraction, edge: Dict[str, int]) -> Fraction:
        """Calculate distance as cost - ratio * time."""
        return Fraction(edge["cost"] - ratio * edge["time"])

    def zero_cancel(self, cycle: Cycle) -> Fraction:
        """Calculate ratio that makes cycle sum to zero."""
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return Fraction(total_cost, total_time)


def test_max_parametric_solver_basic() -> None:
    """Test basic functionality of MaxParametricSolver."""
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }

    omega = TestParametricAPI()
    solver = MaxParametricSolver(digraph, omega)
    dist: Dict[str, Fraction] = {node: Fraction(0) for node in digraph}

    ratio, cycle = solver.run(dist, Fraction(10))

    assert ratio == Fraction(2, 1)
    assert len(cycle) > 0


def test_max_parametric_solver_no_negative_cycles() -> None:
    """Test MaxParametricSolver with graph that has no negative cycles."""
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"d": {"cost": 2, "time": 1}},
        "d": {"a": {"cost": 1, "time": 1}},  # Add edge to make it a complete graph
    }

    omega = TestParametricAPI()
    solver = MaxParametricSolver(digraph, omega)
    dist: Dict[str, Fraction] = {node: Fraction(0) for node in digraph}

    ratio, cycle = solver.run(dist, Fraction(0))

    # With no negative cycles, the ratio should remain at 0
    assert ratio == Fraction(0)
    # The cycle might be empty or not depending on the algorithm
    assert isinstance(cycle, list)


def test_max_parametric_solver_with_float_ratio() -> None:
    """Test MaxParametricSolver with float ratio type."""

    class FloatParametricAPI(ParametricAPI[Node, Dict[str, int], float]):
        def distance(self, ratio: float, edge: Dict[str, int]) -> float:
            return edge["cost"] - ratio * edge["time"]

        def zero_cancel(self, cycle: Cycle) -> float:
            total_cost = sum(edge["cost"] for edge in cycle)
            total_time = sum(edge["time"] for edge in cycle)
            return total_cost / total_time

    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }

    omega = FloatParametricAPI()
    solver = MaxParametricSolver(digraph, omega)
    dist: Dict[str, float] = {node: 0.0 for node in digraph}

    ratio, cycle = solver.run(dist, 10.0)

    assert abs(ratio - 2.0) < 1e-9
    assert len(cycle) > 0


def test_max_parametric_solver_complex_graph() -> None:
    """Test MaxParametricSolver with a more complex graph."""
    digraph: Dict[int, Dict[int, Dict[str, int]]] = {
        0: {1: {"cost": 4, "time": 1}, 2: {"cost": 2, "time": 1}},
        1: {2: {"cost": 5, "time": 1}, 3: {"cost": 10, "time": 2}},
        2: {0: {"cost": 3, "time": 1}, 3: {"cost": 4, "time": 1}},
        3: {0: {"cost": -8, "time": 2}},
    }

    omega = TestParametricAPI()
    solver = MaxParametricSolver(digraph, omega)
    dist: Dict[int, Fraction] = {node: Fraction(0) for node in digraph}

    ratio, cycle = solver.run(dist, Fraction(5))

    # The ratio should be a valid Fraction
    assert isinstance(ratio, Fraction)
    assert isinstance(cycle, list)


def test_max_parametric_solver_initialization() -> None:
    """Test that MaxParametricSolver initializes correctly."""
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {"a": {"b": {"cost": 1, "time": 1}}}
    omega = TestParametricAPI()

    solver = MaxParametricSolver(digraph, omega)

    assert solver.digraph == digraph
    assert solver.omega == omega
