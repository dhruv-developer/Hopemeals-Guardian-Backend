# app/services/ledger_service.py
import os, json, hashlib
from datetime import datetime
from typing import Tuple

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "ledger", "chain.jsonl")

def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _compute_record_hash(rec_wo_hash: dict) -> str:
    canonical = json.dumps(rec_wo_hash, sort_keys=True, separators=(",", ":"))
    return _sha256_str(canonical)

def append_ledger(evidence_id: str, file_sha256: str) -> dict:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    prev = "GENESIS"
    index = 0
    if os.path.exists(LEDGER_PATH) and os.path.getsize(LEDGER_PATH) > 0:
        with open(LEDGER_PATH, "rb") as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()
        last = json.loads(last_line)
        prev = last["record_hash"]
        index = last["index"] + 1

    base = {
        "index": index,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evidence_id": evidence_id,
        "sha256": file_sha256,
        "prev_hash": prev
    }
    rh = _compute_record_hash(base)
    rec = {**base, "record_hash": rh}

    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return rec

def verify_ledger() -> Tuple[bool, int]:
    if not os.path.exists(LEDGER_PATH):
        return True, 0
    prev = "GENESIS"
    count = 0
    with open(LEDGER_PATH) as f:
        for line in f:
            rec = json.loads(line)
            record_hash = rec["record_hash"]
            base = {k: v for k, v in rec.items() if k != "record_hash"}
            if base["prev_hash"] != prev:
                return False, count
            if _compute_record_hash(base) != record_hash:
                return False, count
            prev = record_hash
            count += 1
    return True, count
