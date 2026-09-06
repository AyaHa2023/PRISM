"""Part 4 — 4-quadrant loop for PwC internal + client/vendor ecosystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterator

import networkx as nx
import random

from ..data_layer.state_db import StateDatabase
from ..graph.network import build_workplace_network, get_neighbors
from ..graph.network_metrics import calculate_network_metrics
from ..graph.policy_graph_backend import build_policy_graph
from ..graph.typed_graph import summarize_typed_graph
from ..models.personas import AgentExternal, AgentInternal
from ..ontology.llm_extractor import extract_policy_ontology_llm
from ..simulation.factory import generate_external_stakeholders, generate_internal_employees
from ..simulation.llm_brain import call_llm
from ..simulation.message_bus import AgentMessage, route_to_neighbors
from ..simulation.network_propagation import apply_neighbor_influence
from ..simulation.persona_profiles import generate_persona_profile, profile_to_prompt
from ..simulation.impact_model import compute_parameter_effects

ENGAGEMENT_LEAD = "Engagement Lead"
CLIENT_ROLE = "Client (Fortune 500)"


@dataclass
class SimulationStep:
    day: int
    quadrant: str
    agent_name: str
    message: str
    stress: int
    trust: int
    sentiment: str = "neutral"
    event_type: str = "message"


@dataclass
class SimulationResult:
    steps: list[SimulationStep] = field(default_factory=list)
    graph: nx.Graph | None = None
    employees: list[AgentInternal] = field(default_factory=list)
    partners: list[AgentExternal] = field(default_factory=list)
    leak_message: str = ""
    policy_graph: nx.Graph | None = None
    network_metrics: dict = field(default_factory=dict)
    messages: list[AgentMessage] = field(default_factory=list)
    policy_ontology: object | None = None
    ontology_metadata: dict = field(default_factory=dict)
    graph_backend: str = "networkx"
    llm_model: str = "mock"
    parameter_effects: object | None = None
    parameter_effects: object | None = None


def run_simulation(
    policy_text: str,
    start_morale: int = 75,
    start_trust: int = 85,
    days: int = 10,
    employee_count: int = 5,
    db: StateDatabase | None = None,
    use_mock_llm: bool = True,
    llm_model: str = "llama3.1:latest",
    graph_backend: str = "networkx",
    graph_database: str | None = None,
    on_step: Callable[[SimulationStep], None] | None = None,
    random_seed: int | None = 42,
) -> SimulationResult:
    if random_seed is not None:
        random.seed(random_seed)
    if db:
        db.clear_metrics()
        db.log_run(policy_text, start_morale, start_trust)

    employees = generate_internal_employees(count=employee_count, start_morale=start_morale, start_trust=start_trust)
    external = generate_external_stakeholders(count=2, start_trust=start_trust)
    graph = build_workplace_network(employees, external)
    policy_graph = build_policy_graph(policy_text, backend=graph_backend, database=graph_database)
    policy_ontology, ontology_metadata = extract_policy_ontology_llm(
        policy_text,
        use_mock=use_mock_llm,
        model=llm_model,
    )
    parameter_effects = compute_parameter_effects(
        employee_count=employee_count,
        start_morale=start_morale,
        start_trust=start_trust,
        days=days,
        policy_severity=policy_ontology.severity,
    )
    policy_graph_context = summarize_typed_graph(policy_graph)

    result = SimulationResult(
        graph=graph,
        employees=employees,
        partners=external,
        policy_graph=policy_graph,
        network_metrics=calculate_network_metrics(graph),
        policy_ontology=policy_ontology,
        ontology_metadata=ontology_metadata,
        graph_backend=graph_backend,
        llm_model=llm_model if not use_mock_llm else "mock",
        parameter_effects=parameter_effects,
    )
    for agent in [*employees, *external]:
        stored_profile = db.load_agent_profile(agent.name) if db else None
        agent.profile = stored_profile or generate_persona_profile(agent, use_mock=use_mock_llm, model=llm_model)
        if db:
            db.store_agent_profile(agent.name, agent.profile)
    leak_msg = ""

    def emit(step: SimulationStep) -> None:
        result.steps.append(step)
        if on_step:
            on_step(step)

    all_agents: list[AgentInternal | AgentExternal] = [*employees, *external]
    day_messages: dict[str, str] = {}

    # Staff roles react in Q2; Partners included but with partner-oversight context
    reacting_staff = [e for e in employees if e.role.title != "Partner"] or employees

    for day in range(1, days + 1):
        day_messages = {}
        day_incoming: list[AgentMessage] = []

        # Q1 — Internal-Formal: Partner Committee announcement
        if day == 1:
            memo = (
                f"PARTNER COMMITTEE MEMO — {policy_text}\n"
                "Effective next engagement cycle. All practice lines must align utilization and client delivery plans."
            )
            step = SimulationStep(
                day=day,
                quadrant="Q1 Internal-Formal",
                agent_name="Partner Committee",
                message=memo,
                stress=0,
                trust=0,
                event_type="memo",
            )
            emit(step)
            if db:
                db.log_metrics(day, all_agents, {"Partner Committee": memo}, "Q1")

        # Q2 — Internal-Informal: Teams backchannel / engagement team gossip
        for emp in reacting_staff:
            team = get_neighbors(graph, emp.name, relation="Engagement_Team")
            manager = get_neighbors(graph, emp.name, relation="Reports_To")
            context = (
                f"Engagement team chatter ({', '.join(team) or 'none'}). "
                f"Manager chain: {', '.join(manager) or 'none'}. "
                f"Neighbor messages: {[message.text for message in day_incoming if message.receiver == emp.name] or 'none'}. "
                + ("Utilization pressure is rising." if day > 2 else "First reactions after partner memo.")
            )
            memory_context = db.build_agent_context(emp.name) if db else ""
            res = call_llm(
                emp,
                policy_text,
                context,
                use_mock=use_mock_llm,
                model=llm_model,
                graph_context=policy_graph_context,
                memory_context=memory_context,
                profile_context=profile_to_prompt(emp.profile),
            )
            emp.metrics.stress = res["updated_stress"]
            emp.metrics.trust = res["updated_trust"]
            scale_delta = round(parameter_effects.estimated_stress_increase / max(days, 1) / 10)
            emp.metrics.apply_delta(stress_delta=scale_delta)
            apply_neighbor_influence(emp, day_incoming)
            day_messages[emp.name] = res["message"]
            if db:
                db.store_agent_memory(emp.name, "reaction", res["message"], "Q2")
            routed = route_to_neighbors(graph, day, emp.name, res["message"], res.get("sentiment", "neutral"))
            result.messages.extend(routed)
            day_incoming.extend(routed)
            if db:
                for message in routed:
                    db.store_message(message.to_dict())
            emit(
                SimulationStep(
                    day=day,
                    quadrant="Q2 Internal-Informal",
                    agent_name=f"{emp.name} ({emp.role.title})",
                    message=res["message"],
                    stress=emp.metrics.stress,
                    trust=emp.metrics.trust,
                    sentiment=res.get("sentiment", "neutral"),
                )
            )

        if db:
            db.log_metrics(day, employees, day_messages, "Q2")

        # Q3 — External-Informal: Engagement Lead leaks to client if team stress high
        staff_stress = [e.metrics.stress for e in reacting_staff]
        avg_stress = sum(staff_stress) / len(staff_stress) if staff_stress else 0
        leak_msg = ""
        if avg_stress > 70:
            leads = [e for e in employees if e.role.title == ENGAGEMENT_LEAD]
            if leads:
                leaker = leads[0]
                clients = get_neighbors(graph, leaker.name, relation="Engagement_Lead")
                if clients:
                    leak_msg = (
                        f"Off the record — engagement team stress at {avg_stress:.0f}/100. "
                        "Audit deliverable timelines may slip; we're managing partner expectations."
                    )
                    emit(
                        SimulationStep(
                            day=day,
                            quadrant="Q3 External-Informal",
                            agent_name=leaker.name,
                            message=f"→ {clients[0]}: {leak_msg}",
                            stress=leaker.metrics.stress,
                            trust=leaker.metrics.trust,
                            event_type="leak",
                        )
                    )

        result.leak_message = leak_msg

        # Q4 — External-Formal: Client SLA / vendor contract reaction
        if leak_msg:
            clients = [e for e in external if e.role.title == CLIENT_ROLE]
            for client in clients:
                memory_context = db.build_agent_context(client.name) if db else ""
                res = call_llm(
                    client,
                    f"Engagement lead leak: {leak_msg}",
                    "",
                    use_mock=use_mock_llm,
                    model=llm_model,
                    graph_context=policy_graph_context,
                    memory_context=memory_context,
                    profile_context=profile_to_prompt(client.profile),
                )
                client.metrics.trust = res["updated_trust"]
                if db:
                    db.store_agent_memory(client.name, "reaction", res["message"], "Q4")
                action = (
                    "CRITICAL: Formal engagement SLA review requested; continuity plan demanded."
                    if client.metrics.trust < 50
                    else "Client monitoring delivery risk; no formal escalation yet."
                )
                emit(
                    SimulationStep(
                        day=day,
                        quadrant="Q4 External-Formal",
                        agent_name=client.name,
                        message=f"{action} | Client: {res['message']}",
                        stress=client.metrics.stress,
                        trust=client.metrics.trust,
                        sentiment=res.get("sentiment", "neutral"),
                        event_type="contract",
                    )
                )
            if db:
                db.log_metrics(day, clients, {c.name: leak_msg for c in clients}, "Q4")

    return result


def iter_quadrant_summary(result: SimulationResult) -> Iterator[tuple[str, int]]:
    counts: dict[str, int] = {}
    for step in result.steps:
        counts[step.quadrant] = counts.get(step.quadrant, 0) + 1
    yield from counts.items()
