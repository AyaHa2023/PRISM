import networkx as nx

from src.graph.policy_graph_backend import build_policy_graph


def test_networkx_backend_is_explicit_and_default():
    graph = build_policy_graph("Mandatory policy affects employees.")
    assert isinstance(graph, nx.DiGraph)
    assert graph.has_edge("Policy", "Employees")


def test_unknown_backend_fails_clearly():
    try:
        build_policy_graph("Policy", backend="unknown")
    except ValueError as error:
        assert "Unsupported graph backend" in str(error)
    else:
        raise AssertionError("Expected unsupported backend error")
