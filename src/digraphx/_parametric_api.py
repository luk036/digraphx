"""The single parametric-API interface consumed by every ratio solver.

The interface is structural: any object with these two methods is accepted, and
callers rely on that (duck-typed strategies are passed in several places), so
this ABC exists to document the contract and to reject incomplete subclasses,
not to gate arguments.
"""

from abc import ABC, abstractmethod
from typing import Generic

from ._types import Arc, Cycle, Node, Ratio


class ParametricAPI(ABC, Generic[Node, Arc, Ratio]):
    """Interface for the parametric distance family ``dist(e, r)``.

    Args:
        ratio: the current value of the parameter ``r``.
        edge: the edge whose parametric distance is requested.
        cycle: the edges of a cycle, in traversal order.

    Examples:
        >>> from fractions import Fraction
        >>> class CostTime(ParametricAPI):
        ...     def distance(self, ratio, edge):
        ...         return edge["cost"] - ratio * edge["time"]
        ...     def zero_cancel(self, cycle):
        ...         return sum(e["cost"] for e in cycle) / sum(
        ...             e["time"] for e in cycle
        ...         )
        >>> api = CostTime()
        >>> api.distance(Fraction(2), {"cost": 5, "time": 1})
        Fraction(3, 1)
    """

    @abstractmethod
    def distance(self, ratio: Ratio, edge: Arc) -> Ratio:
        """Return ``dist(edge, ratio)`` for the current parameter value."""

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """Return the ratio at which ``cycle`` has zero total distance."""
