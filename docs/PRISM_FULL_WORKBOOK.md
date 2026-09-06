# PwC Prism Full Project Workbook

**Project:** PwC Prism
**Purpose:** Run a graph-driven, ontology-aware, local-LLM policy simulation for an organizational environment.
**Platform:** Windows + PowerShell
**Checkpoint:** 2026-09-06

---

## 1. What Prism does

Prism accepts a policy or organizational decision and simulates:

```text
Policy text
  -> entity extraction
  -> ontology and evidence
  -> typed policy graph
  -> NetworkX or Neo4j graph backend
  -> agent profiles and memory
  -> Ollama agent reasoning
  -> graph-constrained communication
  -> internal/external propagation
  -> forecast report
  -> agent/reporter chat
  -> scenario comparison and calibration
```

Prism is an organizational analogue of a MiroFish-style system. It does not literally simulate Twitter and Reddit. Its channels are:

- internal employees, managers, consultants, leadership
- external clients, vendors, partners, engagement leads

---

## 2. Project environments

Prism uses two Python environments.

| Environment | Python | Use |
|---|---:|---|
| `.venv` | Python 3.14 | Main dashboard, tests, NetworkX, Ollama client |
| `.venv-crewai` | Python 3.12 | CrewAI dashboard and CrewAI end-to-end workflow |

Never replace `.venv` with `.venv-crewai`. They serve different purposes.

---

## 3. One-time installation

### 3.1 Open the project

```powershell
cd C:\Users\USER\prism
```

### 3.2 Main environment

If `.venv` does not exist:

```powershell
python -m venv .venv
```

Install main dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The main environment contains:

- Streamlit
- NetworkX
- pandas
- matplotlib
- pypdf
- spaCy
- requests
- Neo4j driver
- Mesa
- pytest

### 3.3 spaCy model

Install the small English model once:

```powershell
.\.venv\Scripts\python.exe -m spacy download en_core_web_sm
```

If the model is unavailable, Prism keeps its regex fallback.

### 3.4 Python 3.12 for CrewAI

Install Python 3.12 if necessary:

```powershell
winget install --id Python.Python.3.12 --exact
```

If the `py` launcher is unavailable, use the direct executable:

```powershell
$python312 = "$env:LocalAppData\Programs\Python\Python312\python.exe"
& $python312 --version
& $python312 -m venv .venv-crewai
```

Create the CrewAI environment:

```powershell
py -3.12 -m venv .venv-crewai
```

Or, if `py` is unavailable:

```powershell
$python312 = "$env:LocalAppData\Programs\Python\Python312\python.exe"
& $python312 -m venv .venv-crewai
```

Install its dependencies:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-optional.txt
python -c "import crewai; print('CrewAI import OK')"
```

---

## 4. Start Ollama

### 4.1 Start Ollama

Open Ollama normally on Windows. Confirm the server:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing
```

Expected status:

```text
200 OK
```

### 4.2 Check the model

```powershell
ollama list
```

Required model:

```text
llama3.1:latest
```

If missing:

```powershell
ollama pull llama3.1
```

### 4.3 Configure Ollama variables

Set these in every terminal used for live LLM runs:

```powershell
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_API_BASE="http://localhost:11434"
$env:OLLAMA_MODEL="llama3.1:latest"
```

No API key is required for local Ollama.

---

## 5. Start Neo4j

### 5.1 Neo4j Desktop

1. Open Neo4j Desktop.
2. Open the `PRISM` DBMS instance.
3. Start the DBMS.
4. Start the `prismDB` database.
5. Confirm Bolt is active on port `7687`.

Check from PowerShell:

```powershell
Test-NetConnection 127.0.0.1 -Port 7687
```

Required:

```text
TcpTestSucceeded : True
```

Check Browser:

```powershell
Invoke-WebRequest http://127.0.0.1:7474 -UseBasicParsing
```

Expected status:

```text
200
```

### 5.2 Configure Neo4j variables

Set these in the same terminal that runs Prism:

```powershell
$env:NEO4J_URI="bolt://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_DATABASE="prismDB"
$env:NEO4J_PASSWORD='YOUR_NEO4J_PASSWORD'
```

Do not commit the password or place it in source code.

### 5.3 Neo4j authentication problems

