"""장비 상태 REST API + 워치독."""
from __future__ import annotations

import asyncio
import math
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

from app.core.logger import get_logger

router = APIRouter(tags=["devices"])
logger = get_logger("device")

# SiLA 서버 연결 정보
SILA_SERVERS = {
    "balance": {
        "id": "balance",
        "name": "CB310 저울",
        "type": "balance",
        "host": "127.0.0.1",
        "port": 50051,
    },
}

_executor = ThreadPoolExecutor(max_workers=4)

# 워치독 상태
_watchdog_task: asyncio.Task | None = None
_device_connected: dict[str, bool] = {"balance": False}

WATCHDOG_INITIAL_INTERVAL = 30   # 초
WATCHDOG_MAX_INTERVAL = 300      # 초 (5분)


def _check_balance_connection(host: str, port: int) -> dict:
    """SiLA gRPC Weight 값을 실제로 구독해 저울 물리 연결 여부를 확인."""
    try:
        from sila2.client import SilaClient
        client = SilaClient(host, port, insecure=True)
    except Exception:
        return {"connected": False, "detail": "SiLA server not reachable"}

    try:
        subscription = client.WeightMeasurement.Weight.subscribe()
        value = next(subscription)
    except StopIteration:
        return {"connected": False, "detail": "No weight data received"}
    except Exception:
        return {"connected": False, "detail": "Weight read failed"}
    finally:
        del client

    if math.isnan(value):
        return {"connected": False, "detail": "Balance not physically connected (NaN)"}
    return {"connected": True, "weight": round(value, 4)}


async def _watchdog_loop() -> None:
    """장치 연결 상태를 감시하고 끊기면 재연결을 시도한다 (지수 백오프)."""
    interval = WATCHDOG_INITIAL_INTERVAL
    while True:
        await asyncio.sleep(interval)
        for device_id, server in SILA_SERVERS.items():
            try:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        _executor, _check_balance_connection, server["host"], server["port"]
                    ),
                    timeout=10.0,
                )
                was_connected = _device_connected.get(device_id, False)
                now_connected = result.get("connected", False)
                _device_connected[device_id] = now_connected

                if was_connected and not now_connected:
                    logger.warning("[device] %s 연결 끊김 감지 — 재연결 대기 중", device_id)
                    interval = WATCHDOG_INITIAL_INTERVAL
                elif not was_connected and now_connected:
                    logger.info("[device] %s 재연결 성공", device_id)
                    interval = WATCHDOG_INITIAL_INTERVAL
                elif not now_connected:
                    interval = min(interval * 2, WATCHDOG_MAX_INTERVAL)
                    logger.info("[device] %s 미연결 — 다음 재시도: %ds", device_id, interval)
            except asyncio.TimeoutError:
                logger.warning("[device] %s 워치독 체크 타임아웃", device_id)
            except Exception as e:
                logger.error("[device] 워치독 오류: %s", e)


async def start_watchdog() -> None:
    global _watchdog_task
    if _watchdog_task is None or _watchdog_task.done():
        _watchdog_task = asyncio.create_task(_watchdog_loop())
        logger.info("[device] 워치독 시작")


async def stop_watchdog() -> None:
    global _watchdog_task
    if _watchdog_task and not _watchdog_task.done():
        _watchdog_task.cancel()
        try:
            await _watchdog_task
        except asyncio.CancelledError:
            pass
    logger.info("[device] 워치독 종료")


@router.get("/devices")
async def list_devices():
    """등록된 SiLA 장비 목록 반환."""
    return list(SILA_SERVERS.values())


@router.get("/devices/{device_id}/status")
async def device_status(device_id: str):
    """특정 장비의 연결 상태 확인."""
    server = SILA_SERVERS.get(device_id)
    if not server:
        raise HTTPException(status_code=404, detail="device not found")

    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, _check_balance_connection, server["host"], server["port"]),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        result = {"connected": False, "detail": "Health check timed out"}
    _device_connected[device_id] = result.get("connected", False)
    return {"id": device_id, **result}
