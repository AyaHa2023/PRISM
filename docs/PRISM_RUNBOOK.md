# Prism runbook

For the complete operational workbook, see [PRISM_FULL_WORKBOOK.md](PRISM_FULL_WORKBOOK.md).

This is the repeatable way to run Prism with Ollama, Neo4j, and CrewAI.

## Architecture and environments

Prism uses two Python environments:

| Environment | Python | Purpose |
|---|---:|---|
| `.venv` | 3.14 | normal Prism dashboard, tests, NetworkX, Ollama client |
| `.venv-crewai` | 3.12 | CrewAI dashboard/review workflow |

Neo4j and Ollama are external local services. They must be running before the live integration commands.

## Start services

### Ollama

Make sure Ollama is running, then verify:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing
ollama list
```

The required model is normally:

```text
llama3.1:latest
```

### Neo4j

Start the `PRISM` DBMS and the `prismDB` database in Neo4j Desktop. Verify Bolt:

```powershell
Test-NetConnection 127.0.0.1 -Port 7687
```

You need:

```text
TcpTestSucceeded : True
```

## Configure the current terminal

Set these variables every time you open a new PowerShell terminal. Do not commit the password.

```powershell
$env:NEO4J_URI="bolt://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_DATABASE="prismDB"
$env:NEO4J_PASSWORD='YOUR_NEO4J_PASSWORD'
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_API_BASE="http://localhost:11434"
$env:OLLAMA_MODEL="llama3.1:latest"
```

## Check all prerequisites

From the project root:

```powershell
.\.venv\Scripts\python.exe scripts\check_prism_setup.py
```

The command prints JSON. It requires Neo4j Bolt, Ollama, and `NEO4J_PASSWORD` for exit code 0. CrewAI is checked but is allowed to be false because it lives in the separate environment.

For CrewAI mode, run the same check with:

```powershell
.\.venv-crewai\Scripts\python.exe scripts\check_prism_setup.py
```

## Normal development mode

Use this for fast work, tests, NetworkX, and the native multi-agent workflow:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
streamlit run src/ui/app.py
```

In the dashboard:

1. enable `Use local Ollama LLM`
2. keep `Policy graph backend` as `networkx` for fast development, or select `neo4j`
3. set the Neo4j database to `prismDB` when using Neo4j
4. run the simulation
5. open `Multi-agent review` or `Agent chat`
6. use `Run graph-constrained conversation` for multi-agent dialogue

## Full Neo4j + Ollama simulation

Use this to prove the graph backend and LLM participate in one run:

```powershell
.\.venv\Scripts\python.exe scripts\run_end_to_end.py --database prismDB --model llama3.1:latest --days 1 --employees 2
```

Expected provenance:

```json
{
  "graph_backend": "neo4j",
  "ontology_source": "ollama",
  "report_source": "ollama"
}
```

## Full Neo4j + Ollama + CrewAI workflow

Activate the CrewAI environment in the same terminal where the environment variables were set:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
python -c "import crewai; print('CrewAI import OK')"
python scripts\run_crewai_end_to_end.py --database prismDB --model llama3.1:latest --days 1 --employees 2
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

## Run the dashboard with CrewAI available

If you want the CrewAI option visible and runnable in the dashboard, launch Streamlit from `.venv-crewai`:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
streamlit run src/ui/app.py
```

The normal dashboard still works from `.venv`; CrewAI is only available when the dashboard process uses `.venv-crewai`.

## Run Phase 2 benchmark

This does not call Ollama repeatedly. It is a deterministic experiment harness for repeatability, sensitivity, and Mesa population scale:

```powershell
.\.venv\Scripts\python.exe scripts\run_phase2_benchmark.py --days 2 --employees 10
```

It runs:

- 12 repeated scenario runs
- 9 population/time sensitivity cases
- Mesa populations of 10, 50, and 100

## Troubleshooting

### `Set NEO4J_PASSWORD before connecting`

Set the password in the same terminal that launches Python or Streamlit.

### `WinError 10061` on port 7687

Start the `PRISM` DBMS and `prismDB` database. Then rerun `Test-NetConnection`.

### CrewAI is not available

Use `.venv-crewai`, not `.venv`:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
python -c "import crewai; print('CrewAI import OK')"
```

### Ollama is slow

Start with one day and two employees. Then increase days and population after the end-to-end path works.

## Next engineering milestone

The next milestone is empirical calibration:

1. replace `data/scenarios/labelled_outcomes_template.json` with supervisor-reviewed outcomes
2. run the same scenarios with fixed seeds
3. calculate stress MAE, trust MAE, and sentiment accuracy
4. compare native multi-agent and CrewAI reports
5. tune prompts and formulas based on measured errors

The current simulator is implementation-complete for Phase 2 infrastructure. It is not empirically validated until real labelled outcomes exist.
