//! TinyDiGraph - A lightweight directed graph implementation optimized for performance and memory efficiency.
//!
//! This module provides a custom graph data structure called TinyDiGraph, which is
//! designed to be a lightweight and efficient implementation of a directed graph.
//! The purpose of this code is to provide a simple way to create and manipulate
//! directed graphs, particularly for cases where performance and memory
//! efficiency are important.

use indexmap::IndexMap;
use std::collections::HashMap;
use std::hash::Hash;

/// A lightweight directed graph implementation optimized for performance and memory efficiency.
///
/// This struct provides custom storage mechanisms using vectors and hash maps,
/// which is particularly efficient for graphs with a known, fixed number of nodes.
#[derive(Debug, Clone)]
pub struct TinyDiGraph<N, E>
where
    N: Hash + Eq + Clone,
    E: Clone,
{
    /// Total number of nodes in the graph
    num_nodes: usize,
    /// Stores node attributes
    nodes: Vec<HashMap<String, String>>,
    /// Stores outgoing edges (successors)
    adj: Vec<IndexMap<N, E>>,
    /// Stores incoming edges (predecessors)
    pred: Vec<IndexMap<N, E>>,
    /// Mapping from node to index
    node_to_index: HashMap<N, usize>,
    /// Mapping from index to node
    index_to_node: Vec<N>,
}

impl<N, E> TinyDiGraph<N, E>
where
    N: Hash + Eq + Clone,
    E: Clone,
{
    /// Creates a new empty TinyDiGraph.
    pub fn new() -> Self {
        Self {
            num_nodes: 0,
            nodes: Vec::new(),
            adj: Vec::new(),
            pred: Vec::new(),
            node_to_index: HashMap::new(),
            index_to_node: Vec::new(),
        }
    }

    /// Initializes the graph with a specified number of nodes.
    ///
    /// Sets up the internal data structures for node storage, adjacency lists (successors),
    /// and predecessor lists. This method must be called before adding any edges.
    ///
    /// # Arguments
    ///
    /// * `nodes` - An iterator of nodes to initialize in the graph.
    ///
    /// # Examples
    ///
    /// ```
    /// use digraphx::tiny_digraph::TinyDiGraph;
    ///
    /// let mut gr: TinyDiGraph<i32, ()> = TinyDiGraph::new();
    /// gr.init_nodes(vec![0, 1, 2, 3, 4]);
    /// assert_eq!(gr.number_of_nodes(), 5);
    /// ```
    pub fn init_nodes<I>(&mut self, nodes: I)
    where
        I: IntoIterator<Item = N>,
    {
        self.nodes.clear();
        self.adj.clear();
        self.pred.clear();
        self.node_to_index.clear();
        self.index_to_node.clear();

        for (idx, node) in nodes.into_iter().enumerate() {
            self.node_to_index.insert(node.clone(), idx);
            self.index_to_node.push(node);
            self.nodes.push(HashMap::new());
            self.adj.push(IndexMap::new());
            self.pred.push(IndexMap::new());
        }

        self.num_nodes = self.index_to_node.len();
    }

    /// Returns the number of nodes in the graph.
    pub fn number_of_nodes(&self) -> usize {
        self.num_nodes
    }

    /// Returns the number of edges in the graph.
    pub fn number_of_edges(&self) -> usize {
        self.adj.iter().map(|edges| edges.len()).sum()
    }

    /// Adds an edge from source node `u` to target node `v` with the given edge data.
    ///
    /// # Arguments
    ///
    /// * `u` - Source node
    /// * `v` - Target node
    /// * `edge` - Edge data
    ///
    /// # Panics
    ///
    /// Panics if either `u` or `v` is not a valid node in the graph.
    pub fn add_edge(&mut self, u: &N, v: &N, edge: E) {
        let u_idx = *self.node_to_index.get(u).expect("Source node not found");
        let v_idx = *self.node_to_index.get(v).expect("Target node not found");

        self.adj[u_idx].insert(v.clone(), edge.clone());
        self.pred[v_idx].insert(u.clone(), edge);
    }

    /// Returns an iterator over all nodes in the graph.
    pub fn nodes(&self) -> impl Iterator<Item = &N> {
        self.index_to_node.iter()
    }

    /// Returns an iterator over all edges in the graph.
    ///
    /// The iterator yields tuples of (source, target, edge_data).
    pub fn edges(&self) -> impl Iterator<Item = (&N, &N, &E)> {
        self.adj.iter().enumerate().flat_map(|(u_idx, edges)| {
            let u = &self.index_to_node[u_idx];
            edges.iter().map(move |(v, edge)| (u, v, edge))
        })
    }

    /// Returns an iterator over the neighbors (successors) of a node.
    ///
    /// # Arguments
    ///
    /// * `node` - The node whose neighbors to retrieve
    ///
    /// # Returns
    ///
    /// An iterator yielding tuples of (neighbor_node, edge_data).
    pub fn neighbors(&self, node: &N) -> impl Iterator<Item = (&N, &E)> {
        let idx = self.node_to_index.get(node).expect("Node not found");
        self.adj[*idx].iter().map(|(v, edge)| (v, edge))
    }

    /// Returns an iterator over the predecessors of a node.
    ///
    /// # Arguments
    ///
    /// * `node` - The node whose predecessors to retrieve
    ///
    /// # Returns
    ///
    /// An iterator yielding tuples of (predecessor_node, edge_data).
    pub fn predecessors(&self, node: &N) -> impl Iterator<Item = (&N, &E)> {
        let idx = self.node_to_index.get(node).expect("Node not found");
        self.pred[*idx].iter().map(|(u, edge)| (u, edge))
    }

    /// Gets a mutable reference to node attributes.
    ///
    /// # Arguments
    ///
    /// * `node` - The node whose attributes to retrieve
    ///
    /// # Returns
    ///
    /// A mutable reference to the node's attribute map.
    pub fn node_attributes_mut(&mut self, node: &N) -> &mut HashMap<String, String> {
        let idx = self.node_to_index.get(node).expect("Node not found");
        &mut self.nodes[*idx]
    }

    /// Gets a reference to node attributes.
    ///
    /// # Arguments
    ///
    /// * `node` - The node whose attributes to retrieve
    ///
    /// # Returns
    ///
    /// A reference to the node's attribute map.
    pub fn node_attributes(&self, node: &N) -> &HashMap<String, String> {
        let idx = self.node_to_index.get(node).expect("Node not found");
        &self.nodes[*idx]
    }
}

