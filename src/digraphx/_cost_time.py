"""A parametric API for edges described by a ``(cost, time)`` column pair.

The CSS objective facades and :class:`~digraphx.min_cycle_ratio.CycleRatioAPI`
all solve the same ``min sum(cost) / sum(time)`` problem; they differ only in
which two columns of an edge they read.  That arithmetic is implemented once
here and the callers supply the extractor.
"""

from typing import Any, Callable, Tuple, Type

from ._parametric_api import ParametricAPI
from ._types import Cycle

CostTime = Callable[[Any], Tuple[Any, Any]]
"""Maps an edge to its ``(cost, time)`` column values."""


def default_cost_time(edge: Any) -> Tuple[Any, Any]:
    return edge["cost"], edge["time"]


class CostTimeAPI(ParametricAPI):
    """Parametric distance ``cost(e) - ratio * time(e)``.

    ``result_type`` is the arithmetic domain of the ratio: ``Fraction`` for
    exact answers, ``float`` otherwise.  Costs are converted before the
    subtraction so exact arithmetic is preserved end to end.

    A cycle with zero total time has an undefined ratio; ``inf`` is returned
    rather than raising, which is the only representation a float-valued caller
    can act on.
    """

    def __init__(
        self,
        cost_time: CostTime = default_cost_time,
        result_type: Type = float,
    ) -> None:
        self._cost_time = cost_time
        self._result_type = result_type

    def distance(self, ratio: Any, edge: Any) -> Any:
        cost, time = self._cost_time(edge)
        return self._result_type(cost) - ratio * time

    def zero_cancel(self, cycle: Cycle) -> Any:
        total_cost = 0
        total_time = 0
        for edge in cycle:
            cost, time = self._cost_time(edge)
            total_cost += cost
            total_time += time
        if not total_time:
            return float("inf")
        return self._result_type(total_cost) / total_time
