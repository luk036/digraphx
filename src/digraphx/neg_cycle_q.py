"""
Negative Cycle Finder (neg_cycle_q.py)

This code implements a Negative Cycle Finder for directed graphs using Howard's method. The purpose of this code is to detect and find negative cycles in a directed graph. A negative cycle is a cycle in the graph where the sum of the edge weights is negative.

The main input for this code is a directed graph, represented as a mapping of nodes to their neighboring nodes and the edges connecting them. The graph is passed to the NegCycleFinder class when it's initialized.

The output of this code is a list of cycles (if any negative cycles are found). Each cycle is represented as a list of edges that form the negative cycle.

The code achieves its purpose through an algorithm called Howard's method, which is a minimum cycle ratio (MCR) algorithm. It works by maintaining a set of candidate cycles and iteratively updating them until it finds the minimum cycle ratio or detects a negative cycle.

The main logic flow of the algorithm involves two key operations: relaxation and cycle detection. The relaxation process updates the distances between nodes based on the edge weights. This is done in two ways: predecessor relaxation (relax_pred) and successor relaxation (relax_succ). The cycle detection part (find_cycle) looks for cycles in the graph based on the current set of predecessors or successors.

The howard_pred and howard_succ methods combine these operations. They repeatedly perform relaxation and then check for cycles. If a negative cycle is found, it's yielded as output.

An important data transformation happening in this code is the maintenance of the 'dist' dictionary, which keeps track of the distances between nodes. This dictionary is continuously updated during the relaxation process.

The code uses some advanced concepts like generic types and generator functions, but the core idea is straightforward: it's trying to find paths in the graph where going around in a circle results in a negative total weight, which shouldn't happen in many real-world scenarios (like currency exchange rates).

Overall, this code provides a tool for analyzing directed graphs and finding problematic cycles, which can be useful in various applications such as detecting arbitrage opportunities in currency exchange or finding inconsistencies in systems modeled as graphs.
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
    succ: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, digraph: Mapping[Node, Mapping[Node, Edge]]) -> None:
        """
        The function initializes a graph object with an adjacency list.

        :param digraph: The parameter `digraph` is a mapping that represents an adjacency list. It is a
            dictionary-like object where the keys are nodes and the values are mappings of nodes to edges. Each
            edge represents a connection between two nodes in a directed graph

        :type digraph: Mapping[Node, Mapping[Node, Edge]]
        """
        self.digraph = digraph

    def find_cycle(self, point_to) -> Generator[Node, None, None]:
        """
        The `find_cycle` function is used to find a cycle in a policy graph and yields the start node of the
        cycle.

        :param point_to: The `point_to` parameter is a dictionary that represents the edges of a directed
            graph. Each key-value pair in the dictionary represents an edge from the key vertex to the value
            vertex

        Yields:
            Generator[Node, None, None]: a start node of the cycle

        Examples:
            >>> digraph = {
            ...     "a0": {"a1": 7, "a2": 5},
            ...     "a1": {"a0": 0, "a2": 3},
            ...     "a2": {"a1": 1, "a0": 2},
            ... }
            >>> finder = NegCycleFinder(digraph)
            >>> for cycle in finder.find_cycle(finder.pred):
            ...     print(cycle)
        """
        visited: Dict[Node, Node] = {}
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            while True:
                visited[utx] = vtx
                if utx not in point_to:
                    break
                utx, _ = point_to[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break

    def relax_pred(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> bool:
        """
        The `relax_pred` function updates the `dist` and `pred` dictionaries based on the current distances and
        weights of edges in a graph.

        :param dist: `dist` is a mutable mapping that represents the current distances from a source node to
            all other nodes in a graph. It is a mapping from nodes to their corresponding distances

        :type dist: MutableMapping[Node, Domain]

        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
            input and returns a value of type `Domain`. This function is used to calculate the weight or cost
            associated with an edge in the graph

        :type get_weight: Callable[[Edge], Domain]

        :param update_ok: The `update_ok` parameter is a function that determines whether an update to the
            distance `dist[vtx_v]` is allowed. It takes two arguments: the current value of `dist[vtx_v]` and
            the new value `d`. It should return `True` if the update is

        :return: a boolean value indicating whether any changes were made to the `dist` mapping and `pred` dictionary.
        """
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[utx] + get_weight(edge)
                if dist[vtx] > distance and update_ok(dist[vtx], distance):
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)
                    changed = True
        return changed

    def relax_succ(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> bool:
        """
        The `relax_succ` function updates the `dist` and `succ` dictionaries based on the current distances and
        weights of edges in a graph.

        :param dist: `dist` is a mutable mapping that represents the current distances from a source node to
            all other nodes in a graph. It is a mapping from nodes to their corresponding distances

        :type dist: MutableMapping[Node, Domain]

        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
            input and returns a value of type `Domain`. This function is used to calculate the weight or cost
            associated with an edge in the graph

        :type get_weight: Callable[[Edge], Domain]

        :param update_ok: The `update_ok` parameter is a function that determines whether an update to the
            distance `dist[vtx_v]` is allowed. It takes two arguments: the current value of `dist[vtx_v]` and
            the new value `d`. It should return `True` if the update is

        :return: a boolean value indicating whether any changes were made to the `dist` mapping and `pred` dictionary.
        """
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[vtx] - get_weight(edge)
                if dist[utx] < distance and update_ok(dist[utx], distance):
                    dist[utx] = distance
                    self.succ[utx] = (vtx, edge)
                    changed = True
        return changed

    def howard_pred(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> Generator[Cycle, None, None]:
        """
        The `howard_pred` function finds negative cycles in a graph and yields a list of cycles.

        :param dist: `dist` is a mutable mapping that maps each node in the graph to a domain value. The
            domain value represents the distance or cost from the source node to that particular node

        :type dist: MutableMapping[Node, Domain]

        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
            input and returns the weight of that edge

        :type get_weight: Callable[[Edge], Domain]

        :param update_ok: The `update_ok` parameter is a callable function that determines whether an update
            to the distance value of a vertex is allowed. It takes in three arguments: the current distance
            value of the vertex, the weight of the edge being considered for update, and the current distance
            value of the vertex at the other

        Examples:
            >>> digraph = {
            ...     "a0": {"a1": 7, "a2": 5},
            ...     "a1": {"a0": 0, "a2": 3},
            ...     "a2": {"a1": 1, "a0": 2},
            ... }
            >>> dist = {vtx: 0 for vtx in digraph}
            >>> def update_ok(dist, v) : return True
            >>> finder = NegCycleFinder(digraph)
            >>> has_neg = False
            >>> for _ in finder.howard_pred(dist, lambda edge: edge, update_ok):
            ...     has_neg = True
            ...     break
            ...
            >>> has_neg
            False
        """
        self.pred = {}
        found = False
        while not found and self.relax_pred(dist, get_weight, update_ok):
            for vtx in self.find_cycle(self.pred):
                # Will zero cycle be found???
                assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx, self.pred)

    def howard_succ(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> Generator[Cycle, None, None]:
        """
        The `howard_succ` function finds negative cycles in a graph and yields a list of cycles.

        :param dist: `dist` is a mutable mapping that maps each node in the graph to a domain value. The
            domain value represents the distance or cost from the source node to that particular node

        :type dist: MutableMapping[Node, Domain]

        :param get_weight: The `get_weight` parameter is a callable function that takes an `Edge` object as
            input and returns the weight of that edge

        :type get_weight: Callable[[Edge], Domain]

        :param update_ok: The `update_ok` parameter is a callable function that determines whether an update
            to the distance value of a vertex is allowed. It takes in three arguments: the current distance
            value of the vertex, the weight of the edge being considered for update, and the current distance
            value of the vertex at the other

        Examples:
            >>> digraph = {
            ...     "a0": {"a1": 7, "a2": 5},
            ...     "a1": {"a0": 0, "a2": 3},
            ...     "a2": {"a1": 1, "a0": 2},
            ... }
            >>> def update_ok(dist, v) : return True
            >>> dist = {vtx: 0 for vtx in digraph}
            >>> finder = NegCycleFinder(digraph)
            >>> has_neg = False
            >>> for _ in finder.howard_succ(dist, lambda edge: edge, update_ok):
            ...     has_neg = True
            ...     break
            ...
            >>> has_neg
            False
        """
        self.succ = {}
        found = False
        while not found and self.relax_succ(dist, get_weight, update_ok):
            for vtx in self.find_cycle(self.succ):
                # Will zero cycle be found???
                # assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx, self.succ)

    def cycle_list(self, handle: Node, point_to) -> Cycle:
        """
        The `cycle_list` function returns a list of edges that form a cycle in a graph, starting from a
        given node.

        :param handle: The `handle` parameter is a reference to a node in a graph. It represents the
            starting point of the cycle in the list

        :type handle: Node

        :param point_to: point_to is a dictionary that maps each graph node to the node it points to

        :return: a list of edges, which represents a cycle in a graph.
        """
        vtx = handle
        cycle = list()
        while True:
            utx, edge = point_to[vtx]
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
