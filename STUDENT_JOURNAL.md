# PwC Prism — Student Journal

**Author:** Aya Hachana (internship project, PwC Tunisia / RSM)  
**Goal:** Build a simplified **MiroFish-style** tool that predicts how workplace policies ripple through an organization.  
**Honest scope:** This is a **student prototype** — free tools only, no cloud API keys required for v0.1.

---

## Step 0 — What am I building? (ABM vs MAS)

### My question (from L'homologue PDF)
> Am I doing ABM, MAS, or both?

### Student thinking
- **ABM (Agent-Based Modeling)** = simulate many simple agents over time to **understand/predict** system behavior (ecology, crowds, **organizational policy**).
- **MAS (Multi-Agent Systems)** = engineering systems where autonomous agents **cooperate or compete** to achieve tasks (robot swarms, logistics).

For **PwC Prism**, my primary goal is **prediction**, not deploying robots. So I chose **ABM** as the main lens.

MiroFish uses **MAS-style LLM agents** inside an ABM time loop — I will do the same later, but start simpler.

### Decision
| Choice | Why (student level) |
|--------|---------------------|
| **ABM first** | Matches coursework: "predict ripple effects of policy" |
| **Python** | Free, lots of tutorials, matches Build.pdf examples |
| **Not NetLogo** | I want a Streamlit dashboard like the Build PDF, and I already know some Python |
| **Not full MiroFish clone** | Real MiroFish needs Flask, Vue, Zep Cloud, OASIS — too big for week 1 |

---

## Current status snapshot (as of 2026-09-06)

This is the honest project state after the prototype work and the semantic upgrades.

### Overall phase completion

| Phase | Phase name | Progress |
|-------|------------|----------|
| **Phase 1** | Semantic policy simulation with graph, LLM reasoning, propagation, and comparison | **100% Prism Phase 1 scope** |
| **Phase 2** | Production-scale persistence, calibration, and richer simulation | **70% implementation; real accuracy pending labels** |

### Phase 1 — prototype to semantic simulation

| Step | What it includes | Status | Completion |
|------|------------------|--------|------------|
| Step 0 | Problem framing, ABM vs MAS, internship scope | ✅ | 100% |
| Step 1 | VS Code setup and Python project baseline | ✅ | 100% |
| Step 2 | Seed data and scenario input | ✅ | 100% |
| Step 3 | Semantic graph and knowledge extraction | ✅ | 100% Phase 1 scope |
| Step 4 | Network topology and propagation | ✅ | 100% Phase 1 scope |
| Step 5 | Agent classes and metrics | ✅ | 90% |
| Step 6 | Mock + Ollama structured brain and ontology reasoning | ✅ | 100% Phase 1 scope |
| Step 7 | 4-quadrant simulation, propagation, and scenario comparison | ✅ | 100% Phase 1 scope |
| Step 8 | SQLite + Streamlit dashboard, report, exports, and chat | ✅ | 100% Phase 1 scope |

### Phase 2 — realistic free local LLM project

| Step | What it includes | Status | Completion |
|------|------------------|--------|------------|
| Step 2.1 | Typed graph from policy text | ✅ | 90% |
| Step 2.2 | Ontology + graph into simulation | ✅ | 90% |
| Step 2.3 | Local free memory layer | ✅ | 90% |
| Step 2.4 | Local Ollama integration | ✅ | 85% |
| Step 2.5 | Live LLM agent reactions and report JSON | ✅ | 80% |
| Step 2.6 | LLM persona profiles and graph-constrained message bus | ✅ | 80% |
| Step 2.7 | Neo4j read-back and explicit backend switch | ✅ | 60% |
| Step 2.8 | Calibration metrics, repeated runs, sensitivity, and scenario exports | ✅ | 85% |
| Step 2.9 | Mesa population scheduler and richer scenarios | ✅ | 80% |

### What has improved since the first prototype

- basic regex knowledge graph was upgraded with spaCy-first extraction
- typed graph nodes and relations were added for richer policy understanding
- parameter-aware formulas now reflect employee count, client trust, morale, and simulation days
- simulation effects are more realistic than a flat rule engine
- free local memory is now in place using SQLite before full Ollama integration
- LLM persona profiles are generated or loaded once and persisted in SQLite
- agent messages are routed only through graph neighbors
- Neo4j can be selected for policy graph write/read-back with `graph_backend="neo4j"`
- calibration metrics and CSV/JSON scenario exports are available
- richer scenarios E–H and a Mesa scheduler boundary were added
- LLM ontology extraction now returns validated confidence, evidence, and relation metadata
- routed neighbor messages now create bounded stress and trust influence during a run
- scenario comparisons use reproducible seeds and include network-density metadata
- repeated scenario runs report standard deviation and leak rate
- sensitivity grids test employee population against simulation duration
- Mesa population benchmarks track Prism stress/trust state at 10, 50, and 100 agents
- CrewAI specialist orchestration is installed in `.venv-crewai` and has passed an Ollama smoke test
- graph-constrained group conversations now let employees, consultants, managers, and partners respond to one another over multiple rounds
- scenario graph visualization shows policy topics, actors, topology edges, and simulated message edges
- forecast reports now include narrative paths, turning points, and confidence gaps
- dashboard supports follow-up chat with both an individual agent and the forecast reporter

