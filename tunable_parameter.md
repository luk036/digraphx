# Tunable Parameters in `digraphx`

A complete reference of every user-tunable parameter of the algorithms in this
project, together with its default value and source location.

## Key finding

`digraphx` has **no `Options` / config dataclass**. There are zero `@dataclass`
or `NamedTuple` definitions in the package. Every tunable is a plain
function/method parameter or an injected callback. The dominant policy knob is
the `update_ok` predicate that gates Bellman-Ford relaxation.

This report separates the categories explicitly so it is clear what a caller
can actually adjust.

---

## 1. Negative-cycle finders

Files: `src/digraphx/neg_cycle.py`, `src/digraphx/neg_cycle_q.py`,
internal `src/digraphx/_cycle_base.py`.

| API | Parameters | Default |
| --- | --- | --- |
| `NegCycleFinder(digraph)` | `digraph` | required |
| `NegCycleFinder.howard(dist, get_weight, max_iter=None)` | `max_iter: int \| None` | `None` (unbounded) |
| `NegCycleFinderQ(digraph)` | `digraph` | required |
| `NegCycleFinderQ.relax_pred(dist, get_weight, update_ok)` | `update_ok` (predicate) | required |
| `NegCycleFinderQ.relax_succ(dist, get_weight, update_ok)` | `update_ok` | required |
| `NegCycleFinderQ.howard_pred(dist, get_weight, update_ok, max_iter=None)` | `update_ok`; `max_iter` | required; `None` |
| `NegCycleFinderQ.howard_succ(dist, get_weight, update_ok, max_iter=None)` | `update_ok`; `max_iter` | required; `None` |
| `howard_search(..., direction, verify=True, max_iter=None)` (internal) | `verify: bool`; `max_iter` | `True`; `None` |

Notes:

- `update_ok(old, new) -> bool` is the relaxation-gate callback. When
  `NegCycleFinder` omits it, the gate is `_always_true`
  (`src/digraphx/_cycle_base.py:36-38`).
- `NegCycleFinderQ.howard_succ` hard-wires `verify=False`; `howard_pred` uses
  `verify=True` (`src/digraphx/neg_cycle_q.py:281` and `:239-241`).

---

## 2. Parametric solvers

Files: `src/digraphx/parametric.py`, `src/digraphx/min_parametric_q.py`,
internal `src/digraphx/_parametric_base.py`.

| API | Parameters | Default |
| --- | --- | --- |
| `MaxParametricSolver(digraph, omega)` | `omega` (strategy) | required |
| `MaxParametricSolver.run(dist, ratio)` | — | no tunables (internally `minimize=True`) |
| `MinParametricSolver(digraph, omega)` | `omega` | required |
| `MinParametricSolver.run(dist, ratio, update_ok, pick_one_only=False)` | `update_ok`; `pick_one_only: bool` | required; `False` |
| `_run_loop(..., *, minimize, update_ok=..., pick_one_only=False, alternate_direction=False)` (internal) | `update_ok`, `pick_one_only`, `alternate_direction` | `lambda old, new: True`; `False`; `False` |

- `MinParametricSolver.run` is the public surface
  (`src/digraphx/min_parametric_q.py:125-131`).
- `alternate_direction=True` is fixed internally for the constrained solver.

---

## 3. Minimum cycle ratio

File: `src/digraphx/min_cycle_ratio.py`.

| API | Parameters | Default |
| --- | --- | --- |
| `MinCycleRatioSolver(digraph)` | `digraph` | required |
| `MinCycleRatioSolver.run(dist, ratio0)` | `ratio0` (initial ratio) | required |
| `CycleRatioAPI(digraph, result_type)` | `result_type` (`Fraction` or `float`) | required (selects numeric precision) |
| `set_default(digraph, weight, value)` | `weight: str`, `value` | required |

---

## 4. Min-cost flow (cycle-canceling)

File: `src/digraphx/mcf.py`.

| API | Parameters | Default |
| --- | --- | --- |
| `cycle_canceling_mcf(g, demands, sink=None)` | `sink` | `None` |
| `VertexFilter(sink)` | `sink` | required |

- When `sink` is provided, the vertex-disjoint constraint is enabled; when
  `None`, no constraint is enforced.
