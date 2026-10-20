"""Shared implementation core for the parametric solvers.

This module centralises the parametric-search loop (Template Method) shared by
:class:`MaxParametricSolver` (parametric.py) and :class:`MinParametricSolver`
(min_parametric_q.py).  The two things that used to be encoded as keyword flags
are injected as strategies instead:

* :class:`KeepSmaller` / :class:`KeepLarger` decide which cycle ratio wins and
  when the search has converged.  The names describe the behaviour, so call
  sites no longer read as if their meaning were inverted.
* :class:`HowardSearch` / :class:`AlternatingSearch` decide which cycles are
  produced each round; the alternation state lives in the strategy that uses it.

It is an implementation detail of the package; the public API lives in
``parametric`` / ``min_parametric_q`` and is unchanged.
"""

from typing import Callable, Iterator, MutableMapping, Protocol, Tuple

from ._parametric_api import ParametricAPI
from ._types import Arc, Cycle, Domain, Graph, Node, Ratio
from .neg_cycle import NegCycleFinder
from .neg_cycle_q import NegCycleFinderQ

__all__ = [
    "AlternatingSearch",
    "CycleSearch",
    "HowardSearch",
    "KeepLarger",
    "KeepSmaller",
    "RatioDirection",
    "parametric_search",
]


class RatioDirection(Protocol[Ratio]):
    """Which ratio wins, and when to stop looking for a better one."""

    def better(self, candidate: Ratio, best: Ratio) -> bool:
        ...

    def converged(self, best: Ratio, current: Ratio) -> bool:
        ...


class KeepSmaller:
    """Keep the smallest cycle ratio; stop once the incumbent stops falling."""

    def better(self, candidate: Ratio, best: Ratio) -> bool:
        return candidate < best

    def converged(self, best: Ratio, current: Ratio) -> bool:
        return best >= current


class KeepLarger:
    """Keep the largest cycle ratio; stop once the incumbent stops rising."""

    def better(self, candidate: Ratio, best: Ratio) -> bool:
        return candidate > best

    def converged(self, best: Ratio, current: Ratio) -> bool:
        return best <= current


class CycleSearch(Protocol[Node, Arc, Domain]):
    """Produces the negative cycles of one relaxation round."""

    def cycles(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> Iterator[Cycle]:
        ...


class HowardSearch:
    """Single-direction Howard search (predecessor relaxation)."""

    def __init__(self, digraph: Graph) -> None:
        self._finder: NegCycleFinder[Node, Arc, Domain] = NegCycleFinder(digraph)

    def cycles(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> Iterator[Cycle]:
        return self._finder.howard(dist, get_weight)


class AlternatingSearch:
    """Alternates successor and predecessor relaxation between rounds.

    The alternation is what lets the constrained solver escape the corner where
    one relaxation direction alone keeps re-finding the same cycle.
    """

    def __init__(
        self,
        digraph: Graph,
        update_ok: Callable[[Domain, Domain], bool],
    ) -> None:
        self._finder: NegCycleFinderQ[Node, Arc, Domain] = NegCycleFinderQ(digraph)
        self._update_ok = update_ok
        self._reverse = True

    def cycles(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> Iterator[Cycle]:
        if self._reverse:
            found = self._finder.howard_succ(dist, get_weight, self._update_ok)
        else:
            found = self._finder.howard_pred(dist, get_weight, self._update_ok)
        self._reverse = not self._reverse
        return found


def parametric_search(
    omega: ParametricAPI[Node, Arc, Ratio],
    dist: MutableMapping[Node, Domain],
    ratio: Ratio,
    direction: RatioDirection[Ratio],
    search: CycleSearch[Node, Arc, Domain],
    *,
    first_only: bool = False,
) -> Tuple[Ratio, Cycle]:
    """Template Method: the parametric-search loop.

    Repeatedly finds negative cycles at the current ratio and moves the ratio to
    the best cycle ratio found, until no cycle improves it.

    Returns ``(final_ratio, critical_cycle)``.
    """
    if not dist:
        return ratio, []

    def get_weight(e: Arc) -> Domain:
        return omega.distance(ratio, e)

    ratio_best = ratio
    cycle_best: Cycle = []
    cycle: Cycle = []

    while True:
        for c_i in search.cycles(dist, get_weight):
            ratio_i = omega.zero_cancel(c_i)
            if direction.better(ratio_i, ratio_best):
                ratio_best = ratio_i
                cycle_best = c_i
                if first_only:
                    break

        if direction.converged(ratio_best, ratio):
            break

        cycle = cycle_best
        ratio = ratio_best

    return ratio, cycle
