"""장비 상태 REST API"""
from __future__ import annotations

import asyncio
import math
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["devices"])

# SiLA 서버 연결 정보 (추후 DB/설정 파일로 관리)
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


def _check_balance_connection(host: str, port: int) -> dict:
    """SiLA gRPC Weight 값을 실제로 구독해 저울 물리 연결 여부를 확인.

    - SiLA 서버 자체에 접속이 안 되면 connected=False
    - 접속은 되지만 Weight 값이 오지 않으면 connected=False (저울 미연결)
    - Weight 값이 정상 수신되면 connected=True
    """
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
    except Exception as e:
        return {"connected": False, "detail": "Weight read failed"}
    finally:
        del client

    if math.isnan(value):
        return {"connected": False, "detail": "Balance not physically connected (NaN)"}
    return {"connected": True, "weight": round(value, 4)}


@router.get("/devices")
async def list_devices():
    """등록된 SiLA 장비 목록 반환."""
    return list(SILA_SERVERS.values())


@router.get("/devices/{device_id}/status")
async def device_status(device_id: str):
    """특정 장비의 연결 상태 확인.

    SiLA gRPC Weight Observable Property 구독으로 물리 장치 연결 여부까지 검증.
    """
    server = SILA_SERVERS.get(device_id)
    if not server:
        raise HTTPException(status_code=404, detail="device not found")

    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _executor,
                _check_balance_connection,
                server["host"],
                server["port"],
            ),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        result = {"connected": False, "detail": "Health check timed out"}
    return {"id": device_id, **result}
