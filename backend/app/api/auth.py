"""인증 API — register / login."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logger import get_logger
from app.dependencies import get_current_user, get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger("auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """신규 사용자 등록."""
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자명입니다")

    if body.email:
        dup_email = await db.execute(select(User).where(User.email == body.email))
        if dup_email.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용 중인 이메일입니다")

    user = User(
        username=body.username,
        password_hash=_hash_password(body.password),
        email=body.email,
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("[auth] 신규 사용자 등록: username=%s", body.username)
    return user


@router.post("/login", response_model=Token)
async def login(body: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    """로그인 — JWT 발급."""
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    if not user or not _verify_password(body.password, user.password_hash):
        logger.warning("[auth] 로그인 실패: username=%s", body.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = _create_access_token(user.user_id)
    logger.info("[auth] 로그인 성공: username=%s", body.username)
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    """현재 로그인 사용자 정보 반환."""
    return current_user
