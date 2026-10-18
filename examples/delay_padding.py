"""Delay padding demo on a four-flip-flop ring with a reconvergent path.

A local data path from ``FF_i`` to ``FF_j`` is ONE block of combinational logic
whose delay runs between a minimum ``d_ij`` (early/fast) and a maximum ``D_ij``
(late/slow).  The two numbers describe the SAME data path: setup uses ``D_ij``,
hold uses ``d_ij``.

Delay padding inserts extra delay into that logic.  The point of this demo is
that an insertion only helps when it raises ``d_ij`` without raising ``D_ij`` --
which is possible only where the minimum-delay route and the maximum-delay route
differ.  On a shared segment both delays rise together and the clock period does
not move.
"""

from __future__ import annotations

from typing import Dict, Tuple

from digraphx import min_clock_period

Path = Tuple[str, str]
Edge = Dict[str, object]
Graph = Dict[str, Dict[str, Dict[str, object]]]

DATA_PATHS: Dict[Path, Tuple[float, float]] = {
    ("A", "B"): (12.0, 3.0),
    ("B", "C"): (4.0, 4.0),
    ("C", "D"): (4.0, 4.0),
    ("D", "A"): (4.0, 4.0),
}
"""Ring ``A -> B -> C -> D -> A``; each value is ``(D_ij, d_ij)``.

``A -> B`` is a reconvergent cone: a shared prefix (delay 2) that fans out into
a long branch (5 + 5) and a short branch (1), so ``D_AB = 12`` and ``d_AB = 3``.
The other three paths are simple (``D = d``).
"""


def build(
    delta_D: Dict[Path, float] | None = None,
    delta_d: Dict[Path, float] | None = None,
) -> Graph:
    """Build the timing constraint graph, optionally perturbing delays.

    Args:
        delta_D: extra delay added to ``D_ij`` (raises the setup path) per pair.
        delta_d: extra delay added to ``d_ij`` (raises the hold path) per pair.
    """
    delta_D = delta_D or {}
    delta_d = delta_d or {}
    g: Graph = {}
    for (i, j), (D, d) in DATA_PATHS.items():
        D += delta_D.get((i, j), 0.0)
        d += delta_d.get((i, j), 0.0)
        g.setdefault(j, {})[i] = {"type": "s", "delay": D}
        g.setdefault(i, {})[j] = {"type": "h", "delay": d}
    return g


def period(
    delta_D: Dict[Path, float] | None = None,
    delta_d: Dict[Path, float] | None = None,
) -> float:
    """Minimum feasible clock period after the given perturbations."""
    g = build(delta_D, delta_d)
    return min_clock_period(g, {node: 0.0 for node in g})[0]


def pad_shared(amount: float) -> float:
    """Pad the shared prefix of ``A -> B``: raises ``D_AB`` and ``d_AB`` together."""
    return period(delta_D={("A", "B"): amount}, delta_d={("A", "B"): amount})


def pad_min_only(amount: float) -> float:
    """Pad the minimum-only branch of ``A -> B``: raises ``d_AB`` alone."""
    return period(delta_d={("A", "B"): amount})


def main() -> None:
    print("Delay padding demo: a 4-flip-flop ring with a reconvergent path\n")
    print("Model")
    print("  a local data path i -> j is ONE block of logic with")
    print(
        "    D_ij = maximum path delay (setup)  and  d_ij = minimum path delay (hold)"
    )
    print("  minimum period = max over cycles of")
    print("    (sum of setup delays - sum of hold delays) / (# setup edges)\n")

    base = period()
    print("[1] Baseline -- clock skew scheduling only")
    print(f"      minimum feasible clock period : {base:.2f}")
    print("      limiting cycle                : pair (A, B), D_AB - d_AB = 12 - 3\n")

    shared = pad_shared(3.0)
    print("[2] Pad the SHARED prefix of A -> B (raises D_AB and d_AB together)")
    print(
        f"      added delay 3.00 -> period {shared:.2f}  (inert: D_AB - d_AB is unchanged)"
    )
    print("      a simple 1-2 gate path behaves the same way: D_ij = d_ij\n")

    min_only = pad_min_only(3.0)
    gain = 100.0 * (base - min_only) / base
    print("[3] Pad the MIN-ONLY branch of A -> B (raises d_AB alone)")
    print(f"      added delay 3.00 -> period {min_only:.2f}  ({gain:.1f}% faster)")
    print("      only a route that misses every maximum-delay route can do this\n")

    print("[4] Sweep of padding on A -> B")
    print("      pad   min-only   shared")
    for amount in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0):
        print(
            f"      {amount:4.1f}   {pad_min_only(amount):8.2f}   {pad_shared(amount):6.2f}"
        )
    floor = (12.0 + 4.0 + 4.0 + 4.0) / 4.0
    print(f"      floor at {floor:.2f} = (12 + 4 + 4 + 4) / 4 setup-only bound\n")

    print("[5] The simple paths B -> C, C -> D, D -> A have D = d,")
    print("      so no insertion can separate their setup and hold delays.")


if __name__ == "__main__":
    main()
