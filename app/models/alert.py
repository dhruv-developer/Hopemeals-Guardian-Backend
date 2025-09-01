# app/models/alert.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class AlertModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    event_id: str
    severity: int = 2
    reasons: List[str] = []
    score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"  # open|ack|closed

    class Config:
        populate_by_name = True
