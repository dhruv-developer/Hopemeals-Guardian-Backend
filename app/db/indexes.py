# app/db/indexes.py
from motor.motor_asyncio import AsyncIOMotorDatabase

async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index("email", unique=True)
    await db.events.create_index([("timestamp", 1)])
    await db.events.create_index([("device_id", 1), ("timestamp", 1)])
    await db.evidence.create_index([("event_id", 1)])
    await db.alerts.create_index([("created_at", 1)])
