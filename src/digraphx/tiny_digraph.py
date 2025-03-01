"""
TinyDiGraph

This code defines a custom graph data structure called TinyDiGraph, which is designed to be a lightweight and efficient implementation of a directed graph. The purpose of this code is to provide a simple way to create and manipulate directed graphs, particularly for cases where performance and memory efficiency are important.

The main input for this code is the number of nodes in the graph, which is set when initializing the graph using the init_nodes method. The code doesn't directly produce any output, but it provides methods to add edges, count nodes and edges, and iterate through the graph's structure.

TinyDiGraph achieves its purpose by subclassing from DiGraphAdapter, which in turn inherits from NetworkX's DiGraph class. This allows TinyDiGraph to leverage existing graph functionality while customizing certain aspects for efficiency. The key feature of TinyDiGraph is its use of a custom data structure called MapAdapter (likely a list-based dictionary) to store node and edge information.

The code implements several important methods:

1. cheat_node_dict and cheat_adjlist_outer_dict: These methods create MapAdapter objects to store node and edge information efficiently.
2. init_nodes: This method initializes the graph with a specified number of nodes, setting up the necessary data structures.

The main logic flow of the code is as follows:

1. Define the TinyDiGraph class with custom node and edge storage methods.
2. Provide a method to initialize the graph with a given number of nodes.
3. Set up the graph structure using MapAdapter objects for efficient storage and access.

At the end of the file, there's a small example of how to use TinyDiGraph. It creates a graph with 1000 nodes, adds an edge, and then demonstrates how to iterate through the graph and access its properties.

The code also includes a brief demonstration of the MapAdapter data structure, showing how it can be used as an efficient list-like dictionary.

Overall, this code provides a foundation for working with directed graphs in a memory-efficient manner, which could be particularly useful for large graphs or in situations where performance is critical.
"""

import networkx as nx
from mywheel.map_adapter import MapAdapter


class DiGraphAdapter(nx.DiGraph):
    def items(self):
        return self.adjacency()


class TinyDiGraph(DiGraphAdapter):
    num_nodes = 0

    def cheat_node_dict(self):
        return MapAdapter([dict() for _ in range(self.num_nodes)])

    def cheat_adjlist_outer_dict(self):
        return MapAdapter([dict() for _ in range(self.num_nodes)])

    node_dict_factory = cheat_node_dict
    adjlist_outer_dict_factory = cheat_adjlist_outer_dict

    def init_nodes(self, n: int):
        """
        The function initializes the number of nodes, a dictionary for nodes, and dictionaries for
        adjacency and predecessor lists.

        :param n: The parameter `n` represents the number of nodes in the graph
        :type n: int
        """
        self.num_nodes = n
        self._node = self.cheat_node_dict()
        self._adj = self.cheat_adjlist_outer_dict()
        self._pred = self.cheat_adjlist_outer_dict()


if __name__ == "__main__":
    gr = TinyDiGraph()
    gr.init_nodes(1000)
    gr.add_edge(2, 1)
    print(gr.number_of_nodes())
    print(gr.number_of_edges())

    for utx in gr:
        for vtx in gr.neighbors(utx):
            print(f"{utx}, {vtx}")

    a = MapAdapter([0] * 8)
    for i in a:
        a[i] = i * i
    for i, vtx in a.items():
        print(f"{i}: {vtx}")
    print(3 in a)
