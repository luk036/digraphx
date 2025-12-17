# digraphx C++ Library

A C++23 implementation of the digraphx Python library for directed graph optimization algorithms.

## Features

- **TinyDiGraph**: Lightweight directed graph implementation optimized for performance
- **Negative Cycle Detection**: Howard's method for finding negative cycles in directed graphs
- **Minimum Cycle Ratio**: Solver for finding cycles with minimum ratio of cost to time
- **Parametric Network Optimization**: Solvers for parametric network problems
- **C++23 Modern Features**: Concepts, ranges, coroutines (via cppcoro)

## Requirements

- C++23 compatible compiler (GCC 11+, Clang 14+, MSVC 2022+)
- [cppcoro](https://github.com/lewissbaker/cppcoro) (included in `include/cppcoro/`)
- [doctest](https://github.com/doctest/doctest) (for testing, automatically downloaded)

## Building

### Using CMake

```bash
mkdir build && cd build
cmake .. -DCMAKE_CXX_STANDARD=23
cmake --build .
```

### Using xmake

```bash
xmake
```

## Project Structure

```
cpp_ai/
├── include/digraphx/     # Public headers
│   ├── types.hpp         # Core types and concepts
│   ├── tiny_digraph.hpp  # Lightweight directed graph
│   ├── neg_cycle.hpp     # Negative cycle finder
│   ├── neg_cycle_q.hpp   # Negative cycle finder with predecessor/successor variants
│   ├── parametric.hpp    # Parametric API and solver
│   ├── min_cycle_ratio.hpp  # Minimum cycle ratio solver
│   └── min_parmetric_q.hpp  # Minimum parametric solver with constraints
├── src/                  # Implementation files
├── tests/                # doctest-based tests
├── examples/             # Usage examples
├── CMakeLists.txt        # CMake build configuration
└── xmake.lua            # xmake build configuration
```

## Quick Start

```cpp
#include "digraphx/tiny_digraph.hpp"
#include "digraphx/neg_cycle.hpp"
#include <iostream>

int main() {
    using namespace digraphx;
    
    // Create a graph
    TinyDiGraph<int, std::string> gr;
    gr.init_nodes({0, 1, 2, 3, 4});
    
    // Add edges
    gr.add_edge(0, 1, "edge_0_1");
    gr.add_edge(1, 2, "edge_1_2");
    gr.add_edge(2, 0, "edge_2_0");  // Creates a cycle
    
    std::cout << "Graph has " << gr.number_of_nodes() << " nodes\n";
    std::cout << "Graph has " << gr.number_of_edges() << " edges\n";
    
    // Find negative cycles (with weights)
    TinyDiGraph<std::string, int> weighted_graph;
    weighted_graph.init_nodes({"A", "B", "C"});
    weighted_graph.add_edge("A", "B", 1);
    weighted_graph.add_edge("B", "C", 2);
    weighted_graph.add_edge("C", "A", -4);  // Negative cycle
    
    // Convert to Digraph format
    Digraph<std::string, int> digraph;
    for (const auto& node : weighted_graph.nodes()) {
        for (const auto& [neighbor, edge] : weighted_graph.neighbors(node)) {
            digraph[node][neighbor] = edge;
        }
    }
    
    // Find negative cycles
    NegCycleFinder<std::string, int, int> finder(digraph);
    DistanceMap<std::string, int> dist{{"A", 0}, {"B", 1000}, {"C", 1000}};
    
    auto get_weight = [](const int& edge) { return edge; };
    
    for (const auto& cycle : finder.howard(dist, get_weight)) {
        std::cout << "Found negative cycle with " << cycle.size() << " edges\n";
    }
    
    return 0;
}
```

## Algorithms

### 1. TinyDiGraph
A memory-efficient directed graph implementation using vectors and hash maps.

### 2. NegCycleFinder
Implements Howard's method for negative cycle detection using Bellman-Ford relaxation.

### 3. MinCycleRatioSolver
Finds the cycle with minimum ratio of total cost to total time.

### 4. Parametric Solvers
- `MaxParametricSolver`: Finds maximum ratio satisfying constraints
- `MinParametricQSolver`: Minimum parametric solver with constraints

## Type Requirements

The library uses C++20 concepts to enforce type requirements:

- **Node**: Must be hashable, copyable, and equality comparable
- **Edge**: Must be copyable and equality comparable
- **Domain**: Must support arithmetic operations and comparisons
- **RatioType**: Extends Domain with numerator/denominator access

## Testing

Tests use the [doctest](https://github.com/doctest/doctest) framework:

```bash
# Run tests with CMake
cd build && ctest

# Run tests with xmake
xmake build digraphx_tests
```

## License

MIT License - see LICENSE file in the parent directory.

## References

- Original Python implementation: [luk036/digraphx](https://github.com/luk036/digraphx)
- Howard's algorithm for negative cycle detection
- Bellman-Ford algorithm
- Parametric network optimization theory