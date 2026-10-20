"""Parity tests for the unified cost/time parametric API.

``CycleRatioAPI`` and the CSS facades used to be two implementations of
``dist(e, r) = cost(e) - r * time(e)``.  They now share one implementation, so
these tests pin that the two call paths agree and that the zero-time policy is
the documented one rather than a ``ZeroDivisionError``.
"""

from fractions import Fraction

from digraphx.css import css_ratio
from digraphx.min_cycle_ratio import CycleRatioAPI


def _graph():
    return {
        "a": {"b": {"cost": 5, "time": 1}},
        "b": {"c": {"cost": 3, "time": 1}},
        "c": {"a": {"cost": -2, "time": 1}},
    }


def test_cycle_ratio_api_matches_css_ratio() -> None:
    graph = _graph()
    api = CycleRatioAPI(graph, Fraction)
    cycle = [graph["a"]["b"], graph["b"]["c"], graph["c"]["a"]]

    assert api.distance(Fraction(1, 2), graph["a"]["b"]) == Fraction(9, 2)

    dist = {node: 0.0 for node in graph}
    ratio, _ = css_ratio(
        graph, dist, 100.0, cost_time=lambda edge: (edge["cost"], edge["time"])
    )
    assert float(api.zero_cancel(cycle)) == ratio


def test_zero_total_time_yields_infinity() -> None:
    api = CycleRatioAPI(_graph(), Fraction)
    assert api.zero_cancel([{"cost": 7, "time": 0}]) == float("inf")
