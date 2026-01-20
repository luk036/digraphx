[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![Documentation Status](https://readthedocs.org/projects/digraphx/badge/?version=latest)](https://digraphx.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/luk036/digraphx/branch/main/graph/badge.svg?token=U7PKg0lceH)](https://codecov.io/gh/luk036/digraphx)

# 🔀 digraphx

> Efficient directed graph algorithms for network optimization in Python

digraphx is a Python library that provides high-performance implementations of directed graph algorithms, optimized for large-scale network optimization problems. It extends NetworkX with specialized data structures and algorithms for negative cycle detection, cycle ratio optimization, and parametric network analysis.

## Features

- **High-performance graph storage**: `TinyDiGraph` with memory-efficient `MapAdapter` backend
- **Negative cycle detection**: Howard's algorithm for finding negative cycles in weighted directed graphs
- **Minimum/Maximum Cycle Ratio**: Efficient algorithms for finding cycles with optimal cost/time ratios
- **Parametric network optimization**: Generic framework for ratio-based optimization problems
- **Type-safe**: Full type hints throughout codebase
- **Well-tested**: Comprehensive test coverage with pytest

## When to Use digraphx vs NetworkX

**Use digraphx when:**
- Working with very large graphs (thousands to millions of nodes)
- Need memory-efficient storage for graphs with known node counts
- Optimizing cycles based on cost/time ratios
- Finding negative cycles in weighted graphs
- Implementing parametric optimization algorithms

**Use standard NetworkX when:**
- Need a general-purpose graph library
- Working with small to medium-sized graphs
- Need extensive graph algorithms not in digraphx
- Dynamic graph operations (frequent node/edge additions/removals)

## Installation

### From PyPI

```bash
pip install digraphx
```

### From Source

```bash
git clone https://github.com/luk036/digraphx.git
cd digraphx
pip install -e .
```

## Dependencies

- [NetworkX](https://networkx.org/) - Graph library foundation
- [luk036/mywheel](https://github.com/luk036/mywheel) - Custom utilities (MapAdapter for efficient storage)

## Quick Start

### Detect Negative Cycles

```python
from digraphx import NegCycleFinder

# Create a directed graph with a negative cycle
digraph = {
    'a': {'b': 7, 'c': 5},
    'b': {'a': 0, 'c': 3},
    'c': {'a': 2, 'b': 1}
}

# Initialize distances
dist = {node: 0 for node in digraph}

# Find negative cycles using Howard's algorithm
finder = NegCycleFinder(digraph)
for cycle in finder.howard(dist, lambda edge: edge):
    print(f"Found negative cycle: {cycle}")
```

### Minimum Cycle Ratio

```python
from digraphx import MinCycleRatioSolver
from digraphx import DiGraphAdapter
from fractions import Fraction

# Create a graph with cost and time attributes
graph = DiGraphAdapter()
graph.add_edge('a', 'b', cost=5, time=1)
graph.add_edge('b', 'c', cost=3, time=1)
graph.add_edge('c', 'a', cost=-2, time=1)

# Solve for minimum cycle ratio
solver = MinCycleRatioSolver(graph)
dist = {node: Fraction(0) for node in graph}
ratio, cycle = solver.run(dist, Fraction(10))
print(f"Minimum cycle ratio: {ratio}")
```

### High-Performance Graph with TinyDiGraph

```python
from digraphx import TinyDiGraph

# Create a graph optimized for 1000 nodes
graph = TinyDiGraph()
graph.init_nodes(1000)

# Add edges efficiently
for i in range(1000):
    for j in range(i+1, min(i+10, 1000)):
        graph.add_edge(i, j, weight=i+j)

# Access graph properties
print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")
```

## Algorithms Implemented

### Core Algorithms

- **Howard's Algorithm**: Efficient negative cycle detection using policy iteration
- **Bellman-Ford**: Shortest paths with negative edge weights
- **Parametric Optimization**: Generic framework for ratio-based objectives
- **Cycle Ratio**: Find cycles with minimum/maximum cost/time ratios

### Data Structures

- **TinyDiGraph**: Memory-efficient directed graph for fixed-size node sets
- **DiGraphAdapter**: NetworkX compatibility layer with custom storage
- **MapAdapter**: List-based dictionary for O(1) node/edge access

## Documentation

Full API documentation is available at [https://digraphx.readthedocs.io/](https://digraphx.readthedocs.io/)

## Testing

Run's test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tiny_digraph.py

# Run with coverage
pytest --cov=digraphx --cov-report=html
```

## Development

```bash
# Install development dependencies
pip install -e ".[testing]"

# Run linting
pre-commit run --all-files

# Format code
black src/digraphx tests
isort src/digraphx tests

# Build package
tox -e build
```

## Contributing

Contributions are welcome! Please ensure:
- All tests pass
- Code follows the project's style guidelines (see AGENTS.md)
- New features include tests and documentation
- Pre-commit hooks pass before pushing

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details.

## Acknowledgments

Built on top of [NetworkX](https://networkx.org/)
Uses [PyScaffold](https://pyscaffold.org/) for project structure

## Contact

- Author: Wai-Shing Luk
- Email: luk036@gmail.com
- GitHub: [@luk036](https://github.com/luk036)

## Citation

If you use digraphx in your research, please cite:

```
@software{digraphx,
  title = {digraphx: Directed Graph X in Python},
  author = {Luk, Wai-Shing},
  url = {https://github.com/luk036/digraphx},
  year = {2026}
}
```

<!-- pyscaffold-notes -->
