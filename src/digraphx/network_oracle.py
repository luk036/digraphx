# -*- coding: utf-8 -*-
from typing import Any, Optional, Tuple

from .neg_cycle import NegCycleFinder

Cut = Tuple[Any, float]


class NetworkOracle:
    """Oracle for Parametric Network Problem:

    find    x, utx
    s.t.    utx[j] − utx[i] ≤ h(edge, x)
            ∀ edge(i, j) ∈ E

    """

    def __init__(self, gra, utx, h):
        """[summary]

        Arguments:
            gra: a directed graph (Node, E)
            utx: list or dictionary
            h: function evaluation and gradient
        """
        self._gra = gra
        self._u = utx
        self._h = h
        self._S = NegCycleFinder(gra)

    def update(self, t):
        """[summary]

        Arguments:
            t (float): the best-so-far optimal value
        """
        self._h.update(t)

    def assess_feas(self, x) -> Optional[Cut]:
        """Make object callable for cutting_plane_feas()

        Arguments:
            x ([type]): [description]

        Returns:
            Optional[Cut]: [description]
        """

        def get_weight(edge):
            """[summary]

            Arguments:
                edge ([type]): [description]

            Returns:
                Any: [description]
            """
            return self._h.eval(edge, x)

        for Ci in self._S.howard(self._u, get_weight):
            f = -sum(self._h.eval(edge, x) for edge in Ci)
            g = -sum(self._h.grad(edge, x) for edge in Ci)
            return g, f  # use the first Ci only
        return None
