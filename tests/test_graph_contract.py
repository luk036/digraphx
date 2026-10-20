"""Contract tests for the four graph implementations.

Every algorithm in the package accepts ``Mapping[node, Mapping[node, edge]]``
structurally, and four implementations satisfy that shape.  These tests pin the
shared contract, so a change to one implementation (or a NetworkX upgrade) cannot
silently diverge from the others.
"""

from fractions import Fraction
from typing import Any, Callable, Dict, List

import networkx as nx
import pytest

from digraphx import (
    CSRDiGraph,
    DiGraphAdapter,
    MinCycleRatioSolver,
    NegCycleFinder,
    TinyDiGraph,
)

Edges = List[Any]

EDGES: Edges = [
    (0, 1, {"weight": 7, "cost": 7, "time": 1}),
    (1, 2, {"weight": 3, "cost": 3, "time": 1}),
    (2, 0, {"weight": -11, "cost": -11, "time": 1}),
]


def _plain() -> Dict[int, Dict[int, Dict[str, Any]]]:
    graph: Dict[int, Dict[int, Dict[str, Any]]] = {}
    for u, v, attr in EDGES:
        graph.setdefault(u, {})[v] = dict(attr)
        graph.setdefault(v, {})
    return graph


def _adapter() -> DiGraphAdapter:
    graph = DiGraphAdapter()
    for u, v, attr in EDGES:
        graph.add_edge(u, v, **attr)
    return graph


def _tiny() -> TinyDiGraph:
    graph = TinyDiGraph()
    graph.init_nodes(3)
    for u, v, attr in EDGES:
        graph.add_edge(u, v, **attr)
    return graph


def _csr() -> CSRDiGraph:
    graph = CSRDiGraph()
    graph.init_nodes(3)
    for u, v, attr in EDGES:
        graph.add_edge(u, v, **attr)
    graph.freeze()
    return graph


@pytest.fixture(
    params=[
        pytest.param(_plain, id="dict"),
        pytest.param(_adapter, id="digraph-adapter"),
        pytest.param(_tiny, id="tiny-digraph"),
        pytest.param(_csr, id="csr-digraph"),
    ]
)
def graph(request: pytest.FixtureRequest) -> Any:
    factory: Callable[[], Any] = request.param
    return factory()


def test_number_of_nodes(graph: Any) -> None:
    assert len(graph) == 3


def test_node_iteration(graph: Any) -> None:
    assert list(graph) == [0, 1, 2]


def test_items_cover_every_node(graph: Any) -> None:
    assert sorted(node for node, _ in graph.items()) == [0, 1, 2]


def test_edge_attributes(graph: Any) -> None:
    assert graph[0][1]["weight"] == 7


def test_neighbor_iteration(graph: Any) -> None:
    assert list(graph[0]) == [1]


def test_neighbor_membership(graph: Any) -> None:
    assert 1 in graph[0]
    assert 2 not in graph[0]


def test_neighbor_get(graph: Any) -> None:
    assert graph[0].get(1)["weight"] == 7
    assert graph[0].get(2) is None


def test_missing_edge_raises_key_error(graph: Any) -> None:
    with pytest.raises(KeyError):
        graph[0][2]


def test_missing_node_raises_lookup_error(graph: Any) -> None:
    with pytest.raises((KeyError, nx.NetworkXError)):
        graph[9]


def test_negative_cycle_is_found(graph: Any) -> None:
    dist = {node: 0 for node in graph}
    cycles = list(NegCycleFinder(graph).howard(dist, lambda edge: edge["weight"]))
    assert len(cycles) == 1
    assert sum(edge["weight"] for edge in cycles[0]) < 0


def test_min_cycle_ratio_is_found(graph: Any) -> None:
    dist = {node: Fraction(0) for node in graph}
    ratio, cycle = MinCycleRatioSolver(graph).run(dist, Fraction(100))
    assert ratio == Fraction(-1, 3)
    assert len(cycle) == 3
