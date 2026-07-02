"""Tests for the min_parametric_q module."""

from fractions import Fraction
from typing import Dict, List

from digraphx.min_parametric_q import MinParametricAPI, MinParametricSolver


class TestMinAPI(MinParametricAPI[str, Dict[str, int], Fraction]):
    """Test implementation of MinParametricAPI."""

    def distance(self, ratio: Fraction, edge: Dict[str, int]) -> Fraction:
        return Fraction(edge["cost"] - ratio * edge["time"])

    def zero_cancel(self, cycle: List[Dict[str, int]]) -> Fraction:
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return Fraction(total_cost, total_time)


def _update_ok(current: Fraction, new: Fraction) -> bool:
    return True


def test_min_parametric_solver_init() -> None:
    digraph = {"a": {"b": {"cost": 5, "time": 1}}}
    omega = TestMinAPI()
    solver = MinParametricSolver(digraph, omega)
    assert solver.digraph == digraph
    assert solver.omega == omega


def test_min_parametric_solver_run_basic() -> None:
    digraph = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }
    omega = TestMinAPI()
    solver = MinParametricSolver(digraph, omega)
    dist = {node: Fraction(0) for node in digraph}
    ratio, cycle = solver.run(dist, Fraction(1), _update_ok)
    assert isinstance(ratio, Fraction)
    assert isinstance(cycle, list)


def test_min_parametric_solver_pick_one() -> None:
    digraph = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }
    omega = TestMinAPI()
    solver = MinParametricSolver(digraph, omega)
    dist = {node: Fraction(0) for node in digraph}
    ratio, cycle = solver.run(dist, Fraction(1), _update_ok, pick_one_only=True)
    assert isinstance(ratio, Fraction)


def test_min_parametric_solver_no_cycles() -> None:
    digraph = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {},
    }
    omega = TestMinAPI()
    solver = MinParametricSolver(digraph, omega)
    dist = {node: Fraction(0) for node in digraph}
    ratio, cycle = solver.run(dist, Fraction(10), _update_ok)
    assert ratio == Fraction(10)
    assert cycle == []


def test_min_parametric_solver_float() -> None:
    class FloatMinAPI(MinParametricAPI[str, Dict[str, int], float]):
        def distance(self, ratio: float, edge: Dict[str, int]) -> float:
            return edge["cost"] - ratio * edge["time"]

        def zero_cancel(self, cycle: List[Dict[str, int]]) -> float:
            total_cost = sum(edge["cost"] for edge in cycle)
            total_time = sum(edge["time"] for edge in cycle)
            return total_cost / total_time if total_time != 0 else 0.0

    def float_update_ok(current: float, new: float) -> bool:
        return True

    digraph = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }
    omega = FloatMinAPI()
    solver = MinParametricSolver(digraph, omega)
    dist = {node: 0.0 for node in digraph}
    ratio, cycle = solver.run(dist, 10.0, float_update_ok)
    assert isinstance(ratio, float)
    assert isinstance(cycle, list)
