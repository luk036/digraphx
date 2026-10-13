from typing import Any, Dict

from pytest import approx

from digraphx.css import cprop, css_ratio, even, min_clock_period, prop


def test_min_clock_period() -> None:
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v1": {"v2": {"type": "s", "delay": 7.0}, "v3": {"type": "h", "delay": 2.0}},
        "v2": {"v1": {"type": "h", "delay": 4.0}, "v3": {"type": "p", "delay": 0.0}},
        "v3": {"v1": {"type": "s", "delay": 3.0}},
    }
    dist: Dict[str, float] = {"v1": 0.0, "v2": 0.0, "v3": 0.0}
    period, cycle = min_clock_period(digraph, dist)
    assert cycle
    assert period == approx(5.0)


def test_even_weights() -> None:
    TCP = 7.5
    digraph: Dict[str, Dict[str, float]] = {
        "v0": {"v2": 6.0, "v3": 6.0},
        "v1": {"v2": 6.0, "v4": TCP - 3.0},
        "v2": {"v0": TCP - 7.0, "v1": TCP - 9.0, "v3": 6.0},
        "v3": {"v4": 8.0, "v2": TCP - 6.0, "v0": TCP - 6.0},
        "v4": {"v3": TCP - 8.0, "v1": 3.0},
    }
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    beta, _ = css_ratio(digraph, dist, 10.0, cost_time=lambda e: (e, 1.0))
    assert beta == approx(1.0)


def test_even() -> None:
    TCP = 6.5
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v1": {
            "v2": {"type": "s", "delay": TCP - 7.0},
            "v3": {"type": "h", "delay": 2.0},
        },
        "v2": {"v1": {"type": "h", "delay": 4.0}, "v3": {"type": "p", "delay": 0.0}},
        "v3": {"v1": {"type": "s", "delay": TCP - 3.0}},
    }
    dist: Dict[str, float] = {"v1": 0.0, "v2": 0.0, "v3": 0.0}
    beta, _ = even(digraph, dist, 10.0)
    assert beta == approx(1.5)


def test_even_multi_node() -> None:
    TCP = 7.5
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v0": {"v2": {"type": "h", "delay": 6.0}, "v3": {"type": "h", "delay": 6.0}},
        "v1": {"v2": {"type": "h", "delay": 6.0}, "v5": {"type": "p", "delay": 0.0}},
        "v2": {
            "v0": {"type": "s", "delay": TCP - 7.0},
            "v1": {"type": "s", "delay": TCP - 9.0},
            "v3": {"type": "s", "delay": 6.0},
        },
        "v3": {
            "v4": {"type": "h", "delay": 8.0},
            "v2": {"type": "s", "delay": TCP - 6.0},
            "v0": {"type": "s", "delay": TCP - 6.0},
        },
        "v4": {
            "v3": {"type": "s", "delay": TCP - 8.0},
            "v5": {"type": "h", "delay": 3.0},
        },
        "v5": {"v4": {"type": "s", "delay": TCP - 3.0}},
    }
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    beta, _ = even(digraph, dist, 10.0)
    assert beta == approx(1.0)


def test_prop() -> None:
    TCP = 7.5
    digraph: Dict[str, Dict[str, Dict[str, float]]] = {
        "v0": {"v3": {"cost": 6.0, "time": 2.5}, "v2": {"cost": 6.0, "time": 3.1}},
        "v1": {
            "v2": {"cost": 6.0, "time": 2.5},
            "v4": {"cost": TCP - 3.0, "time": 1.1},
        },
        "v2": {
            "v0": {"cost": TCP - 7.0, "time": 1.5},
            "v1": {"cost": TCP - 9.0, "time": 4.1},
            "v3": {"cost": 6.0, "time": 2.5},
        },
        "v3": {
            "v0": {"cost": TCP - 6.0, "time": 3.1},
            "v2": {"cost": TCP - 6.0, "time": 3.1},
            "v4": {"cost": 8.0, "time": 1.5},
        },
        "v4": {
            "v1": {"cost": 3.0, "time": 1.0},
            "v3": {"cost": TCP - 8.0, "time": 4.1},
        },
    }
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    beta, _ = prop(digraph, dist, 10.0)
    assert beta == approx(0.32258064516129037)


def test_cprop() -> None:
    digraph: Dict[str, Dict[str, Dict[str, float]]] = {
        "a": {"b": {"mu": 4.0, "sigma": 1.0}},
        "b": {"a": {"mu": 2.0, "sigma": 1.0}},
    }
    dist: Dict[str, float] = {"a": 0.0, "b": 0.0}
    beta, _ = cprop(digraph, dist, 10.0)
    assert beta == approx(3.0)


def test_min_clock_period_alt() -> None:
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v1": {"v2": {"type": "s", "delay": 2.0}, "v3": {"type": "h", "delay": 1.5}},
        "v2": {"v3": {"type": "s", "delay": 3.0}, "v1": {"type": "h", "delay": 2.0}},
        "v3": {"v1": {"type": "s", "delay": 4.0}, "v2": {"type": "h", "delay": 3.0}},
    }
    dist: Dict[str, float] = {"v1": 0.0, "v2": 0.0, "v3": 0.0}
    period, cycle = min_clock_period(digraph, dist)
    assert cycle
    assert period == approx(3.0)


def test_prop_alt() -> None:
    TCP = 4.5
    digraph: Dict[str, Dict[str, Dict[str, float]]] = {
        "v1": {
            "v2": {"cost": TCP - 2.0, "time": 3.1},
            "v3": {"cost": 1.5, "time": 0.7},
        },
        "v2": {
            "v3": {"cost": TCP - 3.0, "time": 4.1},
            "v1": {"cost": 2.0, "time": 2.2},
        },
        "v3": {
            "v1": {"cost": TCP - 4.0, "time": 5.1},
            "v2": {"cost": 3.0, "time": 1.5},
        },
    }
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    beta, _ = prop(digraph, dist, 10.0)
    assert beta == approx(0.3448275862069039)


def test_min_clock_period_ratio_graph() -> None:
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v0": {"v3": {"type": "s", "delay": 6.0}, "v2": {"type": "s", "delay": 7.0}},
        "v1": {"v2": {"type": "s", "delay": 9.0}, "v4": {"type": "h", "delay": 3.0}},
        "v2": {
            "v0": {"type": "h", "delay": 6.0},
            "v1": {"type": "h", "delay": 6.0},
            "v3": {"type": "s", "delay": 6.0},
        },
        "v3": {
            "v4": {"type": "s", "delay": 8.0},
            "v0": {"type": "h", "delay": 6.0},
            "v2": {"type": "h", "delay": 6.0},
        },
        "v4": {"v1": {"type": "s", "delay": 3.0}, "v3": {"type": "h", "delay": 8.0}},
    }
    dist: Dict[str, float] = {v: 0.0 for v in digraph}
    period, cycle = min_clock_period(digraph, dist)
    assert cycle
    assert period == approx(6.5)
