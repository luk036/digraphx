"""Clock Skew Scheduling (CSS) solvers.

Single-parameter clock-skew scheduling, expressed as one min-ratio-cycle
engine.  Every member of the paper's family -- minimum clock period, EVEN,
PROP, and C-PROP -- is the *same* parametric potential problem with a
different ``(cost, time)`` column; they differ only in the graph that is
built, not in the solver.

+----------+----------------------------+-----------------------+
| Problem  | ``cost``                   | ``time``              |
+==========+============================+=======================+
| Min CP   | ``-delay`` (setup) /       | ``1`` (setup) /       |
|          | ``+delay`` (hold)          | ``0`` (hold)          |
+----------+----------------------------+-----------------------+
| EVEN     | ``delay``                  | ``1`` / ``0`` (pass)  |
+----------+----------------------------+-----------------------+
| PROP     | ``cost``                   | ``time``              |
+----------+----------------------------+-----------------------+
| C-PROP   | ``mu``                     | ``sigma``             |
+----------+----------------------------+-----------------------+

``min_cycle_ratio`` solves ``min_C sum(cost)/sum(time)`` for any such columns
and is the single code path shared by the objective facades.
"""

from typing import Any, Callable, Mapping, MutableMapping, Optional, Tuple

from .neg_cycle import Cycle, Node
from .parametric import MaxParametricSolver, ParametricAPI

HI = 1e12
"""Finite initial ratio; the parametric solver rejects ``inf``."""

CostTime = Callable[[Any], Tuple[float, float]]
"""Maps an edge to its ``(cost, time)`` column values."""


class _Ratio(ParametricAPI[Any, Any, float]):
    def __init__(self, cost_time: CostTime) -> None:
        self._cost_time = cost_time

    def distance(self, ratio: float, edge: Any) -> float:
        cost, time = self._cost_time(edge)
        return cost - ratio * time

    def zero_cancel(self, cycle: Any) -> float:
        cost = sum(self._cost_time(e)[0] for e in cycle)
        time = sum(self._cost_time(e)[1] for e in cycle)
        return cost / time if time else float("inf")


def _default_cost_time(edge: Any) -> Tuple[float, float]:
    return edge["cost"], edge["time"]


def min_cycle_ratio(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
    *,
    cost_time: Optional[CostTime] = None,
) -> Tuple[float, Cycle]:
    """Minimum cost-to-time ratio cycle.

    Returns ``(ratio, cycle)`` where ``ratio = min_C sum(cost)/sum(time)``
    over all cycles ``C`` (``hi`` if the graph has no cycle).

    ``cost_time`` maps an edge to ``(cost, time)``; by default edges are
    assumed to be mappings with keys ``"cost"`` and ``"time"``.
    """
    omega = _Ratio(cost_time or _default_cost_time)
    return MaxParametricSolver(g, omega).run(dist, hi)


def even(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """EVEN: maximum uniform slack.

    Edges are ``{"type": ..., "delay": d}``; a ``"p"`` (pass-through) edge
    contributes delay but no slack, so it has ``time == 0``.
    """

    def cost_time(e: Any) -> Tuple[float, float]:
        return e["delay"], 0.0 if e["type"] == "p" else 1.0

    return min_cycle_ratio(g, dist, hi, cost_time=cost_time)


def prop(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """PROP: variance-proportional slack (edges carry ``cost`` / ``time``)."""
    return min_cycle_ratio(g, dist, hi)


def cprop(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """C-PROP: minimum cost-to-time ratio cycle (edges carry ``mu`` / ``sigma``)."""

    def cost_time(e: Any) -> Tuple[float, float]:
        return e["mu"], e["sigma"]

    return min_cycle_ratio(g, dist, hi, cost_time=cost_time)


def min_clock_period(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """Minimum feasible clock period.

    Edges are ``{"type": "s"|"h", "delay": d}``.  The smallest feasible
    period is the *maximum* cycle ratio, so it is computed as the negated
    minimum ratio of the transformed ``(cost, time)`` columns.
    """

    def cost_time(e: Any) -> Tuple[float, float]:
        return (-e["delay"], 1.0) if e["type"] == "s" else (e["delay"], 0.0)

    ratio, cycle = min_cycle_ratio(g, dist, hi, cost_time=cost_time)
    return -ratio, cycle
