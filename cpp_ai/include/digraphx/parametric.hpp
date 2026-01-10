#pragma once
#ifndef DIGRAPHX_PARAMETRIC_HPP
#define DIGRAPHX_PARAMETRIC_HPP

#include "types.hpp"
#include "neg_cycle.hpp"
#include <unordered_map>
#include <vector>
#include <functional>
#include <stdexcept>
#include <concepts>
#include <memory>
#include <cppcoro/generator.hpp>

namespace digraphx {

/**
 * @brief Parametric API trait for distance calculation and cycle analysis.
 *
 * This trait defines an interface for calculating distances and handling cycles,
 * allowing for different implementations of these operations.
 *
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam R Ratio type (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class ParametricAPI {
public:
    virtual ~ParametricAPI() = default;

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
 * @brief Maximum Parametric Solver
 *
 * This class solves parametric network problems by finding the maximum ratio
 * that satisfies certain constraints in a directed graph.
 *
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam R Ratio type (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class MaxParametricSolver {
private:
    Digraph<N, E> digraph_;
    std::unique_ptr<ParametricAPI<N, E, R>> omega_;

public:
    /**
     * @brief Initialize the solver with a graph and a parametric API.
     *
     * @param digraph A mapping of nodes to a mapping of nodes to edges
     * @param omega A parametric API instance that provides methods for distance
     *              calculation and cycle analysis
     */
    MaxParametricSolver(Digraph<N, E> digraph, const ParametricAPI<N, E, R>& omega)
        : digraph_(std::move(digraph))
        , omega_(std::make_unique<ParametricAPI<N, E, R>>(omega)) {}

    /**
     * @brief Run the maximum parametric solver algorithm.
     *
     * The algorithm works by:
     * 1. Starting with an initial ratio and distance estimates
     * 2. Using a negative cycle finder to find cycles in the graph
     * 3. For each cycle found, calculating a new ratio
     * 4. Updating the maximum ratio if a larger one is found
     * 5. Repeating until no better ratio can be found
     *
     * @param dist Initial distance labels for nodes
     * @param r0 Initial ratio value to start the search
     * @return std::pair<R, Cycle<E>> Tuple containing the optimal ratio and the cycle that achieves it
     */
    std::pair<R, Cycle<E>> run(DistanceMap<N, R> dist, const R& r0) {
        R r_max = r0;
        Cycle<E> c_max;
        R current_ratio = r0;

        NegCycleFinder<N, E, R> ncf(digraph_);

        while (true) {
            auto get_weight = [this, &current_ratio](const E& e) {
                return omega_->distance(current_ratio, e);
            };

            auto cycles = ncf.howard(dist, get_weight);
            bool found_better = false;

            for (const auto& cycle : cycles) {
                R ri = omega_->zero_cancel(cycle);

                if (ri > r_max) {
                    r_max = ri;
                    c_max = cycle;
                    found_better = true;
                }
            }

            if (!found_better) {
                break;
            }

            current_ratio = r_max;
        }

        return std::make_pair(r_max, c_max);
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

} // namespace digraphx

#endif // DIGRAPHX_PARAMETRIC_HPP
