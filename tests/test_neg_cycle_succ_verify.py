"""Regression test for successor-orientation cycle verification.

Successor relaxation enforces the mirror-image inequality of predecessor
relaxation, so its negativity test must be mirrored too.  `howard_succ` used to
skip verification entirely; this test pins the successor path to the same
guarantee as `howard_pred`: every yielded cycle is genuinely negative.
"""

from digraphx.neg_cycle_q import NegCycleFinderQ


def test_howard_succ_yields_only_negative_cycles() -> None:
    digraph = {"a": {"b": 1.0}, "b": {"c": 1.0}, "c": {"a": -3.0}}
    finder = NegCycleFinderQ(digraph)
    dist = {node: 0.0 for node in digraph}

    cycles = list(finder.howard_succ(dist, lambda edge: edge, lambda old, new: True))

    assert cycles
    assert all(sum(cycle) < 0 for cycle in cycles)


def test_howard_succ_and_pred_agree() -> None:
    digraph = {"a": {"b": 1.0}, "b": {"c": 1.0}, "c": {"a": -3.0}}
    finder = NegCycleFinderQ(digraph)

    succ = list(
        finder.howard_succ(
            {node: 0.0 for node in digraph}, lambda edge: edge, lambda old, new: True
        )
    )
    pred = list(
        finder.howard_pred(
            {node: 0.0 for node in digraph}, lambda edge: edge, lambda old, new: True
        )
    )

    assert sum(succ[0]) == sum(pred[0])
