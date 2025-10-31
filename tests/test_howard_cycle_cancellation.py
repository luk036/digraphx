from typing import Any, Callable, Dict, List, Tuple

from pytest import approx

from digraphx.neg_cycle import NegCycleFinder


def even(
    digraph: Dict[str, Dict[str, float]],
    beta: float,
    dist: Dict[str, float],
    max_iter: int = 2000,
) -> Tuple[float, int]:
    finder: NegCycleFinder[str, float, float] = NegCycleFinder(digraph)
    done: bool = False
    num_iter: int = 0
    while not done and num_iter < max_iter:
        done = True
        for neg_cycle in finder.howard(dist, lambda edge: edge - beta):
            beta = sum(neg_cycle) / len(neg_cycle)
            done = False
            break  # pick only the first one
        num_iter += 1
    return beta, num_iter


def test_even() -> None:
    TCP: float = 4.5
    digraph: Dict[str, Dict[str, float]] = {
        "v1": {"v2": TCP - 2.0, "v3": 1.5},
        "v2": {"v3": TCP - 3.0, "v1": 2.0},
        "v3": {"v1": TCP - 4.0, "v2": 3.0},
    }
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    beta, num_iter = even(digraph, 10, dist)
    assert num_iter < 4
    assert beta == approx(1.0)


def prop(
    digraph: Dict[str, Dict[str, Dict[str, float]]],
    beta: float,
    dist: Dict[str, float],
    max_iter: int = 2000,
) -> Tuple[float, int]:
    finder: NegCycleFinder[str, Dict[str, float], float] = NegCycleFinder(digraph)
    done: bool = False
    num_iter: int = 0
    while not done and num_iter < max_iter:
        done = True
        for neg_cycle in finder.howard(
            dist, lambda edge: edge["cost"] - beta * edge["time"]
        ):
            beta = sum(edge["cost"] for edge in neg_cycle) / sum(
                edge["time"] for edge in neg_cycle
            )
            done = False
            break  # pick only the first one
        num_iter += 1
    return beta, num_iter


def test_prop() -> None:
    TCP: float = 4.5
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
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    beta, num_iter = prop(digraph, 10, dist)
    assert num_iter < 5
    assert beta == approx(0.3448275862068966)
    # assert dist == {"v1": -1, "v2": 0, "v3": 0}
