"""
TinyDiGraph

This code defines a custom graph data structure called TinyDiGraph, which is
designed to be a lightweight and efficient implementation of a directed graph.
The purpose of this code is to provide a simple way to create and manipulate
directed graphs, particularly for cases where performance and memory
efficiency are important.

The main input for this code is the number of nodes in the graph, which is set
when initializing the graph using the init_nodes method. The code doesn't
directly produce any output, but it provides methods to add edges, count nodes
and edges, and iterate through the graph's structure.

TinyDiGraph achieves its purpose by subclassing from DiGraphAdapter, which in
turn inherits from NetworkX's DiGraph class. This allows TinyDiGraph to
leverage existing graph functionality while customizing certain aspects for
efficiency. The key feature of TinyDiGraph is its use of a custom data
structure called MapAdapter (likely a list-based dictionary) to store node
and edge information.

The code implements several important methods:

1. cheat_node_dict and cheat_adjlist_outer_dict: These methods create
   MapAdapter objects to store node and edge information efficiently.
2. init_nodes: This method initializes the graph with a specified number of
   nodes, setting up the necessary data structures.

The main logic flow of the code is as follows:

1. Define the TinyDiGraph class with custom node and edge storage methods.
2. Provide a method to initialize the graph with a given number of nodes.
3. Set up the graph structure using MapAdapter objects for efficient storage
   and access.

At the end of the file, there's a small example of how to use TinyDiGraph. It
creates a graph with 1000 nodes, adds an edge, and then demonstrates how to
iterate through the graph and access its properties.

The code also includes a brief demonstration of the MapAdapter data structure,
showing how it can be used as an efficient list-like dictionary.

Overall, this code provides a foundation for working with directed graphs in a
memory-efficient manner, which could be particularly useful for large graphs or
in situations where performance is critical.
"""

from typing import ItemsView, Iterator, MutableMapping

import networkx as nx
from mywheel.map_adapter import MapAdapter  # type: ignore


class DiGraphAdapter(nx.DiGraph, MutableMapping):
    def __iter__(self) -> Iterator:

        return super().__iter__()

    def __setitem__(self, key: object, value: object) -> None:

        super().__setitem__(key, value)

    def __delitem__(self, key: object) -> None:

        super().__delitem__(key)

    def items(self) -> ItemsView:
        """Returns an iterator over (node, adjacency dict) pairs for all nodes.

        This method overrides the default items() method to use adjacency() instead,
        providing a consistent interface for iterating through the graph's nodes
        and their connections.

        Examples:
            >>> graph = DiGraphAdapter()
            >>> graph.add_edge(1, 2)
            >>> graph.add_edge(2, 3)
            >>> sorted(list(graph.items()))
            [(1, {2: {}}), (2, {3: {}}), (3, {})]
        """

        return self.adjacency()


# Sentinel — a dict is only allocated when a node is first used
_UNINIT = object()


class _LazyMapAdapter(MapAdapter):
    """MapAdapter that treats ``_UNINIT`` sentinels as empty dicts.

    ``items()`` and ``values()`` skip uninitialised slots so that
    ``OutEdgeView`` and other internal NetworkX machinery only see
    nodes that actually have adjacency data.
    """

    def __getitem__(self, key: int):  # type: ignore
        val = self.lst[key]
        if val is _UNINIT:
            return {}
        return val

    def items(self):  # type: ignore
        for key, val in enumerate(self.lst):
            if val is not _UNINIT:
                yield key, val

    def values(self):  # type: ignore
        for val in self.lst:
            if val is not _UNINIT:
                yield val


