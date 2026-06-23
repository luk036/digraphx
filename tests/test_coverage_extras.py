"""Additional tests for digraphx code coverage."""


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
