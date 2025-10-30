from digraphx.neg_cycle import NegCycleFinder


def has_negative_cycle(TCP, dist):
    """Creates a test graph for timing tests."""
    digraph = {
        "v0": {"v3": TCP - 6, "v2": 6},
        "v1": {"v2": TCP - 9, "v4": 3},
        "v2": {"v0": TCP - 7, "v1": 6},
        "v3": {"v4": TCP - 8, "v0": 6},
        "v4": {"v1": TCP - 3, "v3": 8},
    }
    finder = NegCycleFinder(digraph)
    for _ in finder.howard(dist, lambda edge: edge):
        return True
    return False


def test_example1():
    """Creates a test graph for timing tests."""
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    assert has_negative_cycle(10.0, dist) is False


def test_example2():
    """Creates a test graph for timing tests."""
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    assert has_negative_cycle(5.0, dist) is True


def test_example3():
    dist = {"v0": 0, "v1": 0, "v2": 0, "v3": 0, "v4": 0}
    assert has_negative_cycle(7.0, dist) is False
    assert dist == {"v0": -2, "v1": 0, "v2": -2, "v3": -1, "v4": -2}
