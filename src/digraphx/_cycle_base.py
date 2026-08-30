"""Shared implementation cores for the negative-cycle finders.

This module centralises the graph-traversal helpers and the Howard
policy-iteration skeleton (Template Method) used by :class:`NegCycleFinder`
(neg_cycle.py) and :class:`NegCycleFinderQ` (neg_cycle_q.py).  The relaxation
direction and the optional negativity check are injected as strategies.

It is an implementation detail of the package; the public API lives in
``neg_cycle`` / ``neg_cycle_q`` and is unchanged.
"""

from fractions import Fraction
from typing import (
    Callable,
    Dict,
    Generator,
    List,
    Mapping,
    MutableMapping,
    Tuple,
    TypeVar,
)

# Type variables for generic graph components
Node = TypeVar("Node")  # Hashable node type (must implement __hash__)
Arc = TypeVar("Arc")  # Hashable edge type (must implement __hash__)
Domain = TypeVar(
    "Domain", int, Fraction, float
)  # Numeric type for weights (must support comparison and arithmetic)
Cycle = List[Arc]  # Alias for a list of edges forming a cycle

# A point-to map: node -> (predecessor/successor node, connecting edge)
PointTo = Dict[Node, Tuple[Node, Arc]]


def _always_true(old: Domain, new: Domain) -> bool:
    """Default `update_ok` gate: allow every distance update."""
    return True


def find_cycle(
    digraph: Mapping[Node, Mapping[Node, Arc]], point_to: PointTo
) -> Generator[Node, None, None]:
    """Yield each node that starts a cycle in the given point-to map.

    Uses a coloring algorithm (white/gray/black) to detect cycles: white nodes
    are unvisited, gray nodes are being visited in the current DFS path, and
    black nodes are fully visited.  A cycle is found when a node in the current
    path is reached again.
    """
    visited: Dict[Node, Node] = {}  # Maps nodes to their DFS root
    for vtx in filter(lambda vtx: vtx not in visited, digraph):
        utx = vtx
        while True:
            visited[utx] = vtx  # Mark as visited with current DFS root
            if utx not in point_to:
                break  # Reached a leaf node
            utx, _ = point_to[utx]  # Move to predecessor/successor
            if utx in visited:
                if visited[utx] == vtx:  # Found cycle back to current root
                    yield utx
                break  # Cycle or different DFS tree


def relax_pred(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
    update_ok: Callable[[Domain, Domain], bool],
    pred: PointTo,
) -> bool:
    """Perform one predecessor relaxation pass (Bellman-Ford style).

    Updates ``dist[v]`` and the predecessor map when the triangle inequality
    ``dist[v] > dist[u] + weight(u, v)`` holds AND ``update_ok`` permits it.
    Returns ``True`` if any distance was updated.
    """
    changed = False
    for utx, neighbors in digraph.items():
        for vtx, edge in neighbors.items():
            distance = dist[utx] + get_weight(edge)
            if dist[vtx] > distance and update_ok(dist[vtx], distance):
                dist[vtx] = distance
                pred[vtx] = (utx, edge)  # Update predecessor
                changed = True
    return changed


def relax_succ(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
    update_ok: Callable[[Domain, Domain], bool],
    succ: PointTo,
) -> bool:
    """Perform one successor relaxation pass (reverse Bellman-Ford style).

    Updates ``dist[u]`` and the successor map when the triangle inequality
    ``dist[u] < dist[v] - weight(u, v)`` holds AND ``update_ok`` permits it.
    Returns ``True`` if any distance was updated.
    """
    changed = False
    for utx, neighbors in digraph.items():
        for vtx, edge in neighbors.items():
            distance = dist[vtx] - get_weight(edge)
            if dist[utx] < distance and update_ok(dist[utx], distance):
                dist[utx] = distance
                succ[utx] = (vtx, edge)  # Update successor
                changed = True
    return changed


def cycle_list(point_to: PointTo, handle: Node) -> Cycle:
    """Reconstruct the cycle starting from ``handle`` in the point-to map.

    Follows predecessor/successor links until returning to the starting node.
    """
    vtx = handle
    cycle = list()
    while True:
        utx, edge = point_to[vtx]  # Get next node and connecting edge
        cycle.append(edge)  # Add edge to cycle
        vtx = utx  # Move to next node
        if vtx == handle:  # Completed the cycle
            break
    return cycle


def is_negative(
    point_to: PointTo,
    handle: Node,
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
) -> bool:
    """Return ``True`` if the cycle starting at ``handle`` is negative.

    A cycle is negative if at least one edge (u, v) on it violates the
    triangle inequality ``dist[v] > dist[u] + weight(u, v)``.
    """
    vtx = handle
    # C-style do-while loop
    while True:
        utx, edge = point_to[vtx]
        if dist[vtx] > dist[utx] + get_weight(edge):  # Found negative cycle
            return True
        vtx = utx
        if vtx == handle:  # Completed full cycle
            break
    return False


def howard_search(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
    update_ok: Callable[[Domain, Domain], bool],
    point_to: PointTo,
    direction: str,
    verify: bool = True,
) -> Generator[Cycle, None, None]:
    """Template Method: Howard's policy-iteration skeleton.

    Repeatedly relaxes the distance estimates until no improvement is made or a
    cycle is found, then yields each detected cycle as a list of edge weights.

    The relaxation pass and the point-to map are selected by ``direction``
    (``"pred"`` for predecessor relaxation, ``"succ"`` for successor).  When
    ``verify`` is ``True``, each candidate cycle is asserted to be negative
    before being yielded (matching the predecessor variants).
    """
    point_to.clear()
    found = False
    relax = relax_pred if direction == "pred" else relax_succ
    while not found and relax(digraph, dist, get_weight, update_ok, point_to):
        for vtx in find_cycle(digraph, point_to):
            if verify:
                # Safety check - verify the cycle is indeed negative
                assert is_negative(point_to, vtx, dist, get_weight)
            found = True
            yield cycle_list(point_to, vtx)
