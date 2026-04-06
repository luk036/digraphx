//! Basic usage example for digraphx library

use digraphx::TinyDiGraph;

fn main() {
    println!("=== TinyDiGraph Example ===");

    // Create a new TinyDiGraph
    let mut digraph = TinyDiGraph::new();

    // Initialize with 5 nodes
    digraph.init_nodes(vec![0, 1, 2, 3, 4]);
    println!("Created graph with {} nodes", digraph.number_of_nodes());

    // Add some edges
    digraph.add_edge(&0, &1, "edge_0_1");
    digraph.add_edge(&1, &2, "edge_1_2");
    digraph.add_edge(&2, &3, "edge_2_3");
    digraph.add_edge(&3, &4, "edge_3_4");
    digraph.add_edge(&4, &0, "edge_4_0");

    println!("Added {} edges", digraph.number_of_edges());

    // List all nodes
    println!("\nNodes:");
    for node in digraph.nodes() {
        println!("  {}", node);
    }

    // List all edges
    println!("\nEdges:");
    for (u, v, edge) in digraph.edges() {
        println!("  {} -> {}: {}", u, v, edge);
    }

    // Show neighbors of node 0
    println!("\nNeighbors of node 0:");
    for (neighbor, edge) in digraph.neighbors(&0) {
        println!("  -> {} via {}", neighbor, edge);
    }

    // Show predecessors of node 0
    println!("\nPredecessors of node 0:");
    for (predecessor, edge) in digraph.predecessors(&0) {
        println!("  <- {} via {}", predecessor, edge);
    }

    // Add node attributes
    println!("\nAdding node attributes...");
    let attrs = digraph.node_attributes_mut(&0);
    attrs.insert("color".to_string(), "red".to_string());
    attrs.insert("weight".to_string(), "10".to_string());

    let attrs = digraph.node_attributes_mut(&1);
    attrs.insert("color".to_string(), "blue".to_string());

    // Show node attributes
    println!("Node 0 attributes: {:?}", digraph.node_attributes(&0));
    println!("Node 1 attributes: {:?}", digraph.node_attributes(&1));

    println!("\n=== Example completed successfully ===");
}
