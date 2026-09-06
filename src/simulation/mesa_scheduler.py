from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

try:
    from mesa import Agent, Model
except ImportError:  # pragma: no cover - optional until Mesa phase is installed
    Agent = None
    Model = None


@dataclass
class TickResult:
    day: int
    active_agents: int


@dataclass
class PopulationRun:
    agent_count: int
    days: int
    ticks: list[TickResult]


@dataclass
class PrismPopulationRun:
    agent_count: int
    days: int
    average_stress: float
    average_trust: float
    ticks: list[TickResult]


if Agent is not None and Model is not None:
    class PrismMesaAgent(Agent):
        def step(self) -> None:
            return None


    class PrismMesaModel(Model):
        def __init__(self, agent_count: int, seed: int | None = None):
            super().__init__(seed=seed)
            for _ in range(agent_count):
                PrismMesaAgent(self)

        def step(self) -> None:
            self.agents.do("step")


def run_mesa_ticks(agent_count: int, days: int, step: Callable[[int], None]) -> list[TickResult]:
    """Small scheduler boundary; the domain engine remains independent of Mesa."""
    if Agent is None or Model is None:
        raise RuntimeError("Install Mesa with `pip install mesa` to use the Mesa scheduler.")
    model = PrismMesaModel(agent_count)
    results = []
    for day in range(1, days + 1):
        model.step()
        step(day)
        results.append(TickResult(day=day, active_agents=agent_count))
    return results


def validate_population_scale(agent_counts: list[int], days: int = 3) -> list[PopulationRun]:
    """Run scheduler-only scale checks before coupling Mesa activation to domain behavior."""
    runs = []
    for agent_count in agent_counts:
        ticks = run_mesa_ticks(agent_count, days, lambda _day: None)
        runs.append(PopulationRun(agent_count=agent_count, days=days, ticks=ticks))
    return runs


def run_prism_population(agent_count: int, days: int, initial_stress: float = 25.0, initial_trust: float = 80.0) -> PrismPopulationRun:
    """Run a lightweight Mesa population benchmark using Prism stress/trust state.

    This validates scheduler scaling independently from LLM latency. The full engine
    remains responsible for policy semantics and Ollama reactions.
    """
    if Agent is None or Model is None:
        raise RuntimeError("Install Mesa with `pip install mesa` to use the Mesa scheduler.")

    class PopulationAgent(Agent):
        def __init__(self, model):
            super().__init__(model)
            self.stress = initial_stress
            self.trust = initial_trust

        def step(self) -> None:
            self.stress = min(100.0, self.stress + 0.5)
            self.trust = max(0.0, self.trust - 0.1)

    class PopulationModel(Model):
        def __init__(self):
            super().__init__()
            for _ in range(agent_count):
                PopulationAgent(self)

        def step(self) -> None:
            self.agents.do("step")

    model = PopulationModel()
    ticks: list[TickResult] = []
    for day in range(1, days + 1):
        model.step()
        ticks.append(TickResult(day=day, active_agents=agent_count))
    agents = list(model.agents)
    return PrismPopulationRun(
        agent_count=agent_count,
        days=days,
        average_stress=round(sum(agent.stress for agent in agents) / len(agents), 3),
        average_trust=round(sum(agent.trust for agent in agents) / len(agents), 3),
        ticks=ticks,
    )
