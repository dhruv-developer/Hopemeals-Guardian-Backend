# app/schemas/common.py
from pydantic import BaseModel

class Message(BaseModel):
    message: str
