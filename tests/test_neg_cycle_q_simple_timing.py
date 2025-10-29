from digraphx.neg_cycle_q import NegCycleFinderQ
from pytest import approx
from typing import Any, Callable, Dict, Tuple


MAX_ITERS = 2000
TOLERANCE = 1e-14


def _always_ok(d, v):
    return True


class Options:
    max_iters: int = MAX_ITERS
    tolerance: float = TOLERANCE


def create_graph(tcp: float, beta: float = 0.0, prop: bool = False) -> Dict:
    if prop:
        return {
            "v1": {"v2": tcp - 2 - beta * 3.1, "v3": 1.5 - beta * 0.7},
            "v2": {"v3": tcp - 3 - beta * 4.1, "v1": 2 - beta * 2.2},
            "v3": {"v1": tcp - 4 - beta * 5.1, "v2": 3 - beta * 1.5},
        }
    return {
        "v1": {"v2": tcp - 2 - beta, "v3": 1.5 - beta},
        "v2": {"v3": tcp - 3 - beta, "v1": 2 - beta},
        "v3": {"v1": tcp - 4 - beta, "v2": 3 - beta},
    }


def has_negative_cycle(digraph, dist):
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


def test_simple_timing_example1():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    digraph = create_graph(4.0)
    assert not has_negative_cycle(digraph, dist)


def test_simple_timing_example2():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    digraph = create_graph(2.0)
    assert has_negative_cycle(digraph, dist)


def test_simple_timing_example3():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    digraph = create_graph(3.0)
    assert not has_negative_cycle(digraph, dist)
    assert dist == {"v1": 0, "v2": 1, "v3": 1}


class MyBSOracle:
    def __init__(self, dist, assessment_fn: Callable):
        self.dist = dist
        self.assessment_fn = assessment_fn

    def assess_bs(self, *args, **kwargs):
        return self.assessment_fn(*args, **kwargs)


def bsearch(omega, intrvl, options=Options()) -> Tuple[Any, int]:
    lower, upper = intrvl
    T = type(upper)
    for niter in range(options.max_iters):
        tau = (upper - lower) / 2
        if tau < options.tolerance:
            return upper, niter
        gamma = T(lower + tau)
        if omega.assess_bs(gamma, omega.dist):
            upper = gamma
        else:
            lower = gamma
    return upper, options.max_iters


def test_minimize_TCP():
    dist = {"v1": 0, "v2": 0, "v3": 0}

    def assessment(tcp, dist):
        digraph = create_graph(tcp)
        return not has_negative_cycle(digraph, dist)

    omega = MyBSOracle(dist, assessment)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, [2.0, 4.0], options)
    assert opt == approx(3.0)
    assert num_iter <= 50


def test_maximize_slack():
    dist = {"v1": 0, "v2": 0, "v3": 0}

    def assessment(beta, dist):
        digraph = create_graph(4.5, beta)
        return has_negative_cycle(digraph, dist)

    omega = MyBSOracle(dist, assessment)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, [0, 10.0], options)
    assert opt == approx(1.0)
    assert num_iter <= 50


def test_maximize_effective_slack():
    dist = {"v1": 0, "v2": 0, "v3": 0}

    def assessment(beta, dist):
        digraph = create_graph(4.5, beta, prop=True)
        return has_negative_cycle(digraph, dist)

    omega = MyBSOracle(dist, assessment)
    options = Options()
    options.tolerance = TOLERANCE
    opt, num_iter = bsearch(omega, [0, 10.0], options)
    assert opt == approx(0.3448275862069039)
    assert num_iter <= 50
