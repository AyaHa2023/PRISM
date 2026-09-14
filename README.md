# PwC Prism

Student prototype of **MiroFish-style** organizational policy simulation for the PwC Tunisia internship project.

## What this is

**Prism** is a simplified, 100% free **Agent-Based Model (ABM)** that predicts ripple effects when leadership announces a workplace policy (RTO, salary changes, AI rollout, etc.).

It implements the **first pipeline steps** from your coursework PDFs:

| Step | MiroFish / Build.pdf | Prism implementation |
|------|----------------------|----------------------|
| 1.1 | Seed documents → vector DB | `data/seed/*.txt` + text loader |
| 1.2 | Org network graph | `src/graph/network.py` (NetworkX) |
| 1.3 | Agent state DB | `src/data_layer/state_db.py` (SQLite) |
| 2 | Agent classes | `src/models/` |
| 3 | LLM brain + sentiment | `src/simulation/llm_brain.py` (mock rules; no API key) |
| 4 | 4-quadrant loop | `src/simulation/engine.py` |
| 5 | Streamlit dashboard | `src/ui/app.py` |

## Quick start

```powershell
cd C:\Users\USER\prism
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/ui/app.py
```

## Project layout

```
prism/
├── data/seed/            ← example policy memos
├── data/scenarios/       ← scenarios A–D from L'homologue PDF
├── src/                  ← Python code
```

## References

- [MiroFish on GitHub](https://github.com/666ghj/MiroFish)
- Course PDFs: see `docs/references/README.md`
