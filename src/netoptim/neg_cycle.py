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
Domain = TypeVar("Domain", int, float, Fraction)  # Comparable Ring
Cycle = List[Tuple[Node, Node]]


class NegCycleFinder(Generic[Node, Domain]):
    pred: Dict[Node, Node] = {}

    def __init__(self, gra: Mapping[Node, Mapping[Node, Any]]) -> None:
        """_summary_

        Args:
            gra (Mapping[Node, Mapping[Node, Any]]): adjacent list
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
                utx = self.pred[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break

    def relax(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Tuple[Node, Node]], Domain],
    ) -> bool:
        """Perform a updating of dist and pred

        Args:
            dist (MutableMapping[Node, Domain]): _description_
            get_weight (Callable[[Tuple[Node, Node]], Domain]): _description_

        Returns:
            bool: _description_
        """
        changed = False
        for utx in self.digraph:
            for vtx in self.digraph[utx]:
                weight = get_weight((utx, vtx))
                distance = dist[utx] + weight
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = utx
                    changed = True
        return changed

    def howard(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Tuple[Node, Node]], Domain],
    ) -> Generator[Cycle, None, None]:
        """_summary_

        Args:
            dist (MutableMapping[Node, Domain]): _description_
            get_weight (Callable[[Tuple[Node, Node]], Domain]): _description_

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
            utx = self.pred[vtx]
            cycle.append((utx, vtx))
            vtx = utx
            if vtx == handle:
                break
        return cycle

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Tuple[Node, Node]], Domain],
    ) -> bool:
        """Check if the cycle list is negative

        Args:
            handle (Node): _description_
            dist (MutableMapping[Node, Any]): _description_
            get_weight (Callable[[Tuple[Node, Node]], Any]): _description_

        Returns:
            bool: _description_
        """
        vtx = handle
        # do while loop in C++
        while True:
            utx = self.pred[vtx]
            weight = get_weight((utx, vtx))
            if dist[vtx] > dist[utx] + weight:
                return True
            vtx = utx
            if vtx == handle:
                break
        return False
