"""Min Parametric Solver with constraints

This code defines a system for solving a specific type of network optimization
problem called a "minimum parametric problem." The purpose of this code is to
find the smallest possible value for a parameter (called a ratio) that
satisfies certain conditions in a graph-like structure.

The code takes as input a graph (represented as a mapping of nodes and edges),
an initial set of distances between nodes, and a starting ratio. It then works
to find the smallest ratio that meets the problem's constraints.

The main output of the code is a tuple containing two things: the final
(minimum) ratio found, and a cycle in the graph that corresponds to this ratio.

To achieve its purpose, the code uses an algorithm that repeatedly searches for
cycles in the graph that could potentially lower the ratio. It does this by
using a "negative cycle finder" (NCF) which looks for cycles where the sum of
the distances (adjusted by the current ratio) is negative. If such a cycle is
found, it means the ratio can be lowered further.

The main logic flow involves a loop that alternates between searching for cycles
and updating the ratio. Each time a cycle is found that allows for a lower
ratio, the ratio is updated. This process continues until no more improvements
can be made - at this point, the minimum ratio has been found.

An important part of the algorithm is the ability to switch between searching
for cycles in the forward direction (successor nodes) and the backward
direction (predecessor nodes). This helps to explore the graph more thoroughly
and find the best possible solution.

The code is designed to be flexible, allowing for different types of numbers
(integers, fractions, or floating-point numbers) to be used for distances and
ratios. It also includes an abstract base class (MinParametricAPI) that defines
the interface for calculating distances and handling cycles, allowing for
different implementations of these operations.

Overall, this code provides a framework for solving complex network
optimization problems, particularly those where a single parameter needs to be
minimized while satisfying constraints across the entire network.
"""

from typing import Callable, Generic, Mapping, MutableMapping, Tuple

from ._parametric_api import ParametricAPI
from ._parametric_base import AlternatingSearch, KeepLarger, parametric_search
from ._types import Arc, Cycle, Domain, Node, Ratio


class MinParametricAPI(ParametricAPI[Node, Arc, Ratio]):
    """Name kept for callers of the constrained solver.

    It deliberately adds no methods: both the maximizing and the minimizing
    solver consume the same two operations, so the interface lives in one place.
    """


class MinParametricSolver(Generic[Node, Arc, Ratio, Domain]):
    """Minimum Parametric Solver with constraints

    This class solves the following parametric network problem:

    |    min  r
    |    s.t. dist[v] - dist[u] <= distrance(e, r)
    |         forall e(u, v) in G(V, E)

    A parametric network problem refers to a type of optimization problem that
    involves finding the optimal solution to a network flow problem as a
    function of one single parameter.
    """

    def __init__(
        self,
        digraph: Mapping[Node, Mapping[Node, Arc]],
        omega: MinParametricAPI[Node, Arc, Ratio],
    ) -> None:
        """Initialize the minimum parametric solver with a graph and parametric API.

        Args:
            digraph: A directed graph represented as a mapping where keys are source
                nodes and values are mappings of {target_node: edge} pairs.
            omega: A MinParametricAPI instance that provides methods for calculating
                edge distances and finding the ratio that zeroes out cycle costs.

        Example:
            >>> from fractions import Fraction
            >>> digraph = {'a': {'b': {'cost': 5, 'time': 1}}}
            >>> omega = MinParametricAPI()  # Requires concrete implementation
        """
        self.digraph = digraph
        self.omega: MinParametricAPI[Node, Arc, Ratio] = omega

    def run(
        self,
        dist: MutableMapping[Node, Domain],
        ratio: Ratio,
        update_ok: Callable[[Domain, Domain], bool],
        pick_one_only: bool = False,
    ) -> Tuple[Ratio, Cycle]:
        """
        The `run` function executes the parametric solver algorithm to find the
        minimum ratio.

        :param dist: A mutable mapping of node distances that will be updated
            during the algorithm. Represents the current distance estimates
            between nodes.
        :type dist: MutableMapping[Node, Domain]
        :param ratio: The initial ratio value to start the optimization from.
        :type ratio: Ratio
        :param update_ok: A callback function that determines whether a distance
            update is acceptable. Takes current and new distance values, returns
            True if update should proceed.
        :type update_ok: Callable[[Domain, Domain], bool]
        :param pick_one_only: If True, stops after finding the first improving
            cycle. Defaults to False.
        :type pick_one_only: bool
        :return: A tuple containing:
                 - The minimum ratio found (ratio)
                 - The cycle that corresponds to this ratio (cycle)
        """
        return parametric_search(
            self.omega,
            dist,
            ratio,
            KeepLarger(),
            AlternatingSearch(self.digraph, update_ok),
            first_only=pick_one_only,
        )
