# Gemini Code Assistant Context

## Project Overview

This project, `digraphx`, is a Python library for network optimization on directed graphs. It provides algorithms for finding minimum cycle ratios, solving parametric network problems, and detecting negative cycles using Howard's algorithm. The library is built on top of `networkx` but includes a custom `TinyDiGraph` data structure for improved memory efficiency with large graphs.

The project is structured as a standard Python library using a `src` layout and is configured with `setup.cfg` and `pyproject.toml`.

### Key Technologies

*   **Language:** Python
*   **Core Library:** `networkx`
*   **Testing:** `pytest`, `pytest-cov`, `tox`
*   **Code Style:** `flake8`, `pre-commit`

### Core Modules

*   `min_cycle_ratio.py`: Implements the Minimum Cycle Ratio (MCR) solver.
*   `parametric.py` & `min_parmetric_q.py`: Implements solvers for parametric network problems.
*   `neg_cycle.py` & `neg_cycle_q.py`: Implements negative cycle detection using Howard's algorithm.
*   `tiny_digraph.py`: Defines a memory-efficient `TinyDiGraph` data structure.

## Building and Running

This is a library, so there is no main application to run. However, you can install it and run tests.

### Installation

To install the project in editable mode, use the following command:

```bash
pip install -e .
```

### Running Tests

The project uses `pytest` for testing. To run the tests, use the following command:

```bash
pytest
```

You can also use `tox` to run tests in different Python environments:

```bash
tox
```

## Development Conventions

### Code Style

The project uses `flake8` for linting and `pre-commit` to enforce code style. Before committing any changes, make sure to run `pre-commit`:

```bash
pre-commit run --all-files
```

### Testing

All new features should be accompanied by tests. The tests are located in the `tests` directory and follow the standard `pytest` conventions.

### Contribution Guidelines

The `CONTRIBUTING.md` file provides guidelines for contributing to the project. Please review it before making any contributions.
