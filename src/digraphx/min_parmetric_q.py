"""
Generalized Howard algorithm Solve minimum parametric network problems

"""

from .neg_cycle import NegCycleFinder


def min_parametric(gra, ratio, cost, zero_cancel, dist, update_ok, pick_one_only=False):
    """
    The `min_parametric` function solves a minimum parametric problem by finding the smallest value of a
    parameter that satisfies a set of constraints in a directed graph:

        min  r
        s.t. dist[v] - dist[v] ≤ cost(u, v, r)
             for all (u, v) in gra

    :param gra: The parameter `gra` represents a directed graph
    :param ratio: The parameter to be minimized. It is initially set to a small number and will be
    updated during the optimization process
    :param cost: The `cost` parameter is a function that takes in three arguments: `ratio`, `edge`, and
    `r`. It represents the cost of traversing an edge in the graph. The `ratio` parameter is the current
    value of the ratio being minimized, `edge` is the edge being considered
    :param zero_cancel: The `zero_cancel` parameter is a function that takes a cycle `c_i` and returns a
    modified cycle `c_i'` such that `cost(u, v, zero_cancel(c_i')) = 0` if and only if `cost(u, v, c_i)
    = 0
    :param dist: The `dist` parameter represents the distances between vertices in the directed graph
    `gra`. It is used in the constraint of the minimum parametric problem to ensure that the difference
    between the distances of two vertices is less than or equal to the cost of the corresponding edge
    :param update_ok: The `update_ok` parameter is a function that determines whether an update to the
    distance value is allowed or not. It takes two arguments: the current distance value and the new
    distance value. If the function returns `True`, the update is allowed. If it returns `False`, the
    update is not
    :param pick_one_only: A boolean parameter that determines whether to pick only one cycle with the
    maximum ratio or to consider all cycles with the maximum ratio. If set to True, only one cycle will
    be picked. If set to False, all cycles with the maximum ratio will be considered, defaults to False
    (optional)
    :return: The function `min_parametric` returns three values: `ratio`, `cycle`, and `dist`.
    """

    def get_weight(edge):
        return cost(ratio, edge)

    omega = NegCycleFinder(gra)
    r_max = ratio
    cycle = None
    reverse = True

    while True:
        if reverse:
            cycles = omega.find_neg_cycle_succ(dist, get_weight, update_ok)
        else:
            cycles = omega.find_neg_cycle_pred(dist, get_weight, update_ok)

        for c_i in cycles:
            r_i = zero_cancel(c_i)
            if r_max < r_i:
                r_max = r_i
                c_max = c_i
                if pick_one_only:
                    break
        if r_max <= ratio:
            break

        cycle = c_max
        ratio = r_max
        reverse = not reverse
    return ratio, cycle


# if __name__ == "__main__":
#     from __future__ import print_function
#     from pprint import pprint
#     import networkx as nx
#     from neg_cycle import *
#     from networkx.utils import generate_unique_node

#     gra = create_test_case1()
#     gra[1][2]['cost'] = 5
#     r, c, dist = max_cycle_ratio(gra)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())

#     gra = nx.cycle_graph(5, create_using=nx.DiGraph())
#     gra[1][2]['cost'] = -6.
#     newnode = generate_unique_node()
#     gra.add_edges_from([(newnode, n) for n in gra])
#     r, c, dist = max_cycle_ratio(gra)
#     assert c != None
#     print(r)
#     print(c)
#     print(dist.items())
