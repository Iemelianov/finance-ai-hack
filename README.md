# Finance AI Hack – Cognee-powered Agents

Local-first Streamlit app that sits on a Cognee knowledge graph + distil SLM to solve finance ops tasks.

## What the app can do
- **Reconciliation Dashboard**: Pulls up to 50 invoices with match status, type, anomaly severity, and a short explanation.
- **Agentic Invoice Concierge**: Paste raw invoice text; it normalizes vendor, IDs, dates, amount, currency, category, risk, and triage status.
- **Financial Anomaly Mini-Detective**: Surfaces the most relevant anomalies with reason codes and recommended next steps.
- **Missing Invoice Detective**: Prompt-driven tool to flag missing invoices by vendor/period using the custom prompt.

The UI lives in `app_streamlit.py`; shared agent logic is in `core/`. The Cognee export and local models are **not** tracked in git (see `.gitignore`)—they must be present locally to run.

## Repository layout
- `app_streamlit.py` — Streamlit UI wiring the three agents.
- `core/agents.py` — Prompts + parsing for dashboard, concierge, anomalies, missing invoices.
- `core/cognee_client.py` — Thin bridge into the Cognee completion function in `solution_q_and_a.py`.
- `core/models.py` — Pydantic-style data containers for agent outputs.
- `cognee-minihack/` — Cognee QA scripts, prompts, setup, and optional enrichment data.
- `docs/` — Prompting notes and UI sketch.

## Prerequisites
- Python 3.12
- Ollama installed locally
- Local models copied into `models/` (ignored by git):
  - `nomic-embed-text/` (Modelfile provided)
  - `cognee-distillabs-model-gguf-quantized/` (Modelfile provided)
  - Optional: `Qwen3-4B-Q4_K_M/`
- Cognee export folder `cognee-minihack/cognee_export/` (ignored by git) containing graph + vector + system DBs.

## Setup (quick path)
```bash
cd cognee-minihack

# Register models with Ollama (once models are placed under ../models/)
cd ../models
ollama create nomic-embed-text -f nomic-embed-text/Modelfile
ollama create cognee-distillabs-model-gguf-quantized -f cognee-distillabs-model-gguf-quantized/Modelfile
# optional base model
ollama create Qwen3-4B-Q4_K_M -f Qwen3-4B-Q4_K_M/Modelfile
cd ../cognee-minihack

# Create & activate venv
python -m venv .venv
source .venv/bin/activate

# Install deps and import graph/export
pip install cognee transformers streamlit pandas
python setup.py
```

For fuller context, see `cognee-minihack/SETUP.md`.

## Running
- Streamlit app:
  ```bash
  source cognee-minihack/.venv/bin/activate
  streamlit run app_streamlit.py
  ```
- Direct QA script for testing:
  ```bash
  cd cognee-minihack
  python solution_q_and_a.py
  ```

## Key behaviors
- `core.cognee_client.ask_cognee_raw` delegates to `cognee-minihack/solution_q_and_a.py:completion`. If import fails, it returns a clear error JSON.
- Agents expect JSON back from Cognee; parsing is defensive and strips code fences.
- The concierge generates normalized invoice objects with risk labels; dashboard/anomaly agents request bounded lists to keep UI responsive.

## Large artifacts (not in git)
- `models/` (LLM/embedding weights)
- `cognee-minihack/cognee_export/` (graph + vector + system DBs)
- `cognee-minihack/graphs/after_setup.html` (generated)

Ship these via external storage or LFS if needed before running the app.

## Troubleshooting
- If Cognee calls return an error, verify the venv has Cognee installed and that `solution_q_and_a.py` is importable from `core/`.
- If you see empty dashboards/anomalies, rerun `python cognee-minihack/setup.py` after ensuring the export directory is present.
- For big pushes, keep `.zip`/model/export artifacts out of git (already ignored).

