# Experiment: spare TSV network flow optimization

import matplotlib.pyplot as plt

from experimental.spare_tsv import (
    formGraph,
    setup_network_flow,
    showPaths,
    solve_network_flow,
    vdcorput,
)

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
result = solve_network_flow(gra, sink)

if result is None:
    print("Solution Infeasible!")
else:
    flow_cost, pathlist = result
    gra.remove_node(sink)
    fig, ax = showPaths(gra, pos2, N, path=pathlist)
    plt.show()
