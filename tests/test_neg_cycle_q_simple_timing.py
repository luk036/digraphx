from typing import Any, Dict

from digraphx.neg_cycle_q import NegCycleFinderQ


def _always_ok(d: Any, v: Any) -> bool:
    return True


def has_negative_cycle(TCP: float, dist: Dict[str, float]) -> bool:
    """Creates a test graph for timing tests."""
    digraph: Dict[str, Dict[str, float]] = {
        "v1": {"v2": TCP - 2, "v3": 1.5},
        "v2": {"v3": TCP - 3, "v1": 2},
        "v3": {"v1": TCP - 4, "v2": 3},
    }
    finder: NegCycleFinderQ[str, float, float] = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


def test_simple_timing_example1() -> None:
    """Creates a test graph for timing tests."""
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(4.0, dist) is False


def test_simple_timing_example2() -> None:
    """Creates a test graph for timing tests."""
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(2.0, dist) is True


def test_simple_timing_example3() -> None:
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(3.0, dist) is False
    assert dist == {"v1": 0, "v2": 1, "v3": 1}
