from __future__ import annotations

import json
from typing import Any

from .engine import SimulationResult
from .multi_agent_workflow import SPECIALISTS
from .reporting import summarize_result


def run_crewai_review(result: SimulationResult, model: str = "ollama/llama3.1:latest") -> dict[str, Any]:
    """Run the specialist review through CrewAI when the optional package is installed.

    CrewAI is intentionally optional. The native workflow remains the tested default.
    """
    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError as error:  # pragma: no cover - depends on optional installation
        raise RuntimeError(
            "CrewAI is optional and not installed. Install requirements-optional.txt to enable it."
        ) from error

    summary = json.dumps(summarize_result(result), indent=2)
    agents = []
    tasks = []
    for name, instruction in SPECIALISTS:
        specialist = Agent(
            role=name,
            goal=instruction,
            backstory="A Prism specialist who reports only evidence from the supplied simulation.",
            verbose=False,
            allow_delegation=False,
            llm=model,
        )
        agents.append(specialist)
        tasks.append(
            Task(
                description=f"{instruction}\nSimulation summary:\n{summary}\nReturn a concise evidence-based finding.",
                expected_output="A finding with risks and confidence.",
                agent=specialist,
            )
        )

    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
    result_value = crew.kickoff()
    return {"source": "crewai", "result": str(result_value)}