`Neo.ClientError.Security.Unauthorized` means the server is reachable but the password is wrong.

`WinError 10061` means the server is not listening. Start the `PRISM` DBMS and `prismDB` database.

---

## 6. Check all prerequisites

From the project root:

```powershell
.\.venv\Scripts\python.exe scripts\check_prism_setup.py
```

The output includes:

- Python version
- Neo4j Bolt status
- Neo4j Browser status
- Ollama status
- whether `NEO4J_PASSWORD` exists
- whether CrewAI is importable in the selected environment
- selected Neo4j database

For CrewAI:

```powershell
.\.venv-crewai\Scripts\python.exe scripts\check_prism_setup.py
```

CrewAI is expected to be false in `.venv` and true in `.venv-crewai`.

---

## 7. Run the normal dashboard

Use this for development and the native workflow:

```powershell
cd C:\Users\USER\prism
.\.venv\Scripts\Activate.ps1
streamlit run src/ui/app.py
```

Open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

### Dashboard controls

#### Simulation setup

- starting employee morale
- starting client trust
- simulation days
- internal employee count

#### Agent brain

- `Use local Ollama LLM` off: deterministic mock fallback
- `Use local Ollama LLM` on: live Ollama reactions
- model: normally `llama3.1:latest`

#### Policy graph backend

- `networkx`: fast in-memory graph
- `neo4j`: writes and reads the policy graph from `prismDB`

Only choose `neo4j` after the Neo4j prerequisite check passes.

---

## 8. Dashboard workflow

### 8.1 Enter a scenario

Use the policy text box or select a seed document.

Examples:

```text
Mandatory return-to-office four days per week affects employees, managers, and clients.
```

```text
Reduce variable compensation temporarily while protecting base salary and funding retention support.
```

### 8.2 Run simulation

Click `Run simulation loop`.

The simulation performs:

1. official policy announcement
2. internal employee reactions
3. graph-routed messages
4. neighbor influence
5. external leak evaluation
6. client/vendor response
7. memory updates
8. metric persistence
9. structured report generation

### 8.3 Inspect the scenario graph

Open `Knowledge graph`.

You can inspect:

- policy nodes
- risk nodes
- stakeholder nodes
- employee/manager/client nodes
- formal edges
- informal edges
- policy impact edges
- dashed message edges

The graph is generated from the last completed simulation.

The interactive graph supports:

- dragging nodes with mouse or touch pointer
- zooming with the mouse wheel
- selecting nodes to inspect role/type and stress/trust metrics
- resetting the layout
- preserving node positions during dashboard reruns

This is an operational world-state view, not a decorative image.

### 8.4 Generate a concrete AI scenario

Use the sidebar button `Generate AI policy/context`.

In live Ollama mode, Prism generates:

- a concrete policy title
- operational policy text
- organizational context
- stakeholders
- risks

The generated policy can then be run through the graph and simulation workflow. Mock mode supplies a deterministic fallback.

### 8.5 Read the forecast report

The report contains:

- headline
- executive summary
- key risks
- recommended actions
- sentiment
- average stress
- minimum external trust
- narrative paths
- turning points
- confidence gaps
- confidence score
- report source: deterministic or Ollama

Download it with `Download report JSON`.

### 8.6 Chat with an agent

Open `Agent chat`.

1. select an employee
2. ask a question
3. review the answer and sentiment
4. the response is saved to SQLite memory

### 8.7 Chat with the reporter

Use `Ask the forecast reporter` to challenge the forecast:

- Why is this scenario risky?
- What caused the turning point?
- Which confidence gap matters most?
- What happens if client trust starts lower?

### 8.8 Run group conversation

Open `Multi-agent review` and choose `Run graph-constrained conversation`.

Agents speak through graph relationships. The conversation contains:

- round number
- speaker
- message
- channel
- sentiment
- stress
- trust
- routed receiver messages

Download it as JSON.

### 8.9 Inspect communication history

The run view shows persisted communication history after a simulation. Use the channel filter to distinguish:

- formal communication: reporting, client delivery, vendor contract, and formal organizational edges
- informal communication: coworker discussion, group conversation, and message propagation

Download the filtered history as CSV. Each message includes day, sender, receiver, channel, text, sentiment, and metric deltas.

---

## 9. Full Neo4j + Ollama simulation

