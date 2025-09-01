# app/models/event.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class GPS(BaseModel):
    lat: float
    lon: float

class EventModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    donor_id: str
    ngo_id: str
    quantity: int
    unit: str = "meals"
    gps: GPS
    timestamp: datetime
    device_id: str
    ip: str
    beneficiary_ids: List[str] = []
    status: str = "pending"  # pending|held|released|closed

    class Config:
        populate_by_name = True
