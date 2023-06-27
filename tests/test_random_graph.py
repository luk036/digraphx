import networkx as nx
import numpy as np

from digraphx.min_cycle_ratio import MinCycleRatioSolver


def vdc(n, base=2):
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    """
    n - number of vectors
    base - seeds
    """
    return [vdc(i, base) for i in range(n)]


def formGraph(T, pos, eta, seed=None):
    """Form N by N grid of nodes, connect nodes within eta.
    mu and eta are relative to 1/(N-1)
    """
    if seed:
        np.random.seed(seed)

    N = np.sqrt(T)
    eta = eta / (N - 1)

    # generate perterbed grid positions for the nodes
    pos = dict(enumerate(pos))
    n = len(pos)

    # connect nodes with edges
    gra = nx.random_geometric_graph(n, eta, pos=pos)
    return gra


# if __name__ == "__main__":
def test_random_graph():
    N = 158
    M = 40
    #    r = 4

    T = N + M
    xbase = 2
    ybase = 3
    x = [i for i in vdcorput(T, xbase)]
    y = [i for i in vdcorput(T, ybase)]
    pos = zip(x, y)
    gra = formGraph(T, pos, 1.6, seed=5)
    #    n = gra.number_of_nodes()
    #    pos2 = dict(enumerate(pos))
    #    fig, ax = showPaths(gra, pos2, N)
    #    plt.show()

    # Add a sink, connect all spareTSV to it.
    # pos = pos + [(1.5,.5)]
    for utx, vtx in gra.edges():
        h = np.array(gra.nodes()[utx]["pos"]) - np.array(gra.nodes()[vtx]["pos"])
        gra[utx][vtx]["cost"] = np.sqrt(np.dot(h, h))
        gra[utx][vtx]["time"] = 1
        # gra[utx][vtx]['cost'] = h[0] + h[1]

    dist = list(0 for _ in gra)
    solver = MinCycleRatioSolver(gra)
    _, cycle = solver.run(dist, 1e100)
    assert cycle is not None

    pathlist = cycle
    print(pathlist)


#    pos2 = dict(enumerate(pos))
#    fig, ax = showPaths(gra, pos2, N, path=pathlist)
#    plt.show()
