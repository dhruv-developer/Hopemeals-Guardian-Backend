# app/services/forensics_service.py
import os
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.forensics.ela import save_ela

ELA_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "ela")

async def run_ela(db: AsyncIOMotorDatabase, evidence_id: str) -> dict:
    evid = await db.evidence.find_one({"_id": {"$eq": evidence_id} })
    if evid is None:
        # try string to ObjectId fallback
        from bson import ObjectId
        try:
            evid = await db.evidence.find_one({"_id": ObjectId(evidence_id)})
        except Exception:
            evid = None
    if not evid:
        raise HTTPException(status_code=404, detail="Evidence not found")

    os.makedirs(ELA_DIR, exist_ok=True)
    fname = os.path.basename(evid["path"])
    out_path = os.path.join(ELA_DIR, f"{evidence_id}.png")
    ela_path, suspicion = save_ela(evid["path"], out_path)
    return {"ela_path": ela_path, "suspicion": suspicion}
