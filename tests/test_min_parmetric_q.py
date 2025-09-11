# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction

from digraphx.min_parmetric_q import MinParametricAPI, MinParametricSolver


class MyAPI(MinParametricAPI):
    def distance(self, ratio, edge):
        return edge["cost"] - ratio * edge["time"]

    def zero_cancel(self, cycle):
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return Fraction(total_cost, total_time)


def test_min_parametric_q():
    digraph = {
        "a0": {"a1": {"cost": 7, "time": 1}, "a2": {"cost": 5, "time": 1}},
        "a1": {"a0": {"cost": 0, "time": 1}, "a2": {"cost": 3, "time": 1}},
        "a2": {"a1": {"cost": 1, "time": 1}, "a0": {"cost": 2, "time": 1}},
    }
    dist = {vtx: 10000 for vtx in digraph}
    solver = MinParametricSolver(digraph, MyAPI())
    ratio, cycle = solver.run(dist, Fraction(0), lambda D, d: D > d)
    print(ratio, cycle)
    assert ratio == Fraction(0, 1)
    assert cycle == []
