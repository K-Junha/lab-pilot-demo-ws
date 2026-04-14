"""Pydantic v2 스키마 — 요청/응답 타입 정의."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 50:
            raise ValueError("username은 2~50자여야 합니다")
        return v

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다")
        if len(v.encode()) > 72:
            raise ValueError("비밀번호는 72바이트를 초과할 수 없습니다")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Workflow ──────────────────────────────────────────────────────────────────

class WorkflowCreate(BaseModel):
    name: str
    data: dict[str, Any] = {}
    notes: str | None = None


class WorkflowUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    data: dict[str, Any] | None = None
    notes: str | None = None


class WorkflowResponse(BaseModel):
    workflow_id: int
    user_id: int
    name: str
    status: str
    data: dict[str, Any]
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Experiment Log ────────────────────────────────────────────────────────────

class ExperimentLogCreate(BaseModel):
    workflow_id: int
    step_uid: int
    step_type: str
    step_name: str
    data_collected: dict[str, Any] | None = None
    started_at: datetime | None = None


class ExperimentLogUpdate(BaseModel):
    status: str | None = None
    data_collected: dict[str, Any] | None = None
    ended_at: datetime | None = None


class ExperimentLogResponse(BaseModel):
    log_id: int
    workflow_id: int
    user_id: int | None
    step_uid: int
    step_type: str
    step_name: str
    status: str
    data_collected: dict[str, Any] | None
    started_at: datetime | None
    ended_at: datetime | None

    model_config = {"from_attributes": True}


# ── Experiment Result ─────────────────────────────────────────────────────────

class ExperimentResultUpdate(BaseModel):
    notes: str | None = None


class ExperimentResultResponse(BaseModel):
    result_id: int
    workflow_id: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
