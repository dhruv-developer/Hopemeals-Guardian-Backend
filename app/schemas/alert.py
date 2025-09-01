# app/schemas/alert.py
from pydantic import BaseModel
from typing import List

class AnalyzeRequest(BaseModel):
    limit: int = 200

class AlertOut(BaseModel):
    alert_id: str
    event_id: str
    severity: int
    reasons: List[str]
    score: float
    created_at: str
    status: str
