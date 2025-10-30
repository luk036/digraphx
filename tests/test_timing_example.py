from typing import Dict

import pytest

from digraphx.neg_cycle import NegCycleFinder


def create_graph(TCP: float) -> Dict[str, Dict[str, float]]:
    """Create a test graph with TCP-dependent edge weights."""
    return {
        "v0": {"v3": TCP - 6, "v2": TCP - 7},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": 6, "v1": 6, "v3": TCP - 6},
        "v3": {"v4": TCP - 8, "v0": 6, "v2": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }


def has_negative_cycle(
    digraph: Dict[str, Dict[str, float]], dist: Dict[str, float]
) -> bool:
    """Check for negative cycles in the graph."""
    finder: NegCycleFinder[str, float, float] = NegCycleFinder(digraph)
    return any(finder.howard(dist, lambda edge: edge))


@pytest.mark.parametrize(
    "tcp, expected_result",
    [
        (10.0, False),
        (5.0, True),
        (7.0, False),
    ],
)
def test_negative_cycle_detection(tcp: float, expected_result: bool) -> None:
    """Test for negative cycles with different TCP values."""
    dist: Dict[str, float] = {f"v{i}": 0 for i in range(5)}
    digraph = create_graph(tcp)
    assert has_negative_cycle(digraph, dist) is expected_result


def test_distance_updates() -> None:
    """Test that the distances are correctly updated."""
    dist: Dict[str, float] = {f"v{i}": 0 for i in range(5)}
    digraph = create_graph(7.0)
    has_negative_cycle(digraph, dist)
    assert dist == {"v0": 0, "v1": 0, "v2": -2.0, "v3": -1, "v4": -2}
