"""애플리케이션 설정 — pydantic-settings 기반 환경변수 관리.

SECRET_KEY는 기본값이 없으며, 미설정 시 서버 시작 단계에서 ValidationError 발생.
"""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT — 기본값 없음: 미설정 시 서버 시작 실패
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일

    # DB
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/labpilot"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:9002",
    ]

    # 파일 경로
    UPLOAD_PATH: str = "./uploads"
    LOG_PATH: str = "./logs"

    # ss_manager 인증 키
    MANAGER_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SECRET_KEY must not be empty")
        return v


settings = Settings()
