//! Min Parametric Solver with constraints
//!
//! This module defines a system for solving a specific type of network optimization
//! problem called a "minimum parametric problem." The purpose of this code is to
//! find the smallest possible value for a parameter (called a ratio) that
//! satisfies certain conditions in a graph-like structure.

use std::collections::HashMap;

use crate::neg_cycle_q::NegCycleFinderQ;
use crate::types::{Cycle, Domain, Edge, Node, RatioType};

/// Minimum Parametric API trait for distance calculation and cycle analysis.
///
/// This trait defines an interface for calculating distances and handling cycles,
/// allowing for different implementations of these operations.
pub trait MinParametricAPI<N, E, R>
where
    N: Node,
    E: Edge,
    R: RatioType,
{
    /// Calculate the parametric distance for an edge given the current ratio.
    fn distance(&self, ratio: R, edge: &E) -> R;

    /// Calculate the actual ratio for a given cycle.
    fn zero_cancel(&self, cycle: &Cycle<E>) -> R;
}

/// Minimum Parametric Solver with constraints
///
/// This struct solves a specific type of network optimization problem called a
/// "minimum parametric problem." It finds the smallest possible value for a
/// parameter (called a ratio) that satisfies certain conditions in a graph.
pub struct MinParametricQSolver<N, E, R, API>
where
    N: Node,
    E: Edge,
    R: RatioType,
    API: MinParametricAPI<N, E, R>,
{
    /// The graph structure where nodes map to neighbors and edges
    digraph: HashMap<N, HashMap<N, E>>,
    /// Parametric API for distance calculation and cycle analysis
    omega: API,
    /// Marker for unused type parameter R
    _marker: std::marker::PhantomData<R>,
}

impl<N, E, R, API> MinParametricQSolver<N, E, R, API>
where
    N: Node,
    E: Edge,
    R: RatioType,
    API: MinParametricAPI<N, E, R>,
{
    /// Initialize the solver with a graph and a parametric API.
    ///
    /// # Arguments
    ///
    /// * `digraph` - A mapping of nodes to a mapping of nodes to edges.
    /// * `omega` - A parametric API instance that provides methods for distance
    ///   calculation and cycle analysis.
    pub fn new(digraph: HashMap<N, HashMap<N, E>>, omega: API) -> Self {
        Self {
            digraph,
            omega,
            _marker: std::marker::PhantomData,
        }
    }

    /// Run the minimum parametric solver algorithm.
    ///
    /// The algorithm works by:
    /// 1. Starting with an initial ratio and distance estimates
    /// 2. Using a negative cycle finder to find cycles in the graph
    /// 3. For each cycle found, calculating a new ratio
    /// 4. Updating the minimum ratio if a smaller one is found
    /// 5. Repeating until no better ratio can be found
    ///
    /// The algorithm can switch between searching for cycles in the forward
    /// direction (successor nodes) and the backward direction (predecessor nodes).
    ///
    /// # Arguments
    ///
    /// * `dist` - Initial distance labels for nodes
    /// * `ratio` - Initial ratio value to start the search
    /// * `use_succ` - Whether to use successor relaxation (true) or predecessor relaxation (false)
    ///
    /// # Returns
    ///
    /// A tuple containing the optimal ratio and the cycle that achieves it.
    pub fn run(&self, mut dist: HashMap<N, R>, ratio: R, use_succ: bool) -> (R, Cycle<E>)
    where
        R: Domain + Clone,
    {
        // Initialize minimum ratio and cycle
        let mut r_min = ratio.clone();
        let mut c_min = Vec::new();
        let mut cycle = Vec::new();
        let mut current_ratio = ratio.clone();

        // Create a negative cycle finder instance with the graph
        let mut ncf: NegCycleFinderQ<N, E, R> = NegCycleFinderQ::new(self.digraph.clone());

        // Main algorithm loop
        loop {
            // Define a weight function that calculates distance based on current ratio
            let get_weight = |e: &E| self.omega.distance(current_ratio.clone(), e);

            // Find all negative cycles in the graph
            let cycles: Vec<Cycle<E>> = if use_succ {
                ncf.howard_succ(&mut dist, &get_weight)
            } else {
                ncf.howard_pred(&mut dist, &get_weight)
            };

            for ci in cycles {
                // Calculate the ratio that would make this cycle's total distance zero
                let ri = self.omega.zero_cancel(&ci);

                // Update minimum ratio if a smaller one is found
                if r_min > ri {
                    r_min = ri;
                    c_min = ci;
                }
            }

            // Termination condition: no better ratio found
            if r_min >= current_ratio {
                break;
            }

            // Update cycle and ratio for next iteration
            cycle = c_min.clone();
            current_ratio = r_min.clone();
        }

        (ratio, cycle)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use num_rational::Ratio;
    use std::collections::HashMap;

    struct TestAPI;

    impl MinParametricAPI<&'static str, i32, Ratio<i64>> for TestAPI {
        fn distance(&self, ratio: Ratio<i64>, _edge: &i32) -> Ratio<i64> {
            // Simple implementation for testing
            ratio.clone()
        }

                    fn zero_cancel(&self, _cycle: &Vec<i32>) -> Ratio<i64> {
                        // Simple implementation for testing
                        Ratio::new(1, 2)
                    }    }

    #[test]
    fn test_min_parametric_q_solver_new() {
        let _digraph: HashMap<&str, HashMap<&str, i32>> = HashMap::new();
        let api = TestAPI;
        let _solver: MinParametricQSolver<&str, i32, Ratio<i64>, TestAPI> = MinParametricQSolver::new(_digraph, api);
        // Just testing that it compiles and creates successfully
        assert!(true);
    }
}
