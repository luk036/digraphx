from typing import Any, Callable, Dict, List, Tuple

from pytest import approx

from digraphx.neg_cycle import NegCycleFinder


def find_beta(
    digraph: Dict[str, Dict[str, Any]],
    beta: float,
    dist: Dict[str, float],
    make_weight_fn: Callable[[float], Callable[[Any], float]],
    zero_cancel_fn: Callable[[List[Any]], float],
    max_iter: int = 2000,
) -> Tuple[float, int, Any]:
    """
    Finds the beta value using a fixed-point iteration.

    This function iteratively searches for negative cycles in a directed graph
    and updates a `beta` value based on the cycles found. The process
    continues until no more negative cycles are found or the maximum number of
    iterations is reached.

    Args:
        digraph (dict): The graph to search for negative cycles, represented as
            an adjacency list.
        beta (float): The initial beta value.
        dist (dict): The initial distances to the nodes.
        make_weight_fn (callable): A function that takes the current `beta`
            value and returns a weight function. The weight function, in turn,
            takes an edge and returns its weight.
        zero_cancel_fn (callable): A function that takes a negative cycle
            (a list of edges) and returns the new `beta` value.
        max_iter (int, optional): The maximum number of iterations.
            Defaults to 2000.

    Returns:
        tuple: A tuple containing the final `beta` value and the number of
        iterations performed.
    """
    finder: NegCycleFinder[str, Any, float] = NegCycleFinder(digraph)
    num_iter: int = 0
    critical_cycle: Any = None
    while num_iter < max_iter:
        num_iter += 1
        weight_fn = make_weight_fn(beta)
        cycle_found: bool = False
        for neg_cycle in finder.howard(dist, weight_fn):
            beta_new = zero_cancel_fn(neg_cycle)
            if abs(beta_new - beta) > 1e-6:
                cycle_found = True
            beta = beta_new
            critical_cycle = neg_cycle
            break
        if not cycle_found:
            return beta, num_iter, critical_cycle
    return beta, max_iter, critical_cycle


def even(
    digraph: Dict[str, Dict[str, Any]],
    beta: float,
    dist: Dict[str, float],
    max_iter: int = 2000,
) -> Tuple[float, int, Any]:
    return find_beta(
        digraph,
        beta,
        dist,
        lambda beta: lambda e: e["delay"] - beta if e["type"] != "p" else e["delay"],
        lambda neg_cycle: (
            sum(e["delay"] for e in neg_cycle)
            / sum(1 for e in neg_cycle if e["type"] != "p")
        ),
        max_iter,
    )


def test_even1() -> None:
    TCP: float = 6.5
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v1": {"v2": {"type": "s", "delay": TCP - 7}, "v3": {"type": "h", "delay": 2}},
        "v2": {"v1": {"type": "h", "delay": 4}, "v3": {"type": "p", "delay": 0}},
        "v3": {"v1": {"type": "s", "delay": TCP - 3}},
    }
    dist: Dict[str, float] = {"v1": 0, "v2": 0, "v3": 0}
    beta, num_iter, _ = even(digraph, 10, dist)
    assert num_iter < 10
    assert beta == approx(1.5)
    assert dist == {"v1": -17, "v2": -19, "v3": -19}


def test_even2() -> None:
    TCP: float = 7.5
    digraph: Dict[str, Dict[str, Dict[str, Any]]] = {
        "v0": {"v2": {"type": "h", "delay": 6}, "v3": {"type": "h", "delay": 6}},
        "v1": {"v2": {"type": "h", "delay": 6}, "v5": {"type": "p", "delay": 0}},
        "v2": {
            "v0": {"type": "s", "delay": TCP - 7},
            "v1": {"type": "s", "delay": TCP - 9},
            "v3": {"type": "s", "delay": 6},
        },
        "v3": {
            "v4": {"type": "h", "delay": 8},
            "v2": {"type": "s", "delay": TCP - 6},
            "v0": {"type": "s", "delay": TCP - 6},
        },
        "v4": {"v3": {"type": "s", "delay": TCP - 8}, "v5": {"type": "h", "delay": 3}},
        "v5": {"v4": {"type": "s", "delay": TCP - 3}},
    }
    dist: Dict[str, float] = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0, "v5": 0}
    beta, num_iter, _ = even(digraph, 10, dist)
    print("slack02(s) = {}".format(TCP - 7 + dist["v2"] - dist["v0"]))
    print("slack02(h) = {}".format(6 + dist["v0"] - dist["v2"]))
    print("slack03(s) = {}".format(TCP - 6 + dist["v3"] - dist["v0"]))
    print("slack03(h) = {}".format(6 + dist["v0"] - dist["v3"]))
    print("slack23(s) = {}".format(TCP - 6 + dist["v3"] - dist["v2"]))
    print("slack23(h) = {}".format(6 + dist["v2"] - dist["v3"]))
    print("slack34(s) = {}".format(TCP - 8 + dist["v4"] - dist["v3"]))
    print("slack34(h) = {}".format(8 + dist["v3"] - dist["v4"]))
    print("slack45(s) = {}".format(TCP - 3 + dist["v5"] - dist["v4"]))
    print("slack45(h) = {}".format(3 + dist["v4"] - dist["v5"]))
    print("slack12(s) = {}".format(TCP - 9 + dist["v2"] - dist["v1"]))
    print("slack12(h) = {}".format(6 + dist["v1"] - dist["v2"]))
    print(dist["v5"])
    print(dist["v1"])
    assert num_iter < 10
    assert beta == approx(1.0)