impl<N, E> Default for TinyDiGraph<N, E>
where
    N: Hash + Eq + Clone,
    E: Clone,
{
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_init_nodes() {
        let mut gr: TinyDiGraph<i32, ()> = TinyDiGraph::new();
        gr.init_nodes(0..5);
        assert_eq!(gr.number_of_nodes(), 5);
    }

    #[test]
    fn test_add_edge() {
        let mut gr: TinyDiGraph<i32, &str> = TinyDiGraph::new();
        gr.init_nodes(0..3);
        gr.add_edge(&0, &1, "edge01");
        gr.add_edge(&1, &2, "edge12");
        gr.add_edge(&2, &0, "edge20");

        assert_eq!(gr.number_of_edges(), 3);
    }

    #[test]
    fn test_neighbors() {
        let mut gr = TinyDiGraph::new();
        gr.init_nodes(vec![0, 1, 2, 3]);
        gr.add_edge(&0, &1, "edge01");
        gr.add_edge(&0, &2, "edge02");
        gr.add_edge(&0, &3, "edge03");

        let neighbors: Vec<_> = gr.neighbors(&0).collect();
        assert_eq!(neighbors.len(), 3);
        assert!(neighbors.contains(&(&1, &"edge01")));
        assert!(neighbors.contains(&(&2, &"edge02")));
        assert!(neighbors.contains(&(&3, &"edge03")));
    }

    #[test]
    fn test_predecessors() {
        let mut gr = TinyDiGraph::new();
        gr.init_nodes(vec![0, 1, 2, 3]);
        gr.add_edge(&1, &0, "edge10");
        gr.add_edge(&2, &0, "edge20");
        gr.add_edge(&3, &0, "edge30");

        let predecessors: Vec<_> = gr.predecessors(&0).collect();
        assert_eq!(predecessors.len(), 3);
        assert!(predecessors.contains(&(&1, &"edge10")));
        assert!(predecessors.contains(&(&2, &"edge20")));
        assert!(predecessors.contains(&(&3, &"edge30")));
    }
}
