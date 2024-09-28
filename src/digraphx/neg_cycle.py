"""
NegCycleFinder

This code defines a class called NegCycleFinder, which is designed to find negative cycles in a directed graph. A negative cycle is a loop in the graph where the sum of the edge weights is less than zero. This can be important in various applications, such as detecting arbitrage opportunities in currency exchange rates.

The NegCycleFinder takes a directed graph as input. The graph is represented as a mapping (like a dictionary) where each key is a node, and its value is another mapping of neighboring nodes and their connecting edges. The class also works with a distance mapping and a function to get the weight of an edge.

The main output of this class is a list of edges that form a negative cycle in the graph. It doesn't return this directly, but instead yields these cycles through a generator function called howard().

To find negative cycles, the class uses two main algorithms: the Bellman-Ford algorithm and Howard's method. The Bellman-Ford algorithm is used in the relax() method to update the shortest distances between nodes. Howard's method, implemented in the howard() function, uses this relaxation step repeatedly to find negative cycles.

The process works like this: First, the relax() method goes through all edges in the graph and updates the distances if a shorter path is found. It also keeps track of which edge led to each node in the pred dictionary. Then, the find_cycle() method looks for cycles in this predecessor graph. If a cycle is found, the is_negative() method checks if it's a negative cycle by comparing the distances and edge weights. If a negative cycle is found, it's yielded by the howard() method.

An important part of the logic is how the class maintains and updates the pred dictionary. This dictionary keeps track of which node and edge led to each node in the shortest path found so far. This information is crucial for reconstructing the cycles when they're found.

The code uses some advanced Python features like type hinting and generators, but the core logic is based on graph traversal and cycle detection, which are fundamental concepts in graph theory and algorithm design. The class provides a reusable tool for finding negative cycles in any directed graph, which can be useful in many different applications.
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

    This code defines a `NegCycleFinder` class, which is used to find negative cycles in a given directed graph. The    `NegCycleFinder` class has the following methods:

    1.  `__init__(self, digraph: MutableMapping[Node, List[Edge]])`:
        The constructor initializes an instance of the `NegCycleFinder` class with the given directed graph.
    2.  `relax(self, dist: MutableMapping[Node, Domain], get_weight: Callable[[Edge], Domain]) -> bool`:
        This method performs one iteration of Bellman-Ford algorithm to relax all edges in the graph and update the shortest
        distances to their neighbors. It returns a boolean value indicating if any changes were made during this iteration.
    3.  `howard(self, dist: MutableMapping[Node, Domain], get_weight: Callable[[Edge], Domain]) -> Generator[Cycle, None, None]`:
        This method finds negative cycles in the graph using the Howard's algorithm and returns a generator that yields a
        list of edges for each cycle.
    4.  `cycle_list(self, handle: Node) -> Cycle`:
        This method returns a list of edges that form a cycle in the graph, starting from a given node.
    5.  `is_negative(self, handle: Node, dist: MutableMapping[Node, Domain], get_weight: Callable[[Edge], Domain]) -> bool`:
        This method checks if a cycle is negative by comparing the distances between nodes and the weights of the edges.

    Here's a brief explanation of the algorithms used in this code:

    1.  Bellman-Ford Algorithm: It is a shortest path algorithm that can find single source shortest paths in a graph with
        negative edge weights. It runs in O(V*E) time complexity.
    2.  Howard's Policy Graph Algorithm: It is used to find cycles in a directed graph and is based on the Bellman-Ford
        Algorithm. It runs in O(V*E + V*E^2) time complexity in the worst case.
    """

    pred: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, digraph: Mapping[Node, Mapping[Node, Edge]]) -> None:
        """
        The function initializes a graph object with an adjacency list.

        :param digraph: The parameter `digraph` is a mapping that represents an adjacency list. It is a
            dictionary-like object where the keys are nodes and the values are mappings of nodes to edges. Each
            edge represents a connection between two nodes in a directed graph

        :type digraph: Mapping[Node, Mapping[Node, Edge]]
        """
        self.digraph = digraph

    def find_cycle(self) -> Generator[Node, None, None]:
        """
        The `find_cycle` function is used to find a cycle in a policy graph and yields the start node of the cycle.

        Yields:
            Generator[Node, None, None]: a start node of the cycle

        Examples:
            >>> digraph = {
            ...     "a0": {"a1": 7, "a2": 5},
            ...     "a1": {"a0": 0, "a2": 3},
            ...     "a2": {"a1": 1, "a0": 2},
            ... }
            >>> finder = NegCycleFinder(digraph)
            >>> for cycle in finder.find_cycle():
            ...     print(cycle)
        """
        visited: Dict[Node, Node] = {}
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            visited[utx] = vtx
            while utx in self.pred:
                utx, _ = self.pred[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break
                visited[utx] = vtx

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

        :return: a boolean value indicating whether any changes were made to the `dist` mapping and `pred` dictionary.
        """
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[utx] + get_weight(edge)
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)
                    changed = True
        return changed

    def cycle_list(self, handle: Node) -> Cycle:
        """
        The `cycle_list` function returns a list of edges that form a cycle in a graph, starting from a given node.

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

        Examples:
            >>> digraph = {
            ...     "a0": {"a1": 7, "a2": 5},
            ...     "a1": {"a0": 0, "a2": 3},
            ...     "a2": {"a1": 1, "a0": 2},
            ... }
            >>> dist = {vtx: 0 for vtx in digraph}
            >>> finder = NegCycleFinder(digraph)
            >>> has_neg = False
            >>> for _ in finder.howard(dist, lambda edge: edge):
            ...     has_neg = True
            ...     break
            ...
            >>> has_neg
            False
        """
        self.pred = {}
        found = False
        while not found and self.relax(dist, get_weight):
            for vtx in self.find_cycle():
                # Will zero cycle be found???
                assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx)
