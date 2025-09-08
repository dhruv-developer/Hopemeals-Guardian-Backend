# app/services/blockchain_service.py
"""
Unified anchoring interface.

Modes:
- off   : do nothing
- local : file-based PoW chain (app/blockchain/blocks.jsonl)
- eth   : Ethereum tx anchoring (requires web3 and env config)

Functions:
- maybe_anchor(record_hash: str) -> dict | None
- status() -> dict
- find_anchor(record_hash: str) -> dict | None
- chain_tail(limit: int = 50) -> list[dict]
- verify() -> dict
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
import os, json

from app.config import settings
from app.blockchain import localchain

# Optional eth
try:
    from app.blockchain.eth_anchor import is_configured as eth_is_configured, anchor_text as eth_anchor_text
except Exception:
    def eth_is_configured() -> bool:  # type: ignore
        return False
    def eth_anchor_text(_: str) -> dict:  # type: ignore
        raise RuntimeError("ETH anchoring not available; install web3 and set ENV.")

def maybe_anchor(record_hash: str) -> Optional[dict]:
    mode = settings.BLOCKCHAIN_MODE.lower().strip()
    if mode == "off":
        return None
    if mode == "local":
        try:
            blk = localchain.add_block(record_hash)
            return {"mode": "local", "height": blk["index"], "hash": blk["hash"]}
        except Exception as e:
            # never break the main flow
            print(f"[anchor][local] failed: {e}")
            return None
    if mode == "eth":
        try:
            if not eth_is_configured():
                print("[anchor][eth] not configured; skipping")
                return None
            tx = eth_anchor_text(record_hash)
            return {"mode": "eth", **tx}
        except Exception as e:
            print(f"[anchor][eth] failed: {e}")
            return None
    print(f"[anchor] unknown mode={mode}; skipping")
    return None

def status() -> dict:
    mode = settings.BLOCKCHAIN_MODE.lower().strip()
    out: Dict[str, Any] = {"mode": mode}
    if mode == "local":
        ok, n = localchain.verify_chain()
        tip = localchain.get_tip()
        out.update({"ok": ok, "height": n, "tip_hash": tip["hash"] if tip else None})
    elif mode == "eth":
        out.update({"configured": eth_is_configured()})
    else:
        out.update({"note": "anchoring disabled"})
    return out

def find_anchor(record_hash: str) -> Optional[dict]:
    mode = settings.BLOCKCHAIN_MODE.lower().strip()
    if mode == "local":
        return localchain.find_by_data(record_hash)
    # For ETH, the lookup would require an index; out of scope here.
    return None

def chain_tail(limit: int = 50) -> List[dict]:
    path = os.path.join(os.path.dirname(__file__), "..", "blockchain", "blocks.jsonl")
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return []
    # read last `limit` entries
    with open(path, "r") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(x) for x in lines]

def verify() -> dict:
    ok, n = localchain.verify_chain()
    return {"ok": ok, "height": n}
