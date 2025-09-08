# # app/services/events_ledger_service.py
# import os, json
# from datetime import datetime
# from typing import Tuple, Optional, List, Dict, Any

# from app.services import blockchain_service  # uses BLOCKCHAIN_MODE as before

# LEDGER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ledger", "events_chain.jsonl"))
# ANCHORS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ledger", "anchors.jsonl"))


# def _sha256_str(s: str) -> str:
#     import hashlib
#     return hashlib.sha256(s.encode("utf-8")).hexdigest()


# def _canonical_json(o: Any) -> str:
#     return json.dumps(o, sort_keys=True, separators=(",", ":"))


# def _ensure_dirs() -> None:
#     os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)


# def _read_last_record() -> Optional[dict]:
#     if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
#         return None
#     with open(LEDGER_PATH, "r") as f:
#         lines = f.readlines()
#     for line in reversed(lines):
#         s = line.strip()
#         if not s:
#             continue
#         try:
#             return json.loads(s)
#         except Exception:
#             continue
#     return None


# def fingerprint_event(event_doc: Dict[str, Any]) -> str:
#     """
#     Produce a deterministic fingerprint for an event.
#     Only stable, relevant fields are included. Beneficiaries are sorted to avoid order effects.
#     """
#     gps = event_doc.get("gps") or {}
#     bene = event_doc.get("beneficiary_ids") or []
#     try:
#         bene = list(bene)
#     except Exception:
#         bene = []
#     bene_sorted = sorted([str(x) for x in bene])

#     # allow both "_id" (ObjectId) and "event_id" strings
#     event_id = str(event_doc.get("_id") or event_doc.get("event_id") or "")

#     core = {
#         "event_id": event_id,
#         "donor_id": event_doc.get("donor_id"),
#         "ngo_id": event_doc.get("ngo_id"),
#         "quantity": event_doc.get("quantity"),
#         "unit": event_doc.get("unit"),
#         "gps": {
#             "lat": float(gps.get("lat")) if gps.get("lat") is not None else None,
#             "lon": float(gps.get("lon")) if gps.get("lon") is not None else None,
#         },
#         "timestamp": event_doc.get("timestamp"),
#         "device_id": event_doc.get("device_id"),
#         "ip": event_doc.get("ip"),
#         "beneficiary_ids": bene_sorted,
#     }
#     return _sha256_str(_canonical_json(core))


# def _compute_record_hash(rec_wo_hash: dict) -> str:
#     return _sha256_str(_canonical_json(rec_wo_hash))


# def append_event_ledger(event_doc: Dict[str, Any]) -> dict:
#     """
#     Append an event to the events ledger, link to previous, anchor record hash to blockchain.
#     Returns the full ledger record (does not change /events response).
#     """
#     _ensure_dirs()

#     last = _read_last_record()
#     if last:
#         prev = last["record_hash"]
#         index = int(last["index"]) + 1
#     else:
#         prev = "GENESIS"
#         index = 0

#     ev_fingerprint = fingerprint_event(event_doc)

#     base = {
#         "index": index,
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#         "event_id": str(event_doc.get("_id") or event_doc.get("event_id") or ""),
#         "fingerprint": ev_fingerprint,
#         "prev_hash": prev,
#     }
#     rh = _compute_record_hash(base)
#     rec = {**base, "record_hash": rh}

#     with open(LEDGER_PATH, "a") as f:
#         f.write(json.dumps(rec, separators=(",", ":")) + "\n")

#     # Anchor to blockchain (never break request if it fails)
#     try:
#         anchor_info = blockchain_service.maybe_anchor(rec["record_hash"])
#         if anchor_info:
#             with open(ANCHORS_PATH, "a") as sf:
#                 sf.write(
#                     json.dumps(
#                         {
#                             "source": "event",
#                             "ledger_index": index,
#                             "record_hash": rh,
#                             "anchor": anchor_info,
#                         },
#                         separators=(",", ":"),
#                     )
#                     + "\n"
#                 )
#     except Exception as e:
#         print(f"[events-ledger->anchor] non-fatal error: {e}")

#     return rec


# def verify_events_ledger() -> Tuple[bool, int]:
#     if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
#         return True, 0

#     prev = "GENESIS"
#     count = 0

#     with open(LEDGER_PATH, "r") as f:
#         for line in f:
#             s = line.strip()
#             if not s:
#                 continue
#             try:
#                 rec = json.loads(s)
#             except Exception:
#                 return False, count

#             record_hash = rec.get("record_hash")
#             base = {k: v for k, v in rec.items() if k != "record_hash"}

#             if base.get("prev_hash") != prev:
#                 return False, count
#             if _compute_record_hash(base) != record_hash:
#                 return False, count

#             prev = record_hash
#             count += 1

#     return True, count


