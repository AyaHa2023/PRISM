# PwC Prism — From Prototype to Realistic Policy Simulation

This document explains the transition from the current working prototype to a more realistic, data-driven, LLM-assisted organizational simulation. It keeps the current dashboard and the current ABM core, but clarifies what is still heuristic, what must be replaced, and how the project should evolve in a professional engineering path.

---

## 1) What exists today: honest prototype stack

The current project is a student prototype inspired by MiroFish and the coursework PDFs. It is intentionally lightweight, offline, and free to run. It is a valid Phase 1 version, but it is not yet a realistic policy digital twin.

### Prototype technology stack

| Layer | Current tool / code | Role in the prototype |
|------|---------------------|----------------------|
| Seed input | `.txt` files in `data/seed/` + PDF-ready loader patterns | Policy documents and scenarios |
| Knowledge graph | `NetworkX` + regex entity extraction | Simple ontology + graph relations |
| Network topology | handcrafted org graph in `src/graph/network.py` | Internal/external links and leak paths |
| Agents | Python dataclasses + factory logic | Personas, roles, stress, trust |
| Simulation engine | deterministic rule loops in `src/simulation/engine.py` | 4-quadrant ABM over time |
| Mock intelligence | keyword heuristics in `src/simulation/llm_brain.py` | Simulated agent reactions without external AI |
| Storage | SQLite in `src/data_layer/state_db.py` | Persists agent metrics over time |
| Frontend | Streamlit in `src/ui/app.py` | Dashboard for policy testing |
| Visualization | Matplotlib + pandas | Trend charts and report summary |

### Current status table

| MiroFish stage | Current status | Meaning |
|----------------|---------------|---------|
| 1. Seed input | ✅ Text/PDF loader + seed memos | Works for prototype demos |
| 2. Ontology / KG | ⚠️ Simple regex KG (not GraphRAG) | Good for first graph but weak for real semantics |
| 3. Persona generation | ⚠️ Random factory (not LLM profiles) | Functional but not realistic |
| 4. Dual simulation | ⚠️ Single org simulation, 4 quadrants | Real logic but simplified |
| 5. Report Agent | ⚠️ Rule-based summary in Streamlit | Not yet proactive intelligence |
| 6. Deep interaction | ❌ Not yet | Agents do not truly reason or chat |

This is not a failure. It is exactly the right first version: a free, transparent, understandable proof of concept.

---

## 2) Why the current results are not yet realistic

The prototype is intentionally simple, but that means the outcomes can feel wrong when you change parameters.

### Problem 1: number of employees changes the signal too much

A simulation with 10 agents is not equivalent to one with 40 agents. In a real system, the distribution matters:

- more employees = more opinions, more rumor spread, more variance
- small groups may amplify same stress signal through a few people
- larger groups create network effects and cluster behavior

A realistic model needs population scaling logic, not just the same rules repeated for more agents.

### Problem 2: starting client trust does not currently produce a realistic response

The trust variable is currently treated too bluntly. In reality, external trust reacts to:

- policy severity
- communication clarity
- contract exposure
- partner dependency
- rumor amplification
- manager narrative quality

A small change in starting client trust should have a measurable but non-linear effect, not just a binary warning.

### Problem 3: simulation length changes outcomes in a way the model does not explain

The number of days matters because:

- short runs show initial shock only
- medium runs show adaptation and gossip spread
- longer runs reveal escalation, contraction, or recovery

The model must be able to distinguish short-term panic vs long-term organizational drift.

### Problem 4: hard-coded rules are not semantic reasoning

This is the biggest gap. If the project only checks strings like `mandatory`, `cut`, `salary`, or `10%`, then it has no understanding of:

- who is affected,
- what the true risk is,
- how messages are interpreted,
- how different roles respond differently.

That is why we need a move from keyword rules to ontology + LLM reasoning.

---

## 3) What is regex and why it matters here

### A simple definition

Regex = regular expression. It is a pattern language used to find strings in text, such as:

- names of departments
- keywords like `salary`, `return to office`, `reduction`, `SLA`
- stakeholders like `employee`, `manager`, `client`, `partner`, `HR`

Example:

