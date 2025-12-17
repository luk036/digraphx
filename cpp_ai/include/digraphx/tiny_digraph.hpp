#pragma once
#ifndef DIGRAPHX_TINY_DIGRAPH_HPP
#define DIGRAPHX_TINY_DIGRAPH_HPP

#include "types.hpp"
#include <vector>
#include <unordered_map>
#include <string>
#include <memory>
#include <cstddef>
#include <stdexcept>
#include <iterator>
#include <concepts>

namespace digraphx {

/**
 * @brief A lightweight directed graph implementation optimized for performance and memory efficiency.
 * 
 * This class provides custom storage mechanisms using vectors and hash maps,
 * which is particularly efficient for graphs with a known, fixed number of nodes.
 * 
 * @tparam N Node type (must satisfy Node concept)
 * @tparam E Edge type (must satisfy Edge concept)
 */
template<Node N, Edge E>
class TinyDiGraph {
private:
    std::size_t num_nodes_;
    std::vector<std::unordered_map<std::string, std::string>> nodes_;
    std::vector<std::unordered_map<N, E>> adj_;      // Outgoing edges (successors)
    std::vector<std::unordered_map<N, E>> pred_;     // Incoming edges (predecessors)
    std::unordered_map<N, std::size_t> node_to_index_;
    std::vector<N> index_to_node_;

public:
    /**
     * @brief Constructs a new empty TinyDiGraph.
     */
    TinyDiGraph() : num_nodes_(0) {}

    /**
     * @brief Initializes the graph with nodes from an iterator range.
     * 
     * Sets up the internal data structures for node storage, adjacency lists (successors),
     * and predecessor lists. This method must be called before adding any edges.
     * 
     * @tparam InputIt Input iterator type
     * @param first Iterator to the beginning of the node sequence
     * @param last Iterator to the end of the node sequence
     * 
     * @throws std::invalid_argument if the iterator range is empty
     */
    template<std::input_iterator InputIt>
    void init_nodes(InputIt first, InputIt last) {
        nodes_.clear();
        adj_.clear();
        pred_.clear();
        node_to_index_.clear();
        index_to_node_.clear();

        std::size_t idx = 0;
        for (auto it = first; it != last; ++it) {
            node_to_index_[*it] = idx;
            index_to_node_.push_back(*it);
            nodes_.emplace_back();
            adj_.emplace_back();
            pred_.emplace_back();
            ++idx;
        }

        num_nodes_ = index_to_node_.size();
    }

    /**
     * @brief Initializes the graph with nodes from an initializer list.
     * 
     * @param nodes Initializer list of nodes
     */
    void init_nodes(std::initializer_list<N> nodes) {
        init_nodes(nodes.begin(), nodes.end());
    }

    /**
     * @brief Returns the number of nodes in the graph.
     * 
     * @return std::size_t Number of nodes
     */
    std::size_t number_of_nodes() const noexcept {
        return num_nodes_;
    }

    /**
     * @brief Returns the number of edges in the graph.
     * 
     * @return std::size_t Number of edges
     */
    std::size_t number_of_edges() const noexcept {
        std::size_t count = 0;
        for (const auto& edges : adj_) {
            count += edges.size();
        }
        return count;
    }

    /**
     * @brief Adds an edge from source node u to target node v with the given edge data.
     * 
     * @param u Source node
     * @param v Target node
     * @param edge Edge data
     * 
     * @throws std::out_of_range if either u or v is not a valid node in the graph
     */
    void add_edge(const N& u, const N& v, const E& edge) {
        auto u_it = node_to_index_.find(u);
        auto v_it = node_to_index_.find(v);
        
        if (u_it == node_to_index_.end()) {
            throw std::out_of_range("Source node not found");
        }
        if (v_it == node_to_index_.end()) {
            throw std::out_of_range("Target node not found");
        }

        std::size_t u_idx = u_it->second;
        std::size_t v_idx = v_it->second;

        adj_[u_idx][v] = edge;
        pred_[v_idx][u] = edge;
    }

    /**
     * @brief Returns an iterator to the beginning of the node sequence.
     * 
     * @return auto Iterator to the first node
     */
    auto nodes_begin() const noexcept {
        return index_to_node_.begin();
    }

    /**
     * @brief Returns an iterator to the end of the node sequence.
     * 
     * @return auto Iterator past the last node
     */
    auto nodes_end() const noexcept {
        return index_to_node_.end();
    }

    /**
     * @brief Returns a range of all nodes in the graph.
     * 
     * @return auto Range of nodes
     */
    auto nodes() const noexcept {
        return std::ranges::subrange(index_to_node_.begin(), index_to_node_.end());
    }

