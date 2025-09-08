# app/services/events_ledger_integration.py
"""
One-line integration helper. Safe to call after you persist the event.
It will:
- Append to the events ledger (hash-linked)
- Anchor the record hash to the selected blockchain mode

Any failure is swallowed and logged, so it can't break your /events endpoint.
"""

from typing import Dict, Any
from app.services.events_ledger_service import append_event_ledger

def safe_anchor_event(event_doc: Dict[str, Any]) -> None:
    try:
        append_event_ledger(event_doc)
    except Exception as e:
        print(f"[safe_anchor_event] non-fatal: {e}")
