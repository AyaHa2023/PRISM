from __future__ import annotations

from collections import defaultdict

import networkx as nx

from .knowledge_graph import extract_policy_entities


NODE_ALIASES = {
    "employee": "Employees",
    "employees": "Employees",
    "manager": "Managers",
    "managers": "Managers",
    "hr": "HR",
    "human resources": "HR",
    "client": "Clients",
    "clients": "Clients",
    "partner": "Partners",
    "partners": "Partners",
    "consultant": "Consultants",
    "consultants": "Consultants",
    "leadership": "Leadership",
    "policy": "Policy",
    "return to office": "Return-to-office policy",
    "return-to-office": "Return-to-office policy",
    "salary": "Salary",
    "bonus": "Bonus",
    "stress": "Stress",
    "trust": "Trust",
    "morale": "Morale",
    "risk": "Risk",
    "contract": "Contract",
    "sla": "SLA",
}

RELATIONS = [
    "REPORTS_TO",
    "WORKS_WITH",
    "AFFECTS",
    "TRUSTS",
    "DEPENDS_ON",
    "LEAKS_TO",
    "RESPONDS_TO",
    "INFLUENCES",
]


def canonicalize_label(label: str) -> str:
    text = (label or "").strip().lower().replace("-", " ")
    if not text:
        return "Unknown"
    return NODE_ALIASES.get(text, text.title())


def build_typed_policy_graph(policy_text: str) -> nx.Graph:
    graph = nx.DiGraph()
    text = (policy_text or "").strip()
    if not text:
        graph.add_node("Policy", node_type="Policy", label="Policy")
        return graph

    lower = text.lower()
    policy_name = "Policy"
    graph.add_node(policy_name, node_type="Policy", label="Policy")

    for extracted, extracted_type in extract_policy_entities(text):
        if extracted == policy_name:
            continue
        node_type = "Stakeholder" if extracted_type == "Stakeholder" else extracted_type
        graph.add_node(extracted, node_type=node_type, label=extracted)
        graph.add_edge(policy_name, extracted, relation="MENTIONS", channel="extraction")

    stakeholder_tokens = [
        ("Employees", "Stakeholder"),
        ("Managers", "Stakeholder"),
        ("HR", "Stakeholder"),
        ("Clients", "Stakeholder"),
        ("Partners", "Stakeholder"),
        ("Consultants", "Stakeholder"),
        ("Leadership", "Stakeholder"),
    ]

    for label, node_type in stakeholder_tokens:
        if label.lower() in lower or ("employee" in lower and label == "Employees") or ("client" in lower and label == "Clients"):
            graph.add_node(label, node_type=node_type, label=label)
            graph.add_edge(policy_name, label, relation="AFFECTS", channel="semantic")

    if "return to office" in lower or "return-to-office" in lower or "rto" in lower:
        policy_label = "Return-to-office policy"
        graph.add_node(policy_label, node_type="Policy", label=policy_label)
        graph.add_edge(policy_name, policy_label, relation="INCLUDES", channel="semantic")
        for stakeholder in ["Employees", "Managers", "Clients"]:
            if stakeholder in graph.nodes:
                graph.add_edge(policy_label, stakeholder, relation="AFFECTS", channel="semantic")

    if "salary" in lower or "bonus" in lower or "cut" in lower:
        pay_label = "Compensation change"
        graph.add_node(pay_label, node_type="Event", label=pay_label)
        graph.add_edge(policy_name, pay_label, relation="INCLUDES", channel="semantic")
        for stakeholder in ["Employees", "Clients"]:
            if stakeholder in graph.nodes:
                graph.add_edge(pay_label, stakeholder, relation="AFFECTS", channel="semantic")

    if "trust" in lower or "risk" in lower or "client" in lower:
        risk_label = "Risk"
        graph.add_node(risk_label, node_type="Risk", label=risk_label)
        graph.add_edge(policy_name, risk_label, relation="IMPACTS", channel="semantic")
        if "Clients" in graph.nodes:
            graph.add_edge(risk_label, "Clients", relation="AFFECTS", channel="semantic")

    if not graph.number_of_edges():
        graph.add_edge(policy_name, "Employees", relation="AFFECTS", channel="semantic")

    return graph


def summarize_typed_graph(graph: nx.Graph) -> str:
    nodes = []
    for node, data in graph.nodes(data=True):
        node_type = data.get("node_type", "Unknown")
        nodes.append(f"{node} ({node_type})")

    edges = []
    for u, v, data in graph.edges(data=True):
        edges.append(f"{u} -> {v} [{data.get('relation', 'RELATED')}]")

    return "; ".join(nodes) + " | " + "; ".join(edges)
