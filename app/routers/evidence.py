# app/routers/evidence.py
from fastapi import APIRouter, Depends, UploadFile, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deps import get_db
from app.schemas.evidence import EvidenceUploadOut
from app.services.evidence_service import save_evidence
from app.services.ledger_service import verify_ledger

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.post("/upload", response_model=EvidenceUploadOut)
async def upload_evidence(
    event_id: str = Form(...),
    type: str = Form(...),
    blob: UploadFile = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await save_evidence(db, event_id, type, blob)

@router.get("/ledger/verify", response_model=dict)
async def ledger_verify():
    ok, n = verify_ledger()
    return {"ok": ok, "length": n}
