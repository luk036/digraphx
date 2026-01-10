// Basic usage example for digraphx C++ library
#include "digraphx/tiny_digraph.hpp"
#include "digraphx/neg_cycle.hpp"
#include <iostream>
#include <vector>
#include <string>

int main() {
    using namespace digraphx;

    std::cout << "=== TinyDiGraph Example ===\n";

    // Create a new TinyDiGraph
    TinyDiGraph<int, std::string> gr;

    // Initialize with 5 nodes
    gr.init_nodes({0, 1, 2, 3, 4});
    std::cout << "Created graph with " << gr.number_of_nodes() << " nodes\n";

    // Add some edges
    gr.add_edge(0, 1, "edge_0_1");
    gr.add_edge(1, 2, "edge_1_2");
    gr.add_edge(2, 3, "edge_2_3");
    gr.add_edge(3, 4, "edge_3_4");
    gr.add_edge(4, 0, "edge_4_0");

    std::cout << "Added " << gr.number_of_edges() << " edges\n";

    // List all nodes
    std::cout << "\nNodes:\n";
    for (const auto& node : gr.nodes()) {
        std::cout << "  " << node << "\n";
    }

    // List all edges
    std::cout << "\nEdges:\n";
    for (const auto& [u, v, edge] : gr.edges()) {
        std::cout << "  " << u << " -> " << v << ": " << edge << "\n";
    }

    // Show neighbors of node 0
    std::cout << "\nNeighbors of node 0:\n";
    for (const auto& [neighbor, edge] : gr.neighbors(0)) {
        std::cout << "  -> " << neighbor << " via " << edge << "\n";
    }

    // Show predecessors of node 0
    std::cout << "\nPredecessors of node 0:\n";
    for (const auto& [predecessor, edge] : gr.predecessors(0)) {
        std::cout << "  <- " << predecessor << " via " << edge << "\n";
    }

    // Add node attributes
    std::cout << "\nAdding node attributes...\n";
    auto& attrs0 = gr.node_attributes_mut(0);
    attrs0["color"] = "red";
    attrs0["weight"] = "10";

    auto& attrs1 = gr.node_attributes_mut(1);
    attrs1["color"] = "blue";

    // Show node attributes
    std::cout << "Node 0 attributes:\n";
    for (const auto& [key, value] : gr.node_attributes(0)) {
        std::cout << "  " << key << ": " << value << "\n";
    }

    std::cout << "\n=== Negative Cycle Detection Example ===\n";

    // Create a graph with a negative cycle
    TinyDiGraph<std::string, int> weighted_graph;
    weighted_graph.init_nodes({"A", "B", "C"});

    // Add edges with weights (creating a negative cycle)
    weighted_graph.add_edge("A", "B", 1);
    weighted_graph.add_edge("B", "C", 2);
    weighted_graph.add_edge("C", "A", -4);  // This creates a negative cycle

    // Convert to Digraph format for NegCycleFinder
    Digraph<std::string, int> digraph;
    for (const auto& node : weighted_graph.nodes()) {
        for (const auto& [neighbor, edge] : weighted_graph.neighbors(node)) {
            digraph[node][neighbor] = edge;
        }
    }

    // Create NegCycleFinder
    NegCycleFinder<std::string, int, int> finder(digraph);
    DistanceMap<std::string, int> dist;
    dist["A"] = 0;
    dist["B"] = 1000;
    dist["C"] = 1000;

    auto get_weight = [](const int& edge) { return edge; };

    // Find negative cycles
    std::cout << "\nSearching for negative cycles...\n";
    int cycle_count = 0;
    for (const auto& cycle : finder.howard(dist, get_weight)) {
        ++cycle_count;
        std::cout << "Found cycle #" << cycle_count << " with " << cycle.size() << " edges\n";

        int cycle_sum = 0;
        std::cout << "  Edges: ";
        for (const auto& edge : cycle) {
            std::cout << edge << " ";
            cycle_sum += edge;
        }
        std::cout << "\n  Cycle sum: " << cycle_sum << " (";
        if (cycle_sum < 0) {
            std::cout << "negative";
        } else if (cycle_sum > 0) {
            std::cout << "positive";
        } else {
            std::cout << "zero";
        }
        std::cout << ")\n";
    }

    if (cycle_count == 0) {
        std::cout << "No negative cycles found\n";
    }

    std::cout << "\n=== Example completed successfully ===\n";
    return 0;
}
