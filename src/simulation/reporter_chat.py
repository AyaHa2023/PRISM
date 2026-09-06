from __future__ import annotations

import json

from ..llm.ollama_client import OllamaClient
from .reporting import SimulationReport


def ask_reporter(
    question: str,
    report: SimulationReport,
    use_mock: bool = True,
    model: str = "llama3.1:latest",
) -> str:
    if use_mock:
        return (
            "The deterministic reporter can explain only the recorded thresholds. "
            f"Current sentiment is {report.sentiment}, average stress is {report.average_stress}/100, "
            f"and minimum external trust is {report.minimum_external_trust}/100."
        )
    prompt = f"""You are the Prism forecast reporter. Answer the user's question using only this report.
Report JSON:
{json.dumps(report.to_dict(), indent=2)}
User question: {question}
Be concise, cite the relevant risk path or confidence gap, and do not invent data.
"""
    try:
        payload = OllamaClient(model=model).generate(prompt, temperature=0.2, stream=False)
        return str(payload.get("response", "No reporter response returned."))
    except Exception:
        return "The reporter could not reach the configured Ollama model."
