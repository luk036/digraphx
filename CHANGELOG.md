# Changelog

## Version 0.8 (2026-10-12)

### Features
- **Clock Skew Scheduling API (`css.py`)**: Added `min_cycle_ratio`, `even`, `prop`, `cprop`, and `min_clock_period`, expressing the single-parameter CSS family (Min CP, EVEN, PROP, C-PROP) as one min-ratio-cycle engine over a shared `(cost, time)` abstraction. `min_clock_period` handles the max-ratio case via the negated-cost transformation. Exported from the package root.

### Testing & Code Quality
- **Canonical CSS tests**: Added `tests/test_css.py` with the preserved golden values. Removed the duplicated `find_beta`/`even`/`prop` helpers by deleting `test_timing_example_howard.py` and `test_delay_padding_example_howard.py`; their golden values now live in `test_css.py`.

## Version 0.7 (2026-10-09)

### Features
- **Optional `max_iter` cap for Howard's method**: `howard` / `howard_pred` / `howard_succ` accept an optional `max_iter` (default `None` = unbounded); a set cap raises `RuntimeError` instead of looping forever on degenerate graphs. (#8669cdd)

### Performance
- **Fast-path `TinyDiGraph.add_edge`**: Lazy-slot resolution avoids unnecessary work on edge insertion. (#a7ed9c3)
- **Pre-weighted edge list reuse**: Howard relaxation reuses the pre-weighted edge list instead of recomputing it. (#da93374)

### Bug Fixes
- **`cheat_adjlist_outer_dict` doctest**: Aligned the doctest with the lazy-sentinel behavior. (#20e7c11)

### Testing & Code Quality
- **Runtime benchmarks**: Added benchmarks for the core graph algorithms. (#0c7329a)
- **Neg-cycle tests**: Added tests covering the `max_iter` cap. (#8669cdd)

### Documentation
- **Tunable parameter reference**: Added `tunable_parameter.md`. (#9e0639b)

## Version 0.6 (2026-09-04)

### Features
- **Shared cycle/parametric bases**: Extracted `_cycle_base.py` (`find_cycle`, `relax_pred`, `relax_succ`, `cycle_list`, `is_negative`, `howard_search`) and `_parametric_base.py` (`_run_loop`) shared by the max/min parametric solvers. `NegCycleFinder`/`NegCycleFinderQ` now delegate to the shared skeleton, `MinParametricAPI` subclasses `ParametricAPI` (was a duplicate interface), and `mcf.py` reuses `_residual_edge`. Public API unchanged. (#1c60bde)
- **Public re-exports in `__init__.py`**: Fixes README quick-start imports such as `NegCycleFinder`, `TinyDiGraph`, `MinCycleRatioSolver`. (#1c60bde)

### Bug Fixes
- **mypy type errors**: Resolved None guards, test generics and networkx config issues. (#13dc943)
- **RTD doc build**: Added matplotlib and numpy to `docs/requirements.txt`. (#1f49779)

### Testing & Code Quality
- **Coverage raised 85%→99%**: Added coverage extras for MCF solver, TinyDiGraph and solvers. (#2cabc4e)
- **Style pass**: Reformatted list comprehensions and type annotations. (#2973013)

### Code Cleanup
- **Removed AI slop**: Stripped boilerplate from docstrings and comments. (#be4456a)
- **Import tidy-up**: Dropped unused `NegCycleFinderQ` import in `min_parametric_q`, split multi-name `_cycle_base` imports, stripped stray blank lines in `tiny_digraph`. (#5e37f7c)

### Build & CI
- **Removed stale `.bak` workflow**: Deleted `ci.bak`. (#5f50fe3)
- **Updated GitHub Actions**: checkout→v4, setup-python→v5, codecov-action→v4 to fix Codecov tokenless upload failure and Node 20 deprecation. (#5334192)

## Version 0.5 (2026-07-16)

### Features
- **MCF solver**: Added min-cost flow cycle-cancellation solver (`mcf.py`) and `NegCycleFinderQ` with `VertexFilter` for vertex-disjoint MCF constraint. (#582b1eb, #e6e248f)
- **CSRDiGraph**: Memory-efficient CSR-backed directed graph with `_CSRNeighbors` Mapping view — compact integer arrays instead of dicts. (#12465a3)
- **Bellman-Ford cycle detection**: Replaced Howard's algorithm with Bellman-Ford for negative cycle detection; fixed parallel edge bug. (#04da700)
- **spareTSV integration**: Added spare TSV network flow utilities and unified variable naming to `utx`/`vtx` (C++ convention). (#762008a)
- **Moved spare_tsv to experimental/**: Relocated matplotlib-dependent spare_tsv module out of main package to avoid CI failures when matplotlib is not installed. (#7367e6c)

### Performance
- **Lazy TinyDiGraph/CSRDiGraph**: Avoid pre-allocating 2N dicts per `init_nodes()` call (~464 MB saved for 1M nodes). (#12465a3)
- **Incremental residual updates**: Update only edges affected by cycle cancellation instead of rebuilding full residual each iteration. (#12465a3)

### Documentation
- **plot_directive and svgbob**: Enabled matplotlib plot_directive for auto-generated figures. Added TinyDiGraph and cycle detection example plots. Added svgbob diagram to TinyDiGraph class docstring. (#b64d424)

### Testing & Code Quality
- **Coverage raised 70%→95%**: Added extensive test coverage including MCF solver, CSRDiGraph, edge cases, and extra min-cycle-ratio tests. (#80da2a2, #9030d8a)

### Code Cleanup
- **Removed PyScaffold boilerplate**: Deleted `skeleton.py` and `test_skeleton.py`. (#9bdbdb1)
- **Dropped Python < 3.9 compat**: Removed `importlib-metadata` conditional dependency. (#9bdbdb1)
- **Config cleanup**: Removed dead entry points, unused mypy ignores, stale `IFLOW.md` and duplicate `LICENSE`. (#9bdbdb1)

### Build & CI
- **CI repair**: Fixed broken entry_points and remaining skeleton imports. (#91fd90e)
- **flake8 cleanup**: Removed unused imports and fixed formatting warnings. (#91d7141)
