"""Tests for spareTSV (integrated into digraphx)."""

import networkx as nx

from digraphx.spare_tsv import (
    formGraph,
    setup_network_flow,
    showPaths,
    solve_network_flow,
    vdc,
    vdcorput,
    vdcorput_iter,
)


def test_vdc():
    result = vdc(1, base=2)
    assert result == 0.5


def test_vdc_sequence_base_2():
    vals = [vdc(i, base=2) for i in range(4)]
    assert vals == [0.0, 0.5, 0.25, 0.75]


def test_vdc_sequence_base_3():
    vals = [vdc(i, base=3) for i in range(3)]
    assert vals == [0.0, 1 / 3, 2 / 3]


def test_vdcorput():
    result = vdcorput(5, base=2)
    assert len(result) == 5
    assert all(0 <= x < 1 for x in result)


def test_vdcorput_iter():
    result = list(vdcorput_iter(5, base=2))
    assert len(result) == 5
    assert result == vdcorput(5, base=2)


def test_formGraph(sample_positions):
    gra = formGraph(12, sample_positions, 0.12, 1.6, seed=5)
    assert gra.number_of_nodes() == 12
    assert gra.is_directed()


def test_formGraph_reproducible(sample_positions):
    g1 = formGraph(12, sample_positions, 0.12, 1.6, seed=42)
    g2 = formGraph(12, sample_positions, 0.12, 1.6, seed=42)
    assert g1.number_of_edges() == g2.number_of_edges()


def test_formGraph_no_seed(sample_positions):
    gra = formGraph(12, sample_positions, 0.12, 1.6)
    assert gra.number_of_nodes() == 12
    assert gra.is_directed()


def test_showPaths(small_graph, sample_positions):
    N = 9
    pos = dict(enumerate(sample_positions))
    fig, ax = showPaths(small_graph, pos, N)
    assert fig is not None
    assert ax is not None


def test_showPaths_with_options(small_graph, sample_positions):
    N = 9
    pos = dict(enumerate(sample_positions))
    edges = list(small_graph.edges())[:3]
    edge_probs = [0.5] * small_graph.number_of_edges()
    vis = list(range(9))
    fig, ax = showPaths(
        small_graph,
        pos,
        N,
        edgeProbs=edge_probs,
        path=edges,
        visibleNodes=vis,
        guards=[0, 1],
    )
    assert fig is not None
    assert ax is not None


# --- Network flow tests ---


def test_setup_network_flow(small_graph, sample_positions):
    gra = small_graph.copy()
    total = gra.number_of_nodes()
    sink = setup_network_flow(gra, sample_positions, primal_count=9, capacity=4)

    assert sink == total
    assert gra.number_of_nodes() == total + 1
    assert gra.has_node(sink)
    assert gra.nodes[0]["demand"] == -1
    assert gra.nodes[9]["demand"] == 0
    assert gra.nodes[sink]["demand"] == 9


def test_setup_network_flow_edge_attrs(small_graph, sample_positions):
    gra = small_graph.copy()
    setup_network_flow(gra, sample_positions, primal_count=9, capacity=4)

    u, v = next(iter(gra.edges()))
    assert "weight" in gra[u][v]
    assert "capacity" in gra[u][v]
    assert gra[u][v]["capacity"] == 4
    assert isinstance(gra[u][v]["weight"], int)


def test_solve_network_flow(small_graph, sample_positions):
    gra = small_graph.copy()
    sink = setup_network_flow(gra, sample_positions, primal_count=9, capacity=4)
    result = solve_network_flow(gra, sink)

    assert result is not None
    flow_cost, path_list = result
    assert isinstance(path_list, list)
    assert flow_cost >= 0


def test_solve_network_flow_path_excludes_sink(small_graph, sample_positions):
    gra = small_graph.copy()
    sink = setup_network_flow(gra, sample_positions, primal_count=9, capacity=4)
    result = solve_network_flow(gra, sink)

    assert result is not None
    _, path_list = result
    for u, v in path_list:
        assert v != sink


def test_solve_network_flow_infeasible():
    gra = nx.DiGraph()
    gra.add_node(0, demand=-1)
    gra.add_node(1, demand=0)
    gra.add_edge(0, 1, weight=1, capacity=0)
    sink = 2
    gra.add_node(sink, demand=1)
    gra.add_edge(1, sink, capacity=0)

    result = solve_network_flow(gra, sink)
    assert result is None
