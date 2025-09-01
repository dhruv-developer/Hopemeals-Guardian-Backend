# app/models/evidence.py
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

EvidenceType = Literal["image", "csv", "json", "note"]

class EvidenceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    event_id: str
    type: EvidenceType
    path: str
    sha256: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
