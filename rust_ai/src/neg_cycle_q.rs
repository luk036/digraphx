//! Negative Cycle Finder with constraints (neg_cycle_q.rs)
//!
//! This module implements a Negative Cycle Finder for directed graphs using Howard's
//! method. The purpose of this code is to detect and find negative cycles in a
//! directed graph. A negative cycle is a cycle in the graph where the sum of the
//! edge weights is negative.

use std::collections::HashMap;
use std::marker::PhantomData;

use crate::types::{Cycle, Domain, Edge, Node};

/// Negative Cycle Finder with constraints using Howard's method
///
/// This struct implements Howard's method, which is a minimum cycle ratio (MCR) algorithm.
/// It works by maintaining a set of candidate cycles and iteratively updating them until
/// it finds the minimum cycle ratio or detects a negative cycle.
pub struct NegCycleFinderQ<N, E, D>
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
    /// Dictionary to store successor information (node -> (successor_node, edge))
    succ: HashMap<N, (N, E)>,
    /// Marker for unused type parameter D
    _marker: PhantomData<D>,
}

impl<N, E, D> NegCycleFinderQ<N, E, D>
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
    pub fn new(digraph: HashMap<N, HashMap<N, E>>) -> Self {
        Self {
            digraph,
            pred: HashMap::new(),
            succ: HashMap::new(),
            _marker: PhantomData,
        }
    }

    /// Find cycles in the current predecessor graph using depth-first search.
    ///
    /// Uses a coloring algorithm (white/gray/black) to detect cycles.
    ///
    /// # Returns
    ///
    /// A vector of nodes that start cycles in the predecessor graph.
    pub fn find_cycle_pred(&self) -> Vec<N> {
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

    /// Find cycles in the current successor graph using depth-first search.
    ///
    /// Uses a coloring algorithm (white/gray/black) to detect cycles.
    ///
    /// # Returns
    ///
    /// A vector of nodes that start cycles in the successor graph.
    pub fn find_cycle_succ(&self) -> Vec<N> {
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

            while let Some((succ_node, _)) = self.succ.get(&utx) {
                utx = succ_node.clone();

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

    /// Perform predecessor relaxation (relax_pred) operation.
    ///
    /// Updates distances based on predecessor edges.
    ///
    /// # Arguments
    ///
    /// * `dist` - Current distance estimates
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// `true` if any distance was updated, `false` otherwise.
    pub fn relax_pred<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> bool
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

    /// Perform successor relaxation (relax_succ) operation.
    ///
    /// Updates distances based on successor edges.
    ///
    /// # Arguments
    ///
    /// * `dist` - Current distance estimates
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// `true` if any distance was updated, `false` otherwise.
    pub fn relax_succ<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> bool
    where
        F: Fn(&E) -> D,
    {
        let mut changed = false;

        for (vtx, _predecessors) in &self.digraph {
            // We need to find edges that end at vtx
            for (utx, neighbors) in &self.digraph {
                if let Some(edge) = neighbors.get(vtx) {
                    let dist_u = dist.get(utx).cloned().unwrap_or_else(D::zero);
                    let weight = get_weight(edge);
                    let distance = dist_u.clone() + weight;

                    let dist_v = dist.entry(vtx.clone()).or_insert_with(D::zero);
                    if *dist_v > distance {
                        *dist_v = distance;
                        self.succ.insert(utx.clone(), (vtx.clone(), edge.clone()));
                        changed = true;
                    }
                }
            }
        }

        changed
    }

    /// Reconstruct the cycle starting from the given node using predecessor links.
    ///
    /// # Arguments
    ///
    /// * `handle` - The starting node of the cycle
    /// * `pred_map` - Predecessor mapping to use
    ///
    /// # Returns
    ///
    /// List of edges forming the cycle in order.
    pub fn cycle_list_pred(&self, handle: &N, pred_map: &HashMap<N, (N, E)>) -> Cycle<E> {
        let mut cycle = Vec::new();
        let mut vtx = handle.clone();

        loop {
            let (utx, edge) = pred_map.get(&vtx).expect("Node not in predecessor graph");
            cycle.push(edge.clone());
            vtx = utx.clone();

            if &vtx == handle {
                break;
            }
        }

        cycle
    }

    /// Reconstruct the cycle starting from the given node using successor links.
    ///
    /// # Arguments
    ///
    /// * `handle` - The starting node of the cycle
    /// * `succ_map` - Successor mapping to use
    ///
    /// # Returns
    ///
    /// List of edges forming the cycle in order.
    pub fn cycle_list_succ(&self, handle: &N, succ_map: &HashMap<N, (N, E)>) -> Cycle<E> {
        let mut cycle = Vec::new();
        let mut vtx = handle.clone();

        loop {
            let (next_vtx, edge) = succ_map.get(&vtx).expect("Node not in successor graph");
            cycle.push(edge.clone());
            vtx = next_vtx.clone();

            if &vtx == handle {
                break;
            }
        }

        cycle
    }

    /// Check if the cycle starting at 'handle' is negative using predecessor links.
    ///
    /// # Arguments
    ///
    /// * `handle` - Starting node of the cycle to check
    /// * `dist` - Current distance estimates
    /// * `get_weight` - Function to get edge weights
    /// * `pred_map` - Predecessor mapping to use
    ///
    /// # Returns
    ///
    /// `true` if the cycle is negative, `false` otherwise.
    pub fn is_negative_pred<F>(
        &self,
        handle: &N,
        dist: &HashMap<N, D>,
        get_weight: F,
        pred_map: &HashMap<N, (N, E)>,
    ) -> bool
    where
        F: Fn(&E) -> D,
    {
        let mut vtx = handle.clone();

        loop {
            let (utx, edge) = pred_map.get(&vtx).expect("Node not in predecessor graph");
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

    /// Check if the cycle starting at 'handle' is negative using successor links.
    ///
    /// # Arguments
    ///
    /// * `handle` - Starting node of the cycle to check
    /// * `dist` - Current distance estimates
    /// * `get_weight` - Function to get edge weights
    /// * `succ_map` - Successor mapping to use
    ///
    /// # Returns
    ///
    /// `true` if the cycle is negative, `false` otherwise.
    pub fn is_negative_succ<F>(
        &self,
        handle: &N,
        dist: &HashMap<N, D>,
        get_weight: F,
        succ_map: &HashMap<N, (N, E)>,
    ) -> bool
    where
        F: Fn(&E) -> D,
    {
        let mut vtx = handle.clone();

        loop {
            let (next_vtx, edge) = succ_map.get(&vtx).expect("Node not in successor graph");
            let weight = get_weight(edge);

            let dist_v = dist.get(&vtx).cloned().unwrap_or_else(D::zero);
            let dist_u = dist.get(next_vtx).cloned().unwrap_or_else(D::zero);

            if dist_v > dist_u.clone() + weight {
                return true;
            }

            vtx = next_vtx.clone();
            if &vtx == handle {
                break;
            }
        }

        false
    }

    /// Main algorithm to find negative cycles using Howard's method with predecessor relaxation.
    ///
    /// # Arguments
    ///
    /// * `dist` - Initial distance estimates
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// A vector of found negative cycles, each as a list of edges.
    pub fn howard_pred<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> Vec<Cycle<E>>
    where
        F: Fn(&E) -> D + Clone,
    {
        let mut cycles = Vec::new();
        self.pred.clear();
        let mut found = false;

        while !found && self.relax_pred(dist, &get_weight) {
            for vtx in self.find_cycle_pred() {
                assert!(self.is_negative_pred(&vtx, dist, &get_weight, &self.pred));
                found = true;
                cycles.push(self.cycle_list_pred(&vtx, &self.pred));
            }
        }

        cycles
    }

    /// Main algorithm to find negative cycles using Howard's method with successor relaxation.
    ///
    /// # Arguments
    ///
    /// * `dist` - Initial distance estimates
    /// * `get_weight` - Function to get edge weights
    ///
    /// # Returns
    ///
    /// A vector of found negative cycles, each as a list of edges.
    pub fn howard_succ<F>(&mut self, dist: &mut HashMap<N, D>, get_weight: F) -> Vec<Cycle<E>>
    where
        F: Fn(&E) -> D + Clone,
    {
        let mut cycles = Vec::new();
        self.succ.clear();
        let mut found = false;

        while !found && self.relax_succ(dist, &get_weight) {
            for vtx in self.find_cycle_succ() {
                assert!(self.is_negative_succ(&vtx, dist, &get_weight, &self.succ));
                found = true;
                cycles.push(self.cycle_list_succ(&vtx, &self.succ));
            }
        }

        cycles
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neg_cycle_finder_q_new() {
        let digraph: HashMap<&str, HashMap<&str, i32>> = HashMap::new();
        let finder: NegCycleFinderQ<&str, i32, i32> = NegCycleFinderQ::new(digraph);
        assert!(finder.pred.is_empty());
        assert!(finder.succ.is_empty());
    }

    #[test]
    fn test_relax_pred() {
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

        let mut finder: NegCycleFinderQ<&str, i32, i32> = NegCycleFinderQ::new(digraph);
        let mut dist = HashMap::new();
        dist.insert("a", 0);
        dist.insert("b", 1000); // Use a large but safe initial value
        dist.insert("c", 1000);

        let changed = finder.relax_pred(&mut dist, |edge| *edge);
        assert!(changed);
        assert_eq!(dist["b"], 1);
        assert_eq!(dist["c"], 3);
    }
}
