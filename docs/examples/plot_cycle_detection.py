"""
Negative Cycle Detection
========================

Demonstrates negative cycle detection in a weighted directed graph.
"""
import matplotlib.pyplot as plt
import networkx as nx

g = nx.DiGraph()
g.add_edge(1, 2, w=2)
g.add_edge(2, 3, w=-3)
g.add_edge(3, 1, w=1)
g.add_edge(2, 4, w=1)
g.add_edge(4, 5, w=-1)
g.add_edge(5, 2, w=2)

plt.figure(figsize=(7, 5))
pos = nx.spring_layout(g, seed=42)
nx.draw(g, pos, with_labels=True, node_color='lightcoral',
        node_size=600, arrowsize=20, font_weight='bold')
edge_labels = {(u, v): f"w={d['w']}" for u, v, d in g.edges(data=True)}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
plt.title("Directed Graph with Potential Negative Cycles")
plt.grid(True, alpha=0.3)
