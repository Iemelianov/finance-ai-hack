
You are working inside a local repository that contains:

- SETUP.md — instructions to set up the local Cognee + distil SLM environment.
- solution_q_and_a.py — reference code for querying Cognee's QA interface.
- A submission/ folder that will hold the final hackathon project.

The starter project in submission/ contains:

- app_streamlit.py
- core/models.py
- core/agents.py
- core/cognee_client.py
- docs/ui_spec.md

Your tasks:

1. Wire Cognee into core/cognee_client.py.
2. Make ask_cognee_json robust.
3. Ensure prompts and JSON contracts in core/agents.py work well with Cognee.
4. Make app_streamlit.py fully functional with the local Cognee backend.
5. Respect constraints: no direct use of raw data files; no mandatory online LLM calls.
6. Test the app locally with `streamlit run app_streamlit.py`.

Goal: a self-contained local app that demonstrates:
- Reconciliation dashboard,
- Agentic Invoice Concierge,
- Financial Anomaly Mini-Detective,
all powered by Cognee QA over the prebuilt knowledge graph.