### What still requires user-side infrastructure

The following cannot be completed without your intervention on the machine:

1. Neo4j Desktop or Docker installation, if Phase 2 graph persistence is wanted
2. creating a Neo4j database and choosing its password
3. setting `NEO4J_PASSWORD` locally

Ollama installation and live model activation are already verified. NetworkX remains the default runtime graph. Neo4j runtime integration, repeated evaluation, Mesa population benchmarks, and CrewAI orchestration are implemented. Real predictive accuracy remains unmeasured until labelled outcomes are supplied.

---

## Step 1 — Project setup (VS Code folder)

### What I did
1. Created folder: `C:\Users\USER\prism`
2. Initialized git (already present in workspace)
3. Added `requirements.txt` with: Streamlit, NetworkX, pandas, matplotlib, pypdf

### Student thinking
- I need a **single place** to run code and show Mr. Jebali progress.
- VS Code / Cursor: open the `prism` folder → terminal at project root.
- Virtual environment (recommended):

```powershell
cd C:\Users\USER\prism
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### What I cannot do yet (honest)
- Enterprise security review, PwC deployment, or production Neo4j cluster — out of scope for prototype.

---

## Step 2 — Seed data (manual policy memos)

### What MiroFish does
Upload articles, policy drafts, financial reports → extract context.

### What I did (student shortcut)
Wrote two **fake but realistic** policy memos in `data/seed/`:

- `policy_rto.txt` — Mandatory return-to-office (Scenario C from coursework)
- `policy_salary_cut.txt` — 10% salary adjustment (PwC slide case study)

Also copied scenario list into `data/scenarios/scenarios.json` (scenarios A–D from PDF).

### Student thinking
- Real MiroFish parses PDFs automatically; I can load PDFs with `pypdf` later.
- For the demo, **plain text memos** are enough to test the pipeline.
- **Manual part (like MiroFish sliders):** user types policy + sets morale/trust in Streamlit sidebar.
- **Automated part:** once you click Run, agents react without hand-writing each message.

---

## Step 3 — Knowledge graph (regex fallback + spaCy + typed NetworkX graph)

### What MiroFish does
GraphRAG + Zep Cloud — entities, relationships, memory.

### What I built
File: `src/graph/knowledge_graph.py`

- Reads seed text (`.txt` or `.pdf`)
- Uses spaCy first and regex as a deterministic fallback
- Normalizes workplace aliases and builds a typed directed NetworkX graph
- Preserves relations such as `AFFECTS`, `INCLUDES`, `IMPACTS`, and `MENTIONS`

### Student thinking
- spaCy is now implemented; regex remains for domain terms that generic NER misses.
- NetworkX is still the verified runtime graph. Neo4j is a later persistence upgrade.
- This matches Workflow PDF Step 4 (build graph with NetworkX).

### Limitation
- Won't catch complex relationships like "Consulting L2 London" — needs richer extraction later.

---

## Step 4 — Network topology (who talks to whom)

### What Build.pdf says (Step 1.2)
Define **nodes** (people) and **edges** (REPORTS_TO, WORKS_WITH, CONTRACTED_TO) so gossip doesn't leak randomly.

### What I built
File: `src/graph/network.py`

- **Internal agents** in departments → `Coworker` edges (informal)
- First person in dept → `Reports_To` (formal hierarchy, simplified)
- **Account Manager** → external client via `Account_Manager` edge (informal leak path)

### Student thinking
- This is the **org chart as a graph** — same idea as MiroFish KG but hard-coded rules instead of LLM ontology.
- NetworkX is free and in the Workflow PDF — no Neo4j install needed yet.

---

## Step 5 — Agent classes (Role, Personality, Metrics)

### What Build.pdf defines
- `Role` — job title, internal vs external
- `Personality` — skeptical, conflict-averse…
- `Metrics` — stress, trust, loyalty (0–100)
- `AgentInternal` / `AgentExternal` — workplace vs partner/client

### What I built
Files: `src/models/agents.py`, `src/models/personas.py`, `src/simulation/factory.py`

- Factory randomly pairs names + roles + personalities (MiroFish "persona generation" simplified)
- **Sliders map to metrics:** low morale → higher starting stress

### Student thinking
- I am **not** writing 100 Python classes by hand — MiroFish automates this with LLM; I automate with random pairing + templates.
- Good enough to show **emergent patterns** in the 4-quadrant loop.

---

## Step 6 — Mock fallback + real Ollama LLM brain

### What MiroFish does
Real LLM agents chat, update memory (Zep), return JSON sentiment.

### What I built
File: `src/simulation/llm_brain.py`

- Mock mode remains deterministic for tests and fallback behavior
- Live mode calls Ollama with ontology, graph, network, and memory context
- Returns JSON: `{ message, sentiment, updated_stress, updated_trust }`

### Student thinking
- As a student I may **not have** OpenAI/Gemini credits — prototype must run **offline**.
- Ollama is installed and verified locally with `llama3.1:latest`.
- `call_llm(..., use_mock=False)` has been tested with a real model response.
- This is **prospective sentiment** simplified: rules predict drift, not analyze old text.

### Current implementation boundary
- `mock_llm_response` is retained as a safety fallback.
- The real path uses an Ollama HTTP request and JSON parsing.
- The report agent also uses the same structured Ollama path.

---

## Step 7 — Four-quadrant simulation loop

### The matrix (from Build.pdf)

|  | INTERNAL | EXTERNAL |
|--|----------|----------|
| **FORMAL** | Q1: Official memo | Q4: SLA / contract warning |
| **INFORMAL** | Q2: Slack gossip | Q3: Account manager leak |

### What I built
File: `src/simulation/engine.py`

For each day (default 10):
1. **Q1** — Day 1 only: leadership posts policy memo
2. **Q2** — Each employee reacts; neighbors from graph provide context
3. **Q3** — If average stress > 70%, account manager leaks to client
4. **Q4** — External partner may trigger SLA warning if trust < 50

### Student thinking
- This is the **ripple effect** PwC Prism slide describes: internal friction → external contract risk.
- Time steps matter: panic Monday → gossip Tuesday → contract warning next week (Build.pdf).
- Rule `if avg_stress > 70` is a simple **ABM behavior rule** (If/Then from L'homologue PDF).

---

## Step 8 — SQLite + Streamlit dashboard

### Data layer (Step 1.3)
File: `src/data_layer/state_db.py`

- SQLite file: `data/prism.db`
- Table `agent_metrics`: day, agent, stress, trust, quadrant, last message
- Enables **line charts** of stress over time

### Dashboard (Part 5 Build.pdf)
File: `src/ui/app.py`

- Sidebar sliders: morale, client trust, simulation days
- Text area: policy input + load seed file
- Tabs: Run simulation | Knowledge graph | This journal
- **Report stub:** warns if stress > 70 or partner trust < 50

### How to run

```powershell
cd C:\Users\USER\prism
.venv\Scripts\activate   # if using venv
pip install -r requirements.txt
streamlit run src/ui/app.py
```

CLI test (no browser):

```powershell
python run_cli.py
```

--- 

## Mapping to MiroFish pipeline (what we have vs not)

| MiroFish stage | Prism v0.1 status | Current completion |
|----------------|-------------------|-------------------|
| 1. Seed input | ✅ Text/PDF loader + seed memos | **100%** |
| 2. Ontology / KG | ⚠️ spaCy-first typed NetworkX graph; no GraphRAG/Neo4j runtime | **75%** |
| 3. Persona generation | ✅ Ollama-generated structured profiles with factory fallback | **85%** |
| 4. Dual simulation analogue | ✅ Internal workplace channel + external client/partner channel with graph propagation | **85%** |
| 5. Report Agent | ✅ Forecast report with risks, paths, turning points, gaps, and Ollama JSON | **90%** |
| 6. Deep interaction (chat with agents) | ✅ Agent chat, reporter chat, and graph-constrained group conversation | **90%** |

---

## What's next (realistic student roadmap)

### Phase 2 — Realistic project upgrade
- [x] LLM-generated entity and ontology extraction with evidence/confidence
- [x] Neo4j persistence adapter and graph read-back foundation
- [x] LLM-generated persona profiles stored in SQLite
- [x] Agent message objects and graph-constrained routing
- [x] Calibration metrics; real labelled outcomes still required
- [x] Mesa scheduler boundary; larger-population validation still required
- [x] More scenarios and CSV/JSON comparison exports
- [x] Native multi-agent specialist orchestration with structured findings
- [x] Optional CrewAI adapter; installation and model configuration remain user-controlled

> Transition plan: see [docs/PRISM_TRANSITION_PLAN.md](docs/PRISM_TRANSITION_PLAN.md) for the full roadmap from the current prototype to a realistic, network-aware, ontology-driven LLM simulation.
>
> Milestone log: see [docs/PRISM_TRANSITION_LOG.md](docs/PRISM_TRANSITION_LOG.md) for the dated rationale, completion definition, current scope, Neo4j path, and Phase 2 plan.
>
> Runbook: see [docs/PRISM_RUNBOOK.md](docs/PRISM_RUNBOOK.md) for the exact commands for `.venv`, `.venv-crewai`, Ollama, Neo4j, the dashboard, and end-to-end runs.
>
> Full workbook: see [docs/PRISM_FULL_WORKBOOK.md](docs/PRISM_FULL_WORKBOOK.md) for the complete installation, execution, output, troubleshooting, and calibration guide.

### The next move after spaCy

The next move after spaCy is to turn extracted entities into a real knowledge graph and then connect that graph to a more realistic simulation loop.

#### After spaCy, the next steps are:

##### 1) Build a structured entity extraction layer
Use spaCy to extract:
- people
- organizations
- departments
- policy terms
- locations
- events

Then clean and normalize them:
- lowercase
- remove duplicates
- map synonyms
- standardize role names like "employee", "manager", "HR", "partner"

This is the step from raw text to usable data.

##### 2) Convert entities into graph nodes
Create a graph where each important item becomes a node:
- employees
- managers
- HR
- clients
- partners
- policy topic
- office location
- salary concern
- return-to-office policy

Example:
- Node: "employees"
- Node: "return to office"
- Node: "managers"

##### 3) Build relations between nodes
Use extracted context to create edges like:
- AFFECTS
- REPORTS_TO
- WORKS_WITH
- RESPONDS_TO
- TRUSTS
- DEPENDS_ON
- LEAKS_TO

This is where the model becomes more realistic than regex-only matching.

##### 4) Add ontology / schema
Now define a project ontology, not just keywords.

Example:
- Policy type
- Severity
- Stakeholders
- Business impact
- Employee impact
- External trust risk

This gives your simulation a structured meaning instead of raw strings.

##### 5) Move from hard-coded rules to agent reasoning
Once the graph is cleaner, the simulation can use:
- policy ontology
- network influence
- agent memory
- neighbor communication
- local context per agent

That is the move from:
- "if word contains mandatory, stress rises"
to:
- "employee sees policy, understands it affects team, hears peers, interprets severity, updates stress and trust"

##### 6) Connect to Ollama
After the graph and ontology are working, use Ollama for:
- agent reaction generation
- sentiment classification
- message writing
- summary generation
- risk interpretation

This is where you get closer to a real LLM brain.

##### 7) Add parameter-driven effects
Then you can compute effects from:
- number of employees
- morale
- client trust
- policy severity
- days simulated
- network density

This is what makes results look realistic instead of constant or arbitrary.

##### Recommended order for your project
1. spaCy entity extraction
2. clean entities + synonyms
3. build knowledge graph from them
4. define ontology schema
5. connect graph to simulation
6. replace mock LLM with Ollama calls
7. add memory and agent-to-agent messages
8. compare scenario outcomes

##### Very short answer

After spaCy, the most important next step is:
- extract entities,
- build graph nodes/edges,
- define ontology,
- then feed that structured data into the simulation and agent brain.

That is the real transition from prototype to realistic system.

### Phase 3 — Richer simulation
- [ ] Mesa framework for explicit "ticks" and scheduling
- [ ] More scenarios E–H (shadow work, vendor negotiation)
- [ ] CSV export + matplotlib charts in report PDF

### Phase 4 — Closer to MiroFish
- [ ] Report Agent (CrewAI or simple ReAct loop)
- [ ] Chat with one agent post-simulation
- [ ] Compare baseline vs shock runs (Workflow PDF)

---

## Presentation talking points (for internship)

1. **Problem:** Leadership changes policy without seeing downstream partner/turnover risk.
2. **Approach:** Digital twin = agents + network + time loop (same *idea* as MiroFish, scoped to PwC org health).
3. **Demo:** RTO memo → stress rises → informal leak → client SLA warning.
4. **Honesty:** Prototype uses mock LLM; production would use GraphRAG + real agents like MiroFish.
5. **Value:** Rehearse decisions in a sandbox before real rollout.

---

*Last updated: 2026-09-06 — Phase 2 graph backend, calibration, Mesa scale, and multi-agent orchestration checkpoint.*
