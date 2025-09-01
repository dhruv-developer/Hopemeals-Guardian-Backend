# app/models/donor.py
from typing import Optional
from pydantic import BaseModel, Field

class DonorModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    contact: str | None = None
    phone: str | None = None
    address: str | None = None

    class Config:
        populate_by_name = True
