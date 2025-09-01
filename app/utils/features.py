# app/utils/features.py
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.utils.geo import haversine_km

def build_features(events: List[Dict[str, Any]]) -> Tuple[list[list[float]], list[str]]:
    """
    Minimal demo features:
      [quantity, hour, gps_jump_km, unique_beneficiaries]
    """
    events_sorted = sorted(events, key=lambda x: x["timestamp"])
    dev_last: Dict[str, tuple[float, float]] = {}
    X: list[list[float]] = []
    meta: list[str] = []

    for ev in events_sorted:
        ts = ev["timestamp"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", ""))
        hour = ts.hour
        jump = 0.0
        if ev["device_id"] in dev_last:
            lat0, lon0 = dev_last[ev["device_id"]]
            jump = haversine_km(lat0, lon0, ev["gps"]["lat"], ev["gps"]["lon"])
        dev_last[ev["device_id"]] = (ev["gps"]["lat"], ev["gps"]["lon"])
        qty = float(ev["quantity"])
        uniq_b = float(len(set(ev.get("beneficiary_ids", []))))
        X.append([qty, float(hour), float(jump), uniq_b])
        meta.append(ev["_id"])
    return X, meta
