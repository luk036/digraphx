"""Shared implementation core for the parametric solvers.

This module centralises the parametric-search loop (Template Method) shared by
:class:`MaxParametricSolver` (parametric.py) and :class:`MinParametricSolver`
(min_parametric_q.py).  The ratio-comparison direction and the cycle-search
direction alternation are injected as strategies.

It is an implementation detail of the package; the public API lives in
``parametric`` / ``min_parametric_q`` and is unchanged.
"""

from typing import Callable, Generic, Mapping, MutableMapping, Tuple, TypeVar

from .neg_cycle import Arc, Cycle, Domain, NegCycleFinder, Node
from .neg_cycle_q import NegCycleFinderQ

Ratio = TypeVar("Ratio", int, float)  # Comparable Ring


class _API(Generic[Node, Arc, Ratio]):
    """Protocol-ish base for the parametric API strategies."""

    def distance(self, ratio: Ratio, edge: Arc) -> Ratio:
        raise NotImplementedError

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        raise NotImplementedError


def _run_loop(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    omega: _API,
    dist: MutableMapping[Node, Domain],
    ratio: Ratio,
    *,
    minimize: bool,
    update_ok: Callable[[Domain, Domain], bool] = lambda old, new: True,
    pick_one_only: bool = False,
    alternate_direction: bool = False,
) -> Tuple[Ratio, Cycle]:
    """Template Method: the parametric-search loop.

    Repeatedly finds negative cycles at the current ratio and updates the ratio
    until no improving cycle exists.  ``minimize`` selects the comparison
    direction; ``alternate_direction`` (with ``update_ok``) enables the
    predecessor/successor alternation used by the constrained solver.

    Returns ``(final_ratio, critical_cycle)``.
    """
    if not dist:  # empty graph case - return early with no cycle found
        return ratio, []

    DomainType = type(next(iter(dist.values())))

    # Define a weight function that calculates distance based on current ratio
    def get_weight(e: Arc) -> Domain:
        return DomainType(omega.distance(ratio, e))

    # Initialize min/max ratio and cycle
    ratio_best = ratio
    cycle_best = []
    cycle = []
    reverse: bool = True  # Flag to alternate search direction

    if alternate_direction:
        ncf: NegCycleFinderQ[Node, Arc, Domain] = NegCycleFinderQ(digraph)
    else:
        ncf = NegCycleFinder(digraph)

    # Main algorithm loop
    while True:
        if alternate_direction:
            # Search for cycles in either forward or reverse direction
            cycles = (
                ncf.howard_succ(dist, get_weight, update_ok)
                if reverse
                else ncf.howard_pred(dist, get_weight, update_ok)
            )
        else:
            cycles = ncf.howard(dist, get_weight)

        # Evaluate all found cycles
        for c_i in cycles:
            ratio_i = omega.zero_cancel(c_i)
            if (ratio_best > ratio_i) if minimize else (ratio_best < ratio_i):
                ratio_best = ratio_i
                cycle_best = c_i
                if pick_one_only:  # Early exit if we only need one improvement
                    break

        # Termination condition: no better ratio found
        if (ratio_best >= ratio) if minimize else (ratio_best <= ratio):
            break

        # Update state for next iteration
        cycle = cycle_best
        ratio = ratio_best
        if alternate_direction:
            reverse = not reverse  # Alternate search direction

    return ratio, cycle
