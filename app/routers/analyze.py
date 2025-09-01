# app/routers/analyze.py
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deps import get_db
from app.schemas.alert import AnalyzeRequest

from app.services.analyze_service import run_anomaly

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/run", response_model=dict)
async def analyze(req: AnalyzeRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    created = await run_anomaly(db, limit=req.limit)
    return {"alerts_created": created}

@router.get("/alerts", response_model=list[dict])
async def list_alerts(db: AsyncIOMotorDatabase = Depends(get_db)):
    items = [a async for a in db.alerts.find().sort([("created_at", -1)]).limit(200)]
    # stringify _id and created_at
    out = []
    for a in items:
        a["alert_id"] = str(a["_id"])
        a["created_at"] = a["created_at"].isoformat() + "Z"
        out.append(a)
    return out
