
"""Agent layer built on top of Cognee QA.

Agents:
- Agentic Invoice Concierge
- Reconciliation Agent
- Financial Anomaly Mini-Detective
"""

from typing import List
from pathlib import Path

from .models import DashboardRow, ConciergeResult, AnomalyCard
from .cognee_client import ask_cognee_json


def get_reconciliation_dashboard(limit: int = 50) -> List[DashboardRow]:
    """Ask Cognee for a compact reconciliation overview."""
    prompt = f"""You are a reconciliation dashboard generator.

Using ONLY the Cognee knowledge graph of vendors, invoices and payments,
build a compact JSON array that summarizes reconciliation and anomaly status
for up to {limit} invoices.

Return a JSON array of objects, each with EXACTLY the following keys:
- invoice_id: string
- vendor_name: string
- amount: number
- currency: string
- match_status: string ("MATCHED" | "UNMATCHED" | "PARTIAL" | "SUSPICIOUS")
- match_type: string ("EXACT" | "APPROX" | "ONE_TO_MANY" | "MANY_TO_ONE" | "NONE")
- anomaly_severity: string ("NONE" | "LOW" | "MEDIUM" | "HIGH")
- short_explanation: string (1 short English sentence explaining the status)

Respond with a single JSON array only, no extra keys or text. If you cannot produce a valid JSON array, return [].
"""
    data = ask_cognee_json(prompt)

    rows: List[DashboardRow] = []
    if isinstance(data, list):
        raw_rows = data
    elif isinstance(data, dict) and isinstance(data.get("rows"), list):
        raw_rows = data["rows"]
    else:
        raw_rows = []

    import logging
    logging.getLogger(__name__).debug("reconciliation raw_rows=%d data_error=%s", len(raw_rows), data.get("error") if isinstance(data, dict) else None)

    for r in raw_rows:
        try:
            rows.append(
                DashboardRow(
                    invoice_id=str(r.get("invoice_id")),
                    vendor_name=str(r.get("vendor_name")),
                    amount=float(r.get("amount", 0.0)),
                    currency=str(r.get("currency", "EUR")),
                    match_status=str(r.get("match_status", "UNMATCHED")),
                    match_type=str(r.get("match_type", "NONE")),
                    anomaly_severity=str(r.get("anomaly_severity", "NONE")),
                    short_explanation=str(r.get("short_explanation", "")),
                )
            )
        except Exception:
            continue

    return rows


def run_concierge_on_invoice_text(raw_text: str) -> ConciergeResult:
    """Run Agentic Invoice Concierge on raw invoice text via Cognee."""
    prompt = f"""You are an Agentic Invoice Concierge.

You will receive raw invoice text from a user. The text may contain:
- vendor name,
- invoice number,
- amounts, currency, dates,
- short description.

Your task:
1. Interpret the text as a single invoice.
2. Normalize and summarise it.
3. Assign a high-level spend category and a simple risk assessment.

Using ONLY the text provided below, and your internal knowledge of common invoice patterns,
produce a JSON object with EXACTLY the following keys:

- invoice_id: string (if no explicit ID is present, generate a short synthetic ID like "NEW-INVOICE-1")
- vendor_name: string
- amount: number
- currency: string
- issue_date: string (YYYY-MM-DD or "UNKNOWN")
- due_date: string (YYYY-MM-DD or "UNKNOWN")
- category: string ("SOFTWARE" | "MARKETING" | "TRAVEL" | "HARDWARE" | "SERVICES" | "OTHER")
- risk_score: number between 0.0 and 1.0
- risk_label: string ("LOW" | "MEDIUM" | "HIGH")
- triage_status: string ("READY_FOR_RECON" | "NEEDS_REVIEW")

Raw invoice text:
\"\"\"{raw_text}\"\"\" 

Return ONLY the JSON object, with no extra commentary.
"""
    data = ask_cognee_json(prompt)

    return ConciergeResult(
        invoice_id=str(data.get("invoice_id", "NEW-INVOICE")),
        vendor_name=str(data.get("vendor_name", "UNKNOWN VENDOR")),
        amount=float(data.get("amount", 0.0)),
        currency=str(data.get("currency", "EUR")),
        issue_date=str(data.get("issue_date", "UNKNOWN")),
        due_date=str(data.get("due_date", "UNKNOWN")),
        category=str(data.get("category", "OTHER")),
        risk_score=float(data.get("risk_score", 0.0)),
        risk_label=str(data.get("risk_label", "LOW")),
        triage_status=str(data.get("triage_status", "READY_FOR_RECON")),
    )


def get_global_anomalies(limit: int = 20) -> List[AnomalyCard]:
    """Ask Cognee for a list of the most important anomalies."""
    prompt = f"""You are a Financial Anomaly Mini-Detective.

Using ONLY the Cognee knowledge graph of vendors, invoices and payments,
identify up to {limit} of the most relevant anomalies in the current data.

Return a JSON array of objects, each with EXACTLY:
- invoice_id: string
- vendor_name: string
- severity: string ("LOW" | "MEDIUM" | "HIGH")
- reason_codes: list of short strings (e.g. ["AMOUNT_OUTLIER", "NO_MATCH"])
- human_explanation: 1–3 sentences
- recommendation: 1–2 sentences with a clear next step

Respond with a single JSON array only, no extra keys. If you cannot produce a valid JSON array, return [].
"""
    data = ask_cognee_json(prompt)

    cards: List[AnomalyCard] = []
    raw_cards = data if isinstance(data, list) else data.get("anomalies", [])

    import logging
    logging.getLogger(__name__).debug("anomalies raw_cards=%d data_error=%s", len(raw_cards), data.get("error") if isinstance(data, dict) else None)

    for c in raw_cards:
        try:
            cards.append(
                AnomalyCard(
                    invoice_id=str(c.get("invoice_id")),
                    vendor_name=str(c.get("vendor_name")),
                    severity=str(c.get("severity", "LOW")),
                    reason_codes=list(c.get("reason_codes", [])),
                    human_explanation=str(c.get("human_explanation", "")),
                    recommendation=str(c.get("recommendation", "")),
                )
            )
        except Exception:
            continue

    return cards


# --- Missing Invoice Detective ---

_MISSING_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "cognee-minihack"
    / "prompts"
    / "missing_invoice_prompt.txt"
)


def _load_missing_prompt() -> str:
    try:
        return _MISSING_PROMPT_PATH.read_text()
    except Exception:
        return ""


def run_missing_invoice_detective(
    vendor: str, period: str, cadence_hint: str = "unknown"
):
    """
    Run Missing Invoice Detective using the custom prompt template.

    Returns parsed JSON (dict) or an error object.
    """
    template = _load_missing_prompt()
    if not template:
        return {"error": f"Missing prompt file at {_MISSING_PROMPT_PATH}"}

    filled = (
        template.replace("{{VENDOR_NAME_OR_ID}}", vendor)
        .replace("{{DATE_RANGE}}", period)
        .replace("{{CADENCE_HINT}}", cadence_hint or "unknown")
    )

    return ask_cognee_json(filled)
