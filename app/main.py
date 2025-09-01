# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.mongo import get_client
from app.db.indexes import ensure_indexes

from app.routers import health, auth, events, evidence, analyze, forensics, nlp

app = FastAPI(title=settings.APP_NAME)

# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(evidence.router)
app.include_router(analyze.router)
app.include_router(forensics.router)
app.include_router(nlp.router)

@app.on_event("startup")
async def on_startup():
    # warm up Mongo and ensure indexes
    db = get_client()[settings.MONGO_DB]
    await ensure_indexes(db)