```python
import re

text = "Mandatory return-to-office policy for all employees"
pattern = r"(mandatory|return[- ]to[- ]office|employees|manager|clients)"
matches = re.findall(pattern, text, flags=re.IGNORECASE)
print(matches)
```

### Why we use regex in the prototype

Regex is a practical way to build the first version of a knowledge graph without external NLP libraries. In this project it helps to:

- detect policy keywords
- identify stakeholder names and categories
- build simple relations such as `AFFECTS`, `RELATED_TO`, `INFLUENCES`
- create a minimal graph for a demo

### Limits of regex

Regex is not semantic intelligence. It does not understand context or meaning deeply. For example, it cannot reliably tell:

- whether a mention is positive or negative
- whether the same entity is being talked about in a different form
- whether two sentences mean the same thing but use different vocabulary
- whether a policy is framed as burden, opportunity, or threat

That is exactly why we will move to spaCy + NER and later to LLM-based ontology extraction.

---

## 4) Why spaCy NER is the next step

### What it is

spaCy is a production NLP library. It can detect entities such as:

- `ORG` = organization
- `PERSON` = individual
- `GPE` = country / city / region
- `EVENT` = policy change, merger, restructure
- `ROLE` = often approximated but useful with custom patterns

### Why it is important for Prism

Right now the graph is based on a small handwritten set of stakeholder words. A more realistic graph should extract entities from real policy text and scenario data.

Example categories we want:

- `employees`
- `managers`
- `HR`
- `partners`
- `clients`
- `office`
- `salary`
- `benefits`
- `work from home`
- `remote policy`

### Recommended first implementation

1. Install spaCy
2. Download the small English model
3. Use a text pipeline that extracts named entities from policy memos
4. Convert those to graph nodes and edges
5. Add a custom rule layer for domain-specific entities that spaCy may miss

Example install steps:

```powershell
cd C:\Users\USER\prism
.venv\Scripts\activate
pip install spacy
python -m spacy download en_core_web_sm
```

Example extraction code:

```python
import spacy

nlp = spacy.load("en_core_web_sm")
text = "Mandatory return-to-office policy will affect employees, managers, and partners across the firm."
doc = nlp(text)

for ent in doc.ents:
    print(ent.text, ent.label_)
```

This replaces the weak regex-only extraction layer.

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

---

## 5) Network topology: why it must become more professional

The project already has network topology logic in `src/graph/network.py`, but for a realistic model we need to move from ad hoc static links to a structured organizational network.

### Current prototype network concept

The current model includes:

- internal employees in departments
- manager hierarchy edges
- informal coworker links
- external client/account-manager links
- leak-path assumptions in the 4-quadrant simulation

This is good for a prototype, but it should be treated as a simplified network skeleton.

### What real network topology should include

A more realistic network should model:

- departments and teams
- formal reporting lines
- informal collaboration links
- trusted peers vs distant peers
- customer / partner dependencies
- cross-functional communication bridges
- risk propagation paths

### Graph design concept

We should define node and edge types more clearly:

```python
Node types:
- Person
- Team
- Department
- Client
- Partner
- Policy
- Event

Edge types:
- REPORTS_TO
- WORKS_WITH
- SHARES_INFO_WITH
- AFFECTS
- TRUSTS
- DEPENDS_ON
- LEAKS_TO
- RESPONDS_TO
```

### Why this matters

Without a proper topology, the simulation can produce unrealistic results:

- everyone talks to everyone equally
- external effects appear without any propagation path
- trust collapse happens without evidence from network structure
- stress is too uniform across people

### Professional coding direction

Instead of hard-coded rules inside one engine loop, split the topology into:

- `network_builder.py` → builds graph
- `network_metrics.py` → computes centrality, clustering, influence
- `policy_propagation.py` → models message spread and rumor diffusion
- `topology_service.py` → exposes network context to agents

This makes the code ready for real simulations rather than a demo script.

---

## 6) From hard-coded rules to LLM ontology

### Current state

The current mock LLM brain uses rules such as:

- if policy contains `mandatory`, increase stress
- if policy contains `cut`, reduce morale
- if trust is low, external risk increases

This is useful, but it is not memory-aware or semantically aware.

