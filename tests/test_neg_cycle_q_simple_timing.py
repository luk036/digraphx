from digraphx.neg_cycle_q import NegCycleFinderQ


def _always_ok(d, v):
    return True


def has_negative_cycle(TCP, dist):
    """Creates a test graph for timing tests."""
    digraph = {
        "v1": {"v2": TCP - 2, "v3": 1.5},
        "v2": {"v3": TCP - 3, "v1": 2},
        "v3": {"v1": TCP - 4, "v2": 3},
    }
    finder = NegCycleFinderQ(digraph)
    for _ in finder.howard_succ(dist, lambda edge: edge, _always_ok):
        return True
    return False


def test_simple_timing_example1():
    """Creates a test graph for timing tests."""
    dist = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(4.0, dist) is False


def test_simple_timing_example2():
    """Creates a test graph for timing tests."""
    dist = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(2.0, dist) is True


def test_simple_timing_example3():
    dist = {"v1": 0, "v2": 0, "v3": 0}
    assert has_negative_cycle(3.0, dist) is False
    assert dist == {"v1": 0, "v2": 1, "v3": 1}
