//! digraphx - A directed graph optimization library for network optimization problems
//!
//! This library provides algorithms for:
//! - Negative cycle detection
//! - Minimum cycle ratio calculation
//! - Parametric optimization algorithms
//! - Efficient graph data structures

pub mod tiny_digraph;
pub mod neg_cycle;
pub mod neg_cycle_q;
pub mod min_cycle_ratio;
pub mod min_parametric_q;
pub mod parametric;

pub use tiny_digraph::TinyDiGraph;
pub use neg_cycle::NegCycleFinder;
pub use neg_cycle_q::NegCycleFinderQ;
pub use min_cycle_ratio::{MinCycleRatioSolver, CycleRatioAPI};
pub use min_parametric_q::{MinParametricQSolver, MinParametricAPI};
pub use parametric::{MaxParametricSolver, ParametricAPI};

/// Common types used throughout the library
pub mod types {
    use num_rational::Ratio;
    use std::hash::Hash;

    /// Node type - must be hashable and comparable
    pub trait Node: Hash + Eq + Clone {}
    impl<T: Hash + Eq + Clone> Node for T {}

    /// Edge type - must be hashable and comparable
    pub trait Edge: Hash + Eq + Clone {}
    impl<T: Hash + Eq + Clone> Edge for T {}

    /// Domain type for weights - supports arithmetic and comparison
    pub trait Domain: Clone + PartialOrd + std::ops::Add<Output = Self> + std::ops::Sub<Output = Self> + std::ops::Mul<Output = Self> + std::ops::Div<Output = Self> + num::Zero + num::One {}
    impl<T: Clone + PartialOrd + std::ops::Add<Output = T> + std::ops::Sub<Output = T> + std::ops::Mul<Output = T> + std::ops::Div<Output = T> + num::Zero + num::One> Domain for T {}

    /// Ratio type - can be either rational or floating point
    pub trait RatioType: Clone + PartialOrd + std::ops::Add<Output = Self> + std::ops::Sub<Output = Self> + std::ops::Mul<Output = Self> + std::ops::Div<Output = Self> + num::Zero + num::One {}
    impl<T: Clone + PartialOrd + std::ops::Add<Output = T> + std::ops::Sub<Output = T> + std::ops::Mul<Output = T> + std::ops::Div<Output = T> + num::Zero + num::One> RatioType for T {}

    /// Type alias for rational numbers
    pub type Rational = Ratio<i64>;

    /// Cycle type - a sequence of edges
    pub type Cycle<E> = Vec<E>;
}