### Desired state

Instead of giving the agent a list of hard-coded strings, we give it an ontology and structured reasoning.

### Example ontology

```json
{
  "policy_type": "return_to_office",
  "severity": 0.8,
  "stakeholders": ["employees", "managers", "partners"],
  "organizational_cost": "high",
  "employee_impact": "medium",
  "client_risk": "elevated",
  "sentiment": "negative",
  "time_horizon": "short_term"
}
```

---

## 7) Last step before the simulation becomes LLM-driven

This is the final operational handoff between the prototype and the realistic version.

At this point, the code already has the following structure:

- regex extraction is available as a fallback
- spaCy extraction is available as the preferred semantic layer
- the graph is built from extracted entities and relations
- ontology provides structured understanding of the policy event
- the LLM brain is prepared to call a local model through Ollama
- the mock path still exists as a safe fallback

The last step is not a code rewrite. It is environment activation.

### Step 1: install Ollama

Use the official installer from:

https://ollama.com/download

On Windows, this is normally a standard install with a local background service.

After installation, verify it is available in your terminal:

```powershell
ollama --version
```

If the command is not recognized, close and reopen PowerShell, or check whether the Ollama tray/service is running.

### Step 2: pull a model such as llama3.1

Once Ollama is installed, pull a local model:

```powershell
ollama pull llama3.1
```

You can also list available models:

```powershell
ollama list
```

If you prefer another local model, that is also acceptable, but `llama3.1` is the simplest first choice for a working student project.

### Step 3: confirm the endpoint is reachable

The default local API endpoint is:

```text
http://localhost:11434
```

Check it from PowerShell:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags
```

If this works, Ollama is running and responding.

A second direct check is:

```powershell
curl http://localhost:11434/api/tags
```

If the endpoint is not reachable, start the local daemon explicitly:

```powershell
ollama serve
```

Then check again.

### Step 4: switch the simulation to the non-mock LLM path

The project has the switch in [src/simulation/llm_brain.py](../src/simulation/llm_brain.py).

The function is:

```python
def call_llm(agent: AgentBase, event: str, context_messages: str = "", use_mock: bool = True, model: str = "llama3.1") -> dict:
```

Currently, the default is `use_mock=True`. That is safe for development.

To activate the real local model, do one of these:

```python
result = call_llm(agent, event, context_messages, use_mock=False, model="llama3.1")
```

or

```python
result = run_simulation(policy_text, use_mock_llm=False)
```

depending on which simulation entry point you are using.

The project is designed so that:

- `use_mock=True` keeps the system stable and deterministic
- `use_mock=False` routes the response through Ollama
- if Ollama fails, the code falls back to the mock response automatically

This makes the transition safe and controllable.

### Step 5: keep the fallback path while testing

Do not remove the mock path yet. Keep it during the first live LLM tests.

The right workflow is:

1. install Ollama
2. pull a model
3. verify the endpoint
4. call the local model once with a tiny example
5. switch the simulation to `use_mock=False`
6. watch real reactions in the agents
7. keep the mock response as a backup until the local model is stable

### Step 6: what comes next after the local LLM is live

Once Ollama is active, the next professional upgrades are:

- agent memory per person
- richer graph-aware prompts
- network propagation between employees and clients
- structured risk summaries
- multi-agent message passing
- scenario comparison across policy plans
- sentiment and trust monitoring over time

That is the real next layer after this installation step.

---

## 8) Final transition summary

The project is now at the point where the path is clear:

1. Prototype foundation works
2. spaCy gives semantic extraction
3. ontology gives structured meaning
4. graph provides network context
5. local LLM through Ollama gives realistic reaction generation
6. agent memory and communication become the next realistic evolution

This is the correct engineering arc for a real digital-twin style policy simulator.

The last step is operational, not conceptual: make Ollama run locally, test the endpoint, and then switch from the mock brain to the non-mock LLM path in [src/simulation/llm_brain.py](../src/simulation/llm_brain.py).

The agent can then reason about the policy as structured data instead of a raw paragraph.

### Why this is a better architecture

An ontology allows:

- consistent interpretation across agents
- easier feature extraction from policies
- realistic comparisons between scenarios
- better future integration with LLMs and RAG

### Transition from rules to ontology

The transition path is:

1. Regex extraction → identify rough keywords
2. spaCy NER → identify entities and roles
3. Built-in domain rules → map entities into policy ontology
4. LLM schema extraction → convert text to structured JSON
5. Agent reasoning → make decisions from ontology, not raw strings

---

## 7) Real LLM brain and agent communication: realistic architecture

This is the next step after the prototype. We do not need to jump directly to a large production system. We can evolve in stages.

### Goal

Have agents that:

- read policy events
- recall their local context
- reason about consequences
- communicate with peers
- update stress, trust, and sentiment
- produce a world state that can be measured over time

### Recommended tech stack

#### Local-first option (best for this project)

- Ollama on your laptop
- local LLM models such as `llama3.1`, `mistral`, `qwen2.5`
- Python HTTP client to call `http://localhost:11434/api/generate`
- structured JSON responses
- optional LangChain or direct `requests`

