"""Min-cost flow via cycle-cancellation descent.

Uses Bellman-Ford to find negative-cost cycles in the residual graph
(replacing Howard's algorithm which had detection gaps on certain
graph structures).  Optional vertex-disjoint constraint via
:class:`VertexDisjointConstraint`.
"""

from collections import deque
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from ._cycle_base import cycle_list
from ._types import Node, PointTo

EdgeData = Dict[str, Any]
EdgeList = List[EdgeData]
Graph = Dict[Node, Dict[Node, EdgeData]]
FlowMap = Dict[Node, Dict[Node, int]]


def _augment_dict(flow: FlowMap, edges: EdgeList, delta: int) -> None:
    for e in edges:
        u, v = e["orig"]
        signed = delta if e["forward"] else -delta
        flow.setdefault(u, {})[v] = flow.get(u, {}).get(v, 0) + signed


class Flow:
    """Integer flow values on the edges of a fixed graph."""

    def __init__(self, g: Graph, initial: Optional[FlowMap] = None) -> None:
        self._map: FlowMap = (
            {u: {v: 0 for v in g[u]} for u in g} if initial is None else initial
        )

    def get(self, u: Node, v: Node) -> int:
        return self._map.get(u, {}).get(v, 0)

    def set(self, u: Node, v: Node, value: int) -> None:
        self._map.setdefault(u, {})[v] = value

    def row(self, u: Node) -> Dict[Node, int]:
        return self._map.setdefault(u, {})

    def augment(self, edges: EdgeList, delta: int) -> None:
        """Push ``delta`` units around a residual cycle."""
        _augment_dict(self._map, edges, delta)

    @property
    def values(self) -> FlowMap:
        return self._map


class VertexDisjointConstraint:
    """At most one outgoing flow edge for every non-sink node.

    A node is 'used' when it has outgoing flow.  The used set persists across
    the entire cycle-cancellation loop.
    """

    def __init__(self, sink: Node) -> None:
        self.sink = sink
        self.used: Set[Node] = set()

    def cycle_uses_used_node(self, edges: EdgeList) -> bool:
        """Reject if a used node gains outflow without offsetting reduction."""
        forward: Set[Node] = set()
        backward: Set[Node] = set()
        for e in edges:
            u, _ = e["orig"]
            if u == self.sink:
                continue
            (forward if e["forward"] else backward).add(u)
        return any(u in self.used for u in forward - backward)

    def accepts(self, edges: EdgeList) -> bool:
        return not self.cycle_uses_used_node(edges)

    def accept_cycle(self, edges: EdgeList, flow: FlowMap, delta: int) -> None:
        _augment_dict(flow, edges, delta)
        self._mark_used(edges)
        self._release_exhausted(edges, flow)

    def on_augment(self, edges: EdgeList, flow: Flow, delta: int) -> None:
        """Update the used set after ``flow`` has been augmented."""
        self._mark_used(edges)
        self._release_exhausted(edges, flow.values)

    def _mark_used(self, edges: EdgeList) -> None:
        for e in edges:
            u, _ = e["orig"]
            if e["forward"] and u != self.sink:
                self.used.add(u)

    def _release_exhausted(self, edges: EdgeList, flow: FlowMap) -> None:
        for e in edges:
            u, _ = e["orig"]
            if not e["forward"] and u in self.used:
                if all(f <= 0 for f in flow.get(u, {}).values()):
                    self.used.discard(u)


VertexFilter = VertexDisjointConstraint


def _residual_edge(
    g: Graph, u: Node, v: Node, flow: FlowMap
) -> Tuple[Optional[EdgeData], Optional[EdgeData]]:
    cap = g[u][v].get("capacity", float("inf"))
    wgt = g[u][v].get("weight", 0)
    f = flow.get(u, {}).get(v, 0)
    fwd = None
    bwd = None
    if f < cap:
        fwd = {
            "cost": wgt,
            "capacity": cap - f,
            "orig": (u, v),
            "forward": True,
        }
    if f > 0:
        bwd = {
            "cost": -wgt,
            "capacity": f,
            "orig": (u, v),
            "forward": False,
        }
    return fwd, bwd


