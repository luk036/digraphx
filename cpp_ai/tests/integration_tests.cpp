#include <doctest/doctest.h>
#include "digraphx/tiny_digraph.hpp"
#include "digraphx/neg_cycle.hpp"
#include <unordered_map>
#include <vector>
#include <string>

TEST_CASE("Integration tests for digraphx library") {
    using namespace digraphx;

    SUBCASE("TinyDiGraph and NegCycleFinder integration") {
        // Create a graph using TinyDiGraph
        TinyDiGraph<int, int> gr;
        gr.init_nodes({0, 1, 2, 3});

        // Add edges with weights
        gr.add_edge(0, 1, 2);   // weight 2
        gr.add_edge(1, 2, 3);   // weight 3
        gr.add_edge(2, 3, 1);   // weight 1
        gr.add_edge(3, 0, -7);  // weight -7 (creates negative cycle)

        // Convert TinyDiGraph to Digraph format for NegCycleFinder
        Digraph<int, int> digraph;
        for (const auto& node : gr.nodes()) {
            for (const auto& [neighbor, edge] : gr.neighbors(node)) {
                digraph[node][neighbor] = edge;
            }
        }

        // Create NegCycleFinder
        NegCycleFinder<int, int, int> finder(digraph);
        DistanceMap<int, int> dist;
        dist[0] = 0;
        dist[1] = 1000;
        dist[2] = 1000;
        dist[3] = 1000;

        auto get_weight = [](const int& edge) { return edge; };

        // Find negative cycles
        std::vector<Cycle<int>> cycles;
        for (const auto& cycle : finder.howard(dist, get_weight)) {
            cycles.push_back(cycle);
        }

        // Should find at least one negative cycle (0->1->2->3->0: 2+3+1-7 = -1)
        CHECK(cycles.size() > 0);

        if (!cycles.empty()) {
            const auto& cycle = cycles[0];
            int cycle_sum = 0;
            for (const auto& edge : cycle) {
                cycle_sum += edge;
            }
            CHECK(cycle_sum < 0);  // Negative cycle
        }
    }

    SUBCASE("Complex graph with multiple cycles") {
        TinyDiGraph<std::string, double> gr;
        gr.init_nodes({"A", "B", "C", "D", "E"});

        // Create a more complex graph
        gr.add_edge("A", "B", 1.5);
        gr.add_edge("B", "C", 2.0);
        gr.add_edge("C", "D", 1.0);
        gr.add_edge("D", "E", 3.0);
        gr.add_edge("E", "A", -8.0);  // Negative cycle A->B->C->D->E->A

        // Also add another cycle
        gr.add_edge("C", "A", -4.0);  // Another negative edge

        // Convert to Digraph
        Digraph<std::string, double> digraph;
        for (const auto& node : gr.nodes()) {
            for (const auto& [neighbor, edge] : gr.neighbors(node)) {
                digraph[node][neighbor] = edge;
            }
        }

        // Create NegCycleFinder
        NegCycleFinder<std::string, double, double> finder(digraph);
        DistanceMap<std::string, double> dist;
        for (const auto& node : gr.nodes()) {
            dist[node] = 0.0;
        }

        auto get_weight = [](const double& edge) { return edge; };

        // Find negative cycles
        std::vector<Cycle<double>> cycles;
        for (const auto& cycle : finder.howard(dist, get_weight)) {
            cycles.push_back(cycle);
        }

        // Should find negative cycles
        CHECK(cycles.size() > 0);

        // Verify all found cycles are negative
        for (const auto& cycle : cycles) {
            double cycle_sum = 0.0;
            for (const auto& edge : cycle) {
                cycle_sum += edge;
            }
            CHECK(cycle_sum < 0.0);
        }
    }

    SUBCASE("Graph with no negative cycles") {
        TinyDiGraph<int, int> gr;
        gr.init_nodes({0, 1, 2});

        // All positive edges - no negative cycles
        gr.add_edge(0, 1, 1);
        gr.add_edge(1, 2, 2);
        gr.add_edge(2, 0, 3);  // Cycle sum: 1+2+3 = 6 (positive)

        // Convert to Digraph
        Digraph<int, int> digraph;
        for (const auto& node : gr.nodes()) {
            for (const auto& [neighbor, edge] : gr.neighbors(node)) {
                digraph[node][neighbor] = edge;
            }
        }

        // Create NegCycleFinder
        NegCycleFinder<int, int, int> finder(digraph);
        DistanceMap<int, int> dist;
        dist[0] = 0;
        dist[1] = 1000;
        dist[2] = 1000;

        auto get_weight = [](const int& edge) { return edge; };

        // Find negative cycles
        std::vector<Cycle<int>> cycles;
        for (const auto& cycle : finder.howard(dist, get_weight)) {
            cycles.push_back(cycle);
        }

        // Should find no negative cycles (but might find the positive cycle)
        // The algorithm might still return cycles, but they won't be negative
        bool found_negative = false;
        for (const auto& cycle : cycles) {
            int cycle_sum = 0;
            for (const auto& edge : cycle) {
                cycle_sum += edge;
            }
            if (cycle_sum < 0) {
                found_negative = true;
                break;
            }
        }
        CHECK(found_negative == false);
    }
}
