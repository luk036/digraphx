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

``css_ratio`` solves ``min_C sum(cost)/sum(time)`` for any such columns
and is the single code path shared by the objective facades.
"""

from typing import Any, Mapping, MutableMapping, Optional, Tuple

from ._cost_time import CostTime, CostTimeAPI, default_cost_time
from ._types import Cycle, Node
from .parametric import MaxParametricSolver

HI = 1e12
"""Finite initial ratio; the parametric solver rejects ``inf``."""


def css_ratio(
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
    omega = CostTimeAPI(cost_time or default_cost_time, float)
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

    return css_ratio(g, dist, hi, cost_time=cost_time)


def prop(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """PROP: variance-proportional slack (edges carry ``cost`` / ``time``)."""
    return css_ratio(g, dist, hi)


def cprop(
    g: Mapping[Node, Mapping[Node, Any]],
    dist: MutableMapping[Node, float],
    hi: float = HI,
) -> Tuple[float, Cycle]:
    """C-PROP: minimum cost-to-time ratio cycle (edges carry ``mu`` / ``sigma``)."""

    def cost_time(e: Any) -> Tuple[float, float]:
        return e["mu"], e["sigma"]

    return css_ratio(g, dist, hi, cost_time=cost_time)


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

    ratio, cycle = css_ratio(g, dist, hi, cost_time=cost_time)
    return -ratio, cycle
