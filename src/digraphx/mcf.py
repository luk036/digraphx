"""Min-cost flow via cycle-cancellation descent.

Uses Bellman-Ford to find negative-cost cycles in the residual graph
(replacing Howard's algorithm which had detection gaps on certain
graph structures).  Optional vertex-disjoint constraint via VertexFilter.
"""

from collections import deque
from typing import Hashable, Set, TypeVar

Node = TypeVar("Node", bound=Hashable)


class VertexFilter:
    """Tracks used nodes for vertex-disjoint constraint enforcement.

    A node is 'used' when it has outgoing flow.  The used set persists
    across the entire cycle-cancellation loop.
    """

    def __init__(self, sink: Hashable):
        self.sink = sink
        self.used: Set[Hashable] = set()

    def cycle_uses_used_node(self, cycle_edges) -> bool:
        """Reject if a used node gains outflow without offsetting reduction."""
        fwd_nodes = set()
        bwd_nodes = set()
        for e in cycle_edges:
            u_orig, _ = e["orig"]
            if u_orig == self.sink:
                continue
            if e["forward"]:
                fwd_nodes.add(u_orig)
            else:
                bwd_nodes.add(u_orig)
        for u in fwd_nodes - bwd_nodes:
            if u in self.used:
                return True
        return False

    def accept_cycle(self, cycle_edges, flow, bottleneck):
        """Apply cycle cancellation and update used set."""
        for e in cycle_edges:
            u_orig, v_orig = e["orig"]
            if e["forward"]:
                flow[u_orig][v_orig] = flow[u_orig].get(v_orig, 0) + bottleneck
                if u_orig != self.sink:
                    self.used.add(u_orig)
            else:
                old = flow[u_orig].get(v_orig, 0)
                flow[u_orig][v_orig] = old - bottleneck
        for e in cycle_edges:
            u_orig, _ = e["orig"]
            if not e["forward"] and u_orig in self.used:
                if all(f <= 0 for f in flow[u_orig].values()):
                    self.used.discard(u_orig)


def _build_residual(g, flow):
    """Build residual graph from current flow.

    Each edge is a dict with ``cost`` (for NegCycleFinder), ``capacity``
    (for bottleneck), and ``orig`` / ``forward`` (for flow updates).
    """
    residual: dict = {}
    for u, neighbors in g.items():
        if u not in residual:
            residual[u] = {}
        for v, data in neighbors.items():
            cap = data.get("capacity", float("inf"))
            wgt = data.get("weight", 0)
            f = flow.get(u, {}).get(v, 0)

            if f < cap:
                edge = {
                    "cost": wgt,
                    "capacity": cap - f,
                    "orig": (u, v),
                    "forward": True,
                }
                # Keep the more negative cost when edges collide at same (u,v)
                prev = residual[u].get(v)
                if prev is None or edge["cost"] < prev["cost"]:
                    residual[u][v] = edge

            if f > 0:
                edge = {
                    "cost": -wgt,
                    "capacity": f,
                    "orig": (u, v),
                    "forward": False,
                }
                prev = residual.setdefault(v, {}).get(u)
                if prev is None or edge["cost"] < prev["cost"]:
                    residual[v][u] = edge

    return residual


def _find_all_neg_cycles_bf(residual, all_nodes):
    """Find all negative-cost cycles in a single Bellman-Ford pass.

    Runs |V| passes; in the V-th pass, every node whose distance still
    improves is part of a negative cycle.  Yields each cycle as a list
    of residual edge dicts.
    """
    n = len(all_nodes)
    dist = {node: 0 for node in all_nodes}
    pred = {}  # node → (prev_node, residual_edge)
    updated_in_last = set()

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
            return  # converged before V passes

    if not updated_in_last:
        return

    yielded_nodes = set()
    for start_node in sorted(updated_in_last):
        if start_node in yielded_nodes:
            continue
        # Trace back to find cycle start
        visited = set()
        u = start_node
        while u not in visited:
            visited.add(u)
            u = pred[u][0]
        cycle_start = u
        # Reconstruct cycle
        cycle = []
        u = cycle_start
        while True:
            prev_node, edge = pred[u]
            cycle.append(edge)
            u = prev_node
            if u == cycle_start:
                break
        cycle.reverse()
        yielded_nodes.update(e["orig"][0] for e in cycle)
        yield cycle


def _bfs_path(g, flow, src, demand_nodes, remaining):
    """BFS to find a path from src to a node with remaining demand."""
    visited = {src}
    parent: dict = {}
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
            existing = flow.get(u, {}).get(v, 0)
            if existing < cap:
                visited.add(v)
                parent[v] = u
                queue.append(v)

    return None


def _find_feasible_flow(g, demands):
    """Find initial feasible flow via greedy BFS routing.

    Routes flow from supply nodes (demand < 0) to demand nodes (demand > 0)
    along capacity-respecting paths.  Returns None if infeasible.
    """
    nodes = list(g.keys())
    flow = {u: {} for u in nodes}
    for u in g:
        for v in g[u]:
            flow[u][v] = 0

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
                existing = flow[u].get(v, 0)
                bottleneck = min(bottleneck, cap - existing)
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

    return flow


def cycle_canceling_mcf(g, demands, sink=None):
    """Solve min-cost flow using cycle-cancellation descent.

    Uses Bellman-Ford for negative-cycle detection (no Howard gap).
    Optional vertex-disjoint constraint via VertexFilter.

    Args:
        g: {u: {v: {'weight': cost, 'capacity': cap}}}
        demands: {node: demand} (negative = supply, positive = demand)
        sink: Optional sink node. When provided, enables the vertex-disjoint
            constraint: each non-sink node may have at most one outgoing
            flow edge.  When None (default), no constraint is enforced.

    Returns:
        (total_cost, flow_dict) or None if infeasible.
    """
    # Stage 1: find feasible initial flow
    flow = _find_feasible_flow(g, demands)
    if flow is None:
        return None

    # Stage 2: cancel negative-cost residual cycles (Bellman-Ford)
    use_constraint = sink is not None
    vf = VertexFilter(sink) if use_constraint else None
    if vf is not None:
        for u in flow:
            for v, f in flow[u].items():
                if f > 0 and u != sink:
                    vf.used.add(u)
                    break  # one outgoing edge is enough to mark as used
    if vf is not None:
        print(f"Used init: {len(vf.used)}")

    while True:
        residual = _build_residual(g, flow)
        if not residual:
            break

        all_nodes = set(residual)
        for neighbors in residual.values():
            all_nodes.update(neighbors)

        cancelled = False
        for cycle_edges in _find_all_neg_cycles_bf(residual, all_nodes):
            # When constraint is active, reject cycles that use already-used nodes
            if use_constraint and vf.cycle_uses_used_node(cycle_edges):
                continue

            bottleneck = float("inf")
            for edge in cycle_edges:
                bottleneck = min(bottleneck, edge["capacity"])
            bottleneck = int(bottleneck)
            if bottleneck <= 0:
                continue

            if use_constraint:
                vf.accept_cycle(cycle_edges, flow, bottleneck)
            else:
                for edge in cycle_edges:
                    u_orig, v_orig = edge["orig"]
                    if edge["forward"]:
                        flow[u_orig][v_orig] = flow[u_orig].get(v_orig, 0) + bottleneck
                    else:
                        flow[u_orig][v_orig] = flow[u_orig].get(v_orig, 0) - bottleneck

            cancelled = True
            break

        if not cancelled:
            break

    total_cost = sum(
        flow[u].get(v, 0) * data["weight"] for u in g for v, data in g[u].items()
    )
    return total_cost, flow
