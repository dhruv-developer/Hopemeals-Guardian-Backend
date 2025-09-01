# app/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Literal

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["admin", "investigator", "field"] = "investigator"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    role: str