def _build_residual(g: Graph, flow: FlowMap) -> Dict[Node, Dict[Node, EdgeData]]:
    """Build residual graph from current flow.

    Each edge is a dict with ``cost`` (for the Bellman-Ford pass), ``capacity``
    (for bottleneck), and ``orig`` / ``forward`` (for flow updates).
    """
    residual: Dict[Node, Dict[Node, EdgeData]] = {}
    for u, neighbors in g.items():
        residual.setdefault(u, {})
        for v in neighbors:
            fwd, bwd = _residual_edge(g, u, v, flow)
            if fwd is not None:
                prev = residual[u].get(v)
                if prev is None or fwd["cost"] < prev["cost"]:
                    residual[u][v] = fwd
            if bwd is not None:
                prev = residual.setdefault(v, {}).get(u)
                if prev is None or bwd["cost"] < prev["cost"]:
                    residual[v][u] = bwd
    return residual


def _update_residual_edge(
    residual: Dict[Node, Dict[Node, EdgeData]],
    g: Graph,
    flow: FlowMap,
    u: Node,
    v: Node,
) -> None:
    if u in residual and v in residual[u]:
        del residual[u][v]
        if not residual[u]:
            del residual[u]
    if v in residual and u in residual[v]:
        del residual[v][u]
        if not residual[v]:
            del residual[v]
    fwd, bwd = _residual_edge(g, u, v, flow)
    if fwd is not None:
        residual.setdefault(u, {})[v] = fwd
    if bwd is not None:
        residual.setdefault(v, {})[u] = bwd


class ResidualNetwork:
    """Residual graph built from a flow, kept in sync as the flow changes."""

    def __init__(self, g: Graph, flow: Flow) -> None:
        self._g = g
        self._flow = flow
        self.residual: Dict[Node, Dict[Node, EdgeData]] = _build_residual(
            g, flow.values
        )

    def __bool__(self) -> bool:
        return bool(self.residual)

    def nodes(self) -> Set[Node]:
        found = set(self.residual)
        for neighbors in self.residual.values():
            found.update(neighbors)
        return found

    def augment(self, edges: EdgeList, delta: int) -> None:
        self._flow.augment(edges, delta)
        seen: Set[Tuple[Node, Node]] = set()
        for e in edges:
            u, v = e["orig"]
            if (u, v) not in seen:
                seen.add((u, v))
                _update_residual_edge(self.residual, self._g, self._flow.values, u, v)


def _find_all_neg_cycles_bf(
    residual: Dict[Node, Dict[Node, EdgeData]],
    all_nodes: Set[Node],
) -> Iterator[EdgeList]:
    """Find all negative-cost cycles in a single Bellman-Ford pass.

    Runs |V| passes; in the V-th pass, every node whose distance still
    improves is part of a negative cycle.  Yields each cycle as a list of
    residual edge dicts.
    """
    n = len(all_nodes)
    dist: Dict[Node, float] = {node: 0 for node in all_nodes}
    pred: PointTo = {}
    updated_in_last: Set[Node] = set()

    for i in range(n):
        changed = False
        for u, neighbors in residual.items():
            du = dist.get(u, 0)
            for v, edge in neighbors.items():
                nd = du + edge["cost"]
                if nd < dist.get(v, 0):
                    dist[v] = nd
                    pred[v] = (u, edge)
                    changed = True
                    if i == n - 1:
                        updated_in_last.add(v)
        if not changed and i < n - 1:
            return

    if not updated_in_last:
        return

    yielded_nodes: Set[Node] = set()
    for start_node in sorted(updated_in_last):
        if start_node in yielded_nodes:
            continue
        visited: Set[Node] = set()
        u = start_node
        while u not in visited:
            visited.add(u)
            u = pred[u][0]
        cycle_start = u
        cycle = list(reversed(cycle_list(pred, cycle_start)))
        yielded_nodes.update(e["orig"][0] for e in cycle)
        yield cycle


