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

# Type variables for generic graph implementation:
# Node must be hashable (used as dictionary keys)
# Edge can be any type (but typically hashable)
# Domain must support comparison and arithmetic operations (int, Fraction, float)
Node = TypeVar("Node")  # Hashable
Edge = TypeVar("Edge")  # Hashable
Domain = TypeVar("Domain", int, Fraction, float)  # Comparable Ring
Cycle = List[Edge]  # List of Edges


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

    The class implements both predecessor and successor versions of Howard's algorithm,
    providing flexibility in how negative cycles are detected and processed.
    """

    # Predecessor dictionary: maps each node to (predecessor_node, connecting_edge)
    pred: Dict[Node, Tuple[Node, Edge]] = {}

    # Successor dictionary: maps each node to (successor_node, connecting_edge)
    succ: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, digraph: Mapping[Node, Mapping[Node, Edge]]) -> None:
        """Initialize the negative cycle finder with a directed graph.

        Args:
            digraph: A directed graph represented as a nested mapping:
                - Outer keys: source nodes
                - Inner mappings: {target_node: edge} pairs
                Example: {u: {v: edge_uv, w: edge_uw}, v: {u: edge_vu}}
        """
        self.digraph = digraph

    def find_cycle(self, point_to) -> Generator[Node, None, None]:
        """Detect cycles in the current predecessor/successor graph using depth-first search.

        Args:
            point_to: Either self.pred or self.succ dictionary defining the graph edges

        Yields:
            Generator[Node, None, None]: Each node that starts a cycle in the graph

        Algorithm:
            1. Uses a coloring approach (white/gray/black) for cycle detection
            2. White nodes are unvisited
            3. Gray nodes are currently being visited in DFS stack
            4. Black nodes are fully processed
            5. A cycle is detected when we encounter a gray node during DFS

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
        visited: Dict[Node, Node] = {}  # Maps nodes to their DFS root
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            while True:
                visited[utx] = vtx  # Mark as visited with current DFS root
                if utx not in point_to:
                    break  # Reached a leaf node
                utx, _ = point_to[utx]  # Move to predecessor/successor
                if utx in visited:
                    if visited[utx] == vtx:  # Found cycle back to current root
                        yield utx
                    break  # Cycle or different DFS tree

    def relax_pred(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> bool:
        """Perform predecessor relaxation step (Bellman-Ford style).

        Args:
            dist: Current distance estimates for each node
            get_weight: Function to get weight of an edge
            update_ok: Function to determine if distance update should be applied

        Returns:
            bool: True if any distances were updated, False otherwise

        Note:
            Updates distances based on predecessor edges (u -> v)
            Implements the relaxation: if dist[v] > dist[u] + weight(u,v), update dist[v]
        """
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[utx] + get_weight(edge)
                if dist[vtx] > distance and update_ok(dist[vtx], distance):
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)  # Update predecessor
                    changed = True
        return changed

    def relax_succ(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> bool:
        """Perform successor relaxation step (reverse Bellman-Ford style).

        Args:
            dist: Current distance estimates for each node
            get_weight: Function to get weight of an edge
            update_ok: Function to determine if distance update should be applied

        Returns:
            bool: True if any distances were updated, False otherwise

        Note:
            Updates distances based on successor edges (u -> v)
            Implements the relaxation: if dist[u] < dist[v] - weight(u,v), update dist[u]
        """
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[vtx] - get_weight(edge)
                if dist[utx] < distance and update_ok(dist[utx], distance):
                    dist[utx] = distance
                    self.succ[utx] = (vtx, edge)  # Update successor
                    changed = True
        return changed

    def howard_pred(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> Generator[Cycle, None, None]:
        """Find negative cycles using predecessor-based Howard's algorithm.

        Args:
            dist: Initial distance estimates (often zero-initialized)
            get_weight: Function to get weight of an edge
            update_ok: Function to determine if distance updates are allowed

        Yields:
            Generator[Cycle, None, None]: Each negative cycle found as a list of edges

        Algorithm:
            1. Repeatedly relax edges using predecessor updates
            2. After each relaxation, check for cycles in predecessor graph
            3. If cycle found, verify if it's negative
            4. Yield each negative cycle found

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
        self.pred = {}  # Reset predecessor graph
        found = False
        while not found and self.relax_pred(dist, get_weight, update_ok):
            for vtx in self.find_cycle(self.pred):
                # Safety check - verify the cycle is indeed negative
                assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx, self.pred)

    def howard_succ(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
        update_ok: Callable[[Domain, Domain], bool],
    ) -> Generator[Cycle, None, None]:
        """Find negative cycles using successor-based Howard's algorithm.

        Args:
            dist: Initial distance estimates (often zero-initialized)
            get_weight: Function to get weight of an edge
            update_ok: Function to determine if distance updates are allowed

        Yields:
            Generator[Cycle, None, None]: Each negative cycle found as a list of edges

        Note:
            Similar to howard_pred but uses successor updates instead of predecessor
            Currently skips the negative cycle verification (commented assert)

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
        self.succ = {}  # Reset successor graph
        found = False
        while not found and self.relax_succ(dist, get_weight, update_ok):
            for vtx in self.find_cycle(self.succ):
                # Note: Negative verification currently disabled
                # assert self.is_negative(vtx, dist, get_weight)
                found = True
                yield self.cycle_list(vtx, self.succ)

    def cycle_list(self, handle: Node, point_to) -> Cycle:
        """Reconstruct the cycle starting from the given node.

        Args:
            handle: Starting node of the cycle
            point_to: Either self.pred or self.succ dictionary defining the edges

        Returns:
            Cycle: List of edges forming the cycle in order

        Note:
            Follows the predecessor/successor links until returning to starting node
        """
        vtx = handle
        cycle = list()
        while True:
            utx, edge = point_to[vtx]  # Get next node and connecting edge
            cycle.append(edge)  # Add edge to cycle
            vtx = utx  # Move to next node
            if vtx == handle:  # Completed the cycle
                break
        return cycle

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
    ) -> bool:
        """Verify if the cycle starting at handle is negative.

        Args:
            handle: Starting node of the cycle
            dist: Current distance estimates
            get_weight: Function to get weight of an edge

        Returns:
            bool: True if the cycle is negative, False otherwise

        Note:
            A cycle is negative if the sum of its edge weights is negative
            This is detected by finding at least one edge that violates the
            triangle inequality: dist[v] > dist[u] + weight(u,v)
        """
        vtx = handle
        # C-style do-while loop
        while True:
            utx, edge = self.pred[vtx]
            if dist[vtx] > dist[utx] + get_weight(edge):
                return True  # Found negative cycle
            vtx = utx
            if vtx == handle:  # Completed full cycle
                break
        return False
