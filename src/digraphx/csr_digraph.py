"""
CSRDiGraph — Memory‑efficient directed graph backed by Compressed Sparse Row storage.

For a graph with *N* nodes and *E* edges the internal arrays use
O(N + E) machine integers plus one Python object per edge (the data dict).
This is dramatically smaller than ``dict``‑of‑``dict`` storage when *N* is large
and the graph is sparse.
"""

from array import array
from typing import Mapping

__all__ = ["CSRDiGraph"]


class _CSRNeighbors(Mapping):
    """Read‑only view into a single node's adjacency (backed by CSR arrays)."""

    __slots__ = ("_indices", "_data", "_start", "_end")

    def __init__(self, indices: array, data: list, start: int, end: int) -> None:
        self._indices = indices
        self._data = data
        self._start = start
        self._end = end

    def __getitem__(self, v: int):
        for i in range(self._start, self._end):
            if self._indices[i] == v:
                return self._data[i]
        raise KeyError(v)

    def __iter__(self):
        return iter(self._indices[self._start : self._end])

    def __len__(self):
        return self._end - self._start

    def __contains__(self, v):
        return any(self._indices[i] == v for i in range(self._start, self._end))

    def items(self):
        for i in range(self._start, self._end):
            yield self._indices[i], self._data[i]

    def keys(self):
        return iter(self._indices[self._start : self._end])

    def values(self):
        return iter(self._data[self._start : self._end])


class CSRDiGraph(Mapping):
    """Memory‑efficient directed graph using Compressed Sparse Row storage.

    Nodes must be integers ``0 .. N-1``.  Call :meth:`init_nodes` first, then
    :meth:`add_edge` any number of times, then call :meth:`freeze` to compact
    storage.  After freezing the graph is still fully readable but no longer
    supports edge addition.

    Examples
    --------
    >>> g = CSRDiGraph()
    >>> g.init_nodes(3)
    >>> g.add_edge(0, 1, weight=7)
    >>> g.add_edge(1, 2, weight=3)
    >>> g.add_edge(2, 0, weight=-5)
    >>> g.freeze()
    >>> sorted(g[0].items())
    [(1, {'weight': 7})]
    >>> list(g.nodes())
    [0, 1, 2]
    """

    def __init__(self) -> None:
        self._num_nodes = 0
        self._edges: list[list] | None = None  # temp storage before freeze
        self._indptr: array | None = None
        self._indices: array | None = None
        self._data: list | None = None
        self._frozen = False

    # ---- construction ----

    def init_nodes(self, num_nodes: int) -> None:
        """Allocate storage for *num_nodes* (``0 … num_nodes-1``)."""
        self._num_nodes = num_nodes
        self._edges = [[] for _ in range(num_nodes)]
        self._frozen = False

    def add_edge(self, u: int, v: int, **attr) -> None:  # type: ignore
        """Add a directed edge ``u → v`` with optional attributes."""
        assert not self._frozen, "graph is frozen"
        self._edges[u].append((v, attr if attr else {}))

    def freeze(self) -> None:
        """Compact internal storage to CSR arrays.

        After this call the graph is read‑only.
        """
        if self._frozen:
            return
        indptr = array("i", [0])  # cumulative counts
        for node_edges in self._edges:
            indptr.append(indptr[-1] + len(node_edges))
        total = indptr[-1]
        indices = array("i", [0]) * total  # placeholder
        data: list = [None] * total
        idx = 0
        for node_edges in self._edges:
            for v, d in node_edges:
                indices[idx] = v
                data[idx] = d
                idx += 1
        self._indptr = indptr
        self._indices = indices
        self._data = data
        self._edges = None  # free temp storage
        self._frozen = True

    # ---- Mapping protocol ----

    def __getitem__(self, u: int):
        if not self._frozen:
            self.freeze()
        start = self._indptr[u]
        end = self._indptr[u + 1]
        return _CSRNeighbors(self._indices, self._data, start, end)

    def __iter__(self):
        return iter(range(self._num_nodes))

    def __len__(self):
        return self._num_nodes

    def __contains__(self, u):
        return isinstance(u, int) and 0 <= u < self._num_nodes

    def items(self):
        if not self._frozen:
            self.freeze()
        for u in range(self._num_nodes):
            start = self._indptr[u]
            end = self._indptr[u + 1]
            yield u, _CSRNeighbors(self._indices, self._data, start, end)

    # ---- graph-like helpers ----

    def nodes(self):
        """Return all node identifiers."""
        return range(self._num_nodes)

    def __repr__(self):
        if self._frozen and self._indptr is not None:
            total = self._indptr[-1]
        elif self._edges is not None:
            total = sum(len(e) for e in self._edges)
        else:
            total = 0
        return f"CSRDiGraph({self._num_nodes} nodes, {total} edges)"
