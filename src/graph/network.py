"""PwC org topology: Partner → Manager → consultants; Engagement Lead → Client."""

from __future__ import annotations

import networkx as nx

from ..models.personas import AgentExternal, AgentInternal

HIERARCHY = [
    ("Partner", "Manager"),
    ("Manager", "Senior Consultant"),
    ("Manager", "Associate"),
]

ROLE_CLIENT_BRIDGE = "Engagement Lead"
CLIENT_ROLE = "Client (Fortune 500)"
VENDOR_ROLE = "Vendor Partner"


def _by_role(agents: list[AgentInternal], title: str) -> list[AgentInternal]:
    return [a for a in agents if a.role.title == title]


def build_workplace_network(
    employees: list[AgentInternal],
    external: list[AgentExternal],
) -> nx.Graph:
    """
    Internal loop: practice-line coworkers + formal reporting chain.
    External loop: Engagement Lead ↔ Client; Manager ↔ Vendor (formal).
    """
    graph = nx.Graph()

    for emp in employees:
        graph.add_node(
            emp.name,
            obj=emp,
            agent_type="internal",
            department=emp.department,
            role=emp.role.title,
        )

    for ext in external:
        graph.add_node(
            ext.name,
            obj=ext,
            agent_type="external",
            role=ext.role.title,
        )

    # Informal: coworkers on same engagement / practice line
    by_practice: dict[str, list[str]] = {}
    for emp in employees:
        by_practice.setdefault(emp.department, []).append(emp.name)

    for names in by_practice.values():
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                graph.add_edge(a, b, relation="Engagement_Team", channel="informal")

    # Formal hierarchy: Partner → Manager → consultants
    for senior_role, junior_role in HIERARCHY:
        seniors = _by_role(employees, senior_role)
        juniors = _by_role(employees, junior_role)
        for senior in seniors:
            for junior in juniors:
                if senior.department == junior.department:
                    graph.add_edge(
                        senior.name,
                        junior.name,
                        relation="Reports_To",
                        channel="formal",
                    )

    clients = [e for e in external if e.role.title == CLIENT_ROLE]
    vendors = [e for e in external if e.role.title == VENDOR_ROLE]
    engagement_leads = _by_role(employees, ROLE_CLIENT_BRIDGE)
    managers = _by_role(employees, "Manager")

    # Engagement Lead → Client (client delivery + informal leak path)
    if engagement_leads and clients:
        graph.add_edge(
            engagement_leads[0].name,
            clients[0].name,
            relation="Engagement_Lead",
            channel="informal",
        )
        graph.add_edge(
            engagement_leads[0].name,
            clients[0].name,
            relation="Client_Delivery",
            channel="formal",
        )

    # Manager → Vendor (outsourcing / shared services relationship)
    if managers and vendors:
        graph.add_edge(
            managers[0].name,
            vendors[0].name,
            relation="Vendor_Contract",
            channel="formal",
        )

    # Partner visibility to Engagement Lead (partner pressure channel)
    partners = _by_role(employees, "Partner")
    if partners and engagement_leads:
        graph.add_edge(
            partners[0].name,
            engagement_leads[0].name,
            relation="Partner_Oversight",
            channel="formal",
        )

    return graph


def get_neighbors(graph: nx.Graph, name: str, relation: str | None = None) -> list[str]:
    neighbors = []
    for n in graph.neighbors(name):
        edge = graph.get_edge_data(name, n) or {}
        if relation is None or edge.get("relation") == relation:
            neighbors.append(n)
    return neighbors
