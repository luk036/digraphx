"""Shared implementation cores for the negative-cycle finders.

This module centralises the graph-traversal helpers and the Howard
policy-iteration skeleton (Template Method) used by :class:`NegCycleFinder`
(neg_cycle.py) and :class:`NegCycleFinderQ` (neg_cycle_q.py).  The relaxation
direction and the optional negativity check are injected as strategies.

It is an implementation detail of the package; the public API lives in
``neg_cycle`` / ``neg_cycle_q`` and is unchanged.
"""

from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Tuple,
)

from ._types import Arc, Cycle, Domain, Node, PointTo


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


def prepare_edges(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    get_weight: Callable[[Arc], Domain],
) -> List[Tuple[Node, Node, Arc, Domain]]:
    """Flatten the graph into ``(u, v, edge, weight)`` tuples.

    ``get_weight`` is evaluated exactly once per edge.  Callers that keep the
    ratio (and hence every edge weight) fixed for the whole search can reuse the
    result across many relaxation passes instead of recomputing it each time.
    """
    return [
        (utx, vtx, edge, get_weight(edge))
        for utx, neighbors in digraph.items()
        for vtx, edge in neighbors.items()
    ]


def relax_pred_flat(
    edges: List[Tuple[Node, Node, Arc, Domain]],
    dist: MutableMapping[Node, Domain],
    update_ok: Callable[[Domain, Domain], bool],
    pred: PointTo,
) -> bool:
    """Predecessor relaxation over a pre-flattened, pre-weighted edge list."""
    changed = False
    for utx, vtx, edge, weight in edges:
        distance = dist[utx] + weight
        if dist[vtx] > distance and update_ok(dist[vtx], distance):
            dist[vtx] = distance
            pred[vtx] = (utx, edge)
            changed = True
    return changed


def relax_succ_flat(
    edges: List[Tuple[Node, Node, Arc, Domain]],
    dist: MutableMapping[Node, Domain],
    update_ok: Callable[[Domain, Domain], bool],
    succ: PointTo,
) -> bool:
    """Successor relaxation over a pre-flattened, pre-weighted edge list."""
    changed = False
    for utx, vtx, edge, weight in edges:
        distance = dist[vtx] - weight
        if dist[utx] < distance and update_ok(dist[utx], distance):
            dist[utx] = distance
            succ[utx] = (vtx, edge)
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


def is_negative_pred(
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


def is_negative_succ(
    point_to: PointTo,
    handle: Node,
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
) -> bool:
    """Predecessor check mirrored for successor relaxation.

    The successor policy keeps ``dist[u] >= dist[v] - weight(u, v)`` for
    ``point_to[u] == (v, edge)``, so a negative cycle violates the inequality in
    the opposite direction: ``dist[u] < dist[v] - weight(u, v)``.
    """
    vtx = handle
    while True:
        utx, edge = point_to[vtx]
        if dist[vtx] < dist[utx] - get_weight(edge):
            return True
        vtx = utx
        if vtx == handle:
            break
    return False


class Relaxation(Protocol[Node, Arc, Domain]):
    """The two orientation-specific operations Howard's method needs."""

    def relax(
        self,
        edges: List[Tuple[Node, Node, Arc, Domain]],
        dist: MutableMapping[Node, Domain],
        update_ok: Callable[[Domain, Domain], bool],
        point_to: PointTo,
    ) -> bool:
        ...

    def is_negative(
        self,
        point_to: PointTo,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        ...


class PredecessorRelaxation:
    """Bellman-Ford relaxation of ``dist[v]`` through each incoming edge."""

    def relax(
        self,
        edges: List[Tuple[Node, Node, Arc, Domain]],
        dist: MutableMapping[Node, Domain],
        update_ok: Callable[[Domain, Domain], bool],
        point_to: PointTo,
    ) -> bool:
        return relax_pred_flat(edges, dist, update_ok, point_to)

    def is_negative(
        self,
        point_to: PointTo,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        return is_negative_pred(point_to, handle, dist, get_weight)


class SuccessorRelaxation:
    """Reverse Bellman-Ford relaxation of ``dist[u]`` through each outgoing edge."""

    def relax(
        self,
        edges: List[Tuple[Node, Node, Arc, Domain]],
        dist: MutableMapping[Node, Domain],
        update_ok: Callable[[Domain, Domain], bool],
        point_to: PointTo,
    ) -> bool:
        return relax_succ_flat(edges, dist, update_ok, point_to)

    def is_negative(
        self,
        point_to: PointTo,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        return is_negative_succ(point_to, handle, dist, get_weight)


class HowardFinderBase(Generic[Node, Arc, Domain]):
    """State shared by the two Howard finders.

    Both keep the graph and a predecessor policy map; the successor map and the
    public method signatures differ, so only these members are shared.
    """

    digraph: Mapping[Node, Mapping[Node, Arc]]
    pred: PointTo

    def __init__(self, digraph: Mapping[Node, Mapping[Node, Arc]]) -> None:
        self.digraph = digraph
        self.pred = {}

    def is_negative(
        self,
        handle: Node,
        dist: MutableMapping[Node, Domain],
        get_weight: Callable[[Arc], Domain],
    ) -> bool:
        """Return ``True`` if the cycle starting at ``handle`` is negative."""
        return is_negative_pred(self.pred, handle, dist, get_weight)


def howard_search(
    digraph: Mapping[Node, Mapping[Node, Arc]],
    dist: MutableMapping[Node, Domain],
    get_weight: Callable[[Arc], Domain],
    update_ok: Callable[[Domain, Domain], bool],
    point_to: PointTo,
    relaxation: Relaxation[Node, Arc, Domain],
    *,
    max_iter: Optional[int] = None,
) -> Generator[Cycle, None, None]:
    """Template Method: Howard's policy-iteration skeleton.

    Repeatedly relaxes the distance estimates until no improvement is made or a
    cycle is found, then yields each detected cycle as a list of its edges.

    ``relaxation`` supplies both the relaxation pass and the orientation-specific
    negativity test, so the skeleton no longer branches on a direction string and
    every yielded cycle is verified.

    ``max_iter`` optionally caps the number of relaxation rounds.  ``None``
    (default) means unbounded; when set and exceeded without finding a negative
    cycle, ``RuntimeError`` is raised rather than looping forever.
    """
    point_to.clear()
    found = False
    num_iter = 0
    edges = prepare_edges(digraph, get_weight)
    while not found and relaxation.relax(edges, dist, update_ok, point_to):
        num_iter += 1
        for vtx in find_cycle(digraph, point_to):
            if not relaxation.is_negative(point_to, vtx, dist, get_weight):
                raise AssertionError(
                    "Howard's method produced a cycle that is not negative"
                )
            found = True
            yield cycle_list(point_to, vtx)
        if not found and max_iter is not None and num_iter >= max_iter:
            raise RuntimeError(
                f"howard_search did not converge within max_iter={max_iter}"
            )