def _bfs_path(
    g: Graph,
    flow: FlowMap,
    src: Node,
    demand_nodes: List[Node],
    remaining: Dict[Node, int],
) -> Optional[List[Node]]:
    """BFS to find a path from src to a node with remaining demand."""
    visited = {src}
    parent: Dict[Node, Node] = {}
    queue = deque([src])

    while queue:
        u = queue.popleft()
        if u in demand_nodes and remaining.get(u, 0) > 0:
            path = [u]
            while u != src:
                u = parent[u]
                path.append(u)
            path.reverse()
            return path

        for v, data in g.get(u, {}).items():
            if v in visited:
                continue
            cap = data.get("capacity", float("inf"))
            if flow[u].get(v, 0) < cap:
                visited.add(v)
                parent[v] = u
                queue.append(v)

    return None


def _find_feasible_flow(g: Graph, demands: Dict[Node, int]) -> Optional[Flow]:
    """Find initial feasible flow via greedy BFS routing.

    Routes flow from supply nodes (demand < 0) to demand nodes (demand > 0)
    along capacity-respecting paths.  Returns None if infeasible.
    """
    flow: FlowMap = {u: {v: 0 for v in g[u]} for u in g}
    remaining = dict(demands)
    supply_nodes = [n for n, d in remaining.items() if d < 0]
    demand_nodes = [n for n, d in remaining.items() if d > 0]

    for src in supply_nodes:
        supply_amount = -remaining[src]
        while supply_amount > 0:
            path = _bfs_path(g, flow, src, demand_nodes, remaining)
            if path is None:
                return None

            dst = path[-1]
            bottleneck = float("inf")
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                cap = g[u][v].get("capacity", float("inf"))
                bottleneck = min(bottleneck, cap - flow[u].get(v, 0))
            bottleneck = min(bottleneck, remaining[dst], supply_amount)
            bottleneck = int(bottleneck)
            if bottleneck <= 0:
                return None

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                flow[u][v] = flow[u].get(v, 0) + bottleneck

            remaining[src] += bottleneck
            remaining[dst] -= bottleneck
            supply_amount -= bottleneck

    return Flow(g, flow)


def _total_cost(g: Graph, flow: Flow) -> float:
    return sum(flow.get(u, v) * data["weight"] for u in g for v, data in g[u].items())


def cycle_canceling_mcf(
    g: Graph,
    demands: Dict[Node, int],
    sink: Optional[Node] = None,
) -> Optional[Tuple[float, FlowMap]]:
    """Solve min-cost flow using cycle-cancellation descent.

    Uses Bellman-Ford for negative-cycle detection (no Howard gap).
    Optional vertex-disjoint constraint via :class:`VertexDisjointConstraint`.

    Args:
        g: ``{u: {v: {'weight': cost, 'capacity': cap}}}``
        demands: ``{node: demand}`` (negative = supply, positive = demand)
        sink: Optional sink node. When provided, enables the vertex-disjoint
            constraint: each non-sink node may have at most one outgoing
            flow edge.  When None (default), no constraint is enforced.

    Returns:
        ``(total_cost, flow_dict)`` or ``None`` if infeasible.
    """
    flow = _find_feasible_flow(g, demands)
    if flow is None:
        return None

    constraint = VertexDisjointConstraint(sink) if sink is not None else None
    if constraint is not None:
        for u, row in flow.values.items():
            if u == sink:
                continue
            if any(f > 0 for f in row.values()):
                constraint.used.add(u)

    network = ResidualNetwork(g, flow)
    if not network:
        return _total_cost(g, flow), flow.values

    all_nodes = network.nodes()

    while True:
        cancelled = False
        for cycle_edges in _find_all_neg_cycles_bf(network.residual, all_nodes):
            if constraint is not None and not constraint.accepts(cycle_edges):
                continue

            bottleneck = int(min(e["capacity"] for e in cycle_edges))
            if bottleneck <= 0:
                continue

            network.augment(cycle_edges, bottleneck)
            if constraint is not None:
                constraint.on_augment(cycle_edges, flow, bottleneck)

            cancelled = True
            break

        if not cancelled:
            break

    return _total_cost(g, flow), flow.values
