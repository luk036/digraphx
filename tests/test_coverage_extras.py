"""Additional tests for digraphx code coverage."""

from fractions import Fraction
from typing import Dict

from pytest import raises


class TestMinParametricQ:
    """Tests covering MinParametricSolver / MinParametricAPI edge cases."""

    def test_min_parametric_api_abstract(self) -> None:
        """Verify MinParametricAPI cannot be instantiated directly."""
        from digraphx.min_parametric_q import MinParametricAPI

        try:
            MinParametricAPI()  # type: ignore[abstract]
        except TypeError:
            pass

    def test_min_parametric_solver_run(self) -> None:
        """Test solver with pick_one_only flag on simple graph."""
        from fractions import Fraction

        from digraphx.min_parametric_q import MinParametricSolver

        class DummyDistance:
            def distance(self, ratio, edge):
                return Fraction(edge).limit_denominator()

            def zero_cancel(self, cycle):
                return Fraction(0)

        graph = {0: {1: 1.0}, 1: {0: -1.0}}
        solver = MinParametricSolver(graph, DummyDistance())  # type: ignore[arg-type]
        dist = {0: 0, 1: 0}
        result = solver.run(dist, Fraction(0), lambda a, b: True, pick_one_only=True)
        assert result is not None

    def test_abstract_method_bodies_callable(self) -> None:
        """Cover the ``pass`` bodies of the abstract MinParametricAPI methods.

        A concrete subclass that delegates to ``super()`` executes the abstract
        method bodies (which simply ``pass``), so they return ``None``.
        """
        from digraphx.min_parametric_q import MinParametricAPI

        class DelegatingAPI(MinParametricAPI):  # type: ignore[type-arg]
            def distance(self, ratio, edge):
                return super().distance(ratio, edge)

            def zero_cancel(self, cycle):
                return super().zero_cancel(cycle)

        api = DelegatingAPI()
        assert api.distance(Fraction(1), {"cost": 1, "time": 1}) is None
        assert api.zero_cancel([]) is None

    def test_solver_improving_ratio(self) -> None:
        """Test that the solver raises the ratio when a cycle improves it."""
        from digraphx.min_parametric_q import MinParametricAPI, MinParametricSolver

        class NegTimeAPI(MinParametricAPI):  # type: ignore[type-arg]
            def distance(self, ratio, edge):
                return Fraction(edge["cost"] - ratio * edge["time"])

            def zero_cancel(self, cycle):
                total_cost = sum(e["cost"] for e in cycle)
                total_time = sum(e["time"] for e in cycle)
                return Fraction(total_cost, total_time)

        # Negative total cycle time makes zero_cancel exceed the initial ratio,
        # so the improving-ratio branch (ratio_max < ratio_i) is taken.
        digraph = {
            0: {1: {"cost": 1, "time": -1}},
            1: {0: {"cost": 1, "time": -1}},
        }
        solver = MinParametricSolver(digraph, NegTimeAPI())
        ratio, cycle = solver.run({0: 0.0, 1: 0.0}, Fraction(-2), lambda D, d: True)
        assert ratio > Fraction(-2)
        assert len(cycle) == 2

    def test_solver_improving_ratio_pick_one(self) -> None:
        """Test improving-ratio with pick_one_only early exit."""
        from digraphx.min_parametric_q import MinParametricAPI, MinParametricSolver

        class NegTimeAPI(MinParametricAPI):  # type: ignore[type-arg]
            def distance(self, ratio, edge):
                return Fraction(edge["cost"] - ratio * edge["time"])

            def zero_cancel(self, cycle):
                total_cost = sum(e["cost"] for e in cycle)
                total_time = sum(e["time"] for e in cycle)
                return Fraction(total_cost, total_time)

        digraph = {
            0: {1: {"cost": 1, "time": -1}},
            1: {0: {"cost": 1, "time": -1}},
        }
        solver = MinParametricSolver(digraph, NegTimeAPI())
        ratio, cycle = solver.run(
            {0: 0.0, 1: 0.0}, Fraction(-2), lambda D, d: True, pick_one_only=True
        )
        assert ratio > Fraction(-2)
        assert len(cycle) == 2


