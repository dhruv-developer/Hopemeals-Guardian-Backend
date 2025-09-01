# app/services/evidence_service.py
import os, hashlib
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, UploadFile
from app.services.ledger_service import append_ledger

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")

async def save_evidence(db: AsyncIOMotorDatabase, event_id: str, ev_type: str, blob: UploadFile) -> dict:
    os.makedirs(STORAGE_DIR, exist_ok=True)
    filename = f"{event_id}_{blob.filename}"
    path = os.path.join(STORAGE_DIR, filename)
    data = await blob.read()
    with open(path, "wb") as f:
        f.write(data)
    sha256 = hashlib.sha256(data).hexdigest()
    ledger_rec = append_ledger(evidence_id=filename, file_sha256=sha256)
    doc = {
        "event_id": event_id,
        "type": ev_type,
        "path": path,
        "sha256": sha256
    }
    res = await db.evidence.insert_one(doc)
    return {
        "evidence_id": str(res.inserted_id),
        "sha256": sha256,
        "ledger_index": ledger_rec["index"],
        "status": "recorded",
    }
