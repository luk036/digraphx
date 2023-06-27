import networkx as nx
from .lict import Lict


# NUM_NODES = 1000
class DiGraphAdapter(nx.DiGraph):
    def items(self):
        return self.adjacency()


class TinyDiGraph(DiGraphAdapter):
    num_nodes = 0

    def cheat_node_dict(self):
        return Lict([dict() for _ in range(self.num_nodes)])

    def cheat_adjlist_outer_dict(self):
        return Lict([dict() for _ in range(self.num_nodes)])

    node_dict_factory = cheat_node_dict
    adjlist_outer_dict_factory = cheat_adjlist_outer_dict

    def init_nodes(self, n: int):
        self.num_nodes = n
        self._node = self.cheat_node_dict()
        self._adj = self.cheat_adjlist_outer_dict()
        self._pred = self.cheat_adjlist_outer_dict()


if __name__ == "__main__":
    gr = TinyDiGraph()
    gr.init_nodes(1000)
    gr.add_edge(2, 1)
    print(gr.number_of_nodes())
    print(gr.number_of_edges())

    for utx in gr:
        for vtx in gr.neighbors(utx):
            print(f"{utx}, {vtx}")

    a = Lict([0] * 8)
    for i in a:
        a[i] = i * i
    for i, vtx in a.items():
        print(f"{i}: {vtx}")
    print(3 in a)
