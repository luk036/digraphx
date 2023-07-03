from fractions import Fraction
from typing import Generic, Mapping, MutableMapping, Tuple, TypeVar
from .neg_cycle import Node, Edge, Domain, Cycle
from .parametric import MaxParametricSolver, ParametricAPI

Ratio = TypeVar("Ratio", Fraction, float)  # Comparable field
Graph = Mapping[Node, Mapping[Node, Mapping[str, Domain]]]
GraphMut = MutableMapping[Node, MutableMapping[Node, MutableMapping[str, Domain]]]


def set_default(gra: GraphMut, weight: str, value: Domain) -> None:
    """_summary_

    Args:
        gra (Graph): _description_
        weight (str): _description_
        value (Any): _description_
    """
    for _, nbrs in gra.items():
        for _, e in nbrs.items():
            if e.get(weight, None) is None:
                e[weight] = value


class CycleRatioAPI(ParametricAPI[Node, MutableMapping[str, Domain], Ratio]):
    def __init__(
        self, gra: Mapping[Node, Mapping[Node, Mapping[str, Domain]]], K: type
    ) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Mapping[str, Domain]]]): _description_
            K (type): _description_
        """
        self.gra: Mapping[Node, Mapping[Node, Mapping[str, Domain]]] = gra
        self.K = K

    def distance(self, ratio: Ratio, edge: MutableMapping[str, Domain]) -> Ratio:
        """[summary]

        Arguments:
            ratio ([type]): [description]
            e ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.K(edge["cost"]) - ratio * edge["time"]

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        """Calculate the ratio of the cycle

        Args:
            cycle (Cycle): _description_

        Returns:
            Ratio: _description_
        """
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return self.K(total_cost) / total_time


class MinCycleRatioSolver(Generic[Node, Edge, Ratio]):
    """Minimum Cycle Ratio Solver

    This class solves the following parametric network problem:

        max  r
        s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
             for all (u, v) in E

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

    def __init__(self, gra: Graph) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Any]]): _description_
        """
        self.gra: Graph = gra

    def run(self, dist: MutableMapping[Node, Domain], r0: Ratio) -> Tuple[Ratio, Cycle]:
        """_summary_

        Args:
            dist (MutableMapping[Node, Ratio]): _description_
            r0 (Ratio): _description_

        Returns:
            Tuple[Ratio, Cycle]: _description_
        """
        omega = CycleRatioAPI(self.gra, type(r0))
        solver = MaxParametricSolver(self.gra, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle
