"""Tests for min-cost flow cycle-cancellation."""

from typing import Dict

import pytest

from digraphx.mcf import cycle_canceling_mcf


def _graph_2node():
    """Simple two-node graph."""
    return {
        0: {1: {"weight": 5, "capacity": 3}},
    }


def test_simple_flow():
    g = _graph_2node()
    demands = {0: -2, 1: 2}
    result = cycle_canceling_mcf(g, demands)
    assert result is not None
    total_cost, flow = result
    assert total_cost == 10
    assert flow[0][1] == 2


def test_zero_demand():
    g = {0: {1: {"weight": 5, "capacity": 3}}}
    demands = {0: 0, 1: 0}
    result = cycle_canceling_mcf(g, demands)
    assert result is not None
    total_cost, flow = result
    assert total_cost == 0
    assert flow[0].get(1, 0) == 0


def test_triangle_with_supply():
    g = {
        0: {1: {"weight": 2, "capacity": 5}},
        1: {0: {"weight": 3, "capacity": 5}},
    }
    demands = {0: -1, 1: 1}
    result = cycle_canceling_mcf(g, demands)
    assert result is not None
    total_cost, flow = result
    assert total_cost == 2
    assert flow[0][1] == 1
    assert flow[1].get(0, 0) == 0


def test_multiple_paths():
    g = {
        0: {
            1: {"weight": 10, "capacity": 1},
            2: {"weight": 3, "capacity": 1},
        },
        1: {3: {"weight": 1, "capacity": 1}},
        2: {3: {"weight": 1, "capacity": 1}},
    }
    demands = {0: -1, 3: 1, 1: 0, 2: 0}
    result = cycle_canceling_mcf(g, demands)
    assert result is not None
    total_cost, flow = result
    # Cheaper path: 0 -> 2 -> 3 (cost 4), vs 0 -> 1 -> 3 (cost 11)
    assert total_cost == 4


def test_cycle_cancels_expensive_path():
    g = {
        0: {
            1: {"weight": 1, "capacity": 1},
            2: {"weight": 10, "capacity": 1},
        },
        1: {3: {"weight": 1, "capacity": 1}},
        2: {3: {"weight": 1, "capacity": 1}},
    }
    demands = {0: -1, 3: 1, 1: 0, 2: 0}
    result = cycle_canceling_mcf(g, demands)
    assert result is not None
    total_cost, flow = result
    # Optimal: 0 -> 1 -> 3 (cost 2); expensive 0->2->3 should be cancelled
    assert total_cost == 2


def test_infeasible():
    g = {0: {1: {"weight": 1, "capacity": 0}}}
    demands = {0: -1, 1: 1}
    result = cycle_canceling_mcf(g, demands)
    assert result is None
