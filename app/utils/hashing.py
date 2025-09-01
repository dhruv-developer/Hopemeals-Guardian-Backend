# app/utils/hashing.py
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return _pwd_context.verify(password, hashed)
