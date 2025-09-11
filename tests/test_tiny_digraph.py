# -*- coding: utf-8 -*-
from __future__ import print_function

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
