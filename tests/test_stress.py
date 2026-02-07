# -*- coding: utf-8 -*-
"""Stress tests for large graphs to test performance and correctness."""

import time
from fractions import Fraction

from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default
from digraphx.neg_cycle import NegCycleFinder
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


def test_tiny_digraph_large_graph():
    """Test TinyDiGraph with a large graph (10000 nodes, 100000 edges)."""
    graph = TinyDiGraph()
    num_nodes = 10000
    num_edges_per_node = 10

    graph.init_nodes(num_nodes)

    # Add edges in a pattern that won't create negative cycles
    for i in range(num_nodes):
        for j in range(1, num_edges_per_node + 1):
            target = (i + j) % num_nodes
            graph.add_edge(i, target, weight=1)

    # Verify basic properties
    assert graph.number_of_nodes() == num_nodes
    assert graph.number_of_edges() == num_nodes * num_edges_per_node

    # Test iteration doesn't break on large graphs
    node_count = 0
    edge_count = 0
    for u in graph:
        node_count += 1
        for v in graph.neighbors(u):
            edge_count += 1

    assert node_count == num_nodes
    assert edge_count == num_nodes * num_edges_per_node


def test_neg_cycle_finder_large_graph():
    """Test negative cycle detection on large graph without negative cycles."""
    graph = DiGraphAdapter()
    num_nodes = 1000

    # Create nodes
    graph.add_nodes_from(range(num_nodes))

    # Add positive weighted edges
    for i in range(num_nodes):
        for j in range(i + 1, min(i + 10, num_nodes)):
            graph.add_edge(i, j, weight=j - i)

    dist = {node: 0 for node in graph}
    finder = NegCycleFinder(graph)

    # Should not find any negative cycles
    cycles_found = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles_found) == 0


def test_neg_cycle_finder_large_graph_with_negative_cycle():
    """Test negative cycle detection on large graph with a negative cycle."""
    graph = DiGraphAdapter()
    num_nodes = 1000

    # Create nodes
    graph.add_nodes_from(range(num_nodes))

    # Add positive weighted edges
    for i in range(num_nodes):
        if i + 1 < num_nodes:
            graph.add_edge(i, i + 1, weight=1)

    # Add a negative cycle at the end
    last_5 = num_nodes - 5
    graph.add_edge(last_5, last_5 + 1, weight=1)
    graph.add_edge(last_5 + 1, last_5 + 2, weight=1)
    graph.add_edge(last_5 + 2, last_5 + 3, weight=1)
    graph.add_edge(last_5 + 3, last_5 + 4, weight=1)
    graph.add_edge(last_5 + 4, last_5, weight=-10)  # Creates negative cycle

    dist = {node: 0 for node in graph}
    finder = NegCycleFinder(graph)

    # Should find the negative cycle
    cycles_found = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles_found) > 0


def test_min_cycle_ratio_large_graph():
    """Test minimum cycle ratio solver on large graph."""
    graph = DiGraphAdapter()
    num_nodes = 500

    # Create a graph with cost and time attributes
    for i in range(num_nodes):
        for j in range(i + 1, min(i + 5, num_nodes)):
            cost = j - i
            time = 1
            graph.add_edge(i, j, cost=cost, time=time)
            graph.add_edge(j, i, cost=cost + 1, time=time + 1)

    set_default(graph, "cost", 0)
    set_default(graph, "time", 1)

    solver = MinCycleRatioSolver(graph)
    dist = {node: Fraction(0) for node in graph}

    # Should complete without errors
    ratio, cycle = solver.run(dist, Fraction(10))
    assert isinstance(ratio, (Fraction, float))


def test_performance_comparison_tiny_vs_adapter():
    """Compare performance between TinyDiGraph and DiGraphAdapter."""
    num_nodes = 5000
    edges_per_node = 5

    # Test TinyDiGraph
    tiny_graph = TinyDiGraph()
    start_time = time.time()
    tiny_graph.init_nodes(num_nodes)
    for i in range(num_nodes):
        for j in range(1, edges_per_node + 1):
            tiny_graph.add_edge(i, (i + j) % num_nodes, weight=1)
    tiny_build_time = time.time() - start_time

    # Test DiGraphAdapter
    adapter_graph = DiGraphAdapter()
    start_time = time.time()
    adapter_graph.add_nodes_from(range(num_nodes))
    for i in range(num_nodes):
        for j in range(1, edges_per_node + 1):
            adapter_graph.add_edge(i, (i + j) % num_nodes, weight=1)
    adapter_build_time = time.time() - start_time

    # Both should work correctly
    assert tiny_graph.number_of_nodes() == num_nodes
    assert adapter_graph.number_of_nodes() == num_nodes

    # TinyDiGraph should be faster (typically)
    # We don't assert this as it depends on system, but it's informational
    print(f"\nTinyDiGraph build time: {tiny_build_time:.4f}s")
    print(f"DiGraphAdapter build time: {adapter_build_time:.4f}s")


def test_memory_efficiency_tiny_digraph():
    """Test that TinyDiGraph is initialized correctly for memory efficiency."""
    graph = TinyDiGraph()
    num_nodes = 10000

    graph.init_nodes(num_nodes)

    # Verify internal structures are MapAdapter instances
    assert hasattr(graph._node, "__getitem__")
    assert hasattr(graph._adj, "__getitem__")
    assert hasattr(graph._pred, "__getitem__")

    # Add some edges and verify they work
    for i in range(100):
        graph.add_edge(i, i + 1, weight=i)

    assert graph.number_of_edges() == 100


def test_large_negative_cycle_multiple():
    """Test finding multiple negative cycles in a large graph."""
    graph = DiGraphAdapter()
    num_nodes = 2000

    # Create nodes
    graph.add_nodes_from(range(num_nodes))

    # Add multiple negative cycles
    for start in range(0, num_nodes, 100):
        graph.add_edge(start, start + 1, weight=1)
        graph.add_edge(start + 1, start + 2, weight=1)
        graph.add_edge(start + 2, start + 3, weight=1)
        graph.add_edge(start + 3, start, weight=-10)

    dist = {node: 0 for node in graph}
    finder = NegCycleFinder(graph)

    # Should find at least some negative cycles
    cycles_found = list(finder.howard(dist, lambda edge: edge.get("weight", 1)))
    assert len(cycles_found) > 0


def test_stress_edge_iteration():
    """Test edge iteration on very large graph."""
    graph = TinyDiGraph()
    num_nodes = 2000
    edges_per_node = 20

    graph.init_nodes(num_nodes)

    # Add edges
    for i in range(num_nodes):
        for j in range(1, edges_per_node + 1):
            graph.add_edge(i, (i + j) % num_nodes, weight=i + j)

    # Count edges by iteration
    edge_count = sum(1 for u, v in graph.edges())
    assert edge_count == num_nodes * edges_per_node
