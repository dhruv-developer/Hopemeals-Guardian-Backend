# # app/blockchain/localchain.py
# """
# Lightweight local blockchain with Proof of Work (file-based).
# Anchors ledger record hashes into blocks.

# - Chain file: app/blockchain/blocks.jsonl (append-only)
# - Block hash = SHA256(index|timestamp|prev_hash|data|nonce)
# - Difficulty: leading zeros count (POW_DIFFICULTY)

# APIs:
# - ensure_genesis()
# - add_block(data: str) -> dict
# - verify_chain() -> tuple[bool, int]
# - get_tip() -> dict | None
# - find_by_data(data: str) -> dict | None
# """

# from __future__ import annotations
# import os, json, time, hashlib
# from datetime import datetime
# from typing import Optional, Tuple, List, Dict
# from app.config import settings

# CHAIN_PATH = os.path.join(os.path.dirname(__file__), "blocks.jsonl")

# def _sha256(s: str) -> str:
#     return hashlib.sha256(s.encode("utf-8")).hexdigest()

# def _target_prefix() -> str:
#     return "0" * max(1, int(settings.POW_DIFFICULTY))

# def ensure_genesis() -> dict:
#     os.makedirs(os.path.dirname(CHAIN_PATH), exist_ok=True)
#     if os.path.exists(CHAIN_PATH) and os.path.getsize(CHAIN_PATH) > 0:
#         # already has genesis
#         with open(CHAIN_PATH, "r") as f:
#             first = f.readline()
#             try:
#                 return json.loads(first)
#             except Exception:
#                 pass
#     # create genesis
#     genesis = {
#         "index": 0,
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#         "prev_hash": "GENESIS",
#         "data": "GENESIS",
#         "nonce": 0,
#         "hash": ""
#     }
#     base = f'{genesis["index"]}|{genesis["timestamp"]}|{genesis["prev_hash"]}|{genesis["data"]}|{genesis["nonce"]}'
#     h = _sha256(base)
#     genesis["hash"] = h
#     with open(CHAIN_PATH, "w") as f:
#         f.write(json.dumps(genesis, separators=(",", ":")) + "\n")
#     return genesis

# def _last_line() -> Optional[str]:
#     if not os.path.exists(CHAIN_PATH) or os.path.getsize(CHAIN_PATH) == 0:
#         return None
#     with open(CHAIN_PATH, "rb") as f:
#         f.seek(-2, os.SEEK_END)
#         while f.read(1) != b"\n":
#             f.seek(-2, os.SEEK_CUR)
#         return f.readline().decode()

# def get_tip() -> Optional[dict]:
#     ll = _last_line()
#     if not ll:
#         return None
#     return json.loads(ll)

# def verify_chain() -> Tuple[bool, int]:
#     if not os.path.exists(CHAIN_PATH):
#         return True, 0
#     prev_hash = "GENESIS"
#     cnt = 0
#     prefix = _target_prefix()
#     with open(CHAIN_PATH, "r") as f:
#         for line in f:
#             b = json.loads(line)
#             base = f'{b["index"]}|{b["timestamp"]}|{b["prev_hash"]}|{b["data"]}|{b["nonce"]}'
#             h = _sha256(base)
#             if h != b["hash"]:
#                 return False, cnt
#             if b["index"] == 0:
#                 if b["prev_hash"] != "GENESIS":
#                     return False, cnt
#             else:
#                 if b["prev_hash"] != prev_hash:
#                     return False, cnt
#                 if not h.startswith(prefix):
#                     return False, cnt
#             prev_hash = b["hash"]
#             cnt += 1
#     return True, cnt

# def _mine(index: int, prev_hash: str, data: str) -> dict:
#     prefix = _target_prefix()
#     nonce = 0
#     while True:
#         ts = datetime.utcnow().isoformat() + "Z"
#         base = f"{index}|{ts}|{prev_hash}|{data}|{nonce}"
#         h = _sha256(base)
#         if h.startswith(prefix):
#             return {"index": index, "timestamp": ts, "prev_hash": prev_hash, "data": data, "nonce": nonce, "hash": h}
#         nonce += 1
#         # tiny sleep to avoid pegging CPU on low difficulty in dev
#         if nonce % 20000 == 0:
#             time.sleep(0.001)

# def add_block(data: str) -> dict:
#     ensure_genesis()
#     tip = get_tip()
#     index = (tip["index"] + 1) if tip else 1
#     prev = tip["hash"] if tip else "GENESIS"
#     block = _mine(index, prev, data)
#     with open(CHAIN_PATH, "a") as f:
#         f.write(json.dumps(block, separators=(",", ":")) + "\n")
#     return block

# def find_by_data(data: str) -> Optional[dict]:
#     if not os.path.exists(CHAIN_PATH):
#         return None
#     with open(CHAIN_PATH, "r") as f:
#         for line in f:
#             b = json.loads(line)
#             if b.get("data") == data:
#                 return b
#     return None

# # Ensure genesis on import (safe, idempotent)
# try:
#     ensure_genesis()
# except Exception:
#     pass