Use the main environment:

```powershell
.\.venv\Scripts\python.exe scripts\run_end_to_end.py `
  --database prismDB `
  --model llama3.1:latest `
  --days 1 `
  --employees 2
```

Expected provenance:

```json
{
  "ok": true,
  "graph_backend": "neo4j",
  "ontology_source": "ollama",
  "report_source": "ollama"
}
```

This proves Neo4j and Ollama participate in one simulation.

---

## 10. Full Neo4j + Ollama + CrewAI workflow

Use the CrewAI environment:

```powershell
.\.venv-crewai\Scripts\Activate.ps1

python scripts\run_crewai_end_to_end.py `
  --database prismDB `
  --model llama3.1:latest `
  --days 1 `
  --employees 2
```

Expected provenance:

```json
{
  "ok": true,
  "graph_backend": "neo4j",
  "ontology_source": "ollama",
  "report_source": "ollama",
  "crewai_source": "crewai",
  "crewai_result_present": true
}
```

To run the dashboard with CrewAI available:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
streamlit run src/ui/app.py
```

---

## 11. Command-line simulation

The simple CLI uses the main environment:

```powershell
.\.venv\Scripts\python.exe run_cli.py
```

It is useful for a quick smoke test without opening the dashboard.

---

## 12. Phase 2 benchmark

Run repeatability, sensitivity, and Mesa population checks:

```powershell
.\.venv\Scripts\python.exe scripts\run_phase2_benchmark.py `
  --days 2 `
  --employees 10
```

The benchmark includes:

- repeated scenario runs
- standard deviation
- leak rate
- employee-count sensitivity
- day-count sensitivity
- Mesa populations of 10, 50, and 100

These are simulator-behavior results, not empirical business accuracy.

---

## 13. Tests and validation

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Compile source and scripts:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src scripts
```

Check Ollama structured generation:

```powershell
.\.venv\Scripts\python.exe scripts\check_ollama.py --model llama3.1:latest --probe
```

Expected current test result is approximately:

```text
42 passed
```

---

## 14. Project outputs

### SQLite

Stored in:

```text
data/prism.db
```

Stores:

- agent metrics
- simulation runs
- agent memory
- agent profiles
- routed messages

### Graph outputs

- in-memory NetworkX graph
- optional Neo4j graph in `prismDB`
- Graphviz visualization in Streamlit

### Reports

- report JSON
- scenario comparison CSV
- scenario comparison JSON
- multi-agent review JSON
- group conversation JSON

---

## 15. Calibration with real outcomes

The template file is:

```text
data/scenarios/labelled_outcomes_template.json
```

Replace example values only with approved reviewed outcomes:

```json
[
  {
    "scenario_id": "C",
    "expected_stress": 65.0,
    "expected_trust": 60.0,
    "expected_sentiment": "negative"
  }
]
```

The system then compares:

- predicted stress vs observed stress
- predicted trust vs observed trust
- predicted sentiment vs reviewed sentiment

Do not present template values as real organizational evidence.

---

## 16. Troubleshooting

### `No module named src`

Run commands from:

```text
C:\Users\USER\prism
```

Project scripts already add the project root when run directly.

### `agent_memory` table missing

Open the database through `StateDatabase`; the schema initializes automatically. Do not delete the database unless you intentionally want to clear history.

### CrewAI ignored

You are using `.venv` instead of `.venv-crewai`:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
python -c "import crewai; print('CrewAI import OK')"
```

### Neo4j unauthorized

The password is wrong for the running DBMS. Reset or verify it in Neo4j Desktop.

### Neo4j connection refused

Start the `PRISM` DBMS and `prismDB`, then verify port `7687`.

### Ollama request timeout

Start with:

- one simulation day
- two employees
- one local model

Increase population and duration after the path works.

---

## 17. Current project status

Implementation status:

- prototype foundation: approximately 95%
- AI/LLM layer: approximately 90%
- graph/Neo4j layer: approximately 85%
- memory: approximately 95%
- network propagation: approximately 85%
- scenario comparison: approximately 90%
- dashboard/report/chat: approximately 90%

The remaining major research gap is empirical validation using real labelled outcomes. The codebase can run the full technical pipeline, but no simulator should claim real-world predictive accuracy without measured outcomes.
