# app/routers/blockchain.py
from fastapi import APIRouter, Query
from typing import Optional
from app.services.blockchain_service import status as bc_status, chain_tail, verify, find_anchor
from app.services.blockchain_service import maybe_anchor

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

@router.get("/status", response_model=dict)
async def status():
    return bc_status()

@router.get("/chain", response_model=list[dict])
async def chain(limit: int = Query(50, ge=1, le=500)):
    return chain_tail(limit=limit)

@router.get("/verify", response_model=dict)
async def verify_chain():
    return verify()

@router.get("/anchor/{record_hash}", response_model=dict | None)
async def get_anchor(record_hash: str):
    # Only supported for local mode fast lookup
    return find_anchor(record_hash)

@router.post("/anchor", response_model=dict | None)
async def anchor_body(payload: dict):
    """
    Manually anchor an arbitrary string:
    body: { "text": "..." } or { "record_hash": "..." }
    """
    text = payload.get("record_hash") or payload.get("text")
    if not text:
        return {"error": "missing text or record_hash"}
    return maybe_anchor(text)
