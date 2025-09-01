# app/schemas/evidence.py
from pydantic import BaseModel
from typing import Literal

class EvidenceUploadOut(BaseModel):
    evidence_id: str
    sha256: str
    ledger_index: int
    status: str

class ELARequest(BaseModel):
    evidence_id: str

class ELAResponse(BaseModel):
    ela_path: str
    suspicion: float
