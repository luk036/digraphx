"""
=============
Node Colormap
=============

Draw a graph with matplotlib, color by degree.
"""

import matplotlib.pyplot as plt
import networkx as nx

digraph = nx.cycle_graph(24)
pos = nx.spring_layout(digraph, iterations=200)
nx.draw(digraph, pos, node_color=range(24), node_size=800, cmap=plt.cm.Blues)
plt.show()
