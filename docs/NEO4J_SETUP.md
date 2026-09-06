# Neo4j setup for Prism Phase 2

## Do you need Neo4j now?

Not to run the current dashboard. Prism currently uses:

- NetworkX for the tested in-memory simulation graph
- SQLite for metrics and agent memory
- Ollama for local LLM inference

NetworkX is already in `requirements.txt` and should remain installed. Neo4j is the next persistence/query upgrade, not a replacement that must be installed before the current dashboard works.

## What the code now provides

The optional adapter is:

- `src/graph/neo4j_repository.py`

It can:

- connect to Neo4j over Bolt
- create a uniqueness constraint and node-type index
- upsert Prism typed graph nodes
- preserve directed relations and channels

The adapter is deliberately separate from the simulation engine. This lets us compare NetworkX and Neo4j on the same graph fixture before changing runtime behavior.

## Windows installation options

### Option A: Neo4j Desktop

1. Download Neo4j Desktop from the official Neo4j website.
2. Create a local database.
3. Set a database password and remember it.
4. Start the database.
5. Confirm Bolt is available at `bolt://localhost:7687`.

### Option B: Docker

If Docker Desktop is installed, run:

```powershell
docker run --name prism-neo4j -p 7474:7474 -p 7687:7687 -d -e NEO4J_AUTH=neo4j/CHANGE_THIS_PASSWORD neo4j:5
```

Replace `CHANGE_THIS_PASSWORD` with a password you choose. Do not commit that password to the repository.

Neo4j Browser is then available at:

```text
http://localhost:7474
```

## Install the Python driver

From the Prism root:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The `neo4j` Python package is optional for the current NetworkX-only runtime but is included for the Phase 2 adapter.

## Configure Prism

Set the password only in the current PowerShell process:

```powershell
$env:NEO4J_URI="bolt://localhost:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="YOUR_LOCAL_PASSWORD"
$env:NEO4J_DATABASE="prismDB"
```

Never place the password in Python source, Markdown, or committed `.env` files.

## First migration check

The migration command is now available. Run it from the Prism root:

```powershell
python scripts/migrate_policy_graph.py --database prismDB
```

Expected output looks like:

```json
{
	"ok": true,
	"database": "prismDB",
	"nodes": 5,
	"edges_written": 6
}
```

The exact counts may differ if you pass different policy text. The sequence is:

1. build a typed NetworkX graph from a seed policy
2. connect `Neo4jRepository`
3. run `verify_connection()`
4. run `ensure_schema()`
5. run `upsert_graph(graph)`
6. query the stored neighborhood
7. compare the Neo4j result with the NetworkX result

After migration, test the actual backend switch with:

```powershell
.venv\Scripts\python.exe -c "from src.simulation.engine import run_simulation; r=run_simulation('Mandatory return-to-office affects employees and clients.', days=1, employee_count=2, graph_backend='neo4j', graph_database='prismDB'); print({'nodes': r.policy_graph.number_of_nodes(), 'edges': r.policy_graph.number_of_edges()})"
```

This is the remaining machine-side verification step for Neo4j runtime use. It requires the running `PRISM` instance, the `prismDB` database, and valid `NEO4J_*` environment variables in the same terminal.

## End-to-end Neo4j + Ollama proof

Once Neo4j is running and the environment variables are set, run:

```powershell
.venv\Scripts\python.exe scripts\run_end_to_end.py --database prismDB --model llama3.1:latest
```

This single run verifies the complete path:

```text
policy text -> typed graph -> Neo4j write/read-back -> graph context -> Ollama ontology/persona/reaction -> report JSON
```

Expected output includes:

```json
{
	"ok": true,
	"graph_backend": "neo4j",
	"ontology_source": "ollama",
	"llm_model": "llama3.1:latest",
	"report_source": "ollama"
}
```

This is the acceptance test for the integrated backend. If `graph_backend` is `networkx` or `ontology_source` is `deterministic_fallback`, the run did not prove the complete live path.

### Troubleshooting `WinError 10061`

If Prism reports:

```text
Failed to establish connection to 127.0.0.1:7687
```

the Neo4j DBMS is not listening on Bolt. This is different from an authentication error.

Check it with:

```powershell
Test-NetConnection 127.0.0.1 -Port 7687
```

You need:

```text
TcpTestSucceeded : True
```

In Neo4j Desktop, open the `PRISM` DBMS and click **Start**. Then make sure the `prismDB` database is started. Retry the port check before retrying Prism.

Do not switch the simulation engine to Neo4j until that comparison passes.

## What you need to do yourself

The following actions require your machine or credentials:

- install Neo4j Desktop or Docker Desktop
- create/start the local Neo4j database
- choose the local database password
- set `NEO4J_PASSWORD` in your terminal

I can implement and test the repository code without connecting to your database, but I cannot know or handle your password.
