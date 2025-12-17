#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>
#include "digraphx/neg_cycle.hpp"
#include <unordered_map>
#include <vector>
#include <string>

TEST_CASE("NegCycleFinder basic operations") {
    using namespace digraphx;
    
    SUBCASE("Default construction with empty graph") {
        Digraph<std::string, int> digraph;
        NegCycleFinder<std::string, int, int> finder(digraph);
        
        // Should compile and create successfully
        CHECK(true);
    }
    
    SUBCASE("Relax operation on simple graph") {
        Digraph<std::string, int> digraph;
        
        // Create a simple graph: a -> b (weight 1), b -> c (weight 2), c -> a (weight -5)
        digraph["a"]["b"] = 1;
        digraph["a"]["c"] = 4;
        digraph["b"]["c"] = 2;
        digraph["c"]["a"] = -5;
        
        NegCycleFinder<std::string, int, int> finder(digraph);
        DistanceMap<std::string, int> dist;
        dist["a"] = 0;
        dist["b"] = 1000;  // Large initial distance
        dist["c"] = 1000;
        
        auto get_weight = [](const int& edge) { return edge; };
        
        bool changed = finder.relax(dist, get_weight);
        CHECK(changed == true);
        CHECK(dist["b"] == 1);
        CHECK(dist["c"] == 3);  // min(4, 1+2)
    }
    
    SUBCASE("Cycle list reconstruction") {
        Digraph<std::string, std::string> digraph;
        NegCycleFinder<std::string, std::string, int> finder(digraph);
        
        // Manually set up a cycle: a -> b -> c -> a
        auto& pred = const_cast<std::unordered_map<std::string, std::pair<std::string, std::string>>&>(finder.pred());
        pred["b"] = {"a", "ab"};
        pred["c"] = {"b", "bc"};
        pred["a"] = {"c", "ca"};
        
        auto cycle = finder.cycle_list("a");
        REQUIRE(cycle.size() == 3);
        CHECK(cycle[0] == "ca");
        CHECK(cycle[1] == "bc");
        CHECK(cycle[2] == "ab");
    }
    
    SUBCASE("Check if cycle is negative") {
        Digraph<std::string, int> digraph;
        NegCycleFinder<std::string, int, int> finder(digraph);
        
        // Manually set up a cycle with weights: a->b(1), b->c(1), c->a(-3)
        auto& pred = const_cast<std::unordered_map<std::string, std::pair<std::string, int>>&>(finder.pred());
        pred["b"] = {"a", 1};
        pred["c"] = {"b", 1};
        pred["a"] = {"c", -3};
        
        DistanceMap<std::string, int> dist;
        dist["a"] = 0;
        dist["b"] = 1;
        dist["c"] = 2;
        
        auto get_weight = [](const int& edge) { return edge; };
        
        bool is_neg = finder.is_negative("a", dist, get_weight);
        CHECK(is_neg == true);  // Cycle sum: 1 + 1 - 3 = -1 (negative)
    }
    
    SUBCASE("Howard algorithm on graph with negative cycle") {
        Digraph<std::string, int> digraph;
        
        // Create a graph with a negative cycle: a->b(1), b->c(2), c->a(-4)
        digraph["a"]["b"] = 1;
        digraph["b"]["c"] = 2;
        digraph["c"]["a"] = -4;
        
        NegCycleFinder<std::string, int, int> finder(digraph);
        DistanceMap<std::string, int> dist;
        dist["a"] = 0;
        dist["b"] = 1000;
        dist["c"] = 1000;
        
        auto get_weight = [](const int& edge) { return edge; };
        
        // Collect cycles from generator
        std::vector<Cycle<int>> cycles;
        for (const auto& cycle : finder.howard(dist, get_weight)) {
            cycles.push_back(cycle);
        }
        
        // Should find at least one negative cycle
        CHECK(cycles.size() > 0);
        
        // Verify the cycle has the correct edges
        if (!cycles.empty()) {
            const auto& cycle = cycles[0];
            // The cycle should contain edges 1, 2, -4 in some order
            bool found1 = false, found2 = false, foundNeg4 = false;
            for (const auto& edge : cycle) {
                if (edge == 1) found1 = true;
                if (edge == 2) found2 = true;
                if (edge == -4) foundNeg4 = true;
            }
            CHECK(found1);
            CHECK(found2);
            CHECK(foundNeg4);
        }
    }
    
    SUBCASE("Exception handling") {
        Digraph<std::string, int> digraph;
        NegCycleFinder<std::string, int, int> finder(digraph);
        
        SUBCASE("Cycle list with invalid node") {
            CHECK_THROWS_AS(finder.cycle_list("nonexistent"), std::runtime_error);
        }
        
        SUBCASE("Is negative with invalid node") {
            DistanceMap<std::string, int> dist;
            auto get_weight = [](const int& edge) { return edge; };
            CHECK_THROWS_AS(finder.is_negative("nonexistent", dist, get_weight), std::runtime_error);
        }
    }
}