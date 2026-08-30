"""NegCycleFinder

This code defines a class called NegCycleFinder, which is designed to find
negative cycles in a directed graph. A negative cycle is a loop in the graph
where the sum of the edge weights is less than zero. This can be important in
various applications, such as detecting arbitrage opportunities in currency
exchange rates.

The NegCycleFinder takes a directed graph as input. The graph is represented as
a mapping (like a dictionary) where each key is a node, and its value is
another mapping of neighboring nodes and their connecting edges. The class also
works with a distance mapping and a function to get the weight of an edge.

The main output of this class is a list of edges that form a negative cycle in
the graph. It doesn't return this directly, but instead yields these cycles
through a generator function called howard().

To find negative cycles, the class uses two main algorithms: the Bellman-Ford
algorithm and Howard's method. The Bellman-Ford algorithm is used in the
relax() method to update the shortest distances between nodes. Howard's method,
implemented in the howard() function, uses this relaxation step repeatedly to
find negative cycles.

The process works like this: First, the relax() method goes through all edges
in the graph and updates the distances if a shorter path is found. It also
keeps track of which edge led to each node in the pred dictionary. Then, the
find_cycle() method looks for cycles in this predecessor graph. If a cycle is
found, the is_negative() method checks if it's a negative cycle by comparing
the distances and edge weights. If a negative cycle is found, it's yielded by
the howard() method.

An important part of the logic is how the class maintains and updates the pred
dictionary. This dictionary keeps track of which node and edge led to each node
in the shortest path found so far. This information is crucial for
reconstructing the cycles when they're found.

The algorithm skeleton is shared with NegCycleFinderQ (see
``_cycle_base.howard_search``); the unconstrained predecessor relaxation and
the negativity check are supplied as strategies there.
"""

from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Tuple,
    Union,
)

from ._cycle_base import (
    Arc,
    Cycle,
    Domain,
    Node,
    _always_true,
    cycle_list as _cycle_list,
    find_cycle as _find_cycle,
    howard_search as _howard_search,
    is_negative as _is_negative,
    relax_pred as _relax_pred,
)


