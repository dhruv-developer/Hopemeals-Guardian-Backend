# app/models/user.py
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

Role = Literal["admin", "investigator", "field"]

class UserModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    password_hash: str
    role: Role = "investigator"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
