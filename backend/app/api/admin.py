"""Admin API — 사용자 관리."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.dependencies import get_db, require_admin
from app.models.models import User
from app.schemas.schemas import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger("system")


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at))
    return list(result.scalars().all())


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> User:
    if role not in ("user", "admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role은 'user' 또는 'admin'이어야 합니다")
    if user_id == current_admin.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="자신의 role은 변경할 수 없습니다")

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")

    user.role = role
    await db.commit()
    await db.refresh(user)
    logger.info("[admin] role 변경: user_id=%d → %s by admin=%s", user_id, role, current_admin.username)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> None:
    if user_id == current_admin.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="자신의 계정은 삭제할 수 없습니다")

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다")

    await db.execute(delete(User).where(User.user_id == user_id))
    await db.commit()
    logger.info("[admin] 계정 삭제: user_id=%d by admin=%s", user_id, current_admin.username)
