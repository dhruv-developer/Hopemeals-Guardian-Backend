# app/routers/events_ledger.py
from fastapi import APIRouter, Query
from app.services.events_ledger_service import verify_events_ledger, tail

router = APIRouter(prefix="/events/ledger", tags=["events-ledger"])

@router.get("/verify", response_model=dict)
async def verify():
    ok, length = verify_events_ledger()
    return {"ok": ok, "length": length}

@router.get("", response_model=list[dict])
async def list_tail(limit: int = Query(25, ge=1, le=500)):
    return tail(limit=limit)
