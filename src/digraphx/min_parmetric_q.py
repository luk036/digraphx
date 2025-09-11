"""
Min Parametric Solver

This code defines a system for solving a specific type of network optimization problem called a "minimum parametric problem." The purpose of this code is to find the smallest possible value for a parameter (called a ratio) that satisfies certain conditions in a graph-like structure.

The code takes as input a graph (represented as a mapping of nodes and edges), an initial set of distances between nodes, and a starting ratio. It then works to find the smallest ratio that meets the problem's constraints.

The main output of the code is a tuple containing two things: the final (minimum) ratio found, and a cycle in the graph that corresponds to this ratio.

To achieve its purpose, the code uses an algorithm that repeatedly searches for cycles in the graph that could potentially lower the ratio. It does this by using a "negative cycle finder" (NCF) which looks for cycles where the sum of the distances (adjusted by the current ratio) is negative. If such a cycle is found, it means the ratio can be lowered further.

The main logic flow involves a loop that alternates between searching for cycles and updating the ratio. Each time a cycle is found that allows for a lower ratio, the ratio is updated. This process continues until no more improvements can be made - at this point, the minimum ratio has been found.

An important part of the algorithm is the ability to switch between searching for cycles in the forward direction (successor nodes) and the backward direction (predecessor nodes). This helps to explore the graph more thoroughly and find the best possible solution.

The code is designed to be flexible, allowing for different types of numbers (integers, fractions, or floating-point numbers) to be used for distances and ratios. It also includes an abstract base class (MinParametricAPI) that defines the interface for calculating distances and handling cycles, allowing for different implementations of these operations.

Overall, this code provides a framework for solving complex network optimization problems, particularly those where a single parameter needs to be minimized while satisfying constraints across the entire network.
"""

from abc import abstractmethod
from fractions import Fraction
from typing import Callable, Generic, Mapping, MutableMapping, Tuple, TypeVar

from .neg_cycle_q import Cycle, Edge, NegCycleFinder, Node

# Define type variables for domain (numeric types) and ratio (fraction or float)
Domain = TypeVar("Domain", int, Fraction, float)  # Comparable Ring
Ratio = TypeVar("Ratio", Fraction, float)


class MinParametricAPI(Generic[Node, Edge, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Edge) -> Ratio:
        """
        The `distance` function calculates the distance between a given ratio and edge.
        This is an abstract method that must be implemented by concrete subclasses.

        :param ratio: The `ratio` parameter is of type `Ratio`. It represents a ratio or proportion
                      that affects the distance calculation.
        :type ratio: Ratio
        :param edge: The `edge` parameter represents an edge in a graph. It is of type `Edge`
        :type edge: Edge
        :return: The calculated distance based on the given ratio and edge
        :rtype: Ratio
        """
        pass

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """
        The `zero_cancel` function takes a `Cycle` object as input and returns a `Ratio` object.
        This calculates the ratio that would make the cycle's total distance sum to zero.

        :param cycle: The `cycle` parameter is of type `Cycle`. It represents a cycle in the graph
                      that needs to be evaluated.
        :type cycle: Cycle
        :return: The ratio that would make the cycle's total distance zero
        :rtype: Ratio
        """
        pass


class MinParametricSolver(Generic[Node, Edge, Ratio]):
    """Minimum Parametric Solver

    This class solves the following parametric network problem:

    |    min  r
    |    s.t. dist[v] - dist[u] <= distrance(e, r)
    |         forall e(u, v) in G(V, E)

    A parametric network problem refers to a type of optimization problem that
    involves finding the optimal solution to a network flow problem as a function
    of one single parameter.
    """

    def __init__(
        self,
        digraph: Mapping[Node, Mapping[Node, Edge]],
        omega: MinParametricAPI[Node, Edge, Ratio],
    ) -> None:
        """
        The `__init__` function initializes the solver with a graph and parametric API.

        :param digraph: A mapping representing a directed graph where each node maps to its
                       neighbors and the edges connecting them. This defines the network structure
                       that the solver will work with.
        :type digraph: Mapping[Node, Mapping[Node, Edge]]
        :param omega: An instance of MinParametricAPI that provides the necessary methods
                     for distance calculation and cycle analysis. This parameterizes the
                     solver's behavior.
        :type omega: MinParametricAPI[Node, Edge, Ratio]
        """
        # self.ncf = NegCycleFinder(digraph)
        self.digraph = digraph
        self.omega: MinParametricAPI[Node, Edge, Ratio] = omega

    def run(
        self,
        dist: MutableMapping[Node, Domain],
        ratio: Ratio,
        update_ok: Callable[[Domain, Domain], bool],
        pick_one_only=False,
    ) -> Tuple[Ratio, Cycle]:
        """
        The `run` function executes the parametric solver algorithm to find the minimum ratio.

        :param dist: A mutable mapping of node distances that will be updated during the algorithm.
                    Represents the current distance estimates between nodes.
        :type dist: MutableMapping[Node, Domain]
        :param ratio: The initial ratio value to start the optimization from.
        :type ratio: Ratio
        :param update_ok: A callback function that determines whether a distance update is acceptable.
                         Takes current and new distance values, returns True if update should proceed.
        :type update_ok: Callable[[Domain, Domain], bool]
        :param pick_one_only: If True, stops after finding the first improving cycle. Defaults to False.
        :type pick_one_only: bool
        :return: A tuple containing:
                 - The minimum ratio found (ratio)
                 - The cycle that corresponds to this ratio (cycle)
        """
        # Determine the numeric type used in distance calculations
        D = type(next(iter(dist.values())))

        # Helper function to calculate edge weights based on current ratio
        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        # Initialize tracking variables for minimum ratio and corresponding cycle
        r_max = ratio
        c_max = []
        cycle = []
        reverse: bool = True  # Flag to alternate search direction

        # Initialize the negative cycle finder with our graph
        ncf: NegCycleFinder[Node, Edge, Domain] = NegCycleFinder(self.digraph)

        # Main optimization loop
        while True:
            # Search for cycles in either forward or reverse direction
            if reverse:
                cycles = ncf.howard_succ(dist, get_weight, update_ok)
            else:
                cycles = ncf.howard_pred(dist, get_weight, update_ok)

            # Evaluate all found cycles
            for c_i in cycles:
                r_i = self.omega.zero_cancel(c_i)
                if r_max < r_i:
                    r_max = r_i
                    c_max = c_i
                    if pick_one_only:  # Early exit if we only need one improvement
                        break

            # Termination condition: no better ratio found
            if r_max <= ratio:
                break

            # Update state for next iteration
            cycle = c_max
            ratio = r_max
            reverse = not reverse  # Alternate search direction

        return ratio, cycle
