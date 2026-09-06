# Ollama setup for PwC Prism

This guide explains how to connect the project to local LLM reasoning using Ollama. This is the next realistic upgrade after the spaCy graph layer and the ontology schema.

---

## 1) What you need

You need:
- a laptop with Ollama installed
- a local model such as `llama3.1` or `mistral`
- local access to `http://localhost:11434`

You do not need a password or API key for this local setup.

---

## 2) Install Ollama

If Ollama is not installed yet, install it from the official site:

- https://ollama.com/download

Then verify it runs:

```powershell
ollama --version
ollama list
```

If the command is not recognized, restart the terminal and check that Ollama is running in the background.

---

## 3) Pull a model

Use a lightweight local model first:

```powershell
ollama pull llama3.1
```

Alternative options:

```powershell
ollama pull mistral
ollama pull qwen2.5
```

For a student project, `llama3.1` is a good default.

---

## 4) Test the local server

In a terminal, run:

```powershell
ollama run llama3.1
```

Then type a sample prompt:

```text
Give me a short workplace reaction to a mandatory return-to-office policy.
```

If it responds, the local model is working.

---

## 5) Link it to the project

The project already contains an Ollama client in:

- [src/llm/ollama_client.py](../src/llm/ollama_client.py)

The simulation brain already tries to use Ollama when `use_mock=False` in:

- [src/simulation/llm_brain.py](../src/simulation/llm_brain.py)

The project also provides a health check:

```powershell
python scripts/check_ollama.py --model llama3.1:latest
```

For one small structured-generation probe:

```powershell
python scripts/check_ollama.py --model llama3.1:latest --probe
```

The probe confirms that the model can return the JSON format required by agent reactions.

You can set an environment variable if needed:

```powershell
$env:OLLAMA_BASE_URL="http://localhost:11434"
```

Then call the simulation with:

```python
result = run_simulation(policy_text, use_mock_llm=False)
```

The dashboard has the same controls in its sidebar:

- enable `Use local Ollama LLM`
- enter the exact model tag, normally `llama3.1:latest`
- run a small one-day simulation first

The live prompt now contains the policy ontology, typed graph context, and prior SQLite memory for that agent. Ollama generates the reaction; Prism clamps the returned stress and trust values to 0-100 and falls back to the mock brain if the request fails.

---

## 6) When you need my intervention

I can help with the code, but I cannot complete the following on your machine without your action:

- installing Ollama itself
- pulling the model
- starting the local server
- approving the model license if prompted
- checking whether port 11434 is free
- confirming the exact model name you want to use locally

You have now completed the machine-side prerequisites when the health check reports `"ok": true` and `"selected_model_available": true`. The remaining action is to enable the dashboard toggle and run the one-day smoke test.

Those are your side steps, and I will guide you through them.

---

## 7) Recommended setup for this project

Use this order:

1. keep the dashboard working
2. keep the mock brain as the default fallback
3. test Ollama locally with a single model
4. switch to `use_mock_llm=False` only when the model is confirmed working
5. keep the mock path for reliability and debugging

This avoids failures from missing local models or empty responses.

---

## 8) Why Ollama is the right tool here

- local and free for prototype work
- no API key required
- easy to test and debug
- fits the internship and student project constraints
- ideal before moving to external APIs

---

## 9) Next step after Ollama

Once the local model works, the next upgrade is:

- agent memory per person
- graph-aware prompts
- network-based message passing
- richer risk summaries
- scenario comparison

Before running a long simulation, use this order:

```powershell
cd C:\Users\USER\prism
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/check_ollama.py --model llama3.1:latest --probe
streamlit run src/ui/app.py
```

If the `.venv` interpreter reports a missing package such as `networkx`, the dependency installation step above is required. This is separate from Ollama and does not change the model setup.

This is where the project becomes much closer to a real digital-twin model.
