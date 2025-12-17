#pragma once
#ifndef DIGRAPHX_MIN_PARAMETRIC_Q_HPP
#define DIGRAPHX_MIN_PARAMETRIC_Q_HPP

#include "types.hpp"
#include "neg_cycle_q.hpp"
#include <unordered_map>
#include <vector>
#include <functional>
#include <stdexcept>
#include <concepts>
#include <memory>

namespace digraphx {

/**
 * @brief Minimum Parametric API trait for distance calculation and cycle analysis.
 * 
 * This trait defines an interface for calculating distances and handling cycles,
 * allowing for different implementations of these operations.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam R Ratio type (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class MinParametricAPI {
public:
    virtual ~MinParametricAPI() = default;
    
    /**
     * @brief Calculate the parametric distance for an edge given the current ratio.
     * 
     * @param ratio The current ratio value being tested
     * @param edge The edge to calculate distance for
     * @return R The calculated distance value
     */
    virtual R distance(const R& ratio, const E& edge) const = 0;
    
    /**
     * @brief Calculate the actual ratio for a given cycle.
     * 
     * @param cycle A sequence of edges forming a cycle
     * @return R The calculated cycle ratio
     */
    virtual R zero_cancel(const Cycle<E>& cycle) const = 0;
};

/**
 * @brief Minimum Parametric Solver with constraints
 * 
 * This struct solves a specific type of network optimization problem called a
 * "minimum parametric problem." It finds the smallest possible value for a
 * parameter (called a ratio) that satisfies certain conditions in a graph.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam R Ratio type (must satisfy RatioType concept)
 * @tparam API Parametric API type (must satisfy MinParametricAPI concept)
 */
template<Node N, Edge E, RatioType R, typename API>
requires std::derived_from<API, MinParametricAPI<N, E, R>>
class MinParametricQSolver {
private:
    Digraph<N, E> digraph_;
    API omega_;
    
public:
    /**
     * @brief Initialize the solver with a graph and a parametric API.
     * 
     * @param digraph A mapping of nodes to a mapping of nodes to edges
     * @param omega A parametric API instance that provides methods for distance
     *              calculation and cycle analysis
     */
    MinParametricQSolver(Digraph<N, E> digraph, API omega)
        : digraph_(std::move(digraph))
        , omega_(std::move(omega)) {}

    /**
     * @brief Run the minimum parametric solver algorithm.
     * 
     * The algorithm works by:
     * 1. Starting with an initial ratio and distance estimates
     * 2. Using a negative cycle finder to find cycles in the graph
     * 3. For each cycle found, calculating a new ratio
     * 4. Updating the minimum ratio if a smaller one is found
     * 5. Repeating until no better ratio can be found
     * 
     * The algorithm can switch between searching for cycles in the forward
     * direction (successor nodes) and the backward direction (predecessor nodes).
     * 
     * @param dist Initial distance labels for nodes
     * @param ratio Initial ratio value to start the search
     * @param use_succ Whether to use successor relaxation (true) or predecessor relaxation (false)
     * @return std::pair<R, Cycle<E>> Tuple containing the optimal ratio and the cycle that achieves it
     */
    std::pair<R, Cycle<E>> run(DistanceMap<N, R> dist, const R& ratio, bool use_succ = true) {
        R r_min = ratio;
        Cycle<E> c_min;
        R current_ratio = ratio;
        
        NegCycleFinderQ<N, E, R> ncf(digraph_);
        
        while (true) {
            auto get_weight = [this, &current_ratio](const E& e) {
                return omega_.distance(current_ratio, e);
            };
            
            std::vector<Cycle<E>> cycles;
            if (use_succ) {
                auto cycle_gen = ncf.howard_succ(dist, get_weight);
                for (const auto& cycle : cycle_gen) {
                    cycles.push_back(cycle);
                }
            } else {
                auto cycle_gen = ncf.howard_pred(dist, get_weight);
                for (const auto& cycle : cycle_gen) {
                    cycles.push_back(cycle);
                }
            }
            
            bool found_better = false;
            for (const auto& cycle : cycles) {
                R ri = omega_.zero_cancel(cycle);
                
                if (ri < r_min) {
                    r_min = ri;
                    c_min = cycle;
                    found_better = true;
                }
            }
            
            if (!found_better) {
                break;
            }
            
            current_ratio = r_min;
        }
        
        return std::make_pair(ratio, c_min);
    }

    /**
     * @brief Get the graph (for testing/debugging).
     * 
     * @return const Digraph<N, E>& Graph
     */
    const Digraph<N, E>& digraph() const noexcept {
        return digraph_;
    }

    /**
     * @brief Get the parametric API (for testing/debugging).
     * 
     * @return const API& Parametric API
     */
    const API& omega() const noexcept {
        return omega_;
    }
};

} // namespace digraphx

#endif // DIGRAPHX_MIN_PARAMETRIC_Q_HPP