# Changelog

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
