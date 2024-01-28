from abc import abstractmethod
from fractions import Fraction
from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Tuple,
    TypeVar,
)

import networkx as nx

Node = TypeVar("Node")  # Hashable
Edge = TypeVar("Edge")  # Hashable
Domain = TypeVar("Domain", int, Fraction, float)  # Comparable Ring
Cycle = List[Edge]  # List of Edges


class DiGraphAdapter(nx.DiGraph):
    def items(self):
        return self.adjacency()


class NegCycleFinder(Generic[Node, Edge, Domain]):
    pred: Dict[Node, Tuple[Node, Edge]] = {}

    def __init__(self, digraph: DiGraphAdapter) -> None:
        self.digraph = digraph

    def find_cycle(self) -> Generator[Node, None, None]:
        visited: Dict[Node, Node] = {}
        for vtx in filter(lambda vtx: vtx not in visited, self.digraph):
            utx = vtx
            while True:
                visited[utx] = vtx
                if utx not in self.pred:
                    break
                utx, _ = self.pred[utx]
                if utx in visited:
                    if visited[utx] == vtx:
                        yield utx
                    break

    def relax(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
    ) -> bool:
        changed = False
        for utx, neighbors in self.digraph.items():
            for vtx, edge in neighbors.items():
                distance = dist[utx] + get_weight(edge)
                if dist[vtx] > distance:
                    dist[vtx] = distance
                    self.pred[vtx] = (utx, edge)
                    changed = True
        return changed

    def howard(
        self,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
    ) -> Generator[Cycle, None, None]:
        self.pred = {}
        while self.relax(dist, get_weight):
            for vtx in self.find_cycle():
                # Will zero cycle be found???
                assert self.is_negative(vtx, dist, get_weight)
                yield self.cycle_list(vtx)
            else:
                break

    def cycle_list(self, handle: Node) -> Cycle:
        vtx = handle
        cycle = list()
        while True:
            utx, edge = self.pred[vtx]
            cycle.append(edge)
            vtx = utx
            if vtx == handle:
                break
        return cycle

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Edge], Domain],
    ) -> bool:
        vtx = handle
        # do while loop in C++
        while True:
            utx, edge = self.pred[vtx]
            if dist[vtx] > dist[utx] + get_weight(edge):
                return True
            vtx = utx
            if vtx == handle:
                break
        return False


Ratio = TypeVar("Ratio", Fraction, float)  # Comparable field


class ParametricAPI(Generic[Node, Edge, Ratio]):
    @abstractmethod
    def distance(self, ratio: Ratio, edge: Edge) -> Ratio:
        pass

    @abstractmethod
    def zero_cancel(self, cycle: Cycle) -> Ratio:
        pass


class MaxParametricSolver(Generic[Node, Edge, Ratio]):
    def __init__(
        self,
        digraph: DiGraphAdapter,
        omega: ParametricAPI[Node, Edge, Ratio],
    ) -> None:
        self.ncf = NegCycleFinder(digraph)
        self.omega: ParametricAPI[Node, Edge, Ratio] = omega

    def run(
        self, dist: MutableMapping[Node, Domain], ratio: Ratio
    ) -> Tuple[Ratio, Cycle]:
        D = type(next(iter(dist.values())))

        def get_weight(e: Edge) -> Domain:
            return D(self.omega.distance(ratio, e))

        r_min = ratio
        c_min = []
        cycle = []

        while True:
            for ci in self.ncf.howard(dist, get_weight):
                ri = self.omega.zero_cancel(ci)
                if r_min > ri:
                    r_min = ri
                    c_min = ci
            if r_min >= ratio:
                break

            cycle = c_min
            ratio = r_min
        return ratio, cycle


def set_default(digraph: DiGraphAdapter, weight: str, value: Domain) -> None:
    for _, neighbors in digraph.items():
        for _, e in neighbors.items():
            if e.get(weight, None) is None:
                e[weight] = value


class CycleRatioAPI(ParametricAPI[Node, MutableMapping[str, Domain], Ratio]):
    def __init__(
        self, digraph: Mapping[Node, Mapping[Node, Mapping[str, Domain]]], K: type
    ) -> None:
        self.digraph: Mapping[Node, Mapping[Node, Mapping[str, Domain]]] = digraph
        self.K = K

    def distance(self, ratio: Ratio, edge: MutableMapping[str, Domain]) -> Ratio:
        return self.K(edge["cost"]) - ratio * edge["time"]

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return self.K(total_cost) / total_time


class MinCycleRatioSolver(Generic[Node, Edge, Ratio]):
    def __init__(self, digraph: DiGraphAdapter) -> None:
        self.digraph: DiGraphAdapter = digraph

    def run(self, dist: MutableMapping[Node, Domain], r0: Ratio) -> Tuple[Ratio, Cycle]:
        omega = CycleRatioAPI(self.digraph, type(r0))
        solver = MaxParametricSolver(self.digraph, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle


def create_test_case1():
    digraph = nx.cycle_graph(5, create_using=DiGraphAdapter())
    digraph[1][2]["weight"] = -5
    digraph.add_edges_from([(5, n) for n in digraph])
    return digraph


def create_test_case_timing():
    digraph = DiGraphAdapter()
    nodelist = ["a1", "a2", "a3"]
    digraph.add_nodes_from(nodelist)
    digraph.add_edges_from(
        [
            ("a1", "a2", {"weight": 7}),
            ("a2", "a1", {"weight": 0}),
            ("a2", "a3", {"weight": 3}),
            ("a3", "a2", {"weight": 1}),
            ("a3", "a1", {"weight": 2}),
            ("a1", "a3", {"weight": 5}),
        ]
    )
    return digraph


def test_cycle_ratio():
    digraph = create_test_case1()
    set_default(digraph, "time", 1)
    set_default(digraph, "cost", 1)
    digraph[1][2]["cost"] = 5
    # dist = list(0 for _ in digraph)
    dist = {vtx: 0 for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing():
    digraph = create_test_case_timing()
    set_default(digraph, "time", 1)
    digraph["a1"]["a2"]["cost"] = 7
    digraph["a2"]["a1"]["cost"] = -1
    digraph["a2"]["a3"]["cost"] = 3
    digraph["a3"]["a2"]["cost"] = 0
    digraph["a3"]["a1"]["cost"] = 2
    digraph["a1"]["a3"]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = {vtx: Fraction(0, 1) for vtx in digraph}
    solver = MinCycleRatioSolver(digraph)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)


def do_case(digraph, dist):
    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(digraph)
    has_neg = False
    for _ in ncf.howard(dist, get_weight):
        has_neg = True
        break
    return has_neg


def test_neg_cycle():
    digraph = create_test_case1()
    dist = list(0 for _ in digraph)
    has_neg = do_case(digraph, dist)
    assert has_neg


def test_timing_graph():
    digraph = create_test_case_timing()
    dist = {vtx: 0 for vtx in digraph}
    has_neg = do_case(digraph, dist)
    assert not has_neg
