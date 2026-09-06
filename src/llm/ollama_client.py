from __future__ import annotations

import json
from typing import Any

import requests


class OllamaClient:
    """Minimal Ollama client for local free LLM generation."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str, temperature: float = 0.7, stream: bool = False) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temperature},
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()

    def structured_generate(self, prompt: str, temperature: float = 0.7) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": temperature},
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        raw = response.json()
        content = raw.get("response", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                start = content.index("{")
                end = content.rindex("}") + 1
                return json.loads(content[start:end])
            except Exception:
                return {"message": content, "sentiment": "neutral", "updated_stress": 0, "updated_trust": 0}
