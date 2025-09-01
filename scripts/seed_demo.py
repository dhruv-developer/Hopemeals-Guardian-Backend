# scripts/seed_demo.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.utils.hashing import hash_password

async def main():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    # Admin user if not exists
    admin = await db.users.find_one({"email": "admin@example.com"})
    if not admin:
        await db.users.insert_one({
            "email": "admin@example.com",
            "password_hash": hash_password("admin123"),
            "role": "admin",
        })
        print("Seeded admin: admin@example.com / admin123")
    else:
        print("Admin already exists")

    # Minimal donors/ngos
    if await db.donors.count_documents({}) == 0:
        await db.donors.insert_many([{"name": f"Donor {i}"} for i in range(1, 6)])
        print("Seeded donors")
    if await db.ngos.count_documents({}) == 0:
        await db.ngos.insert_many([{"name": f"NGO {i}"} for i in range(1, 6)])
        print("Seeded NGOs")

if __name__ == "__main__":
    asyncio.run(main())