#### Free / low-cost external options for testing

- Ollama (best fit here)
- Groq free tier (for fast LLM generation)
- Hugging Face Inference API (limited free quota)
- Google Gemini free tier (if available in your region)

### Agent communication model

A realistic agent should have:

- identity
- role
- team
- network neighbors
- memory
- beliefs about policy
- response strategy

Example concept:

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AgentMemory:
    summary: str = ""
    recent_events: List[str] = field(default_factory=list)

@dataclass
class LlmAgent:
    agent_id: str
    name: str
    role: str
    team: str
    personality: str
    stress: float = 50.0
    trust: float = 70.0
    memory: AgentMemory = field(default_factory=AgentMemory)
```

### Communication flow

1. Policy event enters the system
2. Agent receives event context
3. Agent reads local network neighbors
4. Agent constructs a prompt with role + memory + network + policy summary
5. LLM returns a structured JSON response
6. System updates stress, trust, sentiment, and generated message
7. Message is broadcast to connected neighbors

### Example LLM prompt structure

```python
prompt = f"""
You are {agent.name}, a {agent.role} in {agent.team}.
Current stress: {agent.stress}
Current trust: {agent.trust}
Personality: {agent.personality}
Recent memory: {agent.memory.summary}
Policy event: {policy_text}
Neighbor updates: {neighbor_context}

Return JSON with:
- message
- stress_delta
- trust_delta
- sentiment
- risk_flag
"""
```

This is the key move from deterministic rule simulation to real decision-making agents.

---

## 8) How to connect Ollama to this project

You already have Ollama installed on your laptop, which is ideal for the next step.

### Local setup

1. Verify Ollama is running
2. Pull a model locally
3. Test the endpoint

Example:

```powershell
ollama pull llama3.1
ollama list
```

Then test locally with a REST call or Python request:

```python
import requests

payload = {
    "model": "llama3.1",
    "prompt": "Give me a short policy reaction as an employee in one paragraph.",
    "stream": False,
    "options": {"temperature": 0.7}
}

response = requests.post("http://localhost:11434/api/generate", json=payload)
print(response.json()["response"])
```

### Why this is better than a cloud API for now

- no billing surprise
- works offline
- easier to prototype and debug
- matches your project stage and internship constraints

### Recommended use in Prism

Use Ollama only for:

- policy summary generation
- agent reaction generation
- narrative message creation
- anomaly and risk interpretation

Do not use it yet for the full final production architecture until the data schema and simulation loop are stable.

---

## 9) Data-driven effect of parameter changes

The project must move from “magic numbers in if-statements” to measurable parameter effects. This is the first step toward more credible results.

### Important parameters

- number of employees
- starting morale
- starting client trust
- simulation days
- policy severity
- communication clarity
- network density
- agent personality variance

### Example parameter effect model

```python

def compute_policy_effect(start_morale, start_trust, n_agents, sim_days, policy_severity):
    morale_factor = (100 - start_morale) / 100
    trust_factor = (100 - start_trust) / 100
    scale_factor = max(1.0, n_agents / 20)
    time_factor = max(1.0, sim_days / 7)

    stress_rise = (morale_factor * 30 + trust_factor * 20 + policy_severity * 25) * scale_factor * time_factor
    trust_drop = (policy_severity * 18 + trust_factor * 15) / max(1.0, 1 + (start_trust / 100))

    return {
        "estimated_stress_increase": round(stress_rise, 1),
        "estimated_trust_drop": round(trust_drop, 1),
    }