# app/blockchain/localchain.py
"""
Lightweight local blockchain with Proof of Work (file-based).
Anchors ledger record hashes into blocks.

- Chain file: app/blockchain/blocks.jsonl (append-only)
- Block hash = SHA256(index|timestamp|prev_hash|data|nonce)
- Difficulty: leading zeros count (POW_DIFFICULTY)

APIs:
- ensure_genesis()
- add_block(data: str) -> dict
- verify_chain() -> tuple[bool, int]
- get_tip() -> dict | None
- find_by_data(data: str) -> dict | None
"""

from __future__ import annotations
import os, json, time, hashlib
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from app.config import settings

CHAIN_PATH = os.path.join(os.path.dirname(__file__), "blocks.jsonl")

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _target_prefix() -> str:
    return "0" * max(1, int(settings.POW_DIFFICULTY))

def ensure_genesis() -> dict:
    """
    Create a genesis block if the chain file is missing or empty, or if the first
    line is invalid JSON. Idempotent and safe to call often.
    """
    os.makedirs(os.path.dirname(CHAIN_PATH), exist_ok=True)

    # Create file with genesis if missing or empty
    if not os.path.exists(CHAIN_PATH) or os.path.getsize(CHAIN_PATH) == 0:
        genesis = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prev_hash": "GENESIS",
            "data": "GENESIS",
            "nonce": 0,
            "hash": "",
        }
        base = f'{genesis["index"]}|{genesis["timestamp"]}|{genesis["prev_hash"]}|{genesis["data"]}|{genesis["nonce"]}'
        genesis["hash"] = _sha256(base)
        with open(CHAIN_PATH, "w") as f:
            f.write(json.dumps(genesis, separators=(",", ":")) + "\n")
        return genesis

    # Validate first line; if bad, rewrite a clean genesis
    try:
        with open(CHAIN_PATH, "r") as f:
            first = f.readline()
        json.loads(first)
    except Exception:
        genesis = {
            "index": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prev_hash": "GENESIS",
            "data": "GENESIS",
            "nonce": 0,
            "hash": "",
        }
        base = f'{genesis["index"]}|{genesis["timestamp"]}|{genesis["prev_hash"]}|{genesis["data"]}|{genesis["nonce"]}'
        genesis["hash"] = _sha256(base)
        with open(CHAIN_PATH, "w") as f:
            f.write(json.dumps(genesis, separators=(",", ":")) + "\n")
        return genesis

    # Already has a valid first line
    with open(CHAIN_PATH, "r") as f:
        return json.loads(f.readline())

def _last_line() -> Optional[str]:
    """
    Robust last-line reader for small files.
    Avoids negative seeks that can fail on 1-line files on macOS.
    """
    if not os.path.exists(CHAIN_PATH) or os.path.getsize(CHAIN_PATH) == 0:
        return None
    with open(CHAIN_PATH, "r") as f:
        lines = f.readlines()
    # return the last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line
    return None

def get_tip() -> Optional[dict]:
    ensure_genesis()
    ll = _last_line()
    if not ll:
        return None
    try:
        return json.loads(ll)
    except Exception:
        return None

def verify_chain() -> Tuple[bool, int]:
    ensure_genesis()
    prev_hash = "GENESIS"
    cnt = 0
    prefix = _target_prefix()
    with open(CHAIN_PATH, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                b = json.loads(line)
            except Exception:
                return False, cnt
            base = f'{b["index"]}|{b["timestamp"]}|{b["prev_hash"]}|{b["data"]}|{b["nonce"]}'
            h = _sha256(base)
            if h != b.get("hash"):
                return False, cnt
            if b["index"] == 0:
                if b.get("prev_hash") != "GENESIS":
                    return False, cnt
            else:
                if b.get("prev_hash") != prev_hash:
                    return False, cnt
                if not h.startswith(prefix):
                    return False, cnt
            prev_hash = b["hash"]
            cnt += 1
    return True, cnt

def _mine(index: int, prev_hash: str, data: str) -> dict:
    prefix = _target_prefix()
    nonce = 0
    while True:
        ts = datetime.utcnow().isoformat() + "Z"
        base = f"{index}|{ts}|{prev_hash}|{data}|{nonce}"
        h = _sha256(base)
        if h.startswith(prefix):
            return {"index": index, "timestamp": ts, "prev_hash": prev_hash, "data": data, "nonce": nonce, "hash": h}
        nonce += 1
        if nonce % 20000 == 0:
            time.sleep(0.001)

def add_block(data: str) -> dict:
    ensure_genesis()
    tip = get_tip()
    index = (tip["index"] + 1) if tip else 1
    prev = tip["hash"] if tip else "GENESIS"
    block = _mine(index, prev, data)
    with open(CHAIN_PATH, "a") as f:
        f.write(json.dumps(block, separators=(",", ":")) + "\n")
    return block

def find_by_data(data: str) -> Optional[dict]:
    ensure_genesis()
    with open(CHAIN_PATH, "r") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                b = json.loads(line)
            except Exception:
                continue
            if b.get("data") == data:
                return b
    return None

# Ensure genesis on import (idempotent)
try:
    ensure_genesis()
except Exception:
    pass
