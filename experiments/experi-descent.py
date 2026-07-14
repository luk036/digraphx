# Experiment: spare TSV network flow optimization using cycle-cancellation descent

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from digraphx.mcf import cycle_canceling_mcf  # noqa: E402
from experimental.spare_tsv import (  # noqa: E402
    formGraph,
    setup_network_flow,
    showPaths,
    vdcorput,
)


def nx_to_dict_graph(gra, sink):
    """Convert networkx graph to dict-of-dicts for cycle_canceling_mcf.

    Extracts weight/capacity from edge data and demand from node data.
    Excludes the sink node (added separately by setup logic).
    """
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
fig.savefig("spareTSV-initial.svg")
plt.close(fig)

# Set up the network flow graph (weights, capacities, demands, sink)
sink = setup_network_flow(gra, pos, primal_count=N, capacity=r)

# Convert to dict-of-dicts format and solve via cycle-cancellation descent
g, demands = nx_to_dict_graph(gra, sink)
result = cycle_canceling_mcf(g, demands, sink=sink)

if result is None:
    print("Solution Infeasible!")
else:
    flow_cost, flow_dict = result
    print(f"Flow cost: {flow_cost}")

    # Extract path edges with positive flow, excluding sink
    pathlist = [
        (u, v)
        for u in flow_dict
        for v, f in flow_dict[u].items()
        if f > 0 and v != sink
    ]

    gra.remove_node(sink)
    fig, ax = showPaths(gra, pos2, N, path=pathlist)
    fig.savefig("spareTSV-solution.svg")
    plt.close(fig)