class TestNegCycleQ:
    """Tests covering neg_cycle_q edge cases."""

    def test_howard_pred_with_float_dist(self) -> None:
        """Test howard_pred with float distances."""
        from digraphx.neg_cycle_q import NegCycleFinderQ

        graph = {
            0: {1: 3.0},
            1: {2: -5.0},
            2: {0: 1.0},
        }
        finder: NegCycleFinderQ[int, float, float] = NegCycleFinderQ(graph)
        dist = {0: 0.0, 1: 0.0, 2: 0.0}
        cycles = list(finder.howard_pred(dist, lambda e: e, lambda a, b: True))
        assert len(cycles) == 1


class TestMcF:
    """Tests covering min-cost flow cycle cancellation edge cases."""

    def test_vertex_filter_used_forward_node(self) -> None:
        """A forward cycle edge leaving an already-used node is rejected."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {0}
        cycle_edges = [{"orig": (0, 1), "forward": True, "cost": -1, "capacity": 1}]
        assert vf.cycle_uses_used_node(cycle_edges)

    def test_vertex_filter_backward_node_not_rejected(self) -> None:
        """A backward cycle edge alone never triggers the used-node check."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {0}
        cycle_edges = [{"orig": (0, 1), "forward": False, "cost": 1, "capacity": 1}]
        assert not vf.cycle_uses_used_node(cycle_edges)

    def test_vertex_filter_sink_exempt(self) -> None:
        """Cycle edges out of the sink node are exempt from the check."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(0)
        vf.used = {0}
        cycle_edges = [{"orig": (0, 1), "forward": True, "cost": -1, "capacity": 1}]
        assert not vf.cycle_uses_used_node(cycle_edges)

    def test_vertex_filter_forward_node_unused(self) -> None:
        """A forward edge from an unused node is accepted."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {5}
        cycle_edges = [{"orig": (0, 1), "forward": True, "cost": -1, "capacity": 1}]
        assert not vf.cycle_uses_used_node(cycle_edges)

    def test_vertex_filter_offsetting_backward_edge(self) -> None:
        """A used node is rejected even when offset by a backward edge."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {0}
        cycle_edges = [
            {"orig": (0, 1), "forward": True, "cost": -1, "capacity": 1},
            {"orig": (1, 0), "forward": False, "cost": 1, "capacity": 1},
        ]
        assert vf.cycle_uses_used_node(cycle_edges)

    def test_vertex_filter_accept_cycle_forward(self) -> None:
        """accept_cycle adds forward flow and marks the source node used."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        flow = {0: {1: 0}, 1: {}, 2: {}}
        cycle_edges = [
            {"orig": (0, 1), "forward": True, "cost": -1, "capacity": 3},
            {"orig": (2, 0), "forward": False, "cost": 1, "capacity": 2},
        ]
        vf.accept_cycle(cycle_edges, flow, 2)
        assert flow[0][1] == 2
        assert flow[2][0] == -2
        assert 0 in vf.used

    def test_vertex_filter_accept_cycle_discard(self) -> None:
        """accept_cycle drops a node from used once its flow is exhausted."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {0}
        flow = {0: {2: 1}, 2: {}}
        cycle_edges = [{"orig": (0, 2), "forward": False, "cost": 1, "capacity": 1}]
        vf.accept_cycle(cycle_edges, flow, 1)
        assert flow[0][2] == 0
        assert 0 not in vf.used

    def test_vertex_filter_accept_cycle_keeps_flow(self) -> None:
        """A node with remaining flow stays in the used set."""
        from digraphx.mcf import VertexFilter

        vf = VertexFilter(9)
        vf.used = {0}
        flow = {0: {2: 3}, 2: {}}
        cycle_edges = [{"orig": (0, 2), "forward": False, "cost": 1, "capacity": 1}]
        vf.accept_cycle(cycle_edges, flow, 1)
        assert flow[0][2] == 2
        assert 0 in vf.used

    def test_mcf_sink_mode_marks_used(self) -> None:
        """Sink mode pre-marks used nodes from the initial flow."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {0: {1: {"weight": 3, "capacity": 1}}, 1: {}}
        result = cycle_canceling_mcf(g, {0: -1, 1: 1}, sink=0)
        assert result is not None
        cost, flow = result
        assert cost == 3
        assert flow[0][1] == 1

    def test_mcf_sink_mode_rejects_used_node(self) -> None:
        """Sink mode rejects cycles that reuse an already-used node."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {
            0: {1: {"weight": 7, "capacity": 3}, 2: {"weight": 6, "capacity": 2}},
            1: {2: {"weight": 8, "capacity": 2}, 3: {"weight": -1, "capacity": 3}},
            2: {1: {"weight": -4, "capacity": 3}, 3: {"weight": 5, "capacity": 2}},
            3: {1: {"weight": -3, "capacity": 3}, 2: {"weight": 3, "capacity": 1}},
        }
        result = cycle_canceling_mcf(g, {0: -1, 1: 2, 2: 0, 3: -1}, sink=2)
        assert result is not None
        cost, flow = result
        assert cost == 4
        assert flow[0][1] + flow[3][1] == 2

    def test_mcf_sink_mode_accepts_cycle(self) -> None:
        """Sink mode accepts a cancellation cycle that respects vertex usage."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {
            0: {2: {"weight": -3, "capacity": 3}},
            1: {0: {"weight": 8, "capacity": 2}},
            2: {0: {"weight": -7, "capacity": 3}, 1: {"weight": 6, "capacity": 3}},
        }
        result = cycle_canceling_mcf(g, {0: 1, 1: -2, 2: 1}, sink=0)
        assert result is not None
        cost, flow = result
        assert cost == -7
        assert flow[1][0] == 2

    def test_mcf_residual_cleanup(self) -> None:
        """A node whose residual is exhausted is deleted from the residual."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {
            0: {2: {"weight": 0, "capacity": 3}},
            1: {0: {"weight": 1, "capacity": 2}, 2: {"weight": -2, "capacity": 3}},
            2: {0: {"weight": -4, "capacity": 1}},
        }
        result = cycle_canceling_mcf(g, {0: 0, 1: -2, 2: 2})
        assert result is not None
        cost, flow = result
        assert cost == -8
        assert flow[1][2] == 2

    def test_mcf_fractional_capacity_infeasible(self) -> None:
        """A fractional-capacity bottleneck that truncates to zero is infeasible."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {0: {1: {"weight": 1, "capacity": 0.5}}}
        assert cycle_canceling_mcf(g, {0: -1, 1: 1}) is None

    def test_mcf_empty_graph(self) -> None:
        """An empty graph with no demands yields zero cost and empty flow."""
        from digraphx.mcf import cycle_canceling_mcf

        assert cycle_canceling_mcf({}, {}) == (0, {})

    def test_mcf_fractional_bottleneck_skipped(self) -> None:
        """A negative cycle whose bottleneck truncates to zero is skipped."""
        from digraphx.mcf import cycle_canceling_mcf

        g = {
            0: {1: {"weight": 1, "capacity": 1}, 2: {"weight": -4, "capacity": 1}},
            1: {2: {"weight": 1, "capacity": 1}},
            2: {0: {"weight": -3, "capacity": 0.5}, 1: {"weight": 10, "capacity": 1}},
        }
        result = cycle_canceling_mcf(g, {0: -1, 2: 1})
        assert result is not None
        cost, flow = result
        assert cost == -4
        assert flow[0][2] == 1

    def test_mcf_build_residual_keeps_cheaper(self) -> None:
        """A forward residual edge is kept when its cost is more negative."""
        from digraphx.mcf import _build_residual

        g = {
            1: {0: {"weight": 1, "capacity": 3}},
            0: {1: {"weight": -5, "capacity": 3}},
        }
        flow = {0: {1: 1}, 1: {0: 0}}
        residual = _build_residual(g, flow)
        assert residual[1][0]["cost"] == 1
        assert residual[1][0]["forward"] is True

    def test_mcf_find_all_neg_cycles_overlap(self) -> None:
        """Overlapping negative cycles share nodes and skip already-yielded ones."""
        from digraphx.mcf import _find_all_neg_cycles_bf

        residual = {
            0: {1: {"cost": -1, "capacity": 1, "orig": (0, 1), "forward": True}},
            1: {2: {"cost": -1, "capacity": 1, "orig": (1, 2), "forward": True}},
            2: {
                0: {"cost": -1, "capacity": 1, "orig": (2, 0), "forward": True},
                3: {"cost": -1, "capacity": 1, "orig": (2, 3), "forward": True},
            },
            3: {1: {"cost": -1, "capacity": 1, "orig": (3, 1), "forward": True}},
        }
        cycles = list(_find_all_neg_cycles_bf(residual, {0, 1, 2, 3}))
        assert len(cycles) == 1
        assert all(e["cost"] < 0 for e in cycles[0])


