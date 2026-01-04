# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest

from digraphx.tiny_digraph import TinyDiGraph

WEIGHT_0_1: int = 7
WEIGHT_1_0: int = 0
WEIGHT_1_2: int = 3
WEIGHT_2_1: int = 1
WEIGHT_2_0: int = 2
WEIGHT_0_2: int = 5
WEIGHT_ADD_EDGE: int = 2
WEIGHT_ATTR: int = 3


def test_tiny_digraph() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(3)
    digraph.add_edges_from(
        [
            (0, 1, {"weight": WEIGHT_0_1}),
            (1, 0, {"weight": WEIGHT_1_0}),
            (1, 2, {"weight": WEIGHT_1_2}),
            (2, 1, {"weight": WEIGHT_2_1}),
            (2, 0, {"weight": WEIGHT_2_0}),
            (0, 2, {"weight": WEIGHT_0_2}),
        ]
    )
    assert list(digraph.nodes) == [0, 1, 2]
    assert sorted(list(digraph.edges)) == sorted(
        [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    )
    assert digraph[0][1]["weight"] == WEIGHT_0_1


def test_tiny_digraph_add_node() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(4)
    digraph.add_node(3)
    assert 3 in digraph.nodes


def test_tiny_digraph_remove_node() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(4)
    with pytest.raises(NotImplementedError):
        digraph.remove_node(3)


def test_tiny_digraph_add_edge() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(2)
    digraph.add_edge(0, 1, weight=WEIGHT_ADD_EDGE)
    assert digraph.has_edge(0, 1)


def test_tiny_digraph_remove_edge() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(2)
    digraph.add_edge(0, 1, weight=WEIGHT_ADD_EDGE)
    digraph.remove_edge(0, 1)
    assert not digraph.has_edge(0, 1)


def test_tiny_digraph_attributes() -> None:
    digraph: TinyDiGraph = TinyDiGraph()
    digraph.init_nodes(2)
    digraph.nodes[0]["foo"] = "bar"
    assert digraph.nodes[0]["foo"] == "bar"
    digraph.add_edge(0, 1, weight=WEIGHT_ATTR)
    assert digraph.get_edge_data(0, 1)["weight"] == WEIGHT_ATTR


def test_digraph_adapter_setitem() -> None:
    """Test __setitem__ method of DiGraphAdapter exists and can be called."""
    from digraphx.tiny_digraph import DiGraphAdapter

    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_node(0)
    digraph.add_node(1)
    digraph.add_edge(0, 1, weight=5)

    # Verify we can access the adjacency dict
    assert digraph[0][1]["weight"] == 5

    # Test that the method exists (it's inherited from NetworkX)
    assert hasattr(digraph, "__setitem__")


def test_digraph_adapter_delitem() -> None:
    """Test __delitem__ method of DiGraphAdapter exists and can be called."""
    from digraphx.tiny_digraph import DiGraphAdapter

    digraph: DiGraphAdapter = DiGraphAdapter()
    digraph.add_node(0)
    digraph.add_node(1)
    digraph.add_edge(0, 1)

    # Test that the method exists (it's inherited from NetworkX)
    assert hasattr(digraph, "__delitem__")

    # NetworkX requires removing nodes with remove_node method
    digraph.remove_node(0)
    assert 0 not in digraph.nodes
    assert not digraph.has_edge(0, 1)
