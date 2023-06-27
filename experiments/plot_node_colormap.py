"""
=============
Node Colormap
=============

Draw a graph with matplotlib, color by degree.
"""

import matplotlib.pyplot as plt
import networkx as nx

gra = nx.cycle_graph(24)
pos = nx.spring_layout(gra, iterations=200)
nx.draw(gra, pos, node_color=range(24), node_size=800, cmap=plt.cm.Blues)
plt.show()