```

### Example dataset

| Employees | Start morale | Start client trust | Days | Policy severity | Stress rise | Trust drop |
|-----------|--------------|--------------------|------|-----------------|-------------|------------|
| 10 | 75 | 85 | 10 | 0.7 | 31.2 | 11.4 |
| 40 | 75 | 85 | 10 | 0.7 | 52.8 | 18.1 |
| 40 | 60 | 85 | 10 | 0.7 | 71.0 | 20.2 |
| 40 | 75 | 50 | 10 | 0.7 | 66.4 | 27.9 |
| 40 | 75 | 85 | 30 | 0.7 | 93.7 | 26.4 |

This shows why the model must be parameterized and data-aware. The effect of starting client trust and simulation length is not uniform.

This is the direction we need: use data and formulas, not just a few hard-coded thresholds.

---

## 10) Full transition roadmap

### Phase 0 — Current prototype

- static seed input
- regex KG
- hand-made network topology
- mocked LLM brain
- rule-based summary
- dashboard only

### Phase 1 — Better NLP foundation

- spaCy NER for policy extraction
- more structured graph schema
- professional `network` and `graph` modules
- parameter-aware simulation formulas
- documented experiments on morale, trust, and time

### Phase 2 — Local LLM integration

- Ollama with small models
- structured JSON agent outputs
- memory per agent
- network-based communication
- no external API needed for development

### Phase 3 — Realistic simulation engine

- deeper org topology
- message propagation and rumor spread
- multi-agent coordination
- quality scoring for policy responses
- scenario comparison baseline vs shock case

### Phase 4 — Report agent and conversation layer

- final risk analyzer
- policy explanation engine
- chat with selected agents
- report generation in dashboard
- compare multiple runs

### Phase 5 — Production-grade AI layer

- RAG over internal policy docs
- graph-aware retrieval
- richer agent memory and context
- enterprise-style dashboards and export features

---

## 11) Recommended technical improvement sequence

This is the realistic coding path we should follow.

### Step A — Improve data model

Create proper schemas for:

- policy events
- agent state
- graph nodes and relations
- simulation run results

### Step B — Replace plain regex with spaCy NER

Add an extraction service that maps raw text into structured entities and relations.

### Step C — Upgrade network topology

Model departments, teams, and communication graphs using real relation types.

### Step D — Add LLM ontology layer

Use structured prompts to transform policy text into a canonical ontology.

### Step E — Add communication among agents

Let agents influence one another with message passing, not just global thresholds.

### Step F — Add reporting and decision support

After simulation, summarize risk drivers and produce a plain-English policy recommendation.

---

## 12) What to do next

### Immediate next tasks

1. Keep the dashboard in place.
2. Preserve the baseline of the current working prototype.
3. Add a structured doc and transition plan like this one.
4. Install spaCy and begin entity extraction on seed files.
5. Replace hard-coded “keyword detection” with ontology-based extraction.
6. Move to local Ollama for agent reasoning.
7. Build a realistic social network layer before adding large-scale agent behavior.

### Important engineering principle

Do not replace everything at once. The right path is:

- stabilize the prototype,
- improve the understanding layer,
- then upgrade agent intelligence,
- then scale the simulation.

This keeps the project honest and gives real, explainable progress instead of a leap from a demo to an overpromised system.

---

## 13) Bottom line

The current project is a legitimate Phase 1 prototype: a free, understandable, offline policy simulation that demonstrates the general pattern of MiroFish-style digital twin design. It is not yet a realistic organizational policy model, but it is a solid foundation.

The right path forward is explicit and professional:

- keep the dashboard,
- improve the graph and ontology,
- introduce spaCy NER,
- move to local LLM reasoning via Ollama,
- model network topology properly,
- and encode real parameter effects with data instead of hard-coded rules.

That is the transition from prototype to a meaningful system that can generate real insight.
