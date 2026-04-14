"""완료 실험 Results API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logger import get_logger
from app.dependencies import get_current_user, get_db
from app.models.models import ExperimentResult, User, Workflow
from app.schemas.schemas import ExperimentResultResponse, ExperimentResultUpdate

router = APIRouter(prefix="/results", tags=["results"])
logger = get_logger("experiment")


@router.get("", response_model=list[ExperimentResultResponse])
async def list_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExperimentResult]:
    if current_user.role == "admin":
        stmt = select(ExperimentResult).order_by(ExperimentResult.created_at.desc())
    else:
        stmt = (
            select(ExperimentResult)
            .join(Workflow, ExperimentResult.workflow_id == Workflow.workflow_id)
            .where(Workflow.user_id == current_user.user_id)
            .order_by(ExperimentResult.created_at.desc())
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{result_id}", response_model=ExperimentResultResponse)
async def get_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentResult:
    result = await db.execute(
        select(ExperimentResult)
        .options(selectinload(ExperimentResult.workflow))
        .where(ExperimentResult.result_id == result_id)
    )
    exp_result = result.scalar_one_or_none()
    if not exp_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="결과를 찾을 수 없습니다")
    if current_user.role != "admin" and exp_result.workflow.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")
    return exp_result


@router.patch("/{result_id}", response_model=ExperimentResultResponse)
async def update_result(
    result_id: int,
    body: ExperimentResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentResult:
    result = await db.execute(
        select(ExperimentResult)
        .options(selectinload(ExperimentResult.workflow))
        .where(ExperimentResult.result_id == result_id)
    )
    exp_result = result.scalar_one_or_none()
    if not exp_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="결과를 찾을 수 없습니다")
    if current_user.role != "admin" and exp_result.workflow.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")

    if body.notes is not None:
        exp_result.notes = body.notes

    await db.commit()
    await db.refresh(exp_result)
    logger.info("[result] 노트 수정: result_id=%d", result_id)
    return exp_result
