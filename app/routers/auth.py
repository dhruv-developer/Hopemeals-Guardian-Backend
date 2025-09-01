# app/routers/auth.py
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deps import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.services.auth_service import create_user, authenticate_user
from app.utils.security import create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=dict)
async def signup(payload: SignupRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = await create_user(db, payload.email, payload.password, payload.role)
    return {"user_id": user_id}

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await authenticate_user(db, payload.email, payload.password)
    token = create_access_token(
        subject=str(user["_id"]),
        role=user["role"],
        secret=settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return TokenResponse(token=token, role=user["role"])