    /**
     * @brief Returns a range of all edges in the graph.
     * 
     * The range yields tuples of (source, target, edge_data).
     * 
     * @return auto Range of edges
     */
    auto edges() const {
        struct EdgeIterator {
            using outer_iterator = typename std::vector<std::unordered_map<N, E>>::const_iterator;
            using inner_iterator = typename std::unordered_map<N, E>::const_iterator;
            
            outer_iterator outer_it;
            outer_iterator outer_end;
            inner_iterator inner_it;
            const std::vector<N>* index_to_node;
            std::size_t current_idx;
            
            EdgeIterator(outer_iterator oit, outer_iterator oend, 
                        const std::vector<N>* nodes, std::size_t idx = 0)
                : outer_it(oit), outer_end(oend), index_to_node(nodes), current_idx(idx) {
                if (outer_it != outer_end) {
                    inner_it = outer_it->begin();
                    advance_to_valid();
                }
            }
            
            void advance_to_valid() {
                while (outer_it != outer_end && inner_it == outer_it->end()) {
                    ++outer_it;
                    ++current_idx;
                    if (outer_it != outer_end) {
                        inner_it = outer_it->begin();
                    }
                }
            }
            
            EdgeIterator& operator++() {
                if (outer_it == outer_end) return *this;
                ++inner_it;
                advance_to_valid();
                return *this;
            }
            
            EdgeIterator operator++(int) {
                EdgeIterator tmp = *this;
                ++(*this);
                return tmp;
            }
            
            bool operator==(const EdgeIterator& other) const {
                return outer_it == other.outer_it && 
                      (outer_it == outer_end || inner_it == other.inner_it);
            }
            
            auto operator*() const {
                return std::make_tuple(
                    std::cref((*index_to_node)[current_idx]),
                    std::cref(inner_it->first),
                    std::cref(inner_it->second)
                );
            }
        };
        
        struct EdgeRange {
            const std::vector<std::unordered_map<N, E>>& adj;
            const std::vector<N>& index_to_node;
            
            EdgeIterator begin() const {
                return EdgeIterator(adj.begin(), adj.end(), &index_to_node, 0);
            }
            
            EdgeIterator end() const {
                return EdgeIterator(adj.end(), adj.end(), &index_to_node, 0);
            }
        };
        
        return EdgeRange{adj_, index_to_node_};
    }

    /**
     * @brief Returns a range of neighbors (successors) of a node.
     * 
     * @param node The node whose neighbors to retrieve
     * @return auto Range yielding tuples of (neighbor_node, edge_data)
     * 
     * @throws std::out_of_range if node is not found
     */
    auto neighbors(const N& node) const {
        auto it = node_to_index_.find(node);
        if (it == node_to_index_.end()) {
            throw std::out_of_range("Node not found");
        }
        
        std::size_t idx = it->second;
        const auto& neighbor_map = adj_[idx];
        
        struct NeighborIterator {
            using map_iterator = typename std::unordered_map<N, E>::const_iterator;
            map_iterator it;
            map_iterator end;
            
            NeighborIterator(map_iterator i, map_iterator e) : it(i), end(e) {}
            
            NeighborIterator& operator++() { ++it; return *this; }
            NeighborIterator operator++(int) { NeighborIterator tmp = *this; ++it; return tmp; }
            
            bool operator==(const NeighborIterator& other) const { return it == other.it; }
            
            auto operator*() const {
                return std::make_pair(std::cref(it->first), std::cref(it->second));
            }
        };
        
        struct NeighborRange {
            const std::unordered_map<N, E>& neighbor_map;
            
            NeighborIterator begin() const { return NeighborIterator(neighbor_map.begin(), neighbor_map.end()); }
            NeighborIterator end() const { return NeighborIterator(neighbor_map.end(), neighbor_map.end()); }
        };
        
        return NeighborRange{neighbor_map};
    }

    /**
     * @brief Returns a range of predecessors of a node.
     * 
     * @param node The node whose predecessors to retrieve
     * @return auto Range yielding tuples of (predecessor_node, edge_data)
     * 
     * @throws std::out_of_range if node is not found
     */
    auto predecessors(const N& node) const {
        auto it = node_to_index_.find(node);
        if (it == node_to_index_.end()) {
            throw std::out_of_range("Node not found");
        }
        
        std::size_t idx = it->second;
        const auto& pred_map = pred_[idx];
        
        struct PredecessorIterator {
            using map_iterator = typename std::unordered_map<N, E>::const_iterator;
            map_iterator it;
            map_iterator end;
            
            PredecessorIterator(map_iterator i, map_iterator e) : it(i), end(e) {}
            
            PredecessorIterator& operator++() { ++it; return *this; }
            PredecessorIterator operator++(int) { PredecessorIterator tmp = *this; ++it; return tmp; }
            
            bool operator==(const PredecessorIterator& other) const { return it == other.it; }
            
            auto operator*() const {
                return std::make_pair(std::cref(it->first), std::cref(it->second));
            }
        };
        
        struct PredecessorRange {
            const std::unordered_map<N, E>& pred_map;
            
            PredecessorIterator begin() const { return PredecessorIterator(pred_map.begin(), pred_map.end()); }
            PredecessorIterator end() const { return PredecessorIterator(pred_map.end(), pred_map.end()); }
        };
        
        return PredecessorRange{pred_map};
    }

    /**
     * @brief Gets a mutable reference to node attributes.
     * 
     * @param node The node whose attributes to retrieve
     * @return std::unordered_map<std::string, std::string>& Mutable reference to node's attribute map
     * 
     * @throws std::out_of_range if node is not found
     */
    std::unordered_map<std::string, std::string>& node_attributes_mut(const N& node) {
        auto it = node_to_index_.find(node);
        if (it == node_to_index_.end()) {
            throw std::out_of_range("Node not found");
        }
        return nodes_[it->second];
    }

    /**
     * @brief Gets a const reference to node attributes.
     * 
     * @param node The node whose attributes to retrieve
     * @return const std::unordered_map<std::string, std::string>& Const reference to node's attribute map
     * 
     * @throws std::out_of_range if node is not found
     */
    const std::unordered_map<std::string, std::string>& node_attributes(const N& node) const {
        auto it = node_to_index_.find(node);
        if (it == node_to_index_.end()) {
            throw std::out_of_range("Node not found");
        }
        return nodes_[it->second];
    }
};

} // namespace digraphx

#endif // DIGRAPHX_TINY_DIGRAPH_HPP