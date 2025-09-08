# # app/routers/events.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from motor.motor_asyncio import AsyncIOMotorDatabase
# from app.deps import get_db
# from app.schemas.event import EventCreate, EventOut
# from typing import List

# router = APIRouter(prefix="/events", tags=["events"])

# @router.post("", response_model=dict)
# async def create_event(payload: EventCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
#     doc = payload.model_dump()
#     res = await db.events.insert_one(doc)
#     await db.events.update_one({"_id": res.inserted_id}, {"$set": {"status": "pending"}})
#     return {"event_id": str(res.inserted_id), "status": "stored"}

# @router.get("/{event_id}", response_model=dict)
# async def get_event(event_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
#     from bson import ObjectId
#     try:
#         ev = await db.events.find_one({"_id": ObjectId(event_id)})
#     except Exception:
#         ev = await db.events.find_one({"_id": event_id})
#     if not ev:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
#     evidences = [e async for e in db.evidence.find({"event_id": event_id})]
#     alerts = [a async for a in db.alerts.find({"event_id": event_id}).sort([("created_at", -1)])]
#     ev["id"] = str(ev.get("_id"))
#     return {"event": ev, "evidence": evidences, "alerts": alerts}

# app/routers/events.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deps import get_db
from app.schemas.event import EventCreate
from typing import List

# Try to import the safe anchoring helper; fall back to a no-op if missing
try:
    from app.services.events_ledger_integration import safe_anchor_event
except Exception:
    def safe_anchor_event(_event_doc):  # type: ignore
        return None

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=dict)
async def create_event(
    payload: EventCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    # Persist the raw doc (allows Mongo to keep datetime types)
    doc = payload.model_dump()
    res = await db.events.insert_one(doc)
    await db.events.update_one({"_id": res.inserted_id}, {"$set": {"status": "pending"}})

    # JSON-safe copy for background anchoring (datetimes -> ISO strings)
    event_doc_json = payload.model_dump(mode="json")
    event_doc_json.update({"_id": str(res.inserted_id), "status": "pending"})

    # Schedule anchoring (events ledger + blockchain); never breaks the request
    if background_tasks is not None:
        background_tasks.add_task(safe_anchor_event, event_doc_json)
    else:
        try:
            safe_anchor_event(event_doc_json)
        except Exception as e:
            print(f"[events-anchor][fallback] non-fatal: {e}")

    return {"event_id": str(res.inserted_id), "status": "stored"}


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    from bson import ObjectId
    try:
        ev = await db.events.find_one({"_id": ObjectId(event_id)})
    except Exception:
        ev = await db.events.find_one({"_id": event_id})
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    evidences = [e async for e in db.evidence.find({"event_id": event_id})]
    alerts = [a async for a in db.alerts.find({"event_id": event_id}).sort([("created_at", -1)])]
    ev["id"] = str(ev.get("_id"))
    return {"event": ev, "evidence": evidences, "alerts": alerts}
