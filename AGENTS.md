# AGENTS.md

This file guides agentic coding assistants working in the digraphx repository.

## Build / Lint / Test Commands

```bash
# Run all tests with coverage
pytest

# Run single test file
pytest tests/test_tiny_digraph.py

# Run specific test
pytest tests/test_tiny_digraph.py::test_tiny_digraph

# Run tests matching pattern
pytest -k "tiny_digraph"

# Build package
tox -e build

# Run linting (pre-commit)
pre-commit run --all-files

# Run specific lint tools
black src/digraphx tests
isort src/digraphx tests
flake8 src/digraphx tests
```

**Testing Notes:**
- Tests located in `tests/` directory
- Pytest configured in `setup.cfg` with coverage enabled
- Fixtures defined in `tests/conftest.py`
- Use `-k` flag to run tests matching name pattern

## Code Style Guidelines

### Formatting
- **Line length**: 256 characters (flake8 config)
- **Formatter**: Black (auto-enforced via pre-commit)
- **Import sorting**: isort (auto-enforced via pre-commit)
- **Linting**: flake8 with E203, W503 ignored (Black-compatible)

### Type Hints
- **Required**: All functions must use type hints
- **Imports**: Use `from typing import List, Dict, Set, Tuple, Optional, Union, Generic, TypeVar, Callable, Mapping, MutableMapping, Iterator, Generator`
- **Generic types**: Use TypeVar for generic classes (e.g., `Node = TypeVar("Node")`)
- **External deps**: Use `# type: ignore` for missing stub files (e.g., `from mywheel.map_adapter import MapAdapter  # type: ignore`)

### Naming Conventions
- **Classes**: PascalCase (TinyDiGraph, NegCycleFinder, MinCycleRatioSolver)
- **Functions/methods**: snake_case (init_nodes, find_cycle, howard)
- **Constants**: UPPER_SNAKE_CASE (WEIGHT_0_1, SELF_LOOP_WEIGHT, NUM_NODES)
- **Private methods**: underscore prefix (`_helper_function`)
- **Type aliases**: PascalCase or short caps (Node, Edge, Domain, Cycle)

### Documentation
- **Docstrings**: Required for all public classes and methods
- **Style**: Google-style with Args, Returns, Examples sections
- **Examples**: Include doctest-style examples for key methods
- **Module docstrings**: Describe purpose, inputs, outputs, algorithms used

### Error Handling
- Use type annotations for validation (e.g., `Mapping[Node, Edge]`)
- Avoid empty catch blocks
- Use pytest.raises for testing expected exceptions
- Raise specific exceptions (NotImplementedError, ValueError, TypeError)

### Import Style
```python
# Standard library imports first
from fractions import Fraction
from typing import List, Dict, TypeVar

# Third-party imports second
import networkx as nx

# Local imports third (relative preferred within package)
from .neg_cycle import NegCycleFinder
from digraphx.tiny_digraph import TinyDiGraph
```

### Code Patterns
- Use generics for reusable components: `class Solver(Generic[Node, Edge, Ratio]):`
- Prefer composition over inheritance
- Use generators for large sequences: `def find_cycle() -> Generator[Node, None, None]:`
- Use dataclasses or named tuples for structured data
- Mutable and immutable types: Separate Mapping (immutable) from MutableMapping (mutable)

### Graph-Specific Conventions
- Node identifiers: Generic hashable types (int, str, tuple)
- Edge data: MutableMapping[str, Any] for attributes
- Use NetworkX DiGraph patterns extended with custom storage
- Separate graph structure from algorithms (adapter pattern)
- Use fractional arithmetic for exact ratios (from fractions import Fraction)

## Project Structure
```
src/digraphx/          # Main package
├── __init__.py        # Version info, exports
├── tiny_digraph.py    # Graph data structures
├── neg_cycle.py       # Negative cycle algorithms
├── parametric.py      # Parametric solver framework
└── min_cycle_ratio.py # Minimum cycle ratio solver

tests/                 # Test suite
├── conftest.py        # Shared fixtures
└── test_*.py          # Test files

setup.cfg              # Package config, pytest options
pyproject.toml         # Build config
.pre-commit-config.yaml # Linting hooks
```

## Dependencies
- **networkx**: Graph library base
- **luk036/mywheel**: Custom utilities (MapAdapter)
- Testing: pytest, pytest-cov
- Development: black, isort, flake8, pre-commit

## Key Algorithms
- **Howard's algorithm**: Negative cycle detection
- **Bellman-Ford**: Shortest paths with negative edges
- **Parametric optimization**: Maximize/minimize ratio-based objectives
- **Cycle ratio**: Find cycle with minimum/maximum cost/time ratio
