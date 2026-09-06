# Prism transition log and completion plan

**Checkpoint:** 2026-09-06
**Project:** PwC Prism
**Purpose:** Record why each engineering step exists, what changed, and what remains before the richer simulation phases.

---

## How completion percentages are defined

A percentage describes completion of the Prism project scope, not parity with the entire MiroFish product.

For example, Prism can complete its internal/external four-quadrant policy simulation without pretending it has MiroFish's Twitter and Reddit ecosystems. GraphRAG, Neo4j, Mesa, CrewAI, and external online providers remain later upgrades where they add value.

A step is complete when:

- the code path exists
- it is connected to the user workflow
- its output is structured and testable
- the limitation is documented

---

## Phase 1 — Prototype foundation and semantic upgrade

**Phase status: 100% of the defined Prism Phase 1 scope.**

Phase 1 means a complete, testable policy simulator: semantic extraction, typed graph, ontology-aware LLM reasoning, graph-constrained propagation, parameter effects, scenario comparison, report JSON, and dashboard workflows. It does not mean full MiroFish parity, production GraphRAG, validated real-world prediction, or a Twitter/Reddit clone.

### Step 0 — Problem framing and scope
**Status: 100%**

We chose organizational ABM as the main lens because the goal is to estimate policy ripple effects over time. MAS-style communication is added later for agent interactions.

**Why this was necessary:** It prevents the project from trying to clone a large social simulation platform before the workplace problem is understood.

### Step 1 — Project setup
**Status: 100%**

Python, Streamlit, NetworkX, pandas, matplotlib, pypdf, SQLite, spaCy, and requests are installed or represented in the dependency manifest. CLI and dashboard entry points have project-root import bootstrapping.

**Why this was necessary:** A reproducible project must run from the command line and dashboard, not only from one working directory in VS Code.

### Step 2 — Seed input
**Status: 100%**

Policy text and PDF-ready loading exist. Seed memos and scenario JSON provide repeatable inputs.

**Why this was necessary:** Agents need a common policy event before their reactions can be compared.

### Step 3 — Entity extraction
**Status: 100% for Phase 1 scope**

The original regex extractor remains as a deterministic fallback. spaCy is now preferred, with canonicalization and domain patterns for workplace terms. The typed graph consumes the extracted entities. Live Ollama mode adds validated ontology extraction with confidence, evidence, and relation metadata.

**Why regex came first:** It was free, transparent, and useful for proving the first graph pipeline.

**Why spaCy came next:** Regex finds surface patterns; spaCy gives tokenization, NER, and a maintainable NLP boundary. It still needs domain rules because generic NER does not reliably identify terms such as employees, stress, or SLA.

### Step 4 — Typed knowledge graph and ontology
**Status: 100% for Phase 1 scope; GraphRAG is future work**

The graph now contains typed Policy, Stakeholder, Event, Risk, and Concept nodes with relations such as AFFECTS, INCLUDES, IMPACTS, and MENTIONS. The ontology records policy type, severity, stakeholders, impact, trust risk, sentiment, time horizon, and risk flags.

**Why this was necessary:** The simulation should reason from structured meaning rather than repeatedly searching raw policy strings.

**What is not being claimed:** This is not yet a production GraphRAG system. It is a typed NetworkX graph with deterministic extraction, suitable as the source of truth for the next phase.

### Step 5 — Network topology
**Status: 100% for Phase 1 scope; Neo4j runtime migration is future work**

The workplace graph contains teams, hierarchy, client delivery, vendor contracts, and partner oversight. Network metrics now expose node count, edge count, density, and degree centrality.

**Was the network improved?** Yes, from only handcrafted links to an observable topology with measurable influence context. It is still an in-memory NetworkX model, not a distributed graph database.

### Step 6 — Agent model, memory, and reasoning
**Status: 100% for Phase 1 scope**

Agents have roles, personalities, stress, trust, loyalty, SQLite memory, graph context, ontology context, and structured reactions. Reactions return:

```json
{
  "message": "I need clarification.",
  "sentiment": "mixed",
  "updated_stress": 64,
  "updated_trust": 72
}
```

The response is clamped to valid metric ranges and falls back to the deterministic mock if Ollama fails.

