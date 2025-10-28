from digraphx.neg_cycle import NegCycleFinder
from pytest import approx
from typing import Any, Tuple
# from icecream import ic

class Options:
    max_iters: int = 2000  # maximum number of iterations
    tolerance: float = 1e-14  # error tolerance


def has_negative_cycle(TCP, dist):
    """Creates a test graph for timing tests."""
    digraph = {
        "v1": {"v2": TCP - 2, "v3": 1.5},
        "v2": {"v3": TCP - 3, "v1": 2},
        "v3": {"v1": TCP - 4, "v2": 3},
    }
    finder = NegCycleFinder(digraph)
    for _ in finder.howard(dist, lambda edge: edge):
        return True
    return False


def test_simple_timing_example1():
    """Creates a test graph for timing tests."""
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    assert has_negative_cycle(4.0, dist) is False


def test_simple_timing_example2():
    """Creates a test graph for timing tests."""
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    assert has_negative_cycle(2.0, dist) is True


def test_simple_timing_example3():
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    assert has_negative_cycle(3.0, dist) is False
    assert dist == {'v1': -1, 'v2': 0, 'v3': 0}


class MyBSOracle:
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, TCP):
        return not has_negative_cycle(TCP, self.dist)


def bsearch(omega, intrvl, options=Options()) -> Tuple[Any, int]:
    lower, upper = intrvl
    T = type(upper)  # Preserve numerical type (int/float)
    for niter in range(options.max_iters):
        tau = (upper - lower) / 2
        if tau < options.tolerance:  # Convergence check
            return upper, niter
        gamma = T(lower + tau)
        if omega.assess_bs(gamma):
            upper = gamma
        else:  # feasible -> move lower bound up
            lower = gamma
    return upper, options.max_iters


def test_minimize_TCP():
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    omega = MyBSOracle(dist)
    options = Options()
    options.tolerance = 1e-14
    opt, num_iter = bsearch(omega, [2.0, 4.0], options)
    print(opt, num_iter)
    assert opt == approx(3.0)
    assert num_iter <= 50


def has_negative_cycle_EVEN(beta, dist):
    TCP = 4.5
    digraph = {
        "v1": {"v2": TCP - 2 - beta, "v3": 1.5 - beta},
        "v2": {"v3": TCP - 3 - beta, "v1": 2 - beta},
        "v3": {"v1": TCP - 4 - beta, "v2": 3 - beta},
    }
    finder = NegCycleFinder(digraph)
    for _ in finder.howard(dist, lambda edge: edge):
        return True
    return False


class MyBSOracle2:
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, gamma):
        return has_negative_cycle_EVEN(gamma, self.dist)


def test_maximize_slack():
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    omega = MyBSOracle2(dist)
    options = Options()
    options.tolerance = 1e-14
    opt, num_iter = bsearch(omega, [0, 10.0], options)
    print(opt, num_iter)
    assert opt == approx(1.0)
    assert num_iter <= 50


def has_negative_cycle_PROP(beta, dist):
    """Creates a test graph for timing tests."""
    TCP = 4.5
    digraph = {
        "v1": {"v2": TCP - 2 - beta * 3.1, "v3": 1.5 - beta * 0.7},
        "v2": {"v3": TCP - 3 - beta * 4.1, "v1": 2 - beta * 2.2},
        "v3": {"v1": TCP - 4 - beta * 5.1, "v2": 3 - beta * 1.5},
    }
    finder = NegCycleFinder(digraph)
    for _ in finder.howard(dist, lambda edge: edge):
        return True
    return False


class MyBSOracle3:
    def __init__(self, dist):
        self.dist = dist

    def assess_bs(self, gamma):
        return has_negative_cycle_PROP(gamma, self.dist)


def test_maximize_effective_slack():
    dist = {'v1': 0, 'v2': 0, 'v3': 0}
    omega = MyBSOracle3(dist)
    options = Options()
    options.tolerance = 1e-14
    opt, num_iter = bsearch(omega, [0, 10.0], options)
    print(opt, num_iter)
    assert opt == approx(0.3448275862069039)
    assert num_iter <= 50
