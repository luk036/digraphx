from abc import abstractmethod
from .neg_cycle import NegCycleFinder, Node, Edge, Domain, Cycle
from typing import Tuple
from typing import MutableMapping, Mapping, TypeVar, Generic
from fractions import Fraction

Ratio = TypeVar("Ratio", Fraction, float)  # Comparable field


class ParametricAPI(Generic[Node, Edge, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Edge) -> Ratio:
        """_summary_

        Args:
            ratio (Ratio): _description_
            edge (Edge): _description_

        Returns:
            Ratio: _description_
        """
        pass

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """_summary_

        Args:
            Cycle (_type_): _description_

        Returns:
            Ratio: _description_
        """
        pass


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
        gra: Mapping[Node, Mapping[Node, Edge]],
        omega: ParametricAPI[Node, Edge, Ratio],
    ) -> None:
        """initialize

        Args:
            gra (Mapping[Node, Mapping[Node, Edge]]): _description_
            omega (ParametricAPI): _description_
        """
        self.ncf = NegCycleFinder(gra)
        self.omega: ParametricAPI[Node, Edge, Ratio] = omega

    def run(
        self, dist: MutableMapping[Node, Domain], ratio: Ratio
    ) -> Tuple[Ratio, Cycle]:
        """run

        Args:
            ratio (Ratio): _description_
            dist (MutableMapping[Node, Ratio]): _description_

        Returns:
            Tuple[Ratio, Cycle]: _description_
        """
        D = type(next(iter(dist.values())))

        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        r_min = ratio
        c_min = []
        cycle = []

        while True:
            for ci in self.ncf.howard(dist, get_weight):
                ri = self.omega.zero_cancel(ci)
                if r_min > ri:
                    r_min = ri
                    c_min = ci
            if r_min >= ratio:
                break

            cycle = c_min
            ratio = r_min
        return ratio, cycle