class TinyDiGraph(DiGraphAdapter):
    """A lightweight directed graph implementation optimized for performance and memory efficiency.

    This class extends DiGraphAdapter to provide custom storage mechanisms using MapAdapter,
    which is particularly efficient for graphs with a known, fixed number of nodes.

    .. svgbob::
       :align: center

           o──────►o
           │       │
           │       │
           ▼       ▼
           o◄──────o
    """

    num_nodes = 0  # Class variable to store the total number of nodes in the graph

    def cheat_node_dict(self) -> MapAdapter:
        """Creates a MapAdapter instance to store node attributes.

        Returns:
            MapAdapter: A list-based dictionary where each node's attributes are stored
                       in a separate dictionary at the node's index position.

        Examples:
            >>> graph = TinyDiGraph()
            >>> graph.init_nodes(3)
            >>> node_dict = graph.cheat_node_dict()
            >>> list(node_dict.keys())
            [0, 1, 2]
            >>> node_dict[0]
            {}
        """
        return MapAdapter([dict() for _ in range(self.num_nodes)])

    def cheat_adjlist_outer_dict(self) -> MapAdapter:
        """Creates a MapAdapter instance to store adjacency lists.

        Returns:
            MapAdapter: A list-based dictionary where nodes store ``_UNINIT`` sentinels.
                       Dicts are allocated lazily on first access — this saves ~232 bytes
                       per node for nodes that never have edges.

        Examples:
            >>> graph = TinyDiGraph()
            >>> graph.init_nodes(2)
            >>> adj_list = graph.cheat_adjlist_outer_dict()
            >>> list(adj_list.keys())
            [0, 1]
            >>> adj_list[0] is _UNINIT
            True
        """
        return _LazyMapAdapter([_UNINIT] * self.num_nodes)

    def node_dict_factory(self) -> MapAdapter:  # type: ignore
        """Return `cheat_node_dict` function.

        The `node_dict_factory` method is responsible for creating a factory
        that produces the dictionary used to store node attributes in the
        `TinyDiGraph`. In this specific implementation, it returns the
        `cheat_node_dict` method, which is a custom function designed to create
        a `MapAdapter` instance. This `MapAdapter` serves as a highly
        efficient, list-based dictionary for storing node attributes.

        The primary purpose of this method is to allow `TinyDiGraph` to
        leverage a more memory-efficient data structure for its node storage
        compared to a standard Python dictionary. By using a `MapAdapter`, the
        graph can achieve better performance, especially when the number of
        nodes is known in advance. This method is part of the internal factory
        customization that allows `TinyDiGraph` to be optimized for specific use
        cases.

        Returns:
            MapAdapter: a list-based dictionary for storing node attributes

        Examples:
            >>> graph = TinyDiGraph()
            >>> graph.init_nodes(3)
            >>> factory = graph.node_dict_factory()
            >>> isinstance(factory, MapAdapter)
            True

        """
        return self.cheat_node_dict()

    def adjlist_outer_dict_factory(self) -> MapAdapter:  # type: ignore
        """Return `cheat_adjlist_outer_dict` function.

        The `adjlist_outer_dict_factory` method is responsible for creating a
        factory that produces the outer dictionary for the adjacency list of the
        `TinyDiGraph`. In this case, it returns the `cheat_adjlist_outer_dict`
        method, which is a custom method designed to create a `MapAdapter`
        instance. This `MapAdapter` serves as a highly efficient, list-based
        dictionary for storing the adjacency lists of each node in the graph.

        The primary purpose of this method is to allow `TinyDiGraph` to
        leverage a more memory-efficient data structure for its adjacency list
        compared to a standard Python dictionary. By using a `MapAdapter`, the
        graph can achieve better performance, especially when the number of
        nodes is known in advance. This method is part of the internal factory
        customization that allows `TinyDiGraph` to be optimized for specific use
        cases.

        Returns:
            MapAdapter: a list-based dictionary for storing node attributes

        Examples:
            >>> graph = TinyDiGraph()
            >>> graph.init_nodes(2)
            >>> factory = graph.adjlist_outer_dict_factory()
            >>> isinstance(factory, MapAdapter)
            True

        """
        return self.cheat_adjlist_outer_dict()

    def _ensure_adj(self, n: int) -> None:
        # Access underlying list directly to bypass _LazyMapAdapter.__getitem__
        if self._succ.lst[n] is _UNINIT:
            self._succ.lst[n] = {}
            self._pred.lst[n] = {}

    # ---- overrides that handle lazy slots ----

    def _adj_init(self, n: int) -> bool:
        """Return True if slot *n* is still the sentinel (bypassing __getitem__)."""
        return self._succ.lst[n] is _UNINIT

    def add_edge(self, u_of_edge, v_of_edge, **attr):  # type: ignore
        u, v = u_of_edge, v_of_edge
        self._ensure_adj(u)
        self._ensure_adj(v)
        super().add_edge(u, v, **attr)

    def add_edges_from(self, ebunch_to_add, **attr):  # type: ignore
        for e in ebunch_to_add:
            ne = len(e)
            if ne == 3:
                u, v, dd = e
                d = {**attr, **dd}
                self.add_edge(u, v, **d)
            elif ne == 2:
                u, v = e
                if attr:
                    self.add_edge(u, v, **attr)
                else:
                    self.add_edge(u, v)
            else:
                raise nx.NetworkXError(f"Edge tuple {e} must be a 2-tuple or 3-tuple.")

    def __getitem__(self, n):
        if n not in self._node:
            raise nx.NetworkXError(f"The node {n} is not in the digraph.")
        self._ensure_adj(n)
        return super().__getitem__(n)

    def has_edge(self, u, v):  # type: ignore
        if self._adj_init(u):
            return False
        return super().has_edge(u, v)

    def successors(self, n):  # type: ignore
        # _LazyMapAdapter.__getitem__ already converts _UNINIT → {}
        try:
            return iter(self._succ[n])
        except KeyError as err:
            raise nx.NetworkXError(f"The node {n} is not in the digraph.") from err

    neighbors = successors  # type: ignore

    def items(self):
        for n in range(self.num_nodes):
            if not self._adj_init(n):
                yield n, self._succ.lst[n]

    def adjacency(self):  # type: ignore
        return self.items()

    def remove_edge(self, u, v):  # type: ignore
        if self._adj_init(u) or v not in self._succ[u]:
            raise nx.NetworkXError(f"The edge {u}-{v} is not in the graph.")
        super().remove_edge(u, v)

    def get_edge_data(self, u, v, default=None):  # type: ignore
        if self._adj_init(u):
            return default
        return super().get_edge_data(u, v, default)

    def out_degree(self, n=None):  # type: ignore
        if n is None:
            return super().out_degree(n)
        if self._adj_init(n):
            return 0
        return super().out_degree(n)

    def in_degree(self, n=None):  # type: ignore
        if n is None:
            return super().in_degree(n)
        if self._adj_init(n):
            return 0
        return super().in_degree(n)

    # ---- init ----

    def init_nodes(self, num_nodes: int) -> None:
        """Initializes the graph with a specified number of nodes.

        Sets up the internal data structures for node storage, adjacency lists (successors),
        and predecessor lists. This method must be called before adding any edges.

        Args:
            num_nodes (int): The number of nodes to initialize in the graph. Nodes will be
                      indexed from 0 to num_nodes-1.

        Examples:
            >>> graph = TinyDiGraph()
            >>> graph.init_nodes(5)
            >>> graph.number_of_nodes()
            5
            >>> list(graph._node.keys())
            [0, 1, 2, 3, 4]
            >>> list(graph._adj.keys())
            [0, 1, 2, 3, 4]
        """
        self.num_nodes = num_nodes
        self._node = self.cheat_node_dict()  # Stores node attributes
        self._adj = (
            self.cheat_adjlist_outer_dict()
        )  # Stores outgoing edges (successors)
        self._pred = (
            self.cheat_adjlist_outer_dict()
        )  # Stores incoming edges (predecessors)


if __name__ == "__main__":
    # Example usage of TinyDiGraph
    graph = TinyDiGraph()
    graph.init_nodes(1000)  # Initialize graph with 1000 nodes
    graph.add_edge(2, 1)  # Add an edge from node 2 to node 1

    # Print basic graph properties
    print(graph.number_of_nodes())  # Expected output: 1000
    print(graph.number_of_edges())  # Expected output: 1

    # Iterate through all edges in the graph
    for utx in graph:
        for vtx in graph.neighbors(utx):
            print(f"{utx}, {vtx}")  # Will print "2, 1"

    # Demonstration of MapAdapter functionality
    a = MapAdapter([0] * 8)  # Create a MapAdapter with 8 zero-initialized elements
    for idx in a:
        a[idx] = idx * idx  # Square each element's index and store it
    for idx, vtx in a.items():
        print(f"{idx}: {vtx}")  # Print index: value pairs
    print(3 in a)  # Check if index 3 exists (should return True)
