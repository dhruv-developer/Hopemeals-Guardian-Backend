# app/utils/security.py
from datetime import datetime, timedelta
from typing import Optional, Literal, Dict, Any
import jwt
from fastapi import HTTPException, status

def create_access_token(
    subject: str,
    role: Literal["admin", "investigator", "field"],
    secret: str,
    algorithm: str,
    expires_minutes: int
) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_token(token: str, secret: str, algorithms: list[str]) -> Dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=algorithms)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
