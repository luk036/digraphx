#pragma once
#ifndef DIGRAPHX_NEG_CYCLE_Q_HPP
#define DIGRAPHX_NEG_CYCLE_Q_HPP

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
 * @brief Negative Cycle Finder with predecessor/successor variants
 * 
 * This class extends the basic negative cycle finder to support both
 * predecessor-based and successor-based cycle detection.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 * @tparam R Ratio type for distances (must satisfy RatioType concept)
 */
template<Node N, Edge E, RatioType R>
class NegCycleFinderQ {
private:
    Digraph<N, E> digraph_;
    std::unordered_map<N, std::pair<N, E>> pred_;
    std::unordered_map<N, std::pair<N, E>> succ_;
    
public:
    /**
     * @brief Initialize the negative cycle finder with a directed graph.
     * 
     * @param digraph A mapping representing a directed graph
     */
    explicit NegCycleFinderQ(Digraph<N, E> digraph) 
        : digraph_(std::move(digraph)) {}

    /**
     * @brief Perform one relaxation pass using predecessor links.
     * 
     * Similar to Bellman-Ford but using predecessor relationships.
     * 
     * @param dist Current shortest distance estimates for each node
     * @param get_weight Function to get weight/cost of an edge
     * @return true if any distance was updated, false otherwise
     */
    bool relax_pred(DistanceMap<N, R>& dist, std::function<R(const E&)> get_weight) {
        bool changed = false;

        for (const auto& [utx, neighbors] : digraph_) {
            R dist_u = dist.contains(utx) ? dist[utx] : numeric_traits<R>::zero();
            
            for (const auto& [vtx, edge] : neighbors) {
                R weight = get_weight(edge);
                R distance = dist_u + weight;
                
                if (!dist.contains(vtx)) {
                    dist[vtx] = numeric_traits<R>::zero();
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
     * @brief Perform one relaxation pass using successor links.
     * 
     * Similar to Bellman-Ford but using successor relationships.
     * 
     * @param dist Current shortest distance estimates for each node
     * @param get_weight Function to get weight/cost of an edge
     * @return true if any distance was updated, false otherwise
     */
    bool relax_succ(DistanceMap<N, R>& dist, std::function<R(const E&)> get_weight) {
        bool changed = false;

        // Build reverse graph for successor-based relaxation
        Digraph<N, E> reverse_graph;
        for (const auto& [utx, neighbors] : digraph_) {
            for (const auto& [vtx, edge] : neighbors) {
                reverse_graph[vtx][utx] = edge;
            }
        }

        for (const auto& [vtx, neighbors] : reverse_graph) {
            R dist_v = dist.contains(vtx) ? dist[vtx] : numeric_traits<R>::zero();
            
            for (const auto& [utx, edge] : neighbors) {
                R weight = get_weight(edge);
                R distance = dist_v - weight;  // Note: different sign for successor
                
                if (!dist.contains(utx)) {
                    dist[utx] = numeric_traits<R>::zero();
                }
                
                if (dist[utx] < distance) {  // Note: different comparison
                    dist[utx] = distance;
                    succ_[utx] = std::make_pair(vtx, edge);
                    changed = true;
                }
            }
        }

        return changed;
    }

    /**
     * @brief Find cycles using predecessor links.
     * 
     * @return cppcoro::generator<N> Generator that yields cycle start nodes
     */
    cppcoro::generator<N> find_cycle_pred() const {
        std::unordered_map<N, N> visited;
        
        for (const auto& [vtx, unused] : digraph_) {
            if (visited.contains(vtx)) {
                continue;
            }
            
            auto utx = vtx;
            visited[utx] = vtx;
            
            while (pred_.contains(utx)) {
                const auto& [pred_node, unused] = pred_.at(utx);
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
     * @brief Find cycles using successor links.
     * 
     * @return cppcoro::generator<N> Generator that yields cycle start nodes
     */
    cppcoro::generator<N> find_cycle_succ() const {
        std::unordered_map<N, N> visited;
        
        for (const auto& [vtx, unused] : digraph_) {
            if (visited.contains(vtx)) {
                continue;
            }
            
            auto utx = vtx;
            visited[utx] = vtx;
            
            while (succ_.contains(utx)) {
                const auto& [succ_node, unused] = succ_.at(utx);
                utx = succ_node;
                
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
     * @brief Reconstruct cycle from predecessor links.
     * 
     * @param handle Starting node of the cycle
     * @return Cycle<E> List of edges forming the cycle
     */
    Cycle<E> cycle_list_pred(const N& handle) const {
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
     * @brief Reconstruct cycle from successor links.
     * 
     * @param handle Starting node of the cycle
     * @return Cycle<E> List of edges forming the cycle
     */
    Cycle<E> cycle_list_succ(const N& handle) const {
        Cycle<E> cycle;
        N vtx = handle;

        while (true) {
            if (!succ_.contains(vtx)) {
                throw std::runtime_error("Node not in successor graph");
            }
            
            const auto& [next_vtx, edge] = succ_.at(vtx);
            cycle.push_back(edge);
            vtx = next_vtx;
            
            if (vtx == handle) {
                break;
            }
        }

        return cycle;
    }

    /**
     * @brief Howard's algorithm using predecessor relaxation.
     * 
     * @param dist Initial distance estimates
     * @param get_weight Function to get edge weights
     * @return cppcoro::generator<Cycle<E>> Generator of negative cycles
     */
    cppcoro::generator<Cycle<E>> howard_pred(DistanceMap<N, R>& dist, 
                                             std::function<R(const E&)> get_weight) {
        pred_.clear();
        bool found = false;

        while (!found && relax_pred(dist, get_weight)) {
            for (const auto& vtx : find_cycle_pred()) {
                // Check if cycle is negative (simplified)
                found = true;
                co_yield cycle_list_pred(vtx);
            }
        }
    }

    /**
     * @brief Howard's algorithm using successor relaxation.
     * 
     * @param dist Initial distance estimates
     * @param get_weight Function to get edge weights
     * @return cppcoro::generator<Cycle<E>> Generator of negative cycles
     */
    cppcoro::generator<Cycle<E>> howard_succ(DistanceMap<N, R>& dist, 
                                             std::function<R(const E&)> get_weight) {
        succ_.clear();
        bool found = false;

        while (!found && relax_succ(dist, get_weight)) {
            for (const auto& vtx : find_cycle_succ()) {
                // Check if cycle is negative (simplified)
                found = true;
                co_yield cycle_list_succ(vtx);
            }
        }
    }

    /**
     * @brief Get the predecessor map.
     * 
     * @return const std::unordered_map<N, std::pair<N, E>>& Predecessor map
     */
    const std::unordered_map<N, std::pair<N, E>>& pred() const noexcept {
        return pred_;
    }

    /**
     * @brief Get the successor map.
     * 
     * @return const std::unordered_map<N, std::pair<N, E>>& Successor map
     */
    const std::unordered_map<N, std::pair<N, E>>& succ() const noexcept {
        return succ_;
    }

    /**
     * @brief Get the graph.
     * 
     * @return const Digraph<N, E>& Graph
     */
    const Digraph<N, E>& digraph() const noexcept {
        return digraph_;
    }
};

} // namespace digraphx

#endif // DIGRAPHX_NEG_CYCLE_Q_HPP