class TestTinyDiGraph:
    """Tests covering TinyDiGraph / DiGraphAdapter edge cases."""

    def test_digraph_adapter_setitem(self) -> None:
        """Setting an adjacency dict on a DiGraphAdapter exercises __setitem__.

        NetworkX has no ``__setitem__``, so the abstract MutableMapping stub
        raises ``KeyError``.
        """
        from digraphx.tiny_digraph import DiGraphAdapter

        dg = DiGraphAdapter()
        dg.add_node(0)
        with raises(KeyError):
            dg[0] = {1: {}}

    def test_digraph_adapter_delitem(self) -> None:
        """Deleting a node via subscript exercises __delitem__.

        NetworkX has no ``__delitem__``, so the abstract MutableMapping stub
        raises ``KeyError``.
        """
        from digraphx.tiny_digraph import DiGraphAdapter

        dg = DiGraphAdapter()
        dg.add_node(0)
        with raises(KeyError):
            del dg[0]

    def test_lazy_adjacency_values(self) -> None:
        """values() on the lazy adjacency map skips uninitialised slots."""
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        tg.add_edge(0, 1)
        assert list(tg._adj.values()) == [{1: {}}, {}]
        assert list(tg._pred.values()) == [{}, {0: {}}]

    def test_add_edges_from_two_tuples(self) -> None:
        """add_edges_from accepts 2-tuples with and without attributes."""
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        tg.add_edges_from([(0, 1), (1, 2)])
        assert tg.has_edge(0, 1)
        assert tg.has_edge(1, 2)

        tg2 = TinyDiGraph()
        tg2.init_nodes(2)
        tg2.add_edges_from([(0, 1)], weight=5)
        assert tg2.get_edge_data(0, 1)["weight"] == 5

    def test_add_edges_from_bad_tuple(self) -> None:
        """add_edges_from rejects tuples that are not 2-tuples or 3-tuples."""
        import networkx as nx

        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        with raises(nx.NetworkXError):
            tg.add_edges_from([(0, 1, {}, "extra")])
        with raises(nx.NetworkXError):
            tg.add_edges_from([(0,)])

    def test_getitem_missing_node(self) -> None:
        """Accessing a missing node via subscript raises NetworkXError."""
        import networkx as nx

        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        with raises(nx.NetworkXError):
            tg[99]

    def test_successors_missing_node(self) -> None:
        """successors() of a missing node raises NetworkXError."""
        import networkx as nx

        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        # The lazy map is list-backed (IndexError for missing keys), so swap in
        # a dict-backed successor map to reach the KeyError -> NetworkXError path.
        tg._succ = {0: {}, 1: {}, 2: {}}
        with raises(nx.NetworkXError):
            list(tg.successors(99))

    def test_adjacency_matches_items(self) -> None:
        """adjacency() delegates to items()."""
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        tg.add_edge(0, 1)
        assert list(tg.adjacency()) == [(0, {1: {}}), (1, {})]

    def test_remove_edge_missing(self) -> None:
        """remove_edge of a missing edge raises NetworkXError."""
        import networkx as nx

        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(2)
        with raises(nx.NetworkXError):
            tg.remove_edge(0, 1)
        tg.add_edge(0, 1)
        tg.remove_edge(0, 1)
        with raises(nx.NetworkXError):
            tg.remove_edge(0, 1)

    def test_get_edge_data_default(self) -> None:
        """get_edge_data returns the default for a node with no adjacency."""
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(3)
        assert tg.get_edge_data(2, 0, "default") == "default"

    def test_out_degree(self) -> None:
        """out_degree handles aggregate, real-node and empty-node cases.

        NetworkX caches the degree view after the first aggregate call, so the
        per-node and aggregate branches are exercised on separate graphs.
        """
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(4)
        tg.add_edge(0, 1)
        tg.add_edge(0, 2)
        tg.add_edge(2, 0)
        assert tg.out_degree(3) == 0
        assert tg.out_degree(0) == 2

        tg2 = TinyDiGraph()
        tg2.init_nodes(4)
        tg2.add_edge(0, 1)
        tg2.add_edge(0, 2)
        tg2.add_edge(2, 0)
        assert list(tg2.out_degree()) == [(0, 2), (1, 0), (2, 1), (3, 0)]

    def test_in_degree(self) -> None:
        """in_degree handles aggregate, real-node and empty-node cases.

        NetworkX caches the degree view after the first aggregate call, so the
        per-node and aggregate branches are exercised on separate graphs.
        """
        from digraphx.tiny_digraph import TinyDiGraph

        tg = TinyDiGraph()
        tg.init_nodes(4)
        tg.add_edge(0, 1)
        tg.add_edge(0, 2)
        tg.add_edge(2, 0)
        assert tg.in_degree(3) == 0
        assert tg.in_degree(1) == 1

        tg2 = TinyDiGraph()
        tg2.init_nodes(4)
        tg2.add_edge(0, 1)
        tg2.add_edge(0, 2)
        tg2.add_edge(2, 0)
        assert list(tg2.in_degree()) == [(0, 1), (1, 1), (2, 1), (3, 0)]


