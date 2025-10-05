from fractions import Fraction
from digraphx.min_cycle_ratio import set_default, CycleRatioAPI
from digraphx.parametric import MaxParametricSolver
from digraphx.neg_cycle import NegCycleFinder as NegCycleFinder_neg_cycle
from digraphx.neg_cycle_q import NegCycleFinder as NegCycleFinder_neg_cycle_q
from digraphx.tiny_digraph import DiGraphAdapter, TinyDiGraph


def test_min_cycle_ratio_set_default_doctest():
    digraph = {
        'a': {'b': {'cost': 5}},
        'b': {'c': {'cost': 3}},
        'c': {'a': {'cost': -2}}
    }
    set_default(digraph, 'time', 1)
    assert digraph['a']['b']['time'] == 1
    assert digraph['b']['c']['time'] == 1
    assert digraph['c']['a']['time'] == 1


def test_min_cycle_ratio_cycle_ratio_api_distance_doctest():
    digraph = {
        'a': {'b': {'cost': 5, 'time': 1}},
        'b': {'c': {'cost': 3, 'time': 1}},
        'c': {'a': {'cost': -2, 'time': 1}}
    }
    api = CycleRatioAPI(digraph, Fraction)
    assert api.distance(Fraction(1, 2), digraph['a']['b']) == Fraction(9, 2)


def test_min_cycle_ratio_cycle_ratio_api_zero_cancel_doctest():
    digraph = {
        'a': {'b': {'cost': 5, 'time': 1}},
        'b': {'c': {'cost': 3, 'time': 1}},
        'c': {'a': {'cost': -2, 'time': 1}}
    }
    api = CycleRatioAPI(digraph, Fraction)
    cycle = [digraph['a']['b'], digraph['b']['c'], digraph['c']['a']]
    assert api.zero_cancel(cycle) == Fraction(2, 1)


def test_parametric_max_parametric_solver_run_doctest():
    digraph = {
        'a': {'b': {'cost': 5, 'time': 1}},
        'b': {'c': {'cost': 3, 'time': 1}},
        'c': {'a': {'cost': -2, 'time': 1}}
    }
    omega = CycleRatioAPI(digraph, Fraction)
    solver = MaxParametricSolver(digraph, omega)
    dist = {node: Fraction(0) for node in digraph}
    ratio, cycle = solver.run(dist, Fraction(10))
    assert ratio == Fraction(2, 1)


def test_neg_cycle_relax_doctest():
    digraph = {
        'a': {'b': 1, 'c': 4},
        'b': {'c': 2},
        'c': {'a': -5}
    }
    dist = {'a': 0, 'b': float('inf'), 'c': float('inf')}
    finder = NegCycleFinder_neg_cycle(digraph)
    finder.relax(dist, lambda edge: edge)
    assert dist['b'] == 1
    assert dist['c'] == 3


def test_neg_cycle_cycle_list_doctest():
    digraph = {
        'a': {'b': 'ab'},
        'b': {'c': 'bc'},
        'c': {'a': 'ca'}
    }
    finder = NegCycleFinder_neg_cycle(digraph)
    finder.pred = {'b': ('a', 'ab'), 'c': ('b', 'bc'), 'a': ('c', 'ca')}
    assert finder.cycle_list('a') == ['ca', 'bc', 'ab']


def test_neg_cycle_is_negative_doctest():
    digraph = {
        'a': {'b': 1},
        'b': {'c': 1},
        'c': {'a': -3}
    }
    dist = {'a': 0, 'b': 1, 'c': 2}
    finder = NegCycleFinder_neg_cycle(digraph)
    finder.pred = {'b': ('a', 1), 'c': ('b', 1), 'a': ('c', -3)}
    assert finder.is_negative('a', dist, lambda edge: edge) is True


def test_neg_cycle_q_relax_pred_doctest():
    digraph = {
        'a': {'b': 1, 'c': 4},
        'b': {'c': 2},
        'c': {'a': -5}
    }
    dist = {'a': 0, 'b': float('inf'), 'c': float('inf')}
    finder = NegCycleFinder_neg_cycle_q(digraph)
    finder.relax_pred(dist, lambda edge: edge, lambda old, new: True)
    assert dist['b'] == 1
    assert dist['c'] == 3


def test_neg_cycle_q_relax_succ_doctest():
    digraph = {
        'a': {'b': 1},
        'b': {}
    }
    dist = {'a': 0, 'b': 5}
    finder = NegCycleFinder_neg_cycle_q(digraph)
    finder.relax_succ(dist, lambda edge: edge, lambda old, new: True)
    assert dist['a'] == 4


def test_neg_cycle_q_cycle_list_doctest():
    digraph = {
        'a': {'b': 'ab'},
        'b': {'c': 'bc'},
        'c': {'a': 'ca'}
    }
    finder = NegCycleFinder_neg_cycle_q(digraph)
    finder.pred = {'b': ('a', 'ab'), 'c': ('b', 'bc'), 'a': ('c', 'ca')}
    assert finder.cycle_list('a', finder.pred) == ['ca', 'bc', 'ab']


def test_neg_cycle_q_is_negative_doctest():
    digraph = {
        'a': {'b': 1},
        'b': {'c': 1},
        'c': {'a': -3}
    }
    dist = {'a': 0, 'b': 1, 'c': 2}
    finder = NegCycleFinder_neg_cycle_q(digraph)
    finder.pred = {'b': ('a', 1), 'c': ('b', 1), 'a': ('c', -3)}
    assert finder.is_negative('a', dist, lambda edge: edge) is True


def test_tiny_digraph_adapter_items_doctest():
    gr = DiGraphAdapter()
    gr.add_edge(1, 2)
    gr.add_edge(2, 3)
    assert sorted(list(gr.items())) == [(1, {2: {}}), (2, {3: {}}), (3, {})]


def test_tiny_digraph_cheat_node_dict_doctest():
    gr = TinyDiGraph()
    gr.init_nodes(3)
    node_dict = gr.cheat_node_dict()
    assert list(node_dict.keys()) == [0, 1, 2]
    assert node_dict[0] == {}


def test_tiny_digraph_cheat_adjlist_outer_dict_doctest():
    gr = TinyDiGraph()
    gr.init_nodes(2)
    adj_list = gr.cheat_adjlist_outer_dict()
    assert list(adj_list.keys()) == [0, 1]
    assert adj_list[0] == {}


def test_tiny_digraph_init_nodes_doctest():
    gr = TinyDiGraph()
    gr.init_nodes(5)
    assert gr.number_of_nodes() == 5
    assert list(gr._node.keys()) == [0, 1, 2, 3, 4]
    assert list(gr._adj.keys()) == [0, 1, 2, 3, 4]
