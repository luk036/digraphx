"""
Parametric Network Solver

This code defines a system for solving parametric network problems, which are a type of optimization problem in graph theory. The main purpose of this code is to find the maximum ratio that satisfies certain conditions in a graph, where the distances between nodes depend on this ratio.

The code takes two main inputs: a graph (represented as a mapping of nodes and edges) and an object that defines how to calculate distances based on the ratio. It produces two outputs: the maximum ratio that satisfies the conditions and a cycle in the graph that corresponds to this ratio.

The code achieves its purpose through an iterative algorithm implemented in the run method of the MaxParametricSolver class. This method starts with an initial ratio and repeatedly finds cycles in the graph that could potentially improve this ratio. It uses a negative cycle finder (NCF) to detect these cycles efficiently.

The algorithm works as follows:

1. It starts with an initial ratio and distance estimates for each node.
2. It uses the NCF to find cycles in the graph where the total distance is negative.
3. For each negative cycle found, it calculates a new ratio that would make the cycle's total distance zero.
4. If this new ratio is smaller than the current best ratio, it updates the best ratio and remembers this cycle.
5. It repeats steps 2-4 until no better ratio can be found.

The main data transformation happening here is the continuous updating of the ratio based on the cycles found in the graph. The algorithm is essentially searching for the highest ratio that doesn't allow any negative cycles in the graph, when distances are calculated using this ratio.

This code is designed to be flexible, using generic types for nodes, edges, and ratios. This allows it to work with different types of graphs and different ways of calculating distances. The ParametricAPI class defines an interface for how distances should be calculated and how to find the ratio that makes a cycle's total distance zero.

Overall, this code provides a framework for solving a specific type of optimization problem on graphs, where the goal is to maximize a ratio while maintaining certain constraints on the distances between nodes in the graph.
"""

from abc import abstractmethod
from fractions import Fraction
from typing import Generic, Mapping, MutableMapping, Tuple, TypeVar

from .neg_cycle import Cycle, Domain, Edge, NegCycleFinder, Node

# Define a type variable Ratio that can be either Fraction or float
Ratio = TypeVar("Ratio", Fraction, float)


class ParametricAPI(Generic[Node, Edge, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Edge) -> Ratio:
        """
        The `distance` function calculates the distance between a given ratio and edge.

        :param ratio: The `ratio` parameter is of type `Ratio`. It represents a ratio or proportion
        :type ratio: Ratio
        :param edge: The `edge` parameter represents an edge in a graph. It is of type `Edge`
        :type edge: Edge
        :return: Returns the calculated distance as a Ratio type
        :rtype: Ratio
        """

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """
        The `zero_cancel` function takes a `Cycle` object as input and returns a `Ratio` object.
        This function calculates the ratio that would make the total distance of the cycle zero.

        :param cycle: The `cycle` parameter is of type `Cycle`. It represents a cycle in the graph
        :type cycle: Cycle
        :return: Returns the calculated ratio that makes the cycle's total distance zero
        :rtype: Ratio
        """


class MaxParametricSolver(Generic[Node, Edge, Ratio]):
    """Maximum Parametric Solver

    This class solves the following parametric network problem:

    |    max  r
    |    s.t. dist[v] - dist[u] <= distrance(e, r)
    |         forall e(u, v) in G(V, E)

    A parametric network problem refers to a type of optimization problem that
    involves finding the optimal solution to a network flow problem as a function
    of one single parameter.
    """

    def __init__(
        self,
        digraph: Mapping[Node, Mapping[Node, Edge]],
        omega: ParametricAPI[Node, Edge, Ratio],
    ) -> None:
        """
        The `__init__` function initializes an object with a graph and an omega parameter.

        :param digraph: digraph is a mapping of nodes to a mapping of nodes to edges. It represents a graph
            where each node is connected to other nodes through edges. The edges are represented by the
            mapping of nodes to edges. The graph structure is used for finding cycles and calculating distances.

        :type digraph: Mapping[Node, Mapping[Node, Edge]]

        :param omega: The `omega` parameter is an instance of the `ParametricAPI` class. It represents
            some kind of parametric API that takes three type parameters: `Node`, `Edge`, and `Ratio`.
            This object provides methods for distance calculation and cycle analysis.

        :type omega: ParametricAPI[Node, Edge, Ratio]
        """
        # self.ncf = NegCycleFinder(digraph)
        self.digraph = digraph
        self.omega: ParametricAPI[Node, Edge, Ratio] = omega

    def run(
        self, dist: MutableMapping[Node, Domain], ratio: Ratio
    ) -> Tuple[Ratio, Cycle]:
        """
        The `run` function takes in a distance mapping and a ratio, and iteratively finds the minimum
        ratio and corresponding cycle until the minimum ratio is greater than or equal to the input
        ratio.

        :param dist: The `dist` parameter is a mutable mapping where the keys are `Node` objects and the
            values are `Domain` objects. It represents the distance between nodes in a graph. This distance
            mapping is updated during the algorithm's execution.

        :type dist: MutableMapping[Node, Domain]

        :param ratio: The `ratio` parameter is a value that represents a ratio or proportion. It is used
            as a threshold or target value in the algorithm. The algorithm will try to find the maximum
            possible ratio that satisfies the constraints.

        :type ratio: Ratio

        :return: The function `run` returns a tuple containing two elements:
            1. The updated ratio (`ratio`) which is the maximum ratio found that satisfies the constraints
            2. The cycle (`cycle`) that corresponds to this ratio

        :rtype: Tuple[Ratio, Cycle]
        """
        # Determine the type of domain values from the first element in dist
        D = type(next(iter(dist.values())))

        # Define a weight function that calculates distance based on current ratio
        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        # Initialize minimum ratio and cycle
        r_min = ratio
        c_min = []
        cycle = []

        # Create a negative cycle finder instance with the graph
        ncf: NegCycleFinder[Node, Edge, Domain] = NegCycleFinder(self.digraph)

        # Main algorithm loop
        while True:
            # Find all negative cycles in the graph
            for ci in ncf.howard(dist, get_weight):
                # Calculate the ratio that would make this cycle's total distance zero
                ri = self.omega.zero_cancel(ci)
                # Update minimum ratio if a smaller one is found
                if r_min > ri:
                    r_min = ri
                    c_min = ci

            # Termination condition: no better ratio found
            if r_min >= ratio:
                break

            # Update cycle and ratio for next iteration
            cycle = c_min
            ratio = r_min
        return ratio, cycle
