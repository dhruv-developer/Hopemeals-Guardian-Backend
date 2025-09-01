# app/routers/forensics.py
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deps import get_db
from app.schemas.evidence import ELARequest, ELAResponse
from app.services.forensics_service import run_ela

router = APIRouter(prefix="/forensics", tags=["forensics"])

@router.post("/ela", response_model=ELAResponse)
async def ela(req: ELARequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    res = await run_ela(db, req.evidence_id)
    return ELAResponse(**res)
