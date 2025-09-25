# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest

from digraphx.tiny_digraph import TinyDiGraph


def test_tiny_digraph():
    digraph = TinyDiGraph()
    digraph.init_nodes(3)
    digraph.add_edges_from(
        [
            (0, 1, {"weight": 7}),
            (1, 0, {"weight": 0}),
            (1, 2, {"weight": 3}),
            (2, 1, {"weight": 1}),
            (2, 0, {"weight": 2}),
            (0, 2, {"weight": 5}),
        ]
    )
    assert list(digraph.nodes) == [0, 1, 2]
    assert sorted(list(digraph.edges)) == sorted(
        [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
    )
    assert digraph[0][1]["weight"] == 7


def test_tiny_digraph_add_remove():
    digraph = TinyDiGraph()
    digraph.init_nodes(4)
    digraph.add_node(3)
    assert 3 in digraph.nodes
    with pytest.raises(NotImplementedError):
        digraph.remove_node(3)
    digraph.add_edge(0, 1, weight=2)
    assert digraph.has_edge(0, 1)
    digraph.remove_edge(0, 1)
    assert not digraph.has_edge(0, 1)


def test_tiny_digraph_attributes():
    digraph = TinyDiGraph()
    digraph.init_nodes(2)
    digraph.nodes[0]["foo"] = "bar"
    assert digraph.nodes[0]["foo"] == "bar"
    digraph.add_edge(0, 1, weight=3)
    assert digraph.get_edge_data(0, 1)["weight"] == 3
