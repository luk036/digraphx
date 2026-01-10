#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include <doctest/doctest.h>
#include "digraphx/tiny_digraph.hpp"
#include <vector>
#include <string>

TEST_CASE("TinyDiGraph basic operations") {
    using namespace digraphx;

    SUBCASE("Default construction") {
        TinyDiGraph<int, std::string> gr;
        CHECK(gr.number_of_nodes() == 0);
        CHECK(gr.number_of_edges() == 0);
    }

    SUBCASE("Initialize nodes with vector") {
        TinyDiGraph<int, std::string> gr;
        std::vector<int> nodes = {0, 1, 2, 3, 4};
        gr.init_nodes(nodes.begin(), nodes.end());

        CHECK(gr.number_of_nodes() == 5);
        CHECK(gr.number_of_edges() == 0);
    }

    SUBCASE("Initialize nodes with initializer list") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2, 3, 4});

        CHECK(gr.number_of_nodes() == 5);
        CHECK(gr.number_of_edges() == 0);
    }

    SUBCASE("Add edges") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2});

        gr.add_edge(0, 1, "edge01");
        gr.add_edge(1, 2, "edge12");
        gr.add_edge(2, 0, "edge20");

        CHECK(gr.number_of_edges() == 3);
    }

    SUBCASE("Iterate nodes") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2, 3, 4});

        std::vector<int> collected_nodes;
        for (const auto& node : gr.nodes()) {
            collected_nodes.push_back(node);
        }

        CHECK(collected_nodes == std::vector<int>{0, 1, 2, 3, 4});
    }

    SUBCASE("Iterate edges") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2});

        gr.add_edge(0, 1, "edge01");
        gr.add_edge(1, 2, "edge12");
        gr.add_edge(2, 0, "edge20");

        std::vector<std::tuple<int, int, std::string>> collected_edges;
        for (const auto& [u, v, edge] : gr.edges()) {
            collected_edges.emplace_back(u, v, edge);
        }

        CHECK(collected_edges.size() == 3);
        bool found01 = false, found12 = false, found20 = false;
        for (const auto& [u, v, edge] : collected_edges) {
            if (u == 0 && v == 1 && edge == "edge01") found01 = true;
            if (u == 1 && v == 2 && edge == "edge12") found12 = true;
            if (u == 2 && v == 0 && edge == "edge20") found20 = true;
        }
        CHECK(found01);
        CHECK(found12);
        CHECK(found20);
    }

    SUBCASE("Neighbors iteration") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2, 3});

        gr.add_edge(0, 1, "edge01");
        gr.add_edge(0, 2, "edge02");
        gr.add_edge(0, 3, "edge03");

        std::vector<std::pair<int, std::string>> neighbors;
        for (const auto& [neighbor, edge] : gr.neighbors(0)) {
            neighbors.emplace_back(neighbor, edge);
        }

        CHECK(neighbors.size() == 3);
        bool found1 = false, found2 = false, found3 = false;
        for (const auto& [n, e] : neighbors) {
            if (n == 1 && e == "edge01") found1 = true;
            if (n == 2 && e == "edge02") found2 = true;
            if (n == 3 && e == "edge03") found3 = true;
        }
        CHECK(found1);
        CHECK(found2);
        CHECK(found3);
    }

    SUBCASE("Predecessors iteration") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2, 3});

        gr.add_edge(1, 0, "edge10");
        gr.add_edge(2, 0, "edge20");
        gr.add_edge(3, 0, "edge30");

        std::vector<std::pair<int, std::string>> predecessors;
        for (const auto& [pred, edge] : gr.predecessors(0)) {
            predecessors.emplace_back(pred, edge);
        }

        CHECK(predecessors.size() == 3);
        bool found1 = false, found2 = false, found3 = false;
        for (const auto& [p, e] : predecessors) {
            if (p == 1 && e == "edge10") found1 = true;
            if (p == 2 && e == "edge20") found2 = true;
            if (p == 3 && e == "edge30") found3 = true;
        }
        CHECK(found1);
        CHECK(found2);
        CHECK(found3);
    }

    SUBCASE("Node attributes") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1});

        auto& attrs0 = gr.node_attributes_mut(0);
        attrs0["color"] = "red";
        attrs0["weight"] = "10";

        auto& attrs1 = gr.node_attributes_mut(1);
        attrs1["color"] = "blue";

        const auto& const_attrs0 = gr.node_attributes(0);
        CHECK(const_attrs0.at("color") == "red");
        CHECK(const_attrs0.at("weight") == "10");

        const auto& const_attrs1 = gr.node_attributes(1);
        CHECK(const_attrs1.at("color") == "blue");
    }

    SUBCASE("Exception on invalid node access") {
        TinyDiGraph<int, std::string> gr;
        gr.init_nodes({0, 1, 2});

        CHECK_THROWS_AS(gr.add_edge(0, 5, "edge05"), std::out_of_range);
        CHECK_THROWS_AS(gr.neighbors(5), std::out_of_range);
        CHECK_THROWS_AS(gr.predecessors(5), std::out_of_range);
        CHECK_THROWS_AS(gr.node_attributes(5), std::out_of_range);
        CHECK_THROWS_AS(gr.node_attributes_mut(5), std::out_of_range);
    }
}
