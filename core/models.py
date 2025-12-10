
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class DashboardRow:
    """One row in the main reconciliation dashboard."""
    invoice_id: str
    vendor_name: str
    amount: float
    currency: str
    match_status: str
    match_type: str
    anomaly_severity: str
    short_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConciergeResult:
    """Result of Agentic Invoice Concierge for a single invoice."""
    invoice_id: str
    vendor_name: str
    amount: float
    currency: str
    issue_date: str
    due_date: str
    category: str
    risk_score: float
    risk_label: str
    triage_status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnomalyCard:
    """One anomaly card for the right-hand panel (Financial Anomaly Mini-Detective)."""
    invoice_id: str
    vendor_name: str
    severity: str
    reason_codes: List[str]
    human_explanation: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
