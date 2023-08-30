# -*- coding: utf-8 -*-
from __future__ import print_function

from fractions import Fraction

from digraphx.lict import Lict
from digraphx.min_cycle_ratio import MinCycleRatioSolver, set_default

from .test_neg_cycle import (
    create_test_case1,
    create_test_case_timing,
    create_tiny_graph,
)


def test_cycle_ratio_raw():
    gra = {
        "a0": {"a1": {"cost": 7, "time": 1}, "a2": {"cost": 5, "time": 1}},
        "a1": {"a0": {"cost": 0, "time": 1}, "a2": {"cost": 3, "time": 1}},
        "a2": {"a1": {"cost": 1, "time": 1}, "a0": {"cost": 2, "time": 1}},
    }
    dist = {vtx: 0 for vtx in gra}
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(2, 1)


def test_cycle_ratio():
    gra = create_test_case1()
    set_default(gra, "time", 1)
    set_default(gra, "cost", 1)
    gra[1][2]["cost"] = 5
    dist = {vtx: 0 for vtx in gra}
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing():
    gra = create_test_case_timing()
    set_default(gra, "time", 1)
    gra["a1"]["a2"]["cost"] = 7
    gra["a2"]["a1"]["cost"] = -1
    gra["a2"]["a3"]["cost"] = 3
    gra["a3"]["a2"]["cost"] = 0
    gra["a3"]["a1"]["cost"] = 2
    gra["a1"]["a3"]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = {vtx: Fraction(0, 1) for vtx in gra}
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)


def test_cycle_ratio_tiny_graph():
    gra = create_tiny_graph()
    set_default(gra, "time", 1)
    gra[0][1]["cost"] = 7
    gra[1][0]["cost"] = -1
    gra[1][2]["cost"] = 3
    gra[2][1]["cost"] = 0
    gra[2][0]["cost"] = 2
    gra[0][2]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = Lict([0 for _ in range(3)])
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)