**Why local memory instead of Zep:** SQLite is free, inspectable, portable, and sufficient for the internship milestone. Zep is not required to demonstrate agent memory.

**Why Ollama:** It provides a real LLM brain without requiring a paid cloud API key. `OLLAMA_BASE_URL` can point to localhost or an Ollama server reachable over a network, so the design is not locked to offline-only execution.

---

## Step 7 — Complete simulation and scenario analysis

**Status: 100% for Phase 1 scope**

The four-quadrant loop now supports:

- policy memo
- internal reactions
- graph-aware context
- agent memory
- sentiment on every event
- external leak path
- external trust reaction
- employee-count and parameter-aware effects
- comparable scenario runs
- report-ready metrics

The scenario comparison view runs selected policies with the same parameters and presents average stress, minimum external trust, leak count, and sentiment.

**Why this was necessary:** A professional policy tool must compare decisions under the same assumptions, not only display one run.

**Future enhancement:** Mesa can replace the hand-built tick loop in a later phase if we need schedulers, larger populations, or reproducible agent activation policies.

## Step 8 — Report and dashboard workflow

**Status: 100% for Phase 1 scope**

The Streamlit dashboard now includes:

- live/mock LLM selection
- typed graph visibility
- simulation event feed
- sentiment column
- structured report agent
- downloadable report JSON
- scenario comparison chart
- post-simulation agent chat
- SQLite-backed conversation memory

The report agent uses Ollama when live mode is selected and a deterministic report when mock mode is selected. Both produce the same report schema.

**Why this was necessary:** The dashboard is not only a demo screen; it is the evaluation surface where a decision-maker compares outcomes and inspects evidence.

---

## Current MiroFish mapping after Step 7 and Step 8

| MiroFish stage | Prism scoped status | Completion | Boundary |
|----------------|--------------------|------------|----------|
| 1. Seed input | Text/PDF loader + scenario memos | 100% | No production document governance yet |
| 2. Ontology / KG | spaCy-first typed NetworkX graph + ontology | 75% | LLM extraction, GraphRAG, and Neo4j are not complete |
| 3. Persona generation | Ollama-generated structured profiles with factory fallback | 85% | Profile quality still needs evaluation |
| 4. Dual simulation analogue | Internal workplace and external client/partner channels | 85% | Not a literal Twitter/Reddit clone |
| 5. Report Agent | Deterministic/Ollama forecast with risks, paths, turning points, and gaps | 90% | Calibration and report evaluation are not complete |
| 6. Deep interaction | Agent chat, reporter chat, and graph-constrained group conversation | 90% | Conversation quality and group dynamics still need calibration |

These percentages measure implemented functionality against the requested realistic target. They do not inflate the score by renaming a simplified feature. Prism does not claim literal Twitter/Reddit parity; it implements the organizational analogue with internal and external channels. Profile quality, empirical calibration, and production GraphRAG remain open evaluation work.

---

## What comes next: Phase 2 realistic project

### Phase 2.1 — LLM-generated entity and ontology extraction

Use an Ollama JSON schema prompt to extract entities, aliases, relations, confidence, and evidence spans. Keep spaCy and regex as validation/fallback layers. The LLM must not silently overwrite evidence; every inferred edge should carry a source and confidence.

### Phase 2.2 — GraphRAG and Neo4j

Neo4j becomes useful when the graph is large enough that NetworkX is no longer a comfortable persistence/query layer.

Migration order:

1. freeze the current node and relationship schema
2. assign stable IDs to agents, policies, organizations, and risks
3. export NetworkX nodes and edges to CSV or Cypher
4. run Neo4j locally with Docker or Neo4j Desktop
5. add indexes and constraints for stable IDs
6. implement a repository interface so the engine can use NetworkX or Neo4j
7. query neighborhood context for agent prompts
8. add vector retrieval only after graph queries are reliable
9. compare NetworkX and Neo4j outputs on the same fixture

The Neo4j Python adapter foundation now exists in `src/graph/neo4j_repository.py`, but it is not connected to the default runtime and has not been verified against a user database. See `docs/NEO4J_SETUP.md` before installing it. NetworkX remains the default because it is already tested and does not require a server.

### Phase 2.3 — Real LLM persona profiles

