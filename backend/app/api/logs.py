"""실험 로그 API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.dependencies import get_current_user, get_db
from app.models.models import ExperimentLog, User, Workflow
from app.schemas.schemas import ExperimentLogCreate, ExperimentLogResponse, ExperimentLogUpdate

router = APIRouter(prefix="/logs", tags=["logs"])
logger = get_logger("experiment")


@router.get("", response_model=list[ExperimentLogResponse])
async def list_logs(
    workflow_id: int | None = Query(None),
    step_type: str | None = Query(None),
    log_status: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ExperimentLog]:
    stmt = select(ExperimentLog)

    if current_user.role != "admin":
        stmt = stmt.where(ExperimentLog.user_id == current_user.user_id)

    if workflow_id:
        stmt = stmt.where(ExperimentLog.workflow_id == workflow_id)
    if step_type:
        stmt = stmt.where(ExperimentLog.step_type == step_type)
    if log_status:
        stmt = stmt.where(ExperimentLog.status == log_status)

    stmt = stmt.order_by(ExperimentLog.started_at.desc().nullslast())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=ExperimentLogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    body: ExperimentLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentLog:
    wf_result = await db.execute(select(Workflow).where(Workflow.workflow_id == body.workflow_id))
    workflow = wf_result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    if current_user.role != "admin" and workflow.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")

    log = ExperimentLog(
        workflow_id=body.workflow_id,
        user_id=current_user.user_id,
        step_uid=body.step_uid,
        step_type=body.step_type,
        step_name=body.step_name,
        data_collected=body.data_collected,
        started_at=body.started_at,
        status="진행중",
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    logger.info("[log] 생성: log_id=%d workflow=%d step=%s", log.log_id, body.workflow_id, body.step_type)
    return log


@router.patch("/{log_id}", response_model=ExperimentLogResponse)
async def update_log(
    log_id: int,
    body: ExperimentLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExperimentLog:
    result = await db.execute(select(ExperimentLog).where(ExperimentLog.log_id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="로그를 찾을 수 없습니다")
    if current_user.role != "admin" and log.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")

    if body.status is not None:
        log.status = body.status
    if body.data_collected is not None:
        log.data_collected = body.data_collected
    if body.ended_at is not None:
        log.ended_at = body.ended_at

    await db.commit()
    await db.refresh(log)
    logger.info("[log] 수정: log_id=%d status=%s", log_id, log.status)
    return log
