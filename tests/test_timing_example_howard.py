from pytest import approx

from digraphx.neg_cycle import NegCycleFinder


def find_beta(digraph, beta, dist, make_weight_fn, get_new_beta_fn, max_iter=2000):
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
        get_new_beta_fn (callable): A function that takes a negative cycle
            (a list of edges) and returns the new `beta` value.
        max_iter (int, optional): The maximum number of iterations.
            Defaults to 2000.

    Returns:
        tuple: A tuple containing the final `beta` value and the number of
        iterations performed.
    """
    finder = NegCycleFinder(digraph)
    num_iter = 0
    while num_iter < max_iter:
        num_iter += 1
        weight_fn = make_weight_fn(beta)
        cycle_found = False
        for neg_cycle in finder.howard(dist, weight_fn):
            beta = get_new_beta_fn(neg_cycle)
            cycle_found = True
            break
        if not cycle_found:
            return beta, num_iter
    return beta, max_iter


def even(digraph, beta, dist, max_iter=2000):
    return find_beta(
        digraph,
        beta,
        dist,
        lambda b: (lambda edge: edge - b),
        lambda neg_cycle: sum(neg_cycle) / len(neg_cycle),
        max_iter,
    )


def test_even():
    TCP = 7.5
    digraph = {
        "v0": {"v3": TCP - 6, "v2": TCP - 7},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": 6, "v1": 6, "v3": TCP - 6},
        "v3": {"v4": TCP - 8, "v0": 6, "v2": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    beta, num_iter = even(digraph, 10, dist)
    assert num_iter < 5
    assert beta == approx(1.0)


def prop(digraph, beta, dist, max_iter=2000):
    return find_beta(
        digraph,
        beta,
        dist,
        lambda b: (lambda edge: edge["cost"] - b * edge["time"]),
        lambda neg_cycle: sum(edge["cost"] for edge in neg_cycle)
        / sum(edge["time"] for edge in neg_cycle),
        max_iter,
    )


def test_prop():
    TCP = 7.5
    digraph = {
        "v0": {
            "v3": {"cost": TCP - 6, "time": 3.1},
            "v2": {"cost": TCP - 7, "time": 1.5},
        },
        "v1": {"v2": {"cost": TCP - 9, "time": 4.1}, "v4": {"cost": 3, "time": 1.0}},
        "v2": {
            "v0": {"cost": 6, "time": 3.1},
            "v1": {"cost": 6, "time": 2.5},
            "v3": {"cost": TCP - 6, "time": 3.1},
        },
        "v3": {
            "v4": {"cost": TCP - 8, "time": 4.1},
            "v0": {"cost": 6, "time": 2.5},
            "v2": {"cost": 6, "time": 2.5},
        },
        "v4": {"v1": {"cost": TCP - 3, "time": 1.1}, "v3": {"cost": 8, "time": 1.5}},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    beta, num_iter = prop(digraph, 10, dist)
    assert num_iter < 5
    assert beta == approx(0.32258064516129037)
    # assert dist == {"v1": -1, "v2": 0, "v3": 0}
