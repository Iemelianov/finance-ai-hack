
import streamlit as st
import pandas as pd

from core.agents import (
    get_reconciliation_dashboard,
    run_concierge_on_invoice_text,
    get_global_anomalies,
)


import logging

# Enable verbose debug logging to trace Cognee calls.
logging.basicConfig(level=logging.DEBUG)

st.set_page_config(page_title="Finance Guardian Agents", layout="wide")

st.title("🛡️ Finance Guardian Agents")
st.caption(
    "Built on top of Cognee + distil SLM: "
    "Reconciliation dashboard • Agentic Invoice Concierge • Financial Anomaly Mini-Detective"
)

# --- Top bar: Add invoice via Concierge ---

with st.expander("➕ Add invoice via Agentic Invoice Concierge", expanded=False):
    st.markdown(
        "Paste invoice text (e.g. from email or OCR) and let the Concierge interpret it.\n"
        "This uses the local Cognee QA backend; no raw CSV data is read directly."
    )
    raw_text = st.text_area("Invoice text", height=160, placeholder="Paste invoice text here...")
    run_concierge = st.button("Run Concierge", type="primary")

    if run_concierge and raw_text.strip():
        with st.spinner("Running Agentic Invoice Concierge via Cognee..."):
            concierge_result = run_concierge_on_invoice_text(raw_text.strip())
        st.success("Concierge finished.")
        st.markdown("**Normalized invoice summary**")
        st.json(concierge_result.to_dict())
    elif run_concierge:
        st.error("Please paste some invoice text before running the concierge.")


st.markdown("---")

# --- Main layout: left = dashboard, right = anomalies panel ---

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Reconciliation Dashboard")

    if st.button("Refresh dashboard"):
        st.session_state["dashboard_rows"] = get_reconciliation_dashboard(limit=50)

    rows = st.session_state.get("dashboard_rows", None)
    if rows is None:
        with st.spinner("Loading reconciliation dashboard from Cognee..."):
            rows = get_reconciliation_dashboard(limit=50)
            st.session_state["dashboard_rows"] = rows

    if not rows:
        st.warning("No dashboard rows received from Cognee yet.")
    else:
        df = pd.DataFrame([r.to_dict() for r in rows])
        st.dataframe(df, use_container_width=True)

        st.markdown("### Focus on an invoice")
        invoice_ids = [r.invoice_id for r in rows]
        selected_invoice_id = st.selectbox("Select invoice ID", options=invoice_ids)

        if selected_invoice_id:
            focused = [r for r in rows if r.invoice_id == selected_invoice_id]
            if focused:
                st.markdown("**Selected invoice row**")
                st.json(focused[0].to_dict())


with right_col:
    st.subheader("Financial Anomaly Mini-Detective")

    if st.button("Refresh anomalies"):
        st.session_state["anomaly_cards"] = get_global_anomalies(limit=20)

    cards = st.session_state.get("anomaly_cards", None)
    # Always try to fetch at first render or when empty
    if cards is None or cards == []:
        with st.spinner("Loading anomaly cards from Cognee..."):
            cards = get_global_anomalies(limit=20)
            st.session_state["anomaly_cards"] = cards

    if not cards:
        st.info("No anomalies reported by Cognee yet.")
    else:
        for card in cards:
            severity = card.severity.upper()
            color = {
                "HIGH": "#ff4b4b",
                "MEDIUM": "#ffb000",
                "LOW": "#1f8b4c",
            }.get(severity, "#444444")

            with st.container():
                st.markdown(
                    f"<div style='border:1px solid {color}; padding:0.5rem 0.75rem; border-radius:0.5rem;'>"
                    f"<div style='font-size:0.8rem; color:{color}; font-weight:600;'>"
                    f"{severity} • Invoice {card.invoice_id} • {card.vendor_name}"
                    f"</div>"
                    f"<div style='margin-top:0.25rem; font-size:0.9rem;'>"
                    f"{card.human_explanation}"
                    f"</div>"
                    f"<div style='margin-top:0.25rem; font-size:0.8rem; color:#666;'>"
                    f"<b>Recommendation:</b> {card.recommendation}"
                    f"</div>"
                    f"<div style='margin-top:0.25rem; font-size:0.75rem; color:#888;'>"
                    f"Reason codes: {', '.join(card.reason_codes)}"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("")  # spacer
