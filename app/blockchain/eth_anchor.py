# app/blockchain/eth_anchor.py
"""
Ethereum text anchoring (optional). Stores a hash in transaction data on EVM.

Requires:
- web3>=6
- ETH_PROVIDER_URL, ETH_PRIVATE_KEY, ETH_CHAIN_ID in .env

Exports:
- is_configured() -> bool
- anchor_text(text: str) -> dict  # returns tx dict incl. tx_hash
"""

from __future__ import annotations
from typing import Dict
from app.config import settings

def is_configured() -> bool:
    return bool(settings.ETH_PROVIDER_URL and settings.ETH_PRIVATE_KEY and settings.ETH_CHAIN_ID)

def anchor_text(text: str) -> Dict[str, str]:
    try:
        from web3 import Web3
        from eth_account import Account
    except Exception as e:
        raise RuntimeError("web3 is not installed. `pip install web3` to enable ETH anchoring.") from e

    if not is_configured():
        raise RuntimeError("ETH anchoring not configured (check ENV).")

    w3 = Web3(Web3.HTTPProvider(settings.ETH_PROVIDER_URL))
    acct = Account.from_key(settings.ETH_PRIVATE_KEY)

    # data payload: bytes of the text (usually your ledger record hash)
    data_hex = w3.to_hex(text.encode("utf-8"))
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = {
        "to": acct.address,         # self-send
        "value": 0,
        "gas": settings.ETH_GAS_LIMIT,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
        "chainId": settings.ETH_CHAIN_ID,
        "data": data_hex,
    }
    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return {
        "tx_hash": tx_hash.hex(),
        "from": acct.address,
        "to": acct.address,
        "data_hex": data_hex,
        "chain_id": str(settings.ETH_CHAIN_ID)
    }
