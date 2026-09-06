# CrewAI setup for Prism

CrewAI is optional and must use a separate Python environment. The main Prism environment uses Python 3.14.2; the current CrewAI dependency path is intended for Python 3.12.

## 1. Install Python 3.12

Run PowerShell outside the active `.venv`:

```powershell
winget install --id Python.Python.3.12 --exact
```

Close and reopen PowerShell after installation. Verify:

```powershell
py -3.12 --version
```

Expected format:

```text
Python 3.12.x
```

If `py` is unavailable, use the full path that is installed on your machine:

```powershell
$python312 = "$env:LocalAppData\Programs\Python\Python312\python.exe"
& $python312 --version
& $python312 -m venv .venv-crewai
```

## 2. Create a separate environment

From the Prism project root:

```powershell
# Use this if the Python Launcher works:
py -3.12 -m venv .venv-crewai

# Or use the direct Python 3.12 executable:
$python312 = "$env:LocalAppData\Programs\Python\Python312\python.exe"
& $python312 -m venv .venv-crewai

.venv-crewai\Scripts\Activate.ps1
python --version
```

The output must start with `Python 3.12`.

Do not replace or rebuild `.venv`; the normal Prism application remains in that environment.

## 3. Install Prism and CrewAI dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-optional.txt
```

Verify CrewAI:

```powershell
python -c "import crewai; print('CrewAI import OK')"
```

The separate `.venv-crewai` environment is the only environment used for CrewAI. Keep running the standard Prism dashboard from `.venv`.

## 4. Configure Ollama for CrewAI

Start Ollama and confirm the model is available:

```powershell
ollama list
```

Set the local Ollama endpoint for the current terminal:

```powershell
$env:OLLAMA_API_BASE="http://localhost:11434"
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:OLLAMA_MODEL="llama3.1:latest"
```

Do not add passwords or API keys to the repository. Local Ollama does not need an API key.

## 5. Run the optional CrewAI adapter

The adapter is:

```text
src/simulation/crewai_workflow.py
```

The native Prism multi-agent workflow remains the default because it is lighter and tested in the main environment. CrewAI is an optional orchestration layer.

Before using the adapter, make sure:

- `.venv-crewai` is active
- Ollama is running
- `llama3.1:latest` is installed
- `OLLAMA_API_BASE` is set

To run the complete Neo4j + Ollama + CrewAI path:

```powershell
.\.venv-crewai\Scripts\Activate.ps1
$env:NEO4J_URI="bolt://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_DATABASE="prismDB"
$env:NEO4J_PASSWORD='YOUR_PASSWORD'
$env:OLLAMA_API_BASE="http://localhost:11434"
$env:OLLAMA_MODEL="llama3.1:latest"
python scripts\run_crewai_end_to_end.py --database prismDB --model llama3.1:latest
```

Expected output includes:

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

## 6. Common errors

### CrewAI is ignored during installation

You are using Python 3.14. Activate `.venv-crewai` and confirm `python --version` reports Python 3.12.

### Ollama connection failure

Check:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags -UseBasicParsing
```

### API key requested

CrewAI may use LiteLLM provider configuration. For the Prism local path, use the Ollama model identifier and local endpoint. Do not add a fake API key. If the installed CrewAI release requires a provider-specific configuration, keep using the native Prism workflow until that adapter is configured.

## User-only actions

You must perform:

1. install Python 3.12
2. create/activate `.venv-crewai`
3. install the optional dependencies
4. start Ollama
5. configure any local provider settings requested by CrewAI

The existing Prism `.venv` and native multi-agent workflow remain unaffected.
