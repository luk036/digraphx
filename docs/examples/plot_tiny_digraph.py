"""
TinyDiGraph visualization
=========================

Example of creating and visualizing a directed graph using TinyDiGraph.
"""
from digraphx.tiny_digraph import TinyDiGraph
import matplotlib.pyplot as plt
import networkx as nx

g = TinyDiGraph()
g.init_nodes(5)
g.add_edge(0, 1)
g.add_edge(1, 2)
g.add_edge(2, 3)
g.add_edge(3, 0)
g.add_edge(0, 4)
g.add_edge(4, 2)

plt.figure(figsize=(6, 5))
pos = nx.spring_layout(g, seed=42)
nx.draw(g, pos, with_labels=True, node_color='lightblue',
        node_size=500, arrowsize=20, font_weight='bold')
plt.title("TinyDiGraph with 5 nodes and 6 edges")
plt.grid(True, alpha=0.3)
