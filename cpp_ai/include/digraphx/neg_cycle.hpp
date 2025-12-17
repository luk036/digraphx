#pragma once
#ifndef DIGRAPHX_NEG_CYCLE_HPP
#define DIGRAPHX_NEG_CYCLE_HPP

#include "types.hpp"
#include <unordered_map>
#include <vector>
#include <functional>
#include <stdexcept>
#include <concepts>
#include <memory>
#include <cppcoro/generator.hpp>

namespace digraphx {

/**
 * @brief Negative Cycle Finder by Howard's method
 * 
 * This class is used to find negative cycles in a given directed graph.
 * It implements the following algorithms:
 * 
 * 1. Bellman-Ford Algorithm: It is a shortest path algorithm that can find
 *    single source shortest paths in a graph with negative edge weights.
 * 2. Howard's Policy Graph Algorithm: It is used to find cycles in a directed
 *    graph and is based on the Bellman-Ford Algorithm.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam D Domain type for distances (must satisfy Domain concept)
 */
template<Node N, Edge E, Domain D>
class NegCycleFinder {
private:
    Digraph<N, E> digraph_;
    std::unordered_map<N, std::pair<N, E>> pred_;
    
public:
    /**
     * @brief Initialize the negative cycle finder with a directed graph.
     * 
     * @param digraph A mapping representing a directed graph where:
     *                - Keys are source nodes
     *                - Values are mappings of destination nodes to edges
     *                Example: {u: {v: edge_uv, w: edge_uw}, v: {u: edge_vu}}
     */
    explicit NegCycleFinder(Digraph<N, E> digraph) 
        : digraph_(std::move(digraph)) {}

    /**
     * @brief Find cycles in the current predecessor graph using depth-first search.
     * 
     * Uses a coloring algorithm (white/gray/black) to detect cycles:
     * - White: unvisited nodes
     * - Gray: nodes being visited in current DFS path
     * - Black: fully visited nodes
     * 
     * @return cppcoro::generator<N> Generator that yields each node that starts a cycle
     */
    cppcoro::generator<N> find_cycle() const {
        std::unordered_map<N, N> visited;
        
        for (const auto& [vtx, _] : digraph_) {
            if (visited.contains(vtx)) {
                continue;
            }
            
            auto utx = vtx;
            visited[utx] = vtx;
            
            while (pred_.contains(utx)) {
                const auto& [pred_node, _] = pred_.at(utx);
                utx = pred_node;
                
                if (visited.contains(utx)) {
                    if (visited[utx] == vtx) {
                        co_yield utx;
                    }
                    break;
                }
                
                visited[utx] = vtx;
            }
        }
    }

    /**
     * @brief Perform one relaxation pass of the Bellman-Ford algorithm.
     * 
     * Updates both distance estimates (dist) and predecessor information
     * (pred) for all edges in the graph following the Bellman-Ford
     * relaxation rule: if dist[v] > dist[u] + weight(u,v), then update
     * dist[v].
     * 
     * @param dist Current shortest distance estimates for each node
     * @param get_weight Function to get weight/cost of an edge
     * @return true if any distance was updated, false otherwise
     */
    bool relax(DistanceMap<N, D>& dist, std::function<D(const E&)> get_weight) {
        bool changed = false;

        for (const auto& [utx, neighbors] : digraph_) {
            D dist_u = dist.contains(utx) ? dist[utx] : numeric_traits<D>::zero();
            
            for (const auto& [vtx, edge] : neighbors) {
                D weight = get_weight(edge);
                D distance = dist_u + weight;
                
                if (!dist.contains(vtx)) {
                    dist[vtx] = numeric_traits<D>::zero();
                }
                
                if (dist[vtx] > distance) {
                    dist[vtx] = distance;
                    pred_[vtx] = std::make_pair(utx, edge);
                    changed = true;
                }
            }
        }

        return changed;
    }

    /**
     * @brief Reconstruct the cycle starting from the given node.
     * 
     * Follows predecessor links until returning to the starting node.
     * 
     * @param handle The starting node of the cycle (must be part of a cycle)
     * @return Cycle<E> List of edges forming the cycle in order
     * 
     * @throws std::runtime_error if node is not in predecessor graph
     */
    Cycle<E> cycle_list(const N& handle) const {
        Cycle<E> cycle;
        N vtx = handle;

        while (true) {
            if (!pred_.contains(vtx)) {
                throw std::runtime_error("Node not in predecessor graph");
            }
            
            const auto& [utx, edge] = pred_.at(vtx);
            cycle.push_back(edge);
            vtx = utx;
            
            if (vtx == handle) {
                break;
            }
        }

        return cycle;
    }

    /**
     * @brief Check if the cycle starting at 'handle' is negative.
     * 
     * A cycle is negative if the sum of its edge weights is negative.
     * This is checked by verifying that for at least one edge (u,v) in the
     * cycle, dist[v] > dist[u] + weight(u,v) (triangle inequality violation).
     * 
     * @param handle Starting node of the cycle to check
     * @param dist Current distance estimates
     * @param get_weight Function to get edge weights
     * @return true if the cycle is negative, false otherwise
     * 
     * @throws std::runtime_error if node is not in predecessor graph
     */
    bool is_negative(const N& handle, const DistanceMap<N, D>& dist, 
                     std::function<D(const E&)> get_weight) const {
        N vtx = handle;

        while (true) {
            if (!pred_.contains(vtx)) {
                throw std::runtime_error("Node not in predecessor graph");
            }
            
            const auto& [utx, edge] = pred_.at(vtx);
            D weight = get_weight(edge);
            
            D dist_v = dist.contains(vtx) ? dist.at(vtx) : numeric_traits<D>::zero();
            D dist_u = dist.contains(utx) ? dist.at(utx) : numeric_traits<D>::zero();
            
            if (dist_v > dist_u + weight) {
                return true;
            }
            
            vtx = utx;
            if (vtx == handle) {
                break;
            }
        }

        return false;
    }

    /**
     * @brief Main algorithm to find negative cycles using Howard's method.
     * 
     * The algorithm:
     * 1. Repeatedly relaxes edges until no more improvements can be made
     * 2. Checks for cycles in the predecessor graph
     * 3. Verifies if found cycles are negative
     * 4. Yields each found negative cycle
     * 
     * @param dist Initial distance estimates (often initialized to zero)
     * @param get_weight Function to get edge weights
     * @return cppcoro::generator<Cycle<E>> Generator that yields found negative cycles
     */
    cppcoro::generator<Cycle<E>> howard(DistanceMap<N, D>& dist, 
                                        std::function<D(const E&)> get_weight) {
        pred_.clear();
        bool found = false;

        while (!found && relax(dist, get_weight)) {
            for (const auto& vtx : find_cycle()) {
                if (is_negative(vtx, dist, get_weight)) {
                    found = true;
                    co_yield cycle_list(vtx);
                }
            }
        }
    }

    /**
     * @brief Get the predecessor map (for testing/debugging).
     * 
     * @return const std::unordered_map<N, std::pair<N, E>>& Predecessor map
     */
    const std::unordered_map<N, std::pair<N, E>>& pred() const noexcept {
        return pred_;
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

#endif // DIGRAPHX_NEG_CYCLE_HPP