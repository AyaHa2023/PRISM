# PwC Prism — Project Status and Roadmap

Date: 2026-09-05
Time: current project checkpoint

---

## 1) Where we are now

We have moved beyond the original student prototype, but we are not yet in the fully realistic LLM-driven project stage.

The honest current state is:

- Phase 1 foundation is working
- the code now includes semantic extraction and ontology scaffolding
- the simulation includes parameter-aware formulas
- the local Ollama path is prepared, but the real free LLM brain is not fully switched on yet
- Phase 2 has not been fully started as a real engineering phase

This means we are in the transition zone between:

- prototype ABM with hard-coded heuristics
- and a realistic, graph-aware, free local LLM simulation

---

## 2) Current MiroFish status table

| MiroFish stage | Prism v0.1 status | Current reality |
|----------------|-------------------|-----------------|
| 1. Seed input | ✅ Text/PDF loader + seed memos | Done |
| 2. Ontology / KG | ⚠️ Simple regex KG, then spaCy-first extraction | Partially upgraded |
| 3. Persona generation | ⚠️ Random factory, not LLM profiles | Not yet realistic |
| 4. Dual simulation (Twitter + Reddit) | ⚠️ Single org sim, 4 quadrants | Prototype still simplified |
| 5. Report Agent | ⚠️ Rule-based summary in Streamlit | Stub only |
| 6. Deep interaction (chat with agent) | ❌ Not yet | Not yet implemented |

This table is the correct current snapshot. We are not pretending we already reached a real project stage.

---

## 3) What has been accomplished

### Phase 1.0 — project foundation

Completed:
- project root import fixes
- CLI entrypoint stability
- Streamlit dashboard remains functional
- scenario data and seed policy memos remain in place

### Phase 1.1 — basic policy text processing

Completed:
- loaded text and PDF-like seed inputs
- processed policy text as evidence for simulation

### Phase 1.2 — graph and entity extraction

Completed / upgraded:
- regex-style KG existed first
- then a richer spaCy-first extraction layer was added
- canonical entity normalization was introduced
- a cleaner graph structure was added around policy-related entities

Still incomplete:
- the graph is not yet a fully typed domain ontology
- no rigorous semantic graph schema yet for all enterprise entities
- node/edge typing is still not mature enough for real policy reasoning

### Phase 1.3 — parameter-aware simulation formulas

Completed:
- employee count, trust, morale, and simulation duration are now used in formulas
- the simulation effect is no longer constant across a 10-person vs. 40-person scenario
- trust drop and stress increase are now sensitive to size and duration

This is a key step because the user requirement was explicit:
- 10 employees should not behave exactly like 40 employees
- client trust should change the outcome realistically
- simulation days should matter

### Phase 1.4 — Ollama-ready agent brain

Completed:
- local Ollama client exists
- code path is prepared for local inference
- mock fallback remains safe and stable
- real agent prompt generation uses ontology context

Not yet complete:
- local LLM is not yet the default production path in the real simulation loop
- no full free local memory layer beyond the basic fallback
- no fully realistic “agent chat + memory” system yet

---

## 4) What is still not realistic enough

The project is still not yet at a true professional level because the following are still missing:

1. Real typed graph schema
   - not just entity detection
   - needs node types, edge types, and domain ontology

2. Real free LLM brain
   - should be Ollama-based, not Zep-based
   - should run purely locally and free on the laptop

3. Real agent memory
   - local memory should be lightweight and free
   - SQLite or JSON memory is enough for this phase
   - no need for external memory system like Zep

4. Better network propagation
   - formal hierarchy + informal gossip + partner dependency need clearer modeling

5. Richer agent reactions
   - agents should react not only to the policy text, but also to:
     - team climate
     - trust history
     - stakeholder pressure
     - peer network influence

6. Final report model
   - the summary agent should not be a simple rules stub
   - it should synthesize a structured risk narrative from graph + ontology + simulation output

---

## 5) Phase definition and next improvement route

## Phase 1 — Prototype stage (current status)

Goal:
- prove the concept
- keep the dashboard functional
- keep logic understandable and editable
- stay free and local

Status:
- largely complete in structure
- still needs semantic upgrades and realistic parameter modeling

### Step 1.1: seed input
Status: done

### Step 1.2: basic graph and extraction
Status: done in a simplified form

### Step 1.3: simulation formula layer
Status: upgraded and validated

### Step 1.4: agent brain and mock fallback
Status: developed

### Step 1.5: user-side environment setup
Status: partly external dependency
- install Ollama
- pull a model
- verify local endpoint

### Step 1.6: final transition from prototype to realistic project
Status: in progress

---

## Phase 2 — Realistic free local LLM project (not started in full)

This is the project stage we should now target.

### Goal
Move from a demo policy simulator to an ontology-aware, graph-driven, local-LLM simulation with free infrastructure and no paid API dependency.

### Recommended stack for Phase 2

- Python backend
- NetworkX for graph logic
- spaCy for NER and entity extraction
- SQLite for simulation state and memory logs
- Ollama for local LLM inference
- local model such as `llama3.1` or `mistral`
- optional lightweight vector search with local embeddings if needed later
- no Zep required

### Phase 2 steps

#### Step 2.1 — Replace regex graph with a richer typed graph

Must do:
- define domain node types
  - Person
  - Team
  - Department
  - Client
  - Partner
  - Policy
  - Event
  - Risk
- define typed relations
  - REPORTS_TO
  - WORKS_WITH
  - AFFECTS
  - TRUSTS
  - DEPENDS_ON
  - LEAKS_TO
  - RESPONDS_TO
- convert extracted entities into canonical graph nodes
- normalize synonyms and duplicate names

Expected outcome:
- graph is not just keyword matching
- graph describes real organizational relations

#### Step 2.2 — Connect graph + ontology to simulation logic

Must do:
- feed ontology output into each agent decision step
- include graph context in prompts for each agent
- compute risk severity from policy features instead of only word matches
- ensure employee count, morale, trust, days, and network density influence the outcome

Expected outcome:
- decision logic becomes more realistic and explainable

#### Step 2.3 — Replace mock responses with free local LLM brain

Must do:
- install Ollama on the machine
- pull a free model locally
- use `use_mock=False` only when model checks pass
- keep mock rule fallback for reliability

Expected outcome:
- realistic local reactions from a free system
- no API key requirement
- no Zep dependency

#### Step 2.4 — Use local memory, not Zep

Recommended option:
- SQLite-based memory store with per-agent event logs
- JSON file memory or event memory table for each agent
- short-term memory and policy-history memory

This is enough for the project stage we are in.

Purpose:
- each agent remembers prior responses
- context becomes richer without external services

#### Step 2.5 — Step 7 and Step 8 completion

This is where the project becomes more complete from a product viewpoint.

Step 7 = simulation logic and scenario deepening
- internal/external propagation
- policy severity weighting
- network spread and rumor path
- scenario comparison across policies

Step 8 = dashboard/report generation
- polished dashboard tabs
- summary cards
- charts for trend and risk
- final narrative report with graph/ontology summary

This is the real final layer after the model is stable.

---

## 6) What is the next best improvement step?

The next best improvement step is not "more documentation" or "more experiments".

The next best step is:

### Next milestone: Phase 2.1 + 2.3 together

1. complete a richer typed graph from policy text
2. connect ontology + graph into the simulation engine
3. switch the LLM brain from mock to local Ollama response generation
4. keep SQLite memory as the free local memory layer

This is the correct next engineering sequence.

In plain language:

- first improve the meaning layer (graph + ontology)
- then improve the reasoning layer (local LLM)
- then improve the decision layer (simulation formulas and propagation)
- then finalize the reporting layer (dashboard and summary)

---

## 7) Completed vs remaining

### Completed
- seed input
- graph foundation
- spaCy-first extraction
- ontology structure
- parameter-aware formulas
- local Ollama scaffold
- docs updated
- tests for graph and impact formulas pass

### Not yet completed
- fully typed graph schema
- deep graph-to-simulation integration
- full free local memory implementation
- real local LLM default path in production
- polished report agent
- Phase 2 project maturation
- complete Step 7 and Step 8 end-to-end

---

## 8) Final assessment

We have reached a solid transition checkpoint:
- the prototype is no longer just a fake keyword engine
- the project now has semantic extraction, typed graph direction, and free local LLM hooks
- but it still needs a proper Phase 2 execution plan to become realistic and professional

The next move should be explicit and disciplined:

1. upgrade entity extraction from policy text into a typed graph
2. make the graph and ontology influence the engine
3. use Ollama with a local free model as the real brain
4. keep memory local and free using SQLite / JSON
5. complete Step 7 and Step 8 only after the live agent layer is stable

This is the correct path from prototype to realistic project.

---

## 9) Recommended milestone title

Current milestone:

"Phase 1.5 — semantic upgrade and free local LLM preparation"

Next milestone:

"Phase 2 — graph-driven, ontology-aware and local-LLM policy simulation"

---

*Status document created on 2026-09-05.*
