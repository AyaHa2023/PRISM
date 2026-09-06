from __future__ import annotations

from html import escape

from ..simulation.engine import SimulationResult


def _quote(value: str) -> str:
    return '"' + escape(str(value)).replace('"', '\\"') + '"'


def scenario_graph_dot(result: SimulationResult) -> str:
    """Build a Graphviz DOT view of policy, agents, topology, and messages."""
    lines = [
        "digraph PrismScenario {",
        "rankdir=LR;",
        "graph [bgcolor=\"transparent\", pad=0.2];",
        "node [shape=box, style=filled, fontname=\"Arial\", color=\"#334155\"];",
    ]
    if result.policy_graph:
        for node, data in result.policy_graph.nodes(data=True):
            node_id = f"policy_{abs(hash(str(node)))}"
            node_type = data.get("node_type", "Concept")
            color = "#fde68a" if node_type == "Policy" else "#fecdd3" if node_type == "Risk" else "#dbeafe"
            lines.append(f"{node_id} [label={_quote(str(node))}, fillcolor=\"{color}\"];")
        for source, target, data in result.policy_graph.edges(data=True):
            source_id = f"policy_{abs(hash(str(source)))}"
            target_id = f"policy_{abs(hash(str(target)))}"
            lines.append(f"{source_id} -> {target_id} [label={_quote(data.get('relation', 'RELATED'))}, color=\"#64748b\"];")

    if result.graph:
        for node, data in result.graph.nodes(data=True):
            node_id = f"agent_{abs(hash(str(node)))}"
            role = data.get("role", data.get("agent_type", "agent"))
            obj = data.get("obj")
            metrics = f"\nS:{obj.metrics.stress} T:{obj.metrics.trust}" if obj else ""
            color = "#bbf7d0" if data.get("agent_type") == "internal" else "#fed7aa"
            label = f"{node}\n{role}{metrics}"
            lines.append(f"{node_id} [label={_quote(label)}, fillcolor=\"{color}\"];")
        for source, target, data in result.graph.edges(data=True):
            source_id = f"agent_{abs(hash(str(source)))}"
            target_id = f"agent_{abs(hash(str(target)))}"
            lines.append(f"{source_id} -> {target_id} [label={_quote(data.get('relation', 'CONNECTED'))}, color=\"#94a3b8\"];")

    for message in result.messages:
        source_id = f"agent_{abs(hash(str(message.sender)))}"
        target_id = f"agent_{abs(hash(str(message.receiver)))}"
        lines.append(
            f"{source_id} -> {target_id} [label={_quote(message.sentiment.upper())}, "
            "color=\"#dc2626\", style=dashed];"
        )
    lines.append("}")
    return "\n".join(lines)
