"""Additional tests for min_cycle_ratio module edge cases."""

from fractions import Fraction
from typing import Any, Dict

from digraphx.min_cycle_ratio import CycleRatioAPI, MinCycleRatioSolver, set_default


def test_set_default_missing_weight() -> None:
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5}},
        "b": {"c": {"cost": 3}},
    }
    set_default(digraph, "time", 1)
    assert digraph["a"]["b"]["time"] == 1
    assert digraph["b"]["c"]["time"] == 1
    assert digraph["a"]["b"]["cost"] == 5


def test_set_default_existing_weight_not_overwritten() -> None:
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "a": {"b": {"cost": 5, "time": 2}},
    }
    set_default(digraph, "time", 1)
    assert digraph["a"]["b"]["time"] == 2


def test_set_default_empty_graph() -> None:
    digraph: Dict[str, Any] = {}
    set_default(digraph, "time", 1)  # Should not raise


def test_cycle_ratio_api_distance() -> None:
    digraph = {"a": {"b": {"cost": 10, "time": 2}}}
    api = CycleRatioAPI(digraph, Fraction)
    result = api.distance(Fraction(1, 2), digraph["a"]["b"])
    assert result == Fraction(10 - 1, 1)  # 10 - 0.5*2 = 9


def test_cycle_ratio_api_zero_cancel() -> None:
    digraph = {"a": {"b": {"cost": 5, "time": 1}}}
    api = CycleRatioAPI(digraph, Fraction)
    cycle = [digraph["a"]["b"]]
    result = api.zero_cancel(cycle)
    assert result == Fraction(5, 1)


def test_min_cycle_ratio_solver_basic() -> None:
    digraph: Dict[str, Dict[str, Dict[str, int]]] = {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }
    solver = MinCycleRatioSolver(digraph)
    dist = {node: Fraction(0) for node in digraph}
    ratio, cycle = solver.run(dist, Fraction(10))
    assert ratio == Fraction(2, 1)
    assert len(cycle) > 0


def test_neg_cycle_finder_cycle_list_with_pred() -> None:
    from mywheel.map_adapter import MapAdapter

    from digraphx.neg_cycle import NegCycleFinder

    digraph = MapAdapter(
        [
            {1: "e01", 2: "e02"},
            {2: "e12"},
            {0: "e20"},
        ]
    )
    finder = NegCycleFinder(digraph)
    finder.pred = {1: (0, "e01"), 2: (1, "e12"), 0: (2, "e20")}
    cycle = finder.cycle_list(0)
    assert len(cycle) == 3
    assert "e20" in cycle


def test_neg_cycle_finder_howard_no_cycles() -> None:
    from mywheel.map_adapter import MapAdapter

    from digraphx.neg_cycle import NegCycleFinder

    digraph = MapAdapter(
        [
            {1: 10},
            {2: 20},
            {},
        ]
    )
    dist = MapAdapter([0, 0, 0])
    finder = NegCycleFinder(digraph)
    cycles = list(finder.howard(dist, lambda e: e))
    assert len(cycles) == 0
