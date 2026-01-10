//! NegCycleFinder - Negative Cycle Finder by Howard's method
//!
//! This module defines a `NegCycleFinder` struct, which is designed to find
//! negative cycles in a directed graph. A negative cycle is a loop in the graph
//! where the sum of the edge weights is less than zero. This can be important in
//! various applications, such as detecting arbitrage opportunities in currency
//! exchange rates.

use std::collections::HashMap;
use std::marker::PhantomData;

use crate::types::{Cycle, Domain, Edge, Node};

/// Negative Cycle Finder by Howard's method
///
/// This struct is used to find negative cycles in a given directed graph.
/// It implements the following algorithms:
///
/// 1. Bellman-Ford Algorithm: It is a shortest path algorithm that can find
///    single source shortest paths in a graph with negative edge weights.
/// 2. Howard's Policy Graph Algorithm: It is used to find cycles in a directed
///    graph and is based on the Bellman-Ford Algorithm.
pub struct NegCycleFinder<N, E, D>
where
    N: Node,
    E: Edge,
    D: Domain,
{
    /// The directed graph where:
    /// - Keys are source nodes
    /// - Values are mappings of destination nodes to edges
    digraph: HashMap<N, HashMap<N, E>>,
    /// Dictionary to store predecessor information (node -> (predecessor_node, edge))
    pred: HashMap<N, (N, E)>,
    /// Marker for unused type parameter D
    _marker: PhantomData<D>,
}

