"""Spare TSV network optimization utilities."""

import math

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def vdc(n, base=2):
    """Van der Corput sequence."""
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    """Generate n Van der Corput vectors as a list."""
    return [vdc(i, base) for i in range(n)]


def vdcorput_iter(n, base=2):
    """Generate n Van der Corput vectors lazily (generator).

    Yields values one at a time instead of allocating a full list.
    """
    for i in range(n):
        yield vdc(i, base)


def formGraph(T, pos, mu, eta, seed=None):
    """Form N by N grid of nodes, perturb by mu and connect nodes within eta.

    mu and eta are relative to 1/(N-1).
    """
    if seed is not None:
        np.random.seed(seed)

    N = int(np.sqrt(T))
    mu = mu / (N - 1)
    eta = eta / (N - 1)

    pos = dict(enumerate(pos))
    n = len(pos)

    gra = nx.random_geometric_graph(n, eta, pos=pos)
    gra = nx.DiGraph(gra)
    return gra


def showPaths(gra, pos, N, edgeProbs=1.0, path=None, visibleNodes=None, guards=None):
    """Draw directed graph with optional path overlay.

    Parameters
    ----------
    gra : nx.DiGraph
        Directed graph.
    pos : dict
        Node positions {node: (x, y)}.
    N : int
        Number of primal nodes (drawn cyan).
    edgeProbs : float or list
        Edge probability/weights for coloring.
    path : list of edges
        Edges to highlight in blue.
    visibleNodes : list
        Nodes to draw (default: all).
    guards : list
        Nodes to highlight with black dots.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, aspect="equal")

    n = gra.number_of_nodes()
    if visibleNodes is None:
        visibleNodes = gra.nodes()
    primalNodes = range(0, N)
    spareNodes = range(N, n)

    nx.draw_networkx_nodes(
        gra, pos, nodelist=primalNodes, node_color="c", node_size=50, ax=ax
    )
    nx.draw_networkx_nodes(
        gra, pos, nodelist=spareNodes, node_color="r", node_size=50, ax=ax
    )

    if guards is not None:
        nx.draw_networkx_nodes(
            gra, pos, nodelist=guards, node_color=".0", node_size=100, ax=ax
        )

    alpha = 1.0 if path is None else 0.15

    # only display edges between non-dummy nodes
    edge_list = list(gra.edges())
    visibleEdges = [
        e
        for e in edge_list
        if e[0] in visibleNodes and e[1] in visibleNodes
    ]

    if isinstance(edgeProbs, float):
        edgeProbs = [edgeProbs] * gra.number_of_edges()
    p = [edgeProbs[i] for i, e in enumerate(edge_list) if e in visibleEdges]

    nx.draw_networkx_edges(
        gra,
        pos,
        edge_color=p,
        width=1,
        edge_cmap=plt.cm.RdYlGn,
        arrows=False,
        edgelist=visibleEdges,
        edge_vmin=0.0,
        edge_vmax=1.0,
        ax=ax,
        alpha=alpha,
    )

    if path is not None:
        nx.draw_networkx_edges(
            gra,
            pos,
            edge_color="b",
            width=1,
            edge_cmap=plt.cm.RdYlGn,
            edgelist=path,
            arrows=True,
            edge_vmin=0.0,
            edge_vmax=1.0,
        )

    ax.axis([-0.05, 1.05, -0.05, 1.05])
    ax.axis("off")

    return fig, ax


def setup_network_flow(gra, pos, primal_count, capacity):
    """Configure graph for spare TSV network flow.

    Sets edge weights (Euclidean distance * 100), assigns demand=-1 to
    primal nodes and demand=0 to spare nodes, then adds a sink node
    connected to all spare nodes.

    Returns the sink node index.
    """
    total = gra.number_of_nodes()
    for u, v in gra.edges():
        dx = pos[u][0] - pos[v][0]
        dy = pos[u][1] - pos[v][1]
        gra[u][v]["weight"] = int(math.sqrt(dx * dx + dy * dy) * 100)
        gra[u][v]["capacity"] = capacity

    for i in range(primal_count):
        gra.nodes[i]["demand"] = -1
    for i in range(primal_count, total):
        gra.nodes[i]["demand"] = 0

    sink = total
    gra.add_node(sink, demand=primal_count)
    for i in range(primal_count, total):
        gra.add_edge(i, sink, capacity=capacity)

    return sink


def solve_network_flow(gra, sink_node):
    """Solve network flow and return path edges.

    Returns (flow_cost, path_list) where path_list contains edges
    with positive flow (excluding edges to the sink).

    Returns None if the problem is infeasible.
    """
    try:
        flow_cost, flow_dict = nx.network_simplex(gra)
    except nx.NetworkXUnfeasible:
        return None

    path_list = [
        (u, v)
        for u in flow_dict
        for v in flow_dict[u]
        if flow_dict[u][v] > 0 and v != sink_node
    ]
    return flow_cost, path_list
