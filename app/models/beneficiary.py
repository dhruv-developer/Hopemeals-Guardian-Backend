# app/models/beneficiary.py
from typing import Optional
from pydantic import BaseModel, Field

class BeneficiaryModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    phone_hash: str | None = None
    address_hash: str | None = None

    class Config:
        populate_by_name = True
