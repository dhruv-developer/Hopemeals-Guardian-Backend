# app/services/auth_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.utils.hashing import hash_password, verify_password

async def create_user(db: AsyncIOMotorDatabase, email: str, password: str, role: str) -> str:
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
    doc = {"email": email, "password_hash": hash_password(password), "role": role}
    res = await db.users.insert_one(doc)
    return str(res.inserted_id)

async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str) -> dict:
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user
