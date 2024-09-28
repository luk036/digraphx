"""
Minimum Cycle Ratio Solver

This code implements a Minimum Cycle Ratio (MCR) Solver for directed graphs. The purpose of this code is to find the cycle in a graph that has the smallest ratio of total edge weights to the number of edges in the cycle. This is useful in analyzing various systems like digital circuits and communication networks.

The main input for this solver is a directed graph, represented as a mapping of nodes to their neighboring nodes and associated edge attributes. The graph is expected to have "cost" and "time" attributes for each edge.

The primary output of this solver is a tuple containing two elements: the minimum cycle ratio (a number) and the cycle itself (a sequence of edges that form the cycle with the minimum ratio).

To achieve its purpose, the code uses a parametric approach. It defines a CycleRatioAPI class that calculates distances between nodes based on a given ratio and edge information. This class also computes the ratio for a given cycle.

The main solver, MinCycleRatioSolver, uses the CycleRatioAPI in combination with a MaxParametricSolver (which is not fully shown in this code snippet) to iteratively find the minimum cycle ratio. It starts with an initial ratio and distance mapping for each node, and then refines these values until it finds the optimal solution.

The algorithm works by repeatedly adjusting the ratio and recalculating distances between nodes. It looks for cycles where the sum of distances around the cycle is negative, which indicates a cycle with a lower ratio than the current best. This process continues until no such cycle can be found, at which point the minimum cycle ratio has been determined.

An important aspect of the code is how it handles different types of numbers. It uses generic types and can work with both fractions and floating-point numbers, allowing for flexibility in how precise the calculations need to be.

The code also includes utility functions like set_default, which ensures that all edges in the graph have a specified weight attribute, setting a default value if it's missing. This helps in preparing the graph data for the main algorithm.

Overall, this code provides a flexible and powerful tool for analyzing directed graphs, particularly useful in scenarios where understanding the most "efficient" or "tightest" cycles in a system is important.
"""

from fractions import Fraction
from typing import Generic, Mapping, MutableMapping, Tuple, TypeVar

from .neg_cycle import Cycle, Domain, Edge, Node
from .parametric import MaxParametricSolver, ParametricAPI

Ratio = TypeVar("Ratio", Fraction, float)
Graph = Mapping[Node, Mapping[Node, Mapping[str, Domain]]]
GraphMut = MutableMapping[Node, MutableMapping[Node, MutableMapping[str, Domain]]]


def set_default(digraph: GraphMut, weight: str, value: Domain) -> None:
    """
    This function sets a default value for a specified weight in a graph.

    :param digraph: The parameter `digraph` is of type `GraphMut`, which is likely a mutable graph data
        structure. It represents a graph where each node has a dictionary of neighbors and their
        corresponding edge attributes

    :type digraph: GraphMut

    :param weight: The `weight` parameter is a string that represents the weight attribute of the edges in the graph

    :type weight: str

    :param value: The `value` parameter is the default value that will be set for the specified weight attribute in the graph

    :type value: Domain
    """
    for _, neighbors in digraph.items():
        for _, e in neighbors.items():
            if e.get(weight, None) is None:
                e[weight] = value


# The `CycleRatioAPI` class is a parametric API that calculates the ratio of a cycle based on the cost
# and time of its edges.
class CycleRatioAPI(ParametricAPI[Node, MutableMapping[str, Domain], Ratio]):
    def __init__(
        self,
        digraph: Mapping[Node, Mapping[Node, Mapping[str, Domain]]],
        result_type: type,
    ) -> None:
        """
        This function initializes an object with two parameters, `digraph` and `result_type`, and assigns them to instance
        variables.

        :param digraph: A mapping of nodes to a mapping of nodes to a mapping of strings to domains. It
            represents a graph structure where each node is connected to other nodes through edges, and each
            edge has associated attributes represented by strings and domains

        :type digraph: Mapping[Node, Mapping[Node, Mapping[str, Domain]]]

        :param result_type: The parameter `result_type` is a type. It is used to specify the type of the variable `result_type`. The type
            can be any valid Python type, such as `int`, `str`, `list`, etc

        :type result_type: type
        """
        self.digraph: Mapping[Node, Mapping[Node, Mapping[str, Domain]]] = digraph
        self.result_type = result_type

    def distance(self, ratio: Ratio, edge: MutableMapping[str, Domain]) -> Ratio:
        """
        The function calculates the distance based on the ratio and edge information.

        :param ratio: The ratio parameter is of type Ratio. It is used in the calculation of the return value

        :type ratio: Ratio

        :param edge: The `edge` parameter is a mutable mapping (dictionary-like object) that contains
            information about a specific edge in a graph. It has two keys: "cost" and "time". The value
            associated with the "cost" key represents the cost of traversing the edge, while the value
            associated with

        :type edge: MutableMapping[str, Domain]

        :return: the result of the expression `self.result_type(edge["cost"]) - ratio * edge["time"]`.
        """
        return self.result_type(edge["cost"]) - ratio * edge["time"]

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """
        The `zero_cancel` function calculates the ratio of the cost to time for a given cycle.

        :param cycle: The `cycle` parameter is of type `Cycle`. It represents a cycle, which is a sequence
            of edges in a graph that starts and ends at the same vertex. Each edge in the cycle is a dictionary
            with keys "cost" and "time", representing the cost and time associated with that edge

        :type cycle: Cycle

        :return: a Ratio object.
        """
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return self.result_type(total_cost) / total_time


# The `MinCycleRatioSolver` class is a solver for the minimum cycle ratio problem in directed graphs.
class MinCycleRatioSolver(Generic[Node, Edge, Ratio]):
    """Minimum Cycle Ratio Solver

    This class solves the following parametric network problem:

    |    max  r
    |    s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
    |         for all (u, v) in E

    The minimum cycle ratio (MCR) problem is a fundamental problem in the
    analysis of directed graphs. Given a directed graph, the MCR problem seeks to
    find the cycle with the minimum ratio of the sum of edge weights to the
    number of edges in the cycle. In other words, the MCR problem seeks to find
    the "tightest" cycle in the graph, where the tightness of a cycle is measured
    by the ratio of the total weight of the cycle to its length.

    The MCR problem has many applications in the analysis of discrete event
    systems, such as digital circuits and communication networks. It is closely
    related to other problems in graph theory, such as the shortest path problem
    and the maximum flow problem. Efficient algorithms for solving the MCR
    problem are therefore of great practical importance.
    """

    def __init__(self, digraph: Graph) -> None:
        """
        The function initializes an instance of a class with a graph object.

        :param digraph: The `digraph` parameter is a mapping of nodes to a mapping of nodes to any type of value. It
            represents a graph where each node is associated with a set of neighboring nodes and their
            corresponding values

        :type digraph: Graph
        """
        self.digraph: Graph = digraph

    def run(self, dist: MutableMapping[Node, Domain], r0: Ratio) -> Tuple[Ratio, Cycle]:
        """
        This function takes a distance mapping and a ratio as input, and returns a ratio and a cycle.

        :param dist: A mutable mapping that maps each node in the graph to a ratio value. This represents
            the initial distribution of ratios for each node

        :type dist: MutableMapping[Node, Domain]

        :param r0: The parameter `r0` is of type `Ratio` and represents the initial ratio value

        :type r0: Ratio

        :return: The function `run` returns a tuple containing the ratio and cycle.
        """
        omega = CycleRatioAPI(self.digraph, type(r0))
        solver = MaxParametricSolver(self.digraph, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle
