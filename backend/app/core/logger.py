"""LpLogger — 타입별 파일, 날짜별 디렉토리 로깅 시스템.

사용법:
    from app.core.logger import get_logger
    logger = get_logger("auth")
    logger.info("로그인 성공: username=%s", username)

로그 타입: auth | workflow | experiment | device | system
출력 경로: {LOG_PATH}/{YYYY-MM-DD}/{type}.log
"""
from __future__ import annotations

import logging
import os
import shutil
from datetime import date, timedelta
from pathlib import Path

_loggers: dict[str, logging.Logger] = {}

LOG_TYPES = frozenset(["auth", "workflow", "experiment", "device", "system"])


def _make_handler(log_path: str, log_type: str) -> logging.FileHandler:
    today = date.today().isoformat()
    dir_path = Path(log_path) / today
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{log_type}.log"
    handler = logging.FileHandler(file_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    return handler


def purge_old_logs() -> None:
    """LOG_KEEP_DAYS보다 오래된 날짜 디렉토리를 삭제한다. 앱 시작 시 호출."""
    from app.config import settings

    log_root = Path(settings.LOG_PATH)
    if not log_root.exists():
        return

    cutoff = date.today() - timedelta(days=settings.LOG_KEEP_DAYS)
    for entry in log_root.iterdir():
        if not entry.is_dir():
            continue
        try:
            entry_date = date.fromisoformat(entry.name)
        except ValueError:
            continue
        if entry_date < cutoff:
            shutil.rmtree(entry, ignore_errors=True)


def get_logger(log_type: str) -> logging.Logger:
    """타입별 로거를 반환한다. 같은 타입은 싱글톤으로 재사용."""
    if log_type not in LOG_TYPES:
        log_type = "system"

    if log_type in _loggers:
        return _loggers[log_type]

    from app.config import settings

    logger = logging.getLogger(f"lp.{log_type}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = _make_handler(settings.LOG_PATH, log_type)
    logger.addHandler(handler)

    # 콘솔에도 출력
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("[%(name)s] %(levelname)s %(message)s"))
    logger.addHandler(console)

    _loggers[log_type] = logger
    return logger