# def tail(limit: int = 50) -> List[dict]:
#     if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
#         return []
#     with open(LEDGER_PATH, "r") as f:
#         lines = f.readlines()[-limit:]
#     out = []
#     for s in lines:
#         s = s.strip()
#         if not s:
#             continue
#         try:
#             out.append(json.loads(s))
#         except Exception:
#             continue
#     return out


# app/services/events_ledger_service.py
import os, json
from datetime import datetime, date, timezone
from typing import Tuple, Optional, List, Dict, Any

from app.services import blockchain_service  # uses BLOCKCHAIN_MODE as before

LEDGER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ledger", "events_chain.jsonl"))
ANCHORS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ledger", "anchors.jsonl"))

def _sha256_str(s: str) -> str:
    import hashlib
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _canonical_json(o: Any) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))

def _ensure_dirs() -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)

def _read_last_record() -> Optional[dict]:
    if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
        return None
    with open(LEDGER_PATH, "r") as f:
        lines = f.readlines()
    for line in reversed(lines):
        s = line.strip()
        if not s:
            continue
        try:
            return json.loads(s)
        except Exception:
            continue
    return None

def _to_iso(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, datetime):
        # normalize to UTC if naive
        if val.tzinfo is None:
            val = val.replace(tzinfo=timezone.utc)
        return val.isoformat()
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day, tzinfo=timezone.utc).isoformat()
    # already a string or other primitive
    return str(val)

def fingerprint_event(event_doc: Dict[str, Any]) -> str:
    """
    Deterministic fingerprint for an event.
    Beneficiaries sorted; timestamp coerced to ISO; _id stringified.
    """
    gps = event_doc.get("gps") or {}
    bene = event_doc.get("beneficiary_ids") or []
    try:
        bene = list(bene)
    except Exception:
        bene = []
    bene_sorted = sorted([str(x) for x in bene])

    event_id = str(event_doc.get("_id") or event_doc.get("event_id") or "")

    core = {
        "event_id": event_id,
        "donor_id": event_doc.get("donor_id"),
        "ngo_id": event_doc.get("ngo_id"),
        "quantity": event_doc.get("quantity"),
        "unit": event_doc.get("unit"),
        "gps": {
            "lat": float(gps.get("lat")) if gps.get("lat") is not None else None,
            "lon": float(gps.get("lon")) if gps.get("lon") is not None else None,
        },
        "timestamp": _to_iso(event_doc.get("timestamp")),
        "device_id": event_doc.get("device_id"),
        "ip": event_doc.get("ip"),
        "beneficiary_ids": bene_sorted,
    }
    return _sha256_str(_canonical_json(core))

def _compute_record_hash(rec_wo_hash: dict) -> str:
    return _sha256_str(_canonical_json(rec_wo_hash))

def append_event_ledger(event_doc: Dict[str, Any]) -> dict:
    """
    Append an event to the events ledger, link to previous, anchor record hash to blockchain.
    """
    _ensure_dirs()

    last = _read_last_record()
    if last:
        prev = last["record_hash"]
        index = int(last["index"]) + 1
    else:
        prev = "GENESIS"
        index = 0

    ev_fingerprint = fingerprint_event(event_doc)

    base = {
        "index": index,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_id": str(event_doc.get("_id") or event_doc.get("event_id") or ""),
        "fingerprint": ev_fingerprint,
        "prev_hash": prev,
    }
    rh = _compute_record_hash(base)
    rec = {**base, "record_hash": rh}

    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")

    # Anchor to blockchain (never break request if it fails)
    try:
        anchor_info = blockchain_service.maybe_anchor(rec["record_hash"])
        if anchor_info:
            with open(ANCHORS_PATH, "a") as sf:
                sf.write(
                    json.dumps(
                        {"source": "event", "ledger_index": index, "record_hash": rh, "anchor": anchor_info},
                        separators=(",", ":"),
                    )
                    + "\n"
                )
    except Exception as e:
        print(f"[events-ledger->anchor] non-fatal error: {e}")

    return rec

def verify_events_ledger() -> Tuple[bool, int]:
    if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
        return True, 0

    prev = "GENESIS"
    count = 0

    with open(LEDGER_PATH, "r") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                rec = json.loads(s)
            except Exception:
                return False, count

            record_hash = rec.get("record_hash")
            base = {k: v for k, v in rec.items() if k != "record_hash"}

            if base.get("prev_hash") != prev:
                return False, count
            if _compute_record_hash(base) != record_hash:
                return False, count

            prev = record_hash
            count += 1

    return True, count

def tail(limit: int = 50) -> List[dict]:
    if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
        return []
    with open(LEDGER_PATH, "r") as f:
        lines = f.readlines()[-limit:]
    out = []
    for s in lines:
        s = s.strip()
        if not s:
            continue
        try:
            out.append(json.loads(s))
        except Exception:
            continue
    return out
