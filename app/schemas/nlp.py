# app/schemas/nlp.py
from pydantic import BaseModel
from typing import List, Dict

class SummarizeRequest(BaseModel):
    text: str
    max_points: int = 5

class SummarizeResponse(BaseModel):
    summary: str
    entities: Dict[str, List[str]]
