"""Min-cost flow via cycle-cancellation descent.

Uses Bellman-Ford to find any negative-cost cycle in the residual graph,
then cancels it.  Repeats until no negative cycles remain — at which
point the flow is optimal.
"""

from collections import deque
from typing import Dict, Hashable, List, Optional, Tuple, TypeVar

from .neg_cycle import NegCycleFinder

Node = TypeVar("Node", bound=Hashable)


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
            # Reconstruct path
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


def cycle_canceling_mcf(g, demands):
    """Solve min-cost flow using cycle-cancellation descent.

    Args:
        g: {u: {v: {'weight': cost, 'capacity': cap}}}
        demands: {node: demand} (negative = supply, positive = demand)

    Returns:
        (total_cost, flow_dict) or None if infeasible.
    """
    # Stage 1: find feasible initial flow
    flow = _find_feasible_flow(g, demands)
    if flow is None:
        return None

    # Stage 2: cancel negative-cost residual cycles
    while True:
        residual = _build_residual(g, flow)
        if not residual:
            break

        finder = NegCycleFinder(residual)
        # Collect all nodes from residual (dict keys + target nodes)
        all_nodes = set(residual)
        for neighbors in residual.values():
            all_nodes.update(neighbors)
        dist = {node: 0 for node in all_nodes}
        cancelled = False
        for cycle_edges in finder.howard(dist, lambda e: e["cost"]):
            bottleneck = float("inf")
            for edge in cycle_edges:
                bottleneck = min(bottleneck, edge["capacity"])
            bottleneck = int(bottleneck)
            if bottleneck <= 0:
                continue

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
