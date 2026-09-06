"""Factory — PwC firm roster: partners, consultants, clients, vendors."""

from __future__ import annotations

import random

from ..models.agents import Metrics, Personality, Role
from ..models.personas import AgentExternal, AgentInternal

# Internal firm roles (professional services hierarchy)
ROLES_INTERNAL = [
    Role("Partner", priorities=["firm profitability", "client retention", "people strategy"]),
    Role("Manager", priorities=["engagement delivery", "utilization", "team development"]),
    Role("Senior Consultant", priorities=["work quality", "client deadlines", "upskilling"]),
    Role("Associate", priorities=["learning", "flexibility", "career progression"]),
    Role("Engagement Lead", priorities=["client relationship", "delivery risk", "revenue"]),
]

# External ecosystem
ROLES_EXTERNAL = [
    Role("Client (Fortune 500)", is_internal=False, priorities=["audit quality", "SLA", "continuity"]),
    Role("Vendor Partner", is_internal=False, priorities=["contract margin", "scope", "SLA compliance"]),
]

PERSONALITIES = [
    Personality("Skeptical", "Questions partner committee decisions; shares concerns on Teams backchannels.", 1.2),
    Personality("Client-Focused", "Prioritizes client delivery over internal politics; stress rises when utilization spikes.", 1.1),
    Personality("Conflict-Averse", "Avoids challenging partners publicly; internalizes pressure.", 1.4),
    Personality("Pragmatic", "Looks for workable compromises across engagement constraints.", 0.9),
]

PRACTICE_LINES = ["Assurance", "Consulting", "Tax", "Deals"]

# Default engagement team for demo simulation
DEFAULT_INTERNAL_ROSTER: list[tuple[str, str, str]] = [
    ("Yasmine K.", "Partner", "Consulting"),
    ("Marc D.", "Manager", "Consulting"),
    ("Sara L.", "Senior Consultant", "Consulting"),
    ("Amine R.", "Associate", "Consulting"),
    ("Leila M.", "Engagement Lead", "Consulting"),
]

DEFAULT_EXTERNAL_ROSTER: list[tuple[str, str, str]] = [
    ("Fortune 500 Retail Co.", "Client (Fortune 500)", "ENG-2026-Audit-Transformation"),
    ("Global IT Services Vendor", "Vendor Partner", "MSA-Shared-Services-2026"),
]


def _role_for_title(title: str) -> Role:
    for r in ROLES_INTERNAL + ROLES_EXTERNAL:
        if r.title == title:
            return r
    return Role(title)


def generate_internal_employees(
    count: int = 5,
    start_morale: int = 75,
    start_trust: int = 80,
) -> list[AgentInternal]:
    """Build a PwC-like engagement team (Partner → Associate + Engagement Lead)."""
    roster = list(DEFAULT_INTERNAL_ROSTER[:count])
    if count > len(DEFAULT_INTERNAL_ROSTER):
        extra_roles = ["Senior Consultant", "Associate", "Consultant", "Analyst"]
        for index in range(len(DEFAULT_INTERNAL_ROSTER), count):
            role = extra_roles[(index - len(DEFAULT_INTERNAL_ROSTER)) % len(extra_roles)]
            roster.append((f"Employee {index + 1:03d}", role, "Consulting"))

    stress = max(0, min(100, 100 - start_morale))
    employees: list[AgentInternal] = []

    for name, title, practice in roster:
        # Partners start with lower stress (decision-makers); associates feel change first
        role_stress = stress
        if title == "Partner":
            role_stress = max(15, stress - 15)
        elif title == "Associate":
            role_stress = min(100, stress + 10)

        employees.append(
            AgentInternal(
                name=name,
                role=_role_for_title(title),
                personality=random.choice(PERSONALITIES),
                metrics=Metrics(stress=role_stress, trust=start_trust, loyalty=start_trust),
                department=practice,
            )
        )
    return employees


def generate_external_stakeholders(count: int = 2, start_trust: int = 85) -> list[AgentExternal]:
    """Clients + vendor partners in the external loop."""
    roster = DEFAULT_EXTERNAL_ROSTER[: max(count, 1)]
    stakeholders: list[AgentExternal] = []

    for name, title, contract in roster:
        stakeholders.append(
            AgentExternal(
                name=name,
                role=_role_for_title(title),
                personality=random.choice(PERSONALITIES),
                metrics=Metrics(stress=25, trust=start_trust, loyalty=start_trust - 5),
                associated_contract=contract,
            )
        )
    return stakeholders


# Backward-compatible alias used by engine imports
generate_partners = generate_external_stakeholders
