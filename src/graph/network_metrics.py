from __future__ import annotations

import networkx as nx


def calculate_network_metrics(graph: nx.Graph) -> dict:
    if graph.number_of_nodes() == 0:
        return {"node_count": 0, "edge_count": 0, "density": 0.0, "centrality": {}}
    centrality = nx.degree_centrality(graph)
    ranked = sorted(centrality.items(), key=lambda item: item[1], reverse=True)
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "density": round(nx.density(graph), 4),
        "centrality": {name: round(score, 4) for name, score in ranked[:10]},
    }
