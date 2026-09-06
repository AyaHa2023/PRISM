from __future__ import annotations

import argparse
import json
import os
import sys

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the local Ollama server and installed models.")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "llama3.1:latest"))
    parser.add_argument("--probe", action="store_true", help="Send one small generation request after the health check.")
    args = parser.parse_args()
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as error:
        print(json.dumps({"ok": False, "base_url": base_url, "error": str(error)}, indent=2))
        return 1

    models = [item.get("name", "") for item in payload.get("models", [])]
    result = {
        "ok": True,
        "base_url": base_url,
        "models": models,
        "selected_model": args.model,
        "selected_model_available": args.model in models or args.model.removesuffix(":latest") in models,
    }

    if args.probe:
        try:
            probe = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": args.model,
                    "prompt": 'Reply with exactly this JSON: {"ok": true}',
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0},
                },
                timeout=120,
            )
            probe.raise_for_status()
            result["probe_response"] = probe.json().get("response", "")
            result["probe_ok"] = bool(result["probe_response"])
        except requests.RequestException as error:
            result["probe_ok"] = False
            result["probe_error"] = str(error)

    print(json.dumps(result, indent=2))
    return 0 if result["ok"] and result.get("probe_ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
