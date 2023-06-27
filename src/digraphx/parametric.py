# -*- coding: utf-8 -*-
from abc import abstractmethod
from .neg_cycle import NegCycleFinder
from typing import Tuple, List, Any
from typing import MutableMapping, Mapping, TypeVar, Generic
from fractions import Fraction


Ratio = TypeVar("Ratio", float, Fraction)  # Comparable field
Node = TypeVar("Node")
Cycle = List[Tuple[Node, Node]]


class ParametricAPI(Generic[Node, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Tuple[Node, Node]) -> Ratio:
        """_summary_

        Args:
            ratio (Ratio): _description_
            edge (Tuple[Node, Node]): _description_

        Returns:
            Ratio: _description_
        """
        pass

    @abstractmethod
    def zero_cancel(self, cycle: List[Tuple[Node, Node]]) -> Ratio:
        """_summary_

        Args:
            Cycle (_type_): _description_

        Returns:
            Ratio: _description_
        """
        pass


class MaxParametricSolver(Generic[Node, Ratio]):
    """Maximum parametric problem:

    Solve:
        max  ratio
        s.t. dist[v] - dist[u] <= distance(u, v, ratio)
             for all (u, v) in gra
    """

    def __init__(
        self, gra: Mapping[Node, Mapping[Node, Any]], omega: ParametricAPI[Node, Ratio]
    ) -> None:
        """initialize

        Args:
            gra (Mapping[Node, Mapping[Node, Any]]): _description_
            omega (ParametricAPI): _description_
        """
        self.ncf = NegCycleFinder(gra)
        self.omega: ParametricAPI[Node, Ratio] = omega

    def run(
        self, dist: MutableMapping[Node, Ratio], ratio: Ratio
    ) -> Tuple[Ratio, Cycle]:
        """run

        Args:
            ratio (Ratio): _description_
            dist (MutableMapping[Node, Ratio]): _description_

        Returns:
            Tuple[Ratio, Cycle]: _description_
        """
        r_min = ratio
        c_min = []
        cycle = []

        while True:
            for ci in self.ncf.howard(dist, lambda e: self.omega.distance(ratio, e)):
                ri = self.omega.zero_cancel(ci)
                if r_min > ri:
                    r_min = ri
                    c_min = ci
            if r_min >= ratio:
                break

            cycle = c_min
            ratio = r_min
        return ratio, cycle
