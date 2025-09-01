# app/db/mongo.py
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

@lru_cache()
def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_URI, uuidRepresentation="standard")
