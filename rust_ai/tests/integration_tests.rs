//! Integration tests for digraphx Rust library

use digraphx::TinyDiGraph;
use std::collections::HashMap;

#[test]
fn test_tiny_digraph_basic() {
    let mut gr: TinyDiGraph<i32, &str> = TinyDiGraph::new();
    gr.init_nodes(0..5);
    
    assert_eq!(gr.number_of_nodes(), 5);
    assert_eq!(gr.number_of_edges(), 0);
    
    gr.add_edge(&0, &1, "edge01");
    gr.add_edge(&1, &2, "edge12");
    gr.add_edge(&2, &0, "edge20");
    
    assert_eq!(gr.number_of_edges(), 3);
}

#[test]
fn test_neg_cycle_finder_basic() {
    use digraphx::NegCycleFinder;
    
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
    
    let changed = finder.relax(&mut dist, |edge| *edge);
    assert!(changed);
    assert_eq!(dist["b"], 1);
    assert_eq!(dist["c"], 3);
}