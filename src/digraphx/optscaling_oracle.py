# -*- coding: utf-8 -*-
from typing import Optional, Tuple, Union

import numpy as np

from .network_oracle import NetworkOracle

# np.ndarray = np.ndarray
Arr = Union[np.ndarray, float]
Cut = Tuple[Arr, float]


class OptScalingOracle:
    """Oracle for Optimal Matrix Scaling

    This example is taken from[Orlin and Rothblum, 1985]

        min     π/ψ
        s.t.    ψ ≤ utx[i] * |aij| * utx[j]^{−1} ≤ π,
                ∀ aij != 0,
                π, ψ, utx, positive
    """

    class Ratio:
        def __init__(self, gra, get_cost):
            """[summary]

            Arguments:
                gra ([type]): [description]
            """
            self._gra = gra
            self._get_cost = get_cost

        def eval(self, edge, x: Arr) -> float:
            """[summary]

            Arguments:
                edge ([type]): [description]
                x (Arr): (π, ψ) in log scale

            Returns:
                float: function evaluation
            """
            utx, vtx = edge
            cost = self._get_cost(edge)
            assert utx != vtx
            return x[0] - cost if utx < vtx else cost - x[1]

        def grad(self, edge, x: Arr) -> Arr:
            """[summary]

            Arguments:
                edge ([type]): [description]
                x (Arr): (π, ψ) in log scale

            Returns:
                [type]: [description]
            """
            utx, vtx = edge
            assert utx != vtx
            return np.array([1.0, 0.0] if utx < vtx else [0.0, -1.0])

    def __init__(self, gra, utx, get_cost):
        """Construct a new optscaling oracle object

        Arguments:
            gra ([type]): [description]
        """
        self._network = NetworkOracle(gra, utx, self.Ratio(gra, get_cost))

    def assess_optim(self, x: Arr, t: float) -> Tuple[Cut, Optional[float]]:
        """Make object callable for cutting_plane_optim()

        Arguments:
            x (Arr): (π, ψ) in log scale
            t (float): the best-so-far optimal value

        Returns:
            Tuple[Cut, float]

        See also:
            cutting_plane_optim
        """
        s = x[0] - x[1]
        g = np.array([1.0, -1.0])
        if (fj := s - t) >= 0.0:
            return (g, fj), None

        if cut := self._network.assess_feas(x):
            return cut, None

        return (g, 0.0), s
