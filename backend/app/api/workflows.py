"""워크플로우 CRUD API — Plan 관리 (localStorage → DB 전환)."""
from __future__ import annotations

from copy import deepcopy

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.dependencies import get_current_user, get_db, require_admin
from app.models.models import ExperimentResult, User, Workflow
from app.schemas.schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate

router = APIRouter(prefix="/workflows", tags=["workflows"])
logger = get_logger("workflow")


def _assert_owner(workflow: Workflow, user: User) -> None:
    """소유자가 아니면 403."""
    if workflow.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다")


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    all: bool = Query(False, description="admin 전용: 전체 워크플로우 조회"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Workflow]:
    if all and current_user.role == "admin":
        result = await db.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    else:
        result = await db.execute(
            select(Workflow)
            .where(Workflow.user_id == current_user.user_id)
            .order_by(Workflow.created_at.desc())
        )
    return list(result.scalars().all())


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workflow:
    workflow = Workflow(
        user_id=current_user.user_id,
        name=body.name,
        data=body.data,
        notes=body.notes,
        status="계획중",
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    logger.info("[workflow] 생성: workflow_id=%d user=%s", workflow.workflow_id, current_user.username)
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workflow:
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    if current_user.role != "admin":
        _assert_owner(workflow, current_user)
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    body: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workflow:
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    _assert_owner(workflow, current_user)

    if body.name is not None:
        workflow.name = body.name
    if body.status is not None:
        workflow.status = body.status
    if body.data is not None:
        workflow.data = body.data
    if body.notes is not None:
        workflow.notes = body.notes

    await db.commit()
    await db.refresh(workflow)
    logger.info("[workflow] 수정: workflow_id=%d user=%s", workflow_id, current_user.username)
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    _assert_owner(workflow, current_user)

    await db.delete(workflow)
    await db.commit()
    logger.info("[workflow] 삭제: workflow_id=%d user=%s", workflow_id, current_user.username)


@router.post("/{workflow_id}/copy", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def copy_workflow(
    workflow_id: int,
    body: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workflow:
    """Plan 복사 — 새 이름으로 동일한 data를 가진 신규 워크플로우 생성."""
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    if current_user.role != "admin":
        _assert_owner(source, current_user)

    copied = Workflow(
        user_id=current_user.user_id,
        name=body.name,
        data=deepcopy(source.data),
        notes=None,
        status="계획중",
    )
    db.add(copied)
    await db.commit()
    await db.refresh(copied)
    logger.info("[workflow] 복사: source=%d → new=%d user=%s", workflow_id, copied.workflow_id, current_user.username)
    return copied


@router.post("/{workflow_id}/complete", response_model=WorkflowResponse)
async def complete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Workflow:
    """실험 완료 처리 — status를 '완료'로 변경하고 ExperimentResult 레코드 생성."""
    result = await db.execute(select(Workflow).where(Workflow.workflow_id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="워크플로우를 찾을 수 없습니다")
    _assert_owner(workflow, current_user)

    if workflow.status != "진행중":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="진행중 상태의 워크플로우만 완료 처리할 수 있습니다")

    workflow.status = "완료"

    existing_result = await db.execute(
        select(ExperimentResult).where(ExperimentResult.workflow_id == workflow_id)
    )
    if not existing_result.scalar_one_or_none():
        db.add(ExperimentResult(workflow_id=workflow_id))

    await db.commit()
    await db.refresh(workflow)
    logger.info("[workflow] 완료: workflow_id=%d user=%s", workflow_id, current_user.username)
    return workflow
