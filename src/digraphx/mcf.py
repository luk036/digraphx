"""Min-cost flow via cycle-cancellation descent.

Uses Howard's negative cycle finding (NegCycleFinderQ) with a vertex-filter
callback to enforce the constraint that each non-sink node may have at most
one outgoing flow edge.
"""

from collections import deque
from typing import Dict, Hashable, List, Optional, Set, Tuple, TypeVar

from .neg_cycle_q import NegCycleFinderQ

Node = TypeVar("Node", bound=Hashable)


class TrackedDist(dict):
    """Dict that remembers the last key accessed via __getitem__."""

    __slots__ = ("last_key",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_key: Optional[Hashable] = None

    def __getitem__(self, key):
        self.last_key = key
        return super().__getitem__(key)


class VertexFilter:
    """Functor for update_ok that rejects distance updates to 'used' nodes.

    A node is 'used' when it already has outgoing flow in the current
    solution (at most one outgoing edge per non-sink node).
    """

    def __init__(self, tracked_dist: TrackedDist, sink: Hashable):
        self.dist = tracked_dist
        self.sink = sink
        self.used: Set[Hashable] = set()

    def _rebuild_used(self, flow):
        """Rebuild used set from current flow state."""
        self.used.clear()
        for u, neighbors in flow.items():
            if u == self.sink:
                continue
            for v, f in neighbors.items():
                if f > 0:
                    self.used.add(u)
                    break  # at most one outgoing edge, but break on first

    def __call__(self, old_dist, new_dist) -> bool:
        """Always allow relaxation.  Constraint-checking happens at cycle level."""
        return True

    def cycle_uses_used_node(self, cycle_edges) -> bool:
        """Check whether any forward edge source in the cycle is already used."""
        for e in cycle_edges:
            if not e["forward"]:
                continue
            u_orig, _ = e["orig"]
            if u_orig != self.sink and u_orig in self.used:
                return True
        return False

    def accept_cycle(self, cycle_edges, flow, bottleneck):
        """Apply cycle cancellation and mark newly-used nodes."""
        for e in cycle_edges:
            u_orig, v_orig = e["orig"]
            if e["forward"]:
                flow[u_orig][v_orig] = flow[u_orig].get(v_orig, 0) + bottleneck
                if u_orig != self.sink:
                    self.used.add(u_orig)
            else:
                old = flow[u_orig].get(v_orig, 0)
                flow[u_orig][v_orig] = old - bottleneck
        # After all edges processed, remove nodes that lost all outgoing flow
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

    # Stage 2: cancel negative-cost residual cycles
    use_constraint = sink is not None
    vf = VertexFilter(TrackedDist({}), sink) if use_constraint else None

    while True:
        residual = _build_residual(g, flow)
        if not residual:
            break

        # Collect all nodes from residual
        all_nodes = set(residual)
        for neighbors in residual.values():
            all_nodes.update(neighbors)

        tracked_dist = TrackedDist({node: 0 for node in all_nodes})
        if vf is not None:
            vf.dist = tracked_dist
            update_ok = vf
        else:
            update_ok = lambda old, new: True

        finder = NegCycleFinderQ(residual)
        get_w = lambda e: e["cost"]

        cancelled = False
        for cycle_edges in finder.howard_pred(tracked_dist, get_w, update_ok):
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