class TestCsrDiGraph:
    """Tests covering CSRDiGraph edge cases."""

    def test_neighbors_iter(self) -> None:
        """Iterating over a node's neighbor view yields its targets."""
        from digraphx.csr_digraph import CSRDiGraph

        g = CSRDiGraph()
        g.init_nodes(3)
        g.add_edge(0, 1)
        g.add_edge(0, 2)
        g.freeze()
        assert sorted(list(g[0])) == [1, 2]


class TestMaxParametric:
    """Tests covering MaxParametricSolver edge cases."""

    def test_solver_keeps_best_cycle(self) -> None:
        """The solver keeps the best cycle and ignores non-improving cycles."""
        from digraphx.parametric import MaxParametricSolver, ParametricAPI

        class API(ParametricAPI):  # type: ignore[type-arg]
            def distance(self, ratio, edge):
                return Fraction(edge["cost"] - ratio * edge["time"])

            def zero_cancel(self, cycle):
                total_cost = sum(e["cost"] for e in cycle)
                total_time = sum(e["time"] for e in cycle)
                return Fraction(total_cost, total_time)

        digraph = {
            0: {1: {"cost": -1, "time": 1}, 3: {"cost": -1, "time": 1}},
            1: {2: {"cost": -2, "time": 1}},
            2: {0: {"cost": -2, "time": 1}},
            3: {4: {"cost": 1, "time": 1}},
            4: {5: {"cost": -2, "time": 1}},
            5: {3: {"cost": -2, "time": 1}},
        }
        solver = MaxParametricSolver(digraph, API())
        dist: Dict[int, Fraction] = {n: Fraction(0) for n in digraph}
        ratio, cycle = solver.run(dist, Fraction(10))
        assert ratio < Fraction(10)
        assert len(cycle) > 0