impl<N, E, D> NegCycleFinder<N, E, D>
where
    N: Node,
    E: Edge,
    D: Domain,
{
    /// Initialize the negative cycle finder with a directed graph.
    ///
    /// # Arguments
    ///
    /// * `digraph` - A mapping representing a directed graph where:
    ///     - Keys are source nodes
    ///     - Values are mappings of destination nodes to edges
    ///     Example: {u: {v: edge_uv, w: edge_uw}, v: {u: edge_vu}}
    pub fn new(digraph: HashMap<N, HashMap<N, E>>) -> Self {
        Self {
            digraph,
            pred: HashMap::new(),
            _marker: PhantomData,
        }
    }

    /// Find cycles in the current predecessor graph using depth-first search.
    ///
    /// Uses a coloring algorithm (white/gray/black) to detect cycles:
    /// - White: unvisited nodes
    /// - Gray: nodes being visited in current DFS path
    /// - Black: fully visited nodes
    ///
    /// # Returns
    ///
    /// A generator that yields each node that starts a cycle in the predecessor graph.
    pub fn find_cycle(&self) -> Vec<N> {
        let mut visited: HashMap<N, N> = HashMap::new();
        let mut result = Vec::new();

        // Collect keys first to avoid borrowing issues
        let keys: Vec<N> = self.digraph.keys().cloned().collect();

        for vtx in keys {
            if visited.contains_key(&vtx) {
                continue;
            }

            let mut utx = vtx.clone();
            visited.insert(utx.clone(), vtx.clone());

            while let Some((pred_node, _)) = self.pred.get(&utx) {
                utx = pred_node.clone();

                if let Some(root) = visited.get(&utx) {
                    if root == &vtx {
                        result.push(utx.clone());
                    }
                    break;
                }

                visited.insert(utx.clone(), vtx.clone());
            }
        }

        result
    }

    /// Perform one relaxation pass of the Bellman-Ford algorithm.
    ///
    /// Updates both distance estimates (dist) and predecessor information
    /// (pred) for all edges in the graph following the Bellman-Ford
    /// relaxation rule: if dist[v] > dist[u] + weight(u,v), then update
    /// dist[v].
    ///
    /// # Arguments
    ///
    /// * `dist` - Current shortest distance estimates for each node
    /// * `get_weight` - Function to get weight/cost of an edge
    ///
    /// # Returns
    ///
    /// `true` if any distance was updated, `false` otherwise.
    pub fn relax<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> bool
    where
        F: Fn(&E) -> D,
    {
        let mut changed = false;

        for (utx, neighbors) in &self.digraph {
            let dist_u = dist.get(utx).cloned().unwrap_or_else(D::zero);

            for (vtx, edge) in neighbors {
                let weight = get_weight(edge);
                let distance = dist_u.clone() + weight;

                let dist_v = dist.entry(vtx.clone()).or_insert_with(D::zero);
                if *dist_v > distance {
                    *dist_v = distance;
                    self.pred.insert(vtx.clone(), (utx.clone(), edge.clone()));
                    changed = true;
                }
            }
        }

        changed
    }

    /// Reconstruct the cycle starting from the given node.
    ///
    /// Follows predecessor links until returning to the starting node.
    ///
    /// # Arguments
    ///
    /// * `handle` - The starting node of the cycle (must be part of a cycle)
    ///
    /// # Returns
    ///
    /// List of edges forming the cycle in order.
    pub fn cycle_list(&self, handle: &N) -> Cycle<E> {
        let mut cycle = Vec::new();
        let mut vtx = handle.clone();

        loop {
            let (utx, edge) = self.pred.get(&vtx).expect("Node not in predecessor graph");
            cycle.push(edge.clone());
            vtx = utx.clone();

            if &vtx == handle {
                break;
            }
        }

        cycle
    }

    /// Check if the cycle starting at 'handle' is negative.
    ///
    /// A cycle is negative if the sum of its edge weights is negative.
    /// This is checked by verifying that for at least one edge (u,v) in the
    /// cycle, dist[v] > dist[u] + weight(u,v) (triangle inequality violation).
    ///
    /// # Arguments
    ///
    /// * `handle` - Starting node of the cycle to check
    /// * `dist` - Current distance estimates
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// `true` if the cycle is negative, `false` otherwise.
    pub fn is_negative<F>(&self, handle: &N, dist: &HashMap<N, D>, get_weight: F) -> bool
    where
        F: Fn(&E) -> D,
    {
        let mut vtx = handle.clone();

        loop {
            let (utx, edge) = self.pred.get(&vtx).expect("Node not in predecessor graph");
            let weight = get_weight(edge);

            let dist_v = dist.get(&vtx).cloned().unwrap_or_else(D::zero);
            let dist_u = dist.get(utx).cloned().unwrap_or_else(D::zero);

            if dist_v > dist_u.clone() + weight {
                return true;
            }

            vtx = utx.clone();
            if &vtx == handle {
                break;
            }
        }

        false
    }

    /// Main algorithm to find negative cycles using Howard's method.
    ///
    /// The algorithm:
    /// 1. Repeatedly relaxes edges until no more improvements can be made
    /// 2. Checks for cycles in the predecessor graph
    /// 3. Verifies if found cycles are negative
    /// 4. Returns each found negative cycle
    ///
    /// # Arguments
    ///
    /// * `dist` - Initial distance estimates (often initialized to zero)
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// A vector of found negative cycles, each as a list of edges.
    pub fn howard<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> Vec<Cycle<E>>
    where
        F: Fn(&E) -> D + Clone,
    {
        let mut cycles = Vec::new();
        self.pred.clear();
        let mut found = false;

        while !found && self.relax(dist, &get_weight) {
            for vtx in self.find_cycle() {
                assert!(self.is_negative(&vtx, dist, &get_weight));
                found = true;
                cycles.push(self.cycle_list(&vtx));
            }
        }

        cycles
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neg_cycle_finder_new() {
        let digraph: HashMap<&str, HashMap<&str, i32>> = HashMap::new();
        let finder: NegCycleFinder<&str, i32, i32> = NegCycleFinder::new(digraph);
        assert!(finder.pred.is_empty());
    }

    #[test]
    fn test_relax() {
        let mut digraph = HashMap::new();
        let mut neighbors = HashMap::new();
        neighbors.insert("b", 1);
        neighbors.insert("c", 4);
        digraph.insert("a", neighbors);

        let mut neighbors = HashMap::new();
        neighbors.insert("c", 2);
        digraph.insert("b", neighbors);

        let mut neighbors = HashMap::new();
        neighbors.insert("a", -5);
        digraph.insert("c", neighbors);

        let mut finder: NegCycleFinder<&str, i32, i32> = NegCycleFinder::new(digraph);
        let mut dist = HashMap::new();
        dist.insert("a", 0);
        dist.insert("b", 1000); // Use a large but safe initial value
        dist.insert("c", 1000);

        let changed = finder.relax(&mut dist, |edge| *edge);
        assert!(changed);
        assert_eq!(dist["b"], 1);
        assert_eq!(dist["c"], 3);
    }

    #[test]
    fn test_cycle_list() {
        let digraph: HashMap<&str, HashMap<&str, &str>> = HashMap::new();
        let mut finder: NegCycleFinder<&str, &str, i32> = NegCycleFinder::new(digraph);

        finder.pred.insert("b", ("a", "ab"));
        finder.pred.insert("c", ("b", "bc"));
        finder.pred.insert("a", ("c", "ca"));

        let cycle = finder.cycle_list(&"a");
        assert_eq!(cycle, vec!["ca", "bc", "ab"]);
    }

    #[test]
    fn test_is_negative() {
        let digraph: HashMap<&str, HashMap<&str, i32>> = HashMap::new();
        let mut finder: NegCycleFinder<&str, i32, i32> = NegCycleFinder::new(digraph);

        finder.pred.insert("b", ("a", 1));
        finder.pred.insert("c", ("b", 1));
        finder.pred.insert("a", ("c", -3));

        let mut dist = HashMap::new();
        dist.insert("a", 0);
        dist.insert("b", 1);
        dist.insert("c", 2);

        let is_neg = finder.is_negative(&"a", &dist, |edge| *edge);
        assert!(is_neg);
    }

    #[test]
    fn test_howard() {
        let mut digraph = HashMap::new();
        let mut neighbors = HashMap::new();
        neighbors.insert("b", 1);
        neighbors.insert("c", 4);
        digraph.insert("a", neighbors);

        let mut neighbors = HashMap::new();
        neighbors.insert("c", 2);
        digraph.insert("b", neighbors);

        let mut neighbors = HashMap::new();
        neighbors.insert("a", -5);
        digraph.insert("c", neighbors);

        let mut finder: NegCycleFinder<&str, i32, i32> = NegCycleFinder::new(digraph);
        let mut dist = HashMap::new();
        dist.insert("a", 0);
        dist.insert("b", i32::MAX);
        dist.insert("c", i32::MAX);

        let cycles = finder.howard(&mut dist, |edge| *edge);
        // With this graph, we should find a negative cycle
        assert!(!cycles.is_empty());
    }
}
