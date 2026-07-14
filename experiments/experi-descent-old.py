# Experiment: spare TSV (OLD method: MCF without vertex-disjoint constraint)

import matplotlib.pyplot as plt

from digraphx.mcf import cycle_canceling_mcf
from experimental.spare_tsv import formGraph, setup_network_flow, showPaths, vdcorput


def nx_to_dict_graph(gra, sink):
    g = {}
    demands = {}
    for u in gra.nodes():
        d = gra.nodes[u].get("demand", 0)
        if d != 0 or u == sink:
            demands[u] = d
    for u, v, data in gra.edges(data=True):
        if u not in g:
            g[u] = {}
        g[u][v] = {
            "weight": data.get("weight", 0),
            "capacity": data.get("capacity", 1),
        }
    return g, demands


N = 155
M = 40
r = 4

T = N + M
xbase = 2
ybase = 3
x = [i for i in vdcorput(T, xbase)]
y = [i for i in vdcorput(T, ybase)]
pos = list(zip(x, y))
gra = formGraph(T, pos, 0.12, 1.6, seed=5)
pos2 = dict(enumerate(pos))
fig, ax = showPaths(gra, pos2, N)
plt.show()

sink = setup_network_flow(gra, pos, primal_count=N, capacity=r)

g, demands = nx_to_dict_graph(gra, sink)
result = cycle_canceling_mcf(g, demands)  # no sink → no constraint

if result is None:
    print("Solution Infeasible!")
else:
    flow_cost, flow_dict = result
    print(f"Flow cost (old): {flow_cost}")

    pathlist = [
        (u, v)
        for u in flow_dict
        for v, f in flow_dict[u].items()
        if f > 0 and v != sink
    ]

    # Count violations
    outgoing = {}
    for u, v in pathlist:
        if u in outgoing:
            print(f"  VIOLATION: node {u} -> {outgoing[u]} and -> {v}")
        outgoing[u] = v
    violations = len(pathlist) - len(outgoing)
    print(
        f"Path edges: {len(pathlist)}, unique sources: {len(outgoing)}, violations: {violations}"
    )

    gra.remove_node(sink)
    fig, ax = showPaths(gra, pos2, N, path=pathlist)
    plt.show()