Generate a structured profile once per agent, validate it, store it in SQLite, and reuse it. Do not generate a new personality on every simulation tick. The factory fallback remains available for tests and offline development. This profile path is now implemented in `src/simulation/persona_profiles.py` and connected to the engine.

### Phase 2.4 — Multi-agent communication

Add message objects with sender, receiver, relation, day, channel, sentiment, and evidence. Broadcast only along graph edges. Persist messages and summarize them into agent memory. The first graph-constrained message bus is now implemented in `src/simulation/message_bus.py`; group-level communication and richer message effects remain to be calibrated.

The current implementation also generates or loads one structured persona profile per agent and includes neighbor messages in later prompts. It does not yet model a full group conversation protocol.

### Phase 2.5 — Calibration and prospective sentiment

Compare model predictions with labelled scenario outcomes where available. Track calibration, not only visually impressive text. Sentiment is a structured signal for monitoring drift, not proof of real-world truth. The calibration utility now reports stress MAE, trust MAE, and sentiment accuracy; repeated runs and sensitivity grids are available through `src/simulation/experiments.py` and `scripts/run_phase2_benchmark.py`. Real labels still require internship data or expert annotation.

### Phase 2.6 — Mesa, richer scenarios, and CrewAI

The project now includes a Mesa scheduler with Prism stress/trust population state, four richer Phase 2 scenarios, repeated evaluation, sensitivity grids, and CSV/JSON comparison exports.

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

After the current scope is stable:

- Mesa for explicit scheduling and larger agent populations
- more policy scenarios and sensitivity experiments
- matplotlib or a report export for longitudinal comparison
- CrewAI or a lightweight ReAct report workflow only if multiple specialized agents are justified

CrewAI is now installed in `.venv-crewai` and the specialist adapter has passed an Ollama smoke test. The native workflow remains available as a lighter fallback.

As of this checkpoint, Mesa 3.5.1 and pytest are installed in the project `.venv`, and the Mesa scheduler test passes there. CrewAI is installed and importable in the separate `.venv-crewai` Python 3.12 environment.

The optional CrewAI adapter is now available in `src/simulation/crewai_workflow.py`. It is not part of the default dependency set because it introduces a large dependency tree and still requires a configured model endpoint. The main Prism environment uses Python 3.14.2, while current CrewAI releases require an older compatible Python environment. To enable it deliberately, use Python 3.12:

```powershell
py -3.12 -m venv .venv-crewai
.venv-crewai\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-optional.txt
```

If Python 3.12 is not installed, install it from python.org or continue using the native Prism workflow. This is a user intervention because it changes the environment and may require additional model/provider configuration.

CrewAI is a later orchestration choice, not a substitute for a clean domain model.

---

## Online versus local execution

The project is LLM-capable without a paid external API. Current supported path:

- local Ollama at `http://localhost:11434`
- remote Ollama by setting `OLLAMA_BASE_URL`
- a future OpenAI-compatible provider can implement the same structured client interface

The engine never depends on internet access when mock mode is selected. Live mode depends on the configured Ollama endpoint. If an external provider is later used, the API key must be supplied by the user through environment variables or Streamlit secrets; it should never be committed to the repository.

---

## Verification checkpoint

The completed scope must pass:

```powershell
python -m pytest -q
python -m compileall -q src scripts
python scripts/check_ollama.py --model llama3.1:latest --probe
```

The first two commands validate the repository. The third validates the user's Ollama installation and is the only machine-side dependency in this milestone.

Latest verification on 2026-09-06:

- full `.venv` suite: 36 passed
- live Ollama ontology extraction: source `ollama`, confidence `0.8`, 3 evidence items, 2 relation items
- Neo4j + Ollama end-to-end runner completed successfully in the project environment
- CrewAI + Ollama specialist smoke test completed successfully in `.venv-crewai`
- Phase 2 benchmark completed 12 repeated scenario runs plus 9 sensitivity cases and Mesa populations of 10, 50, and 100 agents
- controlled high-severity sensitivity stress increased from 91.2 at 10 employees to 98.3 at 50 and 99.2 at 100; these are simulator results, not real-world accuracy
- real predictive accuracy remains unverified until labelled outcomes are supplied
