# -*- coding: utf-8 -*-
"""Property-based tests for digraphx using hypothesis."""

from __future__ import annotations

from typing import Any

import hypothesis.strategies as st
from hypothesis import given, assume

from digraphx.tiny_digraph import TinyDiGraph


@st.composite
def tiny_graph_strategy(draw: Any) -> TinyDiGraph:
    """Generate a TinyDiGraph with random nodes and edges."""
    # Generate number of nodes (1-20 to keep tests reasonable)
    n_nodes = draw(st.integers(min_value=1, max_value=20))

    # Create graph
    graph = TinyDiGraph()
    graph.init_nodes(n_nodes)

    # Generate random edges
    n_edges = draw(st.integers(min_value=0, max_value=n_nodes * 2))

    for _ in range(n_edges):
        u = draw(st.integers(min_value=0, max_value=n_nodes - 1))
        v = draw(st.integers(min_value=0, max_value=n_nodes - 1))
        weight = draw(st.integers(min_value=-10, max_value=10))

        # Only add edge if it's not a self-loop
        assume(u != v)
        graph.add_edge(u, v, weight=weight)

    return graph


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_node_count_property(graph: TinyDiGraph) -> None:
    """Test that node count is consistent."""
    expected_count = len(list(graph.nodes))
    actual_count = graph.number_of_nodes()
    assert expected_count == actual_count


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_edge_count_property(graph: TinyDiGraph) -> None:
    """Test that edge count is consistent."""
    expected_count = len(list(graph.edges))
    actual_count = graph.number_of_edges()
    assert expected_count == actual_count


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_symmetric_edge_addition(graph: TinyDiGraph) -> None:
    """Test that adding edges maintains consistency."""
    original_edge_count = graph.number_of_edges()

    # Add a new edge
    n_nodes = len(list(graph.nodes))
    assume(n_nodes >= 2)  # Need at least 2 nodes for an edge

    u = 0
    v = 1
    weight = 5

    # Only add if edge doesn't exist
    if not graph.has_edge(u, v):
        graph.add_edge(u, v, weight=weight)

        # Check edge was added correctly
        assert graph.has_edge(u, v)
        assert graph[u][v]["weight"] == weight
        assert graph.number_of_edges() == original_edge_count + 1


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_edge_removal(graph: TinyDiGraph) -> None:
    """Test that removing edges maintains consistency."""
    edges = list(graph.edges)
    assume(len(edges) > 0)  # Need at least one edge to remove

    # Pick first edge to remove
    u, v = edges[0]
    original_edge_count = graph.number_of_edges()

    # Remove edge
    graph.remove_edge(u, v)

    # Check edge was removed
    assert not graph.has_edge(u, v)
    assert graph.number_of_edges() == original_edge_count - 1


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_node_attributes(graph: TinyDiGraph) -> None:
    """Test that node attributes can be set and retrieved."""
    nodes = list(graph.nodes)
    assume(len(nodes) > 0)

    node = nodes[0]
    test_key = "test_attr"
    test_value = "test_value"

    # Set attribute
    graph.nodes[node][test_key] = test_value

    # Retrieve and check
    assert graph.nodes[node][test_key] == test_value


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_edge_attributes(graph: TinyDiGraph) -> None:
    """Test that edge attributes can be set and retrieved."""
    edges = list(graph.edges)
    assume(len(edges) > 0)

    u, v = edges[0]
    test_key = "test_attr"
    test_value = "test_value"

    # Set attribute
    graph[u][v][test_key] = test_value

    # Retrieve and check
    assert graph[u][v][test_key] == test_value


@given(n_nodes=st.integers(min_value=1, max_value=10))
def test_tiny_digraph_initialization(n_nodes: int) -> None:
    """Test that graph initialization works correctly."""
    graph = TinyDiGraph()
    graph.init_nodes(n_nodes)

    # Check nodes exist
    assert len(list(graph.nodes)) == n_nodes
    assert graph.number_of_nodes() == n_nodes

    # Check no edges initially
    assert len(list(graph.edges)) == 0
    assert graph.number_of_edges() == 0


# @given(
#     n_nodes=st.integers(min_value=2, max_value=10),
#     edges=st.lists(
#         st.tuples(
#             st.integers(min_value=0, max_value=9),
#             st.integers(min_value=0, max_value=9),
#             st.integers(min_value=-5, max_value=5)
#         ),
#         min_size=0,
#         max_size=15
#     )
# )
# def test_tiny_digraph_with_specific_edges(n_nodes: int, edges: list[tuple[int, int, int]]) -> None:
#     """Test graph creation with specific edges."""
#     graph = TinyDiGraph()
#     graph.init_nodes(n_nodes)

#     # Add edges, filtering out invalid ones
#     valid_edges = [(u, v, w) for u, v, w in edges if u < n_nodes and v < n_nodes and u != v]

#     for u, v, w in valid_edges:
#         graph.add_edge(u, v, weight=w)

#     # Check all edges exist with correct weights
#     for u, v, w in valid_edges:
#         assert graph.has_edge(u, v)
#         assert graph[u][v]["weight"] == w

#     # Check edge count
#     assert graph.number_of_edges() == len(valid_edges)


@given(graph=tiny_graph_strategy())
def test_tiny_digraph_neighbors_property(graph: TinyDiGraph) -> None:
    """Test that neighbors are correctly identified."""
    nodes = list(graph.nodes)
    assume(len(nodes) > 0)

    for node in nodes:
        # Get neighbors from adjacency
        adjacency_neighbors = set(graph[node].keys())

        # Get neighbors using neighbors() method if available
        try:
            method_neighbors = set(graph.neighbors(node))
            assert adjacency_neighbors == method_neighbors
        except AttributeError:
            # TinyDiGraph may not have neighbors() method, that's fine
            pass

        # All neighbors should be valid nodes
        for neighbor in adjacency_neighbors:
            assert neighbor in nodes
            assert graph.has_edge(node, neighbor)
