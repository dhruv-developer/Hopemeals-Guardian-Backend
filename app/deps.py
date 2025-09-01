# app/deps.py
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.db.mongo import get_client

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client: AsyncIOMotorClient = get_client()
    db = client[settings.MONGO_DB]
    try:
        yield db
    finally:
        # keep client cached; do not close per request
        pass
