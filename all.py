from typing import Dict, Callable, Generator, Tuple, List
from typing import MutableMapping, Mapping, TypeVar, Generic
from fractions import Fraction
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

    def __init__(self, gra: DiGraphAdapter) -> None:
        self.digraph = gra

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
        for utx, nbrs in self.digraph.items():
            for vtx, edge in nbrs.items():
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
                break; 

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
        gra: DiGraphAdapter,
        omega: ParametricAPI[Node, Edge, Ratio],
    ) -> None:
        self.ncf = NegCycleFinder(gra)
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


def set_default(gra: DiGraphAdapter, weight: str, value: Domain) -> None:
    for _, nbrs in gra.items():
        for _, e in nbrs.items():
            if e.get(weight, None) is None:
                e[weight] = value


class CycleRatioAPI(ParametricAPI[Node, MutableMapping[str, Domain], Ratio]):
    def __init__(
        self, gra: Mapping[Node, Mapping[Node, Mapping[str, Domain]]], K: type
    ) -> None:
        self.gra: Mapping[Node, Mapping[Node, Mapping[str, Domain]]] = gra
        self.K = K

    def distance(self, ratio: Ratio, edge: MutableMapping[str, Domain]) -> Ratio:
        return self.K(edge["cost"]) - ratio * edge["time"]

    def zero_cancel(self, cycle: Cycle) -> Ratio:
        total_cost = sum(edge["cost"] for edge in cycle)
        total_time = sum(edge["time"] for edge in cycle)
        return self.K(total_cost) / total_time


class MinCycleRatioSolver(Generic[Node, Edge, Ratio]):
    def __init__(self, gra: DiGraphAdapter) -> None:
        self.gra: DiGraphAdapter = gra

    def run(self, dist: MutableMapping[Node, Domain], r0: Ratio) -> Tuple[Ratio, Cycle]:
        omega = CycleRatioAPI(self.gra, type(r0))
        solver = MaxParametricSolver(self.gra, omega)
        ratio, cycle = solver.run(dist, r0)
        return ratio, cycle


def create_test_case1():
    gra = nx.cycle_graph(5, create_using=DiGraphAdapter())
    gra[1][2]["weight"] = -5
    gra.add_edges_from([(5, n) for n in gra])
    return gra


def create_test_case_timing():
    gra = DiGraphAdapter()
    nodelist = ["a1", "a2", "a3"]
    gra.add_nodes_from(nodelist)
    gra.add_edges_from(
        [
            ("a1", "a2", {"weight": 7}),
            ("a2", "a1", {"weight": 0}),
            ("a2", "a3", {"weight": 3}),
            ("a3", "a2", {"weight": 1}),
            ("a3", "a1", {"weight": 2}),
            ("a1", "a3", {"weight": 5}),
        ]
    )
    return gra


def test_cycle_ratio():
    gra = create_test_case1()
    set_default(gra, "time", 1)
    set_default(gra, "cost", 1)
    gra[1][2]["cost"] = 5
    # dist = list(0 for _ in gra)
    dist = {vtx: 0 for vtx in gra}
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(9, 5)


def test_cycle_ratio_timing():
    gra = create_test_case_timing()
    set_default(gra, "time", 1)
    gra["a1"]["a2"]["cost"] = 7
    gra["a2"]["a1"]["cost"] = -1
    gra["a2"]["a3"]["cost"] = 3
    gra["a3"]["a2"]["cost"] = 0
    gra["a3"]["a1"]["cost"] = 2
    gra["a1"]["a3"]["cost"] = 4
    # make sure no parallel edges in above!!!
    dist = {vtx: Fraction(0, 1) for vtx in gra}
    solver = MinCycleRatioSolver(gra)
    ratio, cycle = solver.run(dist, Fraction(10000, 1))
    print(ratio)
    print(cycle)
    assert cycle
    assert ratio == Fraction(1, 1)


def do_case(gra, dist):
    def get_weight(edge):
        return edge.get("weight", 1)

    ncf = NegCycleFinder(gra)
    hasNeg = False
    for _ in ncf.howard(dist, get_weight):
        hasNeg = True
        break
    return hasNeg


def test_neg_cycle():
    gra = create_test_case1()
    dist = list(0 for _ in gra)
    hasNeg = do_case(gra, dist)
    assert hasNeg


def test_timing_graph():
    gra = create_test_case_timing()
    dist = {vtx: 0 for vtx in gra}
    has_neg = do_case(gra, dist)
    assert not has_neg

