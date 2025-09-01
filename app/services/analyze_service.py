# app/services/analyze_service.py
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
import numpy as np
from sklearn.ensemble import IsolationForest
from app.utils.features import build_features

async def run_anomaly(db: AsyncIOMotorDatabase, limit: int = 200) -> int:
    cur = db.events.find().sort([("timestamp", -1)]).limit(limit)
    events = [e async for e in cur]
    if not events:
        return 0

    X, meta = build_features(events)
    if not X:
        return 0

    clf = IsolationForest(random_state=42, contamination=0.03)
    clf.fit(X)
    scores = -clf.score_samples(X)
    thr = float(np.percentile(scores, 97))

    created = 0
    for eid, s, feat in zip(meta, scores, X):
        qty, hour, jump, uniq_b = feat
        reasons = []
        if qty > 240:
            reasons.append("surge_volume")
        if jump > 500:
            reasons.append("impossible_route")
        if s >= thr or reasons:
            alert = {
                "event_id": eid,
                "severity": 3 if s >= float(np.percentile(scores, 99)) else 2,
                "reasons": reasons or ["model_anomaly"],
                "score": float(s),
                "created_at": datetime.utcnow(),
                "status": "open",
            }
            await db.alerts.insert_one(alert)
            created += 1
    return created
