# -*- coding: utf-8 -*-
"""
Negative cycle detection for weighed graphs.
1. Support Lazy evalution
"""
from typing import Dict, Generator


# The `NegCycleFinder` class is used to find negative cycles in a graph.
class NegCycleFinder:
    pred: Dict = {}
    succ: Dict = {}

    def __init__(self, gra) -> None:
        """
        The above function is the initialization method for a class, which takes a graph as an argument and
        initializes various attributes and data structures.
        
        :param gra: The parameter `gra` is a graph object. It is used to represent a graph and store
        information about the graph's nodes, edges, and weights. The `gra` object is used in the
        initialization of the class and is stored as an instance variable (`self.gra`) for later use in
        """
        self.gra = gra

    def find_cycle(self, point_to):
        """
        The `find_cycle` function finds a cycle on a policy graph.
        
        :param point_to: The `point_to` parameter is a dictionary that represents the edges of a directed
        graph. Each key-value pair in the dictionary represents an edge from the key vertex to the value
        vertex
        """
        visited = {}
        for vtx_v in filter(lambda vtx_v: vtx_v not in visited, self.gra):
            vtx_u = vtx_v
            while True:
                visited[vtx_u] = vtx_v
                if vtx_u not in point_to:
                    break
                vtx_u = point_to[vtx_u]
                if vtx_u in visited:
                    if visited[vtx_u] == vtx_v:
                        yield vtx_u
                    break

    def relax_pred(self, dist, get_weight, update_ok) -> bool:
        """
        The `relax_pred` function updates the `dist` and `pred` arrays based on the weights of edges in a
        graph.
        
        :param dist: The `dist` parameter is a data structure that represents the distances from a source
        vertex to all other vertices in a graph. It is typically implemented as an array or a dictionary,
        where the keys are the vertices and the values are the corresponding distances
        :param get_weight: The `get_weight` parameter is a function that takes an edge as input and returns
        the weight of that edge
        :param update_ok: The `update_ok` parameter is a function that determines whether an update to the
        distance `dist[vtx_v]` is allowed. It takes two arguments: the current value of `dist[vtx_v]` and
        the new value `d`. It should return `True` if the update is
        :return: a boolean value.
        """
        changed = False
        for e in self.gra.edges():
            vtx_u, vtx_v = e
            weight = get_weight(e)
            d = dist[vtx_u] + weight
            if dist[vtx_v] > d and update_ok(dist[vtx_v], d):
                dist[vtx_v] = d
                self.pred[vtx_v] = vtx_u
                changed = True
        return changed

    def relax_succ(self, dist, get_weight, update_ok) -> bool:
        """
        The `relax_succ` function performs an update of the `dist` and `succ` variables.
        
        :param dist: The `dist` parameter is a variable that represents the distance between nodes in a
        graph. It is typically a dictionary where the keys are nodes and the values are the distances from a
        source node to each node in the graph
        :param get_weight: A function that takes in two nodes and returns the weight of the edge between
        them
        :param update_ok: A boolean value indicating whether the update operation is allowed or not
        """
        changed = False
        for e in self.gra.edges():
            vtx_u, vtx_v = e
            weight = get_weight(e)
            d = dist[vtx_v] - weight
            if dist[vtx_u] < d and update_ok(dist[vtx_u], d):
                dist[vtx_u] = d
                self.succ[vtx_u] = vtx_v
                changed = True
        return changed

    def find_neg_cycle_pred(self, dist, get_weight, update_ok) -> Generator:
        """
        The function `find_neg_cycle_pred` performs an updating of `dist` and `pred` and yields a list of
        edges representing a negative cycle.
        
        :param dist: The `dist` parameter is either a list or a dictionary. It represents the distances from
        a source vertex to all other vertices in the graph. If it is a list, the indices of the list
        correspond to the vertices, and the values represent the distances. If it is a dictionary, the keys
        :param get_weight: The `get_weight` parameter is a callable function that takes in an edge and
        returns its weight
        :param update_ok: The `update_ok` parameter is a callable function that determines whether an update
        to the distance value of a vertex is allowed. It takes in three arguments: the current distance
        value of the vertex, the weight of the edge being considered for update, and the current distance
        value of the vertex at the other
        """
        self.pred = {}
        found = False
        while not found and self.relax_pred(dist, get_weight, update_ok):
            for vtx_v in self.find_cycle(self.pred):
                found = True
                yield self.cycle_list(vtx_v, self.pred)

    def find_neg_cycle_succ(self, dist, get_weight, update_ok) -> Generator:
        """
        The function `find_neg_cycle_succ` performs an updating of `dist` and `succ` and yields a list of
        edges representing a negative cycle.
        
        :param dist: The `dist` parameter is either a list or a dictionary. It represents the distances from
        a source vertex to all other vertices in the graph. If it is a list, the indices of the list
        correspond to the vertices in the graph. If it is a dictionary, the keys represent the vertices and
        :param get_weight: get_weight is a callable function that takes in an edge and returns the weight of
        that edge
        :param update_ok: The `update_ok` parameter is a callable function that determines whether an update
        to the distance value of a vertex is allowed. It takes in three arguments: the current distance
        value of the vertex, the weight of the edge being considered for update, and the current distance
        value of the vertex at the other
        """
        self.succ = {}
        found = False
        while not found and self.relax_succ(dist, get_weight, update_ok):
            for vtx_v in self.find_cycle(self.succ):
                found = True
                yield self.cycle_list(vtx_v, self.succ)

    def cycle_list(self, handle, point_to) -> list:
        """
        The `cycle_list` function takes a starting node and a dictionary mapping nodes to their next node,
        and returns a list of edges representing a cycle in the graph.
        
        :param handle: The `handle` parameter represents the starting node of the cycle in the graph. It is
        the node from which the cycle traversal begins
        :param point_to: point_to is a dictionary that maps each graph node to the node it points to
        :return: a list of edges, which represents a cycle in a graph.
        """
        vtx_v = handle
        cycle = list()
        while True:
            vtx_u = point_to[vtx_v]
            cycle += [(vtx_u, vtx_v)]
            vtx_v = vtx_u
            if vtx_v == handle:
                break
        return cycle

    def is_negative(self, handle, dist, get_weight) -> bool:
        """
        The `is_negative` function checks if a cycle in a graph is negative by iterating through the cycle
        and comparing the distances between nodes.
        
        :param handle: The `handle` parameter is a graph node that represents the starting point of the
        cycle list
        :param dist: The `dist` parameter is a list that represents the distance from the starting node to
        each node in the graph. Each element in the list corresponds to a node in the graph, and the value
        represents the distance from the starting node to that node
        :param get_weight: The `get_weight` parameter is a callable function that takes in a tuple `(vtx_u,
        vtx_v)` as input and returns the weight of the edge between vertices `vtx_u` and `vtx_v`
        :return: a boolean value.
        """
        vtx_v = handle
        while True:
            vtx_u = self.pred[vtx_v]
            wt = get_weight((vtx_u, vtx_v))
            if dist[vtx_v] > dist[vtx_u] + wt:
                return True
            vtx_v = vtx_u
            if vtx_v == handle:
                break
        return False
