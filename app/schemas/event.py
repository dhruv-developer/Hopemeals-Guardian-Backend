# app/schemas/event.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class GPSIn(BaseModel):
    lat: float
    lon: float

class EventCreate(BaseModel):
    donor_id: str
    ngo_id: str
    quantity: int
    unit: str = "meals"
    gps: GPSIn
    timestamp: datetime
    device_id: str
    ip: str
    beneficiary_ids: List[str] = []

class EventOut(EventCreate):
    id: str
    status: str