class NegCycleFinder(Generic[Node, Arc, Domain]):
    """Negative Cycle Finder by Howard's method

    This code defines a `NegCycleFinder` class, which is used to find negative
    cycles in a given directed graph. The `NegCycleFinder` class has the
    following methods:

    1.  `__init__(self, digraph: MutableMapping[Node, List[Arc]])`:
        The constructor initializes an instance of the `NegCycleFinder` class
        with the given directed graph.
    2.  `relax(self, dist: MutableMapping[Node, Domain], get_weight:
        Callable[[Arc], Domain]) -> bool`:
        This method performs one iteration of Bellman-Ford algorithm to relax
        all edges in the graph and update the shortest distances to their
        neighbors. It returns a boolean value indicating if any changes were
        made during this iteration.
    3.  `howard(self, dist: MutableMapping[Node, Domain], get_weight:
        Callable[[Arc], Domain]) -> Generator[Cycle, None, None]`:
        This method finds negative cycles in the graph using the Howard's
        algorithm and returns a generator that yields a list of edges for each
        cycle.
    4.  `cycle_list(self, handle: Node) -> Cycle`:
        This method returns a list of edges that form a cycle in the graph,
        starting from a given node.
    5.  `is_negative(self, handle: Node, dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain]) -> bool`:
        This method checks if a cycle is negative by comparing the distances
        between nodes and the weights of the edges.

    Here's a brief explanation of the algorithms used in this code:

    1.  Bellman-Ford Algorithm: It is a shortest path algorithm that can find
        single source shortest paths in a graph with negative edge weights. It
        runs in O(V*E) time complexity.
    2.  Howard's Policy Graph Algorithm: It is used to find cycles in a directed
        graph and is based on the Bellman-Ford Algorithm. It runs in O(V*E +
        V*E^2) time complexity in the worst case.
    """

    # Dictionary to store predecessor information (node -> (predecessor_node, edge))
    pred: Dict[Node, Tuple[Node, Arc]]

    def __init__(
        self, digraph: Mapping[Node, Union[Mapping[Node, Arc], Mapping[Node, Arc]]]
    ) -> None:
        """Initialize the negative cycle finder with a directed graph.

        Args:
            digraph: A mapping representing a directed graph where:
                - Keys are source nodes
                - Values are iterables of (target_node, edge) pairs
                Example: {u: [(v, edge_uv), (w, edge_uw)], v: [(u, edge_vu)]}
        """
        self.digraph = digraph
        self.pred: Dict[Node, Tuple[Node, Arc]] = {}

    def find_cycle(self) -> Generator[Node, None, None]:
        """Find cycles in the current predecessor graph using depth-first search.

        Yields:
            Generator[Node, None, None]: Each node that starts a cycle in the
                predecessor graph

        Note:
            Uses a coloring algorithm (white/gray/black) to detect cycles:
            - White: unvisited nodes
            - Gray: nodes being visited in current DFS path
            - Black: fully visited nodes

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
        yield from _find_cycle(self.digraph, self.pred)

    def relax(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        """Perform one relaxation pass of the Bellman-Ford algorithm.

        Args:
            dist: Current shortest distance estimates for each node
            get_weight: Function to get weight/cost of an edge

        Returns:
            bool: True if any distance was updated, False otherwise

        Note:
            Updates both distance estimates (dist) and predecessor information
            (pred) for all edges in the graph following the Bellman-Ford
            relaxation rule: if dist[v] > dist[u] + weight(u,v), then update
            dist[v]

        Examples:
            >>> digraph = {
            ...     'a': {'b': 1, 'c': 4},
            ...     'b': {'c': 2},
            ...     'c': {'a': -5}
            ... }
            >>> dist = {'a': 0, 'b': float('inf'), 'c': float('inf')}
            >>> finder = NegCycleFinder(digraph)
            >>> finder.relax(dist, lambda edge: edge)
            True
            >>> dist['b']
            1
            >>> dist['c']
            3
        """
        return _relax_pred(
            self.digraph, dist, get_weight, _always_true, self.pred
        )

    def cycle_list(self, handle: Node) -> Cycle:
        """Reconstruct the cycle starting from the given node.

        Args:
            handle: The starting node of the cycle (must be part of a cycle)

        Returns:
            Cycle: List of edges forming the cycle in order

        Note:
            Follows predecessor links until returning to the starting node

        Examples:
            >>> digraph = {
            ...     'a': {'b': 'ab'},
            ...     'b': {'c': 'bc'},
            ...     'c': {'a': 'ca'}
            ... }
            >>> finder = NegCycleFinder(digraph)
            >>> finder.pred = {'b': ('a', 'ab'), 'c': ('b', 'bc'), 'a': ('c', 'ca')}
            >>> finder.cycle_list('a')
            ['ca', 'bc', 'ab']
        """
        return _cycle_list(self.pred, handle)

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        """Check if the cycle starting at 'handle' is negative.

        Args:
            handle: Starting node of the cycle to check
            dist: Current distance estimates
            get_weight: Function to get edge weights

        Returns:
            bool: True if the cycle is negative, False otherwise

        Note:
            A cycle is negative if the sum of its edge weights is negative.
            This is checked by verifying that for at least one edge (u,v) in the
            cycle, dist[v] > dist[u] + weight(u,v) (triangle inequality
            violation)

        Examples:
            >>> digraph = {
            ...     'a': {'b': 1},
            ...     'b': {'c': 1},
            ...     'c': {'a': -3}
            ... }
            >>> dist = {'a': 0, 'b': 1, 'c': 2}
            >>> finder = NegCycleFinder(digraph)
            >>> finder.pred = {'b': ('a', 1), 'c': ('b', 1), 'a': ('c', -3)}
            >>> finder.is_negative('a', dist, lambda edge: edge)
            True
        """
        return _is_negative(self.pred, handle, dist, get_weight)

    def howard(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> Generator[Cycle, None, None]:
        """Main algorithm to find negative cycles using Howard's method.

        Args:
            dist: Initial distance estimates (often initialized to zero)
            get_weight: Function to get edge weights

        Yields:
            Generator[Cycle, None, None]: Each found negative cycle as a list of edges

        Note:
            1. Repeatedly relaxes edges until no more improvements can be made
            2. Checks for cycles in the predecessor graph
            3. Verifies if found cycles are negative
            4. Yields each negative cycle found

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
        yield from _howard_search(
            self.digraph, dist, get_weight, _always_true, self.pred, "pred"
        )
