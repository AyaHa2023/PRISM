from dataclasses import dataclass, field
from typing import Any

from .agents import Metrics, Personality, Role


@dataclass
class AgentBase:
    name: str
    role: Role
    personality: Personality
    metrics: Metrics
    profile: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInternal(AgentBase):
    department: str = "General"


@dataclass
class AgentExternal(AgentBase):
    associated_contract: str = "SLA_standard.pdf"
