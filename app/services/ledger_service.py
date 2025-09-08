# # app/services/ledger_service.py
# import os, json, hashlib
# from datetime import datetime
# from typing import Tuple

# LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "ledger", "chain.jsonl")

# def _sha256_str(s: str) -> str:
#     return hashlib.sha256(s.encode("utf-8")).hexdigest()

# def _compute_record_hash(rec_wo_hash: dict) -> str:
#     canonical = json.dumps(rec_wo_hash, sort_keys=True, separators=(",", ":"))
#     return _sha256_str(canonical)

# def append_ledger(evidence_id: str, file_sha256: str) -> dict:
#     os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
#     prev = "GENESIS"
#     index = 0
#     if os.path.exists(LEDGER_PATH) and os.path.getsize(LEDGER_PATH) > 0:
#         with open(LEDGER_PATH, "rb") as f:
#             f.seek(-2, os.SEEK_END)
#             while f.read(1) != b"\n":
#                 f.seek(-2, os.SEEK_CUR)
#             last_line = f.readline().decode()
#         last = json.loads(last_line)
#         prev = last["record_hash"]
#         index = last["index"] + 1

#     base = {
#         "index": index,
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#         "evidence_id": evidence_id,
#         "sha256": file_sha256,
#         "prev_hash": prev
#     }
#     rh = _compute_record_hash(base)
#     rec = {**base, "record_hash": rh}

#     with open(LEDGER_PATH, "a") as f:
#         f.write(json.dumps(rec, separators=(",", ":")) + "\n")
#     return rec

# def verify_ledger() -> Tuple[bool, int]:
#     if not os.path.exists(LEDGER_PATH):
#         return True, 0
#     prev = "GENESIS"
#     count = 0
#     with open(LEDGER_PATH) as f:
#         for line in f:
#             rec = json.loads(line)
#             record_hash = rec["record_hash"]
#             base = {k: v for k, v in rec.items() if k != "record_hash"}
#             if base["prev_hash"] != prev:
#                 return False, count
#             if _compute_record_hash(base) != record_hash:
#                 return False, count
#             prev = record_hash
#             count += 1
#     return True, count
# filename: app/services/ledger_service.py
import os
import json
from datetime import datetime
from typing import Tuple, Optional

from app.services import blockchain_service  # optional anchoring (non-fatal if fails)

LEDGER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ledger", "chain.jsonl")
)
ANCHORS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ledger", "anchors.jsonl")
)


def _sha256_str(s: str) -> str:
    import hashlib

    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _compute_record_hash(rec_wo_hash: dict) -> str:
    # Canonicalize for deterministic hashing
    canonical = json.dumps(rec_wo_hash, sort_keys=True, separators=(",", ":"))
    return _sha256_str(canonical)


def _ensure_dirs() -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)


def _read_last_record() -> Optional[dict]:
    """Robust last-line reader (no negative seeks). Returns None if no records yet."""
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
            # skip malformed lines instead of crashing
            continue
    return None


def append_ledger(evidence_id: str, file_sha256: str) -> dict:
    """
    Append a new ledger record that hash-links to the previous one.

    Returns the full record:
        {
          "index": int,
          "timestamp": "...Z",
          "evidence_id": str,
          "sha256": str,
          "prev_hash": str,
          "record_hash": str
        }
    """
    _ensure_dirs()

    last = _read_last_record()
    if last:
        prev = last["record_hash"]
        index = int(last["index"]) + 1
    else:
        prev = "GENESIS"
        index = 0

    base = {
        "index": index,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evidence_id": evidence_id,
        "sha256": file_sha256,
        "prev_hash": prev,
    }
    rh = _compute_record_hash(base)
    rec = {**base, "record_hash": rh}

    # Append atomically enough for our local demo
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")

    # ---- Optional: anchor to blockchain (never break the request) ----
    try:
        anchor_info = blockchain_service.maybe_anchor(rec["record_hash"])
        if anchor_info:
            with open(ANCHORS_PATH, "a") as sf:
                sf.write(
                    json.dumps(
                        {"ledger_index": index, "record_hash": rh, "anchor": anchor_info},
                        separators=(",", ":"),
                    )
                    + "\n"
                )
    except Exception as e:
        # Non-fatal by design
        print(f"[ledger->anchor] non-fatal error: {e}")
    # -----------------------------------------------------------------

    return rec


def verify_ledger() -> Tuple[bool, int]:
    """
    Verify the entire ledger chain.
    Returns (ok, length).
    """
    if not os.path.exists(LEDGER_PATH) or os.path.getsize(LEDGER_PATH) == 0:
        # Empty chain is considered valid with length 0
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

            # recompute and compare hash
            record_hash = rec.get("record_hash")
            base = {k: v for k, v in rec.items() if k != "record_hash"}
            if base.get("prev_hash") != prev:
                return False, count
            if _compute_record_hash(base) != record_hash:
                return False, count

            prev = record_hash
            count += 1

    return True, count
