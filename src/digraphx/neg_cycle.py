"""
Negative cycle detection for directed graphs.
1. Based on Howard's policy graph algorithm
2. Looking for more than one negative cycle
"""
from fractions import Fraction
from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Tuple,
    TypeVar,
)

Node = TypeVar("Node")  # Hashable
Edge = TypeVar("Edge")  # Hashable
Domain = TypeVar("Domain", int, Fraction, float)  # Comparable Ring
Cycle = List[Edge]  # List of Edges


# The `NegCycleFinder` class implements Howard's method, a minimum cycle ratio algorithm, to find
# negative cycles in a directed graph.
class NegCycleFinder(Generic[Node, Edge, Domain]):
    """Negative Cycle Finder by Howard's method

    Howard's method is a minimum cycle ratio (MCR) algorithm that uses a policy
    iteration algorithm to find the minimum cycle ratio of a directed graph. The
    algorithm maintains a set of candidate cycles and iteratively updates the
    cycle with the minimum ratio until convergence. To detect negative cycles,
    Howard's method uses a cycle detection algorithm that is based on the
    Bellman-Ford relaxation algorithm. Specifically, the algorithm maintains a
    predecessor graph of the original graph and performs cycle detection on this
    graph using the Bellman-Ford relaxation algorithm. If a negative cycle is
    detected, the algorithm terminates and returns the cycle.
    """

    pred: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, gra: Mapping[Node, Mapping[Node, Edge]]) -> None:
        """
        The function initializes a graph object with an adjacency list.

        :param gra: The parameter `gra` is a mapping that represents an adjacency list. It is a
        dictionary-like object where the keys are nodes and the values are mappings of nodes to edges. Each
        edge represents a connection between two nodes in a directed graph
        :type gra: Mapping[Node, Mapping[Node, Edge]]
        """
        self.digraph = gra

    def find_cycle(self) -> Generator[Node, None, None]:
        """
        The `find_cycle` function is used to find a cycle in a policy graph and yields the start node of the
        cycle.

        Yields:
            Generator[Node, None, None]: a start node of the cycle

        Examples:
            >>> from digraphx.neg_cycle import NegCycleFinder
            >>> from fractions import Fraction
            >>> from collections import defaultdict
            >>> g = defaultdict(dict)
            >>> g[1][2] = Fraction(1, 2)
            >>> g[2][3] = Fraction(1, 2)
            >>> g[3][1] = Fraction(1, 2)
            >>> g[1][3] = Fraction(1, 2)
            >>> g[3][4] = Fraction(1, 2)
            >>> g[4][5] = Fraction(1, 2)
            >>> g[5][3] = Fraction(1, 2)
            >>> finder = NegCycleFinder(g)
            >>> for cycle in finder.find_cycle():
            ...     print(cycle)
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
        get_weight: Callable[[Edge], Domain],
    ) -> bool:
        """
        The `relax` function updates the `dist` and `pred` dictionaries based on the current distances and
        weights of edges in a graph.

        :param dist: `dist` is a mutable mapping that represents the current distances from a source node to
        all other nodes in a graph. It is a mapping from nodes to their corresponding distances
        :type dist: MutableMapping[Node, Domain]
        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
        input and returns a value of type `Domain`. This function is used to calculate the weight or cost
        associated with an edge in the graph
        :type get_weight: Callable[[Edge], Domain]
        :return: a boolean value indicating whether any changes were made to the `dist` mapping and `pred`
        dictionary.
        """
        changed = False
        for utx, nbrs in self.digraph.items():
            for vtx, edge in nbrs.items():
                distance = dist[utx] + get_weight(edge)
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)
                    changed = True
        return changed

    def howard(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
    ) -> Generator[Cycle, None, None]:
        """
        The `howard` function finds negative cycles in a graph and yields a list of cycles.

        :param dist: `dist` is a mutable mapping that maps each node in the graph to a domain value. The
        domain value represents the distance or cost from the source node to that particular node
        :type dist: MutableMapping[Node, Domain]
        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
        input and returns the weight of that edge
        :type get_weight: Callable[[Edge], Domain]
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
        """
        The `cycle_list` function returns a list of edges that form a cycle in a graph, starting from a
        given node.

        :param handle: The `handle` parameter is a reference to a node in a graph. It represents the
        starting point of the cycle in the list
        :type handle: Node
        :return: a list called "cycle".
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
        get_weight: Callable[[Edge], Domain],
    ) -> bool:
        """
        The `is_negative` function checks if a cycle list is negative by comparing the distances between
        nodes and the weights of the edges.

        :param handle: The `handle` parameter is a `Node` object that represents a vertex in a graph. It is
        used as a starting point to check for negative cycles in the graph
        :type handle: Node
        :param dist: `dist` is a mutable mapping that maps each node to its corresponding domain value. The
        domain value represents the distance from the starting node to the current node in a graph
        :type dist: MutableMapping[Node, Domain]
        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
        input and returns the weight of that edge
        :type get_weight: Callable[[Edge], Domain]
        :return: a boolean value.
        """
        vtx = handle
        # do while loop in C++
        while True:
            utx, edge = self.pred[vtx]
            if dist[vtx] > dist[utx] + get_weight(edge):
                return True
            vtx = utx
            if vtx == handle:
                break
        return False
