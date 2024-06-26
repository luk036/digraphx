from abc import abstractmethod
from fractions import Fraction
from typing import Generic, Mapping, MutableMapping, Tuple, TypeVar, Callable

from .neg_cycle_q import Cycle, Edge, NegCycleFinder, Node

Domain = TypeVar("Domain", int, Fraction, float)  # Comparable Ring
Ratio = TypeVar("Ratio", Fraction, float)


class MinParametricAPI(Generic[Node, Edge, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Edge) -> Ratio:
        """
        The `distance` function calculates the distance between a given ratio and edge.

        :param ratio: The `ratio` parameter is of type `Ratio`. It represents a ratio or proportion
        :type ratio: Ratio
        :param edge: The `edge` parameter represents an edge in a graph. It is of type `Edge`
        :type edge: Edge
        """
        pass

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """
        The `zero_cancel` function takes a `Cycle` object as input and returns a `Ratio` object.

        :param cycle: The `cycle` parameter is of type `Cycle`.
        :type cycle: Cycle
        """
        pass


class MinParametricSolver(Generic[Node, Edge, Ratio]):
    """Minimum Parametric Solver

    This class solves the following parametric network problem:

        min  r
        s.t. dist[v] - dist[u] <= distrance(e, r)
             forall e(u, v) in G(V, E)

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
        self.omega: MinParametricAPI[Node, Edge, Ratio] = omega

    def run(
        self,
        dist: MutableMapping[Node, Domain],
        ratio: Ratio,
        update_ok: Callable[[Domain, Domain], bool],
        pick_one_only=False,
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

        :param update_ok: The `update_ok` parameter is a function that determines whether an update to the
            distance `dist[vtx_v]` is allowed. It takes two arguments: the current value of `dist[vtx_v]` and
            the new value `d`. It should return `True` if the update is

        :return: The function `run` returns a tuple containing the updated ratio (`ratio`) and the cycle (`cycle`).
        """
        D = type(next(iter(dist.values())))

        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        r_max = ratio
        c_max = []
        cycle = []
        reverse: bool = True

        ncf: NegCycleFinder[Node, Edge, Domain] = NegCycleFinder(self.digraph)

        while True:
            if reverse:
                cycles = ncf.howard_succ(dist, get_weight, update_ok)
            else:
                cycles = ncf.howard_pred(dist, get_weight, update_ok)
            for c_i in cycles:
                r_i = self.omega.zero_cancel(c_i)
                if r_max < r_i:
                    r_max = r_i
                    c_max = c_i
                    if pick_one_only:
                        break
            if r_max <= ratio:
                break

            cycle = c_max
            ratio = r_max
            reverse = not reverse
        return ratio, cycle
