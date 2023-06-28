# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
1. Based on Howard's policy graph algorithm
2. Looking for more than one negative cycles
"""
from typing import Dict, Callable, Generator, Tuple, List
from typing import MutableMapping, Mapping, TypeVar, Generic, Any
from fractions import Fraction

Node = TypeVar("Node")  # Hashable
Edge = TypeVar("Edge")  # Hashable
Domain = TypeVar("Domain", int, float, Fraction)  # Comparable Ring
Cycle = List[Edge]  # List of Edges


class NegCycleFinder(Generic[Node, Edge, Domain]):
    pred: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, gra: Mapping[Node, Mapping[Node, Edge]]) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Edge]]): adjacent list
        """
        self.digraph = gra

    def find_cycle(self) -> Generator[Node, None, None]:
        """Find a cycle on the policy graph

        Yields:
            Generator[Node, None, None]: node: a start node of the cycle
        """
        visited: Dict[Node, Node] = {}
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            while True:
                visited[utx] = vtx
                if utx not in self.pred:
                    break
                utx, _ = self.pred[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break

    def relax(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Any],
    ) -> bool:
        """Perform a updating of dist and pred

        Args:
            dist (MutableMapping[Node, Domain]): _description_
            get_weight (Callable[[Tuple[Node, Node]], Any]): _description_

        Returns:
            bool: _description_
        """
        changed = False
        for utx, nbrs in self.digraph.items():
            for vtx, edge in nbrs.items():
                D = type(dist[utx]) # D could be integer
                distance = dist[utx] + D(get_weight(edge))
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)
                    changed = True
        return changed

    def howard(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Any],
    ) -> Generator[Cycle, None, None]:
        """_summary_

        Args:
            dist (MutableMapping[Node, Domain]): _description_
            get_weight (Callable[[Edge], Any]): _description_

        Yields:
            Generator[Cycle, None, None]: cycle list
        """
        self.pred = {}
        found = False
        while not found and self.relax(dist, get_weight):
            for vtx in self.find_cycle():
                # Will zero cycle be found???
                assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx)

    def cycle_list(self, handle: Node) -> Cycle:
        """Cycle list started from handle

        Args:
            handle (Node): _description_

        Returns:
            Cycle: _description_
        """
        vtx = handle
        cycle = list()
        while True:
            utx, edge = self.pred[vtx]
            cycle.append(edge)
            vtx = utx
            if vtx == handle:
                break
        return cycle

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Any],
    ) -> bool:
        """Check if the cycle list is negative

        Args:
            handle (Node): _description_
            dist (MutableMapping[Node, Any]): _description_
            get_weight (Callable[[Edge], Any]): _description_

        Returns:
            bool: _description_
        """
        vtx = handle
        D = type(dist[vtx])

        # do while loop in C++
        while True:
            utx, edge = self.pred[vtx]
            if dist[vtx] > dist[utx] + D(get_weight(edge)):
                return True
            vtx = utx
            if vtx == handle:
                break
        return False