- Edge-data defaults consumed internally: `capacity` defaults to `inf`,
  `weight` defaults to `0`; the bottleneck is truncated via `int(...)`
  (`src/digraphx/mcf.py:61-62`, `:239`, `:304`).

---

## 5. Graph containers

Files: `src/digraphx/tiny_digraph.py`, `src/digraphx/csr_digraph.py`.

| API | Parameters | Default |
| --- | --- | --- |
| `TinyDiGraph.init_nodes(num_nodes)` | `num_nodes: int` | required |
| `TinyDiGraph.add_edge(u, v, **attr)` | free-form attributes | — |
| `CSRDiGraph.init_nodes(num_nodes)` | `num_nodes: int` | required |
| `CSRDiGraph.add_edge(u, v, **attr)` | free-form attributes | — |
| `CSRDiGraph.freeze()` | — | — |
| `DiGraphAdapter.get_edge_data(u, v, default=None)` | `default` | `None` |

---

## 6. Repository utilities (experiments, not core library)

File: `experimental/spare_tsv.py`.

| Function | Parameters | Default |
| --- | --- | --- |
| `formGraph(T, pos, mu, eta, seed=None)` | `seed` | `None` |
| `vdc(n, base=2)` | `base` | `2` |
| `vdcorput(n, base=2)` | `base` | `2` |
| `vdcorput_iter(n, base=2)` | `base` | `2` |
| `showPaths(gra, pos, N, edgeProbs=1.0, path=None, visibleNodes=None, guards=None)` | `edgeProbs`, `path`, `visibleNodes`, `guards` | `1.0`, `None`, `None`, `None` |
| `setup_network_flow(gra, pos, primal_count, capacity)` | `capacity` | required |
| `solve_network_flow(gra, sink_node)` | `sink_node` | required |

---

## 7. Fixed values in tests and benchmarks (not library defaults)

| Source | Constant | Value |
| --- | --- | --- |
| `benchmarks/test_benchmarks.py:21-23` | `SEED`, `SIZES`, `MCR_SIZES` | `1234`, `[200, 1000]`, `[50, 100]` |
| `benchmarks/test_benchmarks.py:53-61` | node degree | `5` / `6` |
| `tests/test_*howard*.py:14,64,107` | test-local Howard helper `max_iter` | `2000` |
| `experiments/experi.py:13-23` and `experi-descent*.py` | `N`, `M`, `r`, `mu`, `eta`, `seed`, `xbase`, `ybase` | `155`, `40`, `4`, `0.12`, `1.6`, `5`, `2`, `3` |
| `docs/examples/plot_*.py` | `seed` | `42` |

---

## Summary of genuine tunables

| Tunable | Default | Location |
| --- | --- | --- |
| `update_ok` predicate (relaxation gate) | `lambda old, new: True` | `src/digraphx/_cycle_base.py:37`, `src/digraphx/_parametric_base.py:37` |
| `howard`/`howard_pred`/`howard_succ` `max_iter` | `None` (unbounded; raises `RuntimeError` if set and exceeded) | `src/digraphx/neg_cycle.py`, `src/digraphx/neg_cycle_q.py` |
| `MinParametricSolver.run(..., pick_one_only)` | `False` | `src/digraphx/min_parametric_q.py:130` |
| `cycle_canceling_mcf(..., sink)` | `None` | `src/digraphx/mcf.py:254` |
| `CycleRatioAPI(..., result_type)` | required (`Fraction` / `float`) | `src/digraphx/min_cycle_ratio.py:113` |
| `howard_search(..., verify)` (internal) | `True` | `src/digraphx/_cycle_base.py:210` |
| `_run_loop(..., alternate_direction)` (internal) | `False` | `src/digraphx/_parametric_base.py:39` |
| `formGraph(..., seed)` | `None` | `experimental/spare_tsv.py:34` |
| `vdc` / `vdcorput` / `vdcorput_iter(..., base)` | `2` | `experimental/spare_tsv.py:10,20,25` |
| `showPaths` overlay options | `edgeProbs=1.0`, `path=None`, `visibleNodes=None`, `guards=None` | `experimental/spare_tsv.py:54` |

Everything else is problem data (graph, distances, ratio, demands) or a
hardcoded constant (`capacity=inf`, `weight=0`, integer bottleneck,
`verify=False` on `howard_succ`).
