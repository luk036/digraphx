"""Shared type aliases for digraphx.

Every module in the package used to declare its own copy of these names, with
subtly different bounds (``Ratio`` was ``int|float`` in one place and
``Fraction|float`` in another).  They now live here so that the dependency
graph is acyclic and unambiguous:

    _types  ->  _cycle_base  ->  neg_cycle / neg_cycle_q
       |                            |
       +--> _parametric_api  ->  _parametric_base  ->  parametric / min_parametric_q
                                                           |
                                                           +--> min_cycle_ratio / css

Downward only: a lower layer never imports a higher one.
"""

from fractions import Fraction
from typing import Dict, List, Mapping, MutableMapping, Tuple, TypeVar

Node = TypeVar("Node")
Arc = TypeVar("Arc")
Domain = TypeVar("Domain", int, Fraction, float)
Ratio = TypeVar("Ratio", int, Fraction, float)

Cycle = List[Arc]
PointTo = Dict[Node, Tuple[Node, Arc]]
Graph = Mapping[Node, Mapping[Node, Arc]]
MutableGraph = MutableMapping[Node, Mapping[Node, Arc]]

__all__ = [
    "Arc",
    "Cycle",
    "Domain",
    "Graph",
    "MutableGraph",
    "Node",
    "PointTo",
    "Ratio",
]
