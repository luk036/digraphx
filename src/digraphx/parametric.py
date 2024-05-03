from abc import abstractmethod
from fractions import Fraction
from typing import Generic, Mapping, MutableMapping, Tuple, TypeVar

from .neg_cycle import Cycle, Domain, Edge, NegCycleFinder, Node

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
        """

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """
        The `zero_cancel` function takes a `Cycle` object as input and returns a `Ratio` object.

        :param cycle: The `cycle` parameter is of type `Cycle`.
        :type cycle: Cycle
        """


class MaxParametricSolver(Generic[Node, Edge, Ratio]):
    """Maximum Parametric Solver

    This class solves the following parametric network problem:

        max  r
        s.t. dist[v] - dist[u] <= distrance(e, r)
             forall e(u, v) in G(V, E)

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
            mapping of nodes to edges

        :type digraph: Mapping[Node, Mapping[Node, Edge]]

        :param omega: The `omega` parameter is an instance of the `ParametricAPI` class. It represents
            some kind of parametric API that takes three type parameters: `Node`, `Edge`, and `Ratio`

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
            values are `Domain` objects. It represents the distance between nodes in a graph

        :type dist: MutableMapping[Node, Domain]

        :param ratio: The `ratio` parameter is a value that represents a ratio or proportion. It is used
            as a threshold or target value in the algorithm

        :type ratio: Ratio

        :return: The function `run` returns a tuple containing the updated ratio (`ratio`) and the cycle (`cycle`).
        """
        D = type(next(iter(dist.values())))

        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        r_min = ratio
        c_min = []
        cycle = []

        ncf: NegCycleFinder[Node, Edge, Domain] = NegCycleFinder(self.digraph)

        while True:
            for ci in ncf.howard(dist, get_weight):
                ri = self.omega.zero_cancel(ci)
                if r_min > ri:
                    r_min = ri
                    c_min = ci
            if r_min >= ratio:
                break

            cycle = c_min
            ratio = r_min
        return ratio, cycle
