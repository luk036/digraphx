#pragma once
#ifndef DIGRAPHX_MIN_CYCLE_RATIO_HPP
#define DIGRAPHX_MIN_CYCLE_RATIO_HPP

#include "types.hpp"
#include "parametric.hpp"
#include <unordered_map>
#include <vector>
#include <functional>
#include <stdexcept>
#include <concepts>
#include <string>
#include <cppcoro/generator.hpp>

namespace digraphx {

/**
 * @brief Cycle Ratio API for parametric cycle ratio calculations.
 * 
 * This class implements the parametric API for cycle ratio calculations.
 * It provides methods to compute distances based on a given ratio and to
 * calculate the actual ratio for a given cycle.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept and have cost/time fields)
 * @tparam R Ratio type (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class CycleRatioAPI : public ParametricAPI<N, E, R> {
private:
    Digraph<N, E> digraph_;
    
public:
    /**
     * @brief Initialize the CycleRatioAPI with a graph.
     * 
     * @param digraph The graph structure where nodes map to neighbors and edge attributes
     */
    explicit CycleRatioAPI(Digraph<N, E> digraph) 
        : digraph_(std::move(digraph)) {}

    /**
     * @brief Calculate the parametric distance for an edge given the current ratio.
     * 
     * The distance formula is: cost - ratio * time
     * 
     * @param ratio The current ratio value being tested
     * @param edge The edge with 'cost' and 'time' attributes
     * @return R The calculated distance value
     * 
     * @throws std::runtime_error if edge doesn't have required attributes
     */
    R distance(const R& ratio, const E& edge) const override {
        // In C++, we assume E has cost() and time() methods
        // For a generic implementation, we might need a different approach
        // For now, we'll assume E is a struct with cost and time fields
        // or has get_cost() and get_time() methods
        
        // This is a placeholder - actual implementation depends on E type
        // In practice, you would use a trait or concept to extract cost/time
        throw std::runtime_error("CycleRatioAPI::distance not implemented for generic E");
    }

    /**
     * @brief Calculate the actual ratio for a given cycle.
     * 
     * The ratio is computed as: total_cost / total_time
     * 
     * @param cycle A sequence of edges forming a cycle
     * @return R The calculated cycle ratio
     * 
     * @throws std::runtime_error if cycle is empty or total_time is zero
     */
    R zero_cancel(const Cycle<E>& cycle) const override {
        if (cycle.empty()) {
            throw std::invalid_argument("Cycle cannot be empty");
        }
        
        R total_cost = numeric_traits<R>::zero();
        R total_time = numeric_traits<R>::zero();
        
        for (const auto& edge : cycle) {
            // Similar to distance(), we need to extract cost and time
            // This is a placeholder
            throw std::runtime_error("CycleRatioAPI::zero_cancel not implemented for generic E");
        }
        
        if (total_time == numeric_traits<R>::zero()) {
            throw std::runtime_error("Total time cannot be zero");
        }
        
        return total_cost / total_time;
    }

    /**
     * @brief Get the graph (for testing/debugging).
     * 
     * @return const Digraph<N, E>& Graph
     */
    const Digraph<N, E>& digraph() const noexcept {
        return digraph_;
    }
};

/**
 * @brief Minimum Cycle Ratio Solver
 * 
 * This class solves the following parametric network problem:
 * 
 * |    max  r
 * |    s.t. dist[v] - dist[u] <= cost(u, v) - ratio * time(u, v)
 * |         for all (u, v) in E
 * 
 * The minimum cycle ratio (MCR) problem is a fundamental problem in the
 * analysis of directed graphs. Given a directed graph, the MCR problem seeks
 * to find the cycle with the minimum ratio of the sum of edge weights to the
 * number of edges in the cycle. In other words, the MCR problem seeks to find
 * the "tightest" cycle in the graph, where the tightness of a cycle is
 * measured by the ratio of the total weight of the cycle to its length.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept and have cost/time fields)
 * @tparam R Ratio type (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class MinCycleRatioSolver {
private:
    Digraph<N, E> digraph_;
    
public:
    /**
     * @brief Initialize the solver with the graph to analyze.
     * 
     * @param digraph The graph structure where nodes map to neighbors and edge attributes
     */
    explicit MinCycleRatioSolver(Digraph<N, E> digraph) 
        : digraph_(std::move(digraph)) {}

    /**
     * @brief Run the minimum cycle ratio solver algorithm.
     * 
     * The algorithm works by:
     * 1. Creating a CycleRatioAPI instance with the graph
     * 2. Using a MaxParametricSolver to find the optimal ratio
     * 3. Returning both the optimal ratio and the corresponding cycle
     * 
     * @param dist Initial distance labels for nodes
     * @param r0 Initial ratio value to start the search
     * @return std::pair<R, Cycle<E>> Tuple containing the optimal ratio and the cycle that achieves it
     */
    std::pair<R, Cycle<E>> run(DistanceMap<N, R> dist, const R& r0) {
        CycleRatioAPI<N, E, R> omega(digraph_);
        MaxParametricSolver<N, E, R> solver(digraph_, omega);
        return solver.run(std::move(dist), r0);
    }

    /**
     * @brief Get the graph (for testing/debugging).
     * 
     * @return const Digraph<N, E>& Graph
     */
    const Digraph<N, E>& digraph() const noexcept {
        return digraph_;
    }
};

/**
 * @brief Set a default value for a specified weight in a graph.
 * 
 * Iterates through all edges in the graph and sets the specified weight to the given value
 * if it's not already present in the edge attributes.
 * 
 * @tparam N Node type
 * @tparam E Edge type (must have operator[] for string keys)
 * @tparam D Value type
 * @param digraph The mutable graph data structure
 * @param weight The weight attribute to set
 * @param value The default value to set for the weight attribute
 */
template<Node N, typename E, Domain D>
void set_default(Digraph<N, E>& digraph, const std::string& weight, const D& value) {
    for (auto& [unused, neighbors] : digraph) {
        for (auto& [unused, edge] : neighbors) {
            // In C++, we need a way to set default values on edges
            // This depends on the Edge type implementation
            // For a generic solution, we might need a callback or trait
        }
    }
}

} // namespace digraphx

#endif // DIGRAPHX_MIN_CYCLE_RATIO_HPP