from digraphx.neg_cycle import NegCycleFinder
from pytest import approx


def even(digraph, beta, dist, max_iter=2000):
    finder = NegCycleFinder(digraph)
    done = False
    num_iter = 0
    while not done and num_iter < max_iter:
        done = True
        for neg_cycle in finder.howard(dist, lambda edge: edge - beta):
            beta = sum(neg_cycle) / len(neg_cycle)
            done = False
            break  # pick only the first one
        num_iter += 1
    return beta, num_iter


def test_even():
    TCP = 7.5
    digraph = {
        "v0": {"v3": TCP - 6, "v2": 6},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": TCP - 7, "v1": 6},
        "v3": {"v4": TCP - 8, "v0": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    beta, num_iter = even(digraph, 10, dist)
    assert num_iter < 5
    assert beta == approx(0.9)


def prop(digraph, beta, dist, max_iter=2000):
    finder = NegCycleFinder(digraph)
    done = False
    num_iter = 0
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


def test_prop():
    TCP = 7.5
    digraph = {
        "v0": {"v3": {"cost": TCP - 6, "time": 3.1}, "v2": {"cost": 6, "time": 1.5}},
        "v1": {"v2": {"cost": TCP - 9, "time": 4.1}, "v4": {"cost": 3, "time": 1.0}},
        "v2": {"v0": {"cost": TCP - 7, "time": 3.1}, "v1": {"cost": 6, "time": 2.5}},
        "v3": {"v4": {"cost": TCP - 8, "time": 4.1}, "v0": {"cost": 6, "time": 2.5}},
        "v4": {"v1": {"cost": TCP - 3, "time": 1.1}, "v3": {"cost": 8, "time": 1.5}},
    }
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    beta, num_iter = prop(digraph, 10, dist)
    assert num_iter < 5
    assert beta == approx(0.290322580645161)
    # assert dist == {"v1": -1, "v2": 0, "v3": 0}
