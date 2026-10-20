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

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from digraphx import min_clock_period

Path_ = Tuple[str, str]
Edge = Dict[str, object]
Graph = Dict[str, Dict[str, Dict[str, object]]]
Sweep = List[Tuple[float, float, float]]

DATA_PATHS: Dict[Path_, Tuple[float, float]] = {
    ("A", "B"): (12.0, 3.0),
    ("B", "C"): (4.0, 4.0),
    ("C", "D"): (4.0, 4.0),
    ("D", "A"): (4.0, 4.0),
}
"""Ring ``A -> B -> C -> D -> A``; each value is ``(D_ij, d_ij)``.

``A -> B`` is a reconvergent cone: a shared prefix (delay 2) that fans out into
a long branch (5 + 5) and a short branch (1), so ``D_AB = 12`` and ``d_AB = 3``.
"""

SWEEP: Sequence[float] = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0)
"""Padding amounts swept by both the printed table and the paper figure."""


def build(
    delta_D: Dict[Path_, float] | None = None,
    delta_d: Dict[Path_, float] | None = None,
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
    delta_D: Dict[Path_, float] | None = None,
    delta_d: Dict[Path_, float] | None = None,
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


def setup_floor() -> float:
    """Setup-only bound: no amount of hold padding can beat it."""
    return sum(D for D, _ in DATA_PATHS.values()) / len(DATA_PATHS)


def sweep() -> Sweep:
    """``(padding, min-only period, shared period)`` for every padding amount."""
    return [(amount, pad_min_only(amount), pad_shared(amount)) for amount in SWEEP]


def tikz(rows: Optional[Sweep] = None) -> str:
    """Render the padding sweep as a pgfplots axis, ready for ``\\input``."""
    rows = sweep() if rows is None else rows
    min_only = "".join(f"({a:g},{p:g})" for a, p, _ in rows)
    shared = "".join(f"({a:g},{p:g})" for a, _, p in rows)
    x_max = max(a for a, _, _ in rows)
    y_max = max(max(p, q) for _, p, q in rows) + 1.0
    return f"""\\begin{{tikzpicture}}
\\begin{{axis}}[
  width=0.82\\linewidth,
  height=5.4cm,
  xlabel={{added delay on the $A\\to B$ logic}},
  ylabel={{minimum clock period}},
  xmin=0, xmax={x_max:g}, ymin=0, ymax={y_max:g},
  domain=0:{x_max:g},
  grid=both, grid style={{gray!25}},
  legend pos=north east, legend cell align=left,
  every axis plot/.append style={{thick}},
]
% padding the min-only branch lowers the period ...
\\addplot[color=red, mark=*] coordinates {{{min_only}}};
\\addlegendentry{{pad min-only branch}}
% ... padding the shared prefix moves both delays and changes nothing.
\\addplot[color=blue, mark=square*] coordinates {{{shared}}};
\\addlegendentry{{pad shared prefix}}
% setup-only floor: no hold padding can beat it.
\\addplot[color=black, dashed, mark=none] {{{setup_floor():g}}};
\\addlegendentry{{setup-only floor}}
\\end{{axis}}
\\end{{tikzpicture}}
"""


def report() -> None:
    """Print the narrative used in the paper."""
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
    for amount, min_only_period, shared_period in sweep():
        print(f"      {amount:4.1f}   {min_only_period:8.2f}   {shared_period:6.2f}")
    print(
        f"      floor at {setup_floor():.2f} = (12 + 4 + 4 + 4) / 4 setup-only bound\n"
    )

    print("[5] The simple paths B -> C, C -> D, D -> A have D = d,")
    print("      so no insertion can separate their setup and hold delays.")


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Delay padding demo")
    parser.add_argument(
        "--tikz",
        type=Path,
        metavar="PATH",
        help="write the padding-sweep figure as TikZ and exit",
    )
    args = parser.parse_args(argv)
    if args.tikz is not None:
        with args.tikz.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(tikz())
        return
    report()


if __name__ == "__main__":
    main()
