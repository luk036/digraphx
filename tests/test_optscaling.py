# -*- coding: utf-8 -*-
from __future__ import print_function

import networkx as nx
import numpy as np
from ellalgo.cutting_plane import cutting_plane_optim
from ellalgo.ell import Ell

from netoptim.optscaling_oracle import OptScalingOracle


def vdc(n, base=2):
    """[summary]

    Arguments:
        n ([type]): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    vdc, denom = 0.0, 1.0
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    """[summary]

    Arguments:
        n ([type]): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    return [vdc(i, base) for i in range(n)]


def formGraph(T, pos, eta, seed=None):
    """Form N by N grid of nodes, connect nodes within eta.
        mu and eta are relative to 1/(N-1)

    Arguments:
        t (float): [description]
        pos ([type]): [description]
        eta ([type]): [description]

    Keyword Arguments:
        seed ([type]): [description] (default: {None})

    Returns:
        [type]: [description]
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
    gra = nx.DiGraph(gra)
    # gra.add_node('dummy', pos = (0.3, 0.4))
    # gra.add_edge('dummy', 1)
    # gra.nodemap = {vtx : i_v for i_v, vtx in enumerate(gra.nodes())}
    return gra


N = 75
M = 20
T = N + M
xbase = 2
ybase = 3
x = [i for i in vdcorput(T, xbase)]
y = [i for i in vdcorput(T, ybase)]
pos = zip(x, y)
gra = formGraph(T, pos, 1.6, seed=5)
# for utx, vtx in gra.edges():
#     h = np.array(gra.nodes()[utx]['pos']) - np.array(gra.nodes()[vtx]['pos'])
#     gra[utx][vtx]['cost'] = np.sqrt(h @ h)

for utx, vtx in gra.edges():
    h = np.array(gra.nodes()[utx]["pos"]) - np.array(gra.nodes()[vtx]["pos"])
    gra[utx][vtx]["cost"] = np.log(np.sqrt(h @ h))

cmax = max(cycle for _, _, cycle in gra.edges.data("cost"))
cmin = min(cycle for _, _, cycle in gra.edges.data("cost"))


def get_cost(edge):
    utx, vtx = edge
    return gra[utx][vtx]["cost"]


def test_optscaling():
    """[summary]

    Keyword Arguments:
        duration (float): [description] (default: {0.000001})

    Returns:
        [type]: [description]
    """
    xinit = np.array([cmax, cmin])
    t = cmax - cmin
    ellip = Ell(1.5 * t, xinit)
    dist = list(0 for _ in gra)
    omega = OptScalingOracle(gra, dist, get_cost)
    xbest, _, _ = cutting_plane_optim(omega, ellip, float("inf"))
    # fmt = '{:f} {} {} {}'
    # print(np.exp(xbest))
    # print(fmt.format(np.exp(fb), niter, feasible, status))
    assert xbest is not None
    # return ell_info.num_iters